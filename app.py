from flask import Flask, request, session, render_template, redirect, url_for, flash
from flask_babel import Babel, gettext as _
from math import ceil
from config import Config
from models import db, User, Product
from auth import login_required, admin_required, get_current_user
from forms import UserForm, ProductForm

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

babel = Babel(app)

@babel.localeselector
def get_locale():
    return session.get('lang', 'pt')

@app.context_processor
def inject_get_locale():
    return {'get_locale': get_locale}

@app.route('/set_language/<lang_code>')
def set_language(lang_code):
    if lang_code in ['pt', 'en', 'es']:
        session['lang'] = lang_code
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    return render_template('index.html', user=get_current_user())

@app.route('/users')
@login_required
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    query = User.query
    total = query.count()
    users = query.offset((page-1)*per_page).limit(per_page).all()
    total_pages = ceil(total/per_page)
    return render_template('users.html', 
                           users=users, 
                           page=page, 
                           total_pages=total_pages,
                           user=get_current_user())

@app.route('/products')
@login_required
def list_products():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    query = Product.query
    total = query.count()
    products = query.offset((page-1)*per_page).limit(per_page).all()
    total_pages = ceil(total/per_page)
    return render_template('products.html', 
                           products=products, 
                           page=page, 
                           total_pages=total_pages,
                           user=get_current_user())

@app.route('/admin/create_user', methods=['GET', 'POST'])
@admin_required
def admin_create_user():
    form = UserForm()
    if form.validate_on_submit():
        # Verifica se já existe usuário com este nome ou email
        existing_user = User.query.filter((User.name == form.name.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash(_('Já existe um usuário com esse nome ou email.'), 'error')
            return render_template('admin_create_user.html', form=form, user=get_current_user())

        new_user = User(name=form.name.data, email=form.email.data, role=form.role.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash(_('Usuário criado com sucesso!'))
        return redirect(url_for('list_users'))
    return render_template('admin_create_user.html', form=form, user=get_current_user())

@app.route('/admin/edit_user/<int:user_id>', methods=['GET','POST'])
@admin_required
def admin_edit_user(user_id):
    user_edit = User.query.get_or_404(user_id)
    form = UserForm(obj=user_edit)

    # Ajuste: Se quiser tornar a senha opcional na edição, você precisaria
    # modificar o formulário ou lógica aqui. Por simplicidade, exigimos senha sempre.
    if form.validate_on_submit():
        # Verifica se já existe outro usuário com o mesmo nome ou email
        existing_user = User.query.filter((User.name == form.name.data) | (User.email == form.email.data), User.id != user_id).first()
        if existing_user:
            flash(_('Já existe um usuário com esse nome ou email.'), 'error')
            return render_template('admin_edit_user.html', form=form, user=user_edit, current_user=get_current_user())

        user_edit.name = form.name.data
        user_edit.email = form.email.data
        user_edit.role = form.role.data
        user_edit.set_password(form.password.data)  # Atualiza a senha

        db.session.commit()
        flash(_('Usuário atualizado com sucesso!'))
        return redirect(url_for('list_users'))
    return render_template('admin_edit_user.html', form=form, user=user_edit, current_user=get_current_user())

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user_del = User.query.get_or_404(user_id)
    db.session.delete(user_del)
    db.session.commit()
    flash(_('Usuário excluído com sucesso!'))
    return redirect(url_for('list_users'))

@app.route('/admin/create_product', methods=['GET','POST'])
@admin_required
def admin_create_product():
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(name=form.name.data)
        db.session.add(new_product)
        db.session.commit()
        flash(_('Produto criado com sucesso!'))
        return redirect(url_for('list_products'))
    return render_template('admin_create_product.html', form=form, user=get_current_user())

@app.route('/admin/edit_product/<int:product_id>', methods=['GET','POST'])
@admin_required
def admin_edit_product(product_id):
    prod = Product.query.get_or_404(product_id)
    form = ProductForm(obj=prod)
    if form.validate_on_submit():
        prod.name = form.name.data
        db.session.commit()
        flash(_('Produto atualizado com sucesso!'))
        return redirect(url_for('list_products'))
    return render_template('admin_edit_product.html', form=form, product=prod, user=get_current_user())

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
@admin_required
def admin_delete_product(product_id):
    prod = Product.query.get_or_404(product_id)
    db.session.delete(prod)
    db.session.commit()
    flash(_('Produto excluído com sucesso!'))
    return redirect(url_for('list_products'))

@app.route('/consult_users')
@login_required
def consult_users():
    # Exemplo com paginação já implementada anteriormente
    page = request.args.get('page', 1, type=int)
    per_page = 5
    query = User.query
    total = query.count()
    users = query.offset((page-1)*per_page).limit(per_page).all()
    total_pages = (total + per_page - 1) // per_page
    return render_template('consult_users.html', 
                           users=users, 
                           page=page, 
                           total_pages=total_pages,
                           user=get_current_user())

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/login_as_admin')
def login_as_admin():
    session['user_id'] = 1
    return redirect(url_for('index'))

@app.route('/login_as_user')
def login_as_user():
    user = User.query.filter_by(role='user').first()
    if user:
        session['user_id'] = user.id
    else:
        new_user = User(name='user2', email='user2@example.com', role='user')
        new_user.set_password('password123')
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Criando um admin se não existir
        if not User.query.first():
            admin = User(name='admin', email='admin@example.com', role='admin')
            admin.set_password('adminpass')
            db.session.add(admin)
            db.session.add(User(name='user1', email='user1@example.com', role='user', password_hash='fakehash')) # Ajustar depois
            db.session.add(Product(name='Produto A'))
            db.session.add(Product(name='Produto B'))
            db.session.commit()

    app.run(debug=True)
