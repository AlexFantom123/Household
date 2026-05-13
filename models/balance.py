from database.db_manager import get_connection
from datetime import datetime

def get_balance(user_id, as_of_date=None):
    # Получает баланс пользователя на указанную дату (или текущую).
    conn = get_connection()
    cur = conn.cursor()
    query = '''
        SELECT COALESCE(SUM(
            CASE WHEN Type.TypeName = 'Доход' THEN Record.Sum ELSE -Record.Sum END
        ), 0)
        FROM Record
        JOIN Category ON Record.CategoryID = Category.CategoryID
        JOIN Type ON Category.TypeID = Type.TypeID
        WHERE Record.UserID = ?
    '''
    params = [user_id]
    if as_of_date is not None:
        query += " AND Record.Date <= ?"
        params.append(as_of_date)
    try:
        cur.execute(query, params)
        result = cur.fetchone()
        if result is None or result[0] is None:
            return 0.0
        return float(result[0])
    except Exception as e:
        print(f"Ошибка при получении баланса: {e}")
        raise
    finally:
        conn.close()

def update_balance(user_id, date):
    # Обновляет баланс пользователя в таблице Balance на указанную дату.
    # Использует INSERT OR REPLACE (UPSERT-операция).
    # Преобразуем входную дату в формат YYYY-MM-DD
    if isinstance(date, str):
        date = datetime.strptime(date.strip(), '%Y-%m-%d')
    elif isinstance(date, int):
        date_str = str(date).zfill(8)
        date = datetime.strptime(date_str, '%Y%m%d')
    elif hasattr(date, 'strftime'):
        pass
    else:
        raise ValueError(f"Неподдерживаемый тип даты: {type(date)}")
    date_str = date.strftime('%Y-%m-%d')
    try:
        conn = get_connection()
        with conn:
            cur = conn.cursor()
            balance = get_balance(user_id, as_of_date=date_str)
            # Используем INSERT OR REPLACE вместо проверки и отдельных INSERT/UPDATE
            cur.execute(
                'INSERT OR REPLACE INTO Balance (UserID, Date, SumBalance) '
                'VALUES (?, ?, ?)',
                (user_id, date_str, balance)
            )
        return balance
    except Exception as e:
        print(f"Ошибка при обновлении баланса: {e}")
        raise