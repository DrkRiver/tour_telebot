import os
from telebot import types
import telebot
from dotenv import load_dotenv
import user_database as ud
from bot_cmd.lowprice import low_price
from bot_cmd.getcityid import get_city_id
from bot_cmd.get_photo import get_pict_url


load_dotenv()
bot = telebot.TeleBot(os.getenv('token'))


@bot.message_handler(commands=['start'])
def welcome(message):
    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
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

        if message.text.lower() == 'history':
            print(ud.show_history(message.chat.id))
            bot.send_message(message.chat.id, ud.show_history(message.chat.id))

        else:
            ud.new_row()
            ud.add_info_to_db('userid', message.chat.id)
            ud.add_info_to_db('command', message.text)

            if message.text.lower() == 'lowprice':
                bot.send_message(message.chat.id, 'В каком городе ищем?')
                bot.register_next_step_handler(message, select_hotel_count)
            elif message.text.lower() == 'highprice':
                pass
            elif message.text.lower() == 'best deal':
                bot.send_photo(message.chat.id,
                                 'https://exp.cdn-hotels.com/hotels/22000000/21230000/21226200/21226125/5a9ce7ee_b.jpg'
                                 , parse_mode="HTML")
                pass
            elif message.text.lower() == 'help':
                pass


@bot.message_handler(func=lambda m: True)
def select_hotel_count(message):
    ud.add_info_to_db('city', message.text)
    bot.send_message(message.chat.id, 'Сколько отелей показать?')
    bot.register_next_step_handler(message, pict_view)


@bot.message_handler(func=lambda m: True)
def pict_view(message):
    ud.add_info_to_db('hotelcount', message.text)
    bot.send_message(message.chat.id, 'Показать фото? Выбирете количество')
    bot.register_next_step_handler(message, filter_low)


@bot.message_handler(func=lambda m: True)
def filter_low(message):
    ud.add_info_to_db('photocount', message.text)
    bot.send_message(message.chat.id, 'Waiting...')
    city_id = get_city_id(ud.get_info_from_db(column='city'))
    data_n = low_price(ud.get_info_from_db(column='hotelcount'), city_id)

    for i_elem in data_n:
        msg_to_user = ''
        for k, v in i_elem.items():
            msg_to_user += f'{k}: {v} \n '
        bot.send_message(message.chat.id, msg_to_user)
        for j_elem in get_pict_url(i_elem['id'], int(message.text)):
            msg_to_user += j_elem + ' '
            bot.send_photo(message.chat.id, j_elem, parse_mode="HTML")
        ud.add_result_to_db(msg_to_user)


bot.polling(none_stop=True)
