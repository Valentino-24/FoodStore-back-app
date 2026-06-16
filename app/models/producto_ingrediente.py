from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class ProductoIngrediente(SQLModel, table=True):
    __tablename__ = "producto_ingrediente"

    producto_id: Optional[int] = Field(
        default=None, foreign_key="producto.id", primary_key=True
    )
    ingrediente_id: Optional[int] = Field(
        default=None, foreign_key="ingrediente.id", primary_key=True
    )

    es_removible: bool = True
    cantidad: Optional[float] = Field(default=None, sa_column_kwargs={"nullable": True})
    unidad_medida_id: Optional[int] = Field(
        default=None, foreign_key="unidad_medida.id"
    )

    producto: Optional["Producto"] = Relationship(back_populates="ingredientes")
    ingrediente: Optional["Ingrediente"] = Relationship(back_populates="productos")