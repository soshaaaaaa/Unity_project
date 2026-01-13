import sqlite3

DB_NAME = r"D:\pythonvs\KKurs.db"  # Путь к базе данных

# --- Вспомогательные функции ---

def get_connection():
    """Подключается к базе данных."""
    return sqlite3.connect(DB_NAME)

def is_leap_year(year):
    """Проверяет, является ли год високосным."""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def validate_date(date_str):
    """Проверяет формат даты ГГГГ-ММ-ДД, год ≤ 2025, месяц ≤ 12, день ≤ 31 с учётом високосного года."""
    if not date_str:
        return None
    # Проверка формата ГГГГ-ММ-ДД
    parts = date_str.split('-')
    if len(parts) != 3 or len(parts[0]) != 4 or len(parts[1]) != 2 or len(parts[2]) != 2:
        print("Ошибка: дата должна быть ГГГГ-ММ-ДД (например, 2023-05-15).")
        return None
    try:
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
        if year > 2025:
            print("Ошибка: год не может быть больше 2025.")
            return None
        if month < 1 or month > 12:
            print("Ошибка: месяц должен быть от 1 до 12.")
            return None
        # Проверка количества дней в месяце
        days_in_month = [31, 29 if is_leap_year(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if day < 1 or day > days_in_month[month - 1]:
            print(f"Ошибка: день должен быть от 1 до {days_in_month[month - 1]} для {month}-го месяца {year} года.")
            return None
        return date_str
    except ValueError:
        print("Ошибка: некорректная дата (используйте цифры).")
        return None

def validate_float(value, field):
    """Проверяет, является ли значение числом."""
    try:
        return float(value)
    except ValueError:
        print(f"Ошибка: {field} должно быть числом (например, 55.7558).")
        return None

# --- Функции для таблицы Sources ---

def sources_list_all(conn):
    """Показывает все источники, сортируя по названию."""
    print("\nИсточники:")
    try:
        cursor = conn.execute("SELECT title, type, link, content, name FROM Sources ORDER BY title")
        rows = cursor.fetchall()
        if not rows:
            print("Нет источников.")
        for row in rows:
            print(f"Название: {row[0]}, Тип: {row[1] or 'Не указано'}, Ссылка: {row[2] or 'Не указано'}, Содержание: {row[3] or 'Не указано'}, Имя: {row[4] or 'Не указано'}")
    except Exception as e:
        print(f"Ошибка: {e}")

def sources_search_by_title(conn):
    """Ищет источник по названию."""
    cursor = conn.execute("SELECT title FROM Sources ORDER BY title")
    titles = [row[0] for row in cursor.fetchall()]
    if not titles:
        print("Нет источников.")
        return
    print("\nНазвания источников:")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    choice = input("Введите номер или название: ")
    try:
        title = titles[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(titles) else choice
        cursor = conn.execute("SELECT title, type, link, content, name FROM Sources WHERE title = ?", (title,))
        row = cursor.fetchone()
        if row:
            print(f"Название: {row[0]}, Тип: {row[1] or 'Не указано'}, Ссылка: {row[2] or 'Не указано'}, Содержание: {row[3] or 'Не указано'}, Имя: {row[4] or 'Не указано'}")
        else:
            print("Источник не найден.")
    except Exception as e:
        print(f"Ошибка: {e}")

def sources_add(conn):
    """Добавляет источник."""
    print("\nНовый источник")
    title = input("> Название: ")
    type_ = input("> Тип (Enter, если нет): ") or None
    link = input("> Ссылка (Enter, если нет): ") or None
    content = input("> Содержание (Enter, если нет): ") or None
    name = input("> Имя (Enter, если нет): ") or None
    try:
        cursor = conn.execute("INSERT INTO Sources (title, type, link, content, name) VALUES (?, ?, ?, ?, ?)", 
                             (title, type_, link, content, name))
        conn.commit()
        print("Источник добавлен.")
        return cursor.lastrowid  # Возвращает ID нового источника
    except sqlite3.IntegrityError:
        print("Ошибка: такой источник уже есть.")
        return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

def sources_update(conn):
    """Обновляет источник."""
    cursor = conn.execute("SELECT title FROM Sources ORDER BY title")
    titles = [row[0] for row in cursor.fetchall()]
    if not titles:
        print("Нет источников.")
        return
    print("\nНазвания источников:")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    choice = input("Введите номер или название: ")
    try:
        title = titles[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(titles) else choice
        type_ = input("> Новый тип (Enter, если не менять): ") or None
        link = input("> Новая ссылка (Enter, если не менять): ") or None
        content = input("> Новое содержание (Enter, если не менять): ") or None
        name = input("> Новое имя (Enter, если не менять): ") or None
        cursor = conn.execute("UPDATE Sources SET type = COALESCE(?, type), link = COALESCE(?, link), content = COALESCE(?, content), name = COALESCE(?, name) WHERE title = ?", 
                             (type_, link, content, name, title))
        conn.commit()
        print("Источник обновлён." if cursor.rowcount else "Источник не найден.")
    except Exception as e:
        print(f"Ошибка: {e}")

def sources_delete(conn):
    """Удаляет источник."""
    cursor = conn.execute("SELECT title FROM Sources ORDER BY title")
    titles = [row[0] for row in cursor.fetchall()]
    if not titles:
        print("Нет источников.")
        return
    print("\nНазвания источников:")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    choice = input("Введите номер или название: ")
    try:
        title = titles[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(titles) else choice
        cursor = conn.execute("DELETE FROM Sources WHERE title = ?", (title,))
        conn.commit()
        print("Источник удалён." if cursor.rowcount else "Источник не найден.")
    except Exception as e:
        print(f"Ошибка: {e}")

# --- Функции для таблицы Coordinates ---

def coordinates_list_all(conn):
    """Показывает все координаты, сортируя по широте."""
    print("\nКоординаты:")
    try:
        cursor = conn.execute("SELECT latitude, longitude, name FROM Coordinates ORDER BY latitude")
        rows = cursor.fetchall()
        if not rows:
            print("Нет координат.")
        for row in rows:
            print(f"Широта: {row[0]}, Долгота: {row[1]}, Название: {row[2] or 'Не указано'}")
    except Exception as e:
        print(f"Ошибка: {e}")

def coordinates_search_by_name(conn):
    """Ищет координаты по названию."""
    cursor = conn.execute("SELECT name FROM Coordinates WHERE name IS NOT NULL ORDER BY name")
    names = [row[0] for row in cursor.fetchall()]
    if not names:
        print("Нет координат с названиями.")
        return
    print("\nНазвания координат:")
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    choice = input("Введите номер или название: ")
    try:
        name = titles[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(names) else choice
        cursor = conn.execute("SELECT latitude, longitude, name FROM Coordinates WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            print(f"Широта: {row[0]}, Долгота: {row[1]}, Название: {row[2] or 'Не указано'}")
        else:
            print("Координаты не найдены.")
    except Exception as e:
        print(f"Ошибка: {e}")

def coordinates_add(conn):
    """Добавляет новые координаты."""
    print("\nНовые координаты")
    lat = input("> Широта: ")
    lat = validate_float(lat, "Широта")
    if lat is None:
        return
    lon = input("> Долгота: ")
    lon = validate_float(lon, "Долгота")
    if lon is None:
        return
    name = input("> Название (Enter, если нет): ") or None
    try:
        conn.execute("INSERT INTO Coordinates (latitude, longitude, name) VALUES (?, ?, ?)", (lat, lon, name))
        conn.commit()
        print("Координаты добавлены.")
    except sqlite3.IntegrityError:
        print("Ошибка: такие координаты уже есть.")
    except Exception as e:
        print(f"Ошибка: {e}")

def coordinates_update(conn):
    """Обновляет координаты."""
    cursor = conn.execute("SELECT name FROM Coordinates WHERE name IS NOT NULL ORDER BY name")
    names = [row[0] for row in cursor.fetchall()]
    if not names:
        print("Нет координат с названиями.")
        return
    print("\nНазвания координат:")
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    choice = input("Введите номер или название: ")
    try:
        name = names[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(names) else choice
        new_lat = input("> Новая широта (Enter, если не менять): ")
        new_lat = validate_float(new_lat, "Широта") if new_lat else None
        new_lon = input("> Новая долгота (Enter, если не менять): ")
        new_lon = validate_float(new_lon, "Долгота") if new_lon else None
        new_name = input("> Новое название (Enter, если не менять): ") or None
        cursor = conn.execute("UPDATE Coordinates SET latitude = COALESCE(?, latitude), longitude = COALESCE(?, longitude), name = COALESCE(?, name) WHERE name = ?", 
                             (new_lat, new_lon, new_name, name))
        conn.commit()
        print("Координаты обновлены." if cursor.rowcount else "Координаты не найдены.")
    except Exception as e:
        print(f"Ошибка: {e}")

def coordinates_delete(conn):
    """Удаляет координаты."""
    cursor = conn.execute("SELECT name FROM Coordinates WHERE name IS NOT NULL ORDER BY name")
    names = [row[0] for row in cursor.fetchall()]
    if not names:
        print("Нет координат с названиями.")
        return
    print("\nНазвания координат:")
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    choice = input("Введите номер или название: ")
    try:
        name = names[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(names) else choice
        cursor = conn.execute("DELETE FROM Coordinates WHERE name = ?", (name,))
        conn.commit()
        print("Координаты удалены." if cursor.rowcount else "Координаты не найдены.")
    except Exception as e:
        print(f"Ошибка: {e}")

# --- Функции для таблицы Persons ---

def persons_list_all(conn):
    """Показывает всех персон, сортируя по фамилии."""
    print("\nПерсоны:")
    try:
        cursor = conn.execute("SELECT surname, name, patronymic, date_of_birth, biography FROM Persons ORDER BY surname")
        rows = cursor.fetchall()
        if not rows:
            print("Нет персон.")
        for row in rows:
            print(f"Фамилия: {row[0]}, Имя: {row[1] or 'Не указано'}, Отчество: {row[2] or 'Не указано'}, Дата рождения: {row[3] or 'Не указано'}, Биография: {row[4] or 'Не указано'}")
    except Exception as e:
        print(f"Ошибка: {e}")

def persons_search_by_surname(conn):
    """Ищет персону по фамилии."""
    cursor = conn.execute("SELECT surname FROM Persons ORDER BY surname")
    surnames = [row[0] for row in cursor.fetchall()]
    if not surnames:
        print("Нет персон.")
        return
    print("\nФамилии:")
    for i, surname in enumerate(surnames, 1):
        print(f"{i}. {surname}")
    choice = input("Введите номер или фамилию: ")
    try:
        surname = surnames[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(surnames) else choice
        cursor = conn.execute("SELECT surname, name, patronymic, date_of_birth, biography FROM Persons WHERE surname = ?", (surname,))
        row = cursor.fetchone()
        if row:
            print(f"Фамилия: {row[0]}, Имя: {row[1] or 'Не указано'}, Отчество: {row[2] or 'Не указано'}, Дата рождения: {row[3] or 'Не указано'}, Биография: {row[4] or 'Не указано'}")
        else:
            print("Персона не найдена.")
    except Exception as e:
        print(f"Ошибка: {e}")

def persons_add(conn):
    """Добавляет персону."""
    print("\nНовая персона")
    surname = input("> Фамилия: ")
    name = input("> Имя: ") or None
    patronymic = input("> Отчество (Enter, если нет): ") or None
    dob = input("> Дата рождения (ГГГГ-ММ-ДД, Enter, если нет): ")
    dob = validate_date(dob)
    if dob is None and dob != '':
        return
    bio = input("> Биография (Enter, если нет): ") or None
    try:
        conn.execute("INSERT INTO Persons (surname, name, patronymic, date_of_birth, biography) VALUES (?, ?, ?, ?, ?)", 
                     (surname, name, patronymic, dob, bio))
        conn.commit()
        print("Персона добавлена.")
    except sqlite3.IntegrityError:
        print("Ошибка: такая персона уже есть.")
    except Exception as e:
        print(f"Ошибка: {e}")

def persons_update(conn):
    """Обновляет персону."""
    cursor = conn.execute("SELECT surname FROM Persons ORDER BY surname")
    surnames = [row[0] for row in cursor.fetchall()]
    if not surnames:
        print("Нет персон.")
        return
    print("\nФамилии:")
    for i, surname in enumerate(surnames, 1):
        print(f"{i}. {surname}")
    choice = input("Введите номер или фамилию: ")
    try:
        surname = surnames[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(surnames) else choice
        name = input("> Новое имя (Enter, если не менять): ") or None
        patronymic = input("> Новое отчество (Enter, если не менять): ") or None
        dob = input("> Новая дата рождения (ГГГГ-ММ-ДД, Enter, если не менять): ")
        dob = validate_date(dob) if dob else None
        bio = input("> Новая биография (Enter, если не менять): ") or None
        cursor = conn.execute("UPDATE Persons SET name = COALESCE(?, name), patronymic = COALESCE(?, patronymic), date_of_birth = COALESCE(?, date_of_birth), biography = COALESCE(?, biography) WHERE surname = ?", 
                             (name, patronymic, dob, bio, surname))
        conn.commit()
        print("Персона обновлена." if cursor.rowcount else "Персона не найдена.")
    except Exception as e:
        print(f"Ошибка: {e}")

def persons_delete(conn):
    """Удаляет персону."""
    cursor = conn.execute("SELECT surname FROM Persons ORDER BY surname")
    surnames = [row[0] for row in cursor.fetchall()]
    if not surnames:
        print("Нет персон.")
        return
    print("\nФамилии:")
    for i, surname in enumerate(surnames, 1):
        print(f"{i}. {surname}")
    choice = input("Введите номер или фамилию: ")
    try:
        surname = surnames[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(surnames) else choice
        cursor = conn.execute("DELETE FROM Persons WHERE surname = ?", (surname,))
        conn.commit()
        print("Персона удалена." if cursor.rowcount else "Персона не найдена.")
    except Exception as e:
        print(f"Ошибка: {e}")

# --- Функции для таблицы Events ---

def events_list_all(conn):
    """Показывает все события, сортируя по дате."""
    print("\nСобытия:")
    try:
        cursor = conn.execute("SELECT Events.name, Events.data, Events.description, Sources.title FROM Events LEFT JOIN Sources ON Events.resource_id = Sources.id ORDER BY Events.data")
        rows = cursor.fetchall()
        if not rows:
            print("Нет событий.")
        for row in rows:
            source = row[3] if row[3] else "Источник не найден"
            print(f"Название: {row[0]}, Дата: {row[1] or 'Не указано'}, Описание: {row[2] or 'Не указано'}, Источник: {source}")
    except Exception as e:
        print(f"Ошибка: {e}")

def events_search_by_name(conn):
    """Ищет событие по названию."""
    cursor = conn.execute("SELECT name FROM Events ORDER BY name")
    names = [row[0] for row in cursor.fetchall()]
    if not names:
        print("Нет событий.")
        return
    print("\nНазвания событий:")
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    choice = input("Введите номер или название: ")
    try:
        name = names[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(names) else choice
        cursor = conn.execute("SELECT Events.name, Events.data, Events.description, Sources.title FROM Events LEFT JOIN Sources ON Events.resource_id = Sources.id WHERE Events.name = ?", (name,))
        row = cursor.fetchone()
        if row:
            source = row[3] if row[3] else "Источник не найден"
            print(f"Название: {row[0]}, Дата: {row[1] or 'Не указано'}, Описание: {row[2] or 'Не указано'}, Источник: {source}")
        else:
            print("Событие не найдено.")
    except Exception as e:
        print(f"Ошибка: {e}")

def events_add(conn):
    """Добавляет событие."""
    print("\nНовое событие")
    name = input("> Название: ")
    data = input("> Дата (ГГГГ-ММ-ДД): ")
    data = validate_date(data)
    if data is None:
        return
    description = input("> Описание (Enter, если нет): ") or None
    cursor = conn.execute("SELECT title FROM Sources ORDER BY title")
    titles = [row[0] for row in cursor.fetchall()]
    if not titles:
        print("Нет источников.")
        return
    print("\nИсточники:")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    choice = input("Введите номер или название источника: ")
    try:
        title = titles[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(titles) else choice
        cursor = conn.execute("SELECT id FROM Sources WHERE title = ?", (title,))
        src = cursor.fetchone()
        if not src:
            print("Источник не найден.")
            return
        conn.execute("INSERT INTO Events (name, data, description, resource_id) VALUES (?, ?, ?, ?)", 
                     (name, data, description, src[0]))
        conn.commit()
        print("Событие добавлено.")
    except sqlite3.IntegrityError:
        print("Ошибка: такое событие уже есть.")
    except Exception as e:
        print(f"Ошибка: {e}")

def events_update(conn):
    """Обновляет событие."""
    cursor = conn.execute("SELECT name FROM Events ORDER BY name")
    names = [row[0] for row in cursor.fetchall()]
    if not names:
        print("Нет событий.")
        return
    print("\nНазвания событий:")
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    choice = input("Введите номер или название: ")
    try:
        name = names[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(names) else choice
        data = input("> Новая дата (ГГГГ-ММ-ДД, Enter, если не менять): ")
        data = validate_date(data) if data else None
        description = input("> Новое описание (Enter, если не менять): ") or None
        cursor = conn.execute("SELECT title FROM Sources ORDER BY title")
        titles = [row[0] for row in cursor.fetchall()]
        if titles:
            print("\nИсточники:")
            for i, title in enumerate(titles, 1):
                print(f"{i}. {title}")
            choice = input("Введите номер или название источника (Enter, если не менять): ")
            resource_id = None
            if choice:
                title = titles[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(titles) else choice
                cursor = conn.execute("SELECT id FROM Sources WHERE title = ?", (title,))
                src = cursor.fetchone()
                if not src:
                    print("Источник не найден.")
                    return
                resource_id = src[0]
            cursor = conn.execute("UPDATE Events SET data = COALESCE(?, data), description = COALESCE(?, description), resource_id = COALESCE(?, resource_id) WHERE name = ?", 
                                 (data, description, resource_id, name))
        else:
            cursor = conn.execute("UPDATE Events SET data = COALESCE(?, data), description = COALESCE(?, description) WHERE name = ?", 
                                 (data, description, name))
        conn.commit()
        print("Событие обновлено." if cursor.rowcount else "Событие не найдено.")
    except Exception as e:
        print(f"Ошибка: {e}")

def events_delete(conn):
    """Удаляет событие."""
    cursor = conn.execute("SELECT name FROM Events ORDER BY name")
    names = [row[0] for row in cursor.fetchall()]
    if not names:
        print("Нет событий.")
        return
    print("\nНазвания событий:")
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    choice = input("Введите номер или название: ")
    try:
        name = names[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(names) else choice
        cursor = conn.execute("DELETE FROM Events WHERE name = ?", (name,))
        conn.commit()
        print("Событие удалено." if cursor.rowcount else "Событие не найдено.")
    except Exception as e:
        print(f"Ошибка: {e}")

# --- Функции для таблицы Texts ---

def texts_list_all(conn):
    """Показывает все тексты, сортируя по дате."""
    print("\nТексты:")
    try:
        cursor = conn.execute("SELECT Tex.name, Tex.data, Tex.content, Sources.title FROM Tex LEFT JOIN Sources ON Tex.resource_id = Sources.id ORDER BY Tex.data")
        rows = cursor.fetchall()
        if not rows:
            print("Нет текстов.")
        for row in rows:
            source = row[3] if row[3] else "Источник не найден"
            print(f"Название: {row[0]}, Дата: {row[1] or 'Не указано'}, Содержание: {row[2] or 'Не указано'}, Источник: {source}")
    except Exception as e:
        print(f"Ошибка: {e}")

def texts_search_by_name(conn):
    """Ищет текст по названию."""
    cursor = conn.execute("SELECT name FROM Tex ORDER BY name")
    names = [row[0] for row in cursor.fetchall()]
    if not names:
        print("Нет текстов.")
        return
    print("\nНазвания текстов:")
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    choice = input("Введите номер или название: ")
    try:
        name = names[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(names) else choice
        cursor = conn.execute("SELECT Tex.name, Tex.data, Tex.content, Sources.title FROM Tex LEFT JOIN Sources ON Tex.resource_id = Sources.id WHERE Tex.name = ?", (name,))
        row = cursor.fetchone()
        if row:
            source = row[3] if row[3] else "Источник не найден"
            print(f"Название: {row[0]}, Дата: {row[1] or 'Не указано'}, Содержание: {row[2] or 'Не указано'}, Источник: {source}")
        else:
            print("Текст не найден.")
    except Exception as e:
        print(f"Ошибка: {e}")

def texts_add(conn):
    """Добавляет текст."""
    print("\nНовый текст")
    name = input("> Название: ")
    content = input("> Содержание: ") or None
    data = input("> Дата (ГГГГ-ММ-ДД): ")
    data = validate_date(data)
    if data is None:
        return
    cursor = conn.execute("SELECT title FROM Sources ORDER BY title")
    titles = [row[0] for row in cursor.fetchall()]
    print("\nИсточники:")
    print("0. Не указывать источник")
    if titles:
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")
    print("-1. Создать новый источник")
    choice = input("Введите номер, название источника, 0 или -1: ")
    try:
        resource_id = None
        if choice == "0":
            resource_id = None
        elif choice == "-1":
            resource_id = sources_add(conn)
            if resource_id is None:
                return
        else:
            title = titles[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(titles) else choice
            cursor = conn.execute("SELECT id FROM Sources WHERE title = ?", (title,))
            src = cursor.fetchone()
            if not src:
                print("Источник не найден.")
                return
            resource_id = src[0]
        conn.execute("INSERT INTO Tex (name, content, data, resource_id) VALUES (?, ?, ?, ?)", 
                     (name, content, data, resource_id))
        conn.commit()
        print("Текст добавлен.")
    except sqlite3.IntegrityError:
        print("Ошибка: такой текст уже есть.")
    except Exception as e:
        print(f"Ошибка: {e}")

def texts_update(conn):
    """Обновляет текст."""
    cursor = conn.execute("SELECT name FROM Tex ORDER BY name")
    names = [row[0] for row in cursor.fetchall()]
    if not names:
        print("Нет текстов.")
        return
    print("\nНазвания текстов:")
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    choice = input("Введите номер или название: ")
    try:
        name = names[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(names) else choice
        content = input("> Новое содержание (Enter, если не менять): ") or None
        data = input("> Новая дата (ГГГГ-ММ-ДД, Enter, если не менять): ")
        data = validate_date(data) if data else None
        cursor = conn.execute("SELECT title FROM Sources ORDER BY title")
        titles = [row[0] for row in cursor.fetchall()]
        print("\nИсточники:")
        print("0. Не указывать источник")
        if titles:
            for i, title in enumerate(titles, 1):
                print(f"{i}. {title}")
        print("-1. Создать новый источник")
        choice = input("Введите номер, название источника, 0 или -1 (Enter, если не менять): ")
        resource_id = None
        if choice == "0":
            resource_id = None
        elif choice == "-1":
            resource_id = sources_add(conn)
            if resource_id is None:
                return
        elif choice:
            title = titles[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(titles) else choice
            cursor = conn.execute("SELECT id FROM Sources WHERE title = ?", (title,))
            src = cursor.fetchone()
            if not src:
                print("Источник не найден.")
                return
            resource_id = src[0]
        cursor = conn.execute("UPDATE Tex SET content = COALESCE(?, content), data = COALESCE(?, data), resource_id = COALESCE(?, resource_id) WHERE name = ?", 
                             (content, data, resource_id, name))
        conn.commit()
        print("Текст обновлён." if cursor.rowcount else "Текст не найден.")
    except Exception as e:
        print(f"Ошибка: {e}")

def texts_delete(conn):
    """Удаляет текст."""
    cursor = conn.execute("SELECT name FROM Tex ORDER BY name")
    names = [row[0] for row in cursor.fetchall()]
    if not names:
        print("Нет текстов.")
        return
    print("\nНазвания текстов:")
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    choice = input("Введите номер или название: ")
    try:
        name = names[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(names) else choice
        cursor = conn.execute("DELETE FROM Tex WHERE name = ?", (name,))
        conn.commit()
        print("Текст удалён." if cursor.rowcount else "Текст не найден.")
    except Exception as e:
        print(f"Ошибка: {e}")

# --- Функции для таблицы Places ---

def places_list_all(conn):
    """Показывает все места, сортируя по названию."""
    print("\nМеста:")
    try:
        cursor = conn.execute("SELECT Places.name, Coordinates.latitude, Coordinates.longitude, Sources.title FROM Places JOIN Coordinates ON Places.coordinate_id = Coordinates.id LEFT JOIN Sources ON Places.resource_id = Sources.id ORDER BY Places.name")
        rows = cursor.fetchall()
        if not rows:
            print("Нет мест.")
        for row in rows:
            source = row[3] if row[3] else "Источник не найден"
            print(f"Название: {row[0]}, Широта: {row[1]}, Долгота: {row[2]}, Источник: {source}")
    except Exception as e:
        print(f"Ошибка: {e}")

def places_search_by_name(conn):
    """Ищет место по названию."""
    cursor = conn.execute("SELECT name FROM Places ORDER BY name")
    names = [row[0] for row in cursor.fetchall()]
    if not names:
        print("Нет мест.")
        return
    print("\nНазвания мест:")
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    choice = input("Введите номер или название: ")
    try:
        name = names[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(names) else choice
        cursor = conn.execute("SELECT Places.name, Coordinates.latitude, Coordinates.longitude, Sources.title FROM Places JOIN Coordinates ON Places.coordinate_id = Coordinates.id LEFT JOIN Sources ON Places.resource_id = Sources.id WHERE Places.name = ?", (name,))
        row = cursor.fetchone()
        if row:
            source = row[3] if row[3] else "Источник не найден"
            print(f"Название: {row[0]}, Широта: {row[1]}, Долгота: {row[2]}, Источник: {source}")
        else:
            print("Место не найдено.")
    except Exception as e:
        print(f"Ошибка: {e}")

def places_add(conn):
    """Добавляет место."""
    print("\nНовое место")
    name = input("> Название: ")
    cursor = conn.execute("SELECT name FROM Coordinates WHERE name IS NOT NULL ORDER BY name")
    coord_names = [row[0] for row in cursor.fetchall()]
    if not coord_names:
        print("Нет координат.")
        return
    print("\nКоординаты:")
    for i, coord_name in enumerate(coord_names, 1):
        print(f"{i}. {coord_name}")
    coord_choice = input("Введите номер или название координат: ")
    cursor = conn.execute("SELECT title FROM Sources ORDER BY title")
    titles = [row[0] for row in cursor.fetchall()]
    if not titles:
        print("Нет источников.")
        return
    print("\nИсточники:")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    source_choice = input("Введите номер или название источника: ")
    try:
        coord_name = coord_names[int(coord_choice) - 1] if coord_choice.isdigit() and 1 <= int(coord_choice) <= len(coord_names) else coord_choice
        cursor = conn.execute("SELECT id FROM Coordinates WHERE name = ?", (coord_name,))
        coord = cursor.fetchone()
        if not coord:
            print("Координаты не найдены.")
            return
        title = titles[int(source_choice) - 1] if source_choice.isdigit() and 1 <= int(source_choice) <= len(titles) else source_choice
        cursor = conn.execute("SELECT id FROM Sources WHERE title = ?", (title,))
        src = cursor.fetchone()
        if not src:
            print("Источник не найден.")
            return
        conn.execute("INSERT INTO Places (name, resource_id, coordinate_id) VALUES (?, ?, ?)", 
                     (name, src[0], coord[0]))
        conn.commit()
        print("Место добавлено.")
    except sqlite3.IntegrityError:
        print("Ошибка: такое место уже есть.")
    except Exception as e:
        print(f"Ошибка: {e}")

def places_update(conn):
    """Обновляет место."""
    cursor = conn.execute("SELECT name FROM Places ORDER BY name")
    names = [row[0] for row in cursor.fetchall()]
    if not names:
        print("Нет мест.")
        return
    print("\nНазвания мест:")
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    choice = input("Введите номер или название: ")
    try:
        name = names[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(names) else choice
        new_name = input("> Новое название (Enter, если не менять): ") or None
        cursor = conn.execute("SELECT title FROM Sources ORDER BY title")
        titles = [row[0] for row in cursor.fetchall()]
        if titles:
            print("\nИсточники:")
            for i, title in enumerate(titles, 1):
                print(f"{i}. {title}")
            source_choice = input("Введите номер или название источника (Enter, если не менять): ")
            resource_id = None
            if source_choice:
                title = titles[int(source_choice) - 1] if source_choice.isdigit() and 1 <= int(source_choice) <= len(titles) else source_choice
                cursor = conn.execute("SELECT id FROM Sources WHERE title = ?", (title,))
                src = cursor.fetchone()
                if not src:
                    print("Источник не найден.")
                    return
                resource_id = src[0]
            cursor = conn.execute("UPDATE Places SET name = COALESCE(?, name), resource_id = COALESCE(?, resource_id) WHERE name = ?", 
                                 (new_name, resource_id, name))
        else:
            cursor = conn.execute("UPDATE Places SET name = COALESCE(?, name) WHERE name = ?", 
                                 (new_name, name))
        conn.commit()
        print("Место обновлено." if cursor.rowcount else "Место не найдено.")
    except Exception as e:
        print(f"Ошибка: {e}")

def places_delete(conn):
    """Удаляет место."""
    cursor = conn.execute("SELECT name FROM Places ORDER BY name")
    names = [row[0] for row in cursor.fetchall()]
    if not names:
        print("Нет мест.")
        return
    print("\nНазвания мест:")
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    choice = input("Введите номер или название: ")
    try:
        name = names[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(names) else choice
        cursor = conn.execute("DELETE FROM Places WHERE name = ?", (name,))
        conn.commit()
        print("Место удалено." if cursor.rowcount else "Место не найдено.")
    except Exception as e:
        print(f"Ошибка: {e}")

# --- Функции для таблицы PeopleInteractions ---

def interactions_list_all(conn):
    """Показывает все взаимодействия, сортируя по описанию."""
    print("\nВзаимодействия:")
    try:
        cursor = conn.execute("SELECT PeopleInteractions.description, Persons.surname, Sources.title FROM PeopleInteractions JOIN Persons ON PeopleInteractions.person_id = Persons.id LEFT JOIN Sources ON PeopleInteractions.resource_id = Sources.id ORDER BY PeopleInteractions.description")
        rows = cursor.fetchall()
        if not rows:
            print("Нет взаимодействий.")
        for row in rows:
            source = row[2] if row[2] else "Источник не найден"
            print(f"Описание: {row[0] or 'Не указано'}, Персона: {row[1]}, Источник: {source}")
    except Exception as e:
        print(f"Ошибка: {e}")

def interactions_add(conn):
    """Добавляет взаимодействие."""
    print("\nНовое взаимодействие")
    description = input("> Описание (Enter, если нет): ") or None
    cursor = conn.execute("SELECT surname FROM Persons ORDER BY surname")
    surnames = [row[0] for row in cursor.fetchall()]
    if not surnames:
        print("Нет персон.")
        return
    print("\nПерсоны:")
    for i, surname in enumerate(surnames, 1):
        print(f"{i}. {surname}")
    person_choice = input("Введите номер или фамилию: ")
    cursor = conn.execute("SELECT title FROM Sources ORDER BY title")
    titles = [row[0] for row in cursor.fetchall()]
    if not titles:
        print("Нет источников.")
        return
    print("\nИсточники:")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    source_choice = input("Введите номер или название источника: ")
    try:
        surname = surnames[int(person_choice) - 1] if person_choice.isdigit() and 1 <= int(person_choice) <= len(surnames) else person_choice
        cursor = conn.execute("SELECT id FROM Persons WHERE surname = ?", (surname,))
        person = cursor.fetchone()
        if not person:
            print("Персона не найдена.")
            return
        title = titles[int(source_choice) - 1] if source_choice.isdigit() and 1 <= int(source_choice) <= len(titles) else source_choice
        cursor = conn.execute("SELECT id FROM Sources WHERE title = ?", (title,))
        src = cursor.fetchone()
        if not src:
            print("Источник не найден.")
            return
        conn.execute("INSERT INTO PeopleInteractions (description, resource_id, person_id) VALUES (?, ?, ?)", 
                     (description, src[0], person[0]))
        conn.commit()
        print("Взаимодействие добавлено.")
    except Exception as e:
        print(f"Ошибка: {e}")

def interactions_delete(conn):
    """Удаляет взаимодействие."""
    cursor = conn.execute("SELECT description FROM PeopleInteractions WHERE description IS NOT NULL ORDER BY description")
    descriptions = [row[0] for row in cursor.fetchall()]
    if not descriptions:
        print("Нет взаимодействий с описаниями.")
        return
    print("\nОписания взаимодействий:")
    for i, desc in enumerate(descriptions, 1):
        print(f"{i}. {desc}")
    choice = input("Введите номер или описание: ")
    try:
        desc = descriptions[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(descriptions) else choice
        cursor = conn.execute("DELETE FROM PeopleInteractions WHERE description = ?", (desc,))
        conn.commit()
        print("Взаимодействие удалено." if cursor.rowcount else "Взаимодействие не найдено.")
    except Exception as e:
        print(f"Ошибка: {e}")

# --- Меню ---

def sources_menu(conn):
    """Меню для Sources."""
    while True:
        print("\nИсточники")
        print("1. Показать все")
        print("2. Найти по названию")
        print("3. Добавить")
        print("4. Обновить")
        print("5. Удалить")
        print("0. Назад")
        choice = input("> ")
        if choice == "0":
            return
        elif choice == "1":
            sources_list_all(conn)
        elif choice == "2":
            sources_search_by_title(conn)
        elif choice == "3":
            sources_add(conn)
        elif choice == "4":
            sources_update(conn)
        elif choice == "5":
            sources_delete(conn)
        else:
            print("Выберите 0-5.")

def coordinates_menu(conn):
    """Меню для Coordinates."""
    while True:
        print("\nКоординаты")
        print("1. Показать все")
        print("2. Найти по названию")
        print("3. Добавить")
        print("4. Обновить")
        print("5. Удалить")
        print("0. Назад")
        choice = input("> ")
        if choice == "0":
            return
        elif choice == "1":
            coordinates_list_all(conn)
        elif choice == "2":
            coordinates_search_by_name(conn)
        elif choice == "3":
            coordinates_add(conn)
        elif choice == "4":
            coordinates_update(conn)
        elif choice == "5":
            coordinates_delete(conn)
        else:
            print("Выберите 0-5.")

def persons_menu(conn):
    """Меню для Persons."""
    while True:
        print("\nПерсоны")
        print("1. Показать всех")
        print("2. Найти по фамилии")
        print("3. Добавить")
        print("4. Обновить")
        print("5. Удалить")
        print("0. Назад")
        choice = input("> ")
        if choice == "0":
            return
        elif choice == "1":
            persons_list_all(conn)
        elif choice == "2":
            persons_search_by_surname(conn)
        elif choice == "3":
            persons_add(conn)
        elif choice == "4":
            persons_update(conn)
        elif choice == "5":
            persons_delete(conn)
        else:
            print("Выберите 0-5.")

def events_menu(conn):
    """Меню для Events."""
    while True:
        print("\nСобытия")
        print("1. Показать все")
        print("2. Найти по названию")
        print("3. Добавить")
        print("4. Обновить")
        print("5. Удалить")
        print("0. Назад")
        choice = input("> ")
        if choice == "0":
            return
        elif choice == "1":
            events_list_all(conn)
        elif choice == "2":
            events_search_by_name(conn)
        elif choice == "3":
            events_add(conn)
        elif choice == "4":
            events_update(conn)
        elif choice == "5":
            events_delete(conn)
        else:
            print("Выберите 0-5.")

def texts_menu(conn):
    """Меню для Texts."""
    while True:
        print("\nТексты")
        print("1. Показать все")
        print("2. Найти по названию")
        print("3. Добавить")
        print("4. Обновить")
        print("5. Удалить")
        print("0. Назад")
        choice = input("> ")
        if choice == "0":
            return
        elif choice == "1":
            texts_list_all(conn)
        elif choice == "2":
            texts_search_by_name(conn)
        elif choice == "3":
            texts_add(conn)
        elif choice == "4":
            texts_update(conn)
        elif choice == "5":
            texts_delete(conn)
        else:
            print("Выберите 0-5.")

def places_menu(conn):
    """Меню для Places."""
    while True:
        print("\nМеста")
        print("1. Показать все")
        print("2. Найти по названию")
        print("3. Добавить")
        print("4. Обновить")
        print("5. Удалить")
        print("0. Назад")
        choice = input("> ")
        if choice == "0":
            return
        elif choice == "1":
            places_list_all(conn)
        elif choice == "2":
            places_search_by_name(conn)
        elif choice == "3":
            places_add(conn)
        elif choice == "4":
            places_update(conn)
        elif choice == "5":
            places_delete(conn)
        else:
            print("Выберите 0-5.")

def interactions_menu(conn):
    """Меню для PeopleInteractions."""
    while True:
        print("\nВзаимодействия")
        print("1. Показать все")
        print("2. Добавить")
        print("3. Удалить")
        print("0. Назад")
        choice = input("> ")
        if choice == "0":
            return
        elif choice == "1":
            interactions_list_all(conn)
        elif choice == "2":
            interactions_add(conn)
        elif choice == "3":
            interactions_delete(conn)
        else:
            print("Выберите 0-3.")

def main_menu():
    """Главное меню."""
    with get_connection() as conn:
        while True:
            print("\nМеню")
            print("1. Источники")
            print("2. Координаты")
            print("3. Персоны")
            print("4. События")
            print("5. Тексты")
            print("6. Места")
            print("7. Взаимодействия")
            print("0. Выход")
            choice = input("> ")
            if choice == "0":
                print("Выход.")
                break
            elif choice == "1":
                sources_menu(conn)
            elif choice == "2":
                coordinates_menu(conn)
            elif choice == "3":
                persons_menu(conn)
            elif choice == "4":
                events_menu(conn)
            elif choice == "5":
                texts_menu(conn)
            elif choice == "6":
                places_menu(conn)
            elif choice == "7":
                interactions_menu(conn)
            else:
                print("Выберите 0-7.")

if __name__ == "__main__":
    main_menu()