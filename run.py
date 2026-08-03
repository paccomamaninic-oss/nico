from app import create_app, db
import os
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        db.create_all()

        db_name = os.getenv("DB_NAME")
        if db_name:
            q = text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA=:schema AND TABLE_NAME='productos' AND COLUMN_NAME='id_proveedores'"
            )
            res = db.session.execute(q, {"schema": db_name}).scalar()
            if res == 0:
                alter = text("ALTER TABLE productos ADD COLUMN id_proveedores INT NULL;")
                db.session.execute(alter)
                db.session.commit()

            fk_exists = text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
                "WHERE TABLE_SCHEMA=:schema AND TABLE_NAME='productos' "
                "AND COLUMN_NAME='id_proveedores' AND REFERENCED_TABLE_NAME='proveedores'"
            )
            fk_count = db.session.execute(fk_exists, {"schema": db_name}).scalar()
            if fk_count == 0:
                db.session.execute(
                    text(
                        "ALTER TABLE productos ADD CONSTRAINT fk_productos_proveedores "
                        "FOREIGN KEY (id_proveedores) REFERENCES proveedores(id)"
                    )
                )
                db.session.commit()

            compras_fk_exists = text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
                "WHERE TABLE_SCHEMA=:schema AND TABLE_NAME='compras' "
                "AND COLUMN_NAME='id_proveedores' AND REFERENCED_TABLE_NAME='proveedores'"
            )
            compras_fk_count = db.session.execute(compras_fk_exists, {"schema": db_name}).scalar()
            if compras_fk_count == 0:
                db.session.execute(
                    text(
                        "ALTER TABLE compras ADD CONSTRAINT fk_compras_proveedores "
                        "FOREIGN KEY (id_proveedores) REFERENCES proveedores(id)"
                    )
                )
                db.session.commit()

            detalle_columns = text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA=:schema AND TABLE_NAME='detalles_compras' AND COLUMN_NAME='id_productos'"
            )
            detalle_res = db.session.execute(detalle_columns, {"schema": db_name}).scalar()
            if detalle_res == 0:
                old_col = text(
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                    "WHERE TABLE_SCHEMA=:schema AND TABLE_NAME='detalles_compras' AND COLUMN_NAME='id_proveedores'"
                )
                old_res = db.session.execute(old_col, {"schema": db_name}).scalar()

                fk_name = db.session.execute(
                    text(
                        "SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
                        "WHERE TABLE_SCHEMA=:schema AND TABLE_NAME='detalles_compras' "
                        "AND REFERENCED_TABLE_NAME='proveedores' LIMIT 1"
                    ),
                    {"schema": db_name},
                ).scalar()
                if fk_name:
                    db.session.execute(text(f"ALTER TABLE detalles_compras DROP FOREIGN KEY `{fk_name}`"))

                if old_res > 0:
                    db.session.execute(
                        text("ALTER TABLE detalles_compras CHANGE COLUMN id_proveedores id_productos INT NOT NULL")
                    )
                else:
                    db.session.execute(
                        text("ALTER TABLE detalles_compras ADD COLUMN id_productos INT NOT NULL")
                    )

                db.session.execute(
                    text(
                        "ALTER TABLE detalles_compras ADD CONSTRAINT fk_detalles_compras_productos "
                        "FOREIGN KEY (id_productos) REFERENCES productos(id)"
                    )
                )
                db.session.commit()
    except Exception as exc:
        print(f"No se pudo inicializar la base de datos: {exc}")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
