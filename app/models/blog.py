from datetime import datetime
import re
from app.factories.app_factory import db

_IMG_SRC_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.I)

class EntradaBlog(db.Model):
    """
    Modelo de Entrada de Blog basado en el script de base de datos
    Tabla: entradas_blog
    """
    __tablename__ = 'entradas_blog'
    
    id_entrada = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_artista = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)
    visible = db.Column(db.Boolean, default=True)
    
    # Relaciones
    comentarios = db.relationship('ComentarioBlog', backref='entrada', lazy='dynamic',
                                 cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<EntradaBlog {self.titulo}>'
    
    def to_dict(self):
        """Convertir entrada a diccionario para API responses"""
        return {
            'id_entrada': self.id_entrada,
            'id_artista': self.id_artista,
            'titulo': self.titulo,
            'contenido': self.contenido,
            'fecha_publicacion': self.fecha_publicacion.isoformat() if self.fecha_publicacion else None,
            'visible': self.visible,
            'artista_nombre': self.artista.nombre if self.artista else None,
            'comentarios_count': self.get_comentarios_count()
        }
    
    def get_comentarios_count(self):
        """Obtener cantidad de comentarios"""
        return self.comentarios.count()
    
    def is_visible(self):
        """Verificar si la entrada es visible"""
        return self.visible

    def imagen_miniatura(self):
        """Primera imagen embebida en el contenido HTML del editor."""
        if not self.contenido:
            return None
        match = _IMG_SRC_RE.search(self.contenido)
        return match.group(1) if match else None
    
    @staticmethod
    def get_publicas(limit=None, offset=None):
        """Obtener entradas públicas"""
        query = EntradaBlog.query.filter_by(visible=True).order_by(
            EntradaBlog.fecha_publicacion.desc()
        )
        
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return query.all()

class ComentarioBlog(db.Model):
    """
    Modelo de Comentario de Blog basado en el script de base de datos
    Tabla: comentarios_blog
    """
    __tablename__ = 'comentarios_blog'
    
    id_comentario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_entrada = db.Column(db.Integer, db.ForeignKey('entradas_blog.id_entrada'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ComentarioBlog Entrada:{self.id_entrada} Usuario:{self.id_usuario}>'
    
    def to_dict(self):
        """Convertir comentario a diccionario para API responses"""
        return {
            'id_comentario': self.id_comentario,
            'id_entrada': self.id_entrada,
            'id_usuario': self.id_usuario,
            'contenido': self.contenido,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'usuario_nombre': self.usuario.nombre if self.usuario else None,
            'usuario_username': self.usuario.username if self.usuario else None
        }
