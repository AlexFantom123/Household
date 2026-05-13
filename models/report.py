from database.db_manager import get_connection

def generate_monthly_report(year_month, user_id=None):
    conn = get_connection()
    cur = conn.cursor()
    where_clause = "WHERE strftime('%Y-%m', Record.Date) = ?"
    params = [year_month]
    if user_id is not None:
        where_clause += " AND Record.UserID = ?"
        params.append(user_id)
    cur.execute(f'''
        SELECT
            Record.CategoryID,
            COALESCE(SUM(Record.Sum), 0) as SumMonth
        FROM Record
        {where_clause}
        GROUP BY Record.CategoryID
    ''', params)
    category_totals = cur.fetchall()
    # Проверяем, существует ли уже отчёт
    cur.execute('SELECT ReportID FROM ReportAtMonth WHERE Date = ?', (year_month,))
    existing_report = cur.fetchone()
    if existing_report:
        report_id = existing_report[0]  # Исправлено: извлекаем значение из кортежа
        cur.execute('DELETE FROM TotalAtMonth WHERE ReportID = ?', (report_id,))
    else:
        cur.execute('INSERT INTO ReportAtMonth (Date) VALUES (?)', (year_month,))
        cur.execute('SELECT ReportID FROM ReportAtMonth WHERE Date = ?', (year_month,))
        report_id = cur.fetchone()[0]  # Исправлено: извлекаем значение из кортежа
    for category_id, amount in category_totals:
        if amount != 0:
            cur.execute('''
                INSERT INTO TotalAtMonth (ReportID, CategoryID, SumMonth)
                VALUES (?, ?, ?)
            ''', (report_id, category_id, amount))
    conn.commit()
    conn.close()
    return get_report_data(year_month, user_id)

def update_monthly_report(year_month, user_id=None):
    existing_report = get_report_data(year_month, user_id)
    if not existing_report:
        return None
    return generate_monthly_report(year_month, user_id)

def get_report_data(year_month, user_id=None):
    conn = get_connection()
    cur = conn.cursor()
    base_query = """
        SELECT
            ReportAtMonth.ReportID,
            ReportAtMonth.Date,
            Category.CategoryID,
            Category.CategoryName,
            Type.TypeName AS TypeName,
            COALESCE(Obligation.ObligationName, '—') AS ObligationName,
            COALESCE(TotalAtMonth.SumMonth, 0) AS SumMonth
        FROM ReportAtMonth
        LEFT JOIN TotalAtMonth ON ReportAtMonth.ReportID = TotalAtMonth.ReportID
        LEFT JOIN Category ON TotalAtMonth.CategoryID = Category.CategoryID
        LEFT JOIN Type ON Category.TypeID = Type.TypeID
        LEFT JOIN Obligation ON Category.ObligationID = Obligation.ObligationID
        WHERE ReportAtMonth.Date = ?
        ORDER BY Category.CategoryName
    """
    params = [year_month]
    try:
        cur.execute(base_query, params)
        rows = cur.fetchall()
        if not rows or not rows[0][0]:  # Если нет ReportID, значит отчёт не существует
            return None
        result = []
        for row in rows:
            # Проверяем, есть ли данные категории
            if row[2] is None:  # Нет категорий в отчёте
                continue
            result.append({
                "report_id": row[0],
                "date": row[1],
                "category_id": row[2],
                "category_name": row[3],
                "type_name": row[4],
                "obligation_name": row[5],
                "sum_month": float(row[6]) if row[6] else 0.0
            })
        return result if result else None
    except Exception as e:
        print(f"Ошибка при получении данных отчёта: {e}")
        return None
    finally:
        conn.close()

def get_available_months(user_id=None):
    conn = get_connection()
    cur = conn.cursor()
    if user_id is not None:
        cur.execute('''
            SELECT DISTINCT strftime("%Y-%m", Date) as Month
            FROM Record
            WHERE UserID = ?
            ORDER BY Month DESC
        ''', (user_id,))
    else:
        cur.execute('''
            SELECT DISTINCT strftime("%Y-%m", Date) as Month
            FROM Record
            ORDER BY Month DESC
        ''')
    # Исправлено: извлекаем первый элемент из каждого кортежа
    months = [row[0] for row in cur.fetchall()]
    conn.close()
    return months