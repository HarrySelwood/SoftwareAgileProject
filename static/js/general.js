window.onload = getUserInventory; // Loads the user's inventory when the page is loaded

function toggleDarkMode() {
    var element = document.body;
    element.classList.toggle("dark-mode"); // Buton to toggle dark mode
}

function logout() {
    window.location.href = "/logout"; // Function to sign the user out
}

function getUserInventory() { // Function to display the user's inventory
    fetch('/userinventory')
    .then(response => response.json())
    .then(items => {
        const inventory = document.getElementById('user-inventory');
        inventory.innerHTML = ''; // Clear existing rows

        if (items.length === 0) { // If there are no items in the inventory, a message saying this is displayed
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = 3;
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
                    `;
                inventory.appendChild(row); // Adds the row to the table
            });
        }
    })
    .catch(error => {
        console.error('Error fetching inventory:', error); // Logs any errors that occur
    });
}

function raiseRequest(item, reason) { // Function to send a POST request to the server
    fetch('/raise_request_route', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json' // Specifies that the data is in JSON format
        },
        body: JSON.stringify({ item: item, reason: reason })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Request submitted:', data); // Logs the success notification
        alert(data.message); // Displays a popup to the user to let them know of the success
    })
    .catch(error => {
        console.error('Error submitting request:', error); // Handles errors that may occur
    });
}

document.getElementById('request-form').addEventListener('submit', function(e) { // Listens for when the form is submitted
    e.preventDefault(); // Prevents the default form submission result (refreshing the page)
    const item = document.getElementById('requestItem').value; // Gets the item name from the input field
    const reason = document.getElementById('requestReason').value; // Gets the reason from the input field
    raiseRequest(item, reason); // Calls the function to raise the request
});

