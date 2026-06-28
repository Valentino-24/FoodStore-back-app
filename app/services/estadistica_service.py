from datetime import date
from typing import Optional

from app.core.uow import UnitOfWork


def get_resumen() -> dict:
    """Resumen general del dashboard."""

    with UnitOfWork() as uow:
        total_productos = len(uow.productos.get_all())
        total_categorias = len(uow.categorias.get_all())
        total_ingredientes = len(uow.ingredientes.get_all())
        total_usuarios = len(uow.usuarios.get_all())
        total_pedidos = uow.pedidos.count_all_activos()

        ingresos_totales = uow.pedidos.get_ingresos_totales()

        pedidos_hoy = uow.pedidos.count_pedidos_hoy()

        # Pedido promedio
        ticket_promedio = round(ingresos_totales / total_pedidos, 2) if total_pedidos > 0 else 0.0

        # Pedidos por estado
        estados = uow.estados_pedido.get_all_ordenados()
        pedidos_por_estado = []
        for e in estados:
            count = uow.pedidos.count_by_estado(e.id)
            pedidos_por_estado.append({
                "codigo": e.codigo,
                "nombre": e.nombre,
                "cantidad": count,
            })

        return {
            "total_productos": total_productos,
            "total_categorias": total_categorias,
            "total_ingredientes": total_ingredientes,
            "total_usuarios": total_usuarios,
            "total_pedidos": total_pedidos,
            "pedidos_hoy": pedidos_hoy,
            "ingresos_totales": round(ingresos_totales, 2),
            "ticket_promedio": ticket_promedio,
            "pedidos_por_estado": pedidos_por_estado,
        }


def get_ventas(
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    agrupar_por: str = "dia",
) -> list[dict]:
    """Ventas agrupadas por día, semana o mes."""

    with UnitOfWork() as uow:
        resultados = uow.pedidos.get_ventas_agrupadas(
            desde=fecha_desde, hasta=fecha_hasta, agrupacion=agrupar_por
        )

        return [
            {
                "fecha": str(row["periodo"]),
                "cantidad_pedidos": row["cantidad_pedidos"],
                "ingresos": round(float(row["total_ventas"]), 2),
            }
            for row in resultados
        ]


def get_productos_mas_vendidos(limite: int = 10) -> list[dict]:
    """Productos más vendidos por cantidad."""

    with UnitOfWork() as uow:
        resultados = uow.pedidos.get_productos_mas_vendidos(limit=limite)

        return [
            {
                "producto_id": row["producto_id"],
                "nombre": row["nombre"],
                "total_vendido": row["total_vendido"],
                "total_ingresos": round(float(row["total_ingresos"]), 2),
            }
            for row in resultados
        ]


def get_pedidos_por_estado() -> list[dict]:
    """Distribución de pedidos por estado."""

    with UnitOfWork() as uow:
        estados = uow.estados_pedido.get_all_ordenados()
        resultado = []
        for e in estados:
            count = uow.pedidos.count_by_estado(e.id)
            resultado.append({
                "codigo": e.codigo,
                "nombre": e.nombre,
                "cantidad": count,
            })
        return resultado
