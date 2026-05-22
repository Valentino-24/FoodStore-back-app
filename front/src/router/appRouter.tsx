import { createBrowserRouter, RouterProvider, Navigate } from "react-router-dom";
import { PrivateRoute } from "./PrivateRoute";
import { PublicRoute } from "./PublicRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { LoginPage } from "@/modules/auth/pages/LoginPage";
import { DashboardPage } from "@/modules/dashboard/pages/DashboardPage";

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
        ],
    },
])

export function AppRouter() {
    return <RouterProvider router={router} />
}