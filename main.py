import os
import telebot
from dotenv import load_dotenv
import user_database as ud


load_dotenv()
bot = telebot.TeleBot(os.getenv('token'))


@bot.message_handler(commands=['start'])
def welcome(message):
    ud.new_row()
    ud.add_info_to_db('userid', message.chat.id)
    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, "
                     "бот созданный чтобы быть подопытным кроликом.".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html')


@bot.message_handler(content_types=['text'])
def command(message):
    ud.add_info_to_db('command', message.text)
    if message.chat.type == 'private':
        if message.text.lower() == 'lowprice':
            bot.send_message(message.chat.id, 'В каком городе ищем?')
            bot.register_next_step_handler(message, select_hotel_count)


@bot.message_handler(func=lambda m: True)
def select_hotel_count(message):
    ud.add_info_to_db('city', message.text)
    bot.send_message(message.chat.id, 'Сколько отелей показать?')
    bot.register_next_step_handler(message, pict_view)


@bot.message_handler(func=lambda m: True)
def pict_view(message):
    ud.add_info_to_db('hotelcount', message.text)
    bot.send_message(message.chat.id, 'Wanna watch photos? Pick photo count')
    bot.register_next_step_handler(message, filter_low)


@bot.message_handler(func=lambda m: True)
def filter_low(message):
    ud.add_info_to_db('photocount', message.text)
    bot.send_message(message.chat.id, 'Waiting...')


# TO DO Написать модуль функции lowprice


bot.polling(none_stop=True)
