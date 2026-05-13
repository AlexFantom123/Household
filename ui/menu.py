def show_main_menu(current_user):
    print(f"\n{'='*57}")
    print(f" ИС учёта доходов и расходов домохозяйства – Главное меню")
    print(f" Пользователь: {current_user.name}")
    if current_user.role_id == 1:
        print(f" Статус: АДМИНИСТРАТОР")
    else:
        print(f" Статус: Член домохозяйства")
    print(f"{'='*57}")
    print("1. Управление категориями")
    print("2. Управление записями (доходы/расходы)")
    print("3. Отчёты по месяцам")
    if current_user.role_id == 1:
        print("4. Управление пользователями (Админ)")
    print("5. Выход")
    return input("\nВыберите действие: ")