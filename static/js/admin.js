window.onload = startup();

function toggleDarkMode() {
    var element = document.body;
    element.classList.toggle("dark-mode");
}

function logout() {
    window.location.href = "/logout";
}


function addItem(name, assignee) {
    fetch('/item', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: name, assignee: assignee})
    })
    .then(response => response.json())
    .then(data => {
        console.log('Item added:', data);
        getAdminInventory(); // Refresh the inventory list after adding an item
    })
    .catch(error => {
        console.error('Error adding item:', error);
    });
}

document.getElementById('addForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const name = document.getElementById('addItemName').value;
    const assignee = document.getElementById('addItemAssignee').value;
    // Call function to add item
    addItem(name, assignee);
});

function getAdminInventory() {
    fetch('/items')
    .then(response => response.json())
    .then(items => {
        const inventory = document.getElementById('inventory');
        inventory.innerHTML = ''; // Clear existing rows

        if (items.length === 0) {
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = 4;
            cell.textContent = 'No items in inventory.';
            row.appendChild(cell);
            inventory.appendChild(row);
        } else {
            items.forEach(item => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.id}</td>
                    <td>${item.name}</td>
                    <td>${item.assignee}</td>
                    <td>
                        <div class="button-container">
                            <button class="delete-button" onclick="deleteItem(${item.id})">Delete</button>
                            <button class="edit-button" onclick="editItem(${item.id})">Edit</button>
                        </div>
                    </td>
                    `;
                inventory.appendChild(row);
            });
        }
    })
    .catch(error => {
        console.error('Error fetching inventory:', error);
    });
}

function getRequests() {
    fetch('/requests')
        .then(response => response.json())
        .then(requests => {
            const requestTable = document.getElementById('request-table');
            requestTable.innerHTML = ''; // Clear existing rows

            if (requests.length === 0) {
                const row = document.createElement('tr');
                const cell = document.createElement('td');
                cell.colSpan = 5;  // adjust colspan accordingly
                cell.textContent = 'No requests found.';
                row.appendChild(cell);
                requestTable.appendChild(row);
            } else {
                requests.forEach(request => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${request.requestID}</td>
                        <td>${request.assignee}</td>
                        <td>${request.item_name}</td>
                        <td>${request.reason}</td>
                        <td>
                            <button class="reject-button" onclick="rejectRequest(${request.requestID})">Reject</button>
                            <button class="accept-button" onclick="acceptRequest(${request.requestID})">Accept</button>
                        </td>
                    `;
                    requestTable.appendChild(row);
                });
            }
        })
        .catch(error => {
            console.error('Error fetching requests:', error);
        });
}

function rejectRequest(requestID) {
    fetch('/rejectrequest', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ requestID: requestID })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        getRequests(); // Refresh the request table
    })
    .catch(error => {
        console.error('Error rejecting request:', error);
    });
}

function acceptRequest(requestID) {
    fetch('/acceptrequest', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ requestID: requestID })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        getRequests(); // Refresh the request table
        getAdminInventory()
    })
    .catch(error => {
        console.error('Error accepting request:', error);
    });
}



function deleteItem(id) {
  fetch('/item/' + id, { method: 'DELETE' })
    .then(() => {
        getAdminInventory();
    })
    .catch(() => alert('Error deleting item'));
}

function editItem(itemId) {
    window.location.href = `/edit/${itemId}`;
}

document.getElementById('deleteForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const id = document.getElementById('deleteItemId').value;
  if (id) {
    deleteItem(id);
  } else {
    alert('Please enter an ID');
  }
});

function startup() {
    getAdminInventory()
    getRequests()
}
