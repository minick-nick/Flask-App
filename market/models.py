from market import db, app, login_manager
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
import locale

bcrypt = Bcrypt(app)

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

class User(db.Model, UserMixin):
  id = db.Column(db.Integer(), primary_key=True)
  username = db.Column(db.String(length=30), nullable=False, unique=True)
  email_address = db.Column(db.String(length=50), nullable=False, unique=True)
  password_hash = db.Column(db.String(length=60), nullable=False)
  budget = db.Column(db.Integer(), default=1000)    
  items = db.relationship('Item', backref='owned_user', lazy=True)

  @property
  def prettier_budget(self):
    # set locale to US
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    # format currency value
    formatted_budget = locale.currency(self.budget, grouping=True)
    return formatted_budget

  @property
  def password(self):
    return self.password

  @password.setter
  def password(self, plain_text_password):
    self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

  def check_password_correction(self, attempted_password):
    return bcrypt.check_password_hash(self.password_hash, attempted_password)

  def can_purchase(self, item_object):
    return self.budget >= item_object.price
  
  def can_sell(self, item_object):
    return item_object in self.items

class Item(db.Model):
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(length=30), nullable=False, unique=True)
  price = db.Column(db.Integer(), nullable=False)
  barcode = db.Column(db.String(length=12), nullable=False, unique=True)
  description = db.Column(db.String(length=1024), nullable=False, unique=True)
  owner = db.Column(db.Integer(), db.ForeignKey('user.id'))

  def buy(self, user):
    self.owner = user.id
    user.budget -= self.price
    db.session.commit()
  def sell(self, user):
    self.owner = None
    user.budget += self.price
    db.session.commit()

  def __repr__(self):
    return f'Item {self.name}'

