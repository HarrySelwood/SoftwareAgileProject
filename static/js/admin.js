window.onload = startup(); // Calls a function that ensures that both the item inventory and requests are displayed when the page is loaded

function toggleDarkMode() {
    var element = document.body;
    element.classList.toggle("dark-mode"); // Button to toggle dark mode
}

function logout() {
    window.location.href = "/logout"; // Button to log out of the account
}


function addItem(name, assignee) {
    fetch('/item', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: name, assignee: assignee })
    })
    .then(async response => {
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Something went wrong');
        }
        alert(data.message); // Show success message
        getAdminInventory(); // Refresh list
    })
    .catch(error => {
        console.error('Error adding item:', error);
        alert(error.message); // Show readable error message to user
    });
}

document.getElementById('addForm').addEventListener('submit', function(e) { // Event listener added to the add item form
    e.preventDefault(); // Prevents the default form reaction, which is to reload the page
    const name = document.getElementById('addItemName').value; // Gets the item name from the input field
    const assignee = document.getElementById('addItemAssignee').value; // Gets the assignee from the input field
    addItem(name, assignee); // Call function to add item
});

function getAdminInventory() { // Function to fetch and display the entire inventory
    fetch('/items') // Sends a GET request to retrieve all data from the inventory
    .then(response => response.json())
    .then(items => {
        const inventory = document.getElementById('inventory');
        inventory.innerHTML = ''; // Clear existing rows

        if (items.length === 0) { // If there are no items in the inventory, a message saying this is displayed
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = 4;
            cell.textContent = 'No items in inventory.';
            row.appendChild(cell);
            inventory.appendChild(row);
        } else { // If items do exist, a new row is created for each item, with the ID, name, assignee, and a delete/edit button
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
                inventory.appendChild(row); // Adds the row to the table
            });
        }
    })
    .catch(error => {
        console.error('Error fetching inventory:', error); // Logs any errors that occur
    });
}

function getRequests() { // Function to fetch all requests and display them
    fetch('/requests') // Sends a GET request to the server to retrieve all requests
        .then(response => response.json())
        .then(requests => {
            const requestTable = document.getElementById('request-table');
            requestTable.innerHTML = ''; // Clear existing rows

            if (requests.length === 0) { // If there are no requests, a message is displayed saying this
                const row = document.createElement('tr');
                const cell = document.createElement('td');
                cell.colSpan = 5;
                cell.textContent = 'No requests found.';
                row.appendChild(cell);
                requestTable.appendChild(row);
            } else { // If there are requests, each one is given a new row in the table, with the ID, assignee, item name, reason, and an accept/reject button
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
                    requestTable.appendChild(row); // Adds the request to the table
                });
            }
        })
        .catch(error => {
            console.error('Error fetching requests:', error); // Handles any errors that occur
        });
}

function rejectRequest(requestID) { // Function to reject the request
    fetch('/rejectrequest', {
        method: 'DELETE', // Sends a DELETE request to the server
        headers: {
            'Content-Type': 'application/json' // Specifies that the data is in JSON format
        },
        body: JSON.stringify({ requestID: requestID })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message); // Logs the server's response
        getRequests(); // Refresh the request table
    })
    .catch(error => {
        console.error('Error rejecting request:', error); // Handles any errors that occur
    });
}

function acceptRequest(requestID) { // Function to accept the request
    fetch('/acceptrequest', {
        method: 'POST', // Sends a POST request to the server
        headers: {
            'Content-Type': 'application/json' // Specifies that the data is in JSON format
        },
        body: JSON.stringify({ requestID: requestID })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message); // Logs the server's response
        getRequests(); // Refresh the request table
        getAdminInventory() // Refreshes the inventory to show the newly accepted item
    })
    .catch(error => {
        console.error('Error accepting request:', error); // Handles any errors that occur
    });
}



function deleteItem(id) { // Function used to delete the item in the same row as the delete button
  fetch('/item/' + id, { method: 'DELETE' }) // DELETE request sent to the server with the item ID
    .then(() => {
        getAdminInventory(); // Refreshes the inventory after a successful deletion
    })
    .catch(() => alert('Error deleting item')); // Error if something goes wrong during the deletion
}


function editItem(itemId) { // Function to navigate to the edit page for the correct item
    window.location.href = `/edit/${itemId}`; // Redirects to the edit page
}



function startup() {
    getAdminInventory() // Loads the inventory of items
    getRequests() // Loads all of the requests
}
