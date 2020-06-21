from flask import current_app
import pymysql
from json import loads

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

    def query_user(self,name):
        user_query = '''SELECT * FROM user WHERE username="''' + name + '";'
        self.cur.execute(user_query)
        return self.cur.fetchone()

    def query_user_id(self,id):
        user_query = '''SELECT * FROM user where user_id="''' + str(id) + '";'
        self.cur.execute(user_query)
        return self.cur.fetchone()

    def does_title_exist(self,title,table='comic'):
        title_query = '''SELECT * FROM '''+table+''' WHERE title="''' + title + '''";'''
        self.cur.execute(title_query)
        return self.cur.fetchone()

    def write(self, querybase, values):
        print("Write called")
        #print(values)
        self.cur.execute(querybase, values)
        self.con.commit()
        print("Write finished")
        return True

    def delete_comic(self,id):
        query = '''DELETE FROM comic WHERE comic_id="'''+str(id)+'''";'''
        self.cur.execute(query)
        self.con.commit()
        print('Deleted comic')
        return True

    def user_and_post_match(self, user_id, comic_id, table):
        id_column=table+"_id"
        post_query = '''SELECT * FROM '''+table+''' WHERE '''+id_column+'''="''' + str(comic_id) + '''";'''
        self.cur.execute(post_query)
        post = self.cur.fetchone()
        post_author = post['author_id']
        if int(post_author) == int(user_id):
            return True
        else:
            return False

    def existSetting(self,settingname):
        setting_query = '''SELECT * FROM lucaflect WHERE name=%s;'''
        self.cur.execute(setting_query,settingname)
        if self.cur.fetchone():
            return True
        else:
            new_setting = '''INSERT INTO lucaflect (name) VALUE (%s)'''
            self.cur.execute(new_setting,settingname)
            self.con.commit()
            return True

    def getSetting(self,settingname):
        setting_query = '''SELECT * FROM lucaflect WHERE name=%s;'''
        self.cur.execute(setting_query, settingname)
        setting = self.cur.fetchone()
        if setting:
            short = str(setting['shortvalue'])
            long = str(setting['longvalue'])
            if short!='None':
                if short == 'True':
                    return True
                elif short == 'False':
                    return False
                else:
                    return short
            elif long!='None':
                return loads(long)
            else:
                return False
        else:
            return False


