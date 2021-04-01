from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField, RadioField
from wtforms.validators import DataRequired


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
        (0, 'Fácil'),
        (33, 'Média'),
        (66, 'Difícil'),
        ])
    submit = SubmitField('Cadastrar')


class PerguntaForm(FlaskForm):
    # resposta = RadioField('Resposta', choices=[
    #     ('resposta1', 'Resposta 1'),
    #     ('resposta2', 'Resposta 2'),
    #     ('resposta3', 'Resposta 3'),
    #     ('resposta4', 'Resposta 4')
    #     ])
    submit = SubmitField('Responder')

    # def __init__(self, respostas: list = None, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.resposta.choices = respostas

