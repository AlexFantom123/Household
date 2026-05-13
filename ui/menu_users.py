from models.user import User, get_all_users, is_admin_exists
from models.role import get_all_roles

def menu_users():
    while True:
        print("\n=== Управление пользователями ===")
        print("1. Показать всех пользователей")
        print("2. Добавить пользователя")
        print("3. Удалить пользователя")
        print("4. Назад")

        choice = input("Выберите действие: ")

        if choice == "1":
            users = get_all_users()
            if not users:
                print("Нет пользователей.")
            else:
                print("\nСписок пользователей:")
                for u in users:
                    role_name = get_role_name(u.role_id)
                    admin_mark = "(АДМИН)" if u.role_id == 1 else ""
                    print(f"{u.id}. {u.name} {admin_mark} | Логин: {u.login} | Роль: {role_name}")
            input("Нажмите Enter для выхода")
        elif choice == "2":
            # Добавление пользователя
            print("\n=== Добавление пользователя ===")
            print("\nРоли:")
            for r in get_all_roles():
                print(f"{r.id}. {r.name}")
            try:
                role_id = int(input("ID роли (1-Админ, 2-Пользователь): "))
                # Проверка: если выбран админ (ID 1), но админ уже есть — автоматически меняем роль на пользователя (ID 2)
                if role_id == 1 and is_admin_exists():
                    print("\nВНИМАНИЕ: Администратор уже существует! Автоматически присваивается роль 'Пользователь'.")
                    role_id = 2
                # Теперь запрашиваем остальные данные
                login = input("Логин: ")
                password = input("Пароль: ")
                name = input("Имя: ")
                # Создаём пользователя с (возможно, изменённой) ролью
                user = User(role_id=role_id, login=login, password=password, name=name)
                user.save()
                # Сообщаем пользователю, с какой ролью он был создан
                final_role_name = "Администратор" if role_id == 1 else "Пользователь"
                print(f"Пользователь добавлен с ролью: {final_role_name}.")
            except ValueError:
                print("\nОШИБКА: Введите корректный ID роли (число).")
            except Exception as e:
                print(f"\nОШИБКА: {e}")

        elif choice == "3":
            try:
                user_id = int(input("ID пользователя для удаления: "))
                user = User(id=user_id)
                user.delete()
                print("Пользователь удалён.")
            except ValueError:
                print("\nОШИБКА: Введите корректный ID пользователя (число).")
            except Exception as e:
                print(f"\nОШИБКА: {e}")
        elif choice == "4":
            break

def get_role_name(role_id):
    for r in get_all_roles():
        if r.id == role_id:
            return r.name
    return "Неизвестно"