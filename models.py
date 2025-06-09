from db import get_db
import bcrypt

def add_item(name, assignee): 
    db = get_db()
    db.execute('INSERT INTO inventory (item_name, assignee) VALUES (?, ?)', (name, assignee)) 
    db.commit()

def get_items():
    db = get_db()
    items = db.execute('SELECT * FROM inventory').fetchall()
    result = []
    for item in items:
        result.append({
            'id': item['id'],
            'name': item['item_name'],
            'assignee': item['assignee']
        })
    return result

def update_item(item_id, assignee): 
    db = get_db() 
    db.execute('UPDATE inventory SET assignee = ? WHERE id = ?', (assignee, item_id)) 
    db.commit()

def delete_item(item_id): 
    db = get_db() 
    db.execute('DELETE FROM inventory WHERE id = ?', (item_id,)) 
    db.commit()




def register_user(firstName, lastName, username, userPassword):
    db = get_db()
    db.execute('INSERT INTO users (firstname, lastname, username, userpassword, isAdmin) VALUES (?, ?, ?, ?, ?)', (firstName, lastName, username, userPassword, False))
    db.commit()

def comparePass(username, userPassword):
    db = get_db()
    result = db.execute('SELECT userPassword FROM users WHERE username = ?', (username,)).fetchone()
    if not result:
        return False
    
    storedHash = result['userPassword'].encode('utf-8')
    user_bytes = userPassword.encode('utf-8')

    return bcrypt.checkpw(user_bytes, storedHash)

def isAdmin(username):
    db = get_db()
    user = db.execute('SELECT isAdmin FROM users WHERE username = ?', (username,)).fetchone()
    return bool(user['isAdmin']) if user else False

def hash_password(plain_password):
    user_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(user_bytes, salt)
    return hashed.decode('utf-8')




def raise_request(item, reason, username):
    db = get_db()
    db.execute('INSERT INTO requests (item_name, reason, assignee) VALUES (?, ?, ?)', (item, reason, username))
    db.commit()

def reject_request(requestID):
    db = get_db()
    db.execute('DELETE FROM requests WHERE requestID = ?', (requestID,))
    db.commit()

def accept_request(requestID):
    db = get_db()

    request_data = db.execute('SELECT item_name, assignee FROM requests WHERE requestID = ?', (requestID,)).fetchone()
    item_name = request_data['item_name']
    assignee = request_data['assignee']

    db.execute('INSERT INTO inventory (item_name, assignee) VALUES (?, ?)', (item_name, assignee))

    db.execute('DELETE FROM requests WHERE requestID = ?', (requestID,))
    db.commit()
    return True