'''
Backlog:
Gravar na tabela de score só o que valer entre os 10
'''

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
from app.tabela import Colocacao, Item
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, login
from app.models import Perguntas, Respostas, Usuarios, ScoreBoard
from random import choice, sample
from wtforms import RadioField
from wtforms.validators import DataRequired
import jinja2


@login.user_loader
def load_user(id):
    return Usuarios.query.filter_by(id=id).first()


@app.route('/')
def index():
    return render_template('index.html', title='Home')


@app.route('/iniciar', methods=['GET', 'POST'])
def iniciar():
    """Função para iniciar o jogo"""
    form = NomeForm()
    if form.validate_on_submit():
        session['nome'] = form.nome.data.title()
        _inicia_sessao()
        return redirect(url_for('gera_pergunta'))
    if current_user.is_authenticated:
        session['nome'] = current_user.fullname
        _inicia_sessao()
        return redirect(url_for('gera_pergunta'))
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


@app.route('/gera_pergunta')
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


@app.route('/pular')
def pular():
    """Pula a pergunta"""
    if int(session.get('pulos')) > 0:
        session['pulos'] = 0
        session['gerado_pergunta'] = 0
        flash("Pulou a pergunta.")
        return redirect(url_for('gera_pergunta'))
    else:
        flash("Acabaram seus pulos.")
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


@app.route('/pergunta', methods=['GET', 'POST'])
def pergunta():
    """Função que faz a pergunta"""
    # Valida se a pergunta já foi feita
    pergunta = session.get('pergunta_id')
    try:
        if int(pergunta) in session.get('perguntas'):
            app.logger.info('Deve ter tentado roubar')
            session['nivel'] = 'A'
            return redirect(url_for('gera_pergunta'))
    except TypeError:
        return redirect(url_for('index'))
    setattr(PerguntaForm, 'resposta', RadioField(
        'Respostas',
        choices=sample(session.get('opcoes'), k=4),
        validators=[DataRequired()]))
    form = PerguntaForm()
    if form.validate_on_submit():
        return redirect(url_for('corrigir', resposta=form.resposta.data))
    pergunta = Perguntas.query.get(pergunta)
    return render_template('pergunta.html', title='Pergunta',
                           pergunta=pergunta, form=form)


@app.route('/corrigir/<resposta>')
def corrigir(resposta):
    """Função que corrige a pergunta"""
    valida = Respostas.query.get(resposta)
    pergunta = Perguntas.query.get(valida.pergunta_id)
    # Adiciona a pergunta feita a lista das já perguntadas
    session['perguntas'] = session.get('perguntas')
    session['gerado_pergunta'] = 0
    try:
        session['perguntas'].append(pergunta.id)
    except AttributeError:
        return redirect(url_for('index'))
    if valida.correta is True:
        session['pontos'] = session.get('pontos') + \
            (1000 * session.get('multiplicador'))
        # Aumenta a dificuldade a cada quantidade de perguntas
        if len(session.get('perguntas')) == 6:
            session['nivel'] = 'C'
            session['multiplicador'] = 2
            flash('Aumentando o nivel de dificuldade!!!')
        elif len(session.get('perguntas')) == 12:
            session['nivel'] = 'B'
            session['multiplicador'] = 3
            flash('Aumentando o nível de dificuldade!!!')
        elif len(session.get('perguntas')) == 18:
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
        grava_rank()
        limpa_sessao()
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
    grava_rank()
    limpa_sessao()
    return render_template('fim.html', title='Fim de jogo', nome=nome,
                           pontos=pontos)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Faz o login pra administração"""
    if current_user.is_authenticated:
        flash('Já autenticado!!!')
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuarios.query.filter_by(username=form.usuario.data).first()
        # app.logger.info(f"Autenticou {usuario.username}")
        if usuario is None or not usuario.valida_senha(form.senha.data):
            flash('Usuario e/ou senha incorretos!')
            return redirect(url_for('login'))
        login_user(usuario)
        flash(f"Bem vindo {usuario.fullname}!")
        return redirect(url_for('index'))
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/add', methods=['GET', 'POST'])
@login_required
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
@login_required
def consulta():
    """Função que faz a consulta no banco sobre a pergunta"""
    form = ConsultaForm()
    if form.validate_on_submit():
        try:
            pergunta = Perguntas.query.get(form.pergunta_id.data)
            respostas = Respostas.query.filter_by(pergunta_id=pergunta.id)
            return render_template('consulta.html', title='Consulta', form=form,
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
@login_required
def editar(tipo, id):
    """Função para a edição da pergunta e resposta"""
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
    return render_template('edita_pergunta.html', form=form, title='Edição')


def limpa_sessao():
    """Limpa a sessão do usuário ao fim do jogo"""
    session.pop('pontos', None)
    session.pop('perguntas', None)
    session.pop('jogando', None)
    session.pop('nivel', None)
    session.pop('multiplicador', None)
    session.pop('gerado_pergunta', None)

def grava_rank():
    pontos = session.get('pontos')
    usuario = session.get('nome')
    menor = db.session.query(ScoreBoard).order_by(
            ScoreBoard.pontos.asc()).first()
    print(menor.pontos)
    rank = ScoreBoard(username = usuario, pontos = pontos)
    db.session.add(rank)
    db.session.commit()


@app.route('/score')
def score():
    score = db.session.query(ScoreBoard).order_by(
            ScoreBoard.pontos.desc()).limit(10)
    # list comprehension
    items = [
        Item(str(posicao) + 'º', linha.username, linha.pontos)
        for posicao, linha in enumerate(score, 1)
        ]
    tabela = Colocacao(items)
    return render_template('ranking.html', title="Melhores Jogadores",
                           tabela=tabela)
