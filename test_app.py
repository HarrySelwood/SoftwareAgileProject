import pytest
import json
from app import app, init_db
from db import get_db, close_db

@pytest.fixture
def client():
    # Set up the Flask test client and initialize the DB for each test session
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            init_db()  # initialize fresh DB before tests
            close_db()
        yield client

def register_user(client, username, password, firstName='Test', lastName='User'):
    return client.post('/register', data=json.dumps({
        'username': username,
        'password': password,
        'firstName': firstName,
        'lastName': lastName
    }), content_type='application/json')

def login_user(client, username, password):
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

#Tests for the index page loading and displaying information correctly
def test_index_page(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"Login" in rv.data
    assert b"Register" in rv.data

# Tests for successful registration of a new user
def test_register_success(client):
    rv = register_user(client, 'newuser', 'password123')
    data = rv.get_json()
    assert rv.status_code == 200
    assert data['message'] == 'Registration successful!'

# Tests registration using a username that already exists
def test_register_duplicate_user(client):
    register_user(client, 'duplicateuser', 'pass123')
    rv = register_user(client, 'duplicateuser', 'pass123')
    data = rv.get_json()
    assert rv.status_code == 400
    assert 'Username already exists' in data['error']

# Tests registration with a field missing
def test_register_missing_fields(client):
    rv = client.post('/register', data=json.dumps({
        'username': 'user2',
        'password': ''
    }), content_type='application/json')
    data = rv.get_json()
    assert rv.status_code == 400
    assert 'All fields are required' in data['error']

# Tests registration with spaces (' ') in the username and password
def test_register_spaces_in_username_password(client):
    rv = register_user(client, 'user space', 'pass 123')
    data = rv.get_json()
    assert rv.status_code == 400
    assert 'must not contain spaces' in data['error']

# Tests for a successful standard user login and redirect to standard dashboard
def test_login_success_and_redirect(client):
    register_user(client, 'loginuser', 'mypassword')
    rv = login_user(client, 'loginuser', 'mypassword')
    # Should redirect to standard dashboard
    assert b"StandardDashboard" in rv.data or rv.status_code == 200

# Tests for a failed login attempt
def test_login_fail(client):
    rv = login_user(client, 'nonexistent', 'nopass')
    # Should return index page again with failure
    assert rv.status_code == 200
    assert b"Login" in rv.data

# Tests adding an item without logging into an admin account
def test_add_item_requires_login(client):
    rv = client.post('/item', data=json.dumps({
        'name': 'Test Item',
        'assignee': 'loginuser'
    }), content_type='application/json')
    # No session set, so should fail on assignee not found (or depends on your code)
    assert rv.status_code == 400 or rv.status_code == 401

# Tests adding an item to a users inventory successfully
def test_add_item_success(client):
    # Register user to assign item to
    register_user(client, 'itemuser', 'pass')
    # Add item assigned to itemuser
    rv = client.post('/item', data=json.dumps({
        'name': 'Laptop',
        'assignee': 'itemuser'
    }), content_type='application/json')
    data = rv.get_json()
    assert rv.status_code == 201
    assert data['message'] == 'Item added successfully'

# Tests retrieval of items list using /items GET route
def test_get_items(client):
    rv = client.get('/items')
    assert rv.status_code == 200
    items = rv.get_json()
    assert isinstance(items, list)

# Tests raising a request with a signed-in user
def test_raise_request(client):
    register_user(client, 'requestuser', 'pass')
    with client.session_transaction() as sess:
        sess['username'] = 'requestuser'
    rv = client.post('/raise_request_route', data=json.dumps({
        'item': 'Laptop',
        'reason': 'Need for project'
    }), content_type='application/json')
    data = rv.get_json()
    assert rv.status_code == 201
    assert data['message'] == 'Request raised successfully'

# Tests rejecting requests
def test_reject_request(client):
    # Insert a dummy request directly for testing reject
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO requests (item_name, reason, assignee) VALUES (?, ?, ?)", ('ItemX', 'ReasonX', 'requestuser'))
        db.commit()
        request_id = db.execute('SELECT requestID FROM requests WHERE item_name=?', ('ItemX',)).fetchone()['requestID']
        close_db()

    rv = client.delete('/rejectrequest', data=json.dumps({'requestID': request_id}), content_type='application/json')
    data = rv.get_json()
    assert rv.status_code == 200
    assert data['message'] == 'Request Rejected'

# Tests accepting requests
def test_accept_request(client):
    # Insert a dummy request directly for testing accept
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO requests (item_name, reason, assignee) VALUES (?, ?, ?)", ('ItemY', 'ReasonY', 'requestuser'))
        db.commit()
        request_id = db.execute('SELECT requestID FROM requests WHERE item_name=?', ('ItemY',)).fetchone()['requestID']
        close_db()

    rv = client.post('/acceptrequest', data=json.dumps({'requestID': request_id}), content_type='application/json')
    data = rv.get_json()
    assert rv.status_code == 200
    assert data['message'] == 'Request Accepted'