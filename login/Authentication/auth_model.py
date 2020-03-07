from login import db, ma
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'flasklogin-users'

    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String(100),
                     nullable=False,
                     unique=False)
    email = db.Column(db.String(40),
                      unique=True,
                      nullable=False)
    password = db.Column(db.String(200),
                         primary_key=False,
                         unique=False,
                         nullable=True)

    def __init__(self,data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.email = data.get('email')
        self.password = data.get('password')

    def save_user(self) -> None:
        self.set_password(self.password)
        db.session.add(self)
        db.session.commit()

    def set_password(self, password) -> None:
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password) -> bool:
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.name)

    @classmethod
    def find_by_mail_id(cls, mail: str) -> "User":
        return cls.query.filter_by(email=mail).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "User":
        return cls.query.filter_by(id=_id).first()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()




"""class User_schema(ma.Schema):
    class Meta:
        model = User
        fields = ("name", "email", "id","password")
        load_only = ("password",)
        dump_only = ("id",)"""


class User_schema(ma.SQLAlchemySchema):
    class Meta:
        model=User
    id = ma.auto_field(dump_only= True)
    name = ma.auto_field()
    password = ma.auto_field(allow_none=True, load_only=True)
    email = ma.auto_field()


























