import smtplib
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask_mysqldb import MySQL
import MySQLdb.cursors

import Applicant
import Cart
import Item
import Resend
import appointments
import qns
import shelve
from Forms import *
from pyechart import bargraph, applicationbargraph, addressbargraph, agerangebargraph, monthlyQnbargraph, usernumber
from flask_recaptcha import ReCaptcha   # Edited by Jabez (pip install Flask-reCaptcha)

app = Flask(__name__, static_url_path='/static')
# Edited by Jabez (Start)
recaptcha = ReCaptcha(app=app)

app.config.update(dict(
    RECAPTCHA_ENABLED=True,
    RECAPTCHA_SITE_KEY="6LcSa3wbAAAAANmKm0NqzQa9ZwAMsKfDcsRQIb8E",
    RECAPTCHA_SECRET_KEY="6LcSa3wbAAAAALbtlSk5wy9VVO9XNqGGCjZ6m_mC",
))

recaptcha = ReCaptcha()
recaptcha.init_app(app)
app.config["SECRET_KEY"] = b'o5Dg987*&G^@(E&FW)}'
# Edited by Jabez (End)

# Email Server
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "nanyanghospital2021@gmail.com"
app.config["MAIL_PASSWORD"] = "flaskapp123"
app.config["DEFAULT_MAIL_SENDER"] = "nanyanghospital2021@gmail.com"

# SQL Server
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'nanyang_login'

# Initialize MySQL
mysql = MySQL(app)
mail = Mail(app)


@app.route('/')
def home():
    return render_template('home.html')


# Register system
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        NRIC = form.NRIC.data
        fname = form.FirstName.data
        lname = form.LastName.data
        gender = form.Gender.data
        dob = form.Dob.data
        email = form.Email.data
        password = form.Password.data

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        user_exist = cursor.execute('SELECT * FROM users WHERE nric = %s', (NRIC,))
        if user_exist:
            flash("This NRIC is already in used. You can login to access our service.", "danger")
            return redirect(url_for('register'))
        else:
            cursor.execute('INSERT INTO users (NRIC, fname, lname, gender, dob, email, password, role, attempt) '
                           'VALUES (%s, %s, %s, %s, %s, %s, %s, "Patient", 0)',
                           (NRIC, fname, lname, gender, dob, email, password,))
            mysql.connection.commit()
            flash(f'Account created for {form.FirstName.data} {form.LastName.data}!', 'success')
            return redirect(url_for('login'))
    return render_template('Login/register.html', form=form)


# Login system
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    print(session['attempt'])   # checking only (to be removed)
    if request.method == "POST" and form.validate():
        NRIC = form.NRIC.data
        password = form.Password.data

        print(session['attempt'])
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE NRIC = %s AND password = %s', (NRIC, password))
        account = cursor.fetchone()
        # Edited by Jabez (start)
        cursor.execute('SELECT NRIC, attempt FROM users WHERE NRIC = %s', (NRIC,))
        attempt_dict = cursor.fetchone()
        # Check if user is real and user's attempt is more than 5
        if session['attempt'] >= 3:
            if recaptcha.verify():
                print('New Device Added successfully')
                if attempt_dict and attempt_dict['attempt'] >= 10:
                    # do not allow the user to login and flash incorrect password
                    flash('Your account have been locked!', 'danger')
                    # add timer
                # Edited by Jabez (end)
                elif account:
                    # resetting the attempts back to 0
                    cursor.execute('UPDATE users SET attempt = 0 WHERE NRIC = %s', (NRIC,))  # Edited by Jabez
                    mysql.connection.commit()  # Edited by Jabez
                    session["user"] = account
                    session["user-name"] = account["fname"] + " " + account["lname"]
                    session["user-NRIC"] = account["nric"]
                    session["user-role"] = account["role"]
                    session.pop("attempt", None)
                    flash(
                        f'{account["fname"]} {account["lname"]} has logged in!',
                        'success')
                    return redirect(url_for('home'))
                else:
                    flash('Incorrect username or password', 'danger')
                    # SQL adding and counting failed attempts
                    cursor.execute('UPDATE users SET attempt = attempt + 1 WHERE NRIC = %s', (NRIC,))  # Edited by Jabez
                    mysql.connection.commit()  # Edited by Jabez
            else:
                print('Error ReCaptcha')
        else:   # When attempt is not more than 3
            if account:
                # resetting the attempts back to 0
                cursor.execute('UPDATE users SET attempt = 0 WHERE NRIC = %s', (NRIC,))  # Edited by Jabez
                mysql.connection.commit()  # Edited by Jabez
                session["user"] = account
                session["user-name"] = account["fname"] + " " + account["lname"]
                session["user-NRIC"] = account["nric"]
                session["user-role"] = account["role"]
                session.pop("attempt", None)
                flash(
                    f'{account["fname"]} {account["lname"]} has logged in!',
                    'success')
                return redirect(url_for('home'))
            else:
                flash('Incorrect username or password', 'danger')
                # SQL adding and counting failed attempts
                cursor.execute('UPDATE users SET attempt = attempt + 1 WHERE NRIC = %s', (NRIC,))  # Edited by Jabez
                mysql.connection.commit()  # Edited by Jabez
                session["attempt"] += 1
    return render_template('Login/login.html', form=form)


# Logout system
@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("user-NRIC", None)
    session.pop("user-role", None)
    return redirect(url_for("home"))


# Profile System
@app.route('/profile', methods=["GET", "POST"])
def profile():
    form = UpdateProfileForm(request.form)

    NRIC = session["user-NRIC"]

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    user = session["user"]

    if request.method == "POST" and form.validate():
        cursor.execute('UPDATE users SET email = %s, dob = %s WHERE NRIC = %s', (form.Email.data, form.Dob.data, NRIC,))
        mysql.connection.commit()  # Edited by Jabez
        cursor.execute('SELECT * from users')  # Edited by Jabez
        account = cursor.fetchone()  # Edited by Jabez
        session["user"] = account  # Edited by Jabez
        return redirect(url_for('profile'))  # Edited by Jabez

    return render_template("Login/profile.html", form=form, user=user)


# User password management
@app.route('/change_password', methods=["GET", "POST"])
def change_password():
    form = ChangePasswordForm(request.form)

    NRIC = session["user-NRIC"]

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST" and form.validate():
        cursor.execute('UPDATE users SET password = %s WHERE NRIC = %s', (form.Password.data, NRIC,))
        mysql.connection.commit()  # Edited by Jabez
        return redirect(url_for('home'))

    return render_template('Login/change_password.html', form=form)


# Helper functions to reset email
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECRET_KEY'])


def confirm_token(token, expiration=300):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECRET_KEY'],
            max_age=expiration
        )
    except:
        return False
    return email


@app.route('/reset_password', methods=["GET", "POST"])
def reset_password():
    form = ResetPasswordForm(request.form)

    if request.method == "POST" and form.validate():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (form.Email.data,))

        token = generate_confirmation_token(form.Email.data)
        msg = Message(subject="Password reset", recipients=[form.Email.data],
                      body="Link to reset password : {}{}. Link valid for only 5 minutes" \
                      .format(request.url_root, url_for("confirm_reset", token=token)),
                      sender="nanyanghospital2021@gmail.com")
        mail.send(msg)

        flash("Successfully entered email, if you have registered an account with us, a reset password email would"
              " be sent to your email", "success")

        return redirect(url_for("home"))

    else:
        flash("Email not found! Please register your email.", "danger")

    return render_template("Login/reset_password.html", form=form)


@app.route('/confirm_reset/<token>', methods=["GET", "POST"])
def confirm_reset(token):
    form = ChangePasswordForm(request.form)

    NRIC = session["user-NRIC"]

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == "POST" and form.validate():
        cursor.execute('UPDATE users SET password = %s WHERE NRIC = %s', (form.Password.data, NRIC,))
        mysql.connection.commit()  # Edited by Jabez
        flash("Successfully reset password", "success")
        return redirect(url_for("login"))

    else:
        email = confirm_token(token)
        if email:
            return render_template("Login/new_password.html", token=token, form=form)
        else:
            flash("Token expired, please try again", "danger")
            return redirect(url_for('home'))


# Online Pharmacy
# Categories
@app.route('/pharmacy', methods=['GET', 'POST'])
def show_items():
    search = SearchBar(request.form)
    if request.method == 'POST':
        db = shelve.open('storage.db', 'r')
        item_dict = db['Items']
        db.close()

        item_list = []
        start_item_list = []
        contain_item_list = []
        for key in item_dict:
            item = item_dict.get(key)
            if not isinstance(item, Item.Prescribed):
                if item.get_item_name().lower().startswith(search.search.data.lower()):
                    start_item_list.append(item)
                elif search.search.data.lower() in item.get_item_name().lower():
                    contain_item_list.append(item)

            item_list = start_item_list + contain_item_list

        return render_template('Pharmacy/pharmacy.html', items_list=item_list, form=search)

    db = shelve.open('storage.db', 'r')
    item_dict = db['Items']
    db.close()

    item_list = []
    for key in item_dict:
        item = item_dict.get(key)
        if not isinstance(item, Item.Prescribed):
            item_list.append(item)

    return render_template('Pharmacy/pharmacy.html', items_list=item_list, form=search)


@app.route('/pharmacy/hot', methods=['GET', 'POST'])
def show_hot():
    search = SearchBar(request.form)
    if request.method == 'POST':

        db = shelve.open('storage.db', 'r')
        item_dict = db['Items']
        db.close()

        item_list = []
        start_item_list = []
        contain_item_list = []
        for key in item_dict:
            item = item_dict.get(key)
            if "hot" in item.get_item_tag() and not isinstance(item, Item.Prescribed):
                if item.get_item_name().lower().startswith(search.search.data.lower()):
                    start_item_list.append(item)
                elif search.search.data.lower() in item.get_item_name().lower():
                    contain_item_list.append(item)

                item_list = start_item_list + contain_item_list

        return render_template('Pharmacy/pharmacy.html', items_list=item_list, form=search)

    db = shelve.open('storage.db', 'r')
    item_dict = db['Items']
    db.close()

    item_list = []
    for key in item_dict:
        item = item_dict.get(key)
        if "hot" in item.get_item_tag() and not isinstance(item, Item.Prescribed):
            if not isinstance(item, Item.Prescribed):
                item_list.append(item)

    return render_template('Pharmacy/pharmacy.html', items_list=item_list, form=search)


@app.route('/pharmacy/limited', methods=['GET', 'POST'])
def show_limited():
    search = SearchBar(request.form)
    if request.method == 'POST':
        db = shelve.open('storage.db', 'r')
        item_dict = db['Items']
        db.close()

        item_list = []
        start_item_list = []
        contain_item_list = []
        for key in item_dict:
            item = item_dict.get(key)
            if item.get_item_tag() < 100 and not isinstance(item, Item.Prescribed):
                if item.get_item_name().lower().startswith(search.search.data.lower()):
                    start_item_list.append(item)
                elif search.search.data.lower() in item.get_item_name().lower():
                    contain_item_list.append(item)

                item_list = start_item_list + contain_item_list

        return render_template('Pharmacy/pharmacy.html', items_list=item_list, form=search)

    db = shelve.open('storage.db', 'r')
    item_dict = db['Items']
    db.close()

    item_list = []
    for key in item_dict:
        item = item_dict.get(key)
        if item.get_item_have() < 100 and not isinstance(item, Item.Prescribed):
            item_list.append(item)

    return render_template('Pharmacy/pharmacy.html', items_list=item_list, form=search)


@app.route('/pharmacy/new', methods=['GET', 'POST'])
def show_new():
    search = SearchBar(request.form)
    if request.method == 'POST':
        db = shelve.open('storage.db', 'r')
        item_dict = db['Items']
        db.close()

        item_list = []
        start_item_list = []
        contain_item_list = []
        for key in item_dict:
            item = item_dict.get(key)
            if "new" in item.get_item_tag() and not isinstance(item, Item.Prescribed):
                if item.get_item_name().lower().startswith(search.search.data.lower()):
                    start_item_list.append(item)
                elif search.search.data.lower() in item.get_item_name().lower():
                    contain_item_list.append(item)

                item_list = start_item_list + contain_item_list

        return render_template('Pharmacy/pharmacy.html', items_list=item_list, form=search)

    db = shelve.open('storage.db', 'r')
    item_dict = db['Items']
    db.close()

    item_list = []
    for key in item_dict:
        item = item_dict.get(key)
        if "new" in item.get_item_tag() and not isinstance(item, Item.Prescribed):
            item_list.append(item)

    return render_template('Pharmacy/pharmacy.html', items_list=item_list, form=search)


@app.route('/purchaseHistory', methods=['GET', 'POST'])
def purchaseHistory():
    search = SearchBar(request.form)
    user_id = session["user-NRIC"]

    if request.method == "POST":
        sort_amount = search.history.data
        if search.search.data != "":
            db = shelve.open('storage.db', 'c')
            cart_dict = db['Paid']

            cart_list = []
            for key in cart_dict:
                cart = cart_dict[key]
                if cart.get_owner() == user_id and cart.get_id() == int(search.search.data):
                    cart_list.append(cart)

            return render_template('Pharmacy/purchaseHistory.html', form=search, cart_list=cart_list)
        elif sort_amount is not None:
            db = shelve.open('storage.db', 'c')
            cart_dict = db['Paid']

            cart_list = []
            for key in cart_dict:
                cart = cart_dict[key]
                if cart.get_owner() == user_id:
                    cart_list.append(cart)

            reverse_cart_list = list(reversed(cart_list))
            cart_list = []

            for cart in reverse_cart_list:
                if len(cart_list) < int(sort_amount):
                    cart_list.append(cart)
                else:
                    break

            return render_template('Pharmacy/purchaseHistory.html', form=search, cart_list=cart_list)
        else:
            return redirect(url_for('purchaseHistory'))

    db = shelve.open('storage.db', 'c')
    cart_dict = db['Paid']

    cart_list = []
    for key in cart_dict:
        cart = cart_dict[key]
        if cart.get_owner() == user_id:
            cart_list.append(cart)

    reverse_cart_list = list(reversed(cart_list))
    cart_list = []

    for cart in reverse_cart_list:
        if len(cart_list) < 10:
            cart_list.append(cart)
        else:
            break

    return render_template('Pharmacy/purchaseHistory.html', form=search, cart_list=cart_list)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    total_sales = int()
    general_list = list()
    general_low_list = list()
    prescribed_list = list()
    prescribed_low_list = list()
    paid_list = list()
    pres_list = list()
    db = shelve.open('storage.db', 'r')
    paid_dict = db['Paid']
    pres_dict = db['Prescription']
    item_dict = db['Items']
    db.close()

    for key in paid_dict:
        paid = paid_dict[key]
        total_sales += paid.total()
        paid_list.append(paid)

    reverse_paid_list = reversed(paid_list)
    paid_list = []

    for cart in reverse_paid_list:
        if len(paid_list) < 10:
            paid_list.append(cart)

    for key in pres_dict:
        pres = pres_dict[key]
        pres_list.append(pres)

    reverse_pres_list = reversed(pres_list)
    pres_list = []

    for cart in reverse_pres_list:
        if len(pres_list) < 10:
            pres_list.append(cart)

    for key in item_dict:
        item = item_dict[key]
        if not isinstance(item, Item.Prescribed):
            general_list.append(item)
            if item.get_item_have() < 100:
                general_low_list.append(item)
        else:
            prescribed_list.append(item)
            if item.get_item_have() < 100:
                prescribed_low_list.append(item)

    no_paid = len(paid_dict)
    no_items = len(item_dict)
    no_general = len(general_list)
    no_prescribed = len(prescribed_list)
    no_pres = len(pres_dict)

    return render_template('Pharmacy/dashboard.html', pres_list=pres_list, paid_list=paid_list,
                           glow_list=general_low_list, plow_list=prescribed_low_list, no_general=no_general,
                           no_prescribed=no_prescribed, no_paid=no_paid, no_items=no_items, no_pres=no_pres,
                           total=total_sales)


# CRUD Items
@app.route('/createItem', methods=['GET', 'POST'])
def create_item():
    create_item_form = CreateItemForm(request.form)
    if request.method == 'POST' and create_item_form.validate():
        item_dict = {}
        db = shelve.open('storage.db', 'c')

        try:
            item_dict = db['Items']
        except:
            print("Error in retrieving Items from storage.db.")
        if not create_item_form.prescription.data:
            item = Item.Item(create_item_form.name.data, round(create_item_form.price.data, 2),
                             create_item_form.have.data,
                             create_item_form.bio.data, create_item_form.picture.data)
        else:
            item = Item.Prescribed(create_item_form.name.data, round(create_item_form.price.data, 2),
                                   create_item_form.have.data,
                                   create_item_form.bio.data, create_item_form.picture.data)

        item_dict[item.get_item_id()] = item
        if isinstance(item, Item.Item):
            item.add_item_tag('new')
        db['Items'] = item_dict

        db.close()

        return redirect(url_for('inventory'))
    return render_template('Pharmacy/createItem.html', form=create_item_form)


@app.route('/inventory')
def inventory():
    db = shelve.open('storage.db', 'r')
    item_dict = db['Items']
    db.close()

    item_list = []
    for key in item_dict:
        item = item_dict.get(key)
        item_list.append(item)

    return render_template('Pharmacy/inventory.html', items_list=item_list)


@app.route('/updateItem/<int:id>/', methods=['GET', 'POST'])
def update_item(id):
    update_item_form = CreateItemForm(request.form)

    if request.method == 'POST' and update_item_form.validate():
        db = shelve.open('storage.db', 'w')
        item_dict = db['Items']

        item = item_dict.get(id)
        item.set_item_name(update_item_form.name.data)
        item.set_item_price(update_item_form.price.data)
        item.set_item_have(update_item_form.have.data)
        item.set_item_bio(update_item_form.bio.data)
        item.set_item_picture(update_item_form.picture.data)

        db['Items'] = item_dict
        db.close()

        return redirect(url_for('inventory'))
    else:
        db = shelve.open('storage.db', 'r')
        item_dict = db['Items']
        db.close()

        item = item_dict.get(id)
        update_item_form.name.data = item.get_item_name()
        update_item_form.price.data = item.get_item_price()
        update_item_form.have.data = item.get_item_have()
        update_item_form.bio.data = item.get_item_bio()
        update_item_form.picture.data = item.get_item_picture()

        return render_template('Pharmacy/updateItem.html', form=update_item_form)


@app.route('/deleteItem/<int:id>', methods=['POST'])
def delete_item(id):
    db = shelve.open('storage.db', 'w')
    item_dict = db['Items']

    item_dict.pop(id)

    db['Items'] = item_dict
    db.close()

    return redirect(url_for('inventory'))


# CRUD Shopping Cart
@app.route('/purchaseItem/<int:id>/', methods=['GET', 'POST'])
def buy_item(id):
    buy_item_form = BuyItemForm(request.form)

    if request.method == 'POST' and buy_item_form.validate():
        db = shelve.open('storage.db', 'w')
        item_dict = db['Items']
        cart_dict = db['Cart']

        user_id = session["user-NRIC"]

        item = item_dict.get(id)
        item.set_item_want(buy_item_form.want.data)

        try:
            cart = cart_dict[user_id]

            if item.get_item_want() > item.get_item_have():
                item.set_item_want(0)
                flash("Not enough stock at the moment, try again later", 'danger')
            elif cart.check(item):
                cart.remove(item)
                item.set_item_want(buy_item_form.want.data)
                cart.add(item)
            else:
                cart.add(item)

        except KeyError:
            temp_cart = [item]
            cart = Cart.Cart(temp_cart)
            cart_dict[user_id] = cart

        finally:
            db['Cart'] = cart_dict
            db['Items'] = item_dict
            db.close()

        return redirect(url_for('show_items'))

    else:
        db = shelve.open('storage.db', 'r')
        item_dict = db['Items']
        db.close()

        item = item_dict.get(id)
        buy_item_form.want.data = item.get_item_want()

        return render_template('Pharmacy/buyItem.html', form=buy_item_form, name=item.get_item_name(),
                               bio=item.get_item_bio(), price=item.get_item_price(), picture=item.get_item_picture(),
                               have=item.get_item_have())


@app.route('/shoppingCart', methods=['GET', 'POST'])
def shopping_cart():
    search = SearchBar(request.form)
    if request.method == 'POST':
        db = shelve.open('storage.db', 'r')
        cart_dict = db['Cart']
        db.close()

        user_id = session["user-NRIC"]

        try:
            cart = cart_dict[user_id]
        except KeyError:
            cart = Cart.Cart([])

        item_list = cart.get_cart()
        total = cart.total()
        count = cart.get_count()

        start_item_list = []
        contain_item_list = []
        for item in cart.get_cart():
            if item.get_item_name().lower().startswith(search.search.data.lower()):
                start_item_list.append(item)
            elif search.search.data.lower() in item.get_item_name().lower():
                contain_item_list.append(item)

            item_list = start_item_list + contain_item_list

        return render_template('Pharmacy/shoppingCart.html', items_list=item_list, form=search, total=total,
                               count=count)
    db = shelve.open('storage.db', 'r')
    cart_dict = db['Cart']
    db.close()

    user_id = session["user-NRIC"]

    try:
        cart = cart_dict[user_id]
    except KeyError:
        cart = Cart.Cart([])

    item_list = cart.get_cart()
    total = cart.total()
    count = cart.get_count()

    return render_template('Pharmacy/shoppingCart.html', items_list=item_list, form=search, total=total, count=count)


@app.route('/shoppingCart/<int:id>', methods=['GET', 'POST'])
def specific_cart(id):
    search = SearchBar(request.form)
    if request.method == 'POST':
        db = shelve.open('storage.db', 'r')
        cart_dict = db['Paid']
        db.close()

        cart = cart_dict[id]

        item_list = cart.get_cart()
        total = cart.total()
        count = cart.get_count()

        start_item_list = []
        contain_item_list = []
        for item in cart.get_cart():
            if item.get_item_name().lower().startswith(search.search.data.lower()):
                start_item_list.append(item)
            elif search.search.data.lower() in item.get_item_name().lower():
                contain_item_list.append(item)

            item_list = start_item_list + contain_item_list

        return render_template('Pharmacy/shoppingCart.html', items_list=item_list, form=search, total=total,
                               count=count)
    db = shelve.open('storage.db', 'r')
    cart_dict = db['Paid']
    db.close()

    cart = cart_dict[id]

    item_list = cart.get_cart()
    total = cart.total()
    count = cart.get_count()

    return render_template('Pharmacy/shoppingCart.html', items_list=item_list, form=search, total=total, count=count)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    checkout_form = CheckoutForm(request.form)

    if (request.method == 'POST' and checkout_form.validate()) or session["user-role"] == 'Admin':
        try:
            session["user"]
        except KeyError:
            return redirect(url_for('paid'))
        else:
            db = shelve.open('storage.db', 'w')
            cart_dict = db['Cart']
            item_dict = db['Items']
            paid_dict = db['Paid']

            user_id = session["user-NRIC"]
            email = session["user"]['email']

            cart = cart_dict[user_id]

            paid = Cart.PaidCart(cart.get_cart())

            paid_dict[paid.get_id()] = paid

            paid.set_owner(user_id)

            db['Paid'] = paid_dict

            cart.checkout()
            cart_dict.pop(user_id)

            for key in item_dict:
                item = item_dict[key]
                if item.get_item_want() != 0:
                    item.set_item_have(item.get_item_have() - item.get_item_want())
                    item.set_item_want(0)
                    if "hot" not in item.get_item_tag() and not isinstance(item, Item.Prescribed):
                        item.add_item_tag('hot')

            db['Items'] = item_dict
            db['Cart'] = cart_dict
            db.close()

            msg = Message(subject='Nanyang Polyclinic order confirmation',
                          sender=app.config.get("MAIL_USERNAME"),
                          recipients=[email],
                          body='Your Purchase with Nanyang Polyclinic has been confirmed \n Cart Number: ' + str(
                              paid.get_id()))
            mail.send(msg)

            return redirect(url_for('paid'))
    return render_template('Pharmacy/checkout.html', form=checkout_form)


@app.route('/removeItem/<int:id>', methods=['POST'])
def remove_item(id):
    db = shelve.open('storage.db', 'c')
    item_dict = db['Items']
    cart_dict = db['Cart']

    user_id = session["user-NRIC"]

    cart = cart_dict[user_id]

    item = item_dict.get(id)
    item.set_item_want(0)
    cart.remove(item)

    db['Items'] = item_dict
    db['Cart'] = cart_dict
    db.close()

    return redirect(url_for('shopping_cart'))


@app.route('/clearCart', methods=['POST'])
def clear_cart():
    db = shelve.open('storage.db', 'w')
    cart_dict = db['Cart']

    user_id = session["user-NRIC"]

    cart = cart_dict[user_id]
    cart.clear_cart()

    db['Cart'] = cart_dict
    db.close()

    return redirect(url_for('shopping_cart'))


@app.route('/complete')
def paid():
    return render_template('Pharmacy/complete.html')


# CRUD Prescription
@app.route('/prescription', methods=['GET', 'POST'])
def prescription():
    search = SearchBar(request.form)
    if request.method == 'POST':
        db = shelve.open('storage.db', 'r')
        item_dict = db['Items']
        db.close()

        item_list = []
        start_item_list = []
        contain_item_list = []
        for key in item_dict:
            item = item_dict.get(key)
            if isinstance(item, Item.Prescribed):
                if item.get_item_name().lower().startswith(search.search.data.lower()):
                    start_item_list.append(item)
                elif search.search.data.lower() in item.get_item_name().lower():
                    contain_item_list.append(item)

                item_list = start_item_list + contain_item_list

        return render_template('Pharmacy/prescription.html', items_list=item_list, form=search)

    db = shelve.open('storage.db', 'r')
    item_dict = db['Items']
    db.close()

    item_list = []
    for key in item_dict:
        item = item_dict.get(key)
        if isinstance(item, Item.Prescribed):
            item_list.append(item)

    return render_template('Pharmacy/prescription.html', items_list=item_list, form=search)


@app.route('/prescribeItem/<int:id>/', methods=['GET', 'POST'])
def prescribe_item(id):
    prescribe_item_form = PrescriptionForm(request.form)

    if request.method == 'POST' and prescribe_item_form.validate():
        db = shelve.open('storage.db', 'w')
        item_dict = db['Items']
        pres_dict = db['Prescription']

        user_id = session["user-NRIC"]
        item = item_dict.get(id)

        item.set_item_want(prescribe_item_form.quantity.data)

        item.set_item_dosage(
            str(prescribe_item_form.dosage_times.data) + " Times " + prescribe_item_form.dosage_interval.data)

        try:
            pres = pres_dict[user_id]

            if item.get_item_want() > item.get_item_have():
                item.set_item_want(0)
                flash("Not enough stock at the moment, try again later", 'danger')
            elif pres.check(item):
                pres.remove(item)
                item.set_item_want(prescribe_item_form.quantity.data)
                item.set_item_dosage(
                    str(prescribe_item_form.dosage_times.data) + " times " + prescribe_item_form.dosage_interval.data)
                pres.add(item)
            else:
                pres.add(item)
                db['Items'] = item_dict

        except KeyError:
            temp_cart = [item]
            pres = Cart.Prescription(temp_cart)
            pres_dict[user_id] = pres

        finally:
            db['Prescription'] = pres_dict
            db.close()

        return redirect(url_for('prescription'))

    else:
        db = shelve.open('storage.db', 'r')
        item_dict = db['Items']
        db.close()

        item = item_dict.get(id)
        prescribe_item_form.quantity.data = item.get_item_want()

        return render_template('Pharmacy/prescriptionForm.html', form=prescribe_item_form, name=item.get_item_name(),
                               bio=item.get_item_bio(), price=item.get_item_price(), picture=item.get_item_picture(),
                               have=item.get_item_have())


@app.route('/prescription/prescribe', methods=['GET', 'POST'])
def prescription_cart():
    search = SearchBar(request.form)
    if request.method == 'POST':
        db = shelve.open('storage.db', 'r')
        pres_dict = db['Prescription']
        db.close()

        user_id = session["user-NRIC"]

        try:
            pres = pres_dict[user_id]

        except KeyError:
            pres = Cart.Prescription([])

        item_list = pres.get_cart()
        total = pres.total()
        count = pres.get_count()

        start_item_list = []
        contain_item_list = []
        for item in pres.get_cart():
            if item.get_item_name().lower().startswith(search.search.data.lower()):
                start_item_list.append(item)
            elif search.search.data.lower() in item.get_item_name().lower():
                contain_item_list.append(item)

            item_list = start_item_list + contain_item_list

        return render_template('Pharmacy/prescriptionCart.html', items_list=item_list, form=search, total=total,
                               count=count)
    db = shelve.open('storage.db', 'r')
    pres_dict = db['Prescription']
    db.close()

    user_id = session["user-NRIC"]

    try:
        pres = pres_dict[user_id]

    except KeyError:
        pres = Cart.Prescription([])

    item_list = pres.get_cart()
    total = pres.total()
    count = pres.get_count()

    return render_template('Pharmacy/prescriptionCart.html', items_list=item_list, form=search, total=total,
                           count=count)


@app.route('/prescribe', methods=['GET', 'POST'])
def prescribe():
    prescribe_form = PrescribeForm(request.form)

    if request.method == 'POST' and prescribe_form.validate():
        patient_id = prescribe_form.patient_nric.data
        db = shelve.open('storage.db', 'w')
        pres_dict = db['Prescription']

        user_id = session["user-NRIC"]

        pres = pres_dict[user_id]

        pres.set_owner(user_id)

        pres_dict[patient_id] = pres
        pres_dict.pop(user_id)

        db['Prescription'] = pres_dict
        db.close()
        return redirect(url_for('prescription'))
    else:
        return render_template('Pharmacy/prescribe.html', form=prescribe_form)


@app.route('/addToCart', methods=['POST'])
def addPrescription():
    db = shelve.open('storage.db', 'c')
    cart_dict = db['Cart']
    pres_dict = db['Prescription']

    user_ID = session["user-NRIC"]

    pres = pres_dict[user_ID]

    cart = []
    for item in pres.get_cart():
        try:
            cart = cart_dict[user_ID]

        except KeyError:
            cart = Cart.Cart([item])

        else:
            cart.add(item)

        finally:
            cart_dict[user_ID] = cart

    db['Cart'] = cart_dict
    db.close()

    return redirect(url_for('shopping_cart'))


# Admin access
@app.route('/all_users')
def admin_all_users():
    if session["user-role"] == "Admin":
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users')
        all_users = cursor.fetchall()

        return render_template("Admin/all_users.html", all_users=all_users)

    flash("Access denied", "danger")
    return redirect(url_for('home'))


@app.route('/admin_update/<uid>', methods=["GET", "POST"])
def admin_update(uid):
    if session["user-role"] == "Admin":
        db = shelve.open("storage.db")
        form = AdminUpdateForm(request.form)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE NRIC = %s', (uid,))

        user = cursor.fetchone()

        if request.method == "POST" and form.validate():
            cursor.execute('UPDATE users SET email = %s, password = %s, url = %s WHERE NRIC = %s',
                           (form.Email.data, form.Password.data, form.URL.data, uid,))
            appointment_dict = db['Appointments']
            for appts in appointment_dict:
                print(appointment_dict[appts])
                if appointment_dict[appts].get_doctor() == user["fname"] + " " + user["lname"]:
                    appointment_dict[appts].set_url(user["url"])
            flash("Successfully updated", "success")
            db.close()
            return redirect(url_for("admin_all_users"))

        return render_template("Admin/admin_update.html", user=user, form=form)

    else:
        flash("Access denied", "danger")
        return redirect(url_for("home"))


@app.route('/admin_delete/<uid>', methods=["GET"])
def admin_delete(uid):
    if session["user-role"] == "Admin":
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE * FROM users WHERE NRIC = %s', (uid,))
        flash("Successfully deleted user", "success")
        return redirect(url_for('admin_all_users'))
    else:
        flash("Access denied", "danger")
        return redirect(url_for('home'))


@app.route('/add_doctor', methods=["GET", "POST"])
def add_doctor():
    if session["user-role"] == "Admin":
        form = RegisterForm(request.form)
        if request.method == "POST" and form.validate():
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE nric = %s', (form.NRIC.data,))
            user_exist = cursor.fetchone()

            if user_exist:
                flash("This NRIC is already in used.You can login to access our service.", "danger")
                return redirect(url_for('admin_all_users'))
            else:
                cursor.execute('INSERT INTO users (NRIC, fname, lname, gender, dob, email, password, role, specialization, url) '
                               'VALUES (%s, %s, %s, %s, %s, %s, %s, "Doctor", %s, %s)',
                               (form.NRIC.data, form.FirstName.data, form.LastName.data, form.Gender.data,
                                form.Dob.data, form.Email.data, form.Password.data, form.specialization.data,
                                form.URL.data))
                mysql.connection.commit()
                flash(f'Account created for {form.FirstName.data} {form.LastName.data}!', 'success')
                return redirect(url_for('admin_all_users'))
        return render_template("Admin/add_doctor.html", form=form)
    else:
        flash("Access denied", "danger")
        return redirect(url_for('home'))


@app.route("/show_pyecharts1")
def showechart1():
    user_count = {'Patients': 0, "Doctors": 0}
    xdata = []
    ydata = []
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    user_count["Doctors"] = cursor.execute('SELECT count(*) FROM users WHERE role = "Doctor"')
    user_count["Patients"] = cursor.execute('SELECT count(*) FROM users WHERE role = "Patient"')

    for key in user_count:
        xdata.append(key)
        ydata.append(user_count[key])
    usernumber(xdata, ydata)

    return render_template("Admin/admin_dashboard.html")


# AppointmentSystem
@app.route('/appointment_list')
def appointment():
    db = shelve.open('storage.db', 'c')
    appointment_dict = db['Appointments']
    appointment_list = []
    year_month = []
    period = {}
    for key in appointment_dict:
        appointment = appointment_dict.get(key)
        if appointment.get_patient() == session["user-name"] or appointment.get_doctor() == session["user-name"] or \
                session["user-role"] == 'Admin':
            appointment_list.append(appointment)
    for appt in appointment_list:
        date = appt.get_date()
        time = appt.get_time()
        appt_date = validate_history(date, time)
        if appt_date:
            appointment_list.remove(appt)
    appointment_list.sort(key=lambda x: x.get_datetime())
    for i in range(len(appointment_list)):
        date = appointment_list[i].get_date()
        appt_date = date.strftime("%Y-%m-%d")
        month = appt_date.split("-")[1]
        year = appt_date.split("-")[0]
        ym = year + "-" + month
        if ym not in year_month:
            year_month.append(ym)
    for i in range(len(year_month)):
        current_month = []
        for appt in appointment_list:
            date = appt.get_date()
            appt_date = date.strftime("%Y-%m-%d")
            month = appt_date.split("-")[1]
            year = appt_date.split("-")[0]
            ym = year + "-" + month
            if ym == year_month[i]:
                current_month.append(appt)
        period[year_month[i]] = current_month
    return render_template('Appointment/appointment_list.html', period=period, number=len(appointment_list))


@app.route('/appointment_history')
def appointment_hist():
    db = shelve.open('storage.db', 'c')
    appointment_dict = db['Appointments']
    appointment_list = []
    appointment_hist = []
    for key in appointment_dict:
        appointment = appointment_dict.get(key)
        if appointment.get_patient() == session["user-name"] or appointment.get_doctor() == session["user-name"] or \
                session[
                    "user-role"] == 'Admin':
            appointment_list.append(appointment)
    for appt in appointment_list:
        date = appt.get_date()
        time = appt.get_time()
        appt_date = validate_history(date, time)
        if appt_date:
            appointment_hist.append(appt)
    appointment_len = len(appointment_hist)
    return render_template('Appointment/appointment_hist.html', appointment_list=appointment_hist,
                           appointment_len=appointment_len)


@app.route('/appointment_summary')
def appointment_summary():
    global current_month
    db = shelve.open('storage.db', 'c')
    appointment_dict = db['Appointments']
    appointment_list = []
    year_month = []
    period = {}
    for key in appointment_dict:
        appointment = appointment_dict.get(key)
        if appointment.get_patient() == session["user-name"] or appointment.get_doctor() == session["user-name"] or \
                session["user-role"] == 'Admin':
            appointment_list.append(appointment)
    appointment_list.sort(key=lambda x: x.get_datetime(), reverse=True)
    for i in range(len(appointment_list)):
        date = appointment_list[i].get_date()
        appt_date = date.strftime("%Y-%m-%d")
        month = appt_date.split("-")[1]
        year = appt_date.split("-")[0]
        ym = year + "-" + month
        if ym not in year_month:
            year_month.append(ym)
    for i in range(len(year_month)):
        current_month = []
        for appt in appointment_list:
            date = appt.get_date()
            appt_date = date.strftime("%Y-%m-%d")
            month = appt_date.split("-")[1]
            year = appt_date.split("-")[0]
            ym = year + "-" + month
            if ym == year_month[i]:
                current_month.append(appt)
        period[year_month[i]] = len(current_month)

    return render_template('Appointment/appointment_summary.html', period=period)


@app.route("/show_pyecharts")
def showechart():
    db = shelve.open('storage.db', 'c')
    appointment_dict = db['Appointments']
    appointment_list = []
    time_visitor = {'8AM': 0, "10AM": 0, "12PM": 0, "2PM": 0, "4PM": 0, "6PM": 0, "8PM": 0, "10PM": 0}
    xdata = []
    ydata = []
    for key in appointment_dict:
        appointment = appointment_dict.get(key)
        appointment_list.append(appointment)
    for appt in appointment_list:
        time = appt.get_time()
        if time == "8:00:00":
            time_visitor['8AM'] += 1
        elif time == "10:00:00":
            time_visitor['10AM'] += 1
        elif time == "12:00:00":
            time_visitor['12PM'] += 1
        elif time == "14:00:00":
            time_visitor['2PM'] += 1
        elif time == "16:00:00":
            time_visitor['4PM'] += 1
        elif time == "18:00:00":
            time_visitor['6PM'] += 1
        elif time == "20:00:00":
            time_visitor['8PM'] += 1
        elif time == "22:00:00":
            time_visitor['10PM'] += 1
    for key in time_visitor:
        xdata.append(key)
        ydata.append(time_visitor[key])
    print(xdata)
    print(ydata)
    bargraph(xdata, ydata)
    return render_template("Appointment/charts.html")


@app.route('/appointment', methods=['GET', 'POST'])
def add_appointment():
    form = AppointmentForm(request.form)
    if request.method == "POST" and form.validate():
        db = shelve.open('storage.db', 'c')
        appointment_dict = db['Appointments']

        appdate = validate_date(form.Date.data, form.Time.data)
        appt = appointments.Appointment(form.Date.data, form.Time.data, form.Department.data, form.Type.data)
        appt.set_patient(session["user-name"])
        repeated = validate_repeated(appointment_dict, appt, session["user-name"])

        if appdate:
            flash("Invalid Date or Time!", 'danger')
        elif repeated:
            flash("You can only have 1 appointment at 1 timing!", 'danger')
        else:
            assignDoctor(appt)
            appt.set_id(id(appt))
            appointment_dict[appt.get_id()] = appt
            db['Appointments'] = appointment_dict
            db.close()
            flash("Appointment has been booked! View it in appointment list!", 'success')

            return redirect(url_for('home'))
    return render_template('Appointment/appointment.html', form=form)


@app.route('/docappointment', methods=['GET', 'POST'])
def doc_add_appointment():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE role = "patient"')

    user_dict = cursor.fetchall()
    patient_list = []

    for user in user_dict:
        patient_info = (user["fname"] + " " + user["lname"], user["fname"] + " " + user["lname"])
        patient_list.append(patient_info)

    form = DocAppointmentForm(request.form, patient_list)
    db = shelve.open('storage.db', 'c')
    appointment_dict = db['Appointments']

    form.Department.data = session["user"]['specialization']
    if request.method == "POST" and form.validate():
        appdate = validate_date(form.Date.data, form.Time.data)
        appt = appointments.Appointment(form.Date.data, form.Time.data, form.Department.data, form.Type.data)
        appt.set_patient(form.Patient.data)
        appt.set_doctor(session["user-NRIC"])
        repeated = validate_repeated(appointment_dict, appt, form.Patient.data)
        if appdate:
            flash("Invalid Date or Time!", 'danger')
        elif repeated:
            flash("You can only have 1 appointment at 1 timing!", 'danger')
        else:
            appt.set_id(id(appt))
            appointment_dict[appt.get_id()] = appt
            db['Appointments'] = appointment_dict
            flash("Appointment has been booked!View it in appointment list!", 'success')

            return redirect(url_for('home'))

    return render_template('Appointment/docappointment.html', form=form, patient_list=patient_list)


@app.route('/Updateappointment/<id>', methods=['GET', 'POST'])
def update_appointment(id):
    form = AppointmentForm(request.form)
    if request.method == "POST" and form.validate():
        db = shelve.open('storage.db', 'c')
        appointment_dict = db['Appointments']
        appt = appointment_dict[int(id)]
        newappt = appointments.Appointment(form.Date.data, form.Time.data, form.Department.data, form.Type.data)
        appdate = validate_date(form.Date.data, form.Time.data)
        repeated = validate_repeated(appointment_dict, newappt, session["user-role"])
        if appdate:
            flash("Invalid Date!", 'danger')
        elif repeated:
            flash("You can only have 1 appointment at 1 timing!", 'danger')
        else:
            assignDoctor(appt)
            appt.set_date(form.Date.data)
            appt.set_time(form.Time.data)
            appt.set_department(form.Department.data)
            appt.set_venue(form.Type.data)
            appointment_dict[appt.get_id()] = appt

            db['Appointments'] = appointment_dict
            db.close()
            flash("Appointment has been changed!View it in appointment list!", 'success')

            return redirect(url_for('home'))
        return redirect(url_for('update_appointment', id=id))

    else:
        db = shelve.open('storage.db', 'r')
        appointment_dict = db['Appointments']
        db.close()
        appt = appointment_dict[int(id)]
        form.Date.data = appt.get_date()
        form.Time.data = appt.get_time()
        form.Type.data = appt.get_venue()
        form.Department.data = appt.get_department()

        return render_template('Appointment/updateAppointment.html', form=form)


@app.route('/deleteAppointment/<id>', methods=['POST'])
def delete_appointment(id):
    db = shelve.open('storage.db', 'w')
    appointment_dict = db['Appointments']
    appointment_dict.pop(int(id))
    db['Appointments'] = appointment_dict
    flash("Appointment has been deleted", 'danger')
    db.close()
    return redirect(url_for('appointment'))


def validate_date(date, time):
    date = date.strftime("%Y-%m-%d")
    appt_time = datetime.strptime(date + " " + time, '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    if now > appt_time:
        return True


def validate_history(date, time):
    date2 = date.strftime("%Y-%m-%d")
    now = datetime.now()
    dt = date2 + " " + time
    appt_time = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    if now > appt_time:
        return True


def validate_repeated(appointment_dict, appt, user):
    for key in appointment_dict:
        if appointment_dict[key].get_patient() == user and appt.get_date() == appointment_dict[
            key].get_date() and appt.get_time() == appointment_dict[key].get_time():
            return True


def assignDoctor(appointment):
    appointment_no = 0
    db = shelve.open('storage.db', 'c')
    appointment_dict = db['Appointments']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE role = Doctor, specialization = %s', (appointment.get_department()))

    doc_list = cursor.fetchall()

    for doctor in doc_list:
        for appts in appointment_dict:
            if appointment_dict[appts].get_doctor() == doctor["fname"] + " " + doctor["lname"]:
                appointment_no += 1
            if appointment_no <= 3:
                appointment.set_doctor(f'{doctor["fname()"]} {doctor["lname()"]}')
                appointment.set_url(doctor["url"])
                break



# Contact Us
@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
    form = ContactForm()
    if form.validate_on_submit():
        flash(
            f'You have successfully submitted the form. Please wait 2-3 working days for reply and also check your email.Thank you.',
            'success')
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        enquiries = request.form['enquiries']
        msg = Message(subject,
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=[email],
                      body="Hi " + name + ',\n\n Thanks a lot for getting in touch with us. \n \n This is an automatic email just to let you know that we have received your enquiries.\n\n'
                                          'This is the message that you sent.\n' + enquiries)
        mail.send(msg)
        return redirect(url_for('contactus'))
    return render_template('FAQ/contactus.html', title='Contact Us', form=form)


# FAQ
@app.route('/faq', methods=['GET', 'POST'])
def create_faq():
    create_faq_form = FAQ(request.form)
    if request.method == 'POST' and create_faq_form.validate():
        qn_dict = {}
        db = shelve.open('storage.db', 'c')
        try:
            qn_dict = db['FAQ']
        except:
            print("Error in retrieving Questions from storage.db.")

        question = qns.FAQ(create_faq_form.question.data, create_faq_form.answer.data, create_faq_form.date.data)
        qn_dict[question.get_qns_id()] = question
        db['FAQ'] = qn_dict

        db.close()

        return redirect(url_for('create_faq'))
    return render_template('FAQ/faq.html', form=create_faq_form)


@app.route('/retrieveQns', methods=['GET', 'POST'])
def retrieve_qns():
    search = SearchBar(request.form)
    if request.method == 'POST':
        db = shelve.open('storage.db', 'r')
        qns_dict = db['FAQ']
        db.close()

        qns_list = []
        for key in qns_dict:
            question = qns_dict.get(key)
            if search.search.data.lower() in question.get_question().lower():
                qns_list.append(question)

        return render_template('FAQ/retrieveQns.html', count=len(qns_list), qn_list=qns_list, form=search)

    db = shelve.open('storage.db', 'r')
    qn_dict = db['FAQ']
    db.close()

    qn_list = []
    for key in qn_dict:
        question = qn_dict.get(key)
        qn_list.append(question)

    return render_template('FAQ/retrieveQns.html', count=len(qn_list), qn_list=qn_list, form=search)


@app.route('/updateQns/<int:id>/', methods=['GET', 'POST'])
def update_qns(id):
    update_faq_form = FAQ(request.form)
    if request.method == 'POST' and update_faq_form.validate():
        db = shelve.open('storage.db', 'w')
        qn_dict = db['FAQ']

        question = qn_dict.get(id)
        question.set_question(update_faq_form.question.data)
        question.set_answer(update_faq_form.answer.data)
        question.set_date(update_faq_form.date.data)

        db['FAQ'] = qn_dict
        db.close()

        return redirect(url_for('retrieve_qns'))
    else:
        db = shelve.open('storage.db', 'r')
        qn_dict = db['FAQ']
        db.close()

        question = qn_dict.get(id)
        update_faq_form.question.data = question.get_question()
        update_faq_form.answer.data = question.get_answer()
        update_faq_form.date.data = question.get_date()

        return render_template('FAQ/updateQns.html', form=update_faq_form)


@app.route('/deleteQns/<int:id>', methods=['POST'])
def delete_qns(id):
    qn_dict = {}
    db = shelve.open('storage.db', 'w')
    qn_dict = db['FAQ']

    qn_dict.pop(id)

    db['FAQ'] = qn_dict
    db.close()

    return redirect(url_for('retrieve_qns'))


@app.route("/monthlyQn")
def monthly_qn():
    db = shelve.open('storage.db', 'c')
    faq_dict = db['FAQ']
    faq_list = []
    month_qn = {"January": 0, "February": 0, "March": 0, "April": 0, "May": 0, "June": 0, "July": 0, "August": 0,
                "September": 0, "October": 0, "November": 0, "December": 0}
    xdata = []
    ydata = []
    for key in faq_dict:
        faq = faq_dict.get(key)
        faq_list.append(faq)
    for qn in faq_list:
        month = qn.get_date()
        month = month.strftime("%Y-%m-%d")
        if month == "2021-01-01":
            month_qn['January'] += 1
        elif month == "2021-02-01":
            month_qn['February'] += 1
        elif month == "2021-03-01":
            month_qn['March'] += 1
        elif month == "2021-04-01":
            month_qn['April'] += 1
        elif month == "2021-05-01":
            month_qn['May'] += 1
        elif month == "2021-06-01":
            month_qn['June'] += 1
        elif month == "2021-07-01":
            month_qn['July'] += 1
        elif month == "2021-08-01":
            month_qn['August'] += 1
        elif month == "2021-09-01":
            month_qn['September'] += 1
        elif month == "2021-10-01":
            month_qn['October'] += 1
        elif month == "2021-11-01":
            month_qn['November'] += 1
        elif month == "2021-12-01":
            month_qn['December'] += 1

    for key in month_qn:
        xdata.append(key)
        ydata.append(month_qn[key])

    print(xdata)
    print(ydata)
    monthlyQnbargraph(xdata, ydata)
    return render_template("FAQ/monthlyQn.html")


# Application Form
@app.route('/createApplicant', methods=['GET', 'POST'])
def create_applicant():
    create_applicant_form = CreateApplicationForm(request.form)

    if request.method == 'POST' and create_applicant_form.validate():
        applicants_dict = {}
        db = shelve.open('storage.db', 'c')

        try:
            applicants_dict = db['Applicant']
        except:
            print("Error in retrieving Applicants from storage.db.")

        # parsing parameters into Application Class in Application.py
        applicant = Applicant.Applicant(create_applicant_form.fname.data, create_applicant_form.lname.data,
                                        create_applicant_form.nric.data,
                                        create_applicant_form.email.data, create_applicant_form.age.data,
                                        create_applicant_form.address.data, create_applicant_form.gender.data,
                                        create_applicant_form.nationality.data, create_applicant_form.language.data,
                                        create_applicant_form.phoneno.data, create_applicant_form.quali.data,
                                        create_applicant_form.industry.data,
                                        create_applicant_form.comp1.data,
                                        create_applicant_form.posi1.data, create_applicant_form.comp2.data,
                                        create_applicant_form.posi2.data)

        applicants_dict[applicant.get_applicantid()] = applicant

        db['Applicant'] = applicants_dict

        # Automatically Send Email Codes
        sender_email = "nyppolyclinic@gmail.com"
        password = "helloworld123"
        rec_email = create_applicant_form.email.data
        subject = "Application for NYP Polyclinic"
        body = "Hello, we have received your application. Please wait for a few days for us to update you about the status. Thank you."
        message = "Subject: {}\n\n{}".format(subject, body)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        print("Login Success")
        server.sendmail(sender_email, rec_email, message)
        print("Email has been sent to ", rec_email)
        # Automatically Send Email Codes

        db.close()

        session['applicant_created'] = applicant.get_first_name() + ' ' + applicant.get_last_name()
        return redirect(url_for('create_applicant'))
    return render_template('ApplicationForm/applicationForm.html', form=create_applicant_form)


@app.route('/retrieveApplicants')
def retrieve_applicants():
    db = shelve.open('storage.db', 'r')
    applicants_dict = db['Applicant']
    db.close()

    applicants_list = []

    for key in applicants_dict:
        applicants = applicants_dict.get(key)
        applicants_list.append(applicants)

    return render_template('ApplicationForm/retrieveApplicants.html', count=len(applicants_list),
                           applicants_list=applicants_list)


@app.route('/updateApplicants/<int:id>/', methods=['GET', 'POST'])
def update_applicants(id):
    update_applicant_form = CreateApplicationForm(request.form)
    if request.method == 'POST' and update_applicant_form.validate():

        db = shelve.open('storage.db', 'w')
        applicants_dict = db['Applicant']

        # after submit, setting the updated inputs.
        # problem now is that updated employment does not display
        applicant = applicants_dict.get(id)
        applicant.set_first_name(update_applicant_form.fname.data)
        applicant.set_last_name(update_applicant_form.lname.data)
        applicant.set_NRIC(update_applicant_form.nric.data)
        applicant.set_email(update_applicant_form.email.data)
        applicant.set_age(update_applicant_form.age.data)
        applicant.set_address(update_applicant_form.address.data)
        applicant.set_gender(update_applicant_form.gender.data)
        applicant.set_nationality(update_applicant_form.nationality.data)
        applicant.set_language(update_applicant_form.language.data)
        applicant.set_phonenumber(update_applicant_form.phoneno.data)
        applicant.set_qualification(update_applicant_form.quali.data)
        applicant.set_industry(update_applicant_form.industry.data)
        applicant.set_company1(update_applicant_form.comp1.data)
        applicant.set_postion1(update_applicant_form.posi1.data)
        applicant.set_company2(update_applicant_form.comp2.data)
        applicant.set_postion2(update_applicant_form.posi2.data)
        db['Applicant'] = applicants_dict

        # Automatically Send Email Codes
        sender_email = "nyppolyclinic@gmail.com"
        password = "helloworld123"
        rec_email = applicant.get_email()
        subject = "Application for NYP Polyclinic"
        body = "Hello, we have your updated application. Please wait for a few days for us to update you about the status. Thank you."
        message = "Subject: {}\n\n{}".format(subject, body)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        print("Login Success")
        server.sendmail(sender_email, rec_email, message)
        print("Email has been sent to ", rec_email)
        # Automatically Send Email Codes

        db.close()

        session['applicant_updated'] = applicant.get_first_name() + ' ' + applicant.get_last_name()

        return redirect(url_for('home'))

    else:

        db = shelve.open('storage.db', 'r')
        applicants_dict = db['Applicant']
        db.close()

        # get data input and place in in the field
        applicant = applicants_dict.get(id)
        update_applicant_form.fname.data = applicant.get_first_name()
        update_applicant_form.lname.data = applicant.get_last_name()
        update_applicant_form.nric.data = applicant.get_NRIC()
        update_applicant_form.email.data = applicant.get_email()
        update_applicant_form.age.data = applicant.get_age()
        update_applicant_form.address.data = applicant.get_address()
        update_applicant_form.gender.data = applicant.get_gender()
        update_applicant_form.nationality.data = applicant.get_nationality()
        update_applicant_form.language.data = applicant.get_language()
        update_applicant_form.phoneno.data = applicant.get_phonenumber()
        update_applicant_form.quali.data = applicant.get_qualification()
        update_applicant_form.industry.data = applicant.get_industry()
        update_applicant_form.comp1.data = applicant.get_company1()
        update_applicant_form.posi1.data = applicant.get_position1()
        update_applicant_form.comp2.data = applicant.get_company2()
        update_applicant_form.posi2.data = applicant.get_position2()

        return render_template('ApplicationForm/updateApplicant.html', form=update_applicant_form)


@app.route('/sendApplicants/<int:id>/', methods=['GET', 'POST'])
def send_applicant(id):
    resend_form = ResendForm(request.form)
    contents = "Hello, Please Resend Your Application Form as there is a certain problem with your inputs. The following inputs with problem are, "
    if request.method == 'POST' and resend_form.validate():
        db = shelve.open('storage.db', 'r')
        applicants_dict = db['Applicant']
        applicant = applicants_dict.get(id)

        resend = Resend.Resend(resend_form.nric.data, resend_form.email.data, resend_form.age.data,
                               resend_form.gender.data, resend_form.nationality.data, resend_form.language.data,
                               resend_form.phoneno.data, resend_form.quali.data, resend_form.industry.data)

        if resend.get_nric() == "Yes":
            contents = contents + "NRIC/FIN"
        else:
            contents = contents

        if resend.get_email() == "Yes":
            contents = contents + " Email"
        else:
            contents = contents

        if resend.get_age() == "Yes":
            contents = contents + " Age"
        else:
            contents = contents

        if resend.get_gender() == "Yes":
            contents = contents + " Gender"
        else:
            contents = contents

        if resend.get_nationality() == "Yes":
            contents = contents + " Nationality"
        else:
            contents = contents

        if resend.get_language() == "Yes":
            contents = contents + " Language"
        else:
            contents = contents

        if resend.get_phoneno() == "Yes":
            contents = contents + " Phone Number"
        else:
            contents = contents

        if resend.get_quali() == "Yes":
            contents = contents + " Qualification"
        else:
            contents = contents

        if resend.get_industry() == "Yes":
            contents = contents + " Industry"
        else:
            contents = contents

        sender_email = "nyppolyclinic@gmail.com"
        password = "helloworld123"
        rec_email = applicant.get_email()
        subject = "Application for NYP Polyclinic"
        body = contents + ". Here's the link to update {}{}".format(request.url_root,
                                                                    url_for('update_applicants', id=id))
        message = "Subject: {}\n\n{}".format(subject, body)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        print("Login Success")
        server.sendmail(sender_email, rec_email, message)
        print("Email has been sent to ", rec_email)
        print(applicant)
        return redirect(url_for('retrieve_applicants'))

    return render_template('ApplicationForm/resendForm.html', form=resend_form)


@app.route('/deleteApplicant/<int:id>', methods=['POST'])
def delete_applicant(id):
    db = shelve.open('storage.db', 'w')
    applicants_dict = db['Applicant']

    applicant = applicants_dict.pop(id)

    db['Applicant'] = applicants_dict
    db.close()
    session['applicant_deleted'] = applicant.get_first_name() + ' ' + applicant.get_last_name()
    return redirect(url_for('retrieve_applicants'))


@app.route('/showDashboard')
def show_dashboard():
    db = shelve.open('storage.db', 'c')
    applicants_dict = db['Applicant']
    applicants_list = []
    qualification_level = {"O'Levels": 0, "A'Levels": 0, "N'Levels": 0, "Diploma": 0, "Bachelor": 0, "Master": 0}
    xdata = []
    ydata = []

    for key in applicants_dict:
        applicant = applicants_dict.get(key)
        applicants_list.append(applicant)

    for people in applicants_list:
        qualification = people.get_qualification()

        if qualification == "O'Levels":
            qualification_level["O'Levels"] += 1
        elif qualification == "A'Levels":
            qualification_level["A'Levels"] += 1
        elif qualification == "N'Levels":
            qualification_level["N'Levels"] += 1
        elif qualification == "Diploma":
            qualification_level["Diploma"] += 1
        elif qualification == "Bachelor":
            qualification_level["Bachelor"] += 1
        elif qualification == "Master":
            qualification_level["Master"] += 1

    for key in qualification_level:
        xdata.append(key)
        ydata.append(qualification_level[key])

    print(xdata)
    print(ydata)

    applicationbargraph(xdata, ydata)

    return render_template("ApplicationForm/dashboard.html")


@app.route('/showDashboard2')
def show_dashboard2():
    db = shelve.open('storage.db', 'c')
    applicants_dict = db['Applicant']
    applicants_list = []
    regions = {"City": 0, "Central": 0, "South": 0, "East": 0, "North": 0, "West": 0}
    xdata1 = []
    ydata1 = []
    city = ['Boat Quay', 'Chinatown', 'Havelock Road', 'Marina Square', 'Raffles Place', 'Suntec City', 'Anson Road',
            'Chinatown', 'Neil Road', 'Raffles Place', 'Shenton Way', 'Tanjong Pagar']
    central = ['Cairnhill', 'Killiney', 'Leonie Hill', 'Orchard', 'Oxley', 'Balmoral', 'Bukit Timah', 'Grange Road',
               'Holland', 'Orchard Boulevard', 'River Valley', 'Tanglin Road', 'Chancery', 'Bukit Timah',
               'Dunearn Road', 'Newton', 'Balestier', 'Moulmein', 'Novena', 'Toa Payoh']
    south = ['Alexandra Road', 'Tiong Bahru', 'Queenstown', 'Keppel', 'Mount Faber', 'Sentosa', 'Telok Blangah',
             'Buona Vista', 'Dover', 'Pasir Panjang', 'West Coast']
    east = ['Potong Pasir', 'Macpherson', 'Eunos', 'Geylang', 'Kembangan', 'Paya Lebar', 'Katong', 'Marine Parade',
            'Siglap', 'Tanjong Rhu', 'Bayshore', 'Bedok', 'Chai Chee', 'Changi', 'Loyang', 'Pasir Ris', 'Simei',
            'Tampines']
    north = ['Hougang', 'Punggol', 'Sengkang', 'Ang Mo Kio', 'Bishan', 'Braddell Road', 'Thomson', 'Admiralty',
             'Woodlands', 'Tagore', 'Yio Chu Kang', 'Sembawang', 'Yishun', 'Seletar']
    west = ['Clementi', 'Upper Bukit Timah', 'Hume Avenue', 'Boon Lay', 'Jurong', 'Tuas', 'Bukit Batok',
            'Choa Chu Kang', 'Hillview Avenue', 'Upper Bukit Timah', 'Kranji', 'Lim Chu Kang', 'Sungei Gedong',
            'Tengah']

    for key in applicants_dict:
        applicant = applicants_dict.get(key)
        applicants_list.append(applicant)

    for people in applicants_list:
        district = people.get_address()

        for i in city:
            if i.lower() in district.lower():
                regions['City'] += 1
                break
            else:
                continue

        for i in central:
            if i.lower() in district.lower():
                regions['Central'] += 1
                break
            else:
                continue

        for i in south:
            if i.lower() in district.lower():
                regions['South'] += 1
                break
            else:
                continue

        for i in east:
            if i.lower() in district.lower():
                regions['East'] += 1
                break
            else:

                continue

        for i in north:
            if i.lower() in district.lower():
                regions['North'] += 1
                break
            else:
                continue

        for i in west:
            if i.lower() in district.lower():
                regions['West'] += 1
                break
            else:
                continue

    for key in regions:
        xdata1.append(key)
        ydata1.append(regions[key])

    print(xdata1)
    print(ydata1)

    addressbargraph(xdata1, ydata1)

    return render_template("ApplicationForm/dashboard2.html")


@app.route('/showDashboard3')
def show_dashboard3():
    db = shelve.open('storage.db', 'c')
    applicants_dict = db['Applicant']
    applicants_list = []
    age_ranges = {"17-25": 0, "26-40": 0, "41-50": 0, "51-60": 0, "61-70": 0}
    xdata2 = []
    ydata2 = []

    for key in applicants_dict:
        applicant = applicants_dict.get(key)
        applicants_list.append(applicant)

    for people in applicants_list:
        ages = people.get_age()

        if ages <= 25:
            age_ranges["17-25"] += 1
        elif 40 >= ages >= 26:
            age_ranges['26-40'] += 1
        elif 50 >= ages >= 41:
            age_ranges["41-50"] += 1
        elif 60 >= ages >= 51:
            age_ranges["51-60"] += 1
        elif 70 >= ages >= 61:
            age_ranges["61-70"] += 1

    for key in age_ranges:
        xdata2.append(key)
        ydata2.append(age_ranges[key])

    print(xdata2)
    print(ydata2)

    agerangebargraph(xdata2, ydata2)

    return render_template("ApplicationForm/dashboard3.html")


@app.errorhandler(404)
def page_not_handle(e):
    return render_template("error404.html"), 404


if __name__ == '__main__':
    app.run(debug=True)
