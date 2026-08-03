from app import db
class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    id_proveedores = db.Column(db.Integer, db.ForeignKey("proveedores.id"), nullable=True)
    nombre = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    precio_venta = db.Column(db.Float, nullable=False)

    proveedor = db.relationship("Proveedor", backref=db.backref("productos", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "id_proveedores": self.id_proveedores,
            "nombre": self.nombre,
            "marca": self.marca,
            "precio_venta": self.precio_venta,
            "proveedor": self.proveedor.to_dict() if self.proveedor else None,
        }