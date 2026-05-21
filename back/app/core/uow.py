from sqlmodel import Session
from app.core.database import engine
from app.repositories.producto_repository import ProductoRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.ingrediente_repository import IngredienteRepository
from app.repositories.usuario_repository import UsuarioRepository


class UnitOfWork:

    def __init__(self):
        self.session = Session(engine)
        self._productos: ProductoRepository | None = None
        self._categorias: CategoriaRepository | None = None
        self._ingredientes: IngredienteRepository | None = None
        self._usuarios: UsuarioRepository | None = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    @property
    def productos(self) -> ProductoRepository:
        if self._productos is None:
            self._productos = ProductoRepository(self.session)
        return self._productos

    @property
    def categorias(self) -> CategoriaRepository:
        if self._categorias is None:
            self._categorias = CategoriaRepository(self.session)
        return self._categorias

    @property
    def ingredientes(self) -> IngredienteRepository:
        if self._ingredientes is None:
            self._ingredientes = IngredienteRepository(self.session)
        return self._ingredientes

    @property
    def usuarios(self) -> UsuarioRepository:
        if self._usuarios is None:
            self._usuarios = UsuarioRepository(self.session)
        return self._usuarios
