from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from .. import db
from ..models.detalles_compras import DetalleCompra
from ..models.compras import Compra
from ..models.productos import Producto

detalle_compra_bp = Blueprint("detalle_compra", __name__)


def _obtener_compra(data):
    for key in ("id_compras", "id_compra", "compra_id"):
        value = data.get(key)
        if value is not None:
            compra = Compra.query.get(int(value))
            if compra:
                return compra

    compra = Compra.query.order_by(Compra.id.desc()).first()
    if compra:
        return compra

    return None


def _recalcular_total_compra(compra):
    if compra is None:
        return
    compra.total = sum(detalle.subtotal for detalle in compra.detalles_compras)


# LISTAR
@detalle_compra_bp.route("/detalles-compras", methods=["GET"])
def listar_detalles():
    return jsonify([d.to_dict() for d in DetalleCompra.query.all()])


# BUSCAR POR ID
@detalle_compra_bp.route("/detalles-compras/<int:id>", methods=["GET"])
def obtener_detalle(id):
    detalle = DetalleCompra.query.get(id)
    if not detalle:
        return jsonify({"mensaje": "Detalle no encontrado"}), 404
    return jsonify(detalle.to_dict())


# REGISTRAR
@detalle_compra_bp.route("/detalles-compras", methods=["POST"])
def crear_detalle():
    try:
        data = request.get_json(silent=True) or {}

        id_productos = data.get("id_productos")
        cantidad = data.get("cantidad")

        if id_productos is None or cantidad is None:
            return jsonify({"mensaje": "Faltan datos requeridos"}), 400

        try:
            id_productos = int(id_productos)
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            return jsonify({"mensaje": "Los campos id_productos y cantidad deben ser números válidos"}), 400

        producto = Producto.query.get(id_productos)
        if not producto:
            return jsonify({"mensaje": "Producto no existe"}), 404

        compra = _obtener_compra(data)
        if not compra:
            return jsonify({"mensaje": "No hay compras registradas para asignar el detalle"}), 404

        subtotal = cantidad * producto.precio_venta

        detalle = DetalleCompra(
            id_compras=compra.id,
            id_productos=id_productos,
            cantidad=cantidad,
            precio_unitario=producto.precio_venta,
            subtotal=subtotal,
        )

        db.session.add(detalle)
        db.session.flush()
        _recalcular_total_compra(compra)
        db.session.commit()

        return jsonify({"mensaje": "Detalle registrado", "detalle": detalle.to_dict()}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"mensaje": "Error al registrar"}), 400
    except Exception as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error al registrar detalle", "detalle": str(exc)}), 500


# ACTUALIZAR
@detalle_compra_bp.route("/detalles-compras/<int:id>", methods=["PUT"])
def actualizar_detalle(id):
    detalle = DetalleCompra.query.get(id)

    if not detalle:
        return jsonify({"mensaje": "Detalle no encontrado"}), 404

    data = request.get_json(silent=True) or {}

    if "id_productos" in data and data.get("id_productos") is not None:
        detalle.id_productos = int(data["id_productos"])

    if "cantidad" in data and data.get("cantidad") is not None:
        detalle.cantidad = int(data["cantidad"])

    if "id_compras" in data and data.get("id_compras") is not None:
        detalle.id_compras = int(data["id_compras"])
    elif "id_compra" in data and data.get("id_compra") is not None:
        detalle.id_compras = int(data["id_compra"])
    elif "compra_id" in data and data.get("compra_id") is not None:
        detalle.id_compras = int(data["compra_id"])

    producto = Producto.query.get(detalle.id_productos)
    if not producto:
        return jsonify({"mensaje": "Producto no existe"}), 404

    detalle.precio_unitario = producto.precio_venta
    detalle.subtotal = detalle.cantidad * detalle.precio_unitario

    compra_anterior = Compra.query.get(id if False else detalle.id_compras)
    compra_actual = Compra.query.get(detalle.id_compras)
    _recalcular_total_compra(compra_actual)
    db.session.commit()

    return jsonify({"mensaje": "Detalle actualizado", "detalle": detalle.to_dict()})


# ELIMINAR
@detalle_compra_bp.route("/detalles-compras/<int:id>", methods=["DELETE"])
def eliminar_detalle(id):
    detalle = DetalleCompra.query.get(id)

    if not detalle:
        return jsonify({"mensaje": "Detalle no encontrado"}), 404

    compra = Compra.query.get(detalle.id_compras)

    db.session.delete(detalle)
    db.session.flush()
    _recalcular_total_compra(compra)
    db.session.commit()

    return jsonify({"mensaje": "Detalle eliminado"})
