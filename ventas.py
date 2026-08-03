from app import db


class Venta(db.Model):
    __tablename__ = "ventas"

    id = db.Column(db.Integer, primary_key=True)
    id_clientes = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    metodo_pago = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(50), nullable=False)

    cliente = db.relationship("Cliente", backref=db.backref("ventas", lazy=True))

    @property
    def total(self):
        return round(sum(detalle.subtotal for detalle in self.detalles_ventas), 2)

    def to_dict(self):
        return {
            "id": self.id,
            "id_clientes": self.id_clientes,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "metodo_pago": self.metodo_pago,
            "estado": self.estado,
            "total": self.total,
            "cliente": self.cliente.to_dict() if self.cliente else None,
        }
