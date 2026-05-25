import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/useAuthStore'

export function LoginPage() {
  const navigate = useNavigate()
  const login = useAuthStore((s) => s.login)
  const error = useAuthStore((s) => s.error)
  const setError = useAuthStore((s) => s.setError)

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    try {
      await login(username, password)
      navigate('/dashboard')
    } catch {
      // el error ya está en el store
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full overflow-hidden rounded-2xl shadow-lg">
      {/* Banner superior */}
      <div className="flex items-center justify-center bg-slate-900 py-10">
        <h1 className="text-2xl font-bold text-white tracking-wide">FoodStore</h1>
      </div>

      {/* Formulario */}
      <div className="bg-white px-8 py-8">
        <h2 className="mb-6 text-center text-xl font-bold text-slate-900">
          Inicio de Sesión
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Correo electrónico
            </label>
            <div className="flex items-center rounded-lg border border-slate-300 px-3 py-2 focus-within:border-slate-500">
              <span className="mr-2 text-slate-400">✉</span>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                disabled={isLoading}
                className="flex-1 text-sm text-slate-900 placeholder-slate-400 focus:outline-none disabled:bg-white"
                placeholder="admin@foodstore.com"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Contraseña
            </label>
            <div className="flex items-center rounded-lg border border-slate-300 px-3 py-2 focus-within:border-slate-500">
              <span className="mr-2 text-slate-400">🔒</span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
                className="flex-1 text-sm text-slate-900 placeholder-slate-400 focus:outline-none disabled:bg-white"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="mt-2 w-full rounded-lg bg-slate-900 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-50 transition-colors"
          >
            {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </button>
        </form>
      </div>
    </div>
  )
}