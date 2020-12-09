import telebot, sqlite3, hashlib

name = ''
surname = ''
patronymic = ''
num_zach = ''

bot = telebot.TeleBot('1397387580:AAFUqrVJ2cB95UitgPgXahvNVOn5y48jGXM')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Вас приветствует бот курса по выбору "Python и анализ данных". /help - помощь по командам')

@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Для студента:\n /join - записаться(войти) на курс\n /getinfo - получить информацию о курсе\n /my_rating - посмотреть успеваемость\n /unjoin - выйти с курса\n Для преподавателя\n /login_admin - вход для преподавателя\n /joined_students - список студентов, записаных на курс\n /show_stats - успеваемость курса')

@bot.message_handler(commands=['getinfo'])
def get_inf(message):
    bot.send_message(message.from_user.id, "Курс Python и анализ данных. Преподаватель Абдуллин Адель Ильдусович. Период 01.09.2020-31.12.2020 по четвергам с 11:50 до 13:20")
    

@bot.message_handler(commands=['join'])
def login_stud_message(message):
    bot.send_message(message.from_user.id, "Введите фамилию: ")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    global name
    name = message.text
    bot.send_message(message.from_user.id, 'Введите имя:')
    bot.register_next_step_handler(message, get_surname)

def get_surname(message):
    global surname
    surname = message.text
    bot.send_message(message.from_user.id, 'Введите отчество:')
    bot.register_next_step_handler(message, get_patronymic)

def get_patronymic(message):
    global patronymic
    patronymic = message.text
    bot.send_message(message.from_user.id, 'Введите номер зачетки:')
    bot.register_next_step_handler(message, get_num_zach)

def get_num_zach(message):
    global num_zach
    num_zach = message.text;    
    con = sqlite3.connect("mybot_database.db")
    cur = con.cursor()
    sel_res = cur.execute('SELECT id FROM students WHERE name=? and surname=? and patronymic=? and num_zach=?', (name, surname, patronymic, num_zach))
    first_row = cur.fetchone()
    if first_row != None:#если студент найден то мы должны привязать его телеграм айди
        tid_was = cur.execute('SELECT id FROM joined WHERE telegram_id=?', (message.from_user.id,))
        tid_was_row = cur.fetchone()
        if tid_was_row != None:#если к этому телеграм айди уже был кто то привязан то перепривязать
            cur.execute('UPDATE joined SET id=? WHERE telegram_id=?', (first_row[0], message.from_user.id))
            con.commit()
        else:#если к этому телеграм айди еще никто не был привязан
            cur.execute('INSERT INTO joined(id, telegram_id) VALUES (?, ?)', (first_row[0], message.from_user.id))
            con.commit()
        bot.send_message(message.from_user.id, 'Вы записались и вошли на курс')
    else:
        bot.send_message(message.from_user.id, 'Студента с такими данными не существует!')
    cur.close()
    con.close()

#Показ рейтинга студента
@bot.message_handler(commands=['my_rating'])
def login_stud_message(message):
    con = sqlite3.connect("mybot_database.db")
    cur = con.cursor()
    sel_res = cur.execute('SELECT points, misses, debts FROM uchet uch, joined jj WHERE jj.id=uch.id AND jj.telegram_id=?', (message.from_user.id,))
    first_row = cur.fetchone()
    if first_row != None:
        bot.send_message(message.from_user.id, f'Баллы {str(first_row[0])}, пропуски {str(first_row[1])}, долги {str(first_row[2])}')
    else:
        bot.send_message(message.from_user.id, "Ошибка - вы не записаны на курс")
    cur.close()
    con.close()

@bot.message_handler(commands=['unjoin'])
def delete_me(message):
    con = sqlite3.connect("mybot_database.db")
    cur = con.cursor()
    cur.execute('DELETE FROM joined WHERE telegram_id=?', (message.from_user.id,))
    bot.send_message(message.from_user.id, 'Вы больше не записаны на этот курс')
    con.commit()
    cur.close()
    con.close()


#Вход для администраторов
def admin_login_exists(adm_login):
    con = sqlite3.connect("mybot_database.db")
    cur = con.cursor()
    sel_res = cur.execute('SELECT * FROM admin WHERE login=?', (adm_login,))
    first_row = cur.fetchone()
    return (first_row != None)

def check_admin_password(adm_psw):
    adm_psw_hash = hashlib.md5(adm_psw.encode("ascii")).hexdigest() 
    con = sqlite3.connect("mybot_database.db")
    cur = con.cursor()
    sel_res = cur.execute('SELECT * FROM admin WHERE password=?', (adm_psw_hash,))
    first_row = cur.fetchone()
    return (first_row != None)
    
@bot.message_handler(commands=['login_admin'])
def login_stud_message(message):
    bot.send_message(message.from_user.id, "Введите логин: ")
    bot.register_next_step_handler(message, get_admin_login)

def get_admin_login(message):
    adm_login = message.text
    #проверяем верный ли логин
    if admin_login_exists(adm_login):
        bot.send_message(message.from_user.id, 'Введите пароль:')
        bot.register_next_step_handler(message, get_admin_password)
    else:
        bot.send_message(message.from_user.id, 'Неверный логин')

def get_admin_password(message):
    adm_psw = message.text
    #проверяем верный ли пароль
    if check_admin_password(adm_psw):
        # привязываем телеграм айди собеседника к админской учетке
        con = sqlite3.connect("mybot_database.db")
        cur = con.cursor()
        cur.execute('UPDATE admin SET telegram_id=?', (message.from_user.id,))
        con.commit()
        cur.close()
        con.close()
        bot.send_message(message.from_user.id, 'Вы вошли в учетную запись администратора')
    else:
        bot.send_message(message.from_user.id, 'Неверный пароль!')


#функции для режима администратора
        
def is_admin(tid):#является ли пользователь с заднным айди админом
    con = sqlite3.connect("mybot_database.db")
    cur = con.cursor()
    sel_res = cur.execute('SELECT * FROM admin WHERE telegram_id=?', (tid,))
    first_row = cur.fetchone()
    return (first_row != None)


@bot.message_handler(commands=['show_stats'])
def login_stud_message(message):
    if is_admin(message.from_user.id):
        con = sqlite3.connect("mybot_database.db")
        cur = con.cursor()
        result = ""
        for row in cur.execute('SELECT name, surname, patronymic, points, misses, debts FROM students st, uchet uch, joined jj WHERE st.id=uch.id AND st.id=jj.id'):
            result = result + str(row)
            result = result + "\n"
        #print(result)
        result = result.replace(',','')
        result = result.replace(')','')
        result = result.replace('(','')
        result = result.replace("'",'')
        bot.send_message(message.from_user.id, result)
        cur.close()
        con.close()
    else:
        bot.send_message(message.from_user.id, "Ошибка - вы не администратор")

@bot.message_handler(commands=['joined_students'])
def joined_st(message):
    if is_admin(message.from_user.id):
        con = sqlite3.connect("mybot_database.db")
        cur = con.cursor()
        result = ""
        for row in cur.execute('SELECT name, surname, patronymic FROM students st, joined jj WHERE st.id=jj.id'):
            result = result + str(row)
            result = result + "\n"
        #print(result)
        result = result.replace(',','')
        result = result.replace(')','')
        result = result.replace('(','')
        result = result.replace("'",'')
        bot.send_message(message.from_user.id, result)
        cur.close()
        con.close()
    else:
        bot.send_message(message.from_user.id, "Ошибка - вы не администратор")
    


#отладочная функция..
@bot.message_handler(content_types=['text'])
def send_text(message):
    #print(message.from_user.id)
    con = sqlite3.connect("mybot_database.db")
    cur = con.cursor()
    for row in cur.execute('SELECT * FROM students'):# where telegram_id=?', (str(message.from_user.id),)):
        print(row)
    print("\n")

    for row in cur.execute('SELECT * FROM joined'):# where telegram_id=?', (str(message.from_user.id),)):
        print(row)
    print("\n")

    for row in cur.execute('SELECT * FROM admin'):# where telegram_id=?', (str(message.from_user.id),)):
        print(row)
    print("\n")

    for row in cur.execute('SELECT * FROM uchet'):# where telegram_id=?', (str(message.from_user.id),)):
        print(row)
    print("\n")
    
    cur.close()
    con.close()




if __name__ == "__main__":


    
    bot.polling()
