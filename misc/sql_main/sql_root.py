from flask import request
import sqlite3


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getAllUser(self):
        sql = f"SELECT ROWID, * FROM users"
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print(f"Ошибка БД: {e}")

    def getUser(self, login):
        sql = f"SELECT login, password, rule FROM users WHERE login = ? LIMIT 1"
        try:
            self.__cur.execute(sql, (login,))
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка БД " +str(e))
        return []

    def delete_user(self, id):
        sql = "DELETE FROM users WHERE rowid=?"
        try:
            self.__cur.execute(sql, str(id))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"Ошибка БД: {e}")

    def register_account(self, login, password):
        sql = "INSERT INTO users (login, password) VALUES (?, ?)"
        try:
            self.__cur.execute(sql, (login, password))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка регистрации " + str(e))
