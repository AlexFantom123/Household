from database.db_manager import get_connection

class User:
    def __init__(self, id=None, role_id=None, login=None, password=None, name=None):
        self.id = id
        self.role_id = role_id
        self.login = login
        self.password = password
        self.name = name

    def save(self):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Проверка: если пытаемся создать администратора
        if self.role_id == 1 and self.id is None:
            cursor.execute("SELECT COUNT(*) FROM User WHERE RoleID = 1")
            admin_count = cursor.fetchone()[0]
            if admin_count > 0:
                conn.close()
                raise Exception("Администратор уже существует! Нельзя создать второго.")
        
        if self.id is None:
            cursor.execute('''
                INSERT INTO User (RoleID, Login, Password, UserName)
                VALUES (?, ?, ?, ?)
            ''', (self.role_id, self.login, self.password, self.name))
            self.id = cursor.lastrowid
        else:
            cursor.execute('''
                UPDATE User SET RoleID=?, Login=?, Password=?, UserName=?
                WHERE UserID=?
            ''', (self.role_id, self.login, self.password, self.name, self.id))
        conn.commit()
        conn.close()

    def delete(self):
        if self.id is not None:
            conn = get_connection()
            cursor = conn.cursor()
            # Проверка: нельзя удалить единственного администратора
            cursor.execute("SELECT RoleID FROM User WHERE UserID=?", (self.id,))
            role = cursor.fetchone()
            if role and role[0] == 1:
                cursor.execute("SELECT COUNT(*) FROM User WHERE RoleID = 1")
                admin_count = cursor.fetchone()[0]
                if admin_count <= 1:
                    conn.close()
                    raise Exception("Нельзя удалить единственного администратора!")
            cursor.execute("DELETE FROM User WHERE UserID=?", (self.id,))
            conn.commit()
            conn.close()

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT UserID, RoleID, Login, Password, UserName FROM User")
    rows = cursor.fetchall()
    conn.close()
    return [User(id=row[0], role_id=row[1], login=row[2], password=row[3], name=row[4]) for row in rows]

def authenticate(login, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT UserID, RoleID, Login, Password, UserName FROM User WHERE Login=? AND Password=?", (login, password))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(id=row[0], role_id=row[1], login=row[2], password=row[3], name=row[4])
    return None

def is_admin_exists():
    """Проверяет, существует ли хотя бы один администратор"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM User WHERE RoleID = 1")
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0