import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from models import db, Ordine, DettaglioOrdine, Prodotto, Cliente, Categoria

app = Flask(__name__)

# Configurazione del Database MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:nondimenticare@localhost/techshop_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Chiave segreta per rendere sicuri i cookie di sessione
app.secret_key = 'una_chiave_segreta_e_sicurissima'

# Inizializzazione del database
db.init_app(app)


# ==========================================
# ROTTE PER IL RESET DELLA SESSIONE
# ==========================================

@app.route('/reset-page')
def reset_page():
    return render_template('reset.html')

@app.route('/clear-session-now', methods=['POST'])
def clear_session_now():
    session.clear()
    return redirect(url_for('login'))


# ==========================================
# ROTTE PER L'INTERFACCIA GRAFICA (HTML)
# ==========================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cognome = request.form.get('cognome')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            nuovo_cliente = Cliente(nome=nome, cognome=cognome, email=email, password=password)
            db.session.add(nuovo_cliente)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return f"Errore durante la registrazione: {e}"

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        cliente = Cliente.query.filter_by(email=email).first()

        if cliente and cliente.password == password:
            session['user_id'] = cliente.id_cliente
            session['user_nome'] = cliente.nome
            # Reindirizza al catalogo prodotti appena loggati
            return redirect(url_for('prodotti'))
        else:
            return "<h1>Credenziali errate! Riprova.</h1>"

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/prodotti')
def prodotti():
    lista_prodotti = Prodotto.query.all()
    lista_categorie = Categoria.query.all()
    return render_template('prodotti.html', prodotti=lista_prodotti, categorie=lista_categorie)


# ==========================================
# ROTTA API PER IL CHECKOUT (JSON)
# ==========================================

@app.route('/checkout', methods=['POST'])
def checkout():
    id_cliente = session.get('user_id')
    if not id_cliente:
        return jsonify({"error": "Devi effettuare il login per procedere al checkout!"}), 401

    data = request.json
    carrello = data.get('carrello')

    if not carrello:
        return jsonify({"error": "Il carrello è vuoto!"}), 400

    try:
        nuovo_ordine = Ordine(id_cliente=id_cliente)
        db.session.add(nuovo_ordine)
        db.session.flush()

        for item in carrello:
            prodotto = Prodotto.query.get(item['id_prodotto'])
            
            if not prodotto or prodotto.quantita_disp < item['quantita']:
                db.session.rollback()
                return jsonify({"error": f"Prodotto {item['id_prodotto']} esaurito!"}), 400
            
            prodotto.quantita_disp -= item['quantita']
            
            dettaglio = DettaglioOrdine(
                id_ordine=nuovo_ordine.id_ordine,
                id_prodotto=prodotto.id_prodotto,
                quantita=item['quantita'],
                prezzo_unitario=prodotto.prezzo
            )
            db.session.add(dettaglio)

        db.session.commit()
        # CARATTERE CORRETTO QUI: nuovo_ordine.id_ordine
        return jsonify({"message": "Ordine creato con successo!", "id_ordine": nuovo_ordine.id_ordine}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Errore interno", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)