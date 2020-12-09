import sqlite3, hashlib

conn = sqlite3.connect("mybot_database.db")
cursor = conn.cursor()
# Создание таблицы студентов
cursor.execute("""CREATE TABLE students
                  (id integer primary key,
                   name text,
                   surname text,
                   patronymic text,
                   num_zach text)
               """)
conn.commit()
# Заполнение таблицы студентов
stud = [('Галеева', 'Аделя', 'Азатовна', '81201'),
        ('Салимуллина', 'Айгуль', 'Альбертовна', '81202'),
        ('Палий', 'Элина', 'Алмазовна', '81203'),
        ('Щипляева', 'Радмила', 'Сергеевна', '81204'),
        ('Гавриличев', 'Павел', 'Николаевич', '81205'),
        ('Ефимов', 'Данила', 'Вадимович', '81206'),
        ('Зарифянов', 'Юсуф', 'Зуфарович', '81207'),
        ('Чернов', 'Никита', 'Андреевич', '81208'),
        ('Биктимиров','Владимир', 'Олегович', '81209'),
        ('Васильев', 'Антон', 'Николаевич', '81210'),
        ('Садыков', 'Ильдар', 'Наилевич', '81211'),
        ('Шахова', 'Анастасия', 'Юрьевна', '81212'),]

cursor.executemany("INSERT INTO students(name, surname, patronymic, num_zach) VALUES (?,?,?,?)", stud)
conn.commit()

# Создание таблицы записавшихся на курс
cursor.execute("""CREATE TABLE joined
                  (id integer primary key,
                   telegram_id text,
                   FOREIGN KEY(id) REFERENCES students(id))
               """)
conn.commit()

# Создание таблицы учета
cursor.execute("""CREATE TABLE uchet
                  (id integer primary key,
                   points integer,
                   misses integer,
                   debts integer,
                   FOREIGN KEY(id) REFERENCES students(id))
               """)
conn.commit()

uch = [(1, 35, 5, 0),
       (3, 33, 1, 3),
       (2, 29, 4, 2), (4, 36, 2, 1), (5, 50, 0, 0),
       (6, 28, 3, 6), (7, 22, 9, 5), (8, 43, 1, 2),
       (9, 32, 3, 3), (10, 43, 2, 1), (11, 50, 0, 0),
       (12, 13, 10, 10)]

cursor.executemany("INSERT INTO uchet(id, points, misses, debts) VALUES (?,?,?,?)", uch)
conn.commit()

# Создание таблицы в которой будет логин и пароль админа
cursor.execute("""CREATE TABLE admin
                  (login text,
                   password text,
                   telegram_id text)
               """)
conn.commit()

cursor.execute("INSERT INTO admin(login, password, telegram_id) VALUES (?,?,?)", ('administrator', hashlib.md5(b"qwerty123").hexdigest(), 'undefined'))
conn.commit()

#CREATE TABLE if not exists students


# вывести содержимое таблиц
for row in cursor.execute('SELECT * FROM students'):
    print(row)
print()
for row in cursor.execute('SELECT * FROM admin'):
    print(row)

cursor.close()
conn.close()
