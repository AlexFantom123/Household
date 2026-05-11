from models.report import get_available_months, get_report_data, generate_monthly_report, update_monthly_report

def menu_reports(current_user):
    # Проверка: только администратор (RoleID = 1)
    if current_user.role_id != 1:
        print("\nДоступ запрещён! Только для администратора.")
        return  # Выход из функции, если не администратор
    while True:
        print("\n=== Отчёты по месяцам (Администратор) ===")
        print("1. Просмотреть отчёт за месяц")
        print("2. Сформировать отчёт за месяц")
        print("3. Обновить отчёт за месяц")
        print("4. Показать все доступные месяцы")
        print("5. Назад")
        choice = input("Выберите действие: ")

        if choice == "1":
            months = get_available_months()
            if not months:
                print("Нет записей для формирования отчётов.")
                continue
            print("\nДоступные месяцы с отчётами:")
            for i, m in enumerate(months, 1):
                # Проверяем, есть ли уже отчёт
                report_data = get_report_data(m)
                status = "Ok" if report_data else "Not"
                print(f"{i}. [{status}] {m}")
            try:
                idx = int(input("Выберите номер месяца: ")) - 1
                if 0 <= idx < len(months):
                    show_report(months[idx])
                else:
                    print("Неверный выбор.")
            except ValueError:
                print("Введите число.")

        elif choice == "2":
            # Показываем доступные месяцы с их статусами
            months = get_available_months()
            if not months:
                print("\nНет доступных месяцев для формирования отчёта.")
                continue
            print("\nДоступные месяцы:")
            for i, m in enumerate(months, 1):
                report_data = get_report_data(m)
                status = "Отчёт сформирован" if report_data else "Отчёт не сформирован"
                print(f"{i}. {m} [{status}]")
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
            # Показываем доступные месяцы с их статусами
            months = get_available_months()
            if not months:
                print("\nНет доступных месяцев для обновления отчёта.")
                continue
            print("\nДоступные месяцы:")
            for i, m in enumerate(months, 1):
                report_data = get_report_data(m)
                status = "Отчёт сформирован" if report_data else "Отчёт не сформирован"
                print(f"{i}. {m} [{status}]")
            try:
                idx = int(input("\nВыберите номер месяца для обновления отчёта: ")) - 1
                if 0 <= idx < len(months):
                    year_month = months[idx]
                    print(f"Обновление отчёта за {year_month}…")
                    # Обновляем существующий отчёт (не создаём новый)
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
            months = get_available_months()
            if not months:
                print("Нет записей.")
            else:
                print("\nМесяцы, в которых есть записи:")
                for m in months:
                    report_data = get_report_data(m)
                    status = "отчёт сформирован" if report_data else "отчёт не сформирован"
                    print(f"  - {m} ({status})")
            input("Нажмите Enter для выхода")

        elif choice == "5":
            break
        else:
            print("Неверный ввод.")

def show_report(year_month):
    """Отображает отчёт за месяц"""
    report = get_report_data(year_month)
    if not report:
        print(f"\nНет данных или отчёт не сформирован за {year_month}")
        return  # Выход, если нет данных
    print(f"\n{'='*55}")
    print(f" ОТЧЁТ ПО ДОХОДАМ И РАСХОДАМ ЗА {report['year_month']} ")
    print(f"{'='*55}")
    # Доходы
    print("\nДОХОДЫ:")
    income_cats = [c for c in report['categories'] if c['type'] == 'Доход']
    if income_cats:
        for cat in income_cats:
            print(f"    {cat['name']:28} {cat['amount']:12.2f} руб.")
        print(f"{'ИТОГО ДОХОДОВ':28} {report['total_income']:16.2f} руб.")
    else:
        print(" Нет доходов за этот период ")
    # Расходы (с группировкой по обязательности)
    print("\nРАСХОДЫ:")
    expense_cats = [c for c in report['categories'] if c['type'] == 'Расход']
    if expense_cats:
        mandatory = [c for c in expense_cats if c.get('obligation') == 'Обязательная']
        optional = [c for c in expense_cats if c.get('obligation') == 'Необязательная']
        total_expense = report['total_expense']
        # Обязательные расходы
        if mandatory:
            print(" Обязательные расходы: ")
            for cat in mandatory:
                print(f"    {cat['name']:26} {cat['amount']:12.2f} руб.")
        # Необязательные расходы
        if optional:
            print(" Необязательные расходы: ")
            for cat in optional:
                print(f"    {cat['name']:26} {cat['amount']:12.2f} руб.")
        print(f"{'ИТОГО РАСХОДОВ':28} {total_expense:14.2f} руб. ")
        # Доля обязательных и необязательных расходов
        if total_expense > 0:
            mandatory_sum = sum(c['amount'] for c in mandatory)
            optional_sum = sum(c['amount'] for c in optional)
            if mandatory_sum > 0:
                mandatory_percent = mandatory_sum / total_expense * 100
                print(f"  (обязательные: {mandatory_percent:.1f}%) ")
            if optional_sum > 0:
                optional_percent = optional_sum / total_expense * 100
                print(f"  (необязательные: {optional_percent:.1f}%) ")
    else:
        print("Нет расходов за этот период")
    # Баланс
    print(f"\n{'='*55}")
    balance = report['balance']
    if balance >= 0:
        print(f"ЧИСТЫЙ БАЛАНС: {balance:26.2f} руб.")
        print(f"(доходы превышают расходы на {balance:.2f} руб.) ")
    else:
        print(f"ЧИСТЫЙ БАЛАНС: {balance:26.2f} руб.")
        print(f"(расходы превышают доходы на {abs(balance):.2f} руб.)")
    # Совет
    if balance < 0:
        optional_cats = [c for c in expense_cats if c.get('obligation') == 'Необязательная'] if expense_cats else []
        optional_sum = sum(c['amount'] for c in optional_cats)
        if optional_sum > 0:
            print(f"\nСовет: сократите необязательные расходы ({optional_sum:.2f} руб.)")
    print(f"{'='*55}")
    input("Нажмите Enter для выхода")