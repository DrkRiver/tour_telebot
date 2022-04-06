import sqlite3


def create_db():
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS user(
                           reqid INTEGER PRIMARY KEY,
                           userid TEXT,
                           command TEXT,
                           city TEXT,
                           city_id TEXT,
                           hotelcount TINYINT,
                           photocount TINYINT,
                           results TEXT);
                        """)

    conn.commit()


def add_info_to_db(column, info):
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()

    # TODO Добавить запись сайта отеля в рез-т (соед. url запроса и id отеля)

    if column == 'results':
        old_info = get_info_from_db(column)
        # print(old_info)
        cur.execute(f"UPDATE user SET '{column}' = '{old_info} {info}' WHERE reqid='{get_last_id()}'")

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
    cur.execute(f"INSERT INTO user ('userid', 'command', 'city', 'hotelcount', 'photocount', 'results') "
                f"VALUES ('','','','','', '')")
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
        hist += f'Город поиска: {i_elem[1]}\n\nКоманда: {i_elem[0]}\n\nРез-т поиска:\n{i_elem[2]}\n\n'
    # print(hist)
    return hist


# new_row()
# add_info_to_db(column='userid', info='253')
# add_info_to_db(column='command', info='lowprice')
# add_info_to_db(column='city', info='Denver')
# add_info_to_db(column='hotelcount', info='5')
# add_info_to_db(column='photocount', info='6')
# add_info_to_db('results', '1st bla')
# add_info_to_db('results', '2nd bla-bla')
# add_info_to_db('results', '3rd bla-bla-bla')
#
# #
# create_db()
# new_row()
# add_info_to_db(column='city_id', info='332483')
print_db()
