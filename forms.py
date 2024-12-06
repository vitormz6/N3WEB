from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length
from flask_babel import _

class UserForm(FlaskForm):
    name = StringField(_('Nome'), validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField(_('Email'), validators=[DataRequired(), Email(), Length(max=120)])
    role = SelectField(_('Papel'), choices=[('user', _('Usuário')), ('admin', _('Admin'))], validators=[DataRequired()])
    password = PasswordField(_('Senha'), validators=[DataRequired(), Length(min=6)])
    submit = SubmitField(_('Salvar'))

class ProductForm(FlaskForm):
    name = StringField(_('Nome do Produto'), validators=[DataRequired()])
    submit = SubmitField(_('Salvar'))
