from sqlmodel import Session
from app.core.database import engine
from app.repositories.producto_repository import ProductoRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.ingrediente_repository import IngredienteRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.pedido_repository import PedidoRepository, DetallePedidoRepository, HistorialEstadoPedidoRepository
from app.repositories.direccion_repository import DireccionRepository
from app.repositories.rol_repository import RolRepository
from app.repositories.unidad_medida_repository import UnidadMedidaRepository
from app.repositories.pago_repository import PagoRepository
from app.repositories.usuario_rol_repository import UsuarioRolRepository
from app.repositories.producto_categoria_repository import ProductoCategoriaRepository
from app.repositories.producto_ingrediente_repository import ProductoIngredienteRepository
from app.repositories.estado_pedido_repository import EstadoPedidoRepository
from app.repositories.forma_pago_repository import FormaPagoRepository

class UnitOfWork:

    def __init__(self):
        self.session = Session(engine)
        self._productos: ProductoRepository | None = None
        self._categorias: CategoriaRepository | None = None
        self._ingredientes: IngredienteRepository | None = None
        self._usuarios: UsuarioRepository | None = None
        self._pedidos: PedidoRepository | None = None
        self._detalles_pedido: DetallePedidoRepository | None = None
        self._historial_estados: HistorialEstadoPedidoRepository | None = None
        self._direcciones: DireccionRepository | None = None
        self._roles: RolRepository | None = None
        self._unidades_medida: UnidadMedidaRepository | None = None
        self._pagos: PagoRepository | None = None
        self._usuarios_roles: UsuarioRolRepository | None = None
        self._productos_categoria: ProductoCategoriaRepository | None = None
        self._productos_ingrediente: ProductoIngredienteRepository | None = None
        self._estados_pedido: EstadoPedidoRepository | None = None
        self._formas_pago: FormaPagoRepository | None = None

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

    @property
    def pedidos(self) -> PedidoRepository:
        if self._pedidos is None:
            self._pedidos = PedidoRepository(self.session)
        return self._pedidos

    @property
    def detalles_pedido(self) -> DetallePedidoRepository:
        if self._detalles_pedido is None:
            self._detalles_pedido = DetallePedidoRepository(self.session)
        return self._detalles_pedido

    @property
    def historial_estados(self) -> HistorialEstadoPedidoRepository:
        if self._historial_estados is None:
            self._historial_estados = HistorialEstadoPedidoRepository(self.session)
        return self._historial_estados

    @property
    def direcciones(self) -> DireccionRepository:
        if self._direcciones is None:
            self._direcciones = DireccionRepository(self.session)
        return self._direcciones

    @property
    def roles(self) -> RolRepository:
        if self._roles is None:
            self._roles = RolRepository(self.session)
        return self._roles

    @property
    def unidades_medida(self) -> UnidadMedidaRepository:
        if self._unidades_medida is None:
            self._unidades_medida = UnidadMedidaRepository(self.session)
        return self._unidades_medida

    @property
    def pagos(self) -> PagoRepository:
        if self._pagos is None:
            self._pagos = PagoRepository(self.session)
        return self._pagos

    @property
    def usuarios_roles(self) -> UsuarioRolRepository:
        if self._usuarios_roles is None:
            self._usuarios_roles = UsuarioRolRepository(self.session)
        return self._usuarios_roles

    @property
    def productos_categoria(self) -> ProductoCategoriaRepository:
        if self._productos_categoria is None:
            self._productos_categoria = ProductoCategoriaRepository(self.session)
        return self._productos_categoria

    @property
    def productos_ingrediente(self) -> ProductoIngredienteRepository:
        if self._productos_ingrediente is None:
            self._productos_ingrediente = ProductoIngredienteRepository(self.session)
        return self._productos_ingrediente

    @property
    def estados_pedido(self) -> EstadoPedidoRepository:
        if self._estados_pedido is None:
            self._estados_pedido = EstadoPedidoRepository(self.session)
        return self._estados_pedido

    @property
    def formas_pago(self) -> FormaPagoRepository:
        if self._formas_pago is None:
            self._formas_pago = FormaPagoRepository(self.session)
        return self._formas_pago