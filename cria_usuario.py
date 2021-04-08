from app import db
from app.models import Usuarios
from getpass import getpass

username = input('Nome de usuário: ')
fullname = input('Nome completo: ')
senha = getpass(prompt='Senha: ')
confirmasenha = getpass(prompt='Repita a senha: ')

if senha != confirmasenha:
    print("As senhas são diferentes!")
else:
    usuario = Usuarios(username=username, fullname=fullname)
    usuario.define_senha(password=senha)
    db.session.add(usuario)
    db.session.commit()
    print(f"Usuário {username} criado com sucesso!")