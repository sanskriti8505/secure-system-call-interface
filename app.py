import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from core.syscall_wrapper import secure_read_file, secure_write_file, secure_delete_file, secure_execute_command

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-cyber-key-2026'
# Use an absolute path for the SQLite DB to avoid path issues
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'system_v3.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')
    failed_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    action = db.Column(db.String(50), nullable=False)
    result = db.Column(db.String(255), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def log_action(username, action, result):
    log_entry = Log(username=username, action=action, result=result)
    db.session.add(log_entry)
    db.session.commit()

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user:
            # Check if account is locked
            if user.locked_until and user.locked_until > datetime.utcnow():
                flash('Account is locked due to multiple failed login attempts. Please try again later.', 'danger')
                return render_template('login.html')
            
            # Check password
            if bcrypt.check_password_hash(user.password_hash, password):
                # Successful login: reset counters
                user.failed_attempts = 0
                user.locked_until = None
                db.session.commit()
                
                login_user(user)
                log_action(user.username, "login", "Success")
                return redirect(url_for('dashboard'))
            else:
                # Failed login: increment counter
                user.failed_attempts += 1
                if user.failed_attempts >= 3:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                    flash('Account locked for 15 minutes due to 3 failed login attempts.', 'danger')
                    log_action(user.username, "login", "Account Locked")
                else:
                    flash('Login Unsuccessful. Please check username and password', 'danger')
                    log_action(user.username, "login", f"Failed (Attempt {user.failed_attempts})")
                db.session.commit()
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            log_action(username or "unknown", "login", "Failed - User not found")
                
    return render_template('login.html')

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        log_action(current_user.username, "logout", "Success")
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logs')
@login_required
def logs_viewer():
    if current_user.role != 'admin':
        flash('Permission denied to view all logs.', 'danger')
        return redirect(url_for('dashboard'))
    logs = Log.query.order_by(Log.timestamp.desc()).all()
    return render_template('logs.html', logs=logs)

@app.route('/api/execute', methods=['POST'])
@login_required
def execute_action():
    data = request.json
    action_type = data.get('action')
    target = data.get('target', '')
    content = data.get('content', '')
    
    result = None
    if action_type == 'read':
        result = secure_read_file(target, current_user)
    elif action_type == 'write':
        result = secure_write_file(target, content, current_user)
    elif action_type == 'delete':
        result = secure_delete_file(target, current_user)
    elif action_type == 'execute':
        result = secure_execute_command(target, current_user)
    else:
        result = {"status": "error", "message": "Invalid action type"}
        
    # Log the attempt
    status_summary = result.get('status', 'unknown')
    msg = result.get('message', '')[:100] # Truncate long messages for logs
    log_action(current_user.username, f"{action_type} on '{target}'", f"{status_summary}: {msg}")
    
    return jsonify(result)

def setup_database():
    with app.app_context():
        db.create_all()
        # Create authorized users if they don't exist
        users_to_create = [
            {'username': 'Amritesh', 'role': 'user'},
            {'username': 'Harshita', 'role': 'user'},
            {'username': 'Sanskriti', 'role': 'admin'}
        ]
        
        for u in users_to_create:
            if not User.query.filter_by(username=u['username']).first():
                # Password is username in lowercase + '123'
                hashed_pw = bcrypt.generate_password_hash(f"{u['username'].lower()}123").decode('utf-8')
                new_user = User(username=u['username'], password_hash=hashed_pw, role=u['role'])
                db.session.add(new_user)
        
        db.session.commit()

if __name__ == '__main__':
    setup_database()
    app.run(debug=True)
