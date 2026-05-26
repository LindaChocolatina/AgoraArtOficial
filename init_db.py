#!/usr/bin/env python3
"""
Script para inicializar la base de datos SQLite
Crea todas las tablas necesarias para la plataforma de arte
"""

import os
from datetime import datetime
from app.factories.app_factory import create_app, db
from app.factories.db_factory import DatabaseFactory

def init_database():
    """Inicializar la base de datos con todas las tablas"""
    
    # Crear aplicación Flask
    app = create_app('development')
    
    with app.app_context():
        print("Inicializando base de datos SQLite...")
        
        # Crear fábrica de base de datos
        db_factory = DatabaseFactory()
        
        # Obtener engine y session
        engine = db_factory.create_engine()
        session = db_factory.get_session()
        
        try:
            # Importar todos los modelos para que SQLAlchemy los reconozca
            from app.models import (
                Usuario, Categoria, Obra, Producto, 
                EntradaBlog, ComentarioBlog, Direccion, 
                Orden, OrdenItem, Pago, Lienzo, LienzoItem,
                Newsletter, Suscripcion, Auditoria
            )
            
            # Crear todas las tablas
            db.create_all()
            
            print("¡Base de datos inicializada exitosamente!")
            print(f"Base de datos creada en: {engine.url}")
            
            # Crear usuario administrador por defecto
            from app.services.auth_service import AuthService
            from app.factories.service_factory import get_service_factory
            
            service_factory = get_service_factory()
            usuario_repo = service_factory.get_usuario_repository()
            auth_service = AuthService(usuario_repo)
            
            # Verificar si ya existe un admin
            admin_existente = usuario_repo.get_by_email('admin@artplatform.com')
            
            if not admin_existente:
                # Crear usuario admin por defecto
                admin_data = {
                    'nombre': 'Administrador',
                    'username': 'admin',
                    'email': 'admin@artplatform.com',
                    'password': 'admin123',  # Cambiar en producción
                    'rol': 'admin',
                    'biografia': 'Administrador del sistema',
                    'estado': 'activo'
                }
                
                exitoso, admin_usuario, errores = auth_service.registrar_usuario(admin_data)
                
                if exitoso:
                    print("Usuario administrador creado exitosamente:")
                    print("  Email: admin@artplatform.com")
                    print("  Password: admin123")
                    print("  ¡IMPORTANTE! Cambiar esta contraseña en producción")
                else:
                    print("Error al crear usuario administrador:")
                    for error in errores:
                        print(f"  - {error}")
            else:
                print("Usuario administrador ya existe")
            
            # Crear categorías del catálogo (solo las que falten)
            from app.utils.categorias_seed import ensure_categorias_catalogo
            creadas = ensure_categorias_catalogo(db.session)
            if creadas:
                print(f'Categorías nuevas en catálogo: {creadas}')
            else:
                print('Catálogo de categorías ya está completo')
            
            # Crear usuarios artistas de ejemplo
            usuario_service = service_factory.get_usuario_service()
            
            artistas_ejemplo = [
                {
                    'nombre': 'María González',
                    'username': 'maria_artista',
                    'email': 'maria.artista@example.com',
                    'password': 'artista123',
                    'rol': 'artista',
                    'biografia': 'Artista plástica especializada en pintura al óleo',
                    'is_active': True
                }
            ]
            
            artistas_creados = []
            for artista_data in artistas_ejemplo:
                if not usuario_service.get_by_email(artista_data['email']):
                    exito, artista, errores = auth_service.registrar_usuario(artista_data)
                    if exito:
                        artistas_creados.append(artista)
                        print(f"Artista creado: {artista_data['nombre']}")
                    else:
                        print(f"Error al crear artista {artista_data['nombre']}: {errores}")
                else:
                    artista = usuario_service.get_by_email(artista_data['email'])
                    if artista:
                        artistas_creados.append(artista)
                        print(f"Artista ya existe: {artista_data['nombre']}")
            
            # Crear obras de ejemplo
            obra_service = service_factory.get_obra_service()
            
            obras_ejemplo = [
                {
                    'titulo': 'Atardecer en el Campo',
                    'descripcion': 'Pintura al óleo que captura la belleza de un atardecer rural',
                    'imagen': '/static/uploads/obra1.jpg',
                    'tecnica': 'Óleo sobre lienzo',
                    'id_categoria': 1,  # Pintura
                    'id_artista': artistas_creados[0].id_usuario if artistas_creados else 2,
                    'visible': True,
                    'fecha_publicacion': datetime.now()
                },
                {
                    'titulo': 'Retrato Moderno',
                    'descripcion': 'Retrato expresionista de una mujer contemporánea',
                    'imagen': '/static/uploads/obra2.jpg',
                    'tecnica': 'Acrílico sobre tela',
                    'id_categoria': 1,  # Pintura
                    'id_artista': artistas_creados[0].id_usuario if artistas_creados else 2,
                    'visible': True,
                    'fecha_publicacion': datetime.now()
                },
                {
                    'titulo': 'Ciudad Nocturna',
                    'descripcion': 'Fotografía urbana tomada durante la noche',
                    'imagen': '/static/uploads/obra3.jpg',
                    'tecnica': 'Fotografía digital',
                    'id_categoria': 3,  # Fotografía
                    'id_artista': artistas_creados[0].id_usuario if artistas_creados else 2,
                    'visible': True,
                    'fecha_publicacion': datetime.now()
                }
            ]
            
            for obra_data in obras_ejemplo:
                exito, obra = obra_service.crear_obra(obra_data)
                if exito:
                    print(f"Obra creada: {obra_data['titulo']}")
                else:
                    print(f"Error al crear obra: {obra_data['titulo']}")
            
            # Guardar cambios
            session.commit()
            
            print("\n¡Inicialización completada!")
            print("La base de datos está lista para usar.")
            
        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")
            session.rollback()
            raise
        finally:
            session.close()

if __name__ == '__main__':
    init_database()
