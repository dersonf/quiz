from flask import render_template, redirect, url_for, flash, request
from app.forms import CadastroForm, PerguntaForm
from app import app, db
from app.models import Perguntas, Respostas
from random import choice, sample

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


@app.route('/pergunta', methods=['GET', 'POST'])
def pergunta():
    id_perguntas = []
    # Pega todas as perguntas
    perguntas = Perguntas.query.all()
    # Coloca o id das perguntas em uma lista
    for id in perguntas:
        id_perguntas.append(id.id)
    # Sorteia uma pergunta
    pergunta = Perguntas.query.get(choice(id_perguntas))
    # Pega as respostas da pergunta
    respostas = Respostas.query.filter_by(pergunta_id=pergunta.id)
    opcoes = []
    for resposta in respostas:
        temp = (resposta.id, resposta.resposta)
        opcoes.append(temp)
    form = PerguntaForm(respostas=sample(opcoes, k=4))
    if form.validate_on_submit():
        print(form)
        return redirect(url_for('pergunta'))
    return render_template('pergunta.html', title='Pergunta', pergunta=pergunta,
                           respostas=respostas, form=form)


@app.route('/corrigir', methods=['POST'])
def corrigir():
    print(request.data)
    return redirect(url_for('index'))


