import telebot
import requests
import dbworker
import config
import datetime
from datetime import datetime as DT
from telebot import types
from config import TOKEN
from bs4 import BeautifulSoup

dt_fmt = '%d.%m'
now = datetime.datetime.now()
apl = {}

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    state = dbworker.get_current_state(message.chat.id)
    if state == config.States.S_USER.value:
        id = message.chat.id
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton(text='Прогулки', callback_data='GoSerf')
        b2 = types.InlineKeyboardButton(text='Контакты', callback_data='Contacts')
        b3 = types.InlineKeyboardButton(text='Погода', callback_data='Weather')
        b4 = types.InlineKeyboardButton(text='Как добраться?', callback_data='Map')
        keyboard.add(b1, b2, b3, b4)
        bot.send_message(id, 'Приветствуем в нашем боте!!!'
                             '\nЗдесь вы можете оставить заявку на прогулку.'
                             '\n\nВыберите тот вариант который вам нужен:', reply_markup=keyboard)
    else:
        dbworker.set_state(message.chat.id, config.States.S_START.value)
        id = message.chat.id
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton(text='Прогулки', callback_data='GoSerf')
        b2 = types.InlineKeyboardButton(text='Контакты', callback_data='Contacts')
        b3 = types.InlineKeyboardButton(text='Погода', callback_data='Weather')
        b4 = types.InlineKeyboardButton(text='Как добраться?', callback_data='Map')
        keyboard.add(b1, b2, b3, b4)
        bot.send_message(id, 'Приветствуем в нашем боте!!!'
                             '\nЗдесь вы можете оставить заявку на прогулку.'
                             '\n\nВыберите тот вариант который вам нужен:', reply_markup=keyboard)


#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_  NAME AND EDIT_NAME   _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_NAME.value)
def user_name(message):
    # В случае с именем не будем ничего проверять, пусть хоть "25671", хоть Евкакий
    name = message.text
    apl[message.chat.id,'name'] = name
    bot.send_message(message.chat.id, "Приятно познакомиться! Теперь укажи, сколько вас человек:")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_AGE.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_EDIT_NAME.value)
def user_edit_name(message):
    # В случае с именем не будем ничего проверять, пусть хоть "25671", хоть Евкакий
    name = message.text
    apl[message.chat.id,'name'] = name
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    b1 = types.InlineKeyboardButton(text='Изменить', callback_data='Edit')
    b2 = types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
    keyboard.add(b1, b2)
    bot.send_message(message.chat.id, f"Ваша заявка:"
                               f"\n\nИмя: {apl[message.chat.id, 'name']}"
                               f"\nКоличество человек: {apl[message.chat.id, 'age']}"
                               f"\nСумма: {apl[message.chat.id, 'sum']}р"
                               f"\nДата: {apl[message.chat.id, 'date']} {now.year}"
                               f"\nВремя: {apl[message.chat.id, 'time']}"
                               f"\nНомер телефона: {apl[message.chat.id, 'number']}",
                          reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)


#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_  AGE AND EDIT_AGE   _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_AGE.value)
def user_age(message):
    age = message.text
    apl[message.chat.id, 'age'] = age
    if int(apl[message.chat.id, 'age']) <= 4:
        bot.send_message(message.chat.id, "Отправь мне свой номер телефона, для того чтобы мы с тобой связались:")
        dbworker.set_state(message.chat.id, config.States.S_ENTER_NUMBER.value)

    if int(apl[message.chat.id, 'age']) > 4:
        bot.send_message(message.chat.id, "Количество человек не может превышать 4:")
        return

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_USER_AGE.value)
def user_age(message):
    age = message.text
    apl[message.chat.id, 'age'] = age
    if int(apl[message.chat.id, 'age']) <= 4:
        bot.send_message(message.chat.id, "Напишите дату, когда бы вы хотели поехать на прогулку:")
        dbworker.set_state(message.chat.id, config.States.S_USER_DATE.value)

    if int(apl[message.chat.id, 'age']) > 4:
        bot.send_message(message.chat.id, "Количество человек не может превышать 4:")
        return


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_EDIT_AGE.value)
def user_edit_age(message):
    age = message.text
    apl[message.chat.id, 'age'] = age
    if int(apl[message.chat.id, 'age']) <= 4:
        if int(apl[message.chat.id, 'age']) == 1 and apl[message.chat.id, 'time'] == 'Утро':
            apl[message.chat.id, 'sum'] = '1000'
        elif int(apl[message.chat.id, 'age']) == 2 and apl[message.chat.id, 'time'] == 'Утро':
            apl[message.chat.id, 'sum'] = '2000'
        elif int(apl[message.chat.id, 'age']) == 3 and apl[message.chat.id, 'time'] == 'Утро':
            apl[message.chat.id, 'sum'] = '3000'
        elif int(apl[message.chat.id, 'age']) == 4 and apl[message.chat.id, 'time'] == 'Утро':
            apl[message.chat.id, 'sum'] = '4000'

        elif int(apl[message.chat.id, 'age']) == 1 and apl[message.chat.id, 'time'] == 'Вечер':
            apl[message.chat.id, 'sum'] = '750'
        elif int(apl[message.chat.id, 'age']) == 2 and apl[message.chat.id, 'time'] == 'Вечер':
            apl[message.chat.id, 'sum'] = '1500'
        elif int(apl[message.chat.id, 'age']) == 3 and apl[message.chat.id, 'time'] == 'Вечер':
            apl[message.chat.id, 'sum'] = '2250'
        elif int(apl[message.chat.id, 'age']) == 4 and apl[message.chat.id, 'time'] == 'Вечер':
            apl[message.chat.id, 'sum'] = '3000'

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton(text='Изменить', callback_data='Edit')
        b2 = types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
        keyboard.add(b1, b2)
        bot.send_message(message.chat.id, f"Ваша заявка:"
                                   f"\n\nИмя: {apl[message.chat.id, 'name']}"
                                   f"\nКоличество человек: {apl[message.chat.id, 'age']}"
                                   f"\nСумма: {apl[message.chat.id, 'sum']}р"
                                   f"\nДата: {apl[message.chat.id, 'date']} {now.year}"
                                   f"\nВремя: {apl[message.chat.id, 'time']}"
                                   f"\nНомер телефона: {apl[message.chat.id, 'number']}",
                              reply_markup=keyboard)
        dbworker.set_state(message.chat.id, config.States.S_USER.value)

    if int(apl[message.chat.id, 'age']) > 4:
        bot.send_message(message.chat.id, "Количество человек не может превышать 4:")
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
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    b1 = types.InlineKeyboardButton(text='Изменить', callback_data='Edit')
    b2 = types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
    keyboard.add(b1, b2)
    bot.send_message(message.chat.id, f"Ваша заявка:"
                               f"\n\nИмя: {apl[message.chat.id, 'name']}"
                               f"\nКоличество человек: {apl[message.chat.id, 'age']}"
                               f"\nСумма: {apl[message.chat.id, 'sum']}р"
                               f"\nДата: {apl[message.chat.id, 'date']} {now.year}"
                               f"\nВремя: {apl[message.chat.id, 'time']}"
                               f"\nНомер телефона: {apl[message.chat.id, 'number']}",
                          reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)


#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_  DATE AND EDIT_DATE   _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_DATE.value)
def user_date(message):
    t_happ_int = message.text
    apl[message.chat.id, 'date'] = t_happ_int
    keyboard = types.InlineKeyboardMarkup()
    b1 = types.InlineKeyboardButton(text='Утро', callback_data='Morning')
    b2 = types.InlineKeyboardButton(text='Вечер', callback_data='Evening')
    keyboard.add(b1, b2)
    bot.send_message(message.chat.id, 'Выберите вариант, который вам больше подходит:'
                                      '\n\n▫️Утром в 6:00. Цена - 1000₽'
                                      '\nРанним утром море по особенному прекрасно, полный штиль, красота😍'
                                      '\nА если повезёт, то мы с вами встретимся с дельфинами, впечатлений останется на весь отпуск'
                                      '\n\n▫️Вечером в 19:30. Цена - 750₽'
                                      '\nКаждый, кто хоть раз плавал на сапе знает, какое невероятное спокойствие можно ощутить вдалеке от берега, когда вас покачивает волнами, а впереди открывается безграничное морское пространство, на фоне уходящего заката и тишина🌅'
                                      '\n\n▫️С 9:00 до 19:00 стоимость проката - 500₽'
                                      '\n\nДарим вам лучшие эмоции каждый день от рассвета до заката🤍',
                     reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_USER_DATE.value)
def user_date(message):
    t_happ_int = message.text
    apl[message.chat.id, 'date'] = t_happ_int
    keyboard = types.InlineKeyboardMarkup()
    b1 = types.InlineKeyboardButton(text='Утро', callback_data='Morning')
    b2 = types.InlineKeyboardButton(text='Вечер', callback_data='Evening')
    keyboard.add(b1, b2)
    bot.send_message(message.chat.id, 'Выберите вариант, который вам больше подходит:'
                                      '\n\n▫️Утром в 6:00. Цена - 1000₽'
                                      '\nРанним утром море по особенному прекрасно, полный штиль, красота😍'
                                      '\nА если повезёт, то мы с вами встретимся с дельфинами, впечатлений останется на весь отпуск'
                                      '\n\n▫️Вечером в 19:30. Цена - 750₽'
                                      '\nКаждый, кто хоть раз плавал на сапе знает, какое невероятное спокойствие можно ощутить вдалеке от берега, когда вас покачивает волнами, а впереди открывается безграничное морское пространство, на фоне уходящего заката и тишина🌅'
                                      '\n\n▫️С 9:00 до 19:00 стоимость проката - 500₽'
                                      '\n\nДарим вам лучшие эмоции каждый день от рассвета до заката🤍',
                     reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_EDIT_DATE.value)
def user_edit_date(message):
    t_happ_int = message.text
    apl[message.chat.id, 'date'] = t_happ_int
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    b1 = types.InlineKeyboardButton(text='Изменить', callback_data='Edit')
    b2 = types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
    keyboard.add(b1, b2)
    bot.send_message(message.chat.id, f"Ваша заявка:"
                                      f"\n\nИмя: {apl[message.chat.id, 'name']}"
                                      f"\nКоличество человек: {apl[message.chat.id, 'age']}"
                                      f"\nСумма: {apl[message.chat.id, 'sum']}р"
                                      f"\nДата: {apl[message.chat.id, 'date']} {now.year}"
                                      f"\nВремя: {apl[message.chat.id, 'time']}"
                                      f"\nНомер телефона: {apl[message.chat.id, 'number']}",
                     reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_USER.value)


#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_  CALL.DATA  _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'Start':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton(text='Прогулки', callback_data='GoSerf')
        b2 = types.InlineKeyboardButton(text='Контакты', callback_data='Contacts')
        b3 = types.InlineKeyboardButton(text='Погода', callback_data='Weather')
        b4 = types.InlineKeyboardButton(text='Как добраться?', callback_data='Map')
        keyboard.add(b1, b2, b3, b4)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Приветствуем в нашем боте!!!'
                             '\nЗдесь вы можете оставить заявку на прогулку.'
                             '\n\nВыберите тот вариант который вам нужен:', reply_markup=keyboard)

    if call.data == 'GoSerf':
        keyboard = types.InlineKeyboardMarkup()
        b1 = types.InlineKeyboardButton(text='Подать заявку', callback_data='Claim')
        b2 = types.InlineKeyboardButton(text='« Вернуться', callback_data='Start')
        keyboard.add(b1, b2)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Работаем каждый день от рассвета до заката'
                                '\n\nУтренние и вечерние прогулки обговариваются заранее, можете оставить заявку здесь, либо написать нам в вотсап или в директ.'
                                '\n\nПрайс:'
                                '\nПрокат SUP в дневное время — 500₽'
                                '\n\nУтренняя прогулка в 6:00 — 1000₽. Вас ждет:'
                                '\n⁃ Встреча с дельфинами'
                                '\n⁃ Шикарные фотографии'
                                '\n⁃ Сопровождение инструктора'
                                '\n⁃ Спокойное и тихое море'
                                '\n\nВечерняя прогулка на закате в 19:00 — 750₽', reply_markup=keyboard)

    if call.data == 'Claim':
        state = dbworker.get_current_state(call.message.chat.id)
        try:
            if state == config.States.S_USER.value:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"{apl[call.message.chat.id, 'name']}, ваше имя и номер у нас есть."
                                           f"\nУкажите, сколько вас человек:")
                dbworker.set_state(call.message.chat.id, config.States.S_USER_AGE.value)
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="Для начала давайте оформим вашу заявку."
                                           "\nНапишите как вас зовут:")
                dbworker.set_state(call.message.chat.id, config.States.S_ENTER_NAME.value)

        except KeyError:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Для начала давайте оформим вашу заявку."
                                       "\nНапишите как вас зовут:")
            dbworker.set_state(call.message.chat.id, config.States.S_ENTER_NAME.value)

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


    if call.data == 'Morning':
        apl[call.message.chat.id, 'time'] = 'Утро'
        if int(apl[call.message.chat.id, 'age']) == 1:
            apl[call.message.chat.id, 'sum'] = '1000'
        elif int(apl[call.message.chat.id, 'age']) == 2:
            apl[call.message.chat.id, 'sum'] = '2000'
        elif int(apl[call.message.chat.id, 'age']) == 3:
            apl[call.message.chat.id, 'sum'] = '3000'
        elif int(apl[call.message.chat.id, 'age']) == 4:
            apl[call.message.chat.id, 'sum'] = '4000'

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton(text='Изменить', callback_data='Edit')
        b2 = types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
        keyboard.add(b1, b2)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"Ваша заявка:"
                                   f"\n\nИмя: {apl[call.message.chat.id, 'name']}"
                                   f"\nКоличество человек: {apl[call.message.chat.id, 'age']}"
                                   f"\nСумма: {apl[call.message.chat.id, 'sum']}р"
                                   f"\nДата: {apl[call.message.chat.id, 'date']} {now.year}"
                                   f"\nВремя: {apl[call.message.chat.id, 'time']}"
                                   f"\nНомер телефона: {apl[call.message.chat.id, 'number']}",
                              reply_markup=keyboard)

    if call.data == 'Evening':
        apl[call.message.chat.id, 'time'] = 'Вечер'
        if int(apl[call.message.chat.id, 'age']) == 1:
            apl[call.message.chat.id, 'sum'] = '750'
        elif int(apl[call.message.chat.id, 'age']) == 2:
            apl[call.message.chat.id, 'sum'] = '1500'
        elif int(apl[call.message.chat.id, 'age']) == 3:
            apl[call.message.chat.id, 'sum'] = '2250'
        elif int(apl[call.message.chat.id, 'age']) == 4:
            apl[call.message.chat.id, 'sum'] = '3000'

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton(text='Изменить', callback_data='Edit')
        b2 = types.InlineKeyboardButton(text='Отправить »', callback_data='Send')
        keyboard.add(b1, b2)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"Ваша заявка:"
                                    f"\n\nИмя: {apl[call.message.chat.id,'name']}"
                                    f"\nКоличество человек: {apl[call.message.chat.id,'age']}"
                                    f"\nСумма: {apl[call.message.chat.id,'sum']}р"
                                    f"\nДата: {apl[call.message.chat.id,'date']} {now.year}"
                                    f"\nВремя: {apl[call.message.chat.id, 'time']}"
                                    f"\nНомер телефона: {apl[call.message.chat.id,'number']}",
                              reply_markup=keyboard)

    if call.data == 'Send':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton(text='Продолжить »', callback_data='Start')
        keyboard.add(b1)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"\n\n{apl[call.message.chat.id, 'name']}, заявка успешно отправлена!!!) "
                                   f"Ждите, скоро с вами свяжутся) "
                                   f"\nСумма: {apl[call.message.chat.id, 'sum']}р",
                              reply_markup=keyboard)

        bot.send_message(1647407069, f"Заявка на утреннюю прогулку:"
                                     f"\n\nИмя: {apl[call.message.chat.id, 'name']}"
                                     f"\nКоличество человек: {apl[call.message.chat.id, 'age']}"
                                     f"\nСумма: {apl[call.message.chat.id, 'sum']}р"
                                     f"\nДата: {apl[call.message.chat.id, 'date']} {now.year}"
                                     f"\nВремя: {apl[call.message.chat.id, 'time']}"
                                     f"\nНомер телефона: {apl[call.message.chat.id, 'number']}")

        bot.send_message(490371324, f"Заявка на утреннюю прогулку:"
                                     f"\n\nИмя: {apl[call.message.chat.id, 'name']}"
                                     f"\nКоличество человек: {apl[call.message.chat.id, 'age']}"
                                     f"\nСумма: {apl[call.message.chat.id, 'sum']}р"
                                     f"\nДата: {apl[call.message.chat.id, 'date']} {now.year}"
                                     f"\nВремя: {apl[call.message.chat.id, 'time']}"
                                     f"\nНомер телефона: {apl[call.message.chat.id, 'number']}")

    if call.data == 'Edit':
        if apl[call.message.chat.id, 'time']:
            TIMETIME = 'Morning'
        else:
            TIMETIME = 'Evening'
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton(text=f"Имя: {apl[call.message.chat.id, 'name']}", callback_data='Edit-name')
        b2 = types.InlineKeyboardButton(text=f"Количество человек: {apl[call.message.chat.id, 'age']}", callback_data='Edit-age')
        b3 = types.InlineKeyboardButton(text=f"Номер телефона: {apl[call.message.chat.id, 'number']}", callback_data='Edit-number')
        b4 = types.InlineKeyboardButton(text=f"Дата: {apl[call.message.chat.id, 'date']} {now.year}", callback_data='Edit-date')
        b5 = types.InlineKeyboardButton(text=f"Время: {apl[call.message.chat.id, 'time']}", callback_data='Edit-time')
        b6 = types.InlineKeyboardButton(text='« Вернуться', callback_data=TIMETIME)
        keyboard.add(b1, b2, b3, b4, b5, b6)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Выберите что хотите изменить:", reply_markup=keyboard)


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

    if call.data == 'Edit-time':
        keyboard = types.InlineKeyboardMarkup()
        b1 = types.InlineKeyboardButton(text='Утро', callback_data='Morning')
        b2 = types.InlineKeyboardButton(text='Вечер', callback_data='Evening')
        keyboard.add(b1, b2)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Выберите время, которое вам больше подходит:'
                                        '\n\n▫️Утром в 6:00. Цена - 1000₽'
                                        '\nРанним утром море по особенному прекрасно, полный штиль, красота😍'
                                        '\nА если повезёт, то мы с вами встретимся с дельфинами, впечатлений останется на весь отпуск'
                                        '\n\n▫️Вечером в 19:30. Цена - 750₽'
                                        '\nКаждый, кто хоть раз плавал на сапе знает, какое невероятное спокойствие можно ощутить вдалеке от берега, когда вас покачивает волнами, а впереди открывается безграничное морское пространство, на фоне уходящего заката и тишина🌅'
                                        '\n\n▫️С 9:00 до 19:00 стоимость проката - 500₽'
                                        '\n\nДарим вам лучшие эмоции каждый день от рассвета до заката🤍', reply_markup=keyboard)


#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_  TYPE:TEXT  _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
@bot.message_handler(content_types=['text'])
def saw(message):
    msg = message.text

    if msg == 'Мой id':
        bot.send_message(message.chat.id, message.chat.id)

bot.polling(none_stop = True, interval = 0)