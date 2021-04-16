from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, app, login


class Perguntas(db.Model):
    """Tabela das perguntas"""
    id = db.Column(db.Integer, unique=True, primary_key=True)
    pergunta = db.Column(db.String(140))
    dificuldade = db.Column(db.Integer, default=0)
    classe = db.Column(db.String(1), default='D')


class Respostas(db.Model):
    """Tabela das respostas"""
    id = db.Column(db.Integer, primary_key=True)
    resposta = db.Column(db.String(140))
    pergunta_id = db.Column(db.Integer, db.ForeignKey('perguntas.id'))
    correta = db.Column(db.Boolean, default=False)


class Usuarios(UserMixin, db.Model):
    """Tabela de usuários"""
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(14), unique=True)
    fullname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def define_senha(self, password):
        """Define a hash do usuario"""
        self.password = generate_password_hash(password)

    def valida_senha(self, password):
        """Valida a senha"""
        return check_password_hash(self.password, password)


class ScoreBoard(db.Model):
    """Tabela de pontuacao"""
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(20))
    pontos = db.Column(db.Integer)
