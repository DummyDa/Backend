from flask import Flask, render_template, request
from dotenv import load_dotenv
from datas import kurs
from werkzeug.security import generate_password_hash, check_password_hash
from functions import check_user
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
        return 'произошла ошибка при работе с БД ', 500

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
        return 'произошла ошибка при работе с БД', 500

@app.route("/")
def basic():
    return render_template("base.html")

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
            return 'произошла ошибка при работе с БД', 500
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
            login = request.form.get("login")
            username = request.form.get("username")
            password = request.form.get("password")
            if not (login and password and username):
                logging.warning("Ошибка при регистрации. Не все данные указаны")
                return "Ошибка регистрации", 500
            password_hash = generate_password_hash(password)
            with conn.cursor() as cur:
                logging.info("Попытка зарегестрироваться")
                cur.execute("INSERT INTO users (login, password_hash, username) VALUES (%s, %s, %s)", (login, password_hash, username))
                conn.commit()

            logging.info(f"Пользователь {username} успешно зарегистрировался")
            return "успешно", 200
        return render_template("register.html")
    except Exception as e:
        conn.rollback()
        logging.error(f"Ошибка при выполнении запроса: {e}", exc_info=True)
        return 'произошла ошибка при работе с БД', 500

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        print(login, password)
        if not (login and password):
            logging.warning("Ошибка при входе. Не все данные указаны")
            return "Ошибка регистрации", 500
        with conn.cursor() as cur:
            try:
                logging.info("Попытка войти в аккаунт")
                cur.execute("SELECT login, password_hash FROM users")
                rows = cur.fetchall()
                result = check_user(rows, login, password)
                if result:
                    logging.info(f'Пользователь {login} успешно вошел в аккаунт')
                    return "Успешно", 200
                else:
                    logging.warning('Ошибка при входе. Неверные данные')
                    return "Неверные данные", 500
            except Exception as e:
                conn.rollback()
                logging.error(f'Ошибка при выполнении запроса: {e}', exc_info=True)
                return "Ошибка при работе с БД", 500
    return render_template("login.html")

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
        return 'произошла ошибка при работе с БД', 500

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()