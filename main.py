import telebot
import dbworker
import config
from telebot import types
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
    bot.send_message(message.chat.id, "Отличное имя, запомню! Теперь укажи, пожалуйста, количество человек в группе. "
                                      "Оно не должно превышать 3. "
                                      "Для того чтобы выбрать больше трех необходимо подавать новые заявки:")
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
    # В случае с именем не будем ничего проверять, пусть хоть "25671", хоть Евкакий
    number = str(message.text)
    bot.send_message(message.chat.id, f'Ваше имя: {name}'
                                      f'\nКоличество человек: {age}'
                                      f'\nВаш номер телефона: {number}')
    bot.send_message(message.chat.id, f'{name}, заявка успешно отправлена!!!) Ждите, скоро с вами свяжутся) Сумма: {sum}р')
    bot.send_message(490371324, f'Заявка на утреннюю прогулку:'
                                f'\n\nИмя: {name}'
                                f'\nКоличество человек: {age}'
                                f'\nСумма: {sum}р'
                                f'\nНомер телефона: {number}'
                                f'\n\nЕго телеграм данные:'
                                f'\n{message.from_user.first_name} {message.from_user.last_name}'
                                f'\nСсылка: @{message.from_user.username}')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'GoSerf':
        keyboard = types.InlineKeyboardMarkup()
        b1 = types.InlineKeyboardButton(text='Подать заявку', callback_data='Claim')
        keyboard.add(b1)
        bot.send_message(call.message.chat.id,
                         'Мы работаем каждый день. Наше местоположение можете узнать чуть раньше.'
                         '\nОсуществляются дополнительные прогулки часов в 5-6 утра, чтобы встретить дельфинов в черном море.'
                         '\nСтоимость прогулки состовлят 500р. Время прогулки 1 час.'
                         '\n\nХотите подать заявку?', reply_markup=keyboard)
    if call.data == 'Claim':
        bot.send_message(call.message.chat.id, "Для начала давайте оформим вашу заявку."
                                               "\nНапишите как вас зовут:")
        dbworker.set_state(call.message.chat.id, config.States.S_ENTER_NAME.value)


    if call.data == 'Contacts':
        bot.send_message(call.message.chat.id, '📞 Данил Сергеевич - +79407322932')
    if call.data == 'Weather':
        Weather(call.message)
    if call.data == 'Map':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton(text='Яндекс.Навигатор', url='https://yandex.ru/maps/10280/gagra/?l=sat&ll=40.277993%2C43.286838&mode=routes&rtext=~43.293617%2C40.258295&rtt=auto&ruri=~&z=14')
        keyboard.add(b1)
        bot.send_message(call.message.chat.id, 'Отметьте свое местоположение 🚩\n\nВам будет построен маршрут. Наше местоположение уже отмечено)', reply_markup=keyboard)

bot.polling(none_stop = True, interval = 0)