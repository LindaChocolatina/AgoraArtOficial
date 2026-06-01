from app.models.newsletter import Newsletter, Suscripcion
from app.models.usuario import bandeja_newsletter
from sqlalchemy import desc, func


class NewsletterService:
    def __init__(self, session=None):
        self.session = session

    def _inbox_query(self, usuario_id):
        return self.session.query(
            Newsletter,
            bandeja_newsletter.c.leido,
        ).join(
            bandeja_newsletter,
            Newsletter.id_newsletter == bandeja_newsletter.c.id_newsletter,
        ).filter(
            bandeja_newsletter.c.id_usuario == usuario_id,
        ).order_by(desc(Newsletter.fecha_envio))

    def get_by_usuario(self, usuario_id, limit=None):
        """Obtener newsletters recibidos por un usuario (Bandeja de Entrada)."""
        query = self._inbox_query(usuario_id)
        if limit:
            query = query.limit(limit)
        return [row[0] for row in query.all()]

    def get_inbox(self, usuario_id, limit=None):
        """Newsletters recibidos con estado de lectura."""
        query = self._inbox_query(usuario_id)
        if limit:
            query = query.limit(limit)
        return query.all()

    def count_no_leidos(self, usuario_id):
        return self.session.query(func.count()).select_from(bandeja_newsletter).filter(
            bandeja_newsletter.c.id_usuario == usuario_id,
            bandeja_newsletter.c.leido.is_(False),
        ).scalar() or 0

    def get_para_cliente(self, usuario_id, newsletter_id):
        """Newsletter en la bandeja del cliente, o None si no le pertenece."""
        return self._inbox_query(usuario_id).filter(
            Newsletter.id_newsletter == newsletter_id,
        ).first()

    def marcar_leido(self, usuario_id, newsletter_id):
        updated = self.session.execute(
            bandeja_newsletter.update().where(
                bandeja_newsletter.c.id_usuario == usuario_id,
                bandeja_newsletter.c.id_newsletter == newsletter_id,
            ).values(leido=True)
        )
        if not updated.rowcount:
            return False
        try:
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False

    def esta_suscrito(self, usuario_id, artista_id):
        """Indica si el cliente está suscrito al newsletter del artista."""
        return self.session.query(Suscripcion).filter_by(
            id_cliente=usuario_id,
            id_artista=artista_id,
        ).first() is not None

    def suscribir(self, usuario_id, artista_id):
        """Suscribir un usuario a un artista."""
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
        return self.session.query(Usuario).join(
            Suscripcion, Usuario.id_usuario == Suscripcion.id_artista
        ).filter(
            Suscripcion.id_cliente == usuario_id
        ).order_by(Usuario.nombre).all()

    def count_suscripciones(self, usuario_id):
        return self.session.query(Suscripcion).filter_by(id_cliente=usuario_id).count()

    def desuscribir(self, usuario_id, artista_id):
        """Desuscribir un usuario de un artista."""
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

    def count_suscriptores(self, artista_id):
        return self.session.query(Suscripcion).filter_by(id_artista=artista_id).count()

    def get_by_artista(self, artista_id, limit=None):
        """Newsletters enviados por un artista."""
        query = self.session.query(Newsletter).filter_by(
            id_artista=artista_id,
        ).order_by(desc(Newsletter.fecha_envio))
        if limit:
            query = query.limit(limit)
        return query.all()

    def crear_y_enviar(self, artista_id, asunto, contenido):
        """
        Crea un newsletter y lo entrega en la bandeja de sus suscriptores.
        Devuelve (éxito, newsletter, destinatarios_count).
        """
        newsletter = Newsletter(
            id_artista=artista_id,
            asunto=asunto,
            contenido=contenido,
        )
        self.session.add(newsletter)
        self.session.flush()

        suscriptor_ids = [
            row[0]
            for row in self.session.query(Suscripcion.id_cliente).filter_by(
                id_artista=artista_id,
            ).all()
        ]

        if suscriptor_ids:
            newsletter.enviar_a_suscriptores(suscriptor_ids)

        try:
            self.session.commit()
            return True, newsletter, len(suscriptor_ids)
        except Exception:
            self.session.rollback()
            return False, None, 0
