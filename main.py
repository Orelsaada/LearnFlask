from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = '123'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(200))
    complete = db.Column(db.Boolean)
    
class RegisterationForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(10), unique= True)
    password = db.Column(db.String(20))
    

@app.route("/", methods=['GET', 'POST'])
def register():
    form = RegisterationForm()
    if form.validate_on_submit():
        user = User(username= form.username.data, password= form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registered!')
        return redirect(url_for('login'))
    flash('Unsuccessful')
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if form.password.data == user.password:
                return redirect(url_for('todo'))
    return render_template('login.html', form=form)

@app.route("/todo")
def todo():
    todos = Todo.query.all()
    return render_template('todo.html', todos=todos)

@app.route("/add", methods=['POST'])
def add():
    item = Todo(text= request.form.get('item'), complete=False)
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('todo'))

@app.route("/remove/<id>", methods=['POST'])
def remove(id):
    Todo.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('todo'))
    

if __name__ == '__main__':
    app.run(debug=True)
