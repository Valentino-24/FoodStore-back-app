import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/useAuthStore";

export function AppLayout() {
    const user = useAuthStore((s) => s.user)
    const logout = useAuthStore((s) => s.logout)
    const navigate = useNavigate()

    const handleLogout = async () => {
        await logout()
        navigate('/auth/login')
    }

    return (
        <div className="flex h-screen bg-zinc-50">
            {/* Sidebar */}
            <aside className="flex w-64 flex-col border-r border-zinc-200 bg-white">
                <div className="border-b border-zinc-200 p-6">
                    <h1 className="text-xl font-bold text-zinc-900">FoodStore</h1>
                    <p className="text-sm text-zinc-500">Panel de Administración</p>
                </div>

                <nav className="flex-1 space-y-1 p-4">
                    <NavLink
                    to="/dashboard"
                    className={({ isActive }) =>
                        `block rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                            isActive
                                ? 'bg-zinc-900 text-white'
                                : 'text-zinc-600 hover:bg-zinc-100'
                        }`
                      }
                    >
                        Dashboard
                    </NavLink>
                    <NavLink 
                    to="/categorias" 
                    className={({ isActive }) =>
                        `block rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                            isActive
                                ? 'bg-zinc-900 text-white'
                                : 'text-zinc-600 hover:bg-zinc-100'
                        }`
                      }
                    >
                        Categorías
                    </NavLink>
                    <NavLink
                    to="/ingredientes"
                    className={({ isActive }) =>
                        `block rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                            isActive
                                ? 'bg-zinc-900 text-white'
                                : 'text-zinc-600 hover:bg-zinc-100'
                        }`
                      }
                    >
                        Ingredientes
                    </NavLink>
                    <NavLink
                    to="/productos"
                    className={({ isActive }) =>
                        `block rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                            isActive
                                ? 'bg-zinc-900 text-white'
                                : 'text-zinc-600 hover:bg-zinc-100'
                        }`
                      }
                    >
                        Productos
                    </NavLink>
                    <NavLink
                    to="/pedidos"
                    className={({ isActive }) =>
                        `block rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                            isActive
                                ? 'bg-zinc-900 text-white'
                                : 'text-zinc-600 hover:bg-zinc-100'
                        }`
                      }
                    >
                        Pedidos
                    </NavLink>
                    <NavLink
                    to="/ususarios"
                    className={({ isActive }) =>
                        `block rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                            isActive
                                ? 'bg-zinc-900 text-white'
                                : 'text-zinc-600 hover:bg-zinc-100'
                        }`
                      }
                    >
                        Usuarios
                    </NavLink>
                </nav>

                <div className="border-t border-zinc-200 p-4">
                    <p className="text-sm font-medium text-zinc-900">{user?.full_name}</p>
                    <p className="text-xs text-zinc-500">{user?.roles.join(', ')}</p>
                    <button
                        onClick={handleLogout}
                        className="mt-3 w-full rounded-lg border border-zinc-200 px-3 py-2 text-sm text-zinc-600 hover:bg-zinc-100"
                    >
                        Cerrar Sesión
                    </button>
                </div>
            </aside>

            {/* Contenido principal */}
            <main className="flex-1 overflow-y-auto p-8">
                <Outlet />
            </main>
        </div>
    )
}