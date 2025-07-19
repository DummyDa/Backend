from flask import Blueprint, render_template
import logging
from db import conn2

plants_bp = Blueprint("plants", __name__)

@plants_bp.route("/plant/<plant_id>")
def plants(plant_id):
    try:
        with conn2.cursor() as cur2:
            logging.info(f"Запрос с айди {plant_id}")
            table = []
            cur2.execute("SELECT * FROM plants WHERE id = %s", [plant_id])
            rows = cur2.fetchall()
            autor = None
            if not rows:
                logging.warning(f"Растение {plant_id} не найдено")
                return "Ошибка", 404

            for row in rows:
                if row[5] is None:
                    autor = "Владелец сайта"
                else:
                    autor = row[5]
                table = {
                    "name": row[1],
                    "description": row[2],
                    "img": row[3],
                    "vids": row[4],
                    "autor": autor,
                }
            logging.info(f"Растение найдено {plant_id}")
            # raise Exception("Ошибка")
        return render_template("plants.html", table2=table)
    except Exception as e:
        conn2.rollback()
        logging.error(f"Ошибка при выполнении запроса: {e}", exc_info=True)
        return "произошла ошибка при работе с БД", 500
