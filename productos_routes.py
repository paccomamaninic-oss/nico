from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from .. import db
from ..models.productos import Producto

producto_bp = Blueprint("producto", __name__)      #agrup

@producto_bp.route("/productos", methods=["GET"]) 
def listar_productos():
    try:
        return jsonify([p.to_dict() for p in Producto.query.all()])
    except Exception as exc:
        return jsonify({"mensaje": "Error al listar productos", "detalle": str(exc)}), 500

@producto_bp.route("/productos/<int:id>", methods=["GET"])
def obtener_producto(id):
    try:
        producto = Producto.query.get(id)                           #bus . id.
        if not producto:                                            #si o no       
            return jsonify({"mensaje": "Producto no encontrado"}), 404
        return jsonify(producto.to_dict())
    except Exception as exc:
        return jsonify({"mensaje": "Error al buscar producto", "detalle": str(exc)}), 500

@producto_bp.route("/productos", methods=["POST"])
def crear_producto():
    data = request.get_json(silent=True) or {}
    payload = {                                     #llamad.
        "id_proveedor": data.get("id_proveedor") if "id_proveedor" in data else data.get("id_proveedores"),
        "nombre": data.get("nombre"),
        "marca": data.get("marca"),
        "precio_venta": data.get("precio_venta"),
    }
    campos_requeridos = ["nombre", "marca", "precio_venta"]
    if any(payload[campo] is None or (isinstance(payload[campo], str) and not str(payload[campo]).strip()) for campo in campos_requeridos):
        return jsonify({"mensaje": "Faltan datos requeridos"}), 400
    try:
        producto = Producto(
            id_proveedores=int(payload["id_proveedor"]) if payload.get("id_proveedor") is not None else None,
            nombre=str(payload["nombre"]).strip(),
            marca=str(payload["marca"]).strip(),
            precio_venta=float(payload["precio_venta"]),
        )
    except (TypeError, ValueError):
        return jsonify({"mensaje": "Datos inválidos"}), 400
    try:
        db.session.add(producto)
        db.session.commit()
        return jsonify({"mensaje": "Producto registrado", "producto": producto.to_dict()}), 201
    except IntegrityError as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error de integridad en la BD", "detalle": str(exc.orig)}), 400
    except Exception as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error al registrar producto", "detalle": str(exc)}), 500

@producto_bp.route("/productos/<int:id>", methods=["PUT"])
def actualizar_producto(id):
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({"mensaje": "Producto no encontrado"}), 404

    data = request.get_json(silent=True) or {}
    try:
        if "id_proveedor" in data and data["id_proveedor"] is not None:
            producto.id_proveedores = int(data["id_proveedor"])
        elif "id_proveedores" in data and data["id_proveedores"] is not None:
            producto.id_proveedores = int(data["id_proveedores"])
        if "nombre" in data and data["nombre"] is not None:
            producto.nombre = str(data["nombre"]).strip()
        if "marca" in data and data["marca"] is not None:
            producto.marca = str(data["marca"]).strip()
        if "precio_venta" in data and data["precio_venta"] is not None:
            producto.precio_venta = float(data["precio_venta"])
        db.session.commit()
        return jsonify({"mensaje": "Producto actualizado", "producto": producto.to_dict()})
    except (TypeError, ValueError):
        return jsonify({"mensaje": "Datos inválidos"}), 400
   
@producto_bp.route("/productos/<int:id>", methods=["DELETE"])
def eliminar_producto(id):
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({"mensaje": "Producto no encontrado"}), 404
    try:
        db.session.delete(producto)
        db.session.commit()
        return jsonify({"mensaje": "Producto eliminado"})
    except Exception as exc:
        db.session.rollback()
        return jsonify({"mensaje": "Error al eliminar producto", "detalle": str(exc)}), 500
