import { createBrowserRouter, RouterProvider, Navigate } from "react-router-dom";
import { PrivateRoute } from "./PrivateRoute";
import { PublicRoute } from "./PublicRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { LoginPage } from "@/modules/auth/pages/LoginPage";
import { DashboardPage } from "@/modules/dashboard/pages/DashboardPage";
import { CategoriasPage } from "@/modules/categorias/pages/CategoriasPage";
import { IngredientesPage } from "@/modules/ingredientes/pages/IngredientesPage";
import { ProductosPage } from "@/modules/productos/pages/ProductosPage";

const router = createBrowserRouter([
    {
        path: '/',
        element: <Navigate to="/dashboard" replace/>
    },
    {
        path: '/auth',
        element: (
            <PublicRoute>
                <AuthLayout />
            </PublicRoute>
        ),
        children: [
            {
                path: 'login',
                element: <LoginPage />,
            },
        ],
    },
    {
        path: '/',
        element: (
            <PrivateRoute>
                <AppLayout />
            </PrivateRoute>
        ),
        children: [
            {
                path: 'dashboard',
                element: <DashboardPage />,
            },
            {
                path: 'categorias',
                element: <CategoriasPage />
            },
            {
                path: 'ingredientes',
                element: <IngredientesPage />,
            },
            {
                path: 'productos',
                element: <ProductosPage />,
            },
        ],
    },
])

export function AppRouter() {
    return <RouterProvider router={router} />
}