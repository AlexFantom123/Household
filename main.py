from database.db_manager import initialize_db
from ui.menu import show_main_menu
from ui.menu_categories import menu_categories
from ui.menu_records import menu_records
from ui.menu_reports import menu_reports
from ui.menu_users import menu_users
from models.user import authenticate, is_admin_exists

def main():
    initialize_db()
    # Проверка: если нет администратора, предложить создать
    if not is_admin_exists():
        print("\n=== ПЕРВЫЙ ЗАПУСК ===")
        print("Администратор не найден. Создайте учётную запись администратора.\n")
        from models.user import User
        login = input("Логин администратора: ")
        password = input("Пароль: ")
        name = input("Имя: ")
        admin = User(role_id=1, login=login, password=password, name=name)
        admin.save()
        print("\nАдминистратор создан!")
        current_user = admin
    else:
        # Обычная авторизация
        print("\n=== ИС учёта доходов и расходов домохозяйства ===\n")
        login = input("Логин: ")
        password = input("Пароль: ")
        current_user = authenticate(login, password)
        if not current_user:
            print("\nОШИБКА: Неверный логин или пароль!")
            return  # Завершаем работу при неудачной авторизации
    print(f"\nДобро пожаловать, {current_user.name}!")
    while True:
        choice = show_main_menu(current_user)
        if choice == "1":
            menu_categories()
        elif choice == "2":
            menu_records(current_user)
        elif choice == "3":
            if current_user.role_id == 1:
                menu_reports(current_user)
            else:
                print("\nДоступ запрещён!")
        elif choice == "4":
            if current_user.role_id == 1:
                menu_users()
            else:
                print("\nДоступ запрещён!")
        elif choice == "5":
            print("\nВыход из программы. До свидания!")
            break
        else:
            print("\nНеверный ввод.")
if __name__ == "__main__":
    main()