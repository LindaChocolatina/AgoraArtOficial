from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.models.auditoria import Auditoria

class BaseRepository:
    """
    Repositorio base con operaciones CRUD genéricas
    Implementa el patrón Repository para acceso a datos
    """
    
    def __init__(self, model_class, session):
        """
        Inicializar repositorio
        
        Args:
            model_class: Clase del modelo SQLAlchemy
            session: Sesión de base de datos
        """
        self.model_class = model_class
        self.session = session
        self.tabla_nombre = model_class.__tablename__
        self._id_field_cache = None

    @property
    def id_field(self):
        """Nombre de la columna PK (evita errores con tablas como 'direcciones')."""
        if self._id_field_cache is None:
            self._id_field_cache = sa_inspect(self.model_class).primary_key[0].key
        return self._id_field_cache

    def create(self, data, usuario_id=None, registrar_auditoria=True):
        """
        Crear un nuevo registro
        
        Args:
            data (dict): Datos del nuevo registro
            usuario_id (int): ID del usuario que realiza la acción
            registrar_auditoria (bool): Si registrar en auditoría
            
        Returns:
            Model: Instancia del modelo creado o None si hay error
        """
        try:
            instance = self.model_class(**data)
            self.session.add(instance)
            self.session.flush()  # Obtener ID sin hacer commit
            
            if registrar_auditoria:
                try:
                    id_registro = getattr(instance, self.id_field, None)
                    
                    # Solo registrar auditoría si tenemos ID válido
                    if id_registro is not None:
                        Auditoria.registrar_cambio(
                            tabla=self.tabla_nombre,
                            id_registro=id_registro,
                            accion='INSERT',
                            usuario_id=usuario_id,
                            descripcion=f"Creación de {self.model_class.__name__}"
                        )
                except Exception as audit_error:
                    # Si la auditoría falla, loguear pero no fallar la creación
                    print(f"Advertencia: Error al registrar auditoría: {audit_error}")
            
            return instance
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error al crear {self.model_class.__name__}: {e}")
            return None
    
    def get_by_id(self, id_value):
        """
        Obtener registro por ID
        
        Args:
            id_value: Valor del ID a buscar
            
        Returns:
            Model: Instancia del modelo o None
        """
        try:
            return self.session.query(self.model_class).filter(
                getattr(self.model_class, self.id_field) == id_value
            ).first()
        except SQLAlchemyError as e:
            print(f"Error al obtener {self.model_class.__name__} por ID: {e}")
            return None
    
    def get_all(self, filters=None, order_by=None, limit=None, offset=None):
        """
        Obtener todos los registros con filtros opcionales
        
        Args:
            filters (dict): Filtros a aplicar
            order_by: Campo de ordenamiento
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de instancias del modelo
        """
        try:
            query = self.session.query(self.model_class)
            
            # Aplicar filtros
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model_class, field):
                        query = query.filter(getattr(self.model_class, field) == value)
            
            # Aplicar ordenamiento
            if order_by:
                if hasattr(self.model_class, order_by):
                    query = query.order_by(getattr(self.model_class, order_by))
            
            # Aplicar límite y desplazamiento
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error al obtener {self.model_class.__name__}: {e}")
            return []
    
    def update(self, id_value, data, usuario_id=None, registrar_auditoria=True):
        """
        Actualizar un registro existente
        
        Args:
            id_value: ID del registro a actualizar
            data (dict): Datos a actualizar
            usuario_id (int): ID del usuario que realiza la acción
            registrar_auditoria (bool): Si registrar en auditoría
            
        Returns:
            Model: Instancia actualizada o None si hay error
        """
        try:
            instance = self.session.query(self.model_class).filter(
                getattr(self.model_class, self.id_field) == id_value
            ).first()
            
            if instance:
                # Guardar valores antiguos para auditoría
                valores_antiguos = {field: getattr(instance, field) for field in data.keys() if hasattr(instance, field)}
                
                # Actualizar campos
                for field, value in data.items():
                    if hasattr(instance, field):
                        setattr(instance, field, value)
                
                if registrar_auditoria:
                    cambios = []
                    for field, nuevo_valor in data.items():
                        if field in valores_antiguos and valores_antiguos[field] != nuevo_valor:
                            cambios.append(f"{field}: {valores_antiguos[field]} -> {nuevo_valor}")
                    
                    Auditoria.registrar_cambio(
                        tabla=self.tabla_nombre,
                        id_registro=id_value,
                        accion='UPDATE',
                        usuario_id=usuario_id,
                        descripcion=f"Actualización de {self.model_class.__name__}: {', '.join(cambios)}"
                    )
                
                return instance
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error al actualizar {self.model_class.__name__}: {e}")
            return None
    
    def delete(self, id_value, usuario_id=None, registrar_auditoria=True):
        """
        Eliminar un registro
        
        Args:
            id_value: ID del registro a eliminar
            usuario_id (int): ID del usuario que realiza la acción
            registrar_auditoria (bool): Si registrar en auditoría
            
        Returns:
            bool: True si se eliminó correctamente, False si hay error
        """
        try:
            instance = self.session.query(self.model_class).filter(
                getattr(self.model_class, self.id_field) == id_value
            ).first()
            
            if instance:
                if registrar_auditoria:
                    Auditoria.registrar_cambio(
                        tabla=self.tabla_nombre,
                        id_registro=id_value,
                        accion='DELETE',
                        usuario_id=usuario_id,
                        descripcion=f"Eliminación de {self.model_class.__name__}"
                    )
                
                self.session.delete(instance)
                return True
            return False
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error al eliminar {self.model_class.__name__}: {e}")
            return False
    
    def count(self, filters=None):
        """
        Contar registros con filtros opcionales
        
        Args:
            filters (dict): Filtros a aplicar
            
        Returns:
            int: Cantidad de registros
        """
        try:
            query = self.session.query(self.model_class)
            
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model_class, field):
                        query = query.filter(getattr(self.model_class, field) == value)
            
            return query.count()
        except SQLAlchemyError as e:
            print(f"Error al contar {self.model_class.__name__}: {e}")
            return 0
    
    def exists(self, id_value):
        """
        Verificar si existe un registro
        
        Args:
            id_value: ID del registro a verificar
            
        Returns:
            bool: True si existe, False si no
        """
        try:
            return self.session.query(self.model_class).filter(
                getattr(self.model_class, self.id_field) == id_value
            ).first() is not None
        except SQLAlchemyError as e:
            print(f"Error al verificar existencia de {self.model_class.__name__}: {e}")
            return False
    
    def save(self):
        """
        Guardar cambios pendientes en la base de datos
        
        Returns:
            bool: True si se guardó correctamente, False si hay error
        """
        try:
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error al guardar cambios: {e}")
            return False
