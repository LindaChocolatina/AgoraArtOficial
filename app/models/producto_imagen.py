from datetime import datetime
from app.factories.app_factory import db

class ProductoImagen(db.Model):
    __tablename__ = 'producto_imagenes'

    id_imagen = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    imagen = db.Column(db.String(255), nullable=False)
    orden = db.Column(db.Integer, default=0)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ProductoImagen {self.id_imagen} producto={self.id_producto}>'
