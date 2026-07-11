from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Categoria(db.Model):
    __tablename__ = 'categoria'
    id_categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descrizione = db.Column(db.Text)

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50), nullable=False)
    cognome = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    data_registrazione = db.Column(db.DateTime, default=datetime.utcnow)

class Prodotto(db.Model):
    __tablename__ = 'prodotto'  # Assicurati che corrisponda al nome della tabella nel DB
    id_prodotto = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descrizione = db.Column(db.Text)
    prezzo = db.Column(db.Float)
    quantita_disp = db.Column(db.Integer)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoria.id_categoria'))
    immagine = db.Column(db.String(255), nullable=True)

class Ordine(db.Model):
    __tablename__ = 'ordine'
    id_ordine = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data_ordine = db.Column(db.DateTime, default=datetime.utcnow)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id_cliente'))

class DettaglioOrdine(db.Model):
    __tablename__ = 'dettaglio_ordine'
    # Chiave primaria composta (entrambi primary_key=True)
    id_ordine = db.Column(db.Integer, db.ForeignKey('ordine.id_ordine'), primary_key=True)
    id_prodotto = db.Column(db.Integer, db.ForeignKey('prodotto.id_prodotto'), primary_key=True)
    quantita = db.Column(db.Integer, nullable=False)
    prezzo_unitario = db.Column(db.Numeric(10, 2), nullable=False)