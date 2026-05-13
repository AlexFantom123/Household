from database.db_manager import get_connection

class Obligation:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

def get_all_obligations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''SELECT ObligationID, ObligationName FROM Obligation''')
    rows = cur.fetchall()
    conn.close()
    return [Obligation(id=row[0], name=row[1]) for row in rows]  