from database.db_manager import get_connection

class Type:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

def get_all_types():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''SELECT TypeID, TypeName FROM Type''')
    rows = cur.fetchall()
    conn.close()
    return [Type(id=row[0], name=row[1]) for row in rows]