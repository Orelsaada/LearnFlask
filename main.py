from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import UserMixin, LoginManager, current_user, login_required, login_user, logout_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = '123'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.init_app(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(200))
    complete = db.Column(db.Boolean)
    shared = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
class RegisterationForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken.')

class LoginForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(10), unique=True, index=True)
    password = db.Column(db.String(20))
    todos = db.relationship('Todo', backref='owner', lazy=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    

@app.route("/", methods=['GET', 'POST'])
def register():
    form = RegisterationForm()
    if form.validate_on_submit():
        user = User(username= form.username.data, password= form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registered!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title='Register')

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and form.password.data == user.password:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('mytodo'))
        else:
            flash('Unsuccesful login. Try again.')
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/database")
@login_required
def database():
    if current_user.username == 'admin':
        users = User.query.all()
        return render_template('database.html', users=users)
    abort(401)

@app.route("/resetdb", methods=['POST', 'GET'])
def resetdb():
    reset_database()
    return redirect(url_for('database'))

@app.route("/mytodo")
@login_required
def mytodo():
    user  = current_user
    todos = Todo.query.filter_by(user_id = user.id)
    return render_template('mytodo.html', todos=todos, user=user)



@app.route("/add", methods=['POST'])
def add():
    user = current_user
    item = Todo(text= request.form.get('item'), complete=False, user_id=user.id, shared=False)
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('mytodo'))

@app.route("/remove/<id>", methods=['POST'])
def remove(id):
    Todo.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('mytodo'))


@app.route("/sharedtodo")
def sharedtodo():
    shared_todos = Todo.query.filter_by(shared=True).all()
    return render_template('sharedtodo.html', shared_todos=shared_todos)


@app.route("/share/<todo_id>", methods=['POST', 'GET'])
def share(todo_id):
    todo_to_share = Todo.query.filter_by(id=todo_id).first()
    todo_to_share.shared = True
    db.session.commit()
    return redirect(url_for('sharedtodo'))



def reset_database():
    users = User.query.delete()
    db.session.commit()
    

if __name__ == '__main__':
    app.run(debug=False)
