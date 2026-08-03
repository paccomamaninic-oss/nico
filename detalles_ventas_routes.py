from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from .. import db
from ..models.detalles_ventas import DetalleVenta
from ..models.ventas import Venta
from ..models.productos import Producto

detalle_venta_bp = Blueprint("detalle_venta", __name__)


def _obtener_venta(data):
    for key in ("id_ventas", "id_venta", "venta_id"):
        value = data.get(key)
        if value is not None:
            venta = Venta.query.get(int(value))
            if venta:
                return venta

    venta = Venta.query.order_by(Venta.id.desc()).first()
    if venta:
        return venta

    return None


# LISTAR
@detalle_venta_bp.route("/detalles-ventas", methods=["GET"])
def listar_detalles():
    return jsonify([d.to_dict() for d in DetalleVenta.query.all()])


# BUSCAR POR ID
@detalle_venta_bp.route("/detalles-ventas/<int:id>", methods=["GET"])
def obtener_detalle(id):
    detalle = DetalleVenta.query.get(id)

    if not detalle:
        return jsonify({"mensaje": "Detalle no encontrado"}), 404

    return jsonify(detalle.to_dict())


# REGISTRAR
@detalle_venta_bp.route("/detalles-ventas", methods=["POST"])
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

        venta = _obtener_venta(data)
        if not venta:
            return jsonify({"mensaje": "No hay ventas registradas para asignar el detalle"}), 404

        subtotal = cantidad * producto.precio_venta

        detalle = DetalleVenta(
            id_ventas=venta.id,
            id_productos=id_productos,
            cantidad=cantidad,
            precio_unitario=producto.precio_venta,
            subtotal=subtotal,
        )

        db.session.add(detalle)
        db.session.commit()

        return jsonify({"mensaje": "Detalle registrado", "detalle": detalle.to_dict(), "total": venta.total}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"mensaje": "Error al registrar"}), 400
    except Exception as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error al registrar detalle", "detalle": str(exc)}), 500


# ACTUALIZAR
@detalle_venta_bp.route("/detalles-ventas/<int:id>", methods=["PUT"])
def actualizar_detalle(id):
    detalle = DetalleVenta.query.get(id)

    if not detalle:
        return jsonify({"mensaje": "Detalle no encontrado"}), 404

    data = request.get_json(silent=True) or {}

    if "id_productos" in data and data.get("id_productos") is not None:
        detalle.id_productos = int(data["id_productos"])

    if "cantidad" in data and data.get("cantidad") is not None:
        detalle.cantidad = int(data["cantidad"])

    if "id_ventas" in data and data.get("id_ventas") is not None:
        detalle.id_ventas = int(data["id_ventas"])
    elif "id_venta" in data and data.get("id_venta") is not None:
        detalle.id_ventas = int(data["id_venta"])
    elif "venta_id" in data and data.get("venta_id") is not None:
        detalle.id_ventas = int(data["venta_id"])

    producto = Producto.query.get(detalle.id_productos)
    if not producto:
        return jsonify({"mensaje": "Producto no existe"}), 404

    detalle.precio_unitario = producto.precio_venta
    detalle.subtotal = detalle.cantidad * detalle.precio_unitario

    db.session.commit()

    return jsonify({"mensaje": "Detalle actualizado", "detalle": detalle.to_dict(), "total": detalle.venta.total if detalle.venta else 0})


# ELIMINAR
@detalle_venta_bp.route("/detalles-ventas/<int:id>", methods=["DELETE"])
def eliminar_detalle(id):
    detalle = DetalleVenta.query.get(id)

    if not detalle:
        return jsonify({"mensaje": "Detalle no encontrado"}), 404

    db.session.delete(detalle)
    db.session.commit()

    return jsonify({"mensaje": "Detalle eliminado"})