from app.core.uow import UnitOfWork


def get_dashboard_stats() -> dict:
    with UnitOfWork() as uow:
        # ─── Counts ─────────────────────────────────────────────
        total_productos = len(uow.productos.get_all())
        total_categorias = len(uow.categorias.get_all())
        total_ingredientes = len(uow.ingredientes.get_all())
        total_pedidos = uow.pedidos.count_all_activos()

        # ─── Ingresos totales ────────────────────────────────────
        ingresos_totales = uow.pedidos.get_ingresos_totales()

        # ─── Pedidos por estado ──────────────────────────────────
        estados = uow.estados_pedido.get_all_ordenados()
        estado_map = {e.id: {"codigo": e.codigo, "nombre": e.nombre} for e in estados}

        pedidos_por_estado = []
        for estado in estados:
            count = uow.pedidos.count_by_estado(estado.id)
            pedidos_por_estado.append({
                "codigo": estado.codigo,
                "nombre": estado.nombre,
                "cantidad": count,
            })

        # ─── Pedidos recientes (últimos 5) ──────────────────────
        pedidos_recientes = uow.pedidos.get_recientes(limit=5)

        recientes = []
        for p in pedidos_recientes:
            estado_info = estado_map.get(p.estado_actual_id, {})
            recientes.append({
                "id": p.id,
                "total": p.total,
                "fecha": p.fecha_pedido.isoformat() if p.fecha_pedido else None,
                "estado_codigo": estado_info.get("codigo", ""),
                "estado_nombre": estado_info.get("nombre", ""),
            })

        # ─── Pedidos de hoy ─────────────────────────────────────
        pedidos_hoy = uow.pedidos.count_pedidos_hoy()

        return {
            "total_productos": total_productos,
            "total_categorias": total_categorias,
            "total_ingredientes": total_ingredientes,
            "total_pedidos": total_pedidos,
            "pedidos_hoy": pedidos_hoy,
            "ingresos_totales": round(ingresos_totales, 2),
            "pedidos_por_estado": pedidos_por_estado,
            "pedidos_recientes": recientes,
        }
