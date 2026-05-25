import apiClient from "./axiosInstance";

export interface Ingrediente {
    id: number
    nombre: string
    descripción: string | null
    es_alergeno: boolean
}

export interface IngredienteCreate {
    nombre: string
    descripcion?: string
    es_alergeno: boolean
}

export interface IngredienteUpdate {
    nombre?: string
    descripcion?: string
    es_alergeno?: boolean
}

const INGREDIENTES = '/ingredientes'

export async function getIngredientes(): Promise<Ingrediente[]> {
    const response = await apiClient.get<Ingrediente[]>(INGREDIENTES)
    return response.data
}

export async function createIngrediente(data: IngredienteCreate): Promise<Ingrediente> {
    const response = await apiClient.post<Ingrediente>(INGREDIENTES, data)
    return response.data
}

export async function updateIngrediente(id: number, data: IngredienteUpdate): Promise<Ingrediente> {
    const response = await apiClient.put<Ingrediente>(`${INGREDIENTES}/${id}`, data)
    return response.data
}

export async function deleteIngrediente(id: number): Promise<void> {
    await apiClient.delete(`${INGREDIENTES}/${id}`)
}