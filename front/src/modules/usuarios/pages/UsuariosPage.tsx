import { useUsuarios, useDeleteUsuario } from "../hooks/useUsuarios";
import { UsuariosTable } from "../components/UsuariosTable";

export function UsuariosPage() {
    const { data: usuarios = [], isLoading, isError } = useUsuarios()
    const deleteUsuario = useDeleteUsuario()

    const handleDelete = async (id: number) => {
        if (!confirm('¿Estás seguro de que querés eliminar este usuario?')) return
        await deleteUsuario.mutateAsync(id)
    }

    if (isLoading) {
        return (
            <div className="flex h-full items-center justify-center">
                <p className="text-slate-500">Cargando usuarios...</p>
            </div>
        )
    }

    if (isError) {
        return (
            <div className="flex h-full items-center justify-center">
                <p className="text-red-500">Error al cargar los usuarios</p>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-slate-900">Usuarios</h1>
                <p className="text-sm text-slate-500">
                    Gestión de usuarios del sistema
                </p>
            </div>

            <UsuariosTable 
            data={usuarios}
            onDelete={handleDelete}
            />
        </div>
    )
}