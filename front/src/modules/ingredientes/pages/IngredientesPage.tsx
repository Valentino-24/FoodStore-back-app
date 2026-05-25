import { useState } from "react";
import { useAuthStore } from "@/stores/useAuthStore";
import { useIngredientes, useCreateIngrediente, useUpdateIngrediente, useDeleteIngrediente } from "../hooks/useIngredientes";
import { IngredientesTable } from "../components/IngredientesTable";
import { IngredienteModal } from "../components/IngredienteModal";
import type { Ingrediente, IngredienteCreate, IngredienteUpdate } from "@/api/ingredientesApi";

export function IngredientesPage() {
    const user = useAuthStore((s) => s.user)
    const isAdmin = user?.roles.includes('ADMIN') ?? false

    const { data: ingredientes = [], isLoading, isError } = useIngredientes()
    const createIngrediente = useCreateIngrediente()
    const updateIngrediente = useUpdateIngrediente()
    const deleteIngrediente = useDeleteIngrediente()

    const [isModalOpen, setIsModalOpen] = useState(false)
    const [ingredienteEditing, setIngredienteEditing] = useState<Ingrediente | null>(null)

    const handleOpenCreate = () => {
        setIngredienteEditing(null)
        setIsModalOpen(true)
    }

    const handleOpenEdit = (ingrediente: Ingrediente) => {
        setIngredienteEditing(ingrediente)
        setIsModalOpen(true)
    }

    const handleClose = () => {
        setIsModalOpen(false)
        setIngredienteEditing(null)
    }

    const handleSubmit = async (data: IngredienteCreate | IngredienteUpdate) => {
        if (ingredienteEditing) {
            await updateIngrediente.mutateAsync({ id: ingredienteEditing.id, data })
        } else {
            await createIngrediente.mutateAsync(data as IngredienteCreate)
        }
        handleClose()
    }

    const handleDelete = async (id: number) => {
        if (!confirm('¿Estás seguro de que querés eliminar este ingrediente?')) return
        await deleteIngrediente.mutateAsync(id)
    }

    if (isLoading) {
        return (
            <div className="flex h-full items-center justify-center">
                <p className="text-slate-500">Cargando ingredientes...</p>
            </div>
        )
    }

    if (isError) {
        return (
            <div className="flex h-full items-center justify-center">
                <p className="text-red-500">Error al cargar los ingredientes</p>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Ingredientes</h1>
                    <p className="text-sm text-slate-500">
                        Gestión de ingredientes y alérgenos
                    </p>
                </div>
                {isAdmin && (
                    <button
                    onClick={handleOpenCreate}
                    className="flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
                    >
                        <span>+</span> Nuevo Ingrediente
                    </button>
                )}
            </div>

            <IngredientesTable 
            data={ingredientes}
            isAdmin={isAdmin}
            onEdit={handleOpenEdit}
            onDelete={handleDelete}
            />

            <IngredienteModal 
            isOpen={isModalOpen}
            onClose={handleClose}
            onSubmit={handleSubmit}
            ingredienteEditing={ingredienteEditing}
            isLoading={createIngrediente.isPending || updateIngrediente.isPending}
            />
        </div>
    )
}