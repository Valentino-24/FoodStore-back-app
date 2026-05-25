import { 
    useReactTable,
    getCoreRowModel,
    flexRender,
    createColumnHelper,
} from "@tanstack/react-table";
import type { Ingrediente } from "@/api/ingredientesApi";

interface IngredientesTableProps {
    data: Ingrediente[]
    isAdmin: boolean
    onEdit: (ingrediente: Ingrediente) => void
    onDelete: (id: number) => void
}

const columnHelper = createColumnHelper<Ingrediente>()

export function IngredientesTable({
    data,
    isAdmin,
    onEdit,
    onDelete,
}: IngredientesTableProps) {
    const columns = [
        columnHelper.accessor('id', {
            header: 'ID',
            cell: (info) => info.getValue(),
        }),
        columnHelper.accessor('nombre', {
            header: 'Nombre',
            cell: (info) => info.getValue(),
        }),
        columnHelper.accessor('es_alergeno', {
            header: 'Alérgeno',
            cell: (info) =>
                info.getValue() ? (
                    <span className="rounded-full bg-red-100 px-2 py-1 text-xs font-medium text-red-700">
                        Sí
                    </span>
                ) : (
                    <span className="rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700">
                        No
                    </span>
                ),
        }),
        columnHelper.display({
            id: 'acciones',
            header: 'Acciones',
            cell: (info) =>
                isAdmin ? (
                    <div className="flex gap-2">
                        <button
                        onClick={() => onEdit(info.row.original)}
                        className="rounded-lg bg-slate-100 px-3 py-1 text-sm text-slate-700 hover:bg-slate-200"
                        >
                            Editar
                        </button>
                        <button
                        onClick={() => onDelete(info.row.original.id)}
                        className="rounded-lg bg-red-50 px-3 py-1 text-sm text-red-600 hover:bg-red-100"
                        >
                            Eliminar
                        </button>
                    </div>
                ) : null,
        }),
    ]

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
    })

    return (
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
            <table className="w-full text-sm">
                <thead className="border-b border-slate-200 bg-slate-50">
                    {table.getHeaderGroups().map((headerGroup) => (
                        <tr key={headerGroup.id}>
                            {headerGroup.headers.map((header) => (
                                <th
                                key={header.id}
                                className="px-5 py-3.5 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
                                >
                                    {flexRender(
                                        header.column.columnDef.header,
                                        header.getContext(),
                                    )}
                                </th>
                            ))}
                        </tr>
                    ))}
                </thead>
                <tbody className="divide-y divide-slate-100">
                    {table.getRowModel().rows.length === 0 ? (
                        <tr>
                            <td
                            colSpan={columns.length}
                            className="px-5 py-10 text-center text-slate-400"
                            >
                                No hay ingredientes cargados
                            </td>
                        </tr>
                    ) : (
                        table.getRowModel().rows.map((row) => (
                            <tr
                            key={row.id}
                            className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
                            >
                                {row.getVisibleCells().map((cell) => (
                                    <td key={cell.id} className="px-5 py-4 text-slate-700">
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </td>
                                ))}
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
        </div>
    )
}