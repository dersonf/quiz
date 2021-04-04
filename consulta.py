from app.models import Perguntas, Respostas

perguntas = Perguntas.query.all()

for pergunta in perguntas:
    print(
        f"id: {pergunta.id}, pergunta: {pergunta.pergunta},"
        f"dificuldade: {pergunta.dificuldade}, classe: {pergunta.classe}"
    )