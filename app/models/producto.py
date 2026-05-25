from datetime import datetime
from sqlalchemy import text
from app.factories.app_factory import db

class Producto(db.Model):
    """
    Modelo de Producto basado en el script de base de datos
    Tabla: productos
    """
    __tablename__ = 'productos'
    
    id_producto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_artista = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    moneda = db.Column(db.String(3), nullable=False, default='COP')
    stock = db.Column(db.Integer, default=0)
    imagen = db.Column(db.String(255))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Estado calculado automáticamente desde stock
    estado = db.Column(db.String(20), default='disponible')
    
    # Relaciones
    orden_items = db.relationship('OrdenItem', backref='producto', lazy='dynamic',
                                 cascade='all, delete-orphan')
    imagenes = db.relationship('ProductoImagen', backref='producto', lazy='dynamic',
                               cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'
    
    def to_dict(self):
        """Convertir producto a diccionario para API responses"""
        return {
            'id_producto': self.id_producto,
            'id_artista': self.id_artista,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': float(self.precio),
            'moneda': self.moneda or 'COP',
            'stock': self.stock,
            'imagen': self.imagen,
            'estado': self.estado,
            'artista_nombre': self.artista.nombre if self.artista else None,
            'ventas_count': self.get_ventas_count()
        }
    
    def is_disponible(self):
        """Verificar si el producto está disponible"""
        return self.stock > 0
    
    def get_ventas_count(self):
        """Obtener cantidad total vendida"""
        from sqlalchemy import func
        
        result = db.session.query(
            func.sum(OrdenItem.cantidad)
        ).filter_by(id_producto=self.id_producto).scalar()
        
        return result or 0
    
    def actualizar_stock(self, cantidad, motivo=None):
        """Actualizar stock y registrar en historial"""
        stock_anterior = self.stock
        self.stock += cantidad
        
        # Crear registro en historial de stock
        historial = HistorialStock(
            id_producto=self.id_producto,
            cambio=cantidad,
            stock_anterior=stock_anterior,
            stock_actual=self.stock,
            motivo=motivo
        )
        db.session.add(historial)
    
    def reducir_stock(self, cantidad):
        """Reducir stock para venta"""
        if self.stock >= cantidad:
            self.actualizar_stock(-cantidad, f"Venta de {cantidad} unidades")
            return True
        return False
    
    @staticmethod
    def get_disponibles(limit=None, offset=None):
        """Obtener productos disponibles"""
        query = Producto.query.filter(Producto.stock > 0).order_by(Producto.fecha_creacion.desc())
        
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return query.all()
    
    @staticmethod
    def buscar_por_nombre(nombre, limit=None):
        """Buscar productos por nombre"""
        query = Producto.query.filter(
            Producto.stock > 0,
            Producto.nombre.contains(nombre)
        ).order_by(Producto.nombre)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()

class HistorialStock(db.Model):
    """
    Modelo para historial de cambios en stock
    Tabla: historial_stock
    """
    __tablename__ = 'historial_stock'
    
    id_historial = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    cambio = db.Column(db.Integer, nullable=False)
    stock_anterior = db.Column(db.Integer, nullable=False)
    stock_actual = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación
    producto = db.relationship('Producto', backref=db.backref('historial_stock', lazy='dynamic'))
    
    def __repr__(self):
        return f'<HistorialStock Producto:{self.id_producto} Cambio:{self.cambio}>'
