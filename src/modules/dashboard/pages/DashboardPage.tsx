import { useAuthStore } from "@/stores/useAuthStore";

export function DashboardPage() {
    const user = useAuthStore((s) => s.user)
    const logout = useAuthStore((s) => s.logout)

    return (
        <div className="flex h-screen items-center justify-center bg-zinc-50">
            <div className="w-full max-w-md rounded-xl border border-zinc-200 bg-white p-8 shadow-sm">
                <h1 className="mb-2 text-2x1 font-bold text-zinc-900">Dashboard</h1>
                <p className="mb-6 text-zinc-600">
                    Bienvenido, {user?.full_name}
                </p>
                <p className="mb-6 text-sm text-zinc-500">
                    Roles: {user?.roles.join(', ')}
                </p>
                <button
                    onClick={() =>logout()}
                    className="w-full rounded-lg bg-zinc-900 px-4 py-2 font-medium text-white hover:bg-zinc-800"
                >
                    Cerrar Sesión
                </button>
            </div>
        </div>
    )
}