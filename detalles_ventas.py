from app import db

class DetalleVenta(db.Model):
    __tablename__ = "detalles_ventas"

    id = db.Column(db.Integer, primary_key=True)
    id_ventas = db.Column(db.Integer, db.ForeignKey("ventas.id"), nullable=False)
    id_productos = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    venta = db.relationship("Venta", backref=db.backref("detalles_ventas", lazy=True))
    producto = db.relationship("Producto", backref=db.backref("detalles_ventas", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "id_ventas": self.id_ventas,
            "id_productos": self.id_productos,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "subtotal": self.subtotal,
            "venta": self.venta.to_dict() if self.venta else None,
            "producto": self.producto.to_dict() if self.producto else None,
        }

    