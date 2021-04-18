from flask_table import Table, Col


class Colocacao(Table):
    posicao = Col('Rank')
    username = Col('Nome')
    pontos = Col('Pontos')


class Item(object):
    def __init__(self, posicao, username, pontos):
        self.posicao = posicao
        self.username = username
        self.pontos = pontos
