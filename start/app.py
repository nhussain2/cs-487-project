from flask import Flask, render_template, redirect, url_for, session, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import update
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/naveedhussain/Desktop/start/database.db'
Bootstrap(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Orders(db.Model):
    orderid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15))
    order_date = db.Column(db.Text)
    cost = db.Column(db.Integer)
    items = db.Column(db.String)

class ItemsPurchased(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String)
    amount_purchased = db.Column(db.Integer)


class AccountInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    address = db.Column(db.String(300))
    rewards = db.Column(db.Integer)
    phone_number = db.Column(db.Integer)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if form.password.data == user.password:
                login_user(user, remember=form.remember.data)
                session['current_user'] = str(user.username)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/menu-1')
@login_required
def menu1():
    return render_template('menu-1.html')

@app.route('/dashboard')
@login_required
def dashboard():
    items_list= ItemsPurchased()
     
    items_names= ['1/4 White', '1/4 Dark','1/2 White','1/2 Dark','2 Wings','4 Wings','5 Wings','6 Wings','7 Wings','Extra Wing']

    items_prices = [6, 5.6,8.05, 6.95, 3.25, 6.35, 6.85, 7.35, 7.85, 1.5]

    for i in range(len(items_names)):
        current = items_names[i]
        x = ItemsPurchased.query.filter_by(item_name=current).first()
        if x:
            pass
        else:
            x = ItemsPurchased(item_name = items_names[i], amount_purchased="0")
            db.session.add(x)
            db.session.commit()

    name = dict(session).get('current_user')
    account = AccountInfo.query.filter_by(username=name).first()
    if account:
        rewards = account.rewards
        address = account.address
        number = account.phone_number
        return render_template('dashboard.html', name=name, address=address, number=number, rewards=rewards)

    return render_template('dashboard.html',name=name)

@app.route('/updateinfo', methods=['GET','POST'])
@login_required
def updateinfo():
    name = dict(session).get('current_user')
    return render_template("update_info.html", name=name)


@app.route('/updated', methods=['GET','POST'])
@login_required
def updated():
    name = dict(session).get('current_user')

    account = AccountInfo.query.filter_by(username=name).first()
    if account:
        account.address = request.values.get('updateaddress')
        account.phone_number = request.values.get('updatenumber')
        db.session.commit()
        return redirect('/dashboard')
    account= AccountInfo(username=name, address=request.values.get('updateaddress'), phone_number=request.values.get('updatenumber'), rewards='0')
    db.session.add(account)
    db.session.commit()

    session['number'] = account.phone_number
    session['address'] = account.address

    return redirect('/dashboard')

@app.route('/order', methods=['GET','POST'])
@login_required
def order():
    return render_template('order.html')

@app.route('/your-order',methods=['GET','POST'])
@login_required
def yourorder():
    name = dict(session).get('current_user')

    items_names= ['1/4 White', '1/4 Dark','1/2 White','1/2 Dark','2 Wings','4 Wings','5 Wings','6 Wings','7 Wings','Extra Wing']

    items = request.form.getlist('item')
    total = 0
    items_lst = []
    for i in items:
        if i == "1":
            x = ItemsPurchased.query.filter_by(item_name=items_names[0]).first()
            x.amount_purchased += 1
            db.session.commit()
            items_lst.append("1/4 White	6.00")
            total += 6.00
        elif i == "2":
            x = ItemsPurchased.query.filter_by(item_name=items_names[1]).first()
            x.amount_purchased += 1
            db.session.commit()
            items_lst.append("1/4 Dark 5.60")
            total += 5.60
        elif i == "3":
            x = ItemsPurchased.query.filter_by(item_name=items_names[2]).first()
            x.amount_purchased += 1
            db.session.commit()
            items_lst.append("1/2 White 8.05")
            total += 8.05
        elif i == "4":
            x = ItemsPurchased.query.filter_by(item_name=items_names[3]).first()
            x.amount_purchased += 1
            db.session.commit()
            items_lst.append("1/2 Dark 6.95")
            total += 6.95
        elif i == "5":
            x = ItemsPurchased.query.filter_by(item_name=items_names[4]).first()
            x.amount_purchased += 1
            db.session.commit()
            items_lst.append("2 Wings 3.25")
            total += 3.25
        elif i == "6":
            x = ItemsPurchased.query.filter_by(item_name=items_names[5]).first()
            x.amount_purchased += 1
            db.session.commit()
            items_lst.append("4 Wings 6.35")
            total += 6.35
        elif i == "7":
            x = ItemsPurchased.query.filter_by(item_name=items_names[6]).first()
            x.amount_purchased += 1
            db.session.commit()
            items_lst.append("5 Wings 6.85")
            total += 6.85
        elif i == "8":
            x = ItemsPurchased.query.filter_by(item_name=items_names[7]).first()
            x.amount_purchased += 1
            db.session.commit()
            items_lst.append("6 Wings 7.35")
            total += 7.35
        elif i == "9":
            x = ItemsPurchased.query.filter_by(item_name=items_names[8]).first()
            x.amount_purchased += 1
            db.session.commit()
            items_lst.append("7 Wings 7.85")
            total += 7.85
        elif i == "10":
            x = ItemsPurchased.query.filter_by(item_name=items_names[9]).first()
            x.amount_purchased += 1
            db.session.commit()
            items_lst.append("Extra Wing 1.50")
            total += 1.50
    rewards = total // 10
    length = len(items_lst)
    session['length'] = length

    user = AccountInfo.query.filter_by(username=name).first()
    if user:
        user.rewards += rewards
        db.session.commit()
    
    

    current_date = str(datetime.datetime.now())
    order = Orders(username=name, order_date= current_date, cost=total, items=str(items_lst))
    db.session.add(order)
    db.session.commit()
    session['id'] = order.orderid

    return render_template("your_order.html", items_lst = items_lst, total = total, length = length, rewards=rewards)

@app.route('/pay')
def pay():
    order_id = dict(session).get('id')
    name = dict(session).get('current_user')

    x = Orders.query.filter_by(orderid=order_id).first()
    total = x.cost

    user = AccountInfo.query.filter_by(username=name).first()
   
    if int(user.rewards) >= int(total):
        after_rewards = 0
        user.rewards -= total
        db.session.commit()
    else:
        after_rewards = int(total) - int(user.rewards)
        user.rewards = 0
        db.session.commit()

    length = dict(session).get('length')
    est_time = 20 + (int(length) * 10)
    rewards = user.rewards

    return render_template('paid.html', rewards=rewards, total=total, after_rewards=after_rewards,est_time=est_time)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/adminlogin', methods=['GET','POST'])
def adminlogin():
    return render_template('adminlogin.html')

@app.route('/admindash', methods=['GET','POST'])
def admindash():
    if request.form['adminuser'] == "admin":
        if request.form['adminpass'] == "adminpass":
            items = ItemsPurchased.query.all()
            orders= Orders.query.all()
            
            return render_template("admindash.html", items=items, orders=orders)
    return render_template("adminlogin.html", itemtable=itemtable)


if __name__ == '__main__':
    app.run(debug=True)