import sqlite3
# импорт имени файла базы данных из конфигурационного файла
from config import DB_NAME
def get_connection():
    return sqlite3.connect(DB_NAME)
# Функция инициализации базы данных: создаёт все таблицы, если они ещё не существуют
def initialize_db():
    # Устанавливаем соединение с базой
    conn = get_connection()
    # Получаем объект курсора для выполнения SQL-запросов
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Role (RoleID INTEGER PRIMARY KEY,
                RoleName TEXT NOT NULL)''')
    cur.execute('''CREATE TABLE  IF NOT EXISTS User (UserID INTEGER PRIMARY KEY,
                RoleID INTEGER NOT NULL,
                Login TEXT UNIQUE NOT NULL,
                Password TEXT NOT NULL,
                UserName TEXT,
                FOREIGN KEY (RoleID) REFERENCES Role(RoleID))''')
    cur.execute('''CREATE TABLE IF NOT EXISTS Type(TypeID INTEGER PRIMARY KEY,
                TypeName TEXT NOT NULL)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS Obligation(ObligationID INTEGER PRIMARY KEY,
                ObligationName TEXT NULL)''')
    cur.execute('''CREATE TABLE  IF NOT EXISTS Category(CategoryID INTEGER PRIMARY KEY,
                CategoryName TEXT NOT NULL,
                TypeID INTEGER NOT NULL,
                ObligationID INTEGER,
                FOREIGN KEY (TypeID) REFERENCES Type(TypeID),
                FOREIGN KEY (ObligationID) REFERENCES Obligation(ObligationID))''')
    cur.execute('''CREATE TABLE IF NOT EXISTS Record(RecordID INTEGER PRIMARY KEY,
                UserID INTEGER NOT NULL,
                CategoryID TEXT INTEGER NOT NULL,
                Date TEXT NOT NULL,
                Sum REAL TEXT,
                FOREIGN KEY (UserID) REFERENCES User(UserID)
                FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID))''')
    cur.execute('''CREATE TABLE IF NOT EXISTS Balance(BalanceID INTEGER PRIMARY KEY,
                UserID INTEGER,
                Date TEXT NOT NULL UNIQUE,
                SumBalance REAL NOT NULL,
                UNIQUE (UserID, Date))''')
    cur.execute('''CREATE TABLE IF NOT EXISTS ReportAtMonth(ReportID INTEGER PRIMARY KEY,
                Date TEXT NOT NULL)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS TotalAtMonth(TotalID INTEGER PRIMARY KEY,
                ReportID INTEGER NOT NULL,
                CategoryID INTEGER NOT NULL,
                SumMonth REAL NOT NULL,
                FOREIGN KEY (ReportID) REFERENCES ReportAtMonth(ReportID),
                FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID))''')
    cur.executemany('''INSERT OR IGNORE INTO Role 
                    VALUES (?, ?)''',
                    [(1, "Админ"), (2, "Пользователь")])
    cur.executemany('''INSERT OR IGNORE INTO Type 
                    VALUES (?, ?)''',
                    [(1, "Доход"), (2, "Расход")])
    cur.executemany('''INSERT OR IGNORE INTO Obligation 
                    VALUES (?, ?)''',
                    [(1, "Обязательная"), (2, "Необязательная")])
    cur.executemany('''INSERT OR IGNORE INTO Category (CategoryID, CategoryName, TypeID, ObligationID) 
                    VALUES (?, ?, ?, ?)''', 
                    [# Доходы (ObligationID = NULL)
                        (1, 'Зарплата', 1, None),
                        (2, 'Фриланс', 1, None),
                        (3, 'Подарки', 1, None),
                        (4, 'Инвестиции', 1, None),
                        (5, 'Кэшбэк', 1, None),
                    # Расходы обязательные
                        (6, 'Продукты', 2, 1),
                        (7, 'Коммунальные платежи', 2, 1),
                        (8, 'Кредит/Ипотека', 2, 1),
                        (9, 'Интернет/Связь', 2, 1),
                        (10, 'Транспорт (проездной)', 2, 1),
                    # Расходы необязательные
                        (11, 'Кафе и рестораны', 2, 2),
                        (12, 'Развлечения', 2, 2),
                        (13, 'Шопинг', 2, 2),
                        (14, 'Такси', 2, 2),
                        (15, 'Хобби', 2, 2),
                        (16, 'Путешествия', 2, 2)])
    cur.executemany('''INSERT OR IGNORE INTO Record (RecordID, UserID, CategoryID, Date, Sum) 
                    VALUES (?, ?, ?, ?, ?)''', 
                    [
                        # Администратор (UserID=1) — доходы
                        (1, 1, 1, '2025-05-01', 80000.00),
                        (2, 1, 2, '2025-05-10', 15000.00),
                        (3, 1, 3, '2025-05-15', 5000.00),
                        (4, 1, 4, '2025-05-20', 3000.00),
                        (5, 1, 5, '2025-05-25', 1200.00),
                        # Администратор — расходы обязательные
                        (6, 1, 6, '2025-05-02', 5600.00),
                        (7, 1, 7, '2025-05-03', 4500.00),
                        (8, 1, 8, '2025-05-05', 12000.00),
                        (9, 1, 9, '2025-05-06', 1200.00),
                        (10, 1, 10, '2025-05-07', 2500.00),
                        # Администратор — расходы необязательные
                        (11, 1, 11, '2025-05-08', 3200.00),
                        (12, 1, 12, '2025-05-12', 2100.00),
                        (13, 1, 13, '2025-05-18', 4500.00),
                        (14, 1, 14, '2025-05-22', 800.00),
                        (15, 1, 15, '2025-05-26', 1500.00),
                        (16, 1, 16, '2025-05-30', 10000.00),
                        # Дополнительные записи
                        (17, 1, 1, '2025-04-01', 78000.00),
                        (18, 1, 6, '2025-04-02', 5200.00),
                        (19, 1, 7, '2025-04-03', 4300.00),
                        (20, 1, 11, '2025-04-08', 2900.00),
                        (21, 1, 1, '2025-03-01', 85000.00), 
                        (22, 1, 6, '2025-03-02', 5800.00), 
                        (23, 1, 2, '2025-03-03', 62000.00), 
                        (24, 1, 7, '2025-03-04', 4700.00),
                        (25, 1, 11, '2025-03-01', 8500.00), 
                        (26, 1, 6, '2025-03-02', 8000.00), 
                        (27, 1, 15, '2025-03-03', 2000.00), 
                        (28, 1, 16, '2025-03-04', 7000.00)])
    cur.executemany('''INSERT OR IGNORE INTO TotalAtMonth (TotalID, ReportID, CategoryID, SumMonth) 
                    VALUES (?, ?, ?, ?)''',
                    [
                        # (ReportID=1)
                        (1, 1, 1, 78000.00),
                        (2, 1, 1, 58000.00),
                        (3, 1, 1, 44000.00),
                        (4, 1, 6, 5200.00),
                        (5, 1, 6, 3900.00),
                        (6, 1, 6, 3600.00),
                        (7, 1, 7, 4300.00),
                        (8, 1, 11, 2900.00),
                        # (ReportID=2) — доходы
                        (9, 2, 1, 185000.00),
                        (10, 2, 2, 20000.00),
                        (11, 2, 3, 8000.00),
                        (12, 2, 4, 3000.00),
                        (13, 2, 5, 1700.00),
                        # (ReportID=2) — расходы
                        (14, 2, 6, 13600.00),
                        (15, 2, 7, 8000.00),
                        (16, 2, 8, 17000.00),
                        (17, 2, 9, 1200.00),
                        (18, 2, 10, 4300.00),
                        (19, 2, 11, 5950.00),
                        (20, 2, 12, 3300.00),
                        (21, 2, 13, 6800.00),
                        (22, 2, 14, 1450.00),
                        (23, 2, 15, 2700.00),
                        (24, 2, 16, 10000.00)])
    conn.commit()
    conn.close()