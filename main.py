import os
import telebot
from telebot import types
from dotenv import load_dotenv
import user_database as ud
from bot_cmd.bot_filters import best_deal, low_high_price
from bot_cmd.getcityid import get_city_id
from bot_cmd.get_photo import get_pict_url
from datetime import datetime
from loguru import logger

logger.add('bot_log.log', format='{time} {level} {message}', level='DEBUG', rotation='1 MB')

load_dotenv()
bot = telebot.TeleBot(os.getenv('token'))
ud.create_db()


@bot.message_handler(commands=['start'])
def welcome(message):
    """
    Приветственная функция - запускает работу бота: выводит приветственное сообщение, отображает кнопки с функциями
    :param message: принимает сообщение пользователя со значением выполняемой команды ('/start')
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    item1 = types.KeyboardButton('/Bestdeal')
    item2 = types.KeyboardButton('/Lowprice')
    item3 = types.KeyboardButton('/Highprice')
    item4 = types.KeyboardButton('/Help')
    item5 = types.KeyboardButton('/History')

    markup.add(item1, item2, item3, item4, item5)

    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, "
                     "бот созданный чтобы помочь в выборе отеля."
                     "\nВведите интересующую команду (помощь по командам /help)".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)

    logger.info(f'Пользователь {message.from_user.first_name} {message.chat.id} начал работу')


@bot.message_handler(content_types=['text'])
def command(message):
    """
    Функция, обрабатывающая введенную пользователем команду
    :param message: принимает сообщение пользователя со значением выполняемой команды
    """
    if message.chat.type == 'private':

        user_cmd = message.text[1:].lower().replace(' ', '')

        if user_cmd == 'history':
            for history_elem in ud.show_history(message.chat.id):
                bot.send_message(message.chat.id, history_elem)

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
            logger.info(f'Пользователь {message.chat.id} запустил команду {message.text}')

        else:
            bot.send_message(message.chat.id, 'Команда не опознана... Пoпробуйте еще раз\n'
                                              'Для получения подсказки по командам нажмите /help')
            logger.debug(f'Пользователь {message.chat.id} ввел некорректную команду {message.text}')


@bot.message_handler(func=lambda m: True)
def check_city(message):
    """
    Функция по проверке существования искомого города
    :param message: принимает сообщение пользователя со значением искомого города
    """
    try:
        city_info = get_city_id(message.text)
        city_id, city_name = city_info[0], city_info[1]

    except TypeError:
        city_info = False
        city_id, city_name = None, None
    if not city_info:
        msg = bot.reply_to(message, 'Указанный город не найден, попробуйте еще раз на английском языке')
        bot.register_next_step_handler(msg, check_city)
        logger.debug(f'Пользователь {message.chat.id} ввел город {message.text}, отсутствующий в HotelsAPI')
    else:
        ud.add_info_to_db('city_id', str(city_id))
        ud.add_info_to_db('city', city_name)
        logger.info(f'Пользователь {message.chat.id} ввел город {ud.get_info_from_db("city")} для поиска отелей')
        if ud.get_info_from_db('command') == 'bestdeal':
            bot.send_message(message.chat.id, 'Введите диапазон цен в USD через пробел')
            bot.register_next_step_handler(message, hotel_price)
        else:
            bot.send_message(message.chat.id, 'Сколько отелей показать?')
            bot.register_next_step_handler(message, hotel_count)


@bot.message_handler(func=lambda m: True)
def hotel_price(message):
    """
    Функция принимает значения диапазона цен и проверяет его валидность
    :param message: принимает сообщение пользователя со значением диапазона цен
    """
    price = message.text.split()
    if len(price) == 2 and (price[0] + price[1]).isdecimal():
        ud.add_info_to_db('price', message.text)
        bot.send_message(message.chat.id, 'Введите максимальную удаленность отеля от цента искомого города в км')
        bot.register_next_step_handler(message, hotel_distance)
    else:
        msg = bot.reply_to(message, 'Диапазон цен в USD введен некорректно. Введите два числа через пробел')
        bot.register_next_step_handler(msg, hotel_price)
        logger.debug(f'Пользователь {message.chat.id} ввел некорректный диапазон цен({message.text})')


@bot.message_handler(func=lambda m: True)
def hotel_distance(message):
    """
    Функция принимает предельное расстояние от центра города до отеля в милях и проверяет его валидность
    :param message: принимает сообщение пользователя со значением предельного расстояния
    """
    if message.text.isdecimal():
        ud.add_info_to_db('dist', message.text)
        bot.send_message(message.chat.id, 'Сколько отелей показать?')
        bot.register_next_step_handler(message, hotel_count)
    else:
        msg = bot.reply_to(message, 'Максимальное расстояние до центра введено некорректно. Введите число')
        bot.register_next_step_handler(msg, hotel_distance)
        logger.debug(f'Пользователь {message.chat.id} ввел некорректное расстояние до центра({message.text})')


@bot.message_handler(func=lambda m: True)
def hotel_count(message):
    """
    Функция принимает количество отелей и проверяет его валидность
    :param message: принимает сообщение пользователя со значением количества отелей
    """
    if message.text.isdecimal() and int(message.text) in range(1, 6):
        ud.add_info_to_db('hotelcount', message.text)
        bot.send_message(message.chat.id, 'Введите кол-во фото')
        bot.register_next_step_handler(message, photo_count)
    else:
        msg = bot.reply_to(message, 'Кол-во отелей введено некорректно. Введите число от 1 до 5')
        bot.register_next_step_handler(msg, hotel_count)
        logger.debug(f'Пользователь {message.chat.id} ввел некорректное кол-во отелей({message.text})')


@bot.message_handler(func=lambda m: True)
def photo_count(message):
    """
    Функция принимает количество фотографий и проверяет его валидность
    :param message: принимает сообщение пользователя со значением количества фотографий
    """
    if message.text.isdecimal() and int(message.text) in range(0, 6):
        ud.add_info_to_db('photocount', message.text)
        bot.send_message(message.chat.id, 'Waiting...')
        user_filter()
    else:
        msg = bot.reply_to(message, 'Кол-во фото введено некорректно. Введите число от 0 до 5')
        bot.register_next_step_handler(msg, photo_count)
        logger.debug(f'Пользователь {message.chat.id} ввел некорректное кол-во фотографий({message.text})')


def user_filter():
    """
    Функция выполняет подбор отелей в зависимости от введенной команды и указанных параметров
    """
    user_id = ud.get_info_from_db('userid')
    bot.send_message(user_id, f'Выполняю поиск отелей в\n{ud.get_info_from_db("city")}')

    if ud.get_info_from_db('command') == 'bestdeal':
        logger.info(f"Запрос №{ud.get_info_from_db('reqid')}:"
                    f"Запущена обработка команды {ud.get_info_from_db('command')} со следующими параметрами: "
                    f"кол-во отелей - {ud.get_info_from_db('hotelcount')},"
                    f"город поиска/его id - {ud.get_info_from_db('city')}/{ud.get_info_from_db('city_id')},"
                    f"максимальная удаленность от центра города - {ud.get_info_from_db('dist')},"
                    f"диапазон цен в USD - {ud.get_info_from_db('price')}")
        data_n = best_deal(ud.get_info_from_db('hotelcount'),
                           ud.get_info_from_db('city_id'),
                           ud.get_info_from_db('dist'),
                           ud.get_info_from_db('price'),)
    else:
        logger.info(f"Запрос №{ud.get_info_from_db('reqid')}: "
                    f"Запущена обработка команды {ud.get_info_from_db('command')} со следующими параметрами: "
                    f"кол-во отелей - {ud.get_info_from_db('hotelcount')},"
                    f"город поиска/его id - {ud.get_info_from_db('city')}/{ud.get_info_from_db('city_id')},")
        data_n = low_high_price(ud.get_info_from_db('hotelcount'),
                                ud.get_info_from_db('city_id'),
                                ud.get_info_from_db('command'))

    if len(data_n) == 0:
        bot.send_message(user_id, 'К сожалению, по Вашим критериям ничего не найдено.')
        ud.add_info_to_db('results', 'По заданным критериям ничего не найдено.')
        logger.debug(f"По запросу {ud.get_info_from_db('reqid')} поиск завершен без результата")
    else:
        for i_elem in data_n:
            msg_to_user = ''
            for k, v in i_elem.items():
                msg_to_user += f'{k}: {v}\n'
            bot.send_message(user_id, msg_to_user)
            if ud.get_info_from_db('photocount') != 0:
                for j_elem in get_pict_url(i_elem['id'], ud.get_info_from_db('photocount')):
                    msg_to_user += ' ' + j_elem + ' \n'
                    bot.send_photo(user_id, j_elem, parse_mode="HTML")
            ud.add_info_to_db('results', msg_to_user + '\n')
        bot.send_message(user_id, 'Поиск завершен.')
        logger.info(f"По запросу {ud.get_info_from_db('reqid')} поиск завершен, результат записан в БД")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    item1 = types.KeyboardButton('/Bestdeal')
    item2 = types.KeyboardButton('/Lowprice')
    item3 = types.KeyboardButton('/Highprice')
    item4 = types.KeyboardButton('/Help')
    item5 = types.KeyboardButton('/History')

    markup.add(item1, item2, item3, item4, item5)

    bot.send_message(user_id, 'Какую команду выполнить?', reply_markup=markup)


bot.polling(none_stop=True)
