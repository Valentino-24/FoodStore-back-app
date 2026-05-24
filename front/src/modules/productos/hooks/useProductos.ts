import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
    getProductos,
    createProducto,
    updateProducto,
    deleteProducto,
    updateDisponibilidad,
    type ProductoCreate,
    type ProductoUpdate,
} from "@/api/productosApi";

const QUERY_KEY = ['productos']

export function useProductos() {
    return useQuery({
        queryKey: QUERY_KEY,
        queryFn: getProductos,
    })
}

export function useCreateProducto() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (data: ProductoCreate) => createProducto(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: QUERY_KEY })
        },
    })
}

export function useUpdateProducto() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: ({ id, data }: { id: number; data: ProductoUpdate }) =>
            updateProducto(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: QUERY_KEY })
        },
    })
}

export function useDeleteProducto() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (id: number) => deleteProducto(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: QUERY_KEY})
        },
    })
}

export function useUpdateDisponibilidad() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: ({ id, disponible }: { id: number; disponible: boolean }) =>
            updateDisponibilidad(id, disponible),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: QUERY_KEY })
        }
    })
}