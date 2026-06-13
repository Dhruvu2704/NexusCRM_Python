from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "crm_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# =========================
# MODELS
# =========================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )


class Customer(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100)
    )

    phone = db.Column(
        db.String(20)
    )

    company = db.Column(
        db.String(100)
    )

    address = db.Column(
        db.String(200)
    )

    status = db.Column(
        db.String(50),
        default="Prospect"
    )


# =========================
# HOME
# =========================

@app.route('/')
def home():
    return redirect('/login')


# =========================
# REGISTER
# =========================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            return "Username already exists"

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')


# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            session['user'] = username

            return redirect('/dashboard')

        return "Invalid Credentials"

    return render_template('login.html')


# =========================
# DASHBOARD
# =========================

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/login')

    total_customers = Customer.query.count()

    active_customers = Customer.query.filter_by(
        status='Active'
    ).count()

    prospect_customers = Customer.query.filter_by(
        status='Prospect'
    ).count()

    inactive_customers = Customer.query.filter_by(
        status='Inactive'
    ).count()

    return render_template(
        'dashboard.html',
        total_customers=total_customers,
        active_customers=active_customers,
        prospect_customers=prospect_customers,
        inactive_customers=inactive_customers
    )

# =========================
# ADD CUSTOMER
# =========================

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():

    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':

        customer = Customer(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            company=request.form['company'],
            address=request.form['address'],
            status=request.form['status']
        )
        db.session.add(customer)
        db.session.commit()

        return redirect('/customers')

    return render_template('add_customer.html')


# =========================
# VIEW CUSTOMERS
# =========================

@app.route('/customers')
def view_customers():

    if 'user' not in session:
        return redirect('/login')

    customers = Customer.query.all()

    return render_template(
        'view_customers.html',
        customers=customers
    )

@app.route('/edit_customer/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):

    if 'user' not in session:
        return redirect('/login')

    customer = Customer.query.get_or_404(id)

    if request.method == 'POST':

        customer.name = request.form['name']
        customer.email = request.form['email']
        customer.phone = request.form['phone']
        customer.company = request.form['company']
        customer.address = request.form['address']
        customer.status = request.form['status']

        db.session.commit()

        return redirect('/customers')

    return render_template(
        'edit_customer.html',
        customer=customer
    )

@app.route('/delete_customer/<int:id>')
def delete_customer(id):

    if 'user' not in session:
        return redirect('/login')

    customer = Customer.query.get_or_404(id)

    db.session.delete(customer)

    db.session.commit()

    return redirect('/customers')

# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')


# =========================
# RUN APP
# =========================

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)