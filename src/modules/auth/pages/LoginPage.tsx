import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/useAuthStore";

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
            // El error ya está guardado en el store
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="flex h-screen items-center justify-center bg-zinc-50">
            <div className="w-full max-w-md rounded-xl border border-zinc-200 bg-white p-8 shadow-sm">
                <h1 className="mb-6 text-2x1 font-bold text-zinc-900">Inicar Sesión</h1>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {error && (
                        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
                            {error}
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-zinc-700">
                            Email
                        </label>
                        <input 
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            disabled={isLoading}
                            className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-2 text-zinc-900 placeholder-zinc-400 focus:border-zinc-500 focus:outline-none disabled:bg-zinc-100"
                            placeholder="tucorreo@email.com"
                         />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-zinc-700">
                            Contraseña
                        </label>
                        <input 
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            disabled={isLoading}
                            className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-2 text-zinc-900 placeholder-zinc-400 focus:border-zinc-500 focus:outline-none disabled:bg-zinc-100"
                            placeholder="Tu contraseña"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full rounded-lg bg-zinc-900 px-4 py-2 font-medium text-white hover:bg-zinc-800 disabled:opacity-50"    
                    >
                        {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
                    </button>

                </form>

            </div>
        </div>
    )
}