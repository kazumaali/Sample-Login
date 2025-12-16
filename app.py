import os
import re
import random
import secrets
from datetime import datetime, timedelta
from flask import Flask, render_template, url_for, redirect, flash, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_required, logout_user, current_user, LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, IntegerField
from wtforms.validators import InputRequired, Length, ValidationError, Regexp, EqualTo
from flask_mail import Mail, Message
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

app = Flask(__name__)

'''Database Creation'''
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database.db')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

if os.getenv('FLASK_ENV') == 'production':
    app.config['SESSION_COOKIE_SECURE'] = True
else:
    app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

limiter = Limiter(
  app=app,
  key_func=get_remote_address,
  default_limits=['200 per day', '50 per hour']
  )

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'false').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER')

@app.after_request
def set_security_headers(response):
  response.headers['X-Content-Type-Options'] = 'nosniff'
  response.headers['X-Frame-Options'] = 'SAMEORIGIN'
  response.headers['X-XSS-Protection'] = '1; mode=block'
  return response

db = SQLAlchemy(app)
mail = Mail(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))
  
def password_complexity(form, field):
  '''Enforce strong Passwords'''
  password = field.data
  if len(password) < 8:
    raise ValidationError('password must contain of at least 8 characters!')
    print('password must contain of at least 8 characters!')
  if not re.search(r'[A-Z]', password):
    raise ValidationError('password must contain of at least one uppercase letter')
    print('password must contain of at least one uppercase letter')
  if not re.search(r'[a-z]', password):
    raise ValidationError('password must contain of at least one lowercase letter')
    print('password must contain of at least one lowercase letter')
  if not re.search(r'\d', password):
    raise ValidationError('password must contain of at least one number')
    print('password must contain of at least one number')
  
class SignupForm(FlaskForm):
  username = StringField(validators=[InputRequired(), Length(min=6, max=80), Regexp('^[a-zA-Z0-9_]+$', message='Username must only contain of letters, numbers, and underscores_')], render_kw={'placeholder': 'please enter a username', 'class': 'form_inputs'})
  email = EmailField(validators=[InputRequired(), Length(min=6, max=120)], render_kw={'placeholder':'please enter an email address', 'class':'form_inputs'})
  password = PasswordField(validators=[InputRequired(), password_complexity], render_kw={'placeholder':'please enter a password', 'class':'form_inputs'})
  repeat_password = PasswordField(validators=[InputRequired(), EqualTo('password', message='Passwords must match')], render_kw={'placeholder':'please confirm your password', 'class':'form_inputs'})
  submit = SubmitField('Sign Up')
  
class LoginForm(FlaskForm):
  email = EmailField(validators=[InputRequired(), Length(min=6, max=120)], render_kw={'placeholder':'please enter your email address', 'class':'form_inputs'})
  password = PasswordField(validators=[InputRequired()], render_kw={'placeholder':'please enter your password', 'class':'form_inputs'})
  submit = SubmitField('Log In')
  
class VerificationForm(FlaskForm):
  verification = StringField(validators=[InputRequired(), Length(min=6, max=6, message='Code must be exactly 6 characters')], render_kw={'placeholder': 'please enter the verification code', 'class': 'form_inputs'})
  submit = SubmitField('Verify')
  
class ChangePasswordForm(FlaskForm):
  verification = StringField(validators=[InputRequired(), Length(min=6, max=6)], render_kw={'placeholder': 'please enter the verification code', 'class': 'form_inputs'})
  changed_password = PasswordField(validators=[InputRequired(), password_complexity], render_kw={'placeholder':'please change your password', 'class':'form_inputs'})
  submit = SubmitField('Reset Password')
  
class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False, index=True)
  password = db.Column(db.String(200), nullable=False)
  is_verified = db.Column(db.Boolean, default=False, nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  
@app.route('/', methods=['GET', 'POST'])
def home():
  return render_template('index.html')
  
@app.route('/signup', methods=['GET', 'POST'])
@limiter.limit('3 per minute')
def signup():
  form = SignupForm()
  is_valid = True
  
  if form.validate_on_submit():
    user_email = form.email.data.lower().strip()
    username = form.username.data.lower().strip()
    
    if User.query.filter_by(email=user_email).first():
      flash('This user already exists!', 'warning')
      print('This user already exists!')
      is_valid = False
      
    if User.query.filter_by(username=username).first():
      flash('This username is already taken!', 'warning')
      print('This username is already taken!')
      is_valid = False
      
    if form.password.data != form.repeat_password.data:
      flash("Passwords don't match!", 'warning')
      print("Passwords don't match!")
      is_valid = False
    
    if is_valid:  
      verification_code = secrets.randbelow(900_000) + 100_000
      session['verification_code'] = verification_code
      session['code_expires'] = (datetime.utcnow() + timedelta(minutes=10)).timestamp()
      session['pending_user'] = {
        'email': user_email,
        'username': username,
        'password': generate_password_hash(form.password.data)
        
      }
      msg = Message(
        'Hi. This is your verification code',
        recipients=[user_email],
        body=f'copy the code {verification_code}'
        )
      mail.send(msg)
      flash('redirected to verification page', 'info')
      print('redirected to verification page')
      return redirect(url_for('verification')) 
  
  return render_template('signup.html', form=form)
  
@app.route('/verification', methods=['GET', 'POST'])
def verification():
  form = VerificationForm()
  is_valid = True
  
  if form.validate_on_submit():
    stored_code = session.get('verification_code')
    expires = session.get('code_expires')
    current_time = datetime.utcnow().timestamp()
    
    if not stored_code or not expires or current_time > expires:
      is_valid = False
      session.pop('verification_code', None)
      session.pop('code_expires', None)
      flash('Code expired. Please try again.', 'warning')
      print('Code expired. Please try again.')
      return redirect(url_for('signup'))
      
    try:
      user_input_code = int(form.verification.data)
    except ValueError:
      is_valid = False
      flash('Invalid code format. Please enter a 6-digit number.', 'danger')
      print('Invalid code format entered!')
      return redirect(url_for('verification'))

    if user_input_code != stored_code:
      is_valid = False
      flash('Wrong Code!', 'danger')
      print('Wrong Code Entered!')
      return redirect(url_for('verification'))
      
    if is_valid:
      user_data = session.pop('pending_user', None)
      
      if not user_data:
        flash('Verification session missing. Please re-register.', 'warning')
        return redirect(url_for('signup'))
        
      new_user = User(
        username=user_data['username'],
        email=user_data['email'],
        password=user_data['password'],
        is_verified=True
        )
        
      db.session.add(new_user)
      db.session.commit()
        
      session.pop('verification_code', None)
      session.pop('code_expires', None)
        
      flash('Account created successfully.', 'success')
      print('Account created successfully.')
        
      return redirect(url_for('login'))
  
  
  return render_template('verification.html', form=form)
  
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def login():
  form = LoginForm()
  is_valid = True
  
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data.lower().strip()).first()
    
    if not user:
      is_valid = False
      flash('Invalid email address', 'warning')
      print('Invalid email address')
      return render_template('login.html', form=form)
        
    if not check_password_hash(user.password, form.password.data):
      is_valid = False
      flash('Invalid password', 'warning')
      print('Invalid password')
      return render_template('login.html', form=form)
        
    if not user.is_verified:
      is_valid = False
      flash('Please verify your email first.', 'warning')
      print('Please verify your email first.')
      return render_template('login.html', form=form)
      
    if is_valid:
      login_user(user, remember=False)
      flash(f'Welcome back {user.username}', 'success')
      print(f'Welcome back {user.username}')
      return redirect(url_for('dashboard'))
  
  return render_template('login.html', form=form)
  
@app.route('/forgot_password', methods=['GET', 'POST'])
@limiter.limit('3 per hour')
def forgot_password():
  
  if request.method == 'POST':
    email = request.form.get('email', '').lower().strip()
    user = User.query.filter_by(email=email).first()
        
    if not user:
      flash('If email exists, a code is sent to it.', 'info')
      print("email doesn't exist")
      return redirect(url_for('forgot_password'))
    
    reset_code = secrets.randbelow(900_000) + 100_000
    session['password_reset_code'] = reset_code
    session['password_reset_email'] = email
    session['reset_expires'] = (datetime.utcnow() + timedelta(minutes=10)).timestamp()
      
    msg = Message(
      'Password Reset Code',
      recipients=[email],
      body=f'Your password reset code is: {reset_code}'
      )
    mail.send(msg)
    flash('Password reset code sent to your email!', 'info')
    print('Password reset code sent to your email!')
    return redirect(url_for('change_password'))
    
  return render_template('forgot_password.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
  form = ChangePasswordForm()
    
  if form.validate_on_submit():
    
    stored_code = session.get('password_reset_code')
    user_email = session.get('password_reset_email')
    expires = session.get('reset_expires')
    current_time = datetime.utcnow().timestamp()
        
    if not all([stored_code, user_email, expires]):
      flash('Session expired. Request a new reset code.', 'warning')
      print('Session expired. Request a new reset code.')
      return redirect(url_for('forgot_password'))
      
    if current_time > expires:
      session.pop('password_reset_code', None)
      session.pop('password_reset_email', None)
      session.pop('reset_expires', None)
      flash('Reset code expired. Please request a new one.', 'warning')
      print('Reset code expired.')
      return redirect(url_for('forgot_password'))
        
    try:
      user_input_code = int(form.verification.data)
    except ValueError:
      flash('Invalid code format. Please enter a 6-digit number.', 'danger')
      print('Invalid code format entered!')
      return redirect(url_for('change_password'))

    if user_input_code != stored_code:
      flash('Invalid verification code', 'danger')
      print('Invalid verification code')
      return redirect(url_for('change_password'))

      
    user = User.query.filter_by(email=user_email).first()
    if not user:
      flash('User not found!', 'danger')
      print('User not found!')
      return redirect(url_for('login'))
    
    user.password = generate_password_hash(form.changed_password.data)
    db.session.commit()
    
    session.pop('password_reset_code', None)
    session.pop('password_reset_email', None)
    session.pop('reset_expires', None)
    
    flash('Password updated successfully.', 'success')
    print('Password updated successfully.')
    return redirect(url_for('login'))
    
  return render_template('change_password.html', form=form)
  
@app.route('/resend_code', methods=['POST'])
@limiter.limit('3 per minute')
def resend_code():
  
  if 'pending_user' in session:
    email = session['pending_user']['email']
    new_code = secrets.randbelow(900_000) + 100_000
    session['verification_code'] = new_code
    session['code_expires'] = (datetime.utcnow() + timedelta(minutes=10)).timestamp()
        
    msg = Message(
      'New Signup Verification Code',
      recipients=[email],
      body=f'Your new verification code is: {new_code}'
      )
    mail.send(msg)
    flash('New signup code sent!', 'info')
    return redirect(url_for('verification'))
    
  elif 'password_reset_email' in session:
    email = session['password_reset_email']
    new_code = secrets.randbelow(900_000) + 100_000
    session['password_reset_code'] = new_code
    session['reset_expires'] = (datetime.utcnow() + timedelta(minutes=10)).timestamp()
        
    msg = Message(
      'New Password Reset Code',
      recipients=[email],
      body=f'Your new reset code is: {new_code}'
      )
    mail.send(msg)
    flash('New reset code sent!', 'info')
    return redirect(url_for('change_password'))
  
    flash('No pending verification found', 'warning')
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
  return render_template('dashboard.html')
  
@app.route('/logout', methods=['GET', 'POST'])
def logout():
  logout_user()
  flash('logged out successfully.', 'success')
  print('logged out successfully.')
  return redirect(url_for('home'))
  
with app.app_context():
    db.create_all()

if __name__ == '__main__':
  if os.path.exists(db_path):
    os.chmod(db_path, 0o600)
  port = int(os.environ.get("PORT", 8080))
  app.run(debug=True, port=port, host='0.0.0.0')