import telebot
import requests
import dbworker
import psycopg2
import config
import datetime
import os
import random
from telebot import types
from config import TOKEN
from bs4 import BeautifulSoup

DATABASE_URL = os.environ['DATABASE_URL']

con = psycopg2.connect(DATABASE_URL, sslmode='require')

# con = psycopg2.connect(
#   database="GagraSup",
#   user="postgres",
#   password="gagrasup",
#   host="127.0.0.1",
#   port="5432"
# )


cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS Events
     (Name TEXT,
     Text TEXT,
     Price INT,
     People INT);''')
con.commit()

events = {}
apl = {}
sm = {}
keys_user = {}

bot = telebot.TeleBot(TOKEN)

joinedFile = open('joined.txt', 'r')
joinedUsers = set()
for line in joinedFile:
    joinedUsers.add(line.strip())
joinedFile.close()

adminFile = open('admin.txt', 'r')
adminUsers = set()
for line in adminFile:
    adminUsers.add(line.strip())
adminFile.close()

@bot.message_handler(commands=['start'])
def start(message):
    if not str(message.chat.id) in joinedUsers and not str(message.chat.id) in adminUsers:
        if message.chat.id != 1647407069 and message.chat.id != 490371324:
            joinedFile = open('joined.txt', 'a')
            joinedFile.write(str(message.chat.id) + '\n')
            joinedUsers.add(message.chat.id)
        bot.send_message(message.chat.id, 'Приветствуем в нашем боте!!!'
                             '\nТебя нет в наше базе)'
                             '\nДавайте познакомимся. Как вас зовут?')
        dbworker.set_state(message.chat.id, config.States.N_USER_NAME.value)
    else:
        if message.chat.id != 1647407069 and message.chat.id != 490371324:
            state = dbworker.get_current_state(message.chat.id)
            if state == config.States.S_USER.value:
                id = message.chat.id
                buttons = [
                    types.InlineKeyboardButton(text="Прогулки", callback_data="GoSerf"),
                    types.InlineKeyboardButton(text="Мои заявки", callback_data="AllClaims"),
                    types.InlineKeyboardButton(text="Контакты", callback_data="Contacts"),
                    types.InlineKeyboardButton(text='Погода', callback_data='Weather'),
                    types.InlineKeyboardButton(text='Как добраться?', callback_data='Map')
                ]
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(*buttons)
                bot.send_message(id, 'Приветствуем в нашем боте!!!'
                                     '\nЗдесь вы можете оставить заявку на прогулку.'
                                     '\n\nВыберите тот вариант который вам нужен:', reply_markup=keyboard)
            else:
                dbworker.set_state(message.chat.id, config.States.S_START.value)
                id = message.chat.id
                buttons = [
                    types.InlineKeyboardButton(text="Прогулки", callback_data="GoSerf"),
                    types.InlineKeyboardButton(text="Мои заявки", callback_data="AllClaims"),
                    types.InlineKeyboardButton(text="Контакты", callback_data="Contacts"),
                    types.InlineKeyboardButton(text='Погода', callback_data='Weather'),
                    types.InlineKeyboardButton(text='Как добраться?', callback_data='Map')
                ]
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(*buttons)
                bot.send_message(id, 'Приветствуем в нашем боте!!!'
                                     '\nЗдесь вы можете оставить заявку на прогулку.'
                                     '\n\nВыберите тот вариант который вам нужен:', reply_markup=keyboard)
        else:
            state = dbworker.get_current_state(message.chat.id)
            if state == config.States.S_USER.value:
                buttons = [
                    types.InlineKeyboardButton(text='Все заявки', callback_data='AdminClaims'),
                    types.InlineKeyboardButton(text='Все пользователи', callback_data='AllUsers'),
                    types.InlineKeyboardButton(text='Все мероприятия', callback_data='AllEvents'),
                    types.InlineKeyboardButton(text='Создать мероприятие', callback_data='CreateEvent'),
                    types.InlineKeyboardButton(text='Отправить сообщение всем', callback_data='SendMessageAll'),
                    types.InlineKeyboardButton(text='Другие функции', callback_data='StartAdmin')
                ]
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(*buttons)
                bot.send_message(message.chat.id,
                                 'Вот функции админа. Хотите посмотреть функции бота, нажмите «Другие функции»',
                                 reply_markup=keyboard)
            else:
                dbworker.set_state(message.chat.id, config.States.S_START.value)
                buttons = [
                    types.InlineKeyboardButton(text='Все заявки', callback_data='AdminClaims'),
                    types.InlineKeyboardButton(text='Все пользователи', callback_data='AllUsers'),
                    types.InlineKeyboardButton(text='Все мероприятия', callback_data='AllEvents'),
                    types.InlineKeyboardButton(text='Создать мероприятие', callback_data='CreateEvent'),
                    types.InlineKeyboardButton(text='Отправить сообщение всем', callback_data='SendMessageAll'),
                    types.InlineKeyboardButton(text='Другие функции', callback_data='StartAdmin')
                ]
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(*buttons)
                bot.send_message(message.chat.id,
                                 'Вот функции админа. Хотите посмотреть функции бота, нажмите «Другие функции»',
                                 reply_markup=keyboard)

# РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.N_USER_NAME.value)
def user_name(message):
    name = message.text
    apl[message.chat.id,'name'] = name
    bot.send_message(message.chat.id, "Приятно познакомиться! Теперь укажи свой номер телефона:")
    dbworker.set_state(message.chat.id, config.States.N_USER_NUMBER.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.N_USER_NUMBER.value)
def user_number(message):
    number = message.text
    apl[message.chat.id, 'number'] = number
    cur.execute(f'''CREATE TABLE IF NOT EXISTS p{message.chat.id}
                             (id TEXT,
                             Name TEXT,
                             Number TEXT,
                             Claims INT);''')
    con.commit()
    cur.execute(f'''INSERT INTO p{message.chat.id} (id, Name, Number, Claims) VALUES 
                                           ('{message.chat.id}', '{apl[message.chat.id, 'name']}', '{apl[message.chat.id, 'number']}', '0')''')
    con.commit()
    buttons = [
        types.InlineKeyboardButton(text='Продолжить »', callback_data='Start')
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, 'Крутой номер!!! Рад знакомству. Чтобы увидеть функции бота нажими на кнопку «Продолжить»', reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_START.value)

#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_  NAME AND EDIT_NAME   _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_NAME.value)
def user_name(message):
    name = message.text
    apl[message.chat.id,'name'] = name
    bot.send_message(message.chat.id, "Приятно познакомиться! Теперь укажи, сколько вас человек:")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_AGE.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_EDIT_NAME.value)
def user_edit_name(message):
    name = message.text
    apl[message.chat.id,'name'] = name
    buttons = [
        types.InlineKeyboardButton(text='Изменить', callback_data='Edit'),
        types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, f"Ваша заявка на {apl[message.chat.id, 'event']}:"
                                            f"\n\nИмя: {apl[message.chat.id, 'name']}"
                                            f"\nКоличество человек: {apl[message.chat.id, 'age']}"
                                            f"\nСумма: {apl[message.chat.id, 'sum']}р"
                                            f"\nДата: {apl[message.chat.id, 'date']}"
                                            f"\nНомер телефона: {apl[message.chat.id, 'number']}",
                          reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)


#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_  AGE AND EDIT_AGE   _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_AGE.value)
def user_age(message):
    age = message.text
    apl[message.chat.id, 'age'] = age
    try:
        if int(apl[message.chat.id, 'age']) <= int(apl[message.chat.id, 'people_sum']):
            apl[message.chat.id, 'sum'] = int(apl[message.chat.id, 'age']) * int(apl[message.chat.id, 'price'])
            bot.send_message(message.chat.id, "Отправь мне свой номер телефона, для того чтобы мы с тобой связались:")
            dbworker.set_state(message.chat.id, config.States.S_ENTER_NUMBER.value)

        if int(apl[message.chat.id, 'age']) > int(apl[message.chat.id, 'people_sum']):
            bot.send_message(message.chat.id, f"Количество человек не может превышать {apl[message.chat.id, 'people_sum']}:")
            return
    except:
        bot.send_message(message.chat.id, 'Что-то не так. Введите количество человек заново:')
        return

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_USER_AGE.value)
def user_age(message):
    age = message.text
    apl[message.chat.id, 'age'] = age
    try:
        if int(apl[message.chat.id, 'age']) <= int(apl[message.chat.id, 'people_sum']):
            apl[message.chat.id, 'sum'] = int(apl[message.chat.id, 'age']) * int(apl[message.chat.id, 'price'])
            bot.send_message(message.chat.id, "Напишите дату, когда бы вы хотели поехать на прогулку:")
            dbworker.set_state(message.chat.id, config.States.S_USER_DATE.value)

        if int(apl[message.chat.id, 'age']) > int(apl[message.chat.id, 'people_sum']):
            bot.send_message(message.chat.id, f"Количество человек не может превышать {apl[message.chat.id, 'people_sum']}:")
            return
    except:
        bot.send_message(message.chat.id, 'Что-то не так. Введите количество человек заново:')
        return


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_EDIT_AGE.value)
def user_edit_age(message):
    age = message.text
    apl[message.chat.id, 'age'] = age
    try:
        if int(apl[message.chat.id, 'age']) <= int(apl[message.chat.id, 'people_sum']):
            apl[message.chat.id, 'sum'] = int(apl[message.chat.id, 'age']) * int(apl[message.chat.id, 'price'])
            buttons = [
                types.InlineKeyboardButton(text='Изменить', callback_data='Edit'),
                types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
            ]
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            bot.send_message(message.chat.id, f"Ваша заявка на {apl[message.chat.id, 'event']}:"
                                              f"\n\nИмя: {apl[message.chat.id, 'name']}"
                                              f"\nКоличество человек: {apl[message.chat.id, 'age']}"
                                              f"\nСумма: {apl[message.chat.id, 'sum']}р"
                                              f"\nДата: {apl[message.chat.id, 'date']}"
                                              f"\nНомер телефона: {apl[message.chat.id, 'number']}",
                             reply_markup=keyboard)
            dbworker.set_state(message.chat.id, config.States.S_USER.value)

        if int(apl[message.chat.id, 'age']) > int(apl[message.chat.id, 'people_sum']):
            bot.send_message(message.chat.id, f"Количество человек не может превышать {apl[message.chat.id, 'people_sum']}:")
            return
    except:
        bot.send_message(message.chat.id, 'Что-то не так. Введите количество человек заново:')
        return



#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_  NUMBER AND EDIT_NUMBER   _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_NUMBER.value)
def user_number(message):
    number = message.text
    apl[message.chat.id, 'number'] = number
    bot.send_message(message.chat.id, "Напишите дату, когда бы вы хотели поехать на прогулку:")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_DATE.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_EDIT_NUMBER.value)
def user_edit_number(message):
    number = message.text
    apl[message.chat.id, 'number'] = number
    buttons = [
        types.InlineKeyboardButton(text='Изменить', callback_data='Edit'),
        types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, f"Ваша заявка на {apl[message.chat.id, 'event']}:"
                               f"\n\nИмя: {apl[message.chat.id, 'name']}"
                               f"\nКоличество человек: {apl[message.chat.id, 'age']}"
                               f"\nСумма: {apl[message.chat.id, 'sum']}р"
                               f"\nДата: {apl[message.chat.id, 'date']}"
                               f"\nНомер телефона: {apl[message.chat.id, 'number']}",
                          reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)


#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_  DATE AND EDIT_DATE   _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_DATE.value)
def user_date(message):
    t_happ_int = message.text
    apl[message.chat.id, 'date'] = t_happ_int
    buttons = [
        types.InlineKeyboardButton(text='Изменить', callback_data='Edit'),
        types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, f"Ваша заявка на {apl[message.chat.id, 'event']}:"
                                      f"\n\nИмя: {apl[message.chat.id, 'name']}"
                                      f"\nКоличество человек: {apl[message.chat.id, 'age']}"
                                      f"\nСумма: {apl[message.chat.id, 'sum']}р"
                                      f"\nДата: {apl[message.chat.id, 'date']}"
                                      f"\nНомер телефона: {apl[message.chat.id, 'number']}",
                     reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_USER_DATE.value)
def user_date(message):
    t_happ_int = message.text
    apl[message.chat.id, 'date'] = t_happ_int
    buttons = [
        types.InlineKeyboardButton(text='Изменить', callback_data='Edit'),
        types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, f"Ваша заявка на {apl[message.chat.id, 'event']}:"
                                            f"\n\nИмя: {apl[message.chat.id, 'name']}"
                                            f"\nКоличество человек: {apl[message.chat.id, 'age']}"
                                            f"\nСумма: {apl[message.chat.id, 'sum']}р"
                                            f"\nДата: {apl[message.chat.id, 'date']}"
                                            f"\nНомер телефона: {apl[message.chat.id, 'number']}",
                           reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_EDIT_DATE.value)
def user_edit_date(message):
    t_happ_int = message.text
    apl[message.chat.id, 'date'] = t_happ_int
    buttons = [
        types.InlineKeyboardButton(text='Изменить', callback_data='Edit'),
        types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, f"Ваша заявка на {apl[message.chat.id, 'event']}:"
                                            f"\n\nИмя: {apl[message.chat.id, 'name']}"
                                            f"\nКоличество человек: {apl[message.chat.id, 'age']}"
                                            f"\nСумма: {apl[message.chat.id, 'sum']}р"
                                            f"\nДата: {apl[message.chat.id, 'date']}"
                                            f"\nНомер телефона: {apl[message.chat.id, 'number']}",
                           reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.C_E_NAME.value)
def c_e_name(message):
    name = message.text
    events[message.chat.id, 'name'] = name
    bot.send_message(message.chat.id, "Отправь текст мероприятия:")
    dbworker.set_state(message.chat.id, config.States.C_E_TEXT.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.C_E_TEXT.value)
def c_e_text(message):
    text = message.text
    events[message.chat.id, 'text'] = text
    bot.send_message(message.chat.id, "Какая будет цена билета?")
    dbworker.set_state(message.chat.id, config.States.C_E_PRICE.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.C_E_PRICE.value)
def c_e_price(message):
    price = str(message.text)
    events[message.chat.id, 'price'] = price
    bot.send_message(message.chat.id, "Сколько человек может достигать в одной группе?")
    dbworker.set_state(message.chat.id, config.States.C_E_PEOPLE.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.C_E_PEOPLE.value)
def c_e_people(message):
    people = message.text
    events[message.chat.id, 'people'] = people
    buttons = [
        types.InlineKeyboardButton(text='Прогулки', callback_data='GoSerf')
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    cur.execute(f'''INSERT INTO Events (Name, Text, Price, People) VALUES 
                           ('{events[message.chat.id, 'name']}', '{events[message.chat.id, 'text']}', '{events[message.chat.id, 'price']}', '{events[message.chat.id, 'people']}')''')
    con.commit()
    bot.send_message(message.chat.id, "Событие успешно создано. Чтобы посмотреть нажмите «Прогулки»", reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.ADMIN_SM_USER.value)
def admin_sm_user(message):
    mes = str(message.text)
    apl[message.chat.id, 'mes_user_mes'] = mes
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    b1 = types.InlineKeyboardButton(text='« Вернуться', callback_data='AdminClaims')
    keyboard.add(b1)
    bot.send_message(message.chat.id, "Сообщение отправлено!", reply_markup=keyboard)
    bot.send_message(apl[message.chat.id, 'id_user_mes'], apl[message.chat.id, 'mes_user_mes'])
    dbworker.set_state(message.chat.id, config.States.S_USER.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.EDIT_NAME_EVENT.value)
def edit_name_event(message):
    name = message.text
    events[message.chat.id, 'name'] = name
    cur.execute(f'''UPDATE Events SET Name = '{events[message.chat.id, 'name']}' WHERE Text = '{apl[message.chat.id, 'e_text']}';''')
    con.commit()
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text='Продолжить »', callback_data='AllEvents')
    ]
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, "Название мероприятия изменено!", reply_markup=keyboard)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.EDIT_TEXT_EVENT.value)
def edit_name_event(message):
    text = message.text
    events[message.chat.id, 'text'] = text
    cur.execute(f'''UPDATE Events SET Text = '{events[message.chat.id, 'text']}' WHERE Name = '{apl[message.chat.id, 'e_name']}';''')
    con.commit()
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text='Продолжить »', callback_data='AllEvents')
    ]
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, "Текст мероприятия изменен!", reply_markup=keyboard)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.EDIT_PRICE_EVENT.value)
def edit_name_event(message):
    price = message.text
    events[message.chat.id, 'price'] = price
    cur.execute(f'''UPDATE Events SET Price = {events[message.chat.id, 'price']} WHERE Name = '{apl[message.chat.id, 'e_name']}';''')
    con.commit()
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text='Продолжить »', callback_data='AllEvents')
    ]
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, "Цена билета изменена!", reply_markup=keyboard)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.EDIT_PEOPLE_EVENT.value)
def edit_name_event(message):
    people = message.text
    events[message.chat.id, 'people'] = people
    cur.execute(f'''UPDATE Events SET People = {events[message.chat.id, 'people']} WHERE Name = '{apl[message.chat.id, 'e_name']}';''')
    con.commit()
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text='Продолжить »', callback_data='AllEvents')
    ]
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, "Кол-во человек в группе изменено!", reply_markup=keyboard)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.ADMIN_SEND_ALL.value)
def admin_send_all(message):
    send_all = message.text
    for user in joinedUsers:
        bot.send_message(user, f'{send_all}')
    keyboard = types.InlineKeyboardMarkup()
    b1 = types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
    keyboard.add(b1)
    bot.send_message(message.chat.id, 'Сообщение отправлено', reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)


# CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK
# BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'Start':
        if call.message.chat.id != 1647407069 and call.message.chat.id != 490371324:
            buttons = [
                types.InlineKeyboardButton(text='Прогулки', callback_data='GoSerf'),
                types.InlineKeyboardButton(text='Мои заявки', callback_data='AllClaims'),
                types.InlineKeyboardButton(text='Контакты', callback_data='Contacts'),
                types.InlineKeyboardButton(text='Погода', callback_data='Weather'),
                types.InlineKeyboardButton(text='Как добраться?', callback_data='Map')
            ]
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text='Приветствуем в нашем боте!!!'
                                             '\nЗдесь вы можете оставить заявку на прогулку.'
                                             '\n\nВыберите тот вариант который вам нужен:', reply_markup=keyboard)
        else:
            buttons = [
                types.InlineKeyboardButton(text='Все заявки', callback_data='AdminClaims'),
                types.InlineKeyboardButton(text='Все пользователи', callback_data='AllUsers'),
                types.InlineKeyboardButton(text='Все мероприятия', callback_data='AllEvents'),
                types.InlineKeyboardButton(text='Создать мероприятие', callback_data='CreateEvent'),
                types.InlineKeyboardButton(text='Отправить сообщение всем', callback_data='SendMessageAll'),
                types.InlineKeyboardButton(text='Другие функции', callback_data='StartAdmin')
            ]
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text='Вот функции админа. Хотите посмотреть функции бота, '
                                             'нажмите «Другие функции»', reply_markup=keyboard)

    if call.data == 'StartAdmin':
        buttons = [
            types.InlineKeyboardButton(text='Прогулки', callback_data='GoSerf'),
            types.InlineKeyboardButton(text='Мои заявки', callback_data='AllClaims'),
            types.InlineKeyboardButton(text='Контакты', callback_data='Contacts'),
            types.InlineKeyboardButton(text='Погода', callback_data='Weather'),
            types.InlineKeyboardButton(text='Как добраться?', callback_data='Map'),
            types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Приветствуем в нашем боте!!!'
                                   '\nЗдесь вы можете оставить заявку на прогулку.'
                                   '\n\nВыберите тот вариант который вам нужен:', reply_markup=keyboard)

    if call.data == 'GoSerf':
        postgreSQL_select_Query = "select * from Events"
        cur.execute(postgreSQL_select_Query)
        event = cur.fetchall()
        keyboard = types.InlineKeyboardMarkup()
        for keys in event:
            keyboard.add(types.InlineKeyboardButton(text=f'{keys[0]}', callback_data=f'{keys[0]}'))
        buttons = [
            types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
        ]
        keyboard.add(*buttons)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Вот все мероприятия:', reply_markup=keyboard)

    cur.execute('''SELECT * FROM Events''')
    events_sql = cur.fetchall()
    for key in events_sql:
        if call.data == f'{key[0]}':
            k = types.InlineKeyboardMarkup(row_width=1)
            if str(call.message.chat.id) in adminUsers:
                buttons = [
                    types.InlineKeyboardButton(text='Редактировать', callback_data=f'EditEvent{key[0]}'),
                    types.InlineKeyboardButton(text='Удалить', callback_data=f'DelEvent{key[0]}'),
                    types.InlineKeyboardButton(text='« Вернуться', callback_data='AllEvents')
                ]
                k.add(*buttons)
            else:
                buttons = [
                    types.InlineKeyboardButton(text='Подать заявку', callback_data=f'Claim{key[0]}'),
                    types.InlineKeyboardButton(text='« Вернуться', callback_data='GoSerf')
                ]
                k.add(*buttons)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'{key[0]}'
                                             f'\n\n{key[1]}', reply_markup=k)

        if call.data == f'Claim{key[0]}':
            apl[call.message.chat.id, 'e_event'] = key[0]
            apl[call.message.chat.id, 'e_price'] = key[2]
            apl[call.message.chat.id, 'e_people_sum'] = key[3]
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Для начала давайте оформим вашу заявку."
                                             "\nНапишите как вас зовут:")
            dbworker.set_state(call.message.chat.id, config.States.S_ENTER_NAME.value)

        if call.data == f'EditEvent{key[0]}' and str(call.message.chat.id) in adminUsers:
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            buttons = [
                types.InlineKeyboardButton(text=f"Название: {key[0]}", callback_data=f'EditName{key[0]}'),
                types.InlineKeyboardButton(text=f"Текст: {key[1]}", callback_data=f'EditText{key[0]}'),
                types.InlineKeyboardButton(text=f"Цена: {key[2]}", callback_data=f'EditPrice{key[2]}'),
                types.InlineKeyboardButton(text=f"Кол-во человек: {key[3]}", callback_data=f'EditPeople{key[3]}'),
                types.InlineKeyboardButton(text='« Вернуться', callback_data=f'{key[0]}')
            ]
            keyboard.add(*buttons)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Выберите что хотите изменить:", reply_markup=keyboard)

        if call.data == f'EditName{key[0]}' and str(call.message.chat.id) in adminUsers:
            apl[call.message.chat.id, 'e_text'] = key[1]
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'Текущее название мероприятия:'
                                       f'\n{key[0]}'
                                       f'\n\nВведите новое название мероприятия:')
            dbworker.set_state(call.message.chat.id, config.States.EDIT_NAME_EVENT.value)

        if call.data == f'EditText{key[0]}' and str(call.message.chat.id) in adminUsers:
            apl[call.message.chat.id, 'e_event'] = key[0]
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'Текущий текст мероприятия:'
                                       f'\n{key[1]}'
                                       f'Введите новый текст мероприятия:')
            dbworker.set_state(call.message.chat.id, config.States.EDIT_TEXT_EVENT.value)

        if call.data == f'EditPrice{key[2]}' and str(call.message.chat.id) in adminUsers:
            apl[call.message.chat.id, 'e_event'] = key[0]
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'Текущая цена билета:'
                                       f'\n{key[2]}'
                                       f'Введите новую цену билета:')
            dbworker.set_state(call.message.chat.id, config.States.EDIT_PRICE_EVENT.value)

        if call.data == f'EditPeople{key[3]}' and str(call.message.chat.id) in adminUsers:
            apl[call.message.chat.id, 'e_event'] = key[0]
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'Текущее кол-во человек в группе:'
                                       f'\n{key[3]}'
                                       f'Введите новое кол-во человек в группе:')
            dbworker.set_state(call.message.chat.id, config.States.EDIT_PRICE_EVENT.value)

        if call.data == f'DelEvent{key[0]}' and str(call.message.chat.id) in adminUsers:
            cur.execute(f'''DELETE FROM Events WHERE Name = '{key[0]}';''')
            con.commit()
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            b1 = types.InlineKeyboardButton(text='« Вернуться', callback_data='AllEvents')
            keyboard.add(b1)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Мероприятие удалено!', reply_markup=keyboard)

    if call.data == 'Contacts':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton(text='Instagram', url='https://www.instagram.com/gagra_sup/')
        b2 = types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
        keyboard.add(b1, b2)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='📞 Данил: +79407322932 (WhatsApp, telegram)', reply_markup=keyboard)

    if call.data == 'Weather':
        URL = 'https://yandex.ru/pogoda/10280?utm_source=serp&utm_campaign=wizard&utm_medium=desktop&utm_content=wizard_desktop_main&utm_term=title&lat=43.266731&lon=40.276294'
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.77'
        }
        response = requests.get(URL, headers=HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        digrees = soup.find('span', class_='temp__value temp__value_with-unit').get_text().encode('utf-8').decode('utf-8', 'ignore')
        digrees_water = soup.find('div', class_='temp fact__water-temp').get_text().encode('utf-8').decode('utf-8','ignore')
        wind = soup.find('span', class_='wind-speed').get_text().encode('utf-8').decode('utf-8', 'ignore')

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
        keyboard.add(b1)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'⛅ Температура: {digrees}°C'
                                          f'\n💨 Скорость ветра: {wind} м/с'
                                          f'\n🌊 Температура воды: {digrees_water}°C', reply_markup=keyboard)

    if call.data == 'Map':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton(text='Яндекс.Навигатор', url='https://yandex.ru/maps/10280/gagra/?l=sat&ll=40.257954%2C43.295045&mode=routes&rtext=~43.294975%2C40.258105&rtt=auto&ruri=~&z=18')
        b2 = types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
        keyboard.add(b1, b2)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Отметьте свое местоположение 🚩'
                                   '\n\nВам будет построен маршрут. Наше местоположение уже отмечено)', reply_markup=keyboard)

    if call.data == 'AllClaims':
        cur.execute("SELECT * FROM pg_catalog.pg_tables")
        rows = cur.fetchall()
        rows.sort()
        if f'u{call.message.chat.id}' in str(rows):
            Query = f"select * from u{call.message.chat.id}"
            cur.execute(Query)
            uid = cur.fetchall()
            keyboard = types.InlineKeyboardMarkup()
            for keys in uid:
                keyboard.add(
                    types.InlineKeyboardButton(text=f'{keys[0]} {keys[5]} ({keys[7]})', callback_data=f'{keys[0]}{keys[8]}'))
            buttons = [
                types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
            ]
            keyboard.add(*buttons)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Выберите одну из заявок, чтобы ее посмотреть:', reply_markup=keyboard)
        else:
            buttons = [
                types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
            ]
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(*buttons)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='У вас заявок пока нет. '
                                       'Чтобы подать заявку перейдите во вкладку «Прогулки» и выберите одно из мероприятий',
                                  reply_markup=keyboard)


    cur.execute("SELECT * FROM pg_catalog.pg_tables")
    rows = cur.fetchall()
    rows.sort()
    for row in rows:
        if f'u{call.message.chat.id}' in row[1]:
            Query = f"select * from u{call.message.chat.id}"
            cur.execute(Query)
            uid = cur.fetchall()
            for keys in uid:
                if call.data == f'{keys[0]}{keys[8]}':
                    keyboard = types.InlineKeyboardMarkup()
                    buttons = [
                        types.InlineKeyboardButton(text='Удалить', callback_data=f'DelClaim{keys[0]}{keys[8]}'),
                        types.InlineKeyboardButton(text='« Вернуться', callback_data='AllClaims')
                    ]
                    keyboard.add(*buttons)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text=f'{keys[0]}:'
                                               f'\nСтатус: {keys[7]}'
                                               f'\n\nВаш id: {keys[1]}'
                                               f'\nИмя: {keys[2]}'
                                               f'\nНомер телефона: {keys[6]}'
                                               f'\nКоличество человек:{keys[3]}'
                                               f'\nДата: {keys[5]}'
                                               f'\n\nСумма: {keys[4]}р', reply_markup=keyboard)

                if call.data == f'DelClaim{keys[0]}{keys[8]}':
                    cur.execute(f'''DELETE FROM u{call.message.chat.id} WHERE Num = {keys[8]};''')
                    con.commit()
                    cur.execute(f'''SELECT Claims FROM p{call.message.chat.id} WHERE id = '{call.message.chat.id}';''')
                    row = cur.fetchone()
                    sum_claims = row[0] - 1
                    cur.execute(f'''UPDATE p{call.message.chat.id} SET Claims = {sum_claims} WHERE id = '{call.message.chat.id}';''')
                    con.commit()
                    cur.execute(f'''SELECT Claims FROM p{call.message.chat.id} WHERE id = '{call.message.chat.id}';''')
                    r = cur.fetchone()
                    if r[0] == 0:
                        cur.execute(f"DROP TABLE u{call.message.chat.id}")
                        con.commit()
                    keyboard = types.InlineKeyboardMarkup(row_width=1)
                    b1 = types.InlineKeyboardButton(text='« Вернуться', callback_data='AllClaims')
                    keyboard.add(b1)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text='Заявка удалена', reply_markup=keyboard)


    if call.data == 'Send':
        apl[call.message.chat.id, 'id'] = call.message.chat.id
        cur.execute(f'''CREATE TABLE IF NOT EXISTS u{apl[call.message.chat.id, 'id']}
                         (Event TEXT,
                         id TEXT,
                         Name TEXT,
                         Age INT,
                         Sum INT,
                         Date TEXT,
                         Number TEXT,
                         State TEXT,
                         Num INT);''')
        con.commit()
        cur.execute(f'''INSERT INTO u{apl[call.message.chat.id, 'id']} (Event, id, Name, Age, Sum, Date, Number, State, Num) VALUES 
                                       ('{apl[call.message.chat.id, 'event']}', 
                                        '{apl[call.message.chat.id, 'id']}', 
                                        '{apl[call.message.chat.id, 'name']}', 
                                        '{apl[call.message.chat.id, 'age']}', 
                                        '{apl[call.message.chat.id, 'sum']}', 
                                        '{apl[call.message.chat.id, 'date']}', 
                                        '{apl[call.message.chat.id, 'number']}', 
                                        'Новая',
                                        '{random.randrange(999999999)}');''')
        con.commit()
        cur.execute(f'''SELECT Claims FROM p{call.message.chat.id} WHERE id = '{call.message.chat.id}';''')
        row = cur.fetchone()
        sum_claims = row[0] + 1
        cur.execute(f'''UPDATE p{call.message.chat.id} SET Claims = {sum_claims} WHERE id = '{call.message.chat.id}';''')
        con.commit()
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton(text='Продолжить »', callback_data='Start')
        keyboard.add(b1)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f"\n\n{apl[call.message.chat.id, 'name']}, заявка успешно отправлена!!!) "
                                         f"Ждите, скоро с вами свяжутся) "
                                         f"\nСумма: {apl[call.message.chat.id, 'sum']}р",
                                    reply_markup=keyboard)

        bot.send_message(1647407069, f"Заявка на {apl[call.message.chat.id, 'event']}:"
                                           f"\n\nИмя: {apl[call.message.chat.id, 'name']}"
                                           f"\n\nid: {apl[call.message.chat.id, 'id']}\n"
                                           f"\nКоличество человек: {apl[call.message.chat.id, 'age']}"
                                           f"\nСумма: {apl[call.message.chat.id, 'sum']}р"
                                           f"\nДата: {apl[call.message.chat.id, 'date']}"
                                           f"\nНомер телефона: {apl[call.message.chat.id, 'number']}")

        bot.send_message(490371324, f"Заявка на {apl[call.message.chat.id, 'event']}:"
                                          f"\n\nИмя: {apl[call.message.chat.id, 'name']}"
                                          f"\n\nid: {apl[call.message.chat.id, 'id']}\n"
                                          f"\nКоличество человек: {apl[call.message.chat.id, 'age']}"
                                          f"\nСумма: {apl[call.message.chat.id, 'sum']}р"
                                          f"\nДата: {apl[call.message.chat.id, 'date']}"
                                          f"\nНомер телефона: {apl[call.message.chat.id, 'number']}")

    if call.data == 'Edit':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton(text=f"Имя: {apl[call.message.chat.id, 'name']}", callback_data='Edit-name')
        b2 = types.InlineKeyboardButton(text=f"Количество человек: {apl[call.message.chat.id, 'age']}",
                                        callback_data='Edit-age')
        b3 = types.InlineKeyboardButton(text=f"Номер телефона: {apl[call.message.chat.id, 'number']}",
                                        callback_data='Edit-number')
        b4 = types.InlineKeyboardButton(text=f"Дата: {apl[call.message.chat.id, 'date']}",
                                        callback_data='Edit-date')
        b5 = types.InlineKeyboardButton(text='« Вернуться', callback_data='Claim')
        keyboard.add(b1, b2, b3, b4, b5)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Выберите что хотите изменить:", reply_markup=keyboard)

    if call.data == 'Claim':
        buttons = [
            types.InlineKeyboardButton(text='Изменить', callback_data='Edit'),
            types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        bot.send_message(call.message.chat.id, f"Ваша заявка на {apl[call.message.chat.id, 'event']}:"
                                                     f"\n\nИмя: {apl[call.message.chat.id, 'name']}"
                                                     f"\nКоличество человек: {apl[call.message.chat.id, 'age']}"
                                                     f"\nСумма: {apl[call.message.chat.id, 'sum']}р"
                                                     f"\nДата: {apl[call.message.chat.id, 'date']}"
                                                     f"\nНомер телефона: {apl[call.message.chat.id, 'number']}",
                               reply_markup=keyboard)
        dbworker.set_state(call.message.chat.id, config.States.S_USER.value)

    if call.data == 'Edit-name':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите ваше имя заново:')
        dbworker.set_state(call.message.chat.id, config.States.S_EDIT_NAME.value)

    if call.data == 'Edit-age':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите количество человек заново:')
        dbworker.set_state(call.message.chat.id, config.States.S_EDIT_AGE.value)

    if call.data == 'Edit-number':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите номер заново:')
        dbworker.set_state(call.message.chat.id, config.States.S_EDIT_NUMBER.value)

    if call.data == 'Edit-date':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите дату заново:')
        dbworker.set_state(call.message.chat.id, config.States.S_EDIT_DATE.value)

    if call.data == 'CreateEvent' and str(call.message.chat.id) in adminUsers:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Напишите название события:')
        dbworker.set_state(call.message.chat.id, config.States.C_E_NAME.value)

    if call.data == 'AdminClaims' and str(call.message.chat.id) in adminUsers:
        cur.execute("SELECT * FROM pg_catalog.pg_tables")
        rows = cur.fetchall()
        rows.sort()
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for row in rows:
            if 'u' in row[1] and not 'pg_' in row[1] and not 'sql_' in row[1]:
                user_id = str(row[1]).replace('u', '').strip()
                postgreSQL_select_Query = f"select * from p{user_id}"
                cur.execute(postgreSQL_select_Query)
                user = cur.fetchall()
                for keys in user:
                    keyboard.add(types.InlineKeyboardButton(text=f'{keys[1]} ({keys[3]})', callback_data=f'{row[1]}'))
        buttons = [
            types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
        ]
        keyboard.add(*buttons)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Выберите одну из таблиц пользователей:', reply_markup=keyboard)

    for all_claims_u in rows:
        if 'u' in all_claims_u[1] and not 'pg_' in all_claims_u[1] and not 'sql_' in all_claims_u[1]:
            if str(call.message.chat.id) in adminUsers:
                if call.data == f'{all_claims_u[1]}' and str(call.message.chat.id) in adminUsers:
                    postgreSQL_select_Query = f"select * from {all_claims_u[1]}"
                    cur.execute(postgreSQL_select_Query)
                    v = cur.fetchall()
                    keyboard = types.InlineKeyboardMarkup()
                    for keys in v:
                        keys_user[f'{keys[0]}{keys[8]}', 'num'] = keys[8]
                        keys_user[f'{keys[0]}{keys[8]}', 'date'] = keys[5]
                        keys_user[f'{keys[0]}{keys[8]}', 'event'] = keys[0]
                        keys_user[f'{keys[0]}{keys[8]}', 'id'] = all_claims_u[1]
                        keys_user[f'{keys[0]}{keys[8]}'] = f'{keys[0]}:' \
                                                           f'\nСтатус: {keys[7]}' \
                                                           f'\n\nid: {keys[1]}' \
                                                           f'\nИмя: {keys[2]}' \
                                                           f'\nНомер телефона: {keys[6]}' \
                                                           f'\nКоличество человек:{keys[3]}' \
                                                           f'\nДата: {keys[5]}' \
                                                           f'\n\nСумма: {keys[4]}р'
                        keyboard.add(
                            types.InlineKeyboardButton(text=f'{keys[0]} {keys[5]} ({keys[7]})',
                                                       callback_data=f'{keys[0]}{keys[8]}'))
                    buttons = [
                        types.InlineKeyboardButton(text='« Вернуться', callback_data='AdminClaims')
                    ]
                    keyboard.add(*buttons)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text='Выберите одну из заявок, чтобы ее посмотреть:', reply_markup=keyboard)
    for e in keys_user.keys():
        if call.data == f'{e}' and str(call.message.chat.id) in adminUsers:
            k = types.InlineKeyboardMarkup(row_width=1)
            buttons = [
                types.InlineKeyboardButton(text='Изменить статус', callback_data=f'EditState{e}'),
                types.InlineKeyboardButton(text='Написать пользователю', callback_data=f'SendMessageUser{e}'),
                types.InlineKeyboardButton(text='Удалить заявку', callback_data=f'DeleteClaim{e}'),
                types.InlineKeyboardButton(text='« Вернуться', callback_data='AdminClaims')
            ]
            k.add(*buttons)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'{keys_user[e]}', reply_markup=k)

        if call.data == f'EditState{e}' and str(call.message.chat.id) in adminUsers:
            keyboard = types.InlineKeyboardMarkup()
            buttons = [
                types.InlineKeyboardButton(text='Одобрена', callback_data=f'ElseState{e}'),
                types.InlineKeyboardButton(text='Отклонена', callback_data=f'FalseState{e}'),
                types.InlineKeyboardButton(text='Дата занята', callback_data=f'DateNotFound{e}'),
                types.InlineKeyboardButton(text='« Вернуться', callback_data='AdminClaims')
            ]
            keyboard.add(*buttons)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Выберите один из вариантов редактирования статуса', reply_markup=keyboard)

        if call.data == f'ElseState{e}' and str(call.message.chat.id) in adminUsers:
            user_id = str(keys_user[e, 'id']).replace('u', '').strip()
            cur.execute(f'''UPDATE {keys_user[e, 'id']} SET State = 'Одобрена' WHERE Num = {keys_user[e, 'num']};''')
            con.commit()
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            b1 = types.InlineKeyboardButton(text='« Вернуться', callback_data='AdminClaims')
            keyboard.add(b1)
            k = types.InlineKeyboardMarkup(row_width=1)
            b2 = types.InlineKeyboardButton(text='Продолжить »', callback_data='AllClaims')
            k.add(b2)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Статус успешно изменен', reply_markup=keyboard)
            bot.send_message(user_id, f"Статус заявки: \n«{keys_user[e, 'event']} {keys_user[e, 'date']}» изменен на: "
                                      f"\n«Одобрена». \nЧтобы посмотреть заявки нажмите «Продолжить»", reply_markup=k)

        if call.data == f'FalseState{e}' and str(call.message.chat.id) in adminUsers:
            user_id = str(keys_user[e, 'id']).replace('u', '').strip()
            cur.execute(f'''UPDATE {keys_user[e, 'id']} SET State = 'Отклонена' WHERE Num = {keys_user[e, 'num']};''')
            con.commit()
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            b1 = types.InlineKeyboardButton(text='« Вернуться', callback_data='AdminClaims')
            keyboard.add(b1)
            k = types.InlineKeyboardMarkup(row_width=1)
            b2 = types.InlineKeyboardButton(text='Продолжить »', callback_data='AllClaims')
            k.add(b2)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Статус успешно изменен', reply_markup=keyboard)
            bot.send_message(user_id, f"Статус заявки: \n«{keys_user[e, 'event']} {keys_user[e, 'date']}» изменен на: "
                                      f"\n«Отклонена». \nЧтобы посмотреть заявки нажмите «Продолжить»", reply_markup=k)

        if call.data == f'DateNotFound{e}' and str(call.message.chat.id) in adminUsers:
            user_id = str(keys_user[e, 'id']).replace('u', '').strip()
            cur.execute(f'''UPDATE {keys_user[e, 'id']} SET State = 'Дата занята' WHERE Num = {keys_user[e, 'num']};''')
            con.commit()
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            b1 = types.InlineKeyboardButton(text='« Вернуться', callback_data='AdminClaims')
            keyboard.add(b1)
            k = types.InlineKeyboardMarkup(row_width=1)
            b2 = types.InlineKeyboardButton(text='Продолжить »', callback_data='AllClaims')
            k.add(b2)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Статус успешно изменен', reply_markup=keyboard)
            bot.send_message(user_id, f"Статус заявки: \n«{keys_user[e, 'event']} {keys_user[e, 'date']}» изменен на: "
                                      f"\n«Дата занята». \nЧтобы посмотреть заявки нажмите «Продолжить»", reply_markup=k)


        if call.data == f'SendMessageUser{e}' and str(call.message.chat.id) in adminUsers:
            user_id = str(keys_user[e, 'id']).replace('u', '').strip()
            apl[call.message.chat.id, 'id_user_mes'] = user_id
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Напишите сообшение которое хотите отправить пользователю:')
            dbworker.set_state(call.message.chat.id, config.States.ADMIN_SM_USER.value)

        if call.data == f'DeleteClaim{e}' and str(call.message.chat.id) in adminUsers:
            cur.execute(f'''DELETE FROM {keys_user[e, 'id']} WHERE Num = {keys_user[e, 'num']};''')
            con.commit()
            user_id = str(keys_user[e, 'id']).replace('u', '').strip()
            cur.execute(f'''SELECT Claims FROM p{user_id} WHERE id = '{user_id}';''')
            row = cur.fetchone()
            sum_claims = row[0] - 1
            cur.execute(f'''UPDATE p{user_id} SET Claims = {sum_claims} WHERE id = '{user_id}';''')
            con.commit()
            cur.execute(f'''SELECT Claims FROM p{user_id} WHERE id = '{user_id}';''')
            r = cur.fetchone()
            if r[0] == 0:
                cur.execute(f"DROP TABLE u{user_id}")
                con.commit()
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            b1 = types.InlineKeyboardButton(text='« Вернуться', callback_data='AdminClaims')
            keyboard.add(b1)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Заявка удалена', reply_markup=keyboard)

    if call.data == 'AllEvents' and str(call.message.chat.id) in adminUsers:
        postgreSQL_select_Query = "select * from Events"
        cur.execute(postgreSQL_select_Query)
        event = cur.fetchall()
        keyboard = types.InlineKeyboardMarkup()
        for keys in event:
            keyboard.add(types.InlineKeyboardButton(text=f'{keys[0]}', callback_data=f'{keys[0]}'))
        buttons = [
            types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
        ]
        keyboard.add(*buttons)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Вот все мероприятия:', reply_markup=keyboard)


    if call.data == 'AllUsers' and str(call.message.chat.id) in adminUsers:
        cur.execute("SELECT * FROM pg_catalog.pg_tables")
        rows = cur.fetchall()
        rows.sort()
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for row in rows:
            if 'p' in row[1] and not 'g_' in row[1] and not 'sql_' in row[1] and not 'u' in row[1]:
                user_id = str(row[1]).replace('p', '').strip()
                postgreSQL_select_Query = f"select * from p{user_id}"
                cur.execute(postgreSQL_select_Query)
                user = cur.fetchall()
                for keys in user:
                    keyboard.add(types.InlineKeyboardButton(text=f'{keys[1]} ({keys[3]})', callback_data=f'{row[1]}'))
        buttons = [
            types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
        ]
        keyboard.add(*buttons)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Выберите одну из таблиц пользователей:', reply_markup=keyboard)

    for useru in rows:
        if 'p' in useru[1] and not 'g_' in useru[1] and not 'sql_' in useru[1] and not 'u' in useru[1]:
            if call.data == f'{useru[1]}' and str(call.message.chat.id) in adminUsers:
                user_id = str(useru[1]).replace('p', '').strip()
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                buttons = [
                    types.InlineKeyboardButton(text='Написать пользователю', callback_data=f'SendMessageUser{useru[1]}'),
                    types.InlineKeyboardButton(text='Удалить пользователя', callback_data=f'DeleteUser{useru[1]}'),
                    types.InlineKeyboardButton(text='« Вернуться', callback_data='AllUsers')
                ]
                keyboard.add(*buttons)
                user_sql = f"select * from p{user_id}"
                cur.execute(user_sql)
                user_conn = cur.fetchall()
                user = {}
                for user_acc in user_conn:
                    user[call.message.chat.id, 'name'] = user_acc[1]
                    user[call.message.chat.id, 'tel'] = user_acc[2]
                    user[call.message.chat.id, 'claims'] = user_acc[3]
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"Имя пользователя: {user[call.message.chat.id, 'name']}"
                                           f"\n\nТелефон: {user[call.message.chat.id, 'tel']}"
                                           f"\n\nКол-во заявок: {user[call.message.chat.id, 'claims']}", reply_markup=keyboard)

            if call.data == f'SendMessageUser{useru[1]}' and str(call.message.chat.id) in adminUsers:
                user_id = str(useru[1]).replace('p', '').strip()
                apl[call.message.chat.id, 'id_user_mes'] = user_id
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Напишите сообшение которое хотите отправить пользователю:')
                dbworker.set_state(call.message.chat.id, config.States.ADMIN_SM_USER.value)

            if call.data == f'DeleteUser{useru[1]}' and str(call.message.chat.id) in adminUsers:
                user_id = str(useru[1]).replace('p', '').strip()
                cur.execute(f"DROP TABLE {useru[1]}")
                con.commit()
                joinedFile = open('joined.txt', 'r')
                lines = joinedFile.readlines()
                joinedFile.close()
                joinedFile = open('joined.txt', 'w')
                for line in lines:
                    if line != f'{user_id}' + '\n':
                        joinedFile.write(line)
                joinedFile.close()
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                b1 = types.InlineKeyboardButton(text='« Вернуться', callback_data='AllUsers')
                keyboard.add(b1)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Пользователь удален', reply_markup=keyboard)

    if call.data == 'SendMessageAll':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Напишите что хотите отправить пользователям бота:')
        dbworker.set_state(call.message.chat.id, config.States.ADMIN_SEND_ALL.value)

#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_  TYPE:TEXT  _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
@bot.message_handler(content_types=['text'])
def saw(message):
    msg = message.text

    if msg == 'Мой id':
        bot.send_message(message.chat.id, message.chat.id)

bot.polling(none_stop = True, interval = 0)