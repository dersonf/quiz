from flask import render_template, redirect, url_for, flash
from app.forms import CadastroForm
from app import app, db
from app.models import Perguntas, Respostas
from random import choice

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


@app.route('/jogar')
def jogar():
    id_perguntas = []
    perguntas = Perguntas.query.all()
    for id in perguntas:
        id_perguntas.append(id.id)
    pergunta = Perguntas.query.get(choice(id_perguntas))
    respostas = Respostas.query.filter_by(pergunta_id=pergunta.id)
    return render_template('pergunta.html', title=pergunta, pergunta=pergunta, respostas=respostas)
