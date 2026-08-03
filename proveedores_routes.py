from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from .. import db
from ..models.proveedores import Proveedor

proveedor_bp = Blueprint("proveedor", __name__)


# LISTAR TODOS LOS PROVEEDORES
@proveedor_bp.route("/proveedores", methods=["GET"])
def listar_proveedores():
    try:
        proveedores = Proveedor.query.all()
        return jsonify([proveedor.to_dict() for proveedor in proveedores])
    except Exception as e:
        return jsonify({"mensaje": "Error al listar proveedores", "detalle": str(e)}), 500


# BUSCAR PROVEEDOR POR ID
@proveedor_bp.route("/proveedores/<int:id>", methods=["GET"])
def obtener_proveedor(id):
    try:
        proveedor = Proveedor.query.get(id)
        if not proveedor:
            return jsonify({"mensaje": "Proveedor no encontrado"}), 404
        return jsonify(proveedor.to_dict())
    except Exception as e:
        return jsonify({"mensaje": "Error al buscar proveedor", "detalle": str(e)}), 500


# REGISTRAR PROVEEDOR
@proveedor_bp.route("/proveedores", methods=["POST"])
def crear_proveedor():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"mensaje": "JSON inválido o faltante"}), 400

        # Validar campos requeridos
        nombre_empresa = data.get("nombre_empresa")
        contactos = data.get("contactos")
        email = data.get("email")
        telefono = data.get("telefono")

        if nombre_empresa is None or not str(nombre_empresa).strip():
            return jsonify({"mensaje": "El campo 'nombre_empresa' es requerido"}), 400
        if contactos is None or not str(contactos).strip():
            return jsonify({"mensaje": "El campo 'contactos' es requerido"}), 400
        if email is None or not str(email).strip():
            return jsonify({"mensaje": "El campo 'email' es requerido"}), 400
        if telefono is None or not str(telefono).strip():
            return jsonify({"mensaje": "El campo 'telefono' es requerido"}), 400

        # Limpiar strings
        nombre_empresa = str(nombre_empresa).strip()
        contactos = str(contactos).strip()
        email = str(email).strip()
        telefono = str(telefono).strip()

        # Crear nuevo proveedor
        nuevo_proveedor = Proveedor(
            nombre_empresa=nombre_empresa,
            contactos=contactos,
            email=email,
            telefono=telefono
        )

        db.session.add(nuevo_proveedor)
        db.session.commit()

        return jsonify({
            "mensaje": "Proveedor registrado correctamente",
            "proveedor": nuevo_proveedor.to_dict()
        }), 201

    except IntegrityError as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error de integridad en la BD", "detalle": str(exc.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"mensaje": "Error al registrar proveedor", "detalle": str(e)}), 500


# ACTUALIZAR PROVEEDOR
@proveedor_bp.route("/proveedores/<int:id>", methods=["PUT"])
def actualizar_proveedor(id):
    try:
        proveedor = Proveedor.query.get(id)
        if not proveedor:
            return jsonify({"mensaje": "Proveedor no encontrado"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "JSON inválido o faltante"}), 400

        # Actualizar nombre_empresa si viene en el JSON
        if "nombre_empresa" in data and data["nombre_empresa"] is not None:
            nombre_empresa = str(data["nombre_empresa"]).strip()
            if not nombre_empresa:
                return jsonify({"mensaje": "El campo 'nombre_empresa' no puede estar vacío"}), 400
            proveedor.nombre_empresa = nombre_empresa

        # Actualizar contactos si viene en el JSON
        if "contactos" in data and data["contactos"] is not None:
            contactos = str(data["contactos"]).strip()
            if not contactos:
                return jsonify({"mensaje": "El campo 'contactos' no puede estar vacío"}), 400
            proveedor.contactos = contactos

        # Actualizar email si viene en el JSON
        if "email" in data and data["email"] is not None:
            email = str(data["email"]).strip()
            if not email:
                return jsonify({"mensaje": "El campo 'email' no puede estar vacío"}), 400
            proveedor.email = email

        # Actualizar telefono si viene en el JSON
        if "telefono" in data and data["telefono"] is not None:
            telefono = str(data["telefono"]).strip()
            if not telefono:
                return jsonify({"mensaje": "El campo 'telefono' no puede estar vacío"}), 400
            proveedor.telefono = telefono

        db.session.commit()

        return jsonify({
            "mensaje": "Proveedor actualizado correctamente",
            "proveedor": proveedor.to_dict()
        })

    except IntegrityError as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error de integridad en la BD", "detalle": str(exc.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"mensaje": "Error al actualizar proveedor", "detalle": str(e)}), 500


# ELIMINAR PROVEEDOR
@proveedor_bp.route("/proveedores/<int:id>", methods=["DELETE"])
def eliminar_proveedor(id):
    try:
        proveedor = Proveedor.query.get(id)
        if not proveedor:
            return jsonify({"mensaje": "Proveedor no encontrado"}), 404

        db.session.delete(proveedor)
        db.session.commit()

        return jsonify({"mensaje": "Proveedor eliminado correctamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"mensaje": "Error al eliminar proveedor", "detalle": str(e)}), 500
