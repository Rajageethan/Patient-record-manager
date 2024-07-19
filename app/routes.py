from flask import render_template, url_for, flash, redirect, request, Blueprint
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, RecordForm
from app.models import User, Record
from flask_login import login_user, current_user, logout_user, login_required

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    return render_template('index.html')

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route("/dashboard")
@login_required
def dashboard():
    records = Record.query.filter_by(author=current_user).all()
    return render_template('dashboard.html', title='Dashboard', records=records)

@main.route("/record/new", methods=['GET', 'POST'])
@login_required
def new_record():
    form = RecordForm()
    if form.validate_on_submit():
        record = Record(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(record)
        db.session.commit()
        flash('Your record has been created!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('add_record.html', title='New Record', form=form)

@main.route("/record/<int:record_id>")
@login_required
def view_record(record_id):
    record = Record.query.get_or_404(record_id)
    return render_template('view_record.html', title='View Record', record=record)

@main.route("/add_record", methods=['GET', 'POST'])
@login_required
def add_record():
    form = RecordForm()
    if form.validate_on_submit():
        record = Record(
            title=form.title.data,
            date=form.date.data,
            description=form.description.data,
            symptoms=form.symptoms.data,
            medications=form.medications.data,
            diagnosis=form.diagnosis.data,
            user_id=current_user.id
        )
        db.session.add(record)
        db.session.commit()
        flash('Your health record has been added!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('add_record.html', title='Add Record', form=form)
