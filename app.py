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

# products page route: joins products with orderdetails to calculate average price
@app.route('/products')
def products():
    search_query = request.args.get('search', '').strip()

    if search_query:
        # filter products matching user input while calculating aggregate price
        query = """
        SELECT
            p.product_id,
            p.product_name,
            p.category,
            ROUND(AVG(od.sales), 2) AS price
        FROM products p
        LEFT JOIN orderdetails od ON p.product_id = od.product_id
        WHERE p.product_name LIKE ?
        GROUP BY p.product_id, p.product_name, p.category;
        """
        product_list = query_db(query, ('%' + search_query + '%',))
    else:
        # return all products with calculated price if no search term is provided
        query = """
            SELECT
                p.product_id,
                p.product_name,
                p.category,
                ROUND(AVG(od.sales), 2) AS price
            FROM products p
            LEFT JOIN orderdetails od ON p.product_id = od.product_id
            GROUP BY p.product_id, p.product_name, p.category;    
        """
        product_list = query_db(query)
    return render_template('products.html', products=product_list)

# orders page route: joins orders with orders_details to calculate total order amount
@app.route('/orders')
def orders():
    query = """
        SELECT
            o.order_id,
            o.order_date,
            o.customer_id,
            ROUND(SUM(od.sales), 2) AS total_amount
        FROM orders o
        LEFT JOIN orderdetails od ON o.order_id = od.order_id
        GROUP BY o.order_id, o.order_date, o.customer_id;
    """
    orders_list = query_db(query)
    return render_template('orders.html', orders=orders_list)

# dynamic order details route, fetches itemised product list for a specific order ID
@app.route('/orders/<order_id>')
def order_details(order_id):
    # parameterised query to fetch order summary details safely
    order_query = """
        SELECT
            o.order_id,
            o.order_date,
            c.customer_name,
            c.segment
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_id = ?;
    """
    order = query_db(order_query, (order_id,), one=True)

    # boundary test: if order ID does not exist in the database, trigger 404
    if order is None:
        return render_template('404.html'), 404

    # query individual line items associated with this specific order
    items_query = """
        SELECT
            p.product_name,
            p.category,
            ROUND(od.sales, 2) AS line_sales
        FROM orderdetails od
        JOIN products p ON od.product_id = p.product_id
        WHERE od.order_id = ?;
    """
    items = query_db(items_query, (order_id,))

    return render_template('order_details.html', order=order, items = items)

# custom 404 error handler: catches invalid URLs and renders 404.html
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# custom 500 internal server error handler
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# run the local Flask development server in debug mode
if __name__ == '__main__':
    app.run(debug=True)