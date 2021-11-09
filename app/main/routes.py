from app.main import bp
from app.models import Perguntas, Respostas
from flask import render_template, session, url_for, redirect, flash
from flask_login import current_user
from app.main.forms import NomeForm
from random import choice


@bp.route('/')
def index():
    return render_template('index.html', title='Home')


@bp.route('/iniciar', methods=['GET', 'POST'])
def iniciar():
    """Função para iniciar o jogo"""
    form = NomeForm()
    if form.validate_on_submit():
        session['nome'] = form.nome.data.title()
        _inicia_sessao()
        return redirect(url_for('main.gera_pergunta'))
    if current_user.is_authenticated:
        session['nome'] = current_user.fullname
        _inicia_sessao()
        return redirect(url_for('main.gera_pergunta'))
    elif session.get('nome'):
        form.nome.data = session.get('nome')
    return render_template('iniciar.html', title='Iniciar', form=form)


def _inicia_sessao():
    """Inicia os dados da sessão."""
    session['pontos'] = 0
    session['perguntas'] = []
    session['jogando'] = 1
    session['nivel'] = 'D'
    session['multiplicador'] = 1
    session['gerado_pergunta'] = 0
    session['pulos'] = 1


@bp.route('/gera_pergunta')
def gera_pergunta():
    """Função que gera o form da pergunta"""
    if int(session.get('gerado_pergunta')) == 0:
        pergunta = _sorteia_pergunta()
        # Pega as respostas da pergunta
        respostas = Respostas.query.filter_by(pergunta_id=pergunta.id)
        # list comprehension
        session['opcoes'] = [
            (resposta.id, resposta.resposta) for resposta in respostas
            ]
        session['pergunta_id'] = pergunta.id
        session['gerado_pergunta'] = 1
    return redirect(url_for('pergunta'))


def _sorteia_pergunta():
    """Sorteia uma pergunta que não foi feita na sessão."""
    # Pega todas as perguntas do nivel
    perguntas = Perguntas.query.filter_by(classe=session.get('nivel'))
    # Coloca o id das perguntas em uma lista exceto as já feitas
    # list comprehension
    id_perguntas = [pergunta.id for pergunta in perguntas
                    if pergunta.id not in session.get('perguntas')]
    # Se acabar todas as perguntas finaliza o jogo
    if not id_perguntas:
        return redirect(url_for('fim'))
    # Sorteia uma pergunta e retorna ela
    return Perguntas.query.get(choice(id_perguntas))


@bp.route('/pular')
def pular():
    """Pula a pergunta"""
    if int(session.get('pulos')) > 0:
        session['pulos'] = 0
        session['gerado_pergunta'] = 0
        flash("Pulou a pergunta.")
        return redirect(url_for('main.gera_pergunta'))
    else:
        flash("Acabaram seus pulos.")
        return redirect(url_for('pergunta'))
