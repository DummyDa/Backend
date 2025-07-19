from flask import Blueprint
import logging
from db import conn2

navigation_bp = Blueprint("navigation", __name__)

def data():
    with conn2.cursor() as cur2:
        animals = {}
        plants = {}
        cur2.execute("SELECT * FROM animals")
        rows = cur2.fetchall()
        cur2.execute("SELECT * FROM plants")
        rows2 = cur2.fetchall()
        for animal in rows:
            animals[animal[0]] = ["animal", animal[1]]
        for plant in rows2:
            plants[plant[0]] = ["plant", plant[1]]
    logging.info("Информация получена")
    return {
        "navigation": {
            "Животные": animals,
            "Растения": plants,
        }
    }
