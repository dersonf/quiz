from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    BooleanField,
    SubmitField,
    SelectField,
    RadioField,
    IntegerField,
    PasswordField,
)
from wtforms.validators import DataRequired


class BotaoConfirma(FlaskForm):
    submit = SubmitField('Consultar')


class CadastroForm(FlaskForm):
    pergunta = StringField('Pergunta', [DataRequired()])
    resposta1 = StringField('Resposta 1', [DataRequired()])
    resposta2 = StringField('Resposta 2', [DataRequired()])
    resposta3 = StringField('Resposta 3', [DataRequired()])
    resposta4 = StringField('Resposta 4', [DataRequired()])
    correta = SelectField('Correta', choices=[
        ('resposta1', 'Resposta 1'),
        ('resposta2', 'Resposta 2'),
        ('resposta3', 'Resposta 3'),
        ('resposta4', 'Resposta 4')
        ])
    dificuldade = SelectField('Dificuldade', choices=[
        (0, 'Muito fácil'),
        (100, 'Fácil'),
        (200, 'Média'),
        (300, 'Difícil'),
        ])
    classe = SelectField('Classe', choices=[
        ('D', 'Muito fácil'),
        ('C', 'Fácil'),
        ('B', 'Média'),
        ('A', 'Difícil'),
        ])
    submit = SubmitField('Cadastrar')


class PerguntaForm(FlaskForm):
    submit = SubmitField('Responder')


class ConsultaForm(BotaoConfirma):
    pergunta_id = IntegerField('ID', [DataRequired()])


class EditaPerguntaForm(FlaskForm):
    pergunta = StringField('Pergunta', [DataRequired()])
    dificuldade = IntegerField('Dificuldade', [DataRequired()])
    classe = StringField('Classe', [DataRequired()])
    submit = SubmitField('Confirma')


class EditaRespostaForm(FlaskForm):
    resposta = StringField('Resposta', [DataRequired()])
    correta = BooleanField('Correta')
    submit = SubmitField('Confirma')


class NomeForm(FlaskForm):
    texto = 'Seu nome ou apelido é somente utilizado para status de pontuação.'
    nome = StringField(label='Nome', description=texto,
                       validators=[DataRequired()])
    iniciar = SubmitField('Iniciar')


class LoginForm(FlaskForm):
    usuario = StringField('Usuário', [DataRequired()])
    senha = PasswordField('Senha', [DataRequired()])
    submit = SubmitField('Login')
