import logging
import dbworker
import psycopg2
import requests
import config
from bs4 import BeautifulSoup
from config import TOKEN
from aiogram import Bot, Dispatcher, executor, types

bot = Bot(token=TOKEN)
db = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

con = psycopg2.connect(
  database="GagraSup",
  user="postgres",
  password="gagrasup",
  host="127.0.0.1",
  port="5432"
)

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

joinedFile = open('joined.txt', 'r')
joinedUsers = set()
for line in joinedFile:
    joinedUsers.add(line.strip())
joinedFile.close()

@db.message_handler(commands="start")
async def start(message: types.Message):
    if not str(message.chat.id) in joinedUsers:
        if message.chat.id != 1647407069 and message.chat.id != 490371324:
            joinedFile = open('joined.txt', 'a')
            joinedFile.write(str(message.chat.id) + '\n')
            joinedUsers.add(message.chat.id)
    if message.chat.id != 1647407069 and message.chat.id != 490371324:
        state = dbworker.get_current_state(message.chat.id)
        if state == config.States.S_USER.value:
            buttons = [
                types.InlineKeyboardButton(text="Прогулки", callback_data="GoSerf"),
                types.InlineKeyboardButton(text="Мои заявки", callback_data="AllClaims"),
                types.InlineKeyboardButton(text="Контакты", callback_data="Contacts"),
                types.InlineKeyboardButton(text='Погода', callback_data='Weather'),
                types.InlineKeyboardButton(text='Как добраться?', callback_data='Map')
            ]
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            await message.answer('Приветствуем в нашем боте!!!'
                                 '\nЗдесь вы можете оставить заявку на прогулку.'
                                 '\n\nВыберите тот вариант который вам нужен:', reply_markup=keyboard)
        else:
            dbworker.set_state(message.chat.id, config.States.S_START.value)
            buttons = [
                types.InlineKeyboardButton(text="Прогулки", callback_data="GoSerf"),
                types.InlineKeyboardButton(text="Мои заявки", callback_data="AllClaims"),
                types.InlineKeyboardButton(text="Контакты", callback_data="Contacts"),
                types.InlineKeyboardButton(text='Погода', callback_data='Weather'),
                types.InlineKeyboardButton(text='Как добраться?', callback_data='Map')
            ]
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            await message.answer('Приветствуем в нашем боте!!!'
                                 '\nЗдесь вы можете оставить заявку на прогулку.'
                                 '\n\nВыберите тот вариант который вам нужен:', reply_markup=keyboard)
    else:
        state = dbworker.get_current_state(message.chat.id)
        if state == config.States.S_USER.value:
            buttons = [
                types.InlineKeyboardButton(text='Все заявки', callback_data='AdminClaims'),
                types.InlineKeyboardButton(text='Создать событие', callback_data='CreateEvent'),
                types.InlineKeyboardButton(text='Отправить сообщение', callback_data='SendMessage'),
                types.InlineKeyboardButton(text='Другие функции', callback_data='StartAdmin')
            ]
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            await message.answer('Вот функции админа. Хотите посмотреть функции бота, нажмите «Другие функции»', reply_markup=keyboard)
        else:
            dbworker.set_state(message.chat.id, config.States.S_START.value)
            buttons = [
                types.InlineKeyboardButton(text='Все заявки', callback_data='AdminClaims'),
                types.InlineKeyboardButton(text='Создать событие', callback_data='CreateEvent'),
                types.InlineKeyboardButton(text='Отправить сообщение', callback_data='SendMessage'),
                types.InlineKeyboardButton(text='Другие функции', callback_data='StartAdmin')
            ]
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            await message.answer('Вот функции админа. Хотите посмотреть функции бота, нажмите «Другие функции»',
                                 reply_markup=keyboard)


# _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_  NAME AND EDIT_NAME   _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
@db.message_handler(lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_NAME.value)
async def user_name(message: types.Message):
    name = message.text
    apl[message.chat.id, 'name'] = name
    await bot.send_message(message.chat.id, "Приятно познакомиться! Теперь укажи, сколько вас человек:")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_AGE.value)


@db.message_handler(lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_EDIT_NAME.value)
async def user_edit_name(message: types.Message):
    name = message.text
    apl[message.chat.id, 'name'] = name
    buttons = [
        types.InlineKeyboardButton(text='Изменить', callback_data='Edit'),
        types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await bot.send_message(message.chat.id, f"Ваша заявка на {apl[message.chat.id, 'event']}:"
                                            f"\n\nИмя: {apl[message.chat.id, 'name']}"
                                            f"\nКоличество человек: {apl[message.chat.id, 'age']}"
                                            f"\nСумма: {apl[message.chat.id, 'sum']}р"
                                            f"\nДата: {apl[message.chat.id, 'date']}"
                                            f"\nНомер телефона: {apl[message.chat.id, 'number']}",
                           reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)

#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_  AGE AND EDIT_AGE   _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
@db.message_handler(lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_AGE.value)
async def user_age(message: types.Message):
    age = message.text
    apl[message.chat.id, 'age'] = age
    try:
        if int(apl[message.chat.id, 'age']) <= int(apl[message.chat.id, 'people_sum']):
            apl[message.chat.id, 'sum'] = int(apl[message.chat.id, 'age']) * int(apl[message.chat.id, 'price'])
            await bot.send_message(message.chat.id, "Отправь мне свой номер телефона, для того чтобы мы с тобой связались:")
            dbworker.set_state(message.chat.id, config.States.S_ENTER_NUMBER.value)

        if int(apl[message.chat.id, 'age']) > int(apl[message.chat.id, 'people_sum']):
            await bot.send_message(message.chat.id, f"Количество человек не может превышать {apl[message.chat.id, 'people_sum']}:")
            return
    except:
        await bot.send_message(message.chat.id, 'Что-то не так. Введите количество человек заново:')
        return

@db.message_handler(lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_USER_AGE.value)
async def user_age(message: types.Message):
    age = message.text
    apl[message.chat.id, 'age'] = age
    try:
        if int(apl[message.chat.id, 'age']) <= int(apl[message.chat.id, 'people_sum']):
            apl[message.chat.id, 'sum'] = int(apl[message.chat.id, 'age']) * int(apl[message.chat.id, 'price'])
            await bot.send_message(message.chat.id,
                                   "Отправь мне свой номер телефона, для того чтобы мы с тобой связались:")
            dbworker.set_state(message.chat.id, config.States.S_USER_DATE.value)

        if int(apl[message.chat.id, 'age']) > int(apl[message.chat.id, 'people_sum']):
            await bot.send_message(message.chat.id,
                                   f"Количество человек не может превышать {apl[message.chat.id, 'people_sum']}:")
            return
    except:
        await bot.send_message(message.chat.id, 'Что-то не так. Введите количество человек заново:')
        return


@db.message_handler(lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_EDIT_AGE.value)
async def user_edit_age(message: types.Message):
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
            await bot.send_message(message.chat.id, f"Ваша заявка на {apl[message.chat.id, 'event']}:"
                                              f"\n\nИмя: {apl[message.chat.id, 'name']}"
                                              f"\nКоличество человек: {apl[message.chat.id, 'age']}"
                                              f"\nСумма: {apl[message.chat.id, 'sum']}р"
                                              f"\nДата: {apl[message.chat.id, 'date']}"
                                              f"\nНомер телефона: {apl[message.chat.id, 'number']}",
                             reply_markup=keyboard)
            dbworker.set_state(message.chat.id, config.States.S_USER.value)

        if int(apl[message.chat.id, 'age']) > int(apl[message.chat.id, 'people_sum']):
            await bot.send_message(message.chat.id, f"Количество человек не может превышать {apl[message.chat.id, 'people_sum']}:")
            return
    except:
        await bot.send_message(message.chat.id, 'Что-то не так. Введите количество человек заново:')
        return

#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_  NUMBER AND EDIT_NUMBER   _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
@db.message_handler(lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_NUMBER.value)
async def user_number(message: types.Message):
    number = message.text
    apl[message.chat.id, 'number'] = number
    await bot.send_message(message.chat.id, "Напишите дату, когда бы вы хотели поехать на прогулку:")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_DATE.value)

@db.message_handler(lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_EDIT_NUMBER.value)
async def user_edit_number(message: types.Message):
    number = message.text
    apl[message.chat.id, 'number'] = number
    buttons = [
        types.InlineKeyboardButton(text='Изменить', callback_data='Edit'),
        types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await bot.send_message(message.chat.id, f"Ваша заявка на {apl[message.chat.id, 'event']}:"
                               f"\n\nИмя: {apl[message.chat.id, 'name']}"
                               f"\nКоличество человек: {apl[message.chat.id, 'age']}"
                               f"\nСумма: {apl[message.chat.id, 'sum']}р"
                               f"\nДата: {apl[message.chat.id, 'date']}"
                               f"\nНомер телефона: {apl[message.chat.id, 'number']}",
                          reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)

#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_  DATE AND EDIT_DATE   _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
@db.message_handler(lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_DATE.value)
async def user_date(message: types.Message):
    t_happ_int = message.text
    apl[message.chat.id, 'date'] = t_happ_int
    buttons = [
        types.InlineKeyboardButton(text='Изменить', callback_data='Edit'),
        types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await bot.send_message(message.chat.id, f"Ваша заявка на {apl[message.chat.id, 'event']}:"
                                            f"\n\nИмя: {apl[message.chat.id, 'name']}"
                                            f"\nКоличество человек: {apl[message.chat.id, 'age']}"
                                            f"\nСумма: {apl[message.chat.id, 'sum']}р"
                                            f"\nДата: {apl[message.chat.id, 'date']}"
                                            f"\nНомер телефона: {apl[message.chat.id, 'number']}",
                           reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)

@db.message_handler(lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_USER_DATE.value)
async def user_date(message: types.Message):
    t_happ_int = message.text
    apl[message.chat.id, 'date'] = t_happ_int
    buttons = [
        types.InlineKeyboardButton(text='Изменить', callback_data='Edit'),
        types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await bot.send_message(message.chat.id, f"Ваша заявка на {apl[message.chat.id, 'event']}:"
                                            f"\n\nИмя: {apl[message.chat.id, 'name']}"
                                            f"\nКоличество человек: {apl[message.chat.id, 'age']}"
                                            f"\nСумма: {apl[message.chat.id, 'sum']}р"
                                            f"\nДата: {apl[message.chat.id, 'date']}"
                                            f"\nНомер телефона: {apl[message.chat.id, 'number']}",
                           reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)

@db.message_handler(lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_EDIT_DATE.value)
async def user_edit_date(message: types.Message):
    t_happ_int = message.text
    apl[message.chat.id, 'date'] = t_happ_int
    buttons = [
        types.InlineKeyboardButton(text='Изменить', callback_data='Edit'),
        types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await bot.send_message(message.chat.id, f"Ваша заявка на {apl[message.chat.id, 'event']}:"
                                            f"\n\nИмя: {apl[message.chat.id, 'name']}"
                                            f"\nКоличество человек: {apl[message.chat.id, 'age']}"
                                            f"\nСумма: {apl[message.chat.id, 'sum']}р"
                                            f"\nДата: {apl[message.chat.id, 'date']}"
                                            f"\nНомер телефона: {apl[message.chat.id, 'number']}",
                           reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)

@db.message_handler(lambda message: dbworker.get_current_state(message.chat.id) == config.States.C_E_NAME.value)
async def c_e_name(message: types.Message):
    name = message.text
    events[message.chat.id, 'name'] = name
    await bot.send_message(message.chat.id, "Отправь текст мероприятия:")
    dbworker.set_state(message.chat.id, config.States.C_E_TEXT.value)

@db.message_handler(lambda message: dbworker.get_current_state(message.chat.id) == config.States.C_E_TEXT.value)
async def c_e_text(message: types.Message):
    text = message.text
    events[message.chat.id, 'text'] = text
    await bot.send_message(message.chat.id, "Какая будет цена билета?")
    dbworker.set_state(message.chat.id, config.States.C_E_PRICE.value)

@db.message_handler(lambda message: dbworker.get_current_state(message.chat.id) == config.States.C_E_PRICE.value)
async def c_e_price(message: types.Message):
    price = str(message.text)
    events[message.chat.id, 'price'] = price
    await bot.send_message(message.chat.id, "Сколько человек может достигать в одной группе?")
    dbworker.set_state(message.chat.id, config.States.C_E_PEOPLE.value)

@db.message_handler(lambda message: dbworker.get_current_state(message.chat.id) == config.States.C_E_PEOPLE.value)
async def c_e_people(message: types.Message):
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
    await bot.send_message(message.chat.id, "Событие успешно создано. Чтобы посмотреть нажмите «Прогулки»", reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)



# CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK
# BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL BACK CALL
@db.callback_query_handler(lambda c: c.data == "Start")
async def start(call: types.CallbackQuery):
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
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Приветствуем в нашем боте!!!'
                                     '\nЗдесь вы можете оставить заявку на прогулку.'
                                     '\n\nВыберите тот вариант который вам нужен:', reply_markup=keyboard)
    else:
        buttons = [
            types.InlineKeyboardButton(text='Все заявки', callback_data='AdminClaims'),
            types.InlineKeyboardButton(text='Создать событие', callback_data='CreateEvent'),
            types.InlineKeyboardButton(text='Отправить сообщение', callback_data='SendMessage'),
            types.InlineKeyboardButton(text='Другие функции', callback_data='StartAdmin')
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Вот функции админа. Хотите посмотреть функции бота, '
                                     'нажмите «Другие функции»', reply_markup=keyboard)

@db.callback_query_handler(lambda c: c.data == "StartAdmin")
async def start_admin(call: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    b1 = types.InlineKeyboardButton(text='Прогулки', callback_data='GoSerf')
    b2 = types.InlineKeyboardButton(text='Мои заявки', callback_data='AllClaims')
    b3 = types.InlineKeyboardButton(text='Контакты', callback_data='Contacts')
    b4 = types.InlineKeyboardButton(text='Погода', callback_data='Weather')
    b5 = types.InlineKeyboardButton(text='Как добраться?', callback_data='Map')
    b6 = types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
    keyboard.add(b1, b2, b3, b4, b5, b6)
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Приветствуем в нашем боте!!!'
                               '\nЗдесь вы можете оставить заявку на прогулку.'
                               '\n\nВыберите тот вариант который вам нужен:', reply_markup=keyboard)

@db.callback_query_handler(lambda c: c.data=="GoSerf")
async def go_serf(call: types.CallbackQuery):
    postgreSQL_select_Query = "select * from Events"
    cur.execute(postgreSQL_select_Query)
    event = cur.fetchall()
    keyboard = types.InlineKeyboardMarkup()
    for keys in event:
        print(keys[0], '\n', keys[1], '\n', keys[2], '\n', keys[3])
        keyboard.add(types.InlineKeyboardButton(text=f'{keys[0]}', callback_data=f'{keys[0]}'))
    buttons = [
        types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
    ]
    keyboard.add(*buttons)
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text='Вот все мероприятия:', reply_markup=keyboard)

cur.execute('''SELECT * FROM Events''')
rows = cur.fetchall()
for key in rows:
    @db.callback_query_handler(lambda c: c.data == f"{key[0]}")
    async def keys_k(call: types.CallbackQuery):
        k = types.InlineKeyboardMarkup()
        buttons = [
            types.InlineKeyboardButton(text='Подать заявку', callback_data=f'Claim{key[0]}'),
            types.InlineKeyboardButton(text='« Вернуться', callback_data='GoSerf')
        ]
        k.add(*buttons)
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{key[0]}'
                                         f'\n{key[1]}', reply_markup=k)

    @db.callback_query_handler(lambda c: c.data == f'Claim{key[0]}')
    async def claim_keys(call: types.CallbackQuery):
        apl[call.message.chat.id, 'event'] = key[0]
        apl[call.message.chat.id, 'price'] = key[2]
        apl[call.message.chat.id, 'people_sum'] = key[3]
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Для начала давайте оформим вашу заявку."
                                         "\nНапишите как вас зовут:")
        dbworker.set_state(call.message.chat.id, config.States.S_ENTER_NAME.value)


@db.callback_query_handler(lambda c: c.data=="AllClaims")
async def all_claims(call: types.CallbackQuery):
    try:
        postgreSQL_select_Query = f"select * from u{call.message.chat.id}"
        cur.execute(postgreSQL_select_Query)
        event = cur.fetchall()
        keyboard = types.InlineKeyboardMarkup()
        for keys in event:
            keyboard.add(types.InlineKeyboardButton(text=f'{keys[0]} ({keys[5]})', callback_data=f'{keys[0]}{keys[5]}'))
        buttons = [
            types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
        ]
        keyboard.add(*buttons)
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Выберите одну из заявок, чтобы ее посмотреть:', reply_markup=keyboard)
        for keys in event:
            @db.callback_query_handler(lambda c: c.data == f'{keys[0]}{keys[5]}')
            async def keys_keys(call: types.CallbackQuery):
                k = types.InlineKeyboardMarkup()
                buttons = [
                    types.InlineKeyboardButton(text='« Вернуться', callback_data='AllClaims')
                ]
                k.add(*buttons)
                await bot.answer_callback_query(call.id)
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=f'{keys[0]}:'
                                                 f'\n\nВаш id: {keys[1]}'
                                                 f'\nИмя: {keys[2]}'
                                                 f'\nНомер телефона: {keys[6]}'
                                                 f'\nКоличество человек:{keys[3]}'
                                                 f'\nДата: {keys[5]}'
                                                 f'\n\nСумма: {keys[4]}', reply_markup=k)

    except:
        buttons = [
            types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
        ]
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*buttons)
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='У вас заявок пока нет. '
                                         'Чтобы подать заявку перейдите во вкладку «Прогулки» и выберите одно из мероприятий',
                                    reply_markup=keyboard)

@db.callback_query_handler(lambda c: c.data=="Contacts")
async def contacts(call: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    b1 = types.InlineKeyboardButton(text='Instagram', url='https://www.instagram.com/gagra_sup/')
    b2 = types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
    keyboard.add(b1, b2)
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='📞 Данил: +79407322932 (WhatsApp, telegram)', reply_markup=keyboard)

@db.callback_query_handler(lambda c: c.data=="Weather")
async def weather(call: types.CallbackQuery):
    URL = 'https://yandex.ru/pogoda/10280?utm_source=serp&utm_campaign=wizard&utm_medium=desktop&utm_content=wizard_desktop_main&utm_term=title&lat=43.266731&lon=40.276294'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.77'
    }
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    digrees = soup.find('span', class_='temp__value temp__value_with-unit').get_text().encode('utf-8').decode('utf-8',
                                                                                                              'ignore')
    digrees_water = soup.find('div', class_='temp fact__water-temp').get_text().encode('utf-8').decode('utf-8',
                                                                                                       'ignore')
    wind = soup.find('span', class_='wind-speed').get_text().encode('utf-8').decode('utf-8', 'ignore')

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    b1 = types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
    keyboard.add(b1)
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f'⛅ Температура: {digrees}°C'
                               f'\n💨 Скорость ветра: {wind} м/с'
                               f'\n🌊 Температура воды: {digrees_water}°C', reply_markup=keyboard)

@db.callback_query_handler(lambda c: c.data=="Map")
async def map(call: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    b1 = types.InlineKeyboardButton(text='Яндекс.Навигатор',
                                    url='https://yandex.ru/maps/10280/gagra/?l=sat&ll=40.257954%2C43.295045&mode=routes&rtext=~43.294975%2C40.258105&rtt=auto&ruri=~&z=18')
    b2 = types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
    keyboard.add(b1, b2)
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Отметьте свое местоположение 🚩'
                               '\n\nВам будет построен маршрут. Наше местоположение уже отмечено)',
                          reply_markup=keyboard)

@db.callback_query_handler(lambda c: c.data == "Send")
async def send(call: types.CallbackQuery):
    apl[call.message.chat.id, 'id'] = call.message.chat.id
    cur.execute(f'''CREATE TABLE IF NOT EXISTS u{apl[call.message.chat.id, 'id']}
                 (Event TEXT,
                 id TEXT,
                 Name TEXT,
                 Age INT,
                 Sum INT,
                 Date TEXT,
                 Number TEXT);''')
    con.commit()
    cur.execute(f'''INSERT INTO u{apl[call.message.chat.id, 'id']} (Event, id, Name, Age, Sum, Date, Number) VALUES 
                               ('{apl[call.message.chat.id, 'event']}', '{apl[call.message.chat.id, 'id']}', '{apl[call.message.chat.id, 'name']}', '{apl[call.message.chat.id, 'age']}', '{apl[call.message.chat.id, 'sum']}', '{apl[call.message.chat.id, 'date']}', '{apl[call.message.chat.id, 'number']}')''')
    con.commit()
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    b1 = types.InlineKeyboardButton(text='Продолжить »', callback_data='Start')
    keyboard.add(b1)
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"\n\n{apl[call.message.chat.id, 'name']}, заявка успешно отправлена!!!) "
                               f"Ждите, скоро с вами свяжутся) "
                               f"\nСумма: {apl[call.message.chat.id, 'sum']}р",
                          reply_markup=keyboard)

    await bot.send_message(1647407069, f"Заявка на {apl[call.message.chat.id, 'event']}:"
                                 f"\n\nИмя: {apl[call.message.chat.id, 'name']}"
                                 f"\n\nid: {apl[call.message.chat.id, 'id']}\n"
                                 f"\nКоличество человек: {apl[call.message.chat.id, 'age']}"
                                 f"\nСумма: {apl[call.message.chat.id, 'sum']}р"
                                 f"\nДата: {apl[call.message.chat.id, 'date']}"
                                 f"\nНомер телефона: {apl[call.message.chat.id, 'number']}")

    await bot.send_message(490371324, f"Заявка на {apl[call.message.chat.id, 'event']}:"
                                f"\n\nИмя: {apl[call.message.chat.id, 'name']}"
                                f"\n\nid: {apl[call.message.chat.id, 'id']}\n"
                                f"\nКоличество человек: {apl[call.message.chat.id, 'age']}"
                                f"\nСумма: {apl[call.message.chat.id, 'sum']}р"
                                f"\nДата: {apl[call.message.chat.id, 'date']}"
                                f"\nНомер телефона: {apl[call.message.chat.id, 'number']}")

@db.callback_query_handler(lambda c: c.data == "Edit")
async def edit(call: types.CallbackQuery):
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
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Выберите что хотите изменить:", reply_markup=keyboard)

@db.callback_query_handler(lambda c: c.data == "Claim")
async def claim(call: types.CallbackQuery):
    buttons = [
        types.InlineKeyboardButton(text='Изменить', callback_data='Edit'),
        types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await bot.send_message(call.message.chat.id, f"Ваша заявка на {apl[call.message.chat.id, 'event']}:"
                                            f"\n\nИмя: {apl[call.message.chat.id, 'name']}"
                                            f"\nКоличество человек: {apl[call.message.chat.id, 'age']}"
                                            f"\nСумма: {apl[call.message.chat.id, 'sum']}р"
                                            f"\nДата: {apl[call.message.chat.id, 'date']}"
                                            f"\nНомер телефона: {apl[call.message.chat.id, 'number']}",
                           reply_markup=keyboard)
    dbworker.set_state(call.message.chat.id, config.States.S_USER.value)

@db.callback_query_handler(lambda c: c.data == "Edit-name")
async def edit_name(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Введите ваше имя заново:')
    dbworker.set_state(call.message.chat.id, config.States.S_EDIT_NAME.value)

@db.callback_query_handler(lambda c: c.data == "Edit-age")
async def edit_age(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Введите количество человек заново:')
    dbworker.set_state(call.message.chat.id, config.States.S_EDIT_AGE.value)

@db.callback_query_handler(lambda c: c.data == "Edit-number")
async def edit_number(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите номер заново:')
    dbworker.set_state(call.message.chat.id, config.States.S_EDIT_NUMBER.value)

@db.callback_query_handler(lambda c: c.data == "Edit-date")
async def edit_date(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите дату заново:')
    dbworker.set_state(call.message.chat.id, config.States.S_EDIT_DATE.value)


@db.callback_query_handler(lambda c: c.data == "CreateEvent")
async def create_event(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text='Напишите название события:')
    dbworker.set_state(call.message.chat.id, config.States.C_E_NAME.value)

@db.callback_query_handler(lambda c: c.data == "AdminClaims")
async def admin_claims(call: types.CallbackQuery):
    cur.execute("SELECT * FROM pg_catalog.pg_tables")
    rows = cur.fetchall()
    rows.sort()
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for row in rows:
        if 'u' in row[1] and not 'pg_' in row[1] and not 'sql_' in row[1]:
            keyboard.add(types.InlineKeyboardButton(text=f'{row[1]}', callback_data=f'{row[1]}'))
    buttons = [
        types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
    ]
    keyboard.add(*buttons)
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text='Выберите одну из таблиц пользователей:', reply_markup=keyboard)

    @db.callback_query_handler(lambda c: c.data == f"{row[1]}")
    async def all_claims(call: types.CallbackQuery):
        postgreSQL_select_Query = f"select * from {row[1]}"
        cur.execute(postgreSQL_select_Query)
        global event
        event = cur.fetchall()
        keyboard = types.InlineKeyboardMarkup()
        for keys in event:
            keyboard.add(
                types.InlineKeyboardButton(text=f'{keys[0]} ({keys[5]})', callback_data=f'{keys[0]}{keys[5]}'))
        buttons = [
            types.InlineKeyboardButton(text='« Вернуться', callback_data='AdminClaims')
        ]
        keyboard.add(*buttons)
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Выберите одну из заявок, чтобы ее посмотреть:', reply_markup=keyboard)

        @db.callback_query_handler(lambda c: c.data == f'{keys[0]}{keys[5]}')
        async def keys_keys(call: types.CallbackQuery):
            k = types.InlineKeyboardMarkup()
            buttons = [
                types.InlineKeyboardButton(text='« Вернуться', callback_data='AdminClaims')
            ]
            k.add(*buttons)
            await bot.answer_callback_query(call.id)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'{keys[0]}:'
                                             f'\n\nВаш id: {keys[1]}'
                                             f'\nИмя: {keys[2]}'
                                             f'\nНомер телефона: {keys[6]}'
                                             f'\nКоличество человек:{keys[3]}'
                                             f'\nДата: {keys[5]}'
                                             f'\n\nСумма: {keys[4]}', reply_markup=k)

if __name__ == "__main__":
    executor.start_polling(db, skip_updates=True)