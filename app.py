from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask import url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash

app=Flask(__name__)
app.secret_key = 'WOODENPLATERESTAURANT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

app.app_context().push()
db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

session={}

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/signup',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user:
        flash('Email address already exists')
        return redirect(url_for('signup'))
    new_user = User(username=name, email=email, password=generate_password_hash(password, method='pbkdf2:sha256'))
    db.session.add(new_user)
    db.session.commit()
    flash('Successfully created the account')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('profile'))
    return render_template("login.html")

@app.route('/book_table', methods=['GET', 'POST'])
def book_table():
    if request.method == 'POST':
        num_people = request.form.get('num_people')
        date = request.form.get('date')
        time = request.form.get('time')
        notes = request.form.get('notes')
        return redirect(url_for('booking_details', num_people=num_people, date=date, time=time, notes=notes))
    return render_template('book_table.html')

@app.route('/booking_details')
def booking_details():
    num_people = request.args.get('num_people')
    date = request.args.get('date')
    time = request.args.get('time')
    notes = request.args.get('notes')
    return render_template('booking_details.html', num_people=num_people, date=date, time=time, notes=notes)

@app.route('/place_order', methods=['GET', 'POST'])
def place_order():
    menu_items = [
        {"id": 1, "name": "Pasta", "price": 200},
        {"id": 2, "name": "Pizza", "price": 300},
        {"id": 3, "name": "Burger", "price": 150},
        {"id": 4, "name": "Salad", "price": 100},
        {"id": 5, "name": "Soup", "price": 120},
        {"id": 6, "name": "Sandwich", "price": 180},
        {"id": 7, "name": "Fries", "price": 90},
        {"id": 8, "name": "Ice Cream", "price": 80},
        {"id": 9, "name": "Coffee", "price": 60},
        {"id": 10, "name": "Juice", "price": 70},
    ]
    if request.method == 'POST':
        order = {}
        total_price = 0
        for item in menu_items:
            quantity = request.form.get(f'quantity_{item["id"]}')
            if quantity and int(quantity) > 0:
                order[item["name"]] = int(quantity)
                total_price += item["price"] * int(quantity)
        return redirect(url_for('order_details'))
    return render_template('place_order.html', menu_items=menu_items)

@app.route('/order', methods=['GET','POST'])
def order_details():
    return render_template('order_details.html')

@app.route('/profile')
def profile():
    return render_template("profile.html",user = current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('logout'))

app.run(debug=True)
