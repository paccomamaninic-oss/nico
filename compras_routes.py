from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from .. import db
from ..models.compras import Compra
from datetime import datetime

compra_bp = Blueprint("compra", __name__)


# LISTAR TODAS LAS COMPRAS
@compra_bp.route("/compras", methods=["GET"])
def listar_compras():
    try:
        compras = Compra.query.all()
        return jsonify([compra.to_dict() for compra in compras])
    except Exception as e:
        return jsonify({"mensaje": "Error al listar compras", "detalle": str(e)}), 500


# BUSCAR COMPRA POR ID
@compra_bp.route("/compras/<int:id>", methods=["GET"])
def obtener_compra(id):
    try:
        compra = Compra.query.get(id)
        if not compra:
            return jsonify({"mensaje": "Compra no encontrada"}), 404
        return jsonify(compra.to_dict())
    except Exception as e:
        return jsonify({"mensaje": "Error al buscar compra", "detalle": str(e)}), 500


# REGISTRAR COMPRA
@compra_bp.route("/compras", methods=["POST"])
def crear_compra():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"mensaje": "JSON inválido o faltante"}), 400

        # Validar campos requeridos
        id_proveedores = data.get("id_proveedores")
        fecha = data.get("fecha")
        total = data.get("total", 0)
        estado = data.get("estado")

        if id_proveedores is None:
            return jsonify({"mensaje": "El campo 'id_proveedores' es requerido"}), 400
        if fecha is None or not str(fecha).strip():
            return jsonify({"mensaje": "El campo 'fecha' es requerido"}), 400
        if estado is None or not str(estado).strip():
            return jsonify({"mensaje": "El campo 'estado' es requerido"}), 400

        # Convertir y validar total
        try:
            total = float(total)
            if total < 0:
                return jsonify({"mensaje": "El total no puede ser negativo"}), 400
        except (TypeError, ValueError):
            return jsonify({"mensaje": "El campo total debe ser un número válido"}), 400

        # Convertir id_proveedores a int
        try:
            id_proveedores = int(id_proveedores)
        except (TypeError, ValueError):
            return jsonify({"mensaje": "El campo id_proveedores debe ser un número entero válido"}), 400

        # Limpiar strings
        estado = str(estado).strip()

        # Convertir fecha si es string
        if isinstance(fecha, str):
            try:
                fecha = datetime.fromisoformat(fecha)
            except:
                return jsonify({"mensaje": "El campo fecha debe estar en formato ISO (YYYY-MM-DD)"}), 400

        # Crear nueva compra
        nueva_compra = Compra(
            id_proveedores=id_proveedores,
            fecha=fecha,
            total=total,
            estado=estado
        )

        db.session.add(nueva_compra)
        db.session.commit()

        return jsonify({
            "mensaje": "Compra registrada correctamente",
            "compra": nueva_compra.to_dict()
        }), 201

    except IntegrityError as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error de integridad en la BD", "detalle": str(exc.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"mensaje": "Error al registrar compra", "detalle": str(e)}), 500


# ACTUALIZAR COMPRA
@compra_bp.route("/compras/<int:id>", methods=["PUT"])
def actualizar_compra(id):
    try:
        compra = Compra.query.get(id)
        if not compra:
            return jsonify({"mensaje": "Compra no encontrada"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "JSON inválido o faltante"}), 400

        # Actualizar id_proveedores si viene en el JSON
        if "id_proveedores" in data and data["id_proveedores"] is not None:
            try:
                id_proveedores = int(data["id_proveedores"])
                compra.id_proveedores = id_proveedores
            except (TypeError, ValueError):
                return jsonify({"mensaje": "El campo id_proveedores debe ser un número entero válido"}), 400

        # Actualizar fecha si viene en el JSON
        if "fecha" in data and data["fecha"] is not None:
            try:
                if isinstance(data["fecha"], str):
                    fecha = datetime.fromisoformat(data["fecha"])
                else:
                    fecha = data["fecha"]
                compra.fecha = fecha
            except:
                return jsonify({"mensaje": "El campo fecha debe estar en formato ISO (YYYY-MM-DD)"}), 400

        # Actualizar total si viene en el JSON
        if "total" in data and data["total"] is not None:
            try:
                total = float(data["total"])
                if total < 0:
                    return jsonify({"mensaje": "El total no puede ser negativo"}), 400
                compra.total = total
            except (TypeError, ValueError):
                return jsonify({"mensaje": "El campo total debe ser un número válido"}), 400

        # Actualizar estado si viene en el JSON
        if "estado" in data and data["estado"] is not None:
            estado = str(data["estado"]).strip()
            if not estado:
                return jsonify({"mensaje": "El campo 'estado' no puede estar vacío"}), 400
            compra.estado = estado

        db.session.commit()

        return jsonify({
            "mensaje": "Compra actualizada correctamente",
            "compra": compra.to_dict()
        })

    except IntegrityError as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error de integridad en la BD", "detalle": str(exc.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"mensaje": "Error al actualizar compra", "detalle": str(e)}), 500


# ELIMINAR COMPRA
@compra_bp.route("/compras/<int:id>", methods=["DELETE"])
def eliminar_compra(id):
    try:
        compra = Compra.query.get(id)
        if not compra:
            return jsonify({"mensaje": "Compra no encontrada"}), 404

        db.session.delete(compra)
        db.session.commit()

        return jsonify({"mensaje": "Compra eliminada correctamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"mensaje": "Error al eliminar compra", "detalle": str(e)}), 500
