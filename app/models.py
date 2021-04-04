from app import db, app


class Perguntas(db.Model):
    'Tabela das perguntas'
    id = db.Column(db.Integer, unique=True ,primary_key=True)
    pergunta = db.Column(db.String(140))
    dificuldade = db.Column(db.Integer, default=0)
    classe = db.Column(db.String(1), default='D')


class Respostas(db.Model):
    'Tabela das respostas'
    id = db.Column(db.Integer, primary_key=True)
    resposta = db.Column(db.String(140))
    pergunta_id = db.Column(db.Integer, db.ForeignKey('perguntas.id'))
    correta = db.Column(db.Boolean, default=False)
