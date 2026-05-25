import { 
    useReactTable,
    getCoreRowModel,
    flexRender,
    createColumnHelper,
} from "@tanstack/react-table";
import type { Pedido, EstadoPedido, CambioEstadoRequest } from "@/api/pedidosApi";
import { useEstadosPosibles } from "../hooks/usePedidos";

interface PedidosTableProps {
    data: Pedido[]
    onCambiarEstado: (id: number, data: CambioEstadoRequest) => void
}

const columnHelper = createColumnHelper<Pedido>()

const estadoColors: Record<string, string> = {
    PENDIENTE: 'bg-yellow-100 text-yellow-700',
    CONFIRMADO: 'bg-blue-100 text-blue-700',
    EN_PREP: 'bg-orange-100 text-orange-700',
    EN_CAMINO: 'bg-purple-100 text-purple-700',
    ENTREGADO: 'bg-green-100 text-green-700',
    CANCELADO: 'bg-red-100 text-red-700',
}

function AccionesCell({
  pedido,
  onCambiarEstado,
}: {
  pedido: Pedido
  onCambiarEstado: (id: number, data: CambioEstadoRequest) => void
}) {
  const { data: estadosPosibles = [] } = useEstadosPosibles(pedido.id)

  if (estadosPosibles.length === 0) return <span className="text-xs text-slate-400">Sin acciones</span>

  return (
    <div className="flex gap-2 flex-wrap">
      {estadosPosibles.map((estado: EstadoPedido) => (
        <button
          key={estado.id}
          onClick={() => onCambiarEstado(pedido.id, { nuevo_estado_id: estado.id })}
          className={`rounded-lg px-3 py-1 text-sm ${
            estado.codigo === 'CANCELADO'
              ? 'bg-red-50 text-red-600 hover:bg-red-100'
              : 'bg-slate-900 text-white hover:bg-slate-700'
          }`}
        >
          {estado.nombre}
        </button>
      ))}
    </div>
  )
}

export function PedidosTable({ data, onCambiarEstado }: PedidosTableProps) {
    const columns = [
        columnHelper.accessor('id', {
            header: 'ID',
            cell: (info) => `#${info.getValue()}`,
        }),
        columnHelper.accessor('usuario_id', {
            header: 'Cliente ID',
            cell: (info) => info.getValue(),
        }),
        columnHelper.accessor('estado_actual', {
            header: 'Estado',
            cell: (info) => {
                const estado = info.getValue()
                if (!estado) return '-'
                return (
                <span
                className={`rounded-full px-2 py-1 text-xs font-medium ${estadoColors[estado.codigo] ?? 'bg-slate-100 text-slate-700'}`}
                >
                    {estado.nombre}
                </span>
                )
            },
        }),
        columnHelper.accessor('total', {
            header: 'Total',
            cell: (info) => `$${info.getValue().toFixed(2)}`,
        }),
        columnHelper.accessor('fecha_pedido', {
            header: 'Fecha',
            cell: (info) => new Date(info.getValue()).toLocaleDateString('es-AR'),
        }),
        columnHelper.accessor('forma_pago', {
            header: 'Forma de Pago',
            cell: (info) => info.getValue()?.nombre ?? '-',
        }),
        columnHelper.display({
            id: 'acciones',
            header: 'Acciones',
            cell: (info) => (
                <AccionesCell 
                pedido={info.row.original}
                onCambiarEstado={onCambiarEstado}
                />
            ),
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
                                No hay pedidos
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