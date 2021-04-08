from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
)
from app.forms import (
    CadastroForm,
    PerguntaForm,
    ConsultaForm,
    EditaPerguntaForm,
    EditaRespostaForm,
    NomeForm,
    LoginForm,
)
from app import app, db
from app.models import Perguntas, Respostas, Usuarios
from random import choice, sample
from wtforms import RadioField
from wtforms.validators import DataRequired
import jinja2

@app.route('/')
def index():
    return render_template('index.html', title='Home')


@app.route('/iniciar', methods=['GET', 'POST'])
def iniciar():
    """Função para iniciar o jogo"""
    form = NomeForm()
    if form.validate_on_submit():
        session['nome'] = form.nome.data.title()
        session['pontos'] = 0
        session['perguntas'] = []
        session['jogando'] = 1
        session['nivel'] = 'D'
        session['multiplicador'] = 1
        return redirect(url_for('gera_pergunta'))
    return render_template('iniciar.html', title='Iniciar', form=form)


@app.route('/gera_pergunta')
def gera_pergunta():
    """Função que gera o form da pergunta"""
    session['opcoes'] = []
    pergunta = _sorteia_pergunta()
    # Pega as respostas da pergunta
    respostas = Respostas.query.filter_by(pergunta_id=pergunta.id)
    for resposta in respostas:
        session['opcoes'].append((resposta.id, resposta.resposta))
    session['pergunta_id'] = pergunta.id
    return redirect(url_for('pergunta'))


def _sorteia_pergunta():
    """Sorteia uma pergunta que não foi feita na sessão."""
    id_perguntas = []    
    # Pega todas as perguntas do nivel
    perguntas = Perguntas.query.filter_by(classe=session.get('nivel'))
    # Coloca o id das perguntas em uma lista exceto as já feitas
    for pergunta in perguntas:
        if pergunta.id not in session.get('perguntas'):
            id_perguntas.append(pergunta.id)
    # Se acabar todas as perguntas finaliza o jogo
    if not id_perguntas:
        return redirect(url_for('fim'))
    # Sorteia uma pergunta e retorna ela
    return Perguntas.query.get(choice(id_perguntas))


@app.route('/pergunta', methods=['GET', 'POST'])
def pergunta():
    """Função que faz a pergunta"""
    # Valida se a pergunta já foi feita
    pergunta = session.get('pergunta_id')
    if int(pergunta) in session.get('perguntas'):
        app.logger.info('Deve ter tentado roubar')
        session['nivel'] = 'A'
        return redirect(url_for('gera_pergunta'))
    setattr(PerguntaForm, 'resposta', RadioField(
        'Respostas',
        choices=sample(session.get('opcoes'), k=4),
        validators=[DataRequired()]))
    form = PerguntaForm()
    if form.validate_on_submit():
        return redirect(url_for('corrigir', resposta=form.resposta.data))
    pergunta = Perguntas.query.get(pergunta)
    return render_template('pergunta.html', title='Pergunta:',
                           pergunta=pergunta, form=form)


@app.route('/corrigir/<resposta>')
def corrigir(resposta):
    """Função que corrige a pergunta"""
    valida = Respostas.query.get(resposta)
    pergunta = Perguntas.query.get(valida.pergunta_id)
    # Adiciona a pergunta feita a lista das já perguntadas
    session['perguntas'] = session.get('perguntas')
    session['perguntas'].append(pergunta.id)
    if valida.correta is True:
        session['pontos'] = session.get('pontos') + \
            (1000 * session.get('multiplicador'))
        # Aumenta a dificuldade a cada quantidade de perguntas
        if len(session.get('perguntas')) == 5:
            session['nivel'] = 'C'
            session['multiplicador'] = 2
            flash('Aumentando o nivel!!!')
        elif len(session.get('perguntas')) == 10:
            session['nivel'] = 'B'
            session['multiplicador'] = 3
            flash('Aumentando o nível!!!')
        elif len(session.get('perguntas')) == 15:
            session['nivel'] = 'A'
            session['multiplicador'] = 4
            flash('Aumentando para o nível mais alto!!!')
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
        return render_template('fim.html', title='Resposta incorreta!!!',
                               nome=nome, pontos=pontos, pergunta=pergunta,
                               resposta=valida)


@app.route('/acertou')
def acertou():
    return render_template('acerto.html', title='Correto!!!')


@app.route('/fim')
def fim():
    """Finaliza jogo em andamento"""
    nome = session.get('nome')
    pontos = session.get('pontos')
    session.clear()
    return render_template('fim.html', title='Fim de jogo', nome=nome,
                           pontos=pontos)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Faz o login pra administração"""
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuarios.query.filter_by(username=form.usuario.data).first()
        app.logger.info(f"Autenticou {usuario.username}")
        if usuario.valida_senha(form.senha.data) is True:
            flash('Usuário autenticado com sucesso!')
        else:
            flash('Usuario e senha incorretos!')
        return redirect(url_for('index'))
    return render_template('login.html', title='Login', form=form)


@app.route('/add', methods=['GET', 'POST'])
def add():
    """Função que cadastra pergunta"""
    form = CadastroForm()
    if form.validate_on_submit():
        p = Perguntas(
                pergunta=form.pergunta.data,
                dificuldade=form.dificuldade.data,
                classe=form.classe.data
            )
        db.session.add(p)
        db.session.commit()
        if form.correta.data == 'resposta1':
            resposta1 = Respostas(resposta=form.resposta1.data,
                                  pergunta_id=p.id, correta=True)
        else:
            resposta1 = Respostas(resposta=form.resposta1.data,
                                  pergunta_id=p.id)
        if form.correta.data == 'resposta2':
            resposta2 = Respostas(resposta=form.resposta2.data,
                                  pergunta_id=p.id, correta=True)
        else:
            resposta2 = Respostas(resposta=form.resposta2.data,
                                  pergunta_id=p.id)
        if form.correta.data == 'resposta3':
            resposta3 = Respostas(resposta=form.resposta3.data,
                                  pergunta_id=p.id, correta=True)
        else:
            resposta3 = Respostas(resposta=form.resposta3.data,
                                  pergunta_id=p.id)
        if form.correta.data == 'resposta4':
            resposta4 = Respostas(resposta=form.resposta4.data,
                                  pergunta_id=p.id, correta=True)
        else:
            resposta4 = Respostas(resposta=form.resposta4.data,
                                  pergunta_id=p.id)
        db.session.add_all([resposta1, resposta2, resposta3, resposta4])
        db.session.commit()
        flash('Pergunta cadastrada com sucesso!')
        return redirect(url_for('index'))
    return render_template('cadastro.html', title='Cadastro de pergunta',
                           form=form)


@app.route('/consulta', methods=['GET', 'POST'])
def consulta():
    """Função que faz a consulta no banco sobre a pergunta"""
    form = ConsultaForm()
    if form.validate_on_submit():
        try:
            pergunta = Perguntas.query.get(form.pergunta_id.data)
            respostas = Respostas.query.filter_by(pergunta_id=pergunta.id)
            return render_template('consulta.html', title='Editar', form=form,
                                   pergunta=pergunta, respostas=respostas)
        except AttributeError:
            flash("ID não existe.")
        else:
            return redirect(url_for('consulta'))
    try:
        return render_template('consulta.html', title='Edição de pergunta',
                               form=form)
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
            pergunta.classe = form.classe.data
        elif tipo == 'resposta':
            resposta.resposta = form.resposta.data
            resposta.correta = form.correta.data
        db.session.commit()
        flash('Pergunta atualizada com sucesso!')
        return redirect(url_for('consulta'))
    if tipo == 'pergunta':
        form.pergunta.data = pergunta.pergunta
        form.dificuldade.data = pergunta.dificuldade
        form.classe.data = pergunta.classe
    elif tipo == 'resposta':
        form.resposta.data = resposta.resposta
        form.correta.data = resposta.correta
    return render_template('edita_pergunta.html', form=form)
