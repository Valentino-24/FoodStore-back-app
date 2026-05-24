import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
    getPedidos,
    avanzarEstado,
    cancelarPedido,
} from "@/api/pedidosApi";

const QUERY_KEY = ['pedidos']

export function usePedidos() {
    return useQuery({
        queryKey: QUERY_KEY,
        queryFn: getPedidos,
    })
}

export function useAvanzarEstado() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (id: number) => avanzarEstado(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: QUERY_KEY })
        },
    })
}

export function useCancelarPedido() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (id: number) => cancelarPedido(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: QUERY_KEY })
        },
    })
}