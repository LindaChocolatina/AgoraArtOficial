"""
Servicio de gestión de Moodboards (Lienzos)
"""

class MoodboardService:
    """
    Servicio de moodboards para operaciones de negocio
    """
    
    def __init__(self, moodboard_repository, obra_repository):
        self.moodboard_repo = moodboard_repository
        self.obra_repo = obra_repository
        
    def get_by_usuario(self, usuario_id):
        """Obtener todos los lienzos de un usuario"""
        return self.moodboard_repo.get_by_usuario(usuario_id)
        
    def get_by_id(self, id_lienzo):
        """Obtener lienzo por ID"""
        return self.moodboard_repo.get_by_id(id_lienzo)

    def get_items(self, id_lienzo):
        """Obtener obras de un lienzo como lista"""
        return self.moodboard_repo.get_items(id_lienzo)
        
    def crear_lienzo(self, usuario_id, nombre):
        """Crear un nuevo lienzo"""
        data = {
            'id_usuario': usuario_id,
            'nombre': nombre
        }
        lienzo = self.moodboard_repo.create(data)
        if lienzo:
            self.moodboard_repo.save()
            return True, lienzo
        return False, None
        
    def agregar_obra(self, id_lienzo, id_obra, nota=None):
        """Agregar una obra a un lienzo"""
        # Verificar que el lienzo existe
        lienzo = self.moodboard_repo.get_by_id(id_lienzo)
        if not lienzo:
            return False
            
        # Verificar que la obra existe
        obra = self.obra_repo.get_by_id(id_obra)
        if not obra:
            return False
            
        # Verificar si ya existe en el lienzo
        if self.moodboard_repo.get_item(id_lienzo, id_obra):
            return True  # Ya está, lo consideramos éxito
            
        if self.moodboard_repo.agregar_item(id_lienzo, id_obra, nota):
            self.moodboard_repo.save()
            return True
        return False
        
    def remover_obra(self, id_lienzo, id_obra):
        """Remover una obra de un lienzo"""
        if self.moodboard_repo.remover_item(id_lienzo, id_obra):
            self.moodboard_repo.save()
            return True
        return False
        
    def eliminar_lienzo(self, id_lienzo):
        """Eliminar un lienzo completo"""
        if self.moodboard_repo.delete(id_lienzo):
            self.moodboard_repo.save()
            return True
        return False
        
    def get_count_usuario(self, usuario_id):
        """Obtener cantidad de lienzos de un usuario"""
        return self.moodboard_repo.count({'id_usuario': usuario_id})
