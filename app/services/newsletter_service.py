from app.models.newsletter import Newsletter, Suscripcion
from app.models.usuario import bandeja_newsletter
from sqlalchemy import desc

class NewsletterService:
    def __init__(self, session=None):
        self.session = session
        
    def get_by_usuario(self, usuario_id, limit=None):
        """Obtener newsletters recibidos por un usuario (Bandeja de Entrada)"""
        from app.models.usuario import bandeja_newsletter
        
        query = self.session.query(Newsletter).join(
            bandeja_newsletter, Newsletter.id_newsletter == bandeja_newsletter.c.id_newsletter
        ).filter(
            bandeja_newsletter.c.id_usuario == usuario_id
        ).order_by(desc(Newsletter.fecha_envio))
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
        
    def esta_suscrito(self, usuario_id, artista_id):
        """Indica si el cliente está suscrito al newsletter del artista."""
        return self.session.query(Suscripcion).filter_by(
            id_cliente=usuario_id,
            id_artista=artista_id,
        ).first() is not None

    def suscribir(self, usuario_id, artista_id):
        """Suscribir un usuario a un artista"""
        # Verificar si ya existe
        existe = self.session.query(Suscripcion).filter_by(
            id_cliente=usuario_id, id_artista=artista_id
        ).first()
        
        if existe:
            return True
            
        suscripcion = Suscripcion(id_cliente=usuario_id, id_artista=artista_id)
        self.session.add(suscripcion)
        try:
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False
        
    def get_artistas_suscritos(self, usuario_id):
        """Artistas a cuyo newsletter está suscrito el cliente."""
        from app.models.usuario import Usuario
        rows = self.session.query(Usuario).join(
            Suscripcion, Usuario.id_usuario == Suscripcion.id_artista
        ).filter(
            Suscripcion.id_cliente == usuario_id
        ).order_by(Usuario.nombre).all()
        return rows

    def count_suscripciones(self, usuario_id):
        return self.session.query(Suscripcion).filter_by(id_cliente=usuario_id).count()
        
    def desuscribir(self, usuario_id, artista_id):
        """Desuscribir un usuario de un artista"""
        suscripcion = self.session.query(Suscripcion).filter_by(
            id_cliente=usuario_id, id_artista=artista_id
        ).first()
        
        if suscripcion:
            self.session.delete(suscripcion)
            try:
                self.session.commit()
                return True
            except Exception:
                self.session.rollback()
                return False
        return True
