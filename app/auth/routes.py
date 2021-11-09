from app.auth import bp
from flask import redirect, flash, render_template, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app.auth.forms import UserLoginForm, RegistroUsuarioForm, PerfilForm
from app.models import Usuarios
from app import db


@bp.route('/logon', methods=['GET', 'POST'])
def logon():
    '''Efetua a autenticação e validação do usuário'''
    form = UserLoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = Usuarios.query.filter_by(username=username).first()
        if user is None or not user.valida_senha(password):
            flash('Acesso negado.')
            return redirect(url_for('auth.logon'))
        login_user(user)
        flash('Acesso liberado.')
        # Medidas de segurança para não forjar acesso
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('logon.html', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/registro', methods=['GET', 'POST'])
@login_required
def registro():
    '''Registro de usuário'''
    form = RegistroUsuarioForm()
    if form.validate_on_submit():
        new_user = Usuarios(username=form.username.data,
            fullname=form.fullname.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash(f"Usuário {form.username.data} cadastrado")
        return redirect(url_for('auth.registro'))
    return render_template('registro.html', form=form)


@bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    '''Editar o perfil do usuário'''
    form = PerfilForm()
    if form.validate_on_submit():
        user = Usuarios.query.get(current_user.id)
        user.fullname = form.fullname.data
        db.session.add(user)
        db.session.commit()
        flash('Dados atualizados')
        return redirect(url_for('auth.perfil'))
    form.fullname.data = current_user.fullname
    return render_template('perfil.html', form=form)
