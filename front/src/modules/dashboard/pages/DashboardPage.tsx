import { useAuthStore } from '@/stores/useAuthStore'

export function DashboardPage() {
  const user = useAuthStore((s) => s.user)

  return (
    <div>
      <h1 className="mb-2 text-2xl font-bold text-zinc-900">Dashboard</h1>
      <p className="text-zinc-600">Bienvenido, {user?.full_name}</p>
      <p className="mt-1 text-sm text-zinc-500">Roles: {user?.roles.join(', ')}</p>
    </div>
  )
}