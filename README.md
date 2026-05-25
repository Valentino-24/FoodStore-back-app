# FoodStore — Sistema de Gestión

Sistema fullstack de gestión para una tienda de comida. Compuesto por un backend en FastAPI y un panel de administración en React.

## Estructura del repositorio

```text
FoodStore-admin-app/
├── back/    # API REST con FastAPI + PostgreSQL
└── front/   # Panel de administración con React
```

## Backend (`/back`)

API REST desarrollada con FastAPI y PostgreSQL.

### Tecnologías
- Python + FastAPI
- SQLModel + PostgreSQL
- JWT en cookie httpOnly
- bcrypt para hash de contraseñas

### Patrones implementados
- Repository Pattern con `BaseRepository[T]` genérico
- Service Layer — lógica de negocio separada del router
- Unit of Work — gestión transaccional atómica
- Soft Delete — `deleted_at` en todas las entidades
- Snapshot Pattern — precio y nombre inmutables en `DetallePedido`
- Audit Trail Append-Only — `HistorialEstadoPedido` solo permite INSERTs

### Módulos
- Autenticación (`/auth`) — registro, login, logout, `/me`
- Categorías (`/categorias`) — CRUD con jerarquía por `parent_id`
- Ingredientes (`/ingredientes`) — CRUD con campo `es_alergeno`
- Productos (`/productos`) — CRUD con relaciones a categorías e ingredientes
- Pedidos (`/pedidos`) — máquina de 6 estados con historial
- Administración (`/admin`) — gestión de usuarios y roles

### Roles
| Rol | Capacidades |
|-----|-------------|
| ADMIN | CRUD completo de todo el sistema |
| STOCK | Leer productos, actualizar disponibilidad |
| PEDIDOS | Ver y avanzar estados de pedidos |
| CLIENT | Catálogo, carrito, pedidos propios |

### Instalación

```bash
cd back
pip install -r requirements.txt
```

Configurar variables de entorno y correr:

```bash
uvicorn app.main:app --reload
```

La documentación de la API estará disponible en `http://localhost:8000/docs`.

## Frontend (`/front`)

Panel de administración desarrollado con React + TypeScript.

### Tecnologías
- React 19 + TypeScript + Vite
- Tailwind CSS v4
- React Router DOM v7
- TanStack Query v5
- TanStack Table v8
- Axios
- Zustand v5

### Instalación

```bash
cd front
pnpm install
```

Crear `.env` basándose en `.env.example`:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Correr el proyecto:

```bash
pnpm dev
```

La app estará disponible en `http://localhost:5173`.

### Módulos
- **Auth** — login con JWT en cookie httpOnly
- **Categorías** — CRUD con soporte de subcategorías via `parent_id`
- **Ingredientes** — CRUD con indicador de alérgenos
- **Productos** — CRUD con relaciones a categorías e ingredientes
- **Pedidos** — gestión de estados para cajero
- **Usuarios** — gestión de usuarios (solo ADMIN)

### Protección de rutas
Las rutas están protegidas por autenticación y por rol usando `PrivateRoute`. El rol ADMIN tiene acceso completo, el rol PEDIDOS solo accede a la sección de pedidos.
