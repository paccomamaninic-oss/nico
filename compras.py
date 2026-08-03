from app import db

class Compra(db.Model):
    __tablename__ = "compras"

    id = db.Column(db.Integer, primary_key=True)
    id_proveedores = db.Column(db.Integer, db.ForeignKey("proveedores.id"), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), nullable=False)

    proveedor = db.relationship("Proveedor", backref=db.backref("compras", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "id_proveedores": self.id_proveedores,
            "fecha": self.fecha,
            "total": self.total,
            "estado": self.estado,
            "proveedor": self.proveedor.to_dict() if self.proveedor else None,
        }