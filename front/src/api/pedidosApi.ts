import apiClient from "./axiosInstance";

export type EstadoPedido = 
    | 'PENDIENTE'
    | 'CONFIRMADO'
    | 'EN_PREP'
    | 'EN_CAMINO'
    | 'ENTREGADO'
    | 'CANCELADO'

export interface DetallePedido {
    id: number
    producto_id: number
    producto_nombre: string
    producto_precio: number
    cantidad: number
    subtotal: number
}

export interface Pedido {
    id: number
    usuario_id: number
    estado: EstadoPedido
    fecha_creacion: string
    detalles: DetallePedido[]
    total: number
}

const PEDIDOS = '/pedidos'

export async function getPedidos(): Promise<Pedido[]> {
    const response = await apiClient.get<Pedido[]>(PEDIDOS)
    return response.data
}

export async function avanzarEstado(id: number): Promise<Pedido> {
    const response = await apiClient.patch<Pedido>(`${PEDIDOS}/${id}/estado`)
    return response.data
}

export async function cancelarPedido(id: number): Promise<Pedido> {
    const response = await apiClient.patch<Pedido>(`${PEDIDOS}/${id}/cancelar`)
    return response.data
}