from flask import Flask, render_template, redirect, url_for, request, session
from functools import wraps

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFError, CSRFProtect

from datetime import timedelta

from captcha import captcha

app = Flask(__name__)
csrf = CSRFProtect(app)  # CSRF korumasını etkinleştir
app.secret_key = 'gizli_anahtar'  # Gizli anahtar oturum yönetimi için gerekli.
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)  # Oturum süresi 15 dakika

# Kullanıcı veritabanı simülasyonu
#emre   s%J!u4Q7
#ahmet  U!W#cP5b
#zeynep @a3N+Oz2
users = {
    "emre": {"password": "pbkdf2:sha256:260000$D7hVzeJT0P5jG6Qw$6c8d68dc4c1b95beed8d6ba57090a875322cf2219fc9f0f46477b8b40d94047b", "role": "Admin"},
    "ahmet": {"password": "pbkdf2:sha256:260000$1e5701Vpt31niGd4$57593c139a37179c17f58032e728bf4b09c99a7dab22524a4cf941065bbb9bc9", "role": "User"},
    "zeynep": {"password": "pbkdf2:sha256:260000$rhoHzooCIHab0MH2$a3afae668facf4ef17968f01d8fda56331f041a3707e08cc7b3a6dd9b3c7ad44", "role": "Guest"}
}




# Başarısız giriş denemeleri için veri yapısı
failed_attempts = {}


class LoginForm(FlaskForm):
    
    username = StringField('Kullanıcı Adı', validators=[DataRequired()])
    password = PasswordField('Parola', validators=[DataRequired()])
    kod = StringField('Kod', validators=[DataRequired()])
    submit = SubmitField('Giriş')

# Brute-force saldırılarına karşı koruma limitleri
MAX_ATTEMPTS = 6
LOCK_TIME = timedelta(minutes=15)

@app.route('/captcha')#captcha resminin yolu
def generate_captcha():
    return captcha()


# Kullanıcı rolüne göre erişim kontrolü
def login_required(role=""):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if "username" not in session:
                return redirect(url_for('login'))
            if role and session.get("role") != role:
                return "Bu sayfaya erişim yetkiniz yok!", 403
            return func(*args, **kwargs)
        return wrapped
    return wrapper

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global failed_attempts
    form = LoginForm()      # Flask-WTF formunu oluştur
    if form.validate_on_submit():   # CSRF ve diğer validasyonları otomatik kontrol eder
    #if request.method == 'POST':
        #username = request.form['username']
        #password = request.form['password']
        username = form.username.data
        password = form.password.data
        kod = form.kod.data
        
        now = datetime.now()

        # Giriş denemesi kontrolü
        if username in failed_attempts:
            attempts, lock_time = failed_attempts[username]
            if attempts >= MAX_ATTEMPTS and now < lock_time:
                return f"Çok fazla başarısız giriş denemesi yaptınız. Lütfen {lock_time - now} dakika bekleyin."
            
            
           
        
        user = users.get(username)

        if user and check_password_hash(user["password"], password) and kod==session.get('captcha'):  # Hash doğrulama
            # Başarılı giriş: Deneme kaydını sıfırla
            failed_attempts.pop(username, None)
            session['username'] = username
            session['role'] = user["role"]
            return redirect(url_for('dashboard'))

        # Başarısız giriş: Deneme sayısını artır
        if username not in failed_attempts:
            failed_attempts[username] = (1, now + LOCK_TIME)
        else:
            attempts, _ = failed_attempts[username]
            failed_attempts[username] = (attempts + 1, now + LOCK_TIME)
        
        return "İstenilen bilgiler hatalı!"

    # Formu şablona gönder
    return render_template('login.html', form=form)
    #return render_template('login.html')
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return "CSRF doğrulama hatası!", 400

@app.route('/dashboard')
@login_required()
def dashboard():
    return f"Hoş geldiniz, {session['username']}! Rolünüz: {session['role']}"

@app.route('/admin')
@login_required(role="Admin")
def admin():
    return "Yönetici sayfasına hoş geldiniz! Burada yalnızca yöneticiler işlem yapabilir."

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
