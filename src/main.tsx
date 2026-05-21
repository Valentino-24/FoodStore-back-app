import { StrictMode } from "react";
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppRouter } from "./router/appRouter";
import { InitApp } from "./components/InitApp";
import "./index.css"

const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <QueryClientProvider client={queryClient}>
            <InitApp>
                <AppRouter />
            </InitApp>
        </QueryClientProvider>
    </StrictMode>
)