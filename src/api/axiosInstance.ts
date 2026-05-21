import axios, { type AxiosError, type AxiosResponse } from 'axios'
import { useAuthStore } from '@/stores/useAuthStore'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

apiClient.interceptors.request.use(
    (config) => {
        return config
    },
    (error: AxiosError) => {
        console.error('Error en request:', error)
        return Promise.reject(error)
    },
)

apiClient.interceptors.response.use(
    (response: AxiosResponse) => {
        return response
    },
    async (error: AxiosError) => {
        if (error.response?.status === 401) {
            console.warn('Sesión expirada (401), limpiando...')
            useAuthStore.getState().clearSession()
        }
        return Promise.reject(error)
    },
)

export default apiClient