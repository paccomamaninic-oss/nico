from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from .. import db
from ..models.ventas import Venta

venta_bp = Blueprint("venta", __name__)


@venta_bp.route("/ventas", methods=["GET"])
def listar_ventas():
    try:
        return jsonify([v.to_dict() for v in Venta.query.all()])
    except Exception as exc:
        return jsonify({"mensaje": "Error al listar ventas", "detalle": str(exc)}), 500


@venta_bp.route("/ventas/<int:id>", methods=["GET"])
def obtener_venta(id):
    try:
        venta = Venta.query.get(id)
        if not venta:
            return jsonify({"mensaje": "Venta no encontrada"}), 404
        return jsonify(venta.to_dict())
    except Exception as exc:
        return jsonify({"mensaje": "Error al buscar venta", "detalle": str(exc)}), 500


@venta_bp.route("/ventas", methods=["POST"])
def crear_venta():
    data = request.get_json(silent=True) or {}
    campos = ["id_clientes", "fecha", "metodo_pago", "estado"]
    if not all(campo in data and data[campo] is not None for campo in campos):
        return jsonify({"mensaje": "Faltan datos requeridos"}), 400

    try:
        id_clientes = int(data["id_clientes"])
        fecha = data["fecha"]
        if isinstance(fecha, str):
            fecha = datetime.fromisoformat(fecha)
        venta = Venta(
            id_clientes=id_clientes,
            fecha=fecha,
            metodo_pago=str(data["metodo_pago"]).strip(),
            estado=str(data["estado"]).strip(),
        )
        db.session.add(venta)
        db.session.commit()
        return jsonify({"mensaje": "Venta registrada", "venta": venta.to_dict()}), 201
    except (TypeError, ValueError):
        db.session.rollback()
        return jsonify({"mensaje": "Datos inválidos"}), 400
    except IntegrityError as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error de integridad en la BD", "detalle": str(exc.orig)}), 400
    except Exception as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error al registrar venta", "detalle": str(exc)}), 500


@venta_bp.route("/ventas/<int:id>", methods=["PUT"])
def actualizar_venta(id):
    venta = Venta.query.get(id)
    if not venta:
        return jsonify({"mensaje": "Venta no encontrada"}), 404

    data = request.get_json(silent=True) or {}
    try:
        if "id_clientes" in data and data["id_clientes"] is not None:
            venta.id_clientes = int(data["id_clientes"])
        if "fecha" in data and data["fecha"] is not None:
            fecha = data["fecha"]
            if isinstance(fecha, str):
                fecha = datetime.fromisoformat(fecha)
            venta.fecha = fecha
        if "metodo_pago" in data and data["metodo_pago"] is not None:
            venta.metodo_pago = str(data["metodo_pago"]).strip()
        if "estado" in data and data["estado"] is not None:
            venta.estado = str(data["estado"]).strip()
        db.session.commit()
        return jsonify({"mensaje": "Venta actualizada", "venta": venta.to_dict()})
    except (TypeError, ValueError):
        db.session.rollback()
        return jsonify({"mensaje": "Datos inválidos"}), 400
    except IntegrityError as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error de integridad en la BD", "detalle": str(exc.orig)}), 400
    except Exception as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error al actualizar venta", "detalle": str(exc)}), 500


@venta_bp.route("/ventas/<int:id>", methods=["DELETE"])
def eliminar_venta(id):
    venta = Venta.query.get(id)
    if not venta:
        return jsonify({"mensaje": "Venta no encontrada"}), 404

    try:
        db.session.delete(venta)
        db.session.commit()
        return jsonify({"mensaje": "Venta eliminada"})
    except Exception as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error al eliminar venta", "detalle": str(exc)}), 500
