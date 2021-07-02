import datetime

import telegramcalendar

import telebot
from telebot import types

import config
import dbworker
from config import TOKEN
from weather import Weather

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
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

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_NAME.value)
def user_entering_name(message):
    # В случае с именем не будем ничего проверять, пусть хоть "25671", хоть Евкакий
    global name
    name = str(message.text)
    bot.send_message(message.chat.id, "Приятно познакомиться! Теперь укажи, сколько вас человек:")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_AGE.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_AGE.value)
def user_entering_age(message):
    # А вот тут сделаем проверку
    if int(message.text) == 1:
        global age
        global sum
        age = str(message.text)
        sum = '750'
        bot.send_message(message.chat.id, "Отправь мне свой номер телефона, для того чтобы мы с тобой связались:")
        dbworker.set_state(message.chat.id, config.States.S_ENTER_NUMBER.value)

    if int(message.text) == 2:
        age = str(message.text)
        sum = '1500'
        bot.send_message(message.chat.id, "Отправь мне свой номер телефона, для того чтобы мы с тобой связались:")
        dbworker.set_state(message.chat.id, config.States.S_ENTER_NUMBER.value)

    if int(message.text) == 3:
        age = str(message.text)
        sum = '2250'
        bot.send_message(message.chat.id, "Отправь мне свой номер телефона, для того чтобы мы с тобой связались:")
        dbworker.set_state(message.chat.id, config.States.S_ENTER_NUMBER.value)
    if int(message.text) > 3:
        bot.send_message(message.chat.id, "Количество человек не может превышать 3:")
        return

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_NUMBER.value)
def user_entering_name(message):
    now = datetime.datetime.now()  # Текущая дата.
    chat_id = message.chat.id
    date = (now.year, now.month)

    # Добавлено создание словаря.
    current_shown_dates = {}

    current_shown_dates[chat_id] = date  # Сохраним текущую дату в словарь.
    markup = create_calendar(now.year, now.month)
    bot.send_message(message.chat.id, "Пожалуйста, выберите дату", reply_markup=markup)
    dbworker.set_state(message.chat.id, config.States.S_ENTER_DATE.value)

    # В случае с именем не будем ничего проверять, пусть хоть "25671", хоть Евкакий

    global number
    number = str(message.text)



@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_DATE.value)
def get_calendar(message):
    now = datetime.datetime.now()  # Текущая дата.
    chat_id = message.chat.id
    date = (now.year,now.month)
    keyboard = types.InlineKeyboardMarkup()
    b1 = types.InlineKeyboardButton(text='Утро', callback_data='Morning')
    b2 = types.InlineKeyboardButton(text='Вечер', callback_data='Evening')

    keyboard.add(b1, b2)
    bot.send_message(message.chat.id, 'Выберите вариант, который вам больше подходит:'
                                      '\n\n▫️Утром в 6:00. Цена - 750₽'
                                      '\nРанним утром море по особенному прекрасно, полный штиль, красота😍'
                                      '\nА если повезёт, то мы с вами встретимся с дельфинами, впечатлений останется на весь отпуск'
                                      '\n\n▫️Вечером в 19:30. Цена - 750₽'
                                      '\nКаждый, кто хоть раз плавал на сапе знает, какое невероятное спокойствие можно ощутить вдалеке от берега, когда вас покачивает волнами, а впереди открывается безграничное морское пространство, на фоне уходящего заката и тишина🌅'
                                      '\n\n▫️С 9:00 до 19:00 стоимость проката - 500₽'
                                      '\n\nДарим вам лучшие эмоции каждый день от рассвета до заката🤍',
                     reply_markup=keyboard)

    # Добавлено создание словаря.
    current_shown_dates = {}

    current_shown_dates[chat_id] = date  # Сохраним текущую дату в словарь.
    markup = create_calendar(now.year,now.month)
    bot.send_message(message.chat.id, "Пожалуйста, выберите дату", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'GoSerf':
        keyboard = types.InlineKeyboardMarkup()
        b1 = types.InlineKeyboardButton(text='Подать заявку', callback_data='Claim')
        keyboard.add(b1)
        bot.send_message(call.message.chat.id,
                         'Работаем каждый день от рассвета до заката'
                         '\n\nУтренние и вечерние прогулки обговариваются заранее, можете оставить заявку здесь, либо написать нам в вотсап или в директ.'
                         '\n\nПрайс:'
                         '\nПрокат SUP в дневное время — 500₽'
                         '\n\nУтренняя прогулка в 6:00 — 750₽. Вас ждет:'
                         '\n⁃ Встреча с дельфинами'
                         '\n⁃ Шикарные фотографии'
                         '\n⁃ Сопровождение инструктора'
                         '\n⁃ Спокойное и тихое море'
                         '\n\nВечерняя прогулка на закате в 19:00 — 750₽', reply_markup=keyboard)

    if call.data == 'Claim':
        bot.send_message(call.message.chat.id, "Для начала давайте оформим вашу заявку."
                                               "\nНапишите как вас зовут:")
        dbworker.set_state(call.message.chat.id, config.States.S_ENTER_NAME.value)

    if call.data == 'Contacts':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton(text='Instagram', url='https://www.instagram.com/gagra_sup/')
        keyboard.add(b1)
        bot.send_message(call.message.chat.id, '📞 Данил: +79407322932 (WhatsApp, telegram)', reply_markup=keyboard)
    if call.data == 'Weather':
        Weather(call.message)
    if call.data == 'Map':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton(text='Яндекс.Навигатор', url='https://yandex.ru/maps/10280/gagra/?l=sat&ll=40.257954%2C43.295045&mode=routes&rtext=~43.294975%2C40.258105&rtt=auto&ruri=~&z=18')
        keyboard.add(b1)
        bot.send_message(call.message.chat.id, 'Отметьте свое местоположение 🚩\n\nВам будет построен маршрут. Наше местоположение уже отмечено)', reply_markup=keyboard)


    if call.data == 'Morning':
        bot.send_message(call.message.chat.id, f'Ваше имя: {name}'
                                          f'\nКоличество человек: {age}'
                                          f'\nВаш номер телефона: {number}'
                                          f'\nВремя: Утро')
        bot.send_message(call.message.chat.id,
                         f'{name}, заявка успешно отправлена!!!) Ждите, скоро с вами свяжутся) Сумма: {sum}р')
        bot.send_message(490371324, f'Заявка на утреннюю прогулку:'
                                    f'\n\nИмя: {name}'
                                    f'\nКоличество человек: {age}'
                                    f'\nСумма: {sum}р'
                                    f'\nВремя: Утро'
                                    f'\nНомер телефона: {number}'
                                    f'\n\nЕго телеграм данные:'
                                    f'\n{call.message.from_user.first_name} {call.message.from_user.last_name}'
                                    f'\nСсылка: @{call.message.from_user.username}')
    if call.data == 'Evening':
        bot.send_message(call.message.chat.id, f'Ваше имя: {name}'
                                               f'\nКоличество человек: {age}'
                                               f'\nВаш номер телефона: {number}'
                                               f'\nВремя: Вечер')
        bot.send_message(call.message.chat.id,
                         f'{name}, заявка успешно отправлена!!!) Ждите, скоро с вами свяжутся) Сумма: {sum}р')
        bot.send_message(490371324, f'Заявка на утреннюю прогулку:'
                                    f'\n\nИмя: {name}'
                                    f'\nКоличество человек: {age}'
                                    f'\nСумма: {sum}р'
                                    f'\nВремя: Вечер'
                                    f'\nНомер телефона: {number}'
                                    f'\n\nЕго телеграм данные:'
                                    f'\n{call.message.from_user.first_name} {call.message.from_user.last_name}'
                                    f'\nСсылка: @{call.message.from_user.username}')

bot.polling(none_stop = True, interval = 0)