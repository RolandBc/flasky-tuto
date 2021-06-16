from werkzeug.security import generate_password_hash, check_password_hash

class Role():
    __tablename__ = 'roles'
    id = 1
    name = 'rup'

    def __repr__(self):
        return '<Role %r>' % self.name

class User():
    __tablename__ = 'users'
    id = 1
    username = 'rolls'

    def __repr__(self) -> str:
        return '<User %r>' % self.username