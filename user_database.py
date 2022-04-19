import sqlite3
import telebot
from dotenv import load_dotenv
import os
from loguru import logger


load_dotenv()

bot = telebot.TeleBot(os.getenv('token'))


@logger.catch
def create_db() -> None:
    """
    Функция по проверке существования базы данных и созданию её, в случае отсутствия.
    """
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS user(
                           reqid INTEGER PRIMARY KEY,
                           userid TEXT,
                           command TEXT,
                           time TEXT,
                           city TEXT,
                           city_id TEXT,
                           price TEXT,
                           dist TEXT,
                           hotelcount TINYINT,
                           photocount TINYINT,
                           results TEXT);
                        """)

    conn.commit()


@logger.catch
def add_info_to_db(column: str, info: str) -> None:
    """
    Функция по добавлению информации в указанный столбец БД
    :param column: принимает строковое значение названия столбца из БД
    :param info: принимает строковое значение информации, которую добавляет в БД
    """
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()

    if column == 'results':
        old_info = get_info_from_db(column)
        cur.execute(f"""UPDATE user SET '{column}' = "{old_info} {info}" WHERE reqid='{get_last_id()}'""")

    else:
        cur.execute(f"UPDATE user SET '{column}' = '{info}' WHERE reqid='{get_last_id()}'")
    conn.commit()


@logger.catch
def get_last_id() -> int:
    """
    Функция по поиску последней строки в БД
    :return: возвращает целочисленный номер последней записи в БД
    """
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM user;")
    try:
        return cur.fetchall()[-1][0]
    except IndexError:
        return False


@logger.catch
def get_info_from_db(column: str) -> str or int:
    """
    Функция предоставляет значение в указанном столбце в последней записи БД
    :param column: принимает строковое значение названия столбца из БД
    :return: возвращает строковое значение информации
    """
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    cur.execute(f"SELECT {column} FROM user WHERE reqid='{get_last_id()}';")
    one_result = cur.fetchone()[0]
    return one_result


@logger.catch
def new_row() -> None:
    """
    Функция, которая создает новую пустую запись(строку) в БД
    """
    create_db()
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    cur.execute(f"INSERT INTO user ('userid', 'command', 'city', 'hotelcount', 'photocount', 'results') "
                f"VALUES ('','','','','', '')")
    conn.commit()


@logger.catch
def print_db() -> None:
    """
    Функция, выводящая всю БД
    """
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM user;")
    all_result = cur.fetchall()
    for i in all_result:
        print(i)


@logger.catch
def show_history(user_id: str) -> str:
    """
    Функция, выдающая 2 последних записи из БД пользователю
    :param user_id: принимает строковое значение id пользователя Telegram
    :return: возвращает 2 последних записи из столбца results БД
    """
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    cur.execute(f"SELECT command, time, city, results FROM user "
                f"WHERE userid = '{user_id}' AND command != 'history' ORDER BY reqid DESC LIMIT 2")
    hist = ''
    for i_elem in cur.fetchall():
        hist += f'Город поиска: {i_elem[2]}\nКоманда: {i_elem[0]}\n' \
                f'Время вып-я команды: {i_elem[1]}\nРез-т поиска:\n{i_elem[3]}\n'
    return hist
