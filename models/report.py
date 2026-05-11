from database.db_manager import get_connection
def generate_monthly_report(year_month):
    #Генерирует отчёт за указанный месяц (формат ‘2025-05’)
    #Возвращает словарь с итогами по категориям
    conn = get_connection()
    cur = conn.cursor()
    # Получаем агрегированные данные по категориям за месяц
    cur.execute('''
        SELECT
            Record.CategoryID,
            COALESCE(SUM(Record.Sum), 0) as SumMonth
        FROM Record
        WHERE strftime("%Y-%m", Record.Date) = ?
        GROUP BY Record.CategoryID''', (year_month,))
    category_totals = cur.fetchall()
    # Создаём или получаем отчёт
    cur.execute('''INSERT OR IGNORE INTO ReportAtMonth (Date) VALUES (?)''', (year_month,))
    cur.execute('''SELECT ReportID FROM ReportAtMonth WHERE Date = ?''', (year_month,))
    report_id = cur.fetchone()[0]
    # Удаляем старые итоги
    cur.execute('''DELETE FROM TotalAtMonth WHERE ReportID = ?''', (report_id,))
    # Вставляем новые итоги
    for category_id, amount in category_totals:
        if amount != 0:
            cur.execute('''
                INSERT INTO TotalAtMonth (ReportID, CategoryID, SumMonth)
                VALUES (?, ?, ?)
            ''', (report_id, category_id, amount))
    conn.commit()
    conn.close()
    return get_report_data(year_month)

def update_monthly_report(year_month):
    # Обновляет существующий отчёт за указанный месяц 
    # Возвращает словарь с обновлёнными данными отчёта или None, если отчёт не существует
    # Проверяем, существует ли отчёт за этот месяц
    existing_report = get_report_data(year_month)
    if not existing_report:
        return None  # Отчёт не существует, обновление невозможно
    return generate_monthly_report(year_month)

def get_report_data(year_month):
    """Возвращает данные отчёта за месяц"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT
            ReportAtMonth.ReportID,
            ReportAtMonth.Date,
            Category.CategoryID,
            Category.CategoryName,
            Type.TypeName as TypeName,
            COALESCE(Obligation.ObligationName, '—') as ObligationName,
            TotalAtMonth.SumMonth
        FROM ReportAtMonth
        LEFT JOIN TotalAtMonth ON ReportAtMonth.ReportID = TotalAtMonth.ReportID
        LEFT JOIN Category ON TotalAtMonth.CategoryID = Category.CategoryID
        LEFT JOIN Type ON Category.TypeID = Type.TypeID
        LEFT JOIN Obligation ON Category.ObligationID = Obligation.ObligationID
        WHERE ReportAtMonth.Date = ?
    ''', (year_month,))
    rows = cur.fetchall()
    conn.close()
    if not rows or not rows[0][2]:  # если нет категорий
        return None
    result = {
        'report_id': rows[0][0],
        'year_month': rows[0][1],
        'categories': []
    }
    total_income = 0
    total_expense = 0
    for row in rows:
        if row[2]:  # если есть категория
            category = {
                'id': row[2],
                'name': row[3],
                'type': row[4],
                'obligation': row[5] if row[5] != '—' else None,
                'amount': row[6] if row[6] else 0
            }
            result['categories'].append(category)
            if row[4] == 'Доход':
                total_income += row[6] if row[6] else 0
            else:
                total_expense += row[6] if row[6] else 0
    result['total_income'] = total_income
    result['total_expense'] = total_expense
    result['balance'] = total_income - total_expense    
    return result

def get_available_months():
    """Возвращает список месяцев, для которых есть записи"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT DISTINCT strftime("%Y-%m", Date) as Month
        FROM Record
        ORDER BY Month DESC
    ''')
    months = [row[0] for row in cur.fetchall()]
    conn.close()
    return months