from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from models import User, Manuscript
from forms import LoginForm, RegisterForm, ManuscriptForm

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'author':
            return redirect(url_for('author_home'))
        elif current_user.role == 'editor':
            return redirect(url_for('editor_home'))
    return redirect(url_for('login'))

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            if user.role == 'author':
                return redirect(url_for('author_home'))
            elif user.role == 'editor':
                return redirect(url_for('editor_home'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if username already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('此使用者名稱已存在', 'danger')
            return render_template('register.html', form=form)
        user = User(username=form.username.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Registration failed: ' + str(e), 'danger')
            return render_template('register.html', form=form)
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Author routes
@app.route('/author')
@login_required
def author_home():
    if current_user.role != 'author':
        abort(403)
    manuscripts = Manuscript.query.filter_by(author_id=current_user.id).all()
    return render_template('author_home.html', manuscripts=manuscripts)

@app.route('/author/new', methods=['GET', 'POST'])
@login_required
def author_new():
    if current_user.role != 'author':
        abort(403)
    form = ManuscriptForm()
    if form.validate_on_submit():
        manuscript = Manuscript(
            author_id=current_user.id,
            category=form.category.data,
            title=form.title.data,
            content=form.content.data,
            status='Draft'
        )
        db.session.add(manuscript)
        db.session.commit()
        flash('Manuscript created.', 'success')
        return redirect(url_for('author_home'))
    return render_template('author_edit.html', form=form, edit=False)

@app.route('/author/edit/<int:mid>', methods=['GET', 'POST'])
@login_required
def author_edit(mid):
    if current_user.role != 'author':
        abort(403)
    manuscript = Manuscript.query.get_or_404(mid)
    if manuscript.author_id != current_user.id or manuscript.status != 'Draft':
        abort(403)
    form = ManuscriptForm(obj=manuscript)
    if form.validate_on_submit():
        manuscript.category = form.category.data
        manuscript.title = form.title.data
        manuscript.content = form.content.data
        db.session.commit()
        flash('Manuscript updated.', 'success')
        return redirect(url_for('author_home'))
    return render_template('author_edit.html', form=form, edit=True)

@app.route('/author/delete/<int:mid>', methods=['POST'])
@login_required
def author_delete(mid):
    if current_user.role != 'author':
        abort(403)
    manuscript = Manuscript.query.get_or_404(mid)
    if manuscript.author_id != current_user.id or manuscript.status != 'Draft':
        abort(403)
    db.session.delete(manuscript)
    db.session.commit()
    flash('Manuscript deleted.', 'info')
    return redirect(url_for('author_home'))

@app.route('/author/submit/<int:mid>', methods=['POST'])
@login_required
def author_submit(mid):
    if current_user.role != 'author':
        print(f">>> [403 Forbidden] current_user.role is {current_user.role}, expected 'author'")
        abort(403)
    manuscript = Manuscript.query.get_or_404(mid)
    if manuscript.author_id != current_user.id:
        print(f">>> [403 Forbidden] manuscript.author_id ({manuscript.author_id}) != current_user.id ({current_user.id})")
        abort(403)
    if manuscript.status != 'Draft':
        print(f">>> [403 Forbidden] manuscript.status is '{manuscript.status}', expected 'Draft'")
        abort(403)
    manuscript.status = 'Under Review'
    db.session.commit()
    flash('Manuscript submitted for review.', 'success')
    return redirect(url_for('author_home'))

# Editor routes
@app.route('/editor')
@login_required
def editor_home():
    if current_user.role != 'editor':
        abort(403)
    manuscripts = Manuscript.query.filter_by(status='Under Review').all()
    return render_template('editor_home.html', manuscripts=manuscripts)

@app.route('/editor/view/<int:mid>')
@login_required
def editor_view(mid):
    if current_user.role != 'editor':
        abort(403)
    manuscript = Manuscript.query.get_or_404(mid)
    if manuscript.status != 'Under Review':
        abort(403)
    return render_template('editor_view.html', manuscript=manuscript)

@app.route('/editor/approve/<int:mid>', methods=['POST'])
@login_required
def editor_approve(mid):
    if current_user.role != 'editor':
        abort(403)
    manuscript = Manuscript.query.get_or_404(mid)
    if manuscript.status != 'Under Review':
        abort(403)
    manuscript.status = 'Approved'
    db.session.commit()
    flash('Manuscript approved.', 'success')
    return redirect(url_for('editor_home'))

@app.route('/editor/reject/<int:mid>', methods=['POST'])
@login_required
def editor_reject(mid):
    if current_user.role != 'editor':
        abort(403)
    manuscript = Manuscript.query.get_or_404(mid)
    if manuscript.status != 'Under Review':
        abort(403)
    manuscript.status = 'Draft'
    db.session.commit()
    flash('Manuscript rejected and returned to author.', 'info')
    return redirect(url_for('editor_home'))
from flask_wtf.csrf import CSRFError

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    print(f">>> [CSRF Error 400/403]: {e.description}")
    return f"CSRF validation failed: {e.description}", 403

@app.route('/debug')
def debug():
    # 這行會在終端機（PowerShell）印出訊息，讓你確認程式已被載入
    print('>>> DEBUG: /debug 路由已被呼叫')
    return '✅ Flask 正在執行，已載入最新的 routes.py'