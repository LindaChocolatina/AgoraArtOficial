"""
Servicio de blog
Gestiona operaciones CRUD para las entradas de blog de los artistas
"""
from app.models.blog import EntradaBlog, ComentarioBlog
from app.factories.app_factory import db

MAX_COMENTARIO_LEN = 2000


class BlogService:
    """Servicio de blog con operaciones de negocio"""

    def __init__(self, repository=None):
        """
        Inicializar servicio de blog

        Args:
            repository: Repositorio de usuarios (opcional, legacy)
        """
        self.repository = repository

    # ── Lectura ─────────────────────────────────────────────

    def get_all(self, visible_only=True):
        """
        Obtener todas las entradas de blog

        Args:
            visible_only (bool): Solo entradas visibles

        Returns:
            list: Lista de EntradaBlog
        """
        try:
            query = EntradaBlog.query
            if visible_only:
                query = query.filter_by(visible=True)
            return query.order_by(EntradaBlog.fecha_publicacion.desc()).all()
        except Exception as e:
            print(f"Error al obtener entradas de blog: {e}")
            return []

    def get_by_artista(self, artista_id, visible_only=False):
        """
        Obtener entradas de blog de un artista

        Args:
            artista_id (int): ID del artista
            visible_only (bool): Solo entradas visibles

        Returns:
            list: Lista de EntradaBlog
        """
        try:
            query = EntradaBlog.query.filter_by(id_artista=artista_id)
            if visible_only:
                query = query.filter_by(visible=True)
            return query.order_by(EntradaBlog.fecha_publicacion.desc()).all()
        except Exception as e:
            print(f"Error al obtener entradas del artista {artista_id}: {e}")
            return []

    def get_by_id(self, entrada_id):
        """
        Obtener entrada por ID

        Args:
            entrada_id (int): ID de la entrada

        Returns:
            EntradaBlog o None
        """
        try:
            return EntradaBlog.query.get(entrada_id)
        except Exception as e:
            print(f"Error al obtener entrada {entrada_id}: {e}")
            return None

    def get_count_by_artista(self, artista_id, visible_only=False):
        """
        Contar entradas de blog de un artista

        Args:
            artista_id (int): ID del artista
            visible_only (bool): Solo entradas visibles

        Returns:
            int: Cantidad de entradas
        """
        try:
            query = EntradaBlog.query.filter_by(id_artista=artista_id)
            if visible_only:
                query = query.filter_by(visible=True)
            return query.count()
        except Exception as e:
            print(f"Error al contar entradas del artista {artista_id}: {e}")
            return 0

    # ── Escritura ───────────────────────────────────────────

    def crear_entrada(self, data, usuario_id=None):
        """
        Crear nueva entrada de blog

        Args:
            data (dict): Datos de la entrada (titulo, contenido, id_artista, visible)
            usuario_id (int): ID del usuario que crea (opcional)

        Returns:
            tuple: (exitoso: bool, entrada: EntradaBlog | None)
        """
        try:
            if not data.get('titulo', '').strip():
                return (False, None)
            if not data.get('contenido', '').strip():
                return (False, None)
            if not data.get('id_artista'):
                return (False, None)

            entrada = EntradaBlog(
                id_artista=data['id_artista'],
                titulo=data['titulo'].strip(),
                contenido=data['contenido'].strip(),
                visible=data.get('visible', True)
            )
            db.session.add(entrada)
            db.session.commit()
            return (True, entrada)
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear entrada de blog: {e}")
            return (False, None)

    def actualizar_entrada(self, entrada_id, data, usuario_id=None):
        """
        Actualizar entrada de blog existente

        Args:
            entrada_id (int): ID de la entrada
            data (dict): Datos a actualizar
            usuario_id (int): ID del usuario que actualiza (opcional)

        Returns:
            tuple: (exitoso: bool, entrada: EntradaBlog | None)
        """
        try:
            entrada = EntradaBlog.query.get(entrada_id)
            if not entrada:
                return (False, None)

            if 'titulo' in data:
                if not data['titulo'].strip():
                    return (False, None)
                entrada.titulo = data['titulo'].strip()

            if 'contenido' in data:
                if not data['contenido'].strip():
                    return (False, None)
                entrada.contenido = data['contenido'].strip()

            if 'visible' in data:
                entrada.visible = data['visible']

            db.session.commit()
            return (True, entrada)
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar entrada {entrada_id}: {e}")
            return (False, None)

    def eliminar_entrada(self, entrada_id, usuario_id=None):
        """
        Eliminar entrada de blog

        Args:
            entrada_id (int): ID de la entrada
            usuario_id (int): ID del usuario que elimina (opcional)

        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            entrada = EntradaBlog.query.get(entrada_id)
            if not entrada:
                return False

            db.session.delete(entrada)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar entrada {entrada_id}: {e}")
            return False

    # ── Comentarios ─────────────────────────────────────────

    def listar_comentarios(self, entrada_id):
        """Comentarios de una entrada, del más antiguo al más reciente."""
        try:
            return (
                ComentarioBlog.query.filter_by(id_entrada=entrada_id)
                .order_by(ComentarioBlog.fecha.asc())
                .all()
            )
        except Exception as e:
            print(f"Error al listar comentarios de entrada {entrada_id}: {e}")
            return []

    def agregar_comentario(self, entrada_id, usuario_id, contenido):
        """
        Publicar comentario en una entrada visible.

        Returns:
            tuple: (exitoso, comentario|None, mensaje_error)
        """
        try:
            entrada = EntradaBlog.query.get(entrada_id)
            if not entrada or not entrada.is_visible():
                return (False, None, 'Entrada no encontrada')

            texto = (contenido or '').strip()
            if not texto:
                return (False, None, 'Escribe un comentario')
            if len(texto) > MAX_COMENTARIO_LEN:
                return (False, None, f'El comentario no puede superar {MAX_COMENTARIO_LEN} caracteres')

            comentario = ComentarioBlog(
                id_entrada=entrada_id,
                id_usuario=usuario_id,
                contenido=texto,
            )
            db.session.add(comentario)
            db.session.commit()
            return (True, comentario, '')
        except Exception as e:
            db.session.rollback()
            print(f"Error al agregar comentario: {e}")
            return (False, None, 'No se pudo publicar el comentario')

    def eliminar_comentario(self, comentario_id, usuario_id, es_artista_entrada=False):
        """
        Eliminar comentario: autor del comentario o artista dueño de la entrada.

        Returns:
            tuple: (exitoso, mensaje_error)
        """
        try:
            comentario = ComentarioBlog.query.get(comentario_id)
            if not comentario:
                return (False, 'Comentario no encontrado')

            puede = comentario.id_usuario == usuario_id or es_artista_entrada
            if not puede:
                return (False, 'No tienes permiso para eliminar este comentario')

            db.session.delete(comentario)
            db.session.commit()
            return (True, '')
        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar comentario {comentario_id}: {e}")
            return (False, 'No se pudo eliminar el comentario')
