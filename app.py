import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
from sqlalchemy import inspect

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESET_TOKEN'] = os.environ.get('RESET_TOKEN')

db = SQLAlchemy(app)

class Poll(db.Model):
    __tablename__ = 'Polls'
    PollID = db.Column(db.Integer, primary_key=True)
    PollDate = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    Title = db.Column(db.String(255), nullable=False)
    Options = db.relationship('PollOption', backref='poll', lazy=True)

class PollOption(db.Model):
    __tablename__ = 'PollOptions'
    PollOptionID = db.Column(db.Integer, primary_key=True)
    PollID = db.Column(db.Integer, db.ForeignKey('Polls.PollID'), nullable=False)
    OptionText = db.Column(db.String(255), nullable=False)
    Votes = db.relationship('Vote', backref='option', lazy=True)

class User(db.Model):
    __tablename__ = 'User'
    UserID = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    IsAdmin = db.Column(db.Boolean, default=False)
    Votes = db.relationship('Vote', backref='user', lazy=True)

class Vote(db.Model):
    __tablename__ = 'Vote'
    VoteID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=True)
    PollOptionID = db.Column(db.Integer, db.ForeignKey('PollOptions.PollOptionID'), nullable=False)

class BugReport(db.Model):
    __tablename__ = 'BugReports'
    ReportID = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(120), nullable=False)
    Message = db.Column(db.Text, nullable=False)
    DateSubmitted = db.Column(db.DateTime, default=datetime.utcnow)
    IsResolved = db.Column(db.Boolean, default=False)

with app.app_context():
    inspector = inspect(db.engine)
    if not inspector.has_table('User'):
        db.create_all()
        admin = User(Email='admin@jpoll.com', Password=generate_password_hash('admin', method='pbkdf2:sha256'), IsAdmin=True)
        db.session.add(admin)
        poll = Poll(Title="Kolik otevřených záložek je ještě normální?")
        db.session.add(poll)
        db.session.commit()
        opt1 = PollOption(PollID=poll.PollID, OptionText="Méně než 10")
        opt2 = PollOption(PollID=poll.PollID, OptionText="10 až 50")
        opt3 = PollOption(PollID=poll.PollID, OptionText="Více než 50 (Prohlížeč trpí)")
        db.session.add_all([opt1, opt2, opt3])
        db.session.commit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('today'))

@app.route('/today')
def today():
    poll = Poll.query.order_by(Poll.PollID.desc()).first()
    user_voted = False
    results = {}
    total_votes = 0
    
    if poll:
        for option in poll.Options:
            count = Vote.query.filter_by(PollOptionID=option.PollOptionID).count()
            results[option.PollOptionID] = count
            total_votes += count

        if 'user_id' in session:
            user_vote = Vote.query.join(PollOption).filter(
                Vote.UserID == session['user_id'],
                PollOption.PollID == poll.PollID
            ).first()
            if user_vote:
                user_voted = True

    is_admin = False
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.IsAdmin:
            is_admin = True

    return render_template('today.html', poll=poll, results=results, total_votes=total_votes, user_voted=user_voted, is_admin=is_admin)

@app.route('/about', methods=['GET', 'POST'])
def about():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('You must be logged in to submit a bug report.', 'danger')
            return redirect(url_for('login'))
            
        user = User.query.get(session['user_id'])
        email = user.Email
        message = request.form.get('message')
        
        if email and message:
            new_report = BugReport(Email=email, Message=message, IsResolved=False)
            db.session.add(new_report)
            db.session.commit()
            flash('Bug report submitted successfully.', 'success')
            return redirect(url_for('about'))
            
    return render_template('about.html')

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/user/login', methods=['POST'])
def api_user_login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(Email=email).first()
    if user and check_password_hash(user.Password, password):
        session['user_id'] = user.UserID
        flash('Logged in successfully.', 'success')
        return redirect(url_for('today'))
    flash('Invalid credentials.', 'danger')
    return redirect(url_for('login'))

@app.route('/user/register', methods=['POST'])
def api_user_register():
    email = request.form.get('email')
    password = request.form.get('password')
    if User.query.filter_by(Email=email).first():
        flash('Email already registered.', 'danger')
        return redirect(url_for('login'))
    
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(Email=email, Password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    flash('Registration successful. Please log in.', 'success')
    return redirect(url_for('login'))

@app.route('/poll/vote', methods=['POST'])
@login_required
def api_poll_vote():
    option_id = request.form.get('option_id')
    if option_id:
        option = PollOption.query.get(option_id)
        if option:
            existing_vote = Vote.query.join(PollOption).filter(
                Vote.UserID == session['user_id'],
                PollOption.PollID == option.PollID
            ).first()
            if not existing_vote:
                new_vote = Vote(UserID=session['user_id'], PollOptionID=option_id)
                db.session.add(new_vote)
                db.session.commit()
                flash('Vote recorded.', 'success')
            else:
                flash('You have already voted in this poll.', 'warning')
    return redirect(url_for('today'))

@app.route('/poll/results', methods=['GET'])
def api_poll_results():
    poll = Poll.query.order_by(Poll.PollID.desc()).first()
    if not poll:
        return jsonify({"error": "No poll found"}), 404
    
    data = {"poll": poll.Title, "results": []}
    for option in poll.Options:
        count = Vote.query.filter_by(PollOptionID=option.PollOptionID).count()
        data["results"].append({
            "option": option.OptionText,
            "votes": count
        })
    return jsonify(data)

@app.route('/poll/reset', methods=['POST'])
@login_required
def reset_poll():
    user = User.query.get(session['user_id'])
    if not user or not user.IsAdmin:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('today'))

    token = request.form.get('reset_token')
    if token == app.config['RESET_TOKEN']:
        poll_id = request.form.get('poll_id')
        options = PollOption.query.filter_by(PollID=poll_id).all()
        for opt in options:
            Vote.query.filter_by(PollOptionID=opt.PollOptionID).delete()
        db.session.commit()
        flash('Poll votes have been reset.', 'success')
    else:
        flash('Invalid reset token.', 'danger')
    
    return redirect(url_for('today'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('today'))

if __name__ == '__main__':
    port = int(os.environ.get('APP_PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)