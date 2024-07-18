from flask import render_template, request, session, flash, redirect, url_for

from app import app, bcrypt, db
from app.decorator import login_required
from app.forms import RegistrationForm, LoginForm, AddBookForm, ConfirmDeleteForm
from app.models import User, Books


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/register', methods=['GET', 'POST'])
# @login_required(required=False)
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            session["password"] = form.password.data
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(
                full_name=form.full_name.data,
                username=form.username.data,
                email=form.email.data,
                password=hashed_password
            )
            db.session.add(user)
            db.session.commit()
            flash('You are now registered!', 'success')
            return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
# @login_required(required=True)
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                session['username'] = user.username
                session['id']= user.id
                flash('You are now logged in!', 'success')
                return redirect(url_for('ui_menu'))
            else:
                flash("Invalid email or password", "danger")
                return redirect(url_for('login'))
    return render_template('auth/login.html', form=form)


@app.route('/ui_menu')
@login_required(required=True)
def ui_menu():
   return  render_template('ui_menu/ui.html')

@app.route('/add_book',methods=['GET', 'POST'])
@login_required(required=True)
def add_book():
    form=AddBookForm()
    owner_id = session['id']
    if form.validate_on_submit():
        book=Books(title=form.title.data,
                   author=form.author.data,
                   page_count=form.page_count.data,
                   owner_id=owner_id)
        db.session.add(book)
        db.session.commit()
        flash('Your book has been added.', 'success')
        return redirect(url_for('ui_menu'))
    return  render_template("ui_menu/add_book.html", form=form)

@app.route('/my_book', methods=['GET', 'POST'])
@login_required(required=True)
def my_book():
    owner_id = session.get("id")
    books = Books.query.filter_by(owner_id=owner_id).all()
    return render_template("ui_menu/my_book.html", books=books)
@app.route('/delete_book', methods=['GET', 'POST'])
@login_required(required=True)
def delete_book():
    user_id = session.get("id")
    if request.method == "POST":
        book_id = request.form.get("book_id")
        book=Books.query.get(book_id)
        if book and book.owner_id == user_id:
            db.session.delete(book)
            db.session.commit()
            flash('Your book has been deleted.', 'success')
            return redirect(url_for('ui_menu'))




@app.route('/top_book', methods=['GET', 'POST'])
@login_required(required=True)
def top_book():
    pass

@app.route('/update_book', methods=['GET', 'POST'])
@login_required(required=True)
def update_book():
    owner_id = session.get("id")
    books = Books.query.filter_by(owner_id=owner_id).all()
    if request.method == 'GET':
        return  render_template('ui_menu/update.html',books=books)

@app.route("/update_/<int:book_id>", methods=["GET", "POST"])
@login_required(required=True)
def update_(book_id):
    book = Books.query.get_or_404(book_id)
    user_id = session.get("id")
    if book.owner_id != user_id:
        flash('You do not have permission to edit this post.', 'danger')
        return redirect(url_for('home'))

    if request.method == "POST":
        book.title = request.form['title']
        book.auther = request.form['auther']
        book.page_count = request.form['page_count']
        db.session.commit()
        flash("Book successfully updated", "success")
        return redirect(url_for("update"))

    return render_template("ui_menu/update_.html", book=book)

@app.route('/log_out')
@login_required(required=True)
def log_out():
    username=session.get('username')
    session.pop('username')
    flash(f"{username} user successfully logged out", "success")
    return redirect(url_for('home'))

@app.route('/user_delete', methods=['GET', 'POST'])
@login_required(required=True)
def user_delete():
    form = ConfirmDeleteForm()
    if form.validate_on_submit():
        if form.confirm.data:
            user_id = session['id']
            user = User.query.filter_by(username=session.get(user_id)).first()
            db.session.delete(user)
            db.session.commit()
            flash('Your account has been deleted successfully.', 'success')
            return redirect(url_for('home'))
        elif form.cancel.data:
            return redirect(url_for('ui_menu'))

    return render_template('ui_menu/delete_user.html', form=form)
