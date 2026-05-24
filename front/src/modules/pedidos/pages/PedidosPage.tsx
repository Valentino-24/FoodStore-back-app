import { useAuthStore } from "@/stores/useAuthStore";
import { usePedidos, useAvanzarEstado, useCancelarPedido } from "../hooks/usePedidos";
import { PedidosTable } from "../components/PedidosTable";

export function PedidosPage() {
    const user = useAuthStore((s) => s.user)
    const isAdmin = user?.roles.includes('ADMIN') ?? false
    const isPedidos = user?.roles.includes('PEDIDOS') ?? false

    const { data: pedidos = [], isLoading, isError } = usePedidos()
    const avanzarEstado = useAvanzarEstado()
    const cancelarPedido = useCancelarPedido()

    const handleAvanzar = async (id: number) => {
        await avanzarEstado.mutateAsync(id)
    }

    const handleCancelar = async (id: number) => {
        if (!confirm('¿Estás seguro de que querés cancelar este pedido?')) return
        await cancelarPedido.mutateAsync(id)
    }

    if (isLoading) {
        return (
            <div className="flex h-full items-center justify-center">
                <p className="text-zinc-500">Cargando pedidos...</p>
            </div>
        )
    }

    if (isError) {
        return (
            <div className="flex h-full items-center justify-center">
                <p className="text-red-500">Error al cargar los pedidos</p>
            </div>
        )
    }

    if (!isAdmin && !isPedidos) {
        return (
            <div className="flex h-full items-center justify-center">
                <p>No tenés permisos para ver esta sección</p>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-zinc-900">Pedidos</h1>
                <p className="text-sm text-zinc-500">
                    Gestión y seguimiento de pedidos
                </p>
            </div>

            <PedidosTable 
            data={pedidos}
            onAvanzar={handleAvanzar}
            onCancelar={handleCancelar}
            />
        </div>
    )
}