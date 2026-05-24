"""
Servicio de gestión de Direcciones
"""

class DireccionService:
    """
    Servicio de direcciones para operaciones de negocio
    """
    
    def __init__(self, direccion_repository):
        self.direccion_repo = direccion_repository
        
    def get_by_usuario(self, usuario_id):
        """Obtener todas las direcciones de un usuario"""
        return self.direccion_repo.get_by_usuario(usuario_id)
        
    def get_by_id(self, id_direccion):
        """Obtener dirección por ID"""
        return self.direccion_repo.get_by_id(id_direccion)

    def get_by_id_for_usuario(self, id_direccion, usuario_id):
        """Obtener dirección validando que pertenezca al usuario"""
        return self.direccion_repo.get_by_id_and_usuario(id_direccion, usuario_id)
        
    def agregar_direccion(self, data):
        """Agregar una nueva dirección"""
        direccion = self.direccion_repo.create(data)
        if direccion:
            self.direccion_repo.save()
            return True, direccion
        return False, None
        
    def actualizar_direccion(self, id_direccion, usuario_id, data):
        """Actualizar una dirección del usuario (no si tiene órdenes)"""
        direccion = self.get_by_id_for_usuario(id_direccion, usuario_id)
        if not direccion:
            return False, None, 'no_encontrada'
        if direccion.tiene_ordenes_asociadas():
            return False, None, 'tiene_ordenes'
        direccion = self.direccion_repo.update(id_direccion, data, usuario_id=usuario_id)
        if direccion:
            self.direccion_repo.save()
            return True, direccion, None
        return False, None, 'error'

    def eliminar_direccion(self, id_direccion, usuario_id):
        """Eliminar una dirección del usuario si no tiene órdenes"""
        direccion = self.get_by_id_for_usuario(id_direccion, usuario_id)
        if not direccion:
            return False, 'no_encontrada'
        if direccion.tiene_ordenes_asociadas():
            return False, 'tiene_ordenes'
        if self.direccion_repo.delete(id_direccion, usuario_id=usuario_id):
            self.direccion_repo.save()
            return True, None
        return False, 'error'
