from .productos_routes import producto_bp
from .clientes_routes import cliente_bp
from .proveedores_routes import proveedor_bp
from .compras_routes import compra_bp
from .ventas_routes import venta_bp
from .detalles_compras_routes import detalle_compra_bp
from .detalles_ventas_routes import detalle_venta_bp


def register_routes(app):
    
    app.register_blueprint(producto_bp)
    app.register_blueprint(cliente_bp)
    app.register_blueprint(proveedor_bp)
    app.register_blueprint(compra_bp)
    app.register_blueprint(venta_bp)
    app.register_blueprint(detalle_compra_bp)
    app.register_blueprint(detalle_venta_bp)
