from app.factories.app_factory import db


class ObraImagen(db.Model):
    """Imágenes adicionales de una obra (galería)."""
    __tablename__ = 'obra_imagenes'

    id_imagen = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_obra = db.Column(db.Integer, db.ForeignKey('obras.id_obra', ondelete='CASCADE'), nullable=False)
    imagen = db.Column(db.String(255), nullable=False)
    orden = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<ObraImagen obra={self.id_obra}>'
