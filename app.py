import sqlite3
from flask import Flask, render_template, request, g

# initialise the Flask application
app = Flask(__name__)

# define the database filename constant
DATABASE = 'retail_orders.db'

# helper function to open and manage a single databse connection per request
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# home page route: fetches all products from SQLite and renders index.html
@app.route('/')
def home():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    return render_template('index.html', items=products)

# products page route: fetches and displays all products
@app.route('/products')
def products():
    search_query = request.args.get('search', '').strip()
    db = get_db()
    cursor = db.cursor()

    if search_query:
        # search for products matching user's input
        cursor.execute('SELECT * FROM products WHERE product_name LIKE ?', ('%' + search_query + '%',))
    else:
        # return all products if no search term is provided
        cursor.execute('SELECT * FROM products')

    product_list = cursor.fetchall()
    return render_template('products.html', products=product_list, search_query=search_query)

@app.route('/orders')
def orders():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM orders')
    orders_list = cursor.fetchall()
    return render_template('orders.html', orders=orders_list)

# custom 404 error handler: catches invalid URLs and renders 404.html
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# run the local Flask development server in debug mode
if __name__ == '__main__':
    app.run(debug=True)