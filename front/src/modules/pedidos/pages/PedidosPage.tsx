import { useAuthStore } from "@/stores/useAuthStore";
import { usePedidos, useCambiarEstado } from "../hooks/usePedidos";
import { PedidosTable } from "../components/PedidosTable";
import type { CambioEstadoRequest } from "@/api/pedidosApi";

export function PedidosPage() {
    const user = useAuthStore((s) => s.user)
    const isAdmin = user?.roles.includes('ADMIN') ?? false
    const isPedidos = user?.roles.includes('PEDIDOS') ?? false

    const { data: pedidos = [], isLoading, isError } = usePedidos()
    const cambiarEstado = useCambiarEstado()

    const handleCambiarEstado = async (id: number, data: CambioEstadoRequest) => {
        await cambiarEstado.mutateAsync({ id, data })
    }

    if (isLoading) {
        return (
            <div className="flex h-full items-center justify-center">
                <p className="text-slate-500">Cargando pedidos...</p>
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
                <h1 className="text-2xl font-bold text-slate-900">Pedidos</h1>
                <p className="text-sm text-slate-500">
                    Gestión y seguimiento de pedidos
                </p>
            </div>

            <PedidosTable 
            data={pedidos}
            onCambiarEstado={handleCambiarEstado}
            />
        </div>
    )
}