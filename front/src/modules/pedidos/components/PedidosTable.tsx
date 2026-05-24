import { 
    useReactTable,
    getCoreRowModel,
    flexRender,
    createColumnHelper,
} from "@tanstack/react-table";
import type { Pedido, EstadoPedido } from "@/api/pedidosApi";

interface PedidosTableProps {
    data: Pedido[]
    onAvanzar: (id: number) => void
    onCancelar: (id: number) => void
}

const columnHelper = createColumnHelper<Pedido>()

const estadoColors: Record<EstadoPedido, string> = {
    PENDIENTE: 'bg-yellow-100 text-yellow-700',
    CONFIRMADO: 'bg-blue-100 text-blue-700',
    EN_PREP: 'bg-orange-100 text-orange-700',
    EN_CAMINO: 'bg-purple-100 text-purple-700',
    ENTREGADO: 'bg-green-100 text-green-700',
    CANCELADO: 'bg-red-100 text-red-700',
}

const estadoSiguiente: Partial<Record<EstadoPedido, string>> = {
    PENDIENTE: 'Confirmar',
    CONFIRMADO: 'En preparación',
    EN_PREP: 'En camino',
    EN_CAMINO: 'Entregar',
}

export function PedidosTable({ data, onAvanzar, onCancelar }: PedidosTableProps) {
    const columns = [
        columnHelper.accessor('id', {
            header: 'ID',
            cell: (info) => `#${info.getValue()}`,
        }),
        columnHelper.accessor('usuario_id', {
            header: 'Cliente ID',
            cell: (info) => info.getValue(),
        }),
        columnHelper.accessor('estado', {
            header: 'Estado',
            cell: (info) => (
                <span
                className={`rounded-full px-2 py-1 text-xs font-medium ${estadoColors[info.getValue()]}`}
                >
                    {info.getValue()}
                </span>
            ),
        }),
        columnHelper.accessor('fecha_creacion', {
            header: 'Fecha',
            cell: (info) => new Date(info.getValue()).toLocaleDateString('es-AR'),
        }),
        columnHelper.display({
            id: 'acciones',
            header: 'Acciones',
            cell: (info) => {
                const estado = info.row.original.estado
                const puedeAvanzar = estado in estadoSiguiente
                const puedeCancelar = estado === 'PENDIENTE' || estado === 'CONFIRMADO'

                return (
                    <div className="flex gap-2">
                        {puedeAvanzar && (
                            <button
                            onClick={() => onAvanzar(info.row.original.id)}
                            className="rounded-lg bg-zinc-900 px-3 py-1 text-sm text-white hover:bg-zinc-700"
                            >
                                {estadoSiguiente[estado]}
                            </button>
                        )}
                        {puedeCancelar && (
                            <button
                            onClick={() => onCancelar(info.row.original.id)}
                            className="rounded-lg bg-red-50 px-3 py-1 text-sm text-red-600 hover:bg-red-100"
                            >
                                Cancelar
                            </button>
                        )}
                    </div>
                )
            },
        }),
    ]

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
    })

    return (
        <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white">
            <table className="w-full text-sm">
                <thead className="border-b border-zinc-200 bg-zinc-50">
                    {table.getHeaderGroups().map((headerGroup) => (
                        <tr key={headerGroup.id}>
                            {headerGroup.headers.map((header) => (
                                <th
                                key={header.id}
                                className="px-4 py-3 text-left font-medium text-zinc-600"
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
                <tbody>
                    {table.getRowModel().rows.length === 0 ? (
                        <tr>
                            <td
                            colSpan={columns.length}
                            className="px-4 py-8 text-center text-zinc-400"
                            >
                                No hay pedidos
                            </td>
                        </tr>
                    ) : (
                        table.getRowModel().rows.map((row) => (
                            <tr
                            key={row.id}
                            className="border-b border-zinc-100 last:border-0 hover:bg-zinc-50"
                            >
                                {row.getVisibleCells().map((cell) => (
                                    <td key={cell.id} className="px-4 py-3 text-zinc-700">
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