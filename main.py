import os
from telebot import types
import telebot
from dotenv import load_dotenv
import user_database as ud
from bot_cmd.lowhighprice import low_high_price
from bot_cmd.getcityid import get_city_id
from bot_cmd.get_photo import get_pict_url

load_dotenv()
bot = telebot.TeleBot(os.getenv('token'))


@bot.message_handler(commands=['start'])
def welcome(message):
    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item1 = types.KeyboardButton('Best deal')
    item2 = types.KeyboardButton('Lowprice')
    item3 = types.KeyboardButton('Highprice')
    item4 = types.KeyboardButton('Help')
    item5 = types.KeyboardButton('History')

    markup.add(item1, item2, item3, item4, item5)

    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, "
                     "бот созданный чтобы быть подопытным кроликом.".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def command(message):
    if message.chat.type == 'private':

        if message.text.lower().replace(' ', '') == 'history':
            print(ud.show_history(message.chat.id))
            bot.send_message(message.chat.id, ud.show_history(message.chat.id))

        elif message.text.lower().replace(' ', '') == 'help':
            bot.send_message(message.chat.id, 'Команды бота:\n'
                                              '/bestdeal - отобразит лучшие предложения по Вашим параметрам\n'
                                              '/lowprice - отели с самой низкой ценой\n'
                                              '/highprice - отели с самой высокой ценой\n'
                                              '/history - покажет 2 последних запроса')

        else:
            ud.new_row()
            ud.add_info_to_db('userid', message.chat.id)
            ud.add_info_to_db('command', message.text.lower())

            if message.text.lower().replace(' ', '') == 'lowprice' \
                    or message.text.lower().replace(' ', '') == 'highprice':
                bot.send_message(message.chat.id, 'В каком городе ищем?')
                bot.register_next_step_handler(message, check_city)

            elif message.text.lower() == 'best deal':
                pass


@bot.message_handler(func=lambda m: True)
def check_city(message):
    try:
        city_info = get_city_id(message.text)
        city_id, city_name = city_info[0], city_info[1]
    except TypeError:
        city_info = False
        city_id, city_name = None, None
    if not city_info:
        msg = bot.reply_to(message, 'Город введен некорректно, попробуйте еще раз')
        bot.register_next_step_handler(msg, check_city)
    else:
        ud.add_info_to_db('city_id', str(city_id))
        ud.add_info_to_db('city', city_name)
        bot.register_next_step_handler(message, select_hotel_count)


# @bot.message_handler(func=lambda m: True)
def select_hotel_count(message):
    bot.send_message(message.chat.id, 'Сколько отелей показать?')
    bot.register_next_step_handler(message, pict_view)


# @bot.message_handler(func=lambda m: True)
def pict_view(message):
    if message.text.isdecimal() and int(message.text) <= 5:
        ud.add_info_to_db('hotelcount', message.text)
        bot.send_message(message.chat.id, 'Показать фото? Выбирете количество')
        bot.register_next_step_handler(message, check_photo_cnt)
    else:
        bot.send_message(message.chat.id, 'Число отелей введено некорректно. Отправьте число отелей цифрой от 1 до 5')
        bot.register_next_step_handler(message, pict_view)


@bot.message_handler(func=lambda m: True)
def check_photo_cnt(message):
    if message.text.isdecimal() and int(message.text) <= 5:
        bot.register_next_step_handler(message, filter_low)
    else:
        bot.send_message(message.chat.id, 'Число фото введено некорректно. Отправьте число отелей цифрой от 0 до 5')
        bot.register_next_step_handler(message, check_photo_cnt)
        # TODO исправить баг: при переходе в проверки (ф-ии check) нужно еще раз отправлять данные


# @bot.message_handler(func=lambda m: True)
def filter_low(message):
    ud.add_info_to_db('photocount', message.text)
    bot.send_message(message.chat.id, 'Waiting...')
    bot.send_message(message.chat.id, f'Выполняю поиск отелей в\n {ud.get_info_from_db("city")}')

    data_n = low_high_price(ud.get_info_from_db('hotelcount'),
                            ud.get_info_from_db('city_id'),
                            ud.get_info_from_db('command'))

    for i_elem in data_n:
        msg_to_user = ''
        for k, v in i_elem.items():
            msg_to_user += f'{k}: {v}\n'
        bot.send_message(message.chat.id, msg_to_user)
        # print(i_elem)
        for j_elem in get_pict_url(i_elem['\nid'], int(message.text)):
            msg_to_user += ' ' + j_elem + ' \n'
            bot.send_photo(message.chat.id, j_elem, parse_mode="HTML")
        ud.add_info_to_db('results', msg_to_user + '\n')


bot.polling(none_stop=True)
