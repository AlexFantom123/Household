from models.record import Record, get_all_records
from models.category import get_all_categories, get_categories_by_type
from models.balance import get_balance, update_balance
from datetime import datetime

def get_category_name(category_id):
    for c in get_all_categories():
        if c.id == category_id:
            return c.name
    return "Неизвестно"

def menu_records(current_user):
    while True:
        # Получаем актуальный баланс перед отображением меню
        current_balance = get_balance(current_user.id)
        print("\n=== Управление записями ===")
        if isinstance(current_balance, tuple):
            current_balance = current_balance[0] if current_balance else 0
        print(f"Текущий баланс: {float(current_balance):.2f} руб.")
        if current_balance >= 0:
            print("Статус: Профицит (доходы > расходы)")
        else:
            print("Статус: Дефицит (расходы > доходы)")
        print("1. Показать все записи")
        print("2. Добавить запись")
        print("3. Удалить запись")
        print("4. Редактировать запись")
        print("5. Назад")

        choice = input("Выберите действие: ")

        if choice == "1":
            records = get_all_records(current_user.id)
            if not records:
                print("Записи не найдены.")
            else:
                sorted_records = sorted(records, key=lambda r: r.id)
                print("\nСписок записей (отсортировано по ID):")
                for r in sorted_records:
                    cat_name = get_category_name(r.category_id)
                    print(f"{r.id}. {r.date} | {cat_name} | {float(r.sum):.2f} руб.")
            input("Нажмите Enter для продолжения...")

        elif choice == "2":
            print("\n=== Добавление записи ===")
            print("\n1. Доход\n2. Расход")
            type_choice = input("Выберите тип (1 или 2): ")
            if type_choice == "1":
                categories = get_categories_by_type(1)
                type_name = "Доход"
            elif type_choice == "2":
                categories = get_categories_by_type(2)
                type_name = "Расход"
            else:
                print("Неверный выбор типа. Попробуйте снова.")
                continue
            if not categories:
                print(f"Нет категорий для {type_name}. Создайте их в меню категорий.")
                continue
            print(f"\nКатегории ({type_name}):")
            for c in categories:
                print(f"{c.id}. {c.name}")
            try:
                category_id = int(input("ID категории: "))
                sum_val = float(input("Сумма: "))
                # Валидация: сумма должна быть положительной
                if sum_val <= 0:
                    print("Сумма должна быть больше нуля.")
                    continue
            except ValueError:
                print("Ошибка: введите корректные числовые значения.")
                continue
            date_input = input("Дата (ГГГГ-ММ-ДД, Enter – сегодня): ")
            if date_input:
                try:
                    datetime.strptime(date_input, "%Y-%m-%d")
                    date = date_input
                except ValueError:
                    print("Некорректный формат даты. Используется текущая дата.")
                    date = datetime.now().strftime("%Y-%m-%d")
            else:
                date = datetime.now().strftime("%Y-%m-%d")
            record = Record(user_id=current_user.id, category_id=category_id, date=date, sum=sum_val)
            record.save()
            print("Запись добавлена.")
            # Обновляем баланс с передачей user_id и даты записи
            try:
                update_balance(current_user.id, date)
                print("Баланс обновлён.")
            except Exception as e:
                print(f"Ошибка при обновлении баланса: {e}")

        elif choice == "3":
            try:
                record_id = int(input("ID записи для удаления: "))
                # Валидация: ID должен быть положительным
                if record_id <= 0:
                    print("ID должен быть положительным числом.")
                    continue
            except ValueError:
                print("Ошибка: введите корректный ID.")
                continue
            # Получаем дату записи перед удалением для корректного пересчёта баланса
            records = get_all_records(current_user.id)
            target_record = next((r for r in records if r.id == record_id), None)
            if target_record:
                target_date = target_record.date
            else:
                target_date = datetime.now().strftime("%Y-%m-%d")
            record = Record(id=record_id)
            record.delete()
            print("Запись удалена.")
            # Обновляем баланс с user_id и датой удалённой записи
            try:
                update_balance(current_user.id, target_date)
                print("Баланс обновлён.")
            except Exception as e:
                print(f"Ошибка при обновлении баланса: {e}")

        elif choice == "4":
            try:
                record_id = int(input("ID записи для редактирования: "))
                # Валидация: ID должен быть положительным
                if record_id <= 0:
                    print("ID должен быть положительным числом.")
                    continue
            except ValueError:
                print("Ошибка: введите корректный ID.")
                continue
            records = get_all_records(current_user.id)
            current = next((r for r in records if r.id == record_id), None)
            if not current:
                print("Запись не найдена!")
                continue
            print(f"Текущая сумма: {current.sum}")
            sum_input = input("Новая сумма (Enter – без изменений): ")
            print(f"Текущая дата: {current.date}")
            date_input = input("Новая дата (ГГГГ-ММ-ДД, Enter – без изменений): ")

            # Обработка изменений суммы
            if sum_input:
                try:
                    new_sum = float(sum_input)
                    if new_sum <= 0:
                        print("Сумма должна быть больше нуля.")
                        continue
                except ValueError:
                    print("Ошибка: сумма должна быть числом.")
                    continue
            else:
                new_sum = current.sum
            # Обработка изменений даты
            if date_input:
                try:
                    datetime.strptime(date_input, "%Y-%m-%d")
                    new_date = date_input
                except ValueError:
                    print("Некорректный формат даты. Сохраняется старая дата.")
                    new_date = current.date
            else:
                new_date = current.date
            record = Record(
                id=record_id,
                user_id=current.user_id,
                category_id=current.category_id,
                date=new_date,
                sum=new_sum
            )
            record.save()
            print("Запись обновлена.")
            # Обновляем баланс только если дата изменилась или сумма повлияла на общий баланс
            dates_to_update = set()
            if new_date != current.date:
                dates_to_update.add(new_date)
                dates_to_update.add(current.date)  # Старая дата тоже может измениться
            else:
                # Если дата не изменилась, обновляем баланс за текущую дату (на всякий случай)
                dates_to_update.add(datetime.now().strftime("%Y-%m-%d"))
            # Обновляем баланс для всех затронутых дат
            for date_to_update in dates_to_update:
                try:
                    update_balance(current_user.id, date_to_update)
                    print(f"Баланс обновлён для даты: {date_to_update}")
                except Exception as e:
                    print(f"Ошибка при обновлении баланса для даты {date_to_update}: {e}")
        elif choice == "5":
            break
        else:
            print("Неверный выбор. Попробуйте снова.")
