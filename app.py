import sqlite3
from flask import Flask, render_template, g

app = Flask(__name__)

DATABASE = 'retail_orders.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.route('/')
def home():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    return render_template('index.html', items=products)

if __name__ == '__main__':
    app.run(debug=True)