import bcrypt #used for hashing passwords
from flask import Flask, session, request, render_template, jsonify, redirect, url_for #imports any flask modules required
from models import add_item, get_items, update_item, delete_item, register_user, comparePass, isAdmin, raise_request, reject_request, accept_request, hash_password #imports all models from models.py that are used in this file
from db import get_db, close_db
import sqlite3 #used for database control

app = Flask(__name__)
app.secret_key = 'your-very-secret-key' #secret key used for sessions

app.teardown_appcontext(close_db)

@app.route('/')
def index():
    return render_template('index.html') #loads the first html template when the application is started

@app.route('/AdminDashboard')
def AdminDashboardRoute():
    return render_template('AdminDashboard.html') #loads the admin dashboard when the url is accessed

@app.route('/StandardDashboard')
def StandardDashboardRoute():
    return render_template('StandardDashboard.html') #loads the general user dashboard when the url is accessed

@app.route('/login', methods=['POST', 'GET'])
def login():
    username = request.form.get('username', '').strip() #gets the entered username from the form
    userPassword = request.form.get('password', '') #gets the entered password from the form
    if comparePass(username, userPassword): #compares the entered username and password to the stored credentials for that username
        session['username'] = username #sets the session (effectively is what 'signs in' the user)
        if isAdmin(username):
            return redirect(url_for('AdminDashboardRoute')) #if user is admin, the admin dashboard loads
        else:
            return redirect(url_for('StandardDashboardRoute'))#if user is not admin, the standard dashboard loads

    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    firstName = data.get('firstName', '').strip()
    lastName = data.get('lastName', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if ' ' in username or ' ' in password: #checks if there are spaces in the username or password
        return jsonify({"error": "Username and password must not contain spaces."}), 400

    if not all([firstName, lastName, username, password]): #checks if the user has filled in all fields
        return jsonify({"error": "All fields are required."}), 400

    try:
        register_user(firstName, lastName, username, hash_password(password)) #adds the credentials and user details to the 'users' table
    except sqlite3.IntegrityError: #error for if a username that already exists is being registered
        return jsonify({"error": "Username already exists."}), 400
    except Exception: #all other errors
        return jsonify({"error": "Registration failed due to server error."}), 500

    return jsonify({"message": "Registration successful!"}), 200

@app.route ('/logout')
def logoutRoute():
    session.clear() #removes the session (effectively signs out the user)
    return redirect(url_for('login'))

def init_db(): #functions required to create the initial database file, and creates the standard admin user used for testing.
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
            AdminPass = hash_password('AdminPass')
            db.execute('INSERT INTO users (firstname, lastname, username, userpassword, isAdmin) VALUES (?, ?, ?, ?, ?)', ('TestFirst', 'TestLast', 'Admin', AdminPass, True))
        db.commit()

@app.cli.command('initdb') #allows for "flask initdb" to be entered into the console in order to initialise the database outside of the running application
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
        return jsonify({'error': 'Assignee name and item name are required'}), 400 #check the user has fulfilled all fields

    db = get_db()
    user_exists = db.execute('SELECT 1 FROM users WHERE username = ?', (assignee,)).fetchone() #checks if the username entered is an existing user
    if not user_exists:
        return jsonify({'error': 'Assignee does not exist'}), 400

    add_item(item_name, assignee) #adds the item if all conditions are met
    return jsonify({'message': 'Item added successfully'}), 201


@app.route('/items', methods=['GET'])
def get_items_route():
    db = get_db()
    items = db.execute('SELECT * FROM inventory').fetchall()
    return jsonify([{'id': item['id'], 'name': item['item_name'], 'assignee': item['assignee']} for item in items]) #returns all items and all information about them

@app.route('/edit/<int:item_id>', methods=['GET']) #handles the gathering of data about an item the admin wants to edit
def edit_item_route(item_id):
    db = get_db()
    item = db.execute('SELECT * FROM inventory WHERE id = ?', (item_id,)).fetchone() #selects the information about the item that the admin is trying to edit
    if not item:
        return "Item not found", 404
    return render_template('AdminEdit.html', item=item) #loads the screen for editing the item

@app.route('/item/<int:item_id>', methods=['PUT']) #handles the actual editing of the item previously mentioned
def update_item_route(item_id):
    data = request.get_json()
    assignee = data['assignee']

    if not assignee:
        return jsonify ({'error':'Assignee is required'}), 400

    update_item(item_id, assignee) #calls the function to actually update the assignee
    return jsonify({'message': 'Item updated successfully'})


@app.route('/userinventory')
def userInventoryRoute():
    username = session.get('username') #pulls the username so the assets assigned to the user can be shown
    if not username:
        return redirect(url_for('login'))

    db = get_db()
    items = db.execute('SELECT * FROM inventory WHERE assignee = ?', (username,)).fetchall() #collects all items assigned to the user signed it
    return jsonify([{'id': item['id'], 'name': item['item_name'], 'assignee': item['assignee']} for item in items]) #pushes the items in order for them to be displayed in the table



@app.route('/item/<int:item_id>', methods=['DELETE'])
def delete_item_route(item_id):
    delete_item(item_id)
    return jsonify({'message': 'Item deleted successfully'}), 200

@app.route('/users', methods=['GET'])
def get_users_route():
    db = get_db()
    users = db.execute('SELECT * FROM users').fetchall() #collects all users
    return jsonify([dict(user) for user in users]) #pushes all users to be displayed (done from console)



@app.route('/requests', methods=['GET'])
def get_requests_route():
    db = get_db()
    requests = db.execute('SELECT * FROM requests').fetchall() #collects all requests
    return jsonify([dict(request) for request in requests]) #pushes all requests to be displyed in the admin dashboard

@app.route('/raise_request_route', methods=['POST'])
def raise_request_route():
    data = request.get_json()
    item = data.get('item', '').strip()
    reason = data.get('reason', '').strip()
    username = session['username']

    if not item or not reason:
        return jsonify({'error': 'Item and reason are required'}), 400

    raise_request(item, reason, username) #raises the request using the item name and reason entered into the table, and taking the username from the session.
    return jsonify({'message': 'Request raised successfully'}), 201

@app.route('/rejectrequest', methods=['DELETE'])
def reject_request_route():
    data = request.get_json()
    request_id = data.get('requestID')

    reject_request(request_id) #deletes the request from the requests table
    return jsonify({'message': 'Request Rejected'}), 200

@app.route('/acceptrequest', methods=['POST'])
def accept_request_route():
    data = request.get_json()
    request_id = data.get('requestID')

    if not request_id:
        return jsonify({'error': 'Missing request ID'}), 400

    try:
        accept_request(request_id) #adds the item with all correct informatino (item name, assignee) to the inventory, and removes the request from the requests table.
        return jsonify({'message': 'Request Accepted'}), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500



if __name__ == '__main__':
    app.run()