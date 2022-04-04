import sqlite3


def create_db():
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS user(
                           reqid INTEGER PRIMARY KEY,
                           userid TEXT,
                           command TEXT,
                           city TEXT,
                           hotelcount TINYINT,
                           photocount TINYINT,
                           results TEXT);
                        """)

    conn.commit()


def add_info_to_db(column, info):
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()

    if column == 'results':  # TODO убрать запись None  БД
        old_info = cur.execute(f"SELECT results FROM user WHERE reqid='{get_last_id()}'").fetchone()[0]
        # if old_info.startswith('None'):
        #     old_info = old_info[4:]
        # print(old_info)
        cur.execute(f"UPDATE user SET '{column}' = '{old_info} {info}' WHERE reqid='{get_last_id()}'")
        # TODO Добавить запись сайта отеля в рез-т (соед. url запроса и id отеля),
        #  корректное название города поиска с регионом
    else:
        cur.execute(f"UPDATE user SET '{column}' = '{info}' WHERE reqid='{get_last_id()}'")
    conn.commit()


def get_last_id():
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM user;")
    try:
        return cur.fetchall()[-1][0]
    except IndexError:
        return False


def get_info_from_db(column):
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    cur.execute(f"SELECT {column} FROM user WHERE reqid='{get_last_id()}';")
    one_result = cur.fetchone()[0]
    # print(one_result)
    return one_result


def new_row():
    create_db()
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    cur.execute(f"INSERT INTO user ('userid') VALUES ('None')")
    conn.commit()


def print_db():
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM user;")
    all_result = cur.fetchall()
    for i in all_result:
        print(i)


def show_history(user_id):
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    cur.execute(f"SELECT command, city, results FROM user "
                f"WHERE userid = '{user_id}' AND command != 'history' ORDER BY reqid DESC LIMIT 2")
    # print(cur.fetchall())
    hist = ''
    for i_elem in cur.fetchall():
        # print(i_elem)
        hist += f' Город поиска: {i_elem[1]} \n Команда: {i_elem[0]} \n Рез-т поиска: {i_elem[2]} \n\n'
    # print(hist)
    return hist

# new_row()
# add_info_to_db(column='userid', info='253')
# add_info_to_db(column='command', info='lowprice')
# add_info_to_db(column='city', info='Denver')
# add_info_to_db(column='hotelcount', info='5')
# add_info_to_db(column='photocount', info='6')


# add_result_to_db(info='bla sg q3rtq herha')

print_db()

# show_history(974598507)
