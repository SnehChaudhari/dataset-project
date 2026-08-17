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

# helper function to query the database cleanly across all routes
def query_db(query, args=(), one=False):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, args)
    results = cursor.fetchall()
    return (results[0] if results else None) if one else results

# home page route: fetches all products from SQLite and renders index.html
@app.route('/')
def home():
    items = query_db('SELECT * FROM products LIMIT 10')
    return render_template('index.html', items=items)

# products page route: fetches and displays all products
@app.route('/products')
def products():
    search_query = request.args.get('search', '').strip()

    if search_query:
        # search for products matching user's input
        product_list = query_db('SELECT * FROM products WHERE product_name LIKE ?', ('%' + search_query + '%',))
    else:
        # return all products if no search term is provided
        product_list=query_db('SELECT * FROM products')

    return render_template('products.html', products=product_list, search_query=search_query)

# intentionally broken code to trigger 505 error
@app.route('/orders')
def orders():
    orders_list = query_db('SELECT * FROM non_existent_table')
    return render_template('orders.html', orders=orders_list)

# custom 404 error handler: catches invalid URLs and renders 404.html
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# custom 500 internal server error handler
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# turn off debug mode to make 500 error page functional
if __name__ == '__main__':
    app.run(debug=False)