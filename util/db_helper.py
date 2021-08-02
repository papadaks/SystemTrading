# import sqlite3
# # conn = sqlite3.connect('universe_price.db')
# conn = sqlite3.connect('universe_price.db', isolation_level=None)
# cur = conn.cursor()
# # cur.execute('''CREATE TABLE balance
# #                 (
# #                  code varchar(6) PRIMARY KEY,
# #                  bid_price int(20) NOT NULL,
# #                  quantity int(20) NOT NULL,
# #                  created_at varchar(14) NOT NULL,
# #                  will_clear_at varchar(14)
# #                )''')
#
# sql = "insert into Balance(code, bid_price, quantity, created_at, will_clear_at) values (?, ?, ?, ?, ?)"
# cur.execute(sql, ('017710', 35000, 30, '20201222', 'today'))
# print(cur.rowcount)

#
# import sqlite3
# conn = sqlite3.connect('universe_price.db', isolation_level=None)
#
# cur = conn.cursor()
#
#
# sql = "delete from balance where will_clear_at=:will_clear_at"
# cur.execute(sql, {"will_clear_at": "next"})
#


#################################################################
# 책에 나오는 코드
import sqlite3


def check_table_exist(db_name, table_name):
    with sqlite3.connect('{}.db'.format(db_name)) as con:
        cur = con.cursor()
        sql = "SELECT name FROM sqlite_master WHERE type='table' and name=:table_name"
        cur.execute(sql, {"table_name": table_name})

        if len(cur.fetchall()) > 0:
            return True
        else:
            return False


def insert_df_to_db(db_name, table_name, df, option="replace"):
   with sqlite3.connect('{}.db'.format(db_name)) as con:
       df.to_sql(table_name, con, if_exists=option)


def execute_sql(db_name, sql, param={}):
   with sqlite3.connect('{}.db'.format(db_name)) as con:
       cur = con.cursor()
       cur.execute(sql, param)
       return cur


if __name__ == "__main__":
    pass