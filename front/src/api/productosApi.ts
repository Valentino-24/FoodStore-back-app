import apiClient from "./axiosInstance";
import type { Ingrediente } from "./ingredientesApi";
import type { Categoria } from "./categoriasApi";

export interface Producto {
    id: number
    nombre: string
    descripcion: string | null
    precio: number
    disponible: boolean
    stock_cantidad: number
    categoria_id: number
    categoria: Categoria
    ingredientes: Ingrediente[]
}

export interface ProductoCreate {
    nombre: string
    descripcion?: string
    precio: number
    disponible: boolean
    stock_cantidad: number
    categoria_id: number
    ingrediente_ids: number[]
}

export interface ProductoUpdate {
    nombre?: string
    descripcion?: string
    precio?: number
    disponible?: boolean
    stock_cantidad?: number
    categoria_id?: number
    ingrediente_ids?: number[]
}

const PRODUCTOS = '/productos'

export async function getProductos(): Promise<Producto[]> {
    const response = await apiClient.get<Producto[]>(PRODUCTOS)
    return response.data
}

export async function createProducto(data: ProductoCreate): Promise<Producto> {
    const response = await apiClient.post<Producto>(PRODUCTOS, data)
    return response.data
}

export async function updateProducto(id: number, data: ProductoUpdate): Promise<Producto> {
    const response = await apiClient.patch<Producto>(`${PRODUCTOS}/${id}`, data)
    return response.data
}

export async function deleteProducto(id: number): Promise<void> {
    await apiClient.delete(`${PRODUCTOS}/${id}`)
}

export async function updateDisponibilidad(id: number, disponible: boolean): Promise<Producto> {
    const response = await apiClient.patch<Producto>(`${PRODUCTOS}/${id}/disponibilidad`, { disponible })
    return response.data
}