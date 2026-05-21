import { Navigate } from "react-router-dom";
import { useAuthStore } from "@/stores/useAuthStore";
import type { ReactNode } from "react";

interface PublicRouteProps {
    children: ReactNode
}

export function PublicRoute({ children }: PublicRouteProps) {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
    const isLoading = useAuthStore((s) => s.isLoading)

    if (isLoading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <p className="text-zinc-500">Cargando...</p>
            </div>
        )
    }

    if (isAuthenticated) {
        return <Navigate to="/dashboard" replace/>
    }

    return <>{children}</>
}