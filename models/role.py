from database.db_manager import get_connection

class Role:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

def get_all_roles():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT RoleID, RoleName FROM Role")
    rows = cursor.fetchall()
    conn.close()
    return [Role(id=row[0], name=row[1]) for row in rows]