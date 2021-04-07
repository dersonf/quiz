from flask import render_template
from app import app


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', title='Erro 500')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title='Erro 404')