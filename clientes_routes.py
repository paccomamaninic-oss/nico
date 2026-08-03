from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from .. import db
from ..models.clientes import Cliente

cliente_bp = Blueprint("cliente", __name__)


@cliente_bp.route("/clientes", methods=["GET"])
def listar_clientes():
    try:
        return jsonify([c.to_dict() for c in Cliente.query.all()])
    except Exception as exc:
        return jsonify({"mensaje": "Error al listar clientes", "detalle": str(exc)}), 500


@cliente_bp.route("/clientes/<int:id>", methods=["GET"])
def obtener_cliente(id):
    try:
        cliente = Cliente.query.get(id)
        if not cliente:
            return jsonify({"mensaje": "Cliente no encontrado"}), 404
        return jsonify(cliente.to_dict())
    except Exception as exc:
        return jsonify({"mensaje": "Error al buscar cliente", "detalle": str(exc)}), 500


@cliente_bp.route("/clientes", methods=["POST"])
def crear_cliente():
    data = request.get_json(silent=True) or {}
    campos = ["nombre", "email", "telefono", "direccion"]
    if not all(campo in data and data[campo] is not None for campo in campos):
        return jsonify({"mensaje": "Faltan datos requeridos"}), 400

    try:
        cliente = Cliente(
            nombre=str(data["nombre"]).strip(),
            email=str(data["email"]).strip(),
            telefono=str(data["telefono"]).strip(),
            direccion=str(data["direccion"]).strip(),
        )
        db.session.add(cliente)
        db.session.commit()
        return jsonify({"mensaje": "Cliente registrado", "cliente": cliente.to_dict()}), 201
    except IntegrityError as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error de integridad en la BD", "detalle": str(exc.orig)}), 400
    except Exception as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error al registrar cliente", "detalle": str(exc)}), 500


@cliente_bp.route("/clientes/<int:id>", methods=["PUT"])
def actualizar_cliente(id):
    cliente = Cliente.query.get(id)
    if not cliente:
        return jsonify({"mensaje": "Cliente no encontrado"}), 404

    data = request.get_json(silent=True) or {}
    try:
        if "nombre" in data and data["nombre"] is not None:
            cliente.nombre = str(data["nombre"]).strip()
        if "email" in data and data["email"] is not None:
            cliente.email = str(data["email"]).strip()
        if "telefono" in data and data["telefono"] is not None:
            cliente.telefono = str(data["telefono"]).strip()
        if "direccion" in data and data["direccion"] is not None:
            cliente.direccion = str(data["direccion"]).strip()
        db.session.commit()
        return jsonify({"mensaje": "Cliente actualizado", "cliente": cliente.to_dict()})
    except IntegrityError as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error de integridad en la BD", "detalle": str(exc.orig)}), 400
    except Exception as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error al actualizar cliente", "detalle": str(exc)}), 500


@cliente_bp.route("/clientes/<int:id>", methods=["DELETE"])
def eliminar_cliente(id):
    cliente = Cliente.query.get(id)
    if not cliente:
        return jsonify({"mensaje": "Cliente no encontrado"}), 404

    try:
        db.session.delete(cliente)
        db.session.commit()
        return jsonify({"mensaje": "Cliente eliminado"})
    except Exception as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error al eliminar cliente", "detalle": str(exc)}), 500
