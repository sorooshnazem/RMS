from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key12345'  # Required for sessions

# --- Helper function ---
def get_orders():
    conn = sqlite3.connect('../main_app/instance/restaurant.db')  # adjust path if needed
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT 
        o.id_order_id,
        u.nm_phone_number,
        u.gn_surname AS gn_full_name,
        o.dt_order_date,
        o.gn_order_status_name
    FROM "order" o
    JOIN "User" u ON o.id_user_id = u.id_user_id
    ORDER BY o.dt_order_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

# --- Routes ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'owner' and password == 'securepass':
            session['admin_logged_in'] = True
            return redirect(url_for('view_orders'))
        else:
            error = 'Invalid credentials. Please try again.'
    return render_template('admin_login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/orders')
def view_orders():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    orders = get_orders()
    return render_template('admin_orders.html', orders=orders)

@app.route('/api/orders')
def api_orders():
    return jsonify(get_orders())

@app.route('/api/orders/<int:order_id>')
def api_order_detail(order_id):
    conn = sqlite3.connect('../main_app/instance/restaurant.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT f.gn_food_name, f.ds_food_descr, f.nm_price_number
        FROM order_detail o
        JOIN food f ON o.id_food_id = f.id_food_id
        WHERE o.id_order_id = ?
    """, (order_id,))
    
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if not items:
        return jsonify({'error': 'No items found for this order'}), 404

    return jsonify({'items': items})

@app.route('/api/orders/<int:order_id>/status', methods=['POST'])
def update_order_status(order_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        new_status = request.json.get('status')
    except:
        return jsonify({'error': 'Invalid JSON'}), 400

    if new_status not in ['Confirmed', 'Rejected']:
        return jsonify({'error': 'Invalid status'}), 400

    conn = sqlite3.connect('../main_app/instance/restaurant.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE 'order' SET gn_order_status_name = ? WHERE id_order_id = ?", (new_status, order_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(port=5001, debug=True)
