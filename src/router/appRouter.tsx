import { createBrowserRouter, RouterProvider, Navigate } from "react-router-dom";
import { PrivateRoute } from "./PrivateRoute";
import { PublicRoute } from "./PublicRoute";
import { LoginPage } from "@/modules/auth/pages/LoginPage";
import { DashboardPage } from "@/modules/dashboard/pages/DashboardPage";

const router = createBrowserRouter([
    {
        path: '/',
        element: <Navigate to="/dashboard" replace/>
    },
    {
        path: '/auth/login',
        element: (
            <PublicRoute>
                <LoginPage />
            </PublicRoute>
        ),
    },
    {
        path: '/dashboard',
        element: (
            <PrivateRoute>
                <DashboardPage />
            </PrivateRoute>
        ),
    },
])

export function AppRouter() {
    return <RouterProvider router={router} />
}