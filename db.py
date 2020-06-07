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

    def does_title_exist(self,title):
        title_query = "SELECT * FROM comic WHERE title='''" + title + "''';"
        self.cur.execute(title_query)
        return self.cur.fetchone()

    def write(self, querybase, values):
        print("Write called")
        #print(values)
        self.cur.execute(querybase, values)
        self.con.commit()
        print("Write finished")
        return True

    def user_and_post_match(self, user_id, comic_id):
        post_query = '''SELECT * FROM comic WHERE comic_id="''' + str(comic_id) + '''";'''
        self.cur.execute(post_query)
        post = self.cur.fetchone()
        post_author = post['author_id']
        if int(post_author) == int(user_id):
            return True
        else:
            return False


