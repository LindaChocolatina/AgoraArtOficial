from datetime import datetime
from app.factories.app_factory import db

class Obra(db.Model):
    """
    Modelo de Obra basado en el script de base de datos
    Tabla: obras
    """
    __tablename__ = 'obras'
    
    id_obra = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_artista = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    imagen = db.Column(db.String(255), nullable=False)
    tecnica = db.Column(db.String(100))
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'))
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)
    visible = db.Column(db.Boolean, default=True)
    
    # Relaciones
    favoritos_usuarios = db.relationship('Usuario', secondary='favoritos_obras',
                                       lazy='subquery')
    lienzo_items = db.relationship('LienzoItem', backref='obra', lazy='dynamic',
                                  cascade='all, delete-orphan')
    galeria_imagenes = db.relationship(
        'ObraImagen', backref='obra', lazy='dynamic',
        cascade='all, delete-orphan', order_by='ObraImagen.orden'
    )
    
    def __repr__(self):
        return f'<Obra {self.titulo}>'
    
    def to_dict(self):
        """Convertir obra a diccionario para API responses"""
        favoritos_count = 0
        try:
            favoritos_count = self.favoritos_usuarios.count() if hasattr(self.favoritos_usuarios, 'count') else len(self.favoritos_usuarios)
        except:
            favoritos_count = 0
            
        return {
            'id_obra': self.id_obra,
            'id_artista': self.id_artista,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'imagen': self.imagen,
            'tecnica': self.tecnica,
            'id_categoria': self.id_categoria,
            'categoria_nombre': self.categoria.nombre if self.categoria else None,
            'fecha_publicacion': self.fecha_publicacion.isoformat() if self.fecha_publicacion else None,
            'visible': self.visible,
            'artista_nombre': self.artista.nombre if self.artista else None,
            'favoritos_count': favoritos_count,
            'en_lienzos': self.lienzo_items.count()
        }
    
    def is_visible(self):
        """Verificar si la obra es visible"""
        return self.visible
    
    def get_favoritos_count(self):
        """Obtener cantidad de favoritos"""
        try:
            return self.favoritos_usuarios.count() if hasattr(self.favoritos_usuarios, 'count') else len(self.favoritos_usuarios)
        except:
            return 0
    
    def esta_en_favoritos(self, usuario):
        """Verificar si la obra está en favoritos de un usuario"""
        return usuario in self.favoritos_usuarios
    
    @staticmethod
    def get_publicas(limit=None, offset=None, categoria_id=None):
        """Obtener obras públicas con filtros opcionales"""
        query = Obra.query.filter_by(visible=True).order_by(Obra.fecha_publicacion.desc())
        
        if categoria_id:
            query = query.filter_by(id_categoria=categoria_id)
        
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return query.all()
    
    @staticmethod
    def buscar_por_titulo(titulo, limit=None):
        """Buscar obras por título"""
        query = Obra.query.filter(
            Obra.visible == True,
            Obra.titulo.contains(titulo)
        ).order_by(Obra.fecha_publicacion.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
