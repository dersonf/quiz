from app import app, db
from app.models import Perguntas, Respostas, Usuarios


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Perguntas': Perguntas,
        'Respostas': Respostas,
        'Usuarios': Usuarios,
        }
