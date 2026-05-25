import { useState } from "react";
import { useAuthStore } from "@/stores/useAuthStore";
import { useCategorias, useCreateCategoria, useUpdateCategoria, useDeleteCategoria } from "../hooks/useCategorias";
import { CategoriasTable } from "../components/CategoriasTable";
import { CategoriaModal } from "../components/CategoriaModal";
import type { Categoria, CategoriaCreate, CategoriaUpdate } from "@/api/categoriasApi";

export function CategoriasPage() {
    const user = useAuthStore((s) => s.user)
    const isAdmin = user?.roles.includes('ADMIN') ?? false

    const { data: categorias = [], isLoading, isError } = useCategorias()
    const createCategoria = useCreateCategoria()
    const updateCategoria = useUpdateCategoria()
    const deleteCategoria = useDeleteCategoria()

    const [isModalOpen, setIsModalOpen] = useState(false)
    const [categoriaEditing, setCategoriaEditing] = useState<Categoria | null>(null)

    const handleOpenCreate = () => {
        setCategoriaEditing(null)
        setIsModalOpen(true)
    }

    const handleOpenEdit = (categoria: Categoria) => {
        setCategoriaEditing(categoria)
        setIsModalOpen(true)
    }

    const handleClose = () => {
        setIsModalOpen(false)
        setCategoriaEditing(null)
    }

    const handleSubmit = async (data: CategoriaCreate | CategoriaUpdate) => {
        if (categoriaEditing) {
            await updateCategoria.mutateAsync({ id: categoriaEditing.id, data })
        } else {
            await createCategoria.mutateAsync(data as CategoriaCreate)
        }
        handleClose()
    }

    const handleDelete = async (id: number) => {
        if (!confirm('¿Estás seguro de que querés eliminar esta categoría?')) return
        await deleteCategoria.mutateAsync(id)
    }

    if (isLoading) {
        return (
            <div className="flex h-full items-center justify-center">
                <p className="text-zinc-500">Cargando categorías...</p>
            </div>
        )
    }

    if (isError) {
        return (
            <div className="flex h-full items-center justify-center">
                <p className="text-red-500">Error al cargar las categorías</p>
            </div>
        )
    }

    return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Categorías</h1>
          <p className="text-sm text-slate-500">
            Gestión de categorías y subcategorías
          </p>
        </div>
        {isAdmin && (
          <button
            onClick={handleOpenCreate}
            className="flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 transition-colors"
          >
            <span>+</span> Nueva Categoría
          </button>
        )}
      </div>

      <CategoriasTable
        data={categorias}
        categorias={categorias}
        isAdmin={isAdmin}
        onEdit={handleOpenEdit}
        onDelete={handleDelete}
      />

      <CategoriaModal
        isOpen={isModalOpen}
        onClose={handleClose}
        onSubmit={handleSubmit}
        categorias={categorias}
        categoriaEditing={categoriaEditing}
        isLoading={createCategoria.isPending || updateCategoria.isPending}
      />
    </div>
  )
}