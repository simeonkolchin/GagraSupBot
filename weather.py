import telebot, requests, random
from bs4 import BeautifulSoup
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

def Weather(message):
    URL = 'https://yandex.ru/pogoda/10280?utm_source=serp&utm_campaign=wizard&utm_medium=desktop&utm_content=wizard_desktop_main&utm_term=title&lat=43.266731&lon=40.276294'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.77'
    }
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    digrees = soup.find('span', class_='temp__value temp__value_with-unit').get_text().encode('utf-8').decode('utf-8', 'ignore')
    digrees_water = soup.find('div', class_='temp fact__water-temp').get_text().encode('utf-8').decode('utf-8', 'ignore')
    wind = soup.find('span', class_='wind-speed').get_text().encode('utf-8').decode('utf-8', 'ignore')

    bot.send_message(message.chat.id, f'⛅ Температура: {digrees}°C'
                                      f'\n💨 Скорость ветра: {wind} м/с'
                                      f'\n🌊 Температура воды: {digrees_water}°C')