import bcrypt
from flask import Flask, session, request, render_template, jsonify, redirect, url_for
from models import add_item, get_items, update_item, delete_item, register_user, comparePass, isAdmin, raise_request, reject_request, accept_request, hash_password
from db import get_db
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-very-secret-key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/AdminDashboard')
def AdminDashboardRoute():
    return render_template('AdminDashboard.html')

@app.route('/StandardDashboard')
def StandardDashboardRoute():
    return render_template('StandardDashboard.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    username = request.form.get('username', '').strip()
    userPassword = request.form.get('password', '')
    if comparePass(username, userPassword):
        session['username'] = username
        if isAdmin(username):
            return redirect(url_for('AdminDashboardRoute'))
        else:
            return redirect(url_for('StandardDashboardRoute'))

    return render_template('index.html')
    

@app.route('/register', methods=['POST', 'GET'])
def register():
    firstName = request.form.get('firstName', '').strip()
    lastName = request.form.get('lastName', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if firstName and lastName and username and password:
        try:
            user_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(user_bytes,salt)
            hashed_str = hashed.decode('utf-8')
            register_user(firstName, lastName, username, hashed_str)
        except Exception:
            pass  # silently ignore errors

    # Always redirect to login page, no messages passed
    return redirect(url_for('login'))

@app.route ('/logout')
def logoutRoute():
    session.clear()
    return redirect(url_for('login'))

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
            AdminPass = hash_password('AdminPass')
            db.execute('INSERT INTO users (firstname, lastname, username, userpassword, isAdmin) VALUES (?, ?, ?, ?, ?)', ('TestFirst', 'TestLast', 'Admin', AdminPass, True))
        db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.shell_context_processor
def make_shell_context():
    return {'add_item': add_item, 'get_items': get_items, 'update_item': update_item, 'delete_item': delete_item}

@app.route('/item', methods=['POST'])
def add_item_route():
    data = request.get_json()
    item_name = data.get('name', '').strip()
    assignee = data.get('assignee', '').strip()

    if not assignee or not item_name:
        return jsonify({'error': 'Assignee name and item name are required'}), 400
    if not all(part.isalnum() for part in assignee.split()):
        return jsonify({'error': 'Assignee name must contain only letters and spaces'}), 400

    db = get_db()
    user_exists = db.execute('SELECT 1 FROM users WHERE username = ?', (assignee,)).fetchone()
    if not user_exists:
        return jsonify({'error': 'Assignee does not exist'}), 400

    add_item(item_name, assignee)
    return jsonify({'message': 'Item added successfully'}), 201


@app.route('/items', methods=['GET'])
def get_items_route():
    db = get_db()
    items = db.execute('SELECT * FROM inventory').fetchall()
    return jsonify([{'id': item['id'], 'name': item['item_name'], 'assignee': item['assignee']} for item in items])

@app.route('/edit/<int:item_id>', methods=['GET'])
def edit_item_route(item_id):
    db = get_db()
    item = db.execute('SELECT * FROM inventory WHERE id = ?', (item_id,)).fetchone()
    if not item:
        return "Item not found", 404
    return render_template('AdminEdit.html', item=item)


@app.route('/userinventory')
def userInventoryRoute():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    
    db = get_db()
    items = db.execute('SELECT * FROM inventory WHERE assignee = ?', (username,)).fetchall()
    return jsonify([{'id': item['id'], 'name': item['item_name'], 'assignee': item['assignee']} for item in items])



@app.route('/item/<int:item_id>', methods=['PUT'])
def update_item_route(item_id):
    data = request.get_json()
    assignee = data['assignee']
    db = get_db()
    db.execute('UPDATE inventory SET assignee = ? WHERE id = ?', (assignee, item_id))
    db.commit()
    return jsonify({'message': 'Item updated successfully'})
 
@app.route('/item/<int:item_id>', methods=['DELETE'])
def delete_item_route(item_id):
    db = get_db()
    db.execute('DELETE FROM inventory WHERE id = ?', (item_id,))
    db.commit()
    return jsonify({'message': 'Item deleted successfully'}), 200

@app.route('/users', methods=['GET'])
def get_users_route():
    db = get_db()
    users = db.execute('SELECT * FROM users').fetchall()
    return jsonify([dict(user) for user in users])

@app.route('/credentials', methods=['GET'])
def get_credentials_route():
    db = get_db()
    creds = db.execute('SELECT * FROM credentials').fetchall()
    return jsonify([dict(cred) for cred in creds])



@app.route('/requests', methods=['GET'])
def get_requests_route():
    db = get_db()
    requests = db.execute('SELECT * FROM requests').fetchall()
    return jsonify([dict(request) for request in requests])

@app.route('/raise_request_route', methods=['POST'])
def raise_request_route():
    data = request.get_json()
    item = data.get('item', '').strip()
    reason = data.get('reason', '').strip()
    username = session['username']

    if not item or not reason:
        return jsonify({'error': 'Item and reason are required'}), 400

    raise_request(item, reason, username)
    return jsonify({'message': 'Request raised successfully'}), 201

@app.route('/rejectrequest', methods=['DELETE'])
def reject_request_route():
    data = request.get_json()
    request_id = data.get('requestID')

    reject_request(request_id)
    return jsonify({'message': 'Request Rejected'}), 200

@app.route('/acceptrequest', methods=['POST'])
def accept_request_route():
    data = request.get_json()
    request_id = data.get('requestID')

    success = accept_request(request_id)
    if success:
        return jsonify({'message': 'Request Accepted'}), 200
    else:
        return jsonify({'error': 'Request not found'}), 404


if __name__ == '__main__':
    app.run()