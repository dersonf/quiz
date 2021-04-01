from flask import render_template, redirect, url_for, flash, request, session
from app.forms import CadastroForm, PerguntaForm
from app import app, db
from app.models import Perguntas, Respostas
from random import choice, sample
from wtforms import RadioField
from wtforms.validators import DataRequired

@app.route('/')
def index():
    return render_template('index.html', title='Home')


@app.route('/add', methods=['GET', 'POST'])
def add():
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
    pergunta = Perguntas.query.get(pergunta)
    form = PerguntaForm()
    if form.validate_on_submit():
        return redirect(url_for('corrigir', resposta=form.resposta.data))
    return render_template('pergunta.html', title='Pergunta', pergunta=pergunta, form=form)


@app.route('/gera_pergunta')
def gera_pergunta():
    id_perguntas, opcoes = [], []
    # Pega todas as perguntas
    perguntas = Perguntas.query.all()
    # Coloca o id das perguntas em uma lista
    for id in perguntas:
        id_perguntas.append(id.id)
    # Sorteia uma pergunta
    pergunta = Perguntas.query.get(choice(id_perguntas))
    # Pega as respostas da pergunta
    respostas = Respostas.query.filter_by(pergunta_id=pergunta.id)
    for resposta in respostas:
        temp = (resposta.id, resposta.resposta)
        opcoes.append(temp)
    setattr(PerguntaForm, 'resposta', RadioField('Respostas', choices=sample(opcoes, k=4), validators=[DataRequired()]))
    return redirect(url_for('pergunta', pergunta=pergunta.id))


@app.route('/corrigir/<resposta>')
def corrigir(resposta):
    valida = Respostas.query.get(resposta)
    if valida.correta == True:
        return render_template('acerto.html', title='Correção')
    else:
        session.clear()
        return render_template('errou.html', title='Correção')