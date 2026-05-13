from models.report import get_available_months, get_report_data, generate_monthly_report, update_monthly_report
from database.db_manager import get_connection

def menu_reports(current_user):
    while True:
        print("\n=== Отчёты по месяцам ===")
        print("1. Просмотреть отчёт за месяц")
        print("2. Сформировать отчёт за месяц")
        print("3. Обновить отчёт за месяц")
        print("4. Показать все доступные месяцы")
        print("5. Назад")
        choice = input("Выберите действие: ")

        if choice == "1":
            if current_user.role_id == 1:
                months = get_available_months()
            else:
                months = get_available_months(user_id=current_user.id)
            if not months:
                print("Нет записей для формирования отчётов.")
                continue
            print("\nДоступные месяцы с отчётами:")
            month_statuses = []
            for m in months:
                report_data = get_report_data(m, user_id=None if current_user.role_id == 1 else current_user.id)
                status = "Ok" if report_data else "Not"
                month_statuses.append((m, status))
                print(f"{len(month_statuses)}. [{status}] {m}")
            try:
                idx = int(input("Выберите номер месяца: ")) - 1
                if 0 <= idx < len(months):
                    selected_month, status = month_statuses[idx]
                    if status == "Ok":
                        show_report(selected_month, user_id=None if current_user.role_id == 1 else current_user.id)
                    else:
                        print("Отчёт за этот месяц не сформирован.")
                else:
                    print("Неверный выбор.")
            except ValueError:
                print("Введите число.")

        elif choice == "2":
            if current_user.role_id != 1:
                print("\nДоступ запрещён! Только для администратора.")
                continue
            months = get_available_months()
            if not months:
                print("\nНет доступных месяцев для формирования отчёта.")
                continue
            display_month_statuses(months)
            try:
                idx = int(input("\nВыберите номер месяца для формирования отчёта: ")) - 1
                if 0 <= idx < len(months):
                    year_month = months[idx]
                    print(f"Формирование отчёта за {year_month}…")
                    report = generate_monthly_report(year_month)
                    if report:
                        print("Отчёт успешно сформирован!")
                        show_report(year_month)
                    else:
                        print("Нет данных для этого месяца.")
                else:
                    print("Неверный выбор.")
            except ValueError:
                print("Введите число.")

        elif choice == "3":
            if current_user.role_id != 1:
                print("\nДоступ запрещён! Только для администратора.")
                continue
            months = get_available_months()
            if not months:
                print("\nНет доступных месяцев для обновления отчёта.")
                continue
            display_month_statuses(months)
            try:
                idx = int(input("\nВыберите номер месяца для обновления отчёта: ")) - 1
                if 0 <= idx < len(months):
                    year_month = months[idx]
                    print(f"Обновление отчёта за {year_month}")
                    updated_report = update_monthly_report(year_month)
                    if updated_report:
                        print("Отчёт успешно обновлён!")
                        show_report(year_month)
                    else:
                        print("Не удалось обновить отчёт. Возможно, отчёт не существует или нет данных.")
                else:
                    print("Неверный выбор.")
            except ValueError:
                print("Введите число.")

        elif choice == "4":
            if current_user.role_id != 1:
                print("\nДоступ запрещён! Только для администратора.")
                continue
            months = get_available_months()
            if not months:
                print("\nВ системе нет доступных месяцев.")
            else:
                print("\nМесяцы, в которых есть записи (все пользователи):")
                for m in months:
                    report_data = get_report_data(m)
                    status = "отчёт сформирован" if report_data else "отчёт не сформирован"
                    print(f"  - {m} ({status})")
                input("Нажмите Enter для выхода")

        elif choice == "5":
            break
        else:
            print("Неверный ввод.")

def display_month_statuses(months):
    # Вспомогательная функция для отображения месяцев с их статусами
    print("\nДоступные месяцы:")
    for i, m in enumerate(months, 1):
        report_data = get_report_data(m)
        status = "Отчёт сформирован" if report_data else "Отчёт не сформирован"
        print(f"{i}. {m} [{status}]")

def show_report(year_month, user_id=None):
    # Отображает отчёт за указанный месяц в структурированном виде.
    # Получаем данные отчёта (список категорий)
    report_data = get_report_data(year_month, user_id=user_id)
    if not report_data:
        print(f"\nНет данных или отчёт не сформирован за {year_month}")
        return
    # Получаем детальные записи с датами
    conn = get_connection()
    cur = conn.cursor()
    # Запрос для доходов с датами
    if user_id is not None:
        cur.execute('''
            SELECT Record.Date, Record.Sum, Category.CategoryName
            FROM Record
            JOIN Category ON Record.CategoryID = Category.CategoryID
            WHERE strftime('%Y-%m', Record.Date) = ?
            AND Category.TypeID = 1
            AND Record.UserID = ?
            ORDER BY Record.Date
        ''', (year_month, user_id))
    else:
        cur.execute('''
            SELECT Record.Date, Record.Sum, Category.CategoryName
            FROM Record
            JOIN Category ON Record.CategoryID = Category.CategoryID
            WHERE strftime('%Y-%m', Record.Date) = ?
            AND Category.TypeID = 1
            ORDER BY Record.Date
        ''', (year_month,))
    income_records = cur.fetchall()
    # Запрос для расходов с датами
    if user_id is not None:
        cur.execute('''
            SELECT Record.Date, Record.Sum, Category.CategoryName, 
                   COALESCE(Obligation.ObligationName, '—')
            FROM Record
            JOIN Category ON Record.CategoryID = Category.CategoryID
            LEFT JOIN Obligation ON Category.ObligationID = Obligation.ObligationID
            WHERE strftime('%Y-%m', Record.Date) = ?
            AND Category.TypeID = 2
            AND Record.UserID = ?
            ORDER BY Record.Date
        ''', (year_month, user_id))
    else:
        cur.execute('''
            SELECT Record.Date, Record.Sum, Category.CategoryName,
                   COALESCE(Obligation.ObligationName, '—')
            FROM Record
            JOIN Category ON Record.CategoryID = Category.CategoryID
            LEFT JOIN Obligation ON Category.ObligationID = Obligation.ObligationID
            WHERE strftime('%Y-%m', Record.Date) = ?
            AND Category.TypeID = 2
            ORDER BY Record.Date
        ''', (year_month,))
    expense_records = cur.fetchall()
    conn.close()
    # Подсчёт итогов (преобразуем сумму в float)
    total_income = 0.0
    for r in income_records:
        try:
            total_income += float(r[1])
        except (ValueError, TypeError):
            total_income += 0.0
    total_expense = 0.0
    for r in expense_records:
        try:
            total_expense += float(r[1])
        except (ValueError, TypeError):
            total_expense += 0.0
    # Заголовок
    print(f"\n{'='*65}")
    print(f" ОТЧЁТ ЗА {year_month}")
    print(f"{'='*65}")
    # Доходы
    print("\nДОХОДЫ:")
    if income_records:
        for date, amount, name in income_records:
            try:
                amount_float = float(amount)
            except (ValueError, TypeError):
                amount_float = 0.0
            day = str(date).split('-')[2] if date else '??'
            month_num = year_month.split('-')[1]
            print(f"  {day}.{month_num}: {name:25} {amount_float:10.2f} руб.")
        print(f"  {'Итого доходов':39} {total_income:10.2f} руб.")
    else:
        print("  Нет доходов")
    # Расходы
    print("\nРАСХОДЫ:")
    if expense_records:
        mandatory_total = 0.0
        optional_total = 0.0
        for record in expense_records:
            if len(record) == 4:
                date, amount, name, obligation = record
            else:
                date, amount, name = record[:3]
                obligation = record[3] if len(record) > 3 else '—'
            try:
                amount_float = float(amount)
            except (ValueError, TypeError):
                amount_float = 0.0
            day = str(date).split('-')[2] if date else '??'
            month_num = year_month.split('-')[1]
            print(f"  {day}.{month_num}: {name:25} {amount_float:10.2f} руб. ({obligation})")
            
            if obligation == 'Обязательная':
                mandatory_total += amount_float
            elif obligation == 'Необязательная':
                optional_total += amount_float
        print(f"  {'Итого расходов':39} {total_expense:10.2f} руб.")
        if mandatory_total > 0:
            print(f"    Обязательные: {mandatory_total:10.2f} руб.")
        if optional_total > 0:
            print(f"    Необязательные: {optional_total:10.2f} руб.")
    else:
        print("  Нет расходов")
    # Баланс
    print(f"\n{'='*65}")
    balance = total_income - total_expense
    if balance >= 0:
        print(f" БАЛАНС: {balance:10.2f} руб. (доходы превышают расходы)")
    else:
        print(f" БАЛАНС: {balance:10.2f} руб. (расходы превышают доходы)")
    # Совет при отрицательном балансе
    if balance < 0 and expense_records:
        optional_total = 0.0
        for record in expense_records:
            obligation = record[3] if len(record) > 3 else '—'
            if obligation == 'Необязательная':
                try:
                    optional_total += float(record[1])
                except (ValueError, TypeError):
                    pass
        if optional_total > 0:
            print(f"\n Совет: сократите необязательные расходы ({optional_total:.2f} руб.)")
    print(f"{'='*65}")
    input("\nНажмите Enter для выхода")