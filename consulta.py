from app.models import Perguntas, Respostas

perguntas = Perguntas.query.all()

for pergunta in perguntas:
    print(f"id: {pergunta.id}, pergunta: {pergunta.pergunta}, dificuldade: {pergunta.dificuldade}")