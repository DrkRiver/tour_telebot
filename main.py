import os
from telebot import types
import telebot
from dotenv import load_dotenv
import user_database as ud
from bot_cmd.lowhighprice import low_high_price
from bot_cmd.bestdeal import best_deal
from bot_cmd.getcityid import get_city_id
from bot_cmd.get_photo import get_pict_url
from datetime import datetime

load_dotenv()
bot = telebot.TeleBot(os.getenv('token'))


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    item1 = types.KeyboardButton('/Best deal')
    item2 = types.KeyboardButton('/Low price')
    item3 = types.KeyboardButton('/High price')
    item4 = types.KeyboardButton('/Help')
    item5 = types.KeyboardButton('/History')

    markup.add(item1, item2, item3, item4, item5)

    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, "
                     "бот созданный чтобы помочь в выборе отеля.".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def command(message):
    if message.chat.type == 'private':

        user_cmd = message.text[1:].lower().replace(' ', '')

        if user_cmd == 'history':
            bot.send_message(message.chat.id, ud.show_history(message.chat.id))

        elif user_cmd == 'help':
            bot.send_message(message.chat.id, 'Команды бота:\n'
                                              '/bestdeal - отобразит лучшие предложения по Вашим параметрам\n'
                                              '/lowprice - отели с самой низкой ценой\n'
                                              '/highprice - отели с самой высокой ценой\n'
                                              '/history - покажет 2 последних запроса')

        elif user_cmd in ('lowprice', 'highprice', 'bestdeal'):
            ud.new_row()
            ud.add_info_to_db('userid', message.chat.id)
            ud.add_info_to_db('command', user_cmd)
            ud.add_info_to_db('time', str(datetime.now())[:-7])

            bot.send_message(message.chat.id, 'В каком городе ищем?', reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, check_city)

        else:
            bot.send_message(message.chat.id, 'Команда не опознана... Пoпробуйте еще раз')


@bot.message_handler(func=lambda m: True)
def check_city(message):
    try:
        city_info = get_city_id(message.text)
        city_id, city_name = city_info[0], city_info[1]
    except TypeError:
        city_info = False
        city_id, city_name = None, None
    if not city_info:
        msg = bot.reply_to(message, 'Указанный город не найден, попробуйте еще раз на английском')
        bot.register_next_step_handler(msg, check_city)
    else:
        ud.add_info_to_db('city_id', str(city_id))
        ud.add_info_to_db('city', city_name)
        if ud.get_info_from_db('command') == 'bestdeal':
            bot.send_message(message.chat.id, 'Введите диапазон цен через пробел')
            bot.register_next_step_handler(message, hotel_price)
        else:
            bot.send_message(message.chat.id, 'Сколько отелей показать?')
            bot.register_next_step_handler(message, hotel_count)


@bot.message_handler(func=lambda m: True)
def hotel_price(message):
    price = message.text.split()
    if len(price) == 2 and (price[0] + price[1]).isdecimal():
        ud.add_info_to_db('price', message.text)
        bot.send_message(message.chat.id, 'Введите расстояние до центра')
        bot.register_next_step_handler(message, hotel_distance)
    else:
        msg = bot.reply_to(message, 'Диапазон цен введен некорректно. Введите два числа через пробел')
        bot.register_next_step_handler(msg, hotel_price)


@bot.message_handler(func=lambda m: True)
def hotel_distance(message):
    if message.text.isdecimal():
        ud.add_info_to_db('dist', message.text)
        bot.send_message(message.chat.id, 'Сколько отелей показать?')
        bot.register_next_step_handler(message, hotel_count)
    else:
        msg = bot.reply_to(message, 'Расстояние до центра введено некорректно. Введите число')
        bot.register_next_step_handler(msg, hotel_distance)


@bot.message_handler(func=lambda m: True)
def hotel_count(message):
    if message.text.isdecimal() and int(message.text) in range(1, 6):
        ud.add_info_to_db('hotelcount', message.text)
        bot.send_message(message.chat.id, 'Введите кол-во фото')
        bot.register_next_step_handler(message, photo_count)
    else:
        msg = bot.reply_to(message, 'Кол-во отелей введено некорректно. Введите число от 1 до 5')
        bot.register_next_step_handler(msg, hotel_count)


@bot.message_handler(func=lambda m: True)
def photo_count(message):
    if message.text.isdecimal() and int(message.text) in range(0, 6):
        ud.add_info_to_db('photocount', message.text)
        bot.send_message(message.chat.id, 'Waiting...')
        filter_low()
    else:
        msg = bot.reply_to(message, 'Кол-во фото введено некорректно. Введите число от 0 до 5')
        bot.register_next_step_handler(msg, photo_count)


def filter_low():
    user_id = ud.get_info_from_db('userid')
    bot.send_message(user_id, f'Выполняю поиск отелей в\n{ud.get_info_from_db("city")}')

    if ud.get_info_from_db('command') == 'bestdeal':
        data_n = best_deal(ud.get_info_from_db('hotelcount'),
                           ud.get_info_from_db('city_id'),
                           ud.get_info_from_db('dist'),
                           ud.get_info_from_db('price'),)
    else:
        data_n = low_high_price(ud.get_info_from_db('hotelcount'),
                                ud.get_info_from_db('city_id'),
                                ud.get_info_from_db('command'))

    if len(data_n) == 0:
        bot.send_message(user_id, 'К сожалению, по Вашим критериям ничего не найдено.')
        ud.add_info_to_db('results', 'По заданным критериям ничего не найдено.')
    else:
        for i_elem in data_n:
            msg_to_user = ''
            for k, v in i_elem.items():
                msg_to_user += f'{k}: {v}\n'
            bot.send_message(user_id, msg_to_user)
            if ud.get_info_from_db('photocount') != 0:
                for j_elem in get_pict_url(i_elem['\nid'], ud.get_info_from_db('photocount')):
                    msg_to_user += ' ' + j_elem + ' \n'
                    bot.send_photo(user_id, j_elem, parse_mode="HTML")
            ud.add_info_to_db('results', msg_to_user + '\n')
        bot.send_message(user_id, 'Поиск завершен.')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    item1 = types.KeyboardButton('/Best deal')
    item2 = types.KeyboardButton('/Low price')
    item3 = types.KeyboardButton('/High price')
    item4 = types.KeyboardButton('/Help')
    item5 = types.KeyboardButton('/History')

    markup.add(item1, item2, item3, item4, item5)

    bot.send_message(user_id, 'Какую команду выполнить?', reply_markup=markup)


bot.polling(none_stop=True)
