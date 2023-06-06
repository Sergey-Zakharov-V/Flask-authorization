from flask_login import UserMixin


class UserLogin(UserMixin):
    def fromDB(self, user_login, db):
        self.__user = db.getUser(user_login)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['login'])
    