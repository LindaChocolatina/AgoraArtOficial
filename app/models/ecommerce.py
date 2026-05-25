from datetime import datetime
from app.factories.app_factory import db

class Direccion(db.Model):
    """
    Modelo de Dirección basado en el script de base de datos
    Tabla: direcciones
    """
    __tablename__ = 'direcciones'
    
    id_direccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    nombre_receptor = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    pais = db.Column(db.String(100), nullable=False)
    codigo_postal = db.Column(db.String(20))
    telefono = db.Column(db.String(30))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    ordenes = db.relationship('Orden', backref='direccion_envio', lazy='dynamic')
    
    def __repr__(self):
        return f'<Direccion {self.direccion}, {self.ciudad}>'
    
    def to_dict(self):
        """Convertir dirección a diccionario para API responses"""
        return {
            'id_direccion': self.id_direccion,
            'id_usuario': self.id_usuario,
            'nombre_receptor': self.nombre_receptor,
            'direccion': self.direccion,
            'ciudad': self.ciudad,
            'pais': self.pais,
            'codigo_postal': self.codigo_postal,
            'telefono': self.telefono,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'ordenes_count': self.ordenes.count()
        }
    
    def tiene_ordenes_asociadas(self):
        """Verificar si la dirección tiene órdenes asociadas"""
        return self.ordenes.count() > 0

    def direccion_completa(self):
        partes = [self.direccion, self.ciudad, self.pais]
        if self.codigo_postal:
            partes.append(f'CP {self.codigo_postal}')
        return ', '.join(p for p in partes if p)

class Orden(db.Model):
    """
    Modelo de Orden basado en el script de base de datos
    Tabla: ordenes
    """
    __tablename__ = 'ordenes'
    
    id_orden = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_direccion = db.Column(db.Integer, db.ForeignKey('direcciones.id_direccion'), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, pagada, cancelada, reembolsada
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    items = db.relationship('OrdenItem', backref='orden', lazy='dynamic',
                          cascade='all, delete-orphan')
    pagos = db.relationship('Pago', backref='orden', lazy='dynamic',
                           cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Orden {self.id_orden} Cliente:{self.id_cliente}>'
    
    def to_dict(self):
        """Convertir orden a diccionario para API responses"""
        return {
            'id_orden': self.id_orden,
            'id_cliente': self.id_cliente,
            'id_direccion': self.id_direccion,
            'total': float(self.total),
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'items_count': self.items.count(),
            'direccion_completa': self.direccion_envio.direccion_completa() if self.direccion_envio else None
        }
    
    def calcular_total(self):
        """Calcular total de la orden basado en items"""
        total = 0
        for item in self.items:
            total += item.subtotal
        self.total = total
        return total
    
    def get_items_count(self):
        """Obtener cantidad total de items"""
        result = db.session.query(db.func.sum(OrdenItem.cantidad)).filter_by(id_orden=self.id_orden).scalar()
        return result or 0

class OrdenItem(db.Model):
    """
    Modelo de Item de Orden basado en el script de base de datos
    Tabla: orden_items
    """
    __tablename__ = 'orden_items'
    
    id_orden = db.Column(db.Integer, db.ForeignKey('ordenes.id_orden'), primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    
    def __repr__(self):
        return f'<OrdenItem Orden:{self.id_orden} Producto:{self.id_producto}>'
    
    def to_dict(self):
        """Convertir item a diccionario para API responses"""
        return {
            'id_orden': self.id_orden,
            'id_producto': self.id_producto,
            'cantidad': self.cantidad,
            'precio_unitario': float(self.precio_unitario),
            'subtotal': float(self.subtotal),
            'producto_nombre': self.producto.nombre if self.producto else None
        }
    
    def calcular_subtotal(self):
        """Calcular subtotal del item"""
        self.subtotal = self.cantidad * self.precio_unitario
        return self.subtotal

class Pago(db.Model):
    """
    Modelo de Pago basado en el script de base de datos
    Tabla: pagos
    """
    __tablename__ = 'pagos'
    
    id_pago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_orden = db.Column(db.Integer, db.ForeignKey('ordenes.id_orden'), nullable=False)
    proveedor = db.Column(db.String(50), nullable=False)  # Stripe, PayPal, etc.
    referencia = db.Column(db.String(150), nullable=False)
    estado = db.Column(db.String(20), nullable=False)  # aprobado, rechazado, pendiente
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Pago {self.referencia} Estado:{self.estado}>'
    
    def to_dict(self):
        """Convertir pago a diccionario para API responses"""
        return {
            'id_pago': self.id_pago,
            'id_orden': self.id_orden,
            'proveedor': self.proveedor,
            'referencia': self.referencia,
            'estado': self.estado,
            'monto': float(self.monto),
            'fecha_pago': self.fecha_pago.isoformat() if self.fecha_pago else None
        }
    
    def is_aprobado(self):
        """Verificar si el pago está aprobado"""
        return self.estado == 'aprobado'
