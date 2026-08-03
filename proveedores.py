from app import db

class Proveedor(db.Model):
    __tablename__ = "proveedores"

    id = db.Column(db.Integer, primary_key=True)
    nombre_empresa = db.Column(db.String(50), nullable=False)
    contactos = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre_empresa": self.nombre_empresa,
            "contactos": self.contactos,
            "email": self.email,
            "telefono": self.telefono,
        }
