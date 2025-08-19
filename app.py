import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")

DB_FILE = "leads.db"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# --- Função para conectar banco ---
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Criar tabela se não existir ---
def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT,
            whatsapp TEXT,
            etapa TEXT,
            data TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Rota: Landing Page ---
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        whatsapp = request.form.get("whatsapp")

        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO leads (nome, email, whatsapp, etapa, data) VALUES (?, ?, ?, ?, ?)",
                  (nome, email, whatsapp, "novo", datetime.now().isoformat()))
        conn.commit()
        conn.close()

        return redirect(url_for("obrigado"))
    return render_template("index.html")

# --- Rota: Página de Obrigado ---
@app.route("/obrigado")
def obrigado():
    return render_template("obrigado.html")

# --- Rota: Política de Privacidade ---
@app.route("/privacidade")
def privacidade():
    return render_template("privacidade.html")

# --- Rota: Admin (painel de funil) ---
@app.route("/admin")
def admin():
    # Login simples via ?key=senha
    if "auth" not in session:
        key = request.args.get("key")
        if key == ADMIN_PASSWORD:
            session["auth"] = True
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=6)
        else:
            return "Acesso negado. Use ?key=SENHA"

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM leads ORDER BY id DESC")
    leads = c.fetchall()
    conn.close()

    return render_template("admin.html", leads=leads)

# --- Rota: mudar etapa ---
@app.route("/mudar/<int:lead_id>/<etapa>")
def mudar(lead_id, etapa):
    if "auth" not in session:
        return "Não autorizado"
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE leads SET etapa=? WHERE id=?", (etapa, lead_id))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)
