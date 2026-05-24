import { useEffect, useState } from "react";
import type { Categoria } from "@/api/categoriasApi";
import type { Ingrediente } from "@/api/ingredientesApi";
import type { Producto, ProductoCreate, ProductoUpdate } from "@/api/productosApi";

interface ProductoModalProps {
    isOpen: boolean
    onClose: () => void
    onSubmit: (data: ProductoCreate | ProductoUpdate) => void
    categorias: Categoria[]
    ingredientes: Ingrediente[]
    productoEditing: Producto | null
    isLoading: boolean
}

export function ProductoModal({
    isOpen,
    onClose,
    onSubmit,
    categorias,
    ingredientes,
    productoEditing,
    isLoading,
}: ProductoModalProps) {
    const [nombre, setNombre] = useState('')
    const [descripcion, setDescripcion] = useState('')
    const [precio, setPrecio] = useState('')
    const [stockCantidad, setStockCantidad] = useState('')
    const [disponible, setDisponible] = useState(true)
    const [categoriaId, setCategoriaId] = useState<number | null>(null)
    const [ingredienteIds, setIngredienteIds] = useState<number[]>([])

    useEffect(() => {
        if (productoEditing) {
            setNombre(productoEditing.nombre)
            setDescripcion(productoEditing.descripcion ?? '')
            setPrecio(productoEditing.precio.toString())
            setStockCantidad(productoEditing.stock_cantidad.toString())
            setDisponible(productoEditing.disponible)
            setCategoriaId(productoEditing.categoria_id)
            setIngredienteIds(productoEditing.ingredientes.map((i) => i.id))
        } else {
            setNombre('')
            setDescripcion('')
            setPrecio('')
            setStockCantidad('')
            setDisponible(true)
            setCategoriaId(null)
            setIngredienteIds([])
        }
    }, [productoEditing, isOpen])

    if (!isOpen) return null

    const handleToggleIngrediente = (id: number) => {
        setIngredienteIds((prev) =>
            prev.includes(id) ? prev.filter((i) => i!== id) : [...prev, id],
        )
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        onSubmit({
            nombre,
            descripcion: descripcion || undefined,
            precio: Number(precio),
            stock_cantidad: Number(stockCantidad),
            disponible,
            categoria_id: categoriaId!,
            ingrediente_ids: ingredienteIds,
        })
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
                <h2 className="mb-4 text-lg font-bold text-zinc-900">
                    {productoEditing ? 'Editar Producto' : 'Nuevo Producto'}
                </h2>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-zinc-700">
                            Nombre
                        </label>
                        <input 
                        type="text"
                        value={nombre}
                        onChange={(e) => setNombre(e.target.value)}
                        required
                        disabled={isLoading}
                        className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-2 text-zinc-900 focus:border-zinc-500 focus:outline-none disabled:bg-zinc-100"
                        placeholder="Nombre del producto"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-zinc-700">
                            Descripción
                        </label>
                        <input 
                        type="text"
                        value={descripcion}
                        onChange={(e) => setDescripcion(e.target.value)}
                        disabled={isLoading}
                        className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-2 text-zinc-900 focus:border-zinc-500 focus:outline-none disabled:bg-zinc-100"
                        placeholder="Descripción opcional"
                        />
                    </div>

                    <div className="flex-gap-4">
                        <div className="flex-1">
                            <label className="block text-sm font-medium text-zinc-700">
                                Precio
                            </label>
                            <input 
                            type="number"
                            min="0"
                            step="0.01"
                            value={precio}
                            onChange={(e) => setPrecio(e.target.value)}
                            required
                            disabled={isLoading}
                            className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-2 text-zinc-900 focus:border-zinc-500 focus:outline-none disabled:bg-zinc-100"
                            placeholder="0.00"
                            />
                        </div>

                        <div className="flex-1">
                            <label className="block text-sm font-medium text-zinc-700">
                                Stock
                            </label>
                            <input 
                            type="number" 
                            min="0"
                            value={stockCantidad}
                            onChange={(e) => setStockCantidad(e.target.value)}
                            required
                            disabled={isLoading}
                            className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-2 text-zinc-900 focus:border-zinc-500 focus:outline-none disabled:bg-zinc-100"
                            placeholder="0"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-zinc-700">
                            Categoría
                        </label>
                        <select 
                        value={categoriaId ?? ''}
                        onChange={(e) => setCategoriaId(Number(e.target.value))}
                        required
                        disabled={isLoading}
                        className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-2 text-zinc-900 focus:border-zinc-500 focus:outline-none disabled:bg-zinc-100"
                        >
                            <option value="">Seleccioná una categoría</option>
                            {categorias.map((c) => (
                                <option key={c.id} value={c.id}>
                                    {c.nombre}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="flex items-center gap-3">
                        <input 
                        type="checkbox"
                        id="disponible"
                        checked={disponible}
                        onChange={(e) => setDisponible(e.target.checked)}
                        disabled={isLoading}
                        className="h-4 w-4 rounded border-zinc-300" 
                        />
                        <label htmlFor="disponible" className="text-sm font-medium text-zinc-700">
                            Disponible
                        </label>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-zinc-700 mb-2">
                            Ingredientes
                        </label>
                        <div className="max-h-36 overflow-y-auto rounded-lg border border-zinc-300 p-3 space-y-2">
                            {ingredientes.length === 0 ? (
                                <p className="text-sm text-zinc-400">No hay ingredientes cargados</p>
                            ) : (
                                ingredientes.map((i) => (
                                    <div key={i.id} className="flex items-center gap-2">
                                        <input 
                                        type="checkbox"
                                        id={`ing-${i.id}`}
                                        checked={ingredienteIds.includes(i.id)} 
                                        onChange={() => handleToggleIngrediente(i.id)}
                                        disabled={isLoading}
                                        className="h-4 w-4 rounded border-zinc-300"
                                        />
                                        <label htmlFor={`ing-${i.id}`} className="text-sm text-zinc-700">
                                            {i.nombre}
                                            {i.es_alergeno && (
                                                <span className="ml-2 rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-700">
                                                    Alérgeno
                                                </span>
                                            )}
                                        </label>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    <div>
                        <button
                        type="button"
                        onClick={onClose}
                        disabled={isLoading}
                        className="rounded-lg border border-zinc-200 px-4 py-2 text-sm text-zinc-600 hover:bg-zinc-50 disabled:opacity-50"
                        >
                            Cancelar
                        </button>
                        <button
                        type="submit"
                        disabled={isLoading}
                        className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50"
                        >
                            {isLoading ? 'Guardando...' : 'Guardar'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}