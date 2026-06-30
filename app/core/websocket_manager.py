import json
from collections import defaultdict
from typing import Optional

from fastapi import WebSocket


class ConnectionManager:
    """Gestiona conexiones WebSocket por usuario."""

    def __init__(self):
        self._connections: dict[int, list[WebSocket]] = defaultdict(list)
        self._admin_connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket, user_id: int, es_admin: bool = False) -> None:
        await ws.accept()
        self._connections[user_id].append(ws)
        if es_admin:
            self._admin_connections.append(ws)

    async def disconnect(self, ws: WebSocket, user_id: int) -> None:
        self._connections[user_id] = [w for w in self._connections[user_id] if w is not ws]
        if not self._connections[user_id]:
            del self._connections[user_id]
        self._admin_connections = [w for w in self._admin_connections if w is not ws]

    async def notify_user(self, user_id: int, data: dict) -> None:
        """Envía notificación a todas las conexiones de un usuario."""
        if user_id not in self._connections:
            return
        message = json.dumps(data)
        stale = []
        for ws in self._connections[user_id]:
            try:
                await ws.send_text(message)
            except Exception:
                stale.append(ws)
        for ws in stale:
            await self.disconnect(ws, user_id)

    async def notify_admins(self, data: dict) -> None:
        message = json.dumps(data)
        stale = []
        for ws in self._admin_connections:
            try:
                await ws.send_text(message)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self._admin_connections.remove(ws)
            # Limpiar también de connections por usuario
            for uid, conns in list(self._connections.items()):
                if ws in conns:
                    conns.remove(ws)
                    if not conns:
                        del self._connections[uid]

    async def broadcast(self, data: dict) -> None:
        message = json.dumps(data)
        all_connections = list(self._admin_connections)
        for conns in self._connections.values():
            all_connections.extend(conns)

        stale = set()
        for ws in all_connections:
            try:
                await ws.send_text(message)
            except Exception:
                stale.add(ws)
        for ws in stale:
            for uid, conns in list(self._connections.items()):
                if ws in conns:
                    conns.remove(ws)
                    if not conns:
                        del self._connections[uid]
            if ws in self._admin_connections:
                self._admin_connections.remove(ws)


# Singleton compartido por toda la app
manager = ConnectionManager()
