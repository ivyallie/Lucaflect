from flask import Flask, render_template
import pymysql

class Database:
    def __init__(self):
        host = 'localhost'
        user = 'ivy'
        password = ''
        db = 'lucaflect01'

        self.con = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.
                                   DictCursor)
        self.cur = self.con.cursor()

    def query(self, querytext):
        self.cur.execute(querytext)
        result = self.cur.fetchall()

        return result

