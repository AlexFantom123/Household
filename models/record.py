from database.db_manager import get_connection
from datetime import datetime

class Record:
    def __init__(self, id=None, user_id=None, category_id=None, date=None, sum=None):
        self.id = id
        self.user_id = user_id
        self.category_id = category_id
        self.date = date
        self.sum = sum

    def save(self):
        conn = get_connection()
        cur = conn.cursor()
        if self.id is None:
            cur.execute('''
                INSERT INTO Record (UserID, CategoryID, Date, Sum)
                VALUES (?, ?, ?, ?)
            ''', (self.user_id, self.category_id, self.date, self.sum))
            self.id = cur.lastrowid
        else:
            cur.execute('''
                UPDATE Record SET UserID=?, CategoryID=?, Date=?, Sum=?
                WHERE RecordID=?
            ''', (self.user_id, self.category_id, self.date, self.sum, self.id))
        conn.commit()
        conn.close()
        # Обновляем отчёт за месяц
        from models.report import generate_monthly_report
        if self.date:
            generate_monthly_report(self.date[:7])

    def delete(self):
        if self.id is not None:
            # Запоминаем месяц перед удалением
            month = self.date[:7] if self.date else None
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('''DELETE FROM Record WHERE RecordID=?''', (self.id,))
            conn.commit()
            conn.close()
            # Обновляем отчёт за месяц
            if month:
                from models.report import generate_monthly_report
                generate_monthly_report(month)

def get_all_records(user_id=None):
    conn = get_connection()
    cur = conn.cursor()
    if user_id:
        cur.execute('''SELECT RecordID, UserID, CategoryID, Date, Sum FROM Record WHERE UserID=? ORDER BY Date DESC''', (user_id,))
    else:
        cur.execute('''SELECT RecordID, UserID, CategoryID, Date, Sum FROM Record ORDER BY Date DESC''')
    rows = cur.fetchall()
    conn.close()
    return [Record(id=row[0], user_id=row[1], category_id=row[2], date=row[3], sum=row[4]) for row in rows]

def get_records_by_month(user_id, year_month):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT RecordID, UserID, CategoryID, Date, Sum
        FROM Record
        WHERE UserID=? AND strftime(‘%Y-%m’, Date)=?
        ORDER BY Date DESC
    ''', (user_id, year_month))
    rows = cur.fetchall()
    conn.close()
    return [Record(id=row[0], user_id=row[1], category_id=row[2], date=row[3], sum=row[4]) for row in rows]