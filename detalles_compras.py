from app import db

class DetalleCompra(db.Model):
    __tablename__ = "detalles_compras"

    id = db.Column(db.Integer, primary_key=True)
    id_compras = db.Column(db.Integer, db.ForeignKey("compras.id"), nullable=False)
    id_productos = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    compra = db.relationship("Compra", backref=db.backref("detalles_compras", lazy=True))
    producto = db.relationship("Producto", backref=db.backref("detalles_compras", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "id_compras": self.id_compras,
            "id_productos": self.id_productos,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "subtotal": self.subtotal,
            "compra": self.compra.to_dict() if self.compra else None,
            "producto": self.producto.to_dict() if self.producto else None,
        }