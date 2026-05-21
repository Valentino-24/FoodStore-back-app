import { create } from 'zustand'
import type { UserPublic } from '@/types/api'

interface AuthState {
    user: UserPublic | null
    isAuthenticated: boolean
    isLoading: boolean
    error: string | null
    setError: (error: string | null) => void
    checkAuth: () => Promise<void>
    login: (username: string, password: string) => Promise<void>
    logout: () => Promise<void>
    clearSession: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,

    setError: (error) => set({ error }),

    clearSession: () =>
        set({ user: null, isAuthenticated: false, isLoading: false }),

    checkAuth: async () => {
        const { requestMe } = await import('@/api/authApi')
        try {
            const user = await requestMe()
            set({ user, isAuthenticated: true, isLoading: false })
        } catch {
            set({ user: null, isAuthenticated: false, isLoading: false })
        }
    },

    login: async (username, password) => {
        const { requestLogin, requestMe } = await import('@/api/authApi')
        try {
            await requestLogin(username, password)
            const user = await requestMe()
            set({ user, isAuthenticated: true, error: null })
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Error al iniciar sesión'
            set({ error: message })
            throw error
        }
    },

    logout: async () => {
        const { requestLogout} = await import('@/api/authApi')
        try {
            await requestLogout()
        } finally {
            set({ user: null, isAuthenticated: false })
        }
    },
}))