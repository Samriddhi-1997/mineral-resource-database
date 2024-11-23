from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mineral_resources.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from models.models import Mineral

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    minerals = Mineral.query.all()
    return render_template('dashboard.html', minerals=minerals)

from flask_login import LoginManager, login_user, logout_user, current_user

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
 @app.route('/login', methods=['GET', 'POST'])
def login():
    # Implement login functionality

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Implement registration functionality

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    minerals = Mineral.query.all()
    users = User.query.all()
    return render_template('admin.html', minerals=minerals, users=users)

@app.route('/add_mineral', methods=['POST'])
def add_mineral():
    if current_user.role == 'admin':
        # Implement add mineral functionality
        pass
    return redirect(url_for('admin_dashboard'))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
