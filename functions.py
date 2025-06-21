from werkzeug.security import check_password_hash

def check_user(rows, login, password):
    for row in rows:
        if row[0] == login:
            if check_password_hash(row[1], password):   
                return True
            else:
                return False