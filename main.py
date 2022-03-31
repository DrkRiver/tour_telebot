import os
import telebot
from dotenv import load_dotenv
import user_database as ud
from bot_cmd.lowprice import low_price
from bot_cmd.getcityid import get_city_id


load_dotenv()
bot = telebot.TeleBot(os.getenv('token'))


@bot.message_handler(commands=['start'])
def welcome(message):
    ud.new_row()
    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, "
                     "бот созданный чтобы быть подопытным кроликом.".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html')


@bot.message_handler(content_types=['text'])
def command(message):
    # ud.add_info_to_db('userid', message.chat.id)
    # ud.add_info_to_db('command', message.text)
    if message.chat.type == 'private':
        if message.text.lower() == 'lowprice':

            ud.add_info_to_db('userid', message.chat.id)
            ud.add_info_to_db('command', message.text)

            bot.send_message(message.chat.id, 'В каком городе ищем?')
            bot.register_next_step_handler(message, select_hotel_count)
        elif message.text.lower() == 'history':
            print(ud.show_history(message.chat.id))
            bot.send_message(message.chat.id, ud.show_history(message.chat.id))


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

    data_n = low_price(ud.get_info_from_db(column='hotelcount'), get_city_id(ud.get_info_from_db(column='city')))

    for i_elem in data_n:
        msg_to_user = ''
        for k, v in i_elem.items():
            msg_to_user += f'{k}: {v}\n'
        # for j_elem in get_pict_url(i_elem['id'], int(message.text)): # TO DO написать ф-ю по фото
        #     msg_to_user += j_elem + ' '
        bot.send_message(message.chat.id, msg_to_user)
        ud.add_result_to_db(msg_to_user)


bot.polling(none_stop=True)
