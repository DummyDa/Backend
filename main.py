from flask import Flask, render_template, request
from dotenv import load_dotenv
from datas import *
import os
import psycopg2
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("DBNAME"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    host=os.getenv("HOST"),
    port=os.getenv("PORT")
)

conn2 = psycopg2.connect(
    dbname=os.getenv("DBNAME2"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    host=os.getenv("HOST"),
    port=os.getenv("PORT")
)
# cur = conn.cursor()

# cur2 = conn2.cursor()

app = Flask(__name__)

game = {}

@app.context_processor
def data():
    with conn2.cursor() as cur2:
        animals = {}
        plants = {}
        cur2.execute("SELECT * FROM animals")
        rows = cur2.fetchall()
        cur2.execute("SELECT * FROM plants")
        rows2 = cur2.fetchall()
        print(rows2)
        for animal in rows:
            animals[animal[0]] = ["animal", animal[1]]
        for plant in rows2:
            plants[plant[0]] = ["plant", plant[1]]
    logging.info("Информация получена")
    return {
        "navigation" : {
            "Животные" : animals,
            "Растения" : plants,
        }
    }

@app.route("/animal/<animal_id>")
def index(animal_id):
    try:
        with conn2.cursor() as cur2:
            logging.info(f'Запрос с айди {animal_id}')
            table = []
            cur2.execute("SELECT * FROM animals WHERE id = %s", [animal_id])
            rows = cur2.fetchall()
            if not rows:
                logging.warning(f'Животное {animal_id} не найдено')
                return "Ошибка", 404
            for row in rows:
                table = {
                    "name" : row[1],
                    "description" : row[2],
                    "img" : row[3],
                    "vids" : row[4]
                }
        return render_template("index.html", table2=table)
    except Exception as e:
        conn2.rollback()
        logging.error(f"Ошибка при выполнении запроса: {e}", exc_info=True)
        return f'произошла ошибка при работе с БД', 500

@app.route("/plant/<plant_id>")
def plants(plant_id):
    try:
        with conn2.cursor() as cur2:
            logging.info(f'Запрос с айди {plant_id}')
            table = []
            cur2.execute("SELECT * FROM plants WHERE id = %s", [plant_id])
            rows = cur2.fetchall()

        if not rows:
            logging.warning(f'Растение {plant_id} не найдено')
            return "Ошибка", 404

        for row in rows:
            table = {
                "name" : row[1],
                "description" : row[2],
                "img" : row[3],
                "vids" : row[4]
            }
        logging.info(f"Растение найдено {plant_id}")
           # raise Exception("Ошибка")
        return render_template("plants.html", table2=table)
    except Exception as e:
        conn2.rollback()
        logging.error(f"Ошибка при выполнении запроса: {e}", exc_info=True)
        return f'произошла ошибка при работе с БД', 500

@app.route("/")
def basic():
    return render_template("base.html")

# @app.route("/frogs")
# def frogs():
#     return render_template("index.html", table2=frogs_data)

# @app.route("/snails")
# def snails():
#     return render_template("index.html", table2=snails_data)

# @app.route("/dynos")
# def dynos():
#     return render_template("index.html", table2=dynos_data)

# @app.route("/pig")
# def pigs():
#     return render_template("index.html", table2=pig_data)

# @app.route("/chamomile")
# def chamomile():
#     return render_template("plants.html", table2=chamomile_data)

# @app.route("/tulip")
# def tulip():
#     return render_template("plants.html", table2=tulip_data)

# @app.route("/cactus")
# def cactus():
#     return render_template("plants.html", table2=cactus_data)

@app.route("/forms", methods=["GET", "POST"])
def forms():
    if request.method == "POST":
        title = request.form["animal-title"]
        desc = request.form["desc"]
        img = request.form["img"]
        vids = request.form["animal-vids"]
        try:
            with conn2.cursor() as cur2:
                cur2.execute("INSERT INTO plants (plant_name, plant_desc, plant_img, plant_vid) VALUES (%s, %s, %s, %s)", (title, desc, img, vids))
                conn2.commit()
            logging.info("Данные в БД записаны успешно")
            return "Успешно"
        except Exception as e:
            conn2.rollback()
            logging.error(f"Ошибка при выполнении запроса: {e}", exc_info=True)
            return f'произошла ошибка при работе с БД', 500
    return render_template("forms.html")

@app.route("/converter", methods=["GET", "POST"])
def converter():
    if request.method == "POST":
        currency = request.form["currency"]
        summa = request.form["summa"]
        return str(kurs[currency] * int(summa))
    return render_template("converter.html")  

@app.route("/register", methods=["GET", "POST"])
def register():
    try:
        if request.method == "POST":
            user_name = request.form["user-name"]
            password = request.form["password"]
            with conn2.cursor() as cur:
                cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user_name, password))
                conn.commit()
            # file = open("users.txt", "a", encoding="utf-8")
            # file.write(f'{user_name}:{password}\n')
            # file.close()
            logging.info(f"Пользователь {user_name} успешно зарегистрировался")
            return "успешно"
        return render_template("register.html")
    except Exception as e:
        conn2.rollback()
        logging.error(f"Ошибка при выполнении запроса: {e}", exc_info=True)
        return f'произошла ошибка при работе с БД', 500

@app.route("/users")
def users():
    try:
        users = []
        with conn2.cursor() as cur:
            cur.execute("SELECT * FROM users")
            rows = cur.fetchall()
            for row in rows:
                users.append(f'{row[1]}:{row[2]}')
        return render_template("users.html", users=users)
    except Exception as e:
        conn2.rollback()
        logging.error(f"Ошибка при выполнении запроса: {e}", exc_info=True)
        return f'произошла ошибка при работе с БД', 500

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()