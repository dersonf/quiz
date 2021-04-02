from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
    abort,
)
from app.forms import (
    CadastroForm,
    PerguntaForm,
    ConsultaForm,
    EditaPerguntaForm,
    EditaRespostaForm,
    NomeForm,
)
from app import app, db
from app.models import Perguntas, Respostas
from random import choice, sample
from wtforms import RadioField
from wtforms.validators import DataRequired
import jinja2
import logging

# logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html', title='Home')


@app.route('/add', methods=['GET', 'POST'])
def add():
    """Função que cadastra pergunta"""
    form = CadastroForm()
    if form.validate_on_submit():
        p = Perguntas(pergunta=form.pergunta.data, dificuldade=form.dificuldade.data)
        db.session.add(p)
        db.session.commit()
        if form.correta.data == 'resposta1':
            resposta1 = Respostas(resposta=form.resposta1.data, pergunta_id=p.id, correta=True)
        else:
            resposta1 = Respostas(resposta=form.resposta1.data, pergunta_id=p.id)
        if form.correta.data == 'resposta2':
            resposta2 = Respostas(resposta=form.resposta2.data, pergunta_id=p.id, correta=True)
        else:
            resposta2 = Respostas(resposta=form.resposta2.data, pergunta_id=p.id)
        if form.correta.data == 'resposta3':
            resposta3 = Respostas(resposta=form.resposta3.data, pergunta_id=p.id, correta=True)
        else:
            resposta3 = Respostas(resposta=form.resposta3.data, pergunta_id=p.id)
        if form.correta.data == 'resposta4':
            resposta4 = Respostas(resposta=form.resposta4.data, pergunta_id=p.id, correta=True)
        else:
            resposta4 = Respostas(resposta=form.resposta4.data, pergunta_id=p.id)
        db.session.add_all([resposta1, resposta2, resposta3, resposta4])
        db.session.commit()
        flash('Pergunta cadastrada com sucesso!')
        return redirect(url_for('index'))
    return render_template('cadastro.html', title='Cadastro', form=form)


@app.route('/pergunta/<pergunta>', methods=['GET', 'POST'])
def pergunta(pergunta):
    """Função que faz a pergunta e corrige"""
    pergunta = Perguntas.query.get(pergunta)
    form = PerguntaForm()
    if form.validate_on_submit():
        return redirect(url_for('corrigir', resposta=form.resposta.data))
    return render_template('pergunta.html', title='Pergunta:', pergunta=pergunta, form=form)


@app.route('/gera_pergunta')
def gera_pergunta():
    """Função que gera o form da pergunta"""
    id_perguntas, opcoes = [], []
    session['perguntas'] = session.get('perguntas')
    # Pega todas as perguntas
    perguntas = Perguntas.query.all()
    # Coloca o id das perguntas em uma lista exceto as já feitas
    for id in perguntas:
        if id.id not in session['perguntas']:
            id_perguntas.append(id.id)
    # Se acabar todas as perguntas finaliza o jogo
    if not id_perguntas:
        return redirect('/corrigir/fim')
    # Sorteia uma pergunta
    pergunta = Perguntas.query.get(choice(id_perguntas))
    # Coloca na sessão perguntas já feitas
    session['perguntas'].append(pergunta.id)
    # Pega as respostas da pergunta
    respostas = Respostas.query.filter_by(pergunta_id=pergunta.id)
    for resposta in respostas:
        temp = (resposta.id, resposta.resposta)
        opcoes.append(temp)
    setattr(PerguntaForm, 'resposta', RadioField('Respostas', choices=sample(opcoes, k=4), validators=[DataRequired()]))
    return redirect(url_for('pergunta', pergunta=pergunta.id))


@app.route('/corrigir/<resposta>')
def corrigir(resposta):
    """Função que corrige a pergunta"""
    if resposta == 'fim':
        session.clear()
        return render_template('index.html', title='Acabaram as perguntas. 500.000 pontos!!!')
    valida = Respostas.query.get(resposta)
    pergunta = Perguntas.query.get(valida.pergunta_id)
    if valida.correta == True:
        session['pontos'] = session.get('pontos') + 1000
        if pergunta.dificuldade >= 0:
            pergunta.dificuldade -= 1
            db.session.commit()
        return redirect(url_for('acertou'))
    else:
        if pergunta.dificuldade <= 400:
            pergunta.dificuldade += 1
            db.session.commit()
        pontos = session.get('pontos')
        nome = session.get('nome')
        session.clear()
        return render_template('errou.html', title='Errou!!!', nome=nome, pontos=pontos, pergunta=pergunta, resposta=valida)


@app.route('/acertou')
def acertou():
    return render_template('acerto.html', title='Correto!!!') 


@app.route('/consulta', methods=['GET', 'POST'])
def consulta():
    """Função que faz a consulta no banco sobre a pergunta"""
    form = ConsultaForm()
    if form.validate_on_submit():
        try:
            pergunta = Perguntas.query.get(form.pergunta_id.data)
            respostas = Respostas.query.filter_by(pergunta_id=pergunta.id)
            return render_template('consulta.html', title='Editar', form=form, pergunta=pergunta, respostas=respostas)
        except AttributeError:
            flash("ID não existe.")
        else:
            return redirect(url_for('consulta'))
    try:
        return render_template('consulta.html', title='Editar', form=form)
    except jinja2.exceptions.UndefinedError:
        flash("ID não existe.")
        return redirect(url_for('consulta'))


@app.route('/editar/<tipo>/<id>', methods=['GET', 'POST'])
def editar(tipo, id):
    """Função para a edição da pergunta"""
    if tipo == 'pergunta':
        pergunta = Perguntas.query.get(id)
        form = EditaPerguntaForm()
    elif tipo == 'resposta':
        resposta = Respostas.query.get(id)
        form = EditaRespostaForm()
    if form.validate_on_submit():
        if tipo == 'pergunta':
            pergunta.pergunta = form.pergunta.data
            pergunta.dificuldade = form.dificuldade.data
        elif tipo == 'resposta':
            resposta.resposta = form.resposta.data
            resposta.correta = form.correta.data
        db.session.commit()
        flash('Pergunta atualizada com sucesso!')
        return redirect(url_for('consulta'))
    if tipo == 'pergunta':
        form.pergunta.data = pergunta.pergunta
        form.dificuldade.data = pergunta.dificuldade
    elif tipo == 'resposta':        
        form.resposta.data = resposta.resposta
        form.correta.data = resposta.correta
    return render_template('edita_pergunta.html', form=form)


@app.route('/iniciar', methods=['GET', 'POST'])
def iniciar():
    """Função para iniciar o jogo"""
    form = NomeForm()
    if form.validate_on_submit():
        session['nome'] = form.nome.data.title()
        session['pontos'] = 0
        session['perguntas'] = []
        session['jogando'] = 1
        return redirect(url_for('gera_pergunta'))
    else:
        print(form.errors)
    return render_template('iniciar.html', title='Iniciar', form=form)


# Decorator pra limpar a sessão
# @session_clear
# def clear_session():
#     session.clear()