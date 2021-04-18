# -*- coding: utf-8 -*-
from app.models import Perguntas, Respostas
from app import db

with open('QUESTOES.txt', encoding='latin-1') as f:
    for linha in f:
        # print(linha.splitlines()[0].split('";"'))
        for chave, entrada in enumerate(linha.splitlines()[0].split('";"')):
            if chave == 0:
                pergunta = entrada.split(';"')[1]
                # print(pergunta)
            elif chave == 7 or chave == 8 or chave == 9:
                pass
            else:
                if chave == 1:
                    r1 = entrada
                    # print(r1)
                elif chave == 2:
                    r2 = entrada
                    # print(r2)
                elif chave == 3:
                    r3 = entrada
                    # print(r3)
                elif chave == 4:
                    r4 = entrada
                    # print(r4)
                elif chave == 5:
                    correta = entrada
                    # print(correta)
                elif chave == 6:
                    if entrada == 'A':
                        dificuldade = 0
                        classe = 'D'
                    elif entrada == 'B':
                        dificuldade = 100
                        classe = 'C'
                    elif entrada == 'C':
                        dificuldade = 200
                        classe = 'B'
                    elif entrada == 'D':
                        dificuldade = 300
                        classe = 'A'
                    # print(classe, dificuldade)
                    # print(dificuldade)
                    # print(pergunta, dificuldade, classe)
                    pergunta = Perguntas(pergunta=pergunta,
                                         dificuldade=dificuldade,
                                         classe=classe)
                    db.session.add(pergunta)
                    db.session.commit()
                    resposta1 = Respostas(resposta=r1,
                                          pergunta_id=pergunta.id)
                    resposta2 = Respostas(resposta=r2,
                                          pergunta_id=pergunta.id)
                    resposta3 = Respostas(resposta=r3,
                                          pergunta_id=pergunta.id)
                    resposta4 = Respostas(resposta=r4,
                                          pergunta_id=pergunta.id)
                    db.session.add_all([
                        resposta1,
                        resposta2,
                        resposta3,
                        resposta4
                        ])
                    db.session.commit()
                    if correta == '1':
                        resposta1.correta = True
                    elif correta == '2':
                        resposta2.correta = True
                    elif correta == '3':
                        resposta3.correta = True
                    elif correta == '4':
                        resposta4.correta = True
                    db.session.commit()
