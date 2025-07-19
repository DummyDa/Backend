from flask import Blueprint, request, render_template
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from user import User
from db import conn, conn2

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
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
                cur.execute(
                    "INSERT INTO users (login, password_hash, username) VALUES (%s, %s, %s)",
                    (login, password_hash, username),
                )
                conn.commit()

            logging.info(f"Пользователь {username} успешно зарегистрировался")
            return "успешно", 200
        return render_template("register.html")
    except Exception as e:
        conn.rollback()
        logging.error(f"Ошибка при выполнении запроса: {e}", exc_info=True)
        return "произошла ошибка при работе с БД", 500


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    logging.info("Пользователь вышел")
    return "Выход выполнен", 200


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        print(login, password)
        if not (login and password):
            logging.warning("Ошибка при входе. Не все данные указаны")
            return "Ошибка регистрации", 400
        with conn.cursor() as cur:
            try:
                logging.info("Попытка войти в аккаунт")
                cur.execute(
                    "SELECT id, login, username, password_hash FROM users WHERE login=%s",
                    [login],
                )
                result = cur.fetchone()
                if not (result and password):
                    return "Неверные данные", 400
                if check_password_hash(result[-1], password):
                    print(result)
                    print(result[0])
                    user = User(result[0], result[1], result[2])
                    print(user.id)
                    login_user(user)
                    return "Успешно", 200
                # rows = cur.fetchall()
                # result = check_user(rows, login, password)
                # if result:
                #     logging.info(f'Пользователь {login} успешно вошел в аккаунт')
                #     return "Успешно", 200
                # else:
                #     logging.warning('Ошибка при входе. Неверные данные')
                #     return "Неверные данные", 500
            except Exception as e:
                conn.rollback()
                logging.error(f"Ошибка при выполнении запроса: {e}", exc_info=True)
                return "Ошибка при работе с БД", 500
    return render_template("login.html")

@auth_bp.route("/users")
def users():
    try:
        users = []
        with conn2.cursor() as cur:
            cur.execute("SELECT * FROM users")
            rows = cur.fetchall()
            for row in rows:
                users.append(f"{row[1]}:{row[2]}")
        return render_template("users.html", users=users)
    except Exception as e:
        conn2.rollback()
        logging.error(f"Ошибка при выполнении запроса: {e}", exc_info=True)
        return "произошла ошибка при работе с БД", 500