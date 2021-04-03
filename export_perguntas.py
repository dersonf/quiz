# -*- coding: utf-8 -*-
from app.models import Perguntas, Respostas

with open('QUESTOES.txt', encoding='latin-1') as f:
    for linha in f:
        # print(linha.splitlines()[0].split('";"'))
        for chave, entrada in enumerate(linha.splitlines()[0].split('";"')):
            if chave == 0:
                nova_entrada = entrada.split(';"')
                print(chave, nova_entrada[1])
            else:
                print(chave, entrada)

