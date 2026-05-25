import { useState } from "react"
import { useAuthStore } from "@/stores/useAuthStore"
import { useProductos, useCreateProducto, useUpdateProducto,useDeleteProducto, useUpdateDisponibilidad } from "../hooks/useProductos"
import { useCategorias } from "@/modules/categorias/hooks/useCategorias"
import { useIngredientes } from "@/modules/ingredientes/hooks/useIngredientes"
import { ProductosTable } from "../components/ProductosTable"
import { ProductoModal } from "../components/ProductoModal"
import { type Producto, type ProductoCreate, type ProductoUpdate } from "@/api/productosApi"

export function ProductosPage() {
    const user = useAuthStore((s) => s.user)
    const isAdmin = user?.roles.includes('ADMIN') ?? false

    const { data: productos = [], isLoading, isError } = useProductos()
    const { data: categorias = [] } = useCategorias()
    const { data: ingredientes = [] } = useIngredientes()

    const createProducto = useCreateProducto()
    const updateProducto = useUpdateProducto()
    const deleteProducto = useDeleteProducto()
    const updateDisponibilidad = useUpdateDisponibilidad()

    const [isModalOpen, setIsModalOpen] = useState(false)
    const [productoEditing, setProductoEditing] = useState<Producto | null>(null)

    const handleOpenCreate = () => {
        setProductoEditing(null)
        setIsModalOpen(true)
    }

    const handleOpenEdit = (producto: Producto) => {
        setProductoEditing(producto)
        setIsModalOpen(true)
    }

    const handleClose = () => {
        setIsModalOpen(false)
        setProductoEditing(null)
    }

    const handleSubmit = async (data: ProductoCreate | ProductoUpdate) => {
        if (productoEditing) {
            await updateProducto.mutateAsync({ id: productoEditing.id, data })
        } else {
            await createProducto.mutateAsync(data as ProductoCreate)
        }
        handleClose()
    }

    const handleDelete = async (id: number) => {
        if (!confirm('¿Estás seguro de que querés eliminar este producto?')) return
        await deleteProducto.mutateAsync(id)
    }

    const handleToggleDisponibilidad = async (id: number, disponible: boolean) => {
        await updateDisponibilidad.mutateAsync({ id, disponible })
    }

    if (isLoading) {
        return (
            <div className="flex h-full items-center justify-center">
                <p className="text-slate-500">Cargando productos...</p>
            </div>
        )
    }

    if (isError) {
        return (
            <div className="flex h-full items-center justify-center">
                <p className="text-red-500">Error al cargar los productos</p>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Productos</h1>
                    <p className="text-sm text-slate-500">
                        Gestión de productos del catálogo
                    </p>
                </div>
                {isAdmin && (
                    <button
                    onClick={handleOpenCreate}
                    className="flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
                    >
                        <span>+</span> Nuevo Producto
                    </button>
                )}
            </div>

            <ProductosTable 
            data={productos}
            isAdmin={isAdmin}
            onEdit={handleOpenEdit}
            onDelete={handleDelete}
            onToggleDisponibilidad={handleToggleDisponibilidad}
            />

            <ProductoModal 
            isOpen={isModalOpen}
            onClose={handleClose}
            onSubmit={handleSubmit}
            categorias={categorias}
            ingredientes={ingredientes}
            productoEditing={productoEditing}
            isLoading={createProducto.isPending || updateProducto.isPending}
            />
        </div>
    )
}