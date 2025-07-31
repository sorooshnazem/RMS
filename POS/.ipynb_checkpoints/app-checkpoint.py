from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key123456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------- Models ----------
class User(db.Model):
    __tablename__ = 'user'
    id_user_id = db.Column(db.Integer, primary_key=True)
    gn_surname = db.Column(db.String(100), nullable=False)
    nm_phone_number = db.Column(db.String(15), nullable=False)

class Food(db.Model):
    __tablename__ = 'food'
    id_food_id = db.Column(db.Integer, primary_key=True)
    gn_food_name = db.Column(db.Text, nullable=False)
    id_food_category_id = db.Column(db.Integer, nullable=False)
    nm_price_number = db.Column(db.Float, nullable=False)
    ds_food_descr = db.Column(db.Text, nullable=False)
    id_restaurant_id = db.Column(db.Integer, nullable=False)

class Order(db.Model):
    __tablename__ = 'order'
    id_order_id = db.Column(db.Integer, primary_key=True)
    ds_order_descr = db.Column(db.Text)
    dt_order_date = db.Column(db.Text, nullable=False)
    dt_total_price_date = db.Column(db.Float, nullable=False)
    id_user_id = db.Column(db.Integer, nullable=False)
    gn_order_status_name = db.Column(db.Text, nullable=False)

class OrderDetail(db.Model):
    __tablename__ = 'order_detail'
    id_order_id = db.Column(db.Integer, db.ForeignKey('order.id_order_id'), primary_key=True)
    id_food_id = db.Column(db.Integer, db.ForeignKey('food.id_food_id'), primary_key=True)
    nm_food_ordered_number = db.Column(db.Integer, nullable=False)
    ds_note_descr = db.Column(db.Text)


# ---------- Routes ----------

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/menu')
def menu():
    try:
        foods = Food.query.all()
    except Exception as e:
        foods = []
        print("Error querying foods:", e)
    return render_template('menu.html', foods=foods, admin=session.get('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session['admin'] = True
            return redirect(url_for('menu'))
        else:
            error = 'Invalid credentials'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/add', methods=['GET', 'POST'])
def add_food():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            new_food = Food(
                gn_food_name=request.form['name'],
                id_food_category_id=1,
                nm_price_number=float(request.form['price']),
                ds_food_descr=request.form['desc'],
                id_restaurant_id=1
            )
            db.session.add(new_food)
            db.session.commit()
            return redirect(url_for('menu'))
        except Exception as e:
            return f"Error adding food: {e}"

    return '''
        <h2>Add Food Item</h2>
        <form method="POST">
            Name: <input type="text" name="name"><br>
            Description: <input type="text" name="desc"><br>
            Price: <input type="number" name="price" step="0.01"><br>
            <input type="submit" value="Add">
        </form>
    '''

@app.route('/edit/<int:food_id>', methods=['GET', 'POST'])
def edit_food(food_id):
    if not session.get('admin'):
        return redirect(url_for('login'))

    food = Food.query.get_or_404(food_id)

    if request.method == 'POST':
        try:
            food.gn_food_name = request.form['name']
            food.ds_food_descr = request.form['desc']
            food.nm_price_number = float(request.form['price'])
            db.session.commit()
            return redirect(url_for('menu'))
        except Exception as e:
            return f"Error editing food: {e}"

    return f'''
        <h2>Edit Food Item</h2>
        <form method="POST">
            Name: <input type="text" name="name" value="{food.gn_food_name}"><br>
            Description: <input type="text" name="desc" value="{food.ds_food_descr}"><br>
            Price: <input type="number" name="price" value="{food.nm_price_number}" step="0.01"><br>
            <input type="submit" value="Update">
        </form>
    '''

@app.route('/delete/<int:food_id>')
def delete_food(food_id):
    if not session.get('admin'):
        return redirect(url_for('login'))

    food = Food.query.get_or_404(food_id)
    db.session.delete(food)
    db.session.commit()
    return redirect(url_for('menu'))


@app.route('/order', methods=['GET', 'POST'])
def order():
    foods = Food.query.all()

    if request.method == 'POST':
        # Get user info
        full_name = (request.form.get('full_name') or '').strip()
        phone = (request.form.get('phone_number') or '').strip()

        if not full_name or not phone:
            flash('Full name and phone number are required.', 'error')
            return redirect(url_for('order'))

        # Create user ID from name and phone
        user_id = abs(hash(full_name + phone)) % (10 ** 8)

        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            user = User(id_user_id=user_id, gn_surname=full_name, nm_phone_number=phone)
            db.session.add(user)

        # Build food order list
        ordered_items = []
        total_price = 0

        for key, value in request.form.items():
            print(f"FORM INPUT: {key} = {value}")
            if key.startswith('quantity_') and value.strip():
                try:
                    food_id = int(key.split('_')[1])
                    quantity = int(value)
                    if quantity > 0:
                        food = Food.query.get(food_id)
                        if food:
                            note_key = f'note_{food_id}'
                            note = request.form.get(note_key, '').strip()
                            
                            subtotal = food.nm_price_number * quantity
                            ordered_items.append({
                                'name': food.gn_food_name,
                                'quantity': quantity,
                                'price': food.nm_price_number,
                                'subtotal': subtotal,
                                'note': note
                            })
                            total_price += subtotal
                except ValueError:
                    continue

        if not ordered_items:
            flash('No food items were selected.', 'error')
            return redirect(url_for('order'))

        # Create and save order
        new_order = Order(
            ds_order_descr=f'Order for {full_name}',
            dt_order_date=datetime.now(),
            dt_total_price_date=total_price,
            id_user_id=user_id,
            gn_order_status_name='Pending'
        )
        db.session.add(new_order)
        db.session.commit()

        # Add to order_detail
        for item in ordered_items:
            food = Food.query.filter_by(gn_food_name=item['name']).first()
            order_detail = OrderDetail(
                id_order_id=new_order.id_order_id,
                id_food_id=food.id_food_id,
                nm_food_ordered_number=item['quantity'],
                ds_note_descr=item.get('note') or 'TEST NOTE'
            )
            db.session.add(order_detail)

        db.session.commit()

        # Pass summary to confirmation page
        return render_template('order_confirmation.html', name=full_name, phone=phone, items=ordered_items, total=total_price)

    return render_template('order.html', foods=foods)


# --- Only for First Run ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

