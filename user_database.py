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
    old_info = cur.execute(f"SELECT results FROM user WHERE reqid='{get_last_id()}'").fetchone()[0]
    cur.execute(f"UPDATE user SET '{column}' = '{info}' WHERE reqid='{get_last_id()}'")
    conn.commit()


def add_result_to_db(info):
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    old_info = cur.execute(f"SELECT results FROM user WHERE reqid='{get_last_id()}'").fetchone()[0]
    # print(old_info)
    cur.execute(f"UPDATE user SET results = '{old_info} {info}' WHERE reqid='{get_last_id()}'")
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


# new_row()
# add_info_to_db(column='userid', info='253')
# add_info_to_db(column='command', info='lowprice')
# add_info_to_db(column='city', info='Denver')
# add_info_to_db(column='hotelcount', info='5')
# add_info_to_db(column='photocount', info='6')


# add_result_to_db(info='bla sg q3rtq herha')

# print_db()
