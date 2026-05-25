import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  createColumnHelper,
} from '@tanstack/react-table'
import type { Categoria } from '@/api/categoriasApi'

interface CategoriasTableProps {
  data: Categoria[]
  categorias: Categoria[]
  isAdmin: boolean
  onEdit: (categoria: Categoria) => void
  onDelete: (id: number) => void
}

const columnHelper = createColumnHelper<Categoria>()

export function CategoriasTable({
  data,
  categorias,
  isAdmin,
  onEdit,
  onDelete,
}: CategoriasTableProps) {
  const columns = [
    columnHelper.accessor('id', {
      header: 'ID',
      cell: (info) => (
        <span className="text-slate-400 text-xs">#{info.getValue()}</span>
      ),
    }),
    columnHelper.accessor('nombre', {
      header: 'Nombre',
      cell: (info) => (
        <span className="font-medium text-slate-900">{info.getValue()}</span>
      ),
    }),
    columnHelper.accessor('descripcion', {
      header: 'Descripción',
      cell: (info) => (
        <span className="text-slate-500">{info.getValue() ?? '—'}</span>
      ),
    }),
    columnHelper.accessor('parent_id', {
      header: 'Categoría Padre',
      cell: (info) => {
        const parentId = info.getValue()
        if (!parentId) return <span className="text-slate-400">—</span>
        const parent = categorias.find((c) => c.id === parentId)
        return (
          <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
            {parent ? parent.nombre : parentId}
          </span>
        )
      },
    }),
    columnHelper.display({
      id: 'acciones',
      header: 'Acciones',
      cell: (info) =>
        isAdmin ? (
          <div className="flex gap-2">
            <button
              onClick={() => onEdit(info.row.original)}
              className="rounded-lg border border-slate-200 px-3 py-1 text-sm text-slate-600 hover:bg-slate-50 transition-colors"
            >
              Editar
            </button>
            <button
              onClick={() => onDelete(info.row.original.id)}
              className="rounded-lg border border-red-200 px-3 py-1 text-sm text-red-500 hover:bg-red-50 transition-colors"
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
                No hay categorías cargadas
              </td>
            </tr>
          ) : (
            table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                className="hover:bg-slate-50 transition-colors"
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