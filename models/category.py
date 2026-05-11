from database.db_manager import get_connection

class Category:
    def __init__(self, id=None, name=None, type_id=None, obligation_id=None):
        self.id = id
        self.name = name
        self.type_id = type_id
        self.obligation_id = obligation_id

    def save(self):
        conn = get_connection()
        cur = conn.cursor()
        if self.id is None:
            cur.execute('''INSERT INTO Category (CategoryName, TypeID, ObligationID)
                VALUES (?, ?, ?)''', (self.name, self.type_id, self.obligation_id))
            self.id = cur.lastrowid
        else:
            cur.execute('''
                UPDATE Category SET CategoryName=?, TypeID=?, ObligationID=?
                WHERE CategoryID=?
            ''', (self.name, self.type_id, self.obligation_id, self.id))
        conn.commit()
        conn.close()

    def delete(self):
        if self.id is None:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('''DELETE FROM Category WHERE CategoryID=?''', (self.id,))
            conn.commit()
            conn.close()

def get_all_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''SELECT CategoryID, CategoryName, TypeID, ObligationID FROM Category''')
    rows = cur.fetchall()
    conn.close()
    return [Category(id=row[0], name=row[1], type_id=row[2], obligation_id=row[3]) for row in rows]

def get_categories_by_type(type_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''SELECT CategoryID, CategoryName, TypeID, ObligationID FROM Category WHERE TypeID=?''', (type_id,))
    rows = cur.fetchall()
    conn.close()
    return [Category(id=row[0], name=row[1], type_id=row[2], obligation_id=row[3]) for row in rows]