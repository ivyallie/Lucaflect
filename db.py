from flask import current_app
import pymysql

class Database:
    def __init__(self):
        host = current_app.config['MYSQL_HOST']
        user = current_app.config['MYSQL_USER']
        password = current_app.config['MYSQL_PASSWORD']
        db = current_app.config['MYSQL_DB']

        self.con = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.
                                   DictCursor)
        self.cur = self.con.cursor()

    def query(self, querytext):
        self.cur.execute(querytext)
        result = self.cur.fetchall()

        return result

    def query_user(self,email):
        user_query = '''SELECT * FROM user WHERE username="''' + email + '";'
        self.cur.execute(user_query)
        return self.cur.fetchone()

    def query_user_id(self,id):
        user_query = '''SELECT * FROM user where user_id="''' + str(id) + '";'
        self.cur.execute(user_query)
        return self.cur.fetchone()

    def write(self, querybase,values):
        print("Write called")
        self.cur.execute(querybase,values)
        self.con.commit()

        return True


