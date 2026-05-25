import { useAuthStore } from '@/stores/useAuthStore'

export function DashboardPage() {
  const user = useAuthStore((s) => s.user)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-sm text-slate-500">
          Bienvenido de vuelta, {user?.nombre}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <p className="text-sm font-medium text-slate-500">Productos</p>
          <p className="mt-1 text-3xl font-bold text-slate-900">—</p>
          <p className="mt-1 text-xs text-slate-400">Total en catálogo</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <p className="text-sm font-medium text-slate-500">Categorías</p>
          <p className="mt-1 text-3xl font-bold text-slate-900">—</p>
          <p className="mt-1 text-xs text-slate-400">Total registradas</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <p className="text-sm font-medium text-slate-500">Ingredientes</p>
          <p className="mt-1 text-3xl font-bold text-slate-900">—</p>
          <p className="mt-1 text-xs text-slate-400">Total registrados</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <p className="text-sm font-medium text-slate-500">Pedidos</p>
          <p className="mt-1 text-3xl font-bold text-slate-900">—</p>
          <p className="mt-1 text-xs text-slate-400">Total recibidos</p>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6">
        <h2 className="text-base font-semibold text-slate-900 mb-1">
          Panel de Administración
        </h2>
        <p className="text-sm text-slate-500">
          Usá el menú lateral para navegar entre los módulos del sistema.
          Rol activo: <span className="font-medium text-slate-700">{user?.rol}</span>
        </p>
      </div>
    </div>
  )
}