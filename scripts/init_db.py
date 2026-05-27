#!/usr/bin/env python3
"""
Inicializa la base de datos local (SQLite) y datos de ejemplo.

Uso:
    python scripts/init_db.py
"""
from pathlib import Path
import os
import sys

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))

from datetime import datetime

from app.factories.app_factory import create_app, db
from app.factories.db_factory import DatabaseFactory


def init_database():
    app = create_app('development')

    with app.app_context():
        print('Inicializando base de datos SQLite...')

        db_factory = DatabaseFactory()
        engine = db_factory.create_engine()
        session = db_factory.get_session()

        try:
            from app.models import (
                Usuario, Categoria, Obra, Producto,
                EntradaBlog, ComentarioBlog, Direccion,
                Orden, OrdenItem, Pago, Lienzo, LienzoItem,
                Newsletter, Suscripcion, Auditoria,
            )

            db.create_all()
            print('¡Base de datos inicializada exitosamente!')
            print(f'Base de datos creada en: {engine.url}')

            from app.services.auth_service import AuthService
            from app.factories.service_factory import get_service_factory

            service_factory = get_service_factory()
            usuario_repo = service_factory.get_usuario_repository()
            auth_service = AuthService(usuario_repo)

            admin_existente = usuario_repo.get_by_email('admin@artplatform.com')
            if not admin_existente:
                admin_data = {
                    'nombre': 'Administrador',
                    'username': 'admin',
                    'email': 'admin@artplatform.com',
                    'password': 'admin123',
                    'rol': 'admin',
                    'biografia': 'Administrador del sistema',
                    'estado': 'activo',
                }
                exitoso, _, errores = auth_service.registrar_usuario(admin_data)
                if exitoso:
                    print('Usuario administrador creado: admin@artplatform.com / admin123')
                else:
                    for error in errores:
                        print(f'  - {error}')
            else:
                print('Usuario administrador ya existe')

            from app.utils.categorias_seed import ensure_categorias_catalogo

            creadas = ensure_categorias_catalogo(db.session)
            if creadas:
                print(f'Categorías nuevas en catálogo: {creadas}')
            else:
                print('Catálogo de categorías ya está completo')

            usuario_service = service_factory.get_usuario_service()
            artistas_ejemplo = [
                {
                    'nombre': 'María González',
                    'username': 'maria_artista',
                    'email': 'maria.artista@example.com',
                    'password': 'artista123',
                    'rol': 'artista',
                    'biografia': 'Artista plástica especializada en pintura al óleo',
                    'is_active': True,
                },
            ]

            artistas_creados = []
            for artista_data in artistas_ejemplo:
                if not usuario_service.get_by_email(artista_data['email']):
                    exito, artista, errores = auth_service.registrar_usuario(artista_data)
                    if exito:
                        artistas_creados.append(artista)
                        print(f'Artista creado: {artista_data["nombre"]}')
                    else:
                        print(f'Error al crear artista {artista_data["nombre"]}: {errores}')
                else:
                    artista = usuario_service.get_by_email(artista_data['email'])
                    if artista:
                        artistas_creados.append(artista)
                        print(f'Artista ya existe: {artista_data["nombre"]}')

            obra_service = service_factory.get_obra_service()
            obras_ejemplo = [
                {
                    'titulo': 'Atardecer en el Campo',
                    'descripcion': 'Pintura al óleo que captura la belleza de un atardecer rural',
                    'imagen': '/static/uploads/obra1.jpg',
                    'tecnica': 'Óleo sobre lienzo',
                    'id_categoria': 1,
                    'id_artista': artistas_creados[0].id_usuario if artistas_creados else 2,
                    'visible': True,
                    'fecha_publicacion': datetime.now(),
                },
                {
                    'titulo': 'Retrato Moderno',
                    'descripcion': 'Retrato expresionista de una mujer contemporánea',
                    'imagen': '/static/uploads/obra2.jpg',
                    'tecnica': 'Acrílico sobre tela',
                    'id_categoria': 1,
                    'id_artista': artistas_creados[0].id_usuario if artistas_creados else 2,
                    'visible': True,
                    'fecha_publicacion': datetime.now(),
                },
                {
                    'titulo': 'Ciudad Nocturna',
                    'descripcion': 'Fotografía urbana tomada durante la noche',
                    'imagen': '/static/uploads/obra3.jpg',
                    'tecnica': 'Fotografía digital',
                    'id_categoria': 3,
                    'id_artista': artistas_creados[0].id_usuario if artistas_creados else 2,
                    'visible': True,
                    'fecha_publicacion': datetime.now(),
                },
            ]

            for obra_data in obras_ejemplo:
                exito, _ = obra_service.crear_obra(obra_data)
                if exito:
                    print(f'Obra creada: {obra_data["titulo"]}')
                else:
                    print(f'Error al crear obra: {obra_data["titulo"]}')

            session.commit()
            print('\n¡Inicialización completada!')

        except Exception as e:
            print(f'Error al inicializar la base de datos: {e}')
            session.rollback()
            raise
        finally:
            session.close()


if __name__ == '__main__':
    init_database()
