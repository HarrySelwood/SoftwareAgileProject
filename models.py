from db import get_db
import bcrypt

#ADMIN DASHBOARD MODELS

def add_item(name, assignee): #adds an item and all information provided into the inventory
    db = get_db()
    db.execute('INSERT INTO inventory (item_name, assignee) VALUES (?, ?)', (name, assignee))
    db.commit()

def get_items(): #pulls all items from the inventory into a list called result
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

def update_item(item_id, assignee): #updates the item with information provided
    db = get_db()
    db.execute('UPDATE inventory SET assignee = ? WHERE id = ?', (assignee, item_id))
    db.commit()


def delete_item(item_id): #deletes the item with the provided id
    db = get_db()
    db.execute('DELETE FROM inventory WHERE id = ?', (item_id,))
    db.commit()



#INDEX MODELS

def register_user(firstName, lastName, username, userPassword):
    db = get_db()
    db.execute('INSERT INTO users (firstname, lastname, username, userpassword, isAdmin) VALUES (?, ?, ?, ?, ?)', (firstName, lastName, username, userPassword, False)) #adds the user information into the users table, ensuring they are set to not be an admin
    db.commit()

def comparePass(username, userPassword):
    db = get_db()
    result = db.execute('SELECT userPassword FROM users WHERE username = ?', (username,)).fetchone()
    if not result:
        return False

    storedHash = result['userPassword'].encode('utf-8')
    user_bytes = userPassword.encode('utf-8')

    return bcrypt.checkpw(user_bytes, storedHash) #checks if the entered password matches the stored password, using the encoded input and the stored hash

def isAdmin(username):
    db = get_db()
    user = db.execute('SELECT isAdmin FROM users WHERE username = ?', (username,)).fetchone()
    return bool(user['isAdmin']) if user else False #returns whether the username entered is an admin account

def hash_password(plain_password): #function to hash an input with a new random salt each time, increasing security
    user_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(user_bytes, salt)
    return hashed.decode('utf-8')



#GENERAL DASHBOARD MODELS

def raise_request(item, reason, username):
    db = get_db()
    db.execute('INSERT INTO requests (item_name, reason, assignee) VALUES (?, ?, ?)', (item, reason, username)) #inserts the request into the request table
    db.commit()

def reject_request(requestID):
    db = get_db()
    db.execute('DELETE FROM requests WHERE requestID = ?', (requestID,)) #deletes the request from the request table
    db.commit()

def accept_request(requestID):
    db = get_db()

    request_data = db.execute('SELECT item_name, assignee FROM requests WHERE requestID = ?', (requestID,)).fetchone() #pulls the information relating to the entered request
    item_name = request_data['item_name'] #assigns the item name from the request
    assignee = request_data['assignee'] #assigns the assignee from the request

    db.execute('INSERT INTO inventory (item_name, assignee) VALUES (?, ?)', (item_name, assignee)) #adds the requested item to the inventory, assigned to the user who requested it

    db.execute('DELETE FROM requests WHERE requestID = ?', (requestID,)) #removes the request from the requests table
    db.commit()
    return True