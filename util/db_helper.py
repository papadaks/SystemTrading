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