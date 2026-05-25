import { Outlet, NavLink } from 'react-router-dom'
import { useAuthStore } from '@/stores/useAuthStore'
import { useNavigate } from 'react-router-dom'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: '⊞' },
  { to: '/categorias', label: 'Categorías', icon: '◫' },
  { to: '/ingredientes', label: 'Ingredientes', icon: '⚗' },
  { to: '/productos', label: 'Productos', icon: '▦' },
  { to: '/pedidos', label: 'Pedidos', icon: '🗒' },
  { to: '/usuarios', label: 'Usuarios', icon: '👤' },
]

export function AppLayout() {
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/auth/login')
  }

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="flex w-60 flex-col border-r border-slate-200 bg-white">
        {/* Logo */}
        <div className="px-6 py-5 border-b border-slate-100">
          <h1 className="text-lg font-bold text-slate-900">FoodStore</h1>
          <p className="text-xs text-slate-400 mt-0.5">{user?.rol ?? 'Admin'}</p>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-slate-900 text-white'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`
              }
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="border-t border-slate-100 p-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-900 text-white text-xs font-bold">
              {user?.nombre?.charAt(0).toUpperCase() ?? 'A'}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-slate-900 truncate">{user?.nombre}</p>
              <p className="text-xs text-slate-400 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <span>⎋</span>
            Cerrar Sesión
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header className="flex h-14 items-center justify-between border-b border-slate-200 bg-white px-6">
          <div className="flex items-center gap-3">
            <input
              type="text"
              placeholder="Buscar..."
              className="w-64 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:border-slate-400"
            />
          </div>
          <div className="flex items-center gap-3">
            <button className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100">
              🔔
            </button>
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-900 text-white text-xs font-bold">
              {user?.nombre?.charAt(0).toUpperCase() ?? 'A'}
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}