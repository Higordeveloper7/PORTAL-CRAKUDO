from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "crakudo_super_seguro_2026"

UPLOAD_FOLDER = "static/uploads"
FILES_FOLDER = "static/files"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FILES_FOLDER, exist_ok=True)

def conectar():
    return sqlite3.connect("database.db")

def criar_db():
    conn = conectar()
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS usuarios (user TEXT, senha TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS posts (titulo TEXT, conteudo TEXT, categoria TEXT, imagem TEXT, arquivo TEXT, ativo INTEGER)")

    conn.commit()
    conn.close()

criar_db()

@app.route('/')
def home():
    return render_template('index.html', user=session.get('user'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/cadastro', methods=['GET','POST'])
def cadastro():
    if request.method == 'POST':
        user = request.form['user']
        senha = request.form['senha']

        conn = conectar()
        c = conn.cursor()
        c.execute("INSERT INTO usuarios VALUES (?,?)", (user, senha))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('cadastro.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form['user']
        senha = request.form['senha']

        conn = conectar()
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE user=? AND senha=?", (user, senha))
        result = c.fetchone()
        conn.close()

        if result:
            session['user'] = user
            return redirect('/')
        else:
            return "Login inválido"

    return render_template('login.html')

@app.route('/categoria/<cat>')
def categoria(cat):
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM posts WHERE categoria=? AND ativo=1", (cat,))
    posts = c.fetchall()
    conn.close()

    return render_template('posts.html', posts=posts, cat=cat)

@app.route('/add', methods=['POST'])
def add():
    if 'user' not in session:
        return redirect('/login')

    titulo = request.form['titulo']
    conteudo = request.form['conteudo']
    categoria = request.form['categoria']

    imagem = request.files['imagem']
    arquivo = request.files['arquivo']

    nome_imagem = ""
    nome_arquivo = ""

    if imagem and imagem.filename != "":
        caminho = os.path.join(UPLOAD_FOLDER, imagem.filename)
        imagem.save(caminho)
        nome_imagem = imagem.filename

    if arquivo and arquivo.filename != "":
        caminho = os.path.join(FILES_FOLDER, arquivo.filename)
        arquivo.save(caminho)
        nome_arquivo = arquivo.filename

    conn = conectar()
    c = conn.cursor()
    c.execute("INSERT INTO posts VALUES (?,?,?,?,?,1)", (titulo, conteudo, categoria, nome_imagem, nome_arquivo))
    conn.commit()
    conn.close()

    return redirect('/')

# 🔥 ADMIN
@app.route('/admin')
def admin():
    if session.get('user') != 'admin':
        return "Acesso negado"

    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT rowid, * FROM posts")
    posts = c.fetchall()

    c.execute("SELECT * FROM usuarios")
    users = c.fetchall()

    conn.close()

    return render_template('admin.html', posts=posts, users=users)

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('user') != 'admin':
        return "Acesso negado"

    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE rowid=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/admin')

@app.route('/bloquear/<int:id>')
def bloquear(id):
    if session.get('user') != 'admin':
        return "Acesso negado"

    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE posts SET ativo=0 WHERE rowid=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/admin')

@app.route('/desbloquear/<int:id>')
def desbloquear(id):
    if session.get('user') != 'admin':
        return "Acesso negado"

    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE posts SET ativo=1 WHERE rowid=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/admin')

@app.route('/delete_user/<user>')
def delete_user(user):
    if session.get('user') != 'admin':
        return "Acesso negado"

    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM usuarios WHERE user=?", (user,))
    conn.commit()
    conn.close()

    return redirect('/admin')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)