import telebot
from telebot import types
import os.path as op
import urllib.request
from datetime import date
from currency_converter import ECB_URL, CurrencyConverter

filename = f"ecb_{date.today():%Y%m%d}.zip"
if not op.isfile(filename):
    urllib.request.urlretrieve(ECB_URL, filename)

TOKEN = None

with open("token.txt") as f:
    TOKEN = f.read().strip()

bot = telebot.TeleBot(TOKEN)

currency = CurrencyConverter(filename)
amount = 0

@bot.message_handler(commands=['start'])
def start(message):
      bot.send_message(message.chat.id, 'Здравствуйте, введите сумму для конвертации')
      bot.register_next_step_handler(message, summa)

def summa(message):
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат. Впишите сумму')
        bot.register_next_step_handler(message, summa)
        return

    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('USD/EUR', callback_data='usd/eur')
        btn2 = types.InlineKeyboardButton('EUR/USD', callback_data='eur/usd')
        btn3 = types.InlineKeyboardButton('RUB/USD', callback_data='rub/usd')
        btn4 = types.InlineKeyboardButton('Другое значение', callback_data='else')
        markup.add(btn1,btn2, btn3, btn4)
        bot.send_message(message.chat.id, 'Выберите пару валют', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Число должно быть больше 0. Впишите сумму')
        bot.register_next_step_handler(message, summa)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data != 'else':
        values = call.data.upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(call.message.chat.id, f'Получается: {round(res, 2)}. Можете заново вписать сумму')
        bot.register_next_step_handler(call.message, summa)
    else:
        bot.send_message(call.message.chat.id, 'Введите пару значений через слэш')
        bot.register_next_step_handler(call.message, my_currency)

def my_currency(message):
    try:
        values = message.text.upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f'Получается: {round(res, 2)}. Можете заново вписать сумму')
        bot.register_next_step_handler(message, summa)
    except Exception:
        bot.send_message(message.chat.id, f'Что-то не так. Впишите значение заново')
        bot.register_next_step_handler(message, my_currency)



bot.polling()