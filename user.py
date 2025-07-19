from flask_login import UserMixin
import logging
from db import conn

class User(UserMixin):
    def __init__(self, id, login, username):
        self.id = id
        self.login = login
        self.username = username

def load_user(user_id):
    try:
        user_id = int(user_id)
        with conn.cursor() as cur:
            cur.execute("SELECT id, login, username FROM users WHERE id =%s", [user_id])
            result = cur.fetchone()
            if result:
                return User(*result)
    except Exception as e:
        conn.rollback()
        logging.error(f"Ошибка при загрузке пользователя {e}", exc_info=True)
    return None