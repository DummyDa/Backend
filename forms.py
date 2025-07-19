from flask import Blueprint, render_template, request
import logging
from flask_login import login_required, current_user
from db import conn2

forms_bp = Blueprint("forms", __name__)

@forms_bp.route("/")
def basic():
    return render_template("base.html")

@forms_bp.route("/forms", methods=["GET", "POST"])
@login_required
def forms():
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["desc"]
        img = request.form["img"]
        vids = request.form["vids"]
        type = request.form["type-of-article"]
        try:
            with conn2.cursor() as cur2:
                if type == "plants":
                    cur2.execute(
                        "INSERT INTO plants (plant_name, plant_desc, plant_img, plant_vid, autor) VALUES (%s, %s, %s, %s, %s)",
                        (title, desc, img, vids, current_user.username),
                    )
                elif type == "animals":
                    cur2.execute(
                        "INSERT INTO animals (animal_name, description, img, vids, autor) VALUES (%s, %s, %s, %s, %s)",
                        (title, desc, img, vids, current_user.username),
                    )
                conn2.commit()
            logging.info("Данные в БД записаны успешно")
            return "Успешно"
        except Exception as e:
            conn2.rollback()
            logging.error(f"Ошибка при выполнении запроса: {e}", exc_info=True)
            return "произошла ошибка при работе с БД", 500
    return render_template("forms.html")
