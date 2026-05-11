from models.category import Category, get_all_categories
from models.type import get_all_types
from models.obligation import get_all_obligations

def menu_categories():
    while True:
        print("\n=== Управление категориями ===")
        print("1. Показать все категории")
        print("2. Добавить категорию")
        print("3. Удалить категорию")
        print("4. Редактировать категорию")
        print("5. Назад")

        choice = input("Выберите действие: ")

        if choice == "1":
            categories = get_all_categories()
            if not categories:
                print("Категории не найдены.")
            else:
                print("\nСписок категорий:")
                for c in categories:
                    type_name = get_type_name(c.type_id)
                    if c.type_id == 1:  # Доход
                        obligation_display = "—"
                    else:
                        obligation_display = get_obligation_name(c.obligation_id) if c.obligation_id else "Не указана"
                    print(f"{c.id}. {c.name} | Тип: {type_name} | Обязательность: {obligation_display}")
            input("Нажмите Enter для выхода")

        elif choice == "2":
            print("\n=== Добавление категории ===")
            name = input("Название: ")
            print("\nТипы:")
            for t in get_all_types():
                print(f"{t.id}. {t.name}")
            try:
                type_id = int(input("ID типа (1-Доход, 2-Расход): "))
                obligation_id = None
                if type_id == 2:  # Только для расходов
                    print("\nОбязательность (только для расходов):")
                    for o in get_all_obligations():
                        print(f"{o.id}. {o.name}")
                    obligation_id_input = input("ID обязательности (1-Обязательная, 2-Необязательная): ")
                    if obligation_id_input:
                        obligation_id = int(obligation_id_input)
                else:
                    print("Для доходов обязательность не указывается.")
                cat = Category(name=name, type_id=type_id, obligation_id=obligation_id)
                cat.save()
                print("Категория добавлена.")
            except ValueError:
                print("\nОШИБКА: Введите корректный ID (число).")
            except Exception as e:
                print(f"\nОШИБКА при добавлении категории: {e}")

        elif choice == "3":
            try:
                cat_id = int(input("ID категории для удаления: "))
                cat = Category(id=cat_id)
                cat.delete()
                print("Категория удалена.")
            except ValueError:
                print("\nОШИБКА: Введите корректный ID категории (число).")
            except Exception as e:
                print(f"\nОШИБКА при удалении категории: {e}")

        elif choice == "4":
            try:
                cat_id = int(input("ID категории для редактирования: "))
                categories = get_all_categories()
                current = next((c for c in categories if c.id == cat_id), None)
                if not current:
                    print("Категория не найдена!")
                    continue

                print(f"Текущее название: {current.name}")
                name = input("Новое название (Enter - без изменений): ")
                print(f"Текущий тип ID: {current.type_id}")
                type_id_input = input("Новый тип ID (Enter - без изменений): ")

                new_type_id = int(type_id_input) if type_id_input else current.type_id

                obligation_id = current.obligation_id
                if new_type_id == 2:  # Расход
                    print(f"Текущая обязательность: {get_obligation_name(current.obligation_id) if current.obligation_id else 'Не указана'}")
                    oblig_input = input("Новый ID обязательности (1-Обязательная, 2-Необязательная, Enter - без изменений): ")
                    if oblig_input:
                        obligation_id = int(oblig_input)
                else:  # Доход
                    obligation_id = None
                    if type_id_input:
                        print("Для доходов обязательность не указывается (будет сброшена).")
                cat = Category(
                    id=cat_id,
                    name=name if name else current.name,
                    type_id=new_type_id,
                    obligation_id=obligation_id
                )
                cat.save()
                print("Категория обновлена.")
            except ValueError:
                print("\nОШИБКА: Введите корректный числовой ID.")
            except Exception as e:
                print(f"\nОШИБКА при редактировании категории: {e}")

        elif choice == "5":
            break

def get_type_name(type_id):
    for t in get_all_types():
        if t.id == type_id:
            return t.name
    return "Неизвестно"

def get_obligation_name(obligation_id):
    if obligation_id is None:
        return "—"
    for o in get_all_obligations():
        if o.id == obligation_id:
            return o.name
    return "Неизвестно"