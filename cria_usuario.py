from app import db
from app.models import Usuarios
from getpass import getpass

username = input('Nome de usuário: ')
fullname = input('Nome completo: ')
senha = getpass(prompt='Senha: ')
confirmasenha = getpass(prompt='Repita a senha: ')

if senha != confirmasenha:
    print("As senhas são diferentes")
else:
    print('OK')