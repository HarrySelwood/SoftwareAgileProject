window.onload = getUserInventory;

function toggleDarkMode() {
    var element = document.body;
    element.classList.toggle("dark-mode");
}

function logout() {
    window.location.href = "/logout";
}

function getUserInventory() {
    fetch('/userinventory')
    .then(response => response.json())
    .then(items => {
        const inventory = document.getElementById('user-inventory');
        inventory.innerHTML = ''; // Clear existing rows

        if (items.length === 0) {
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = 3;
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
                    `;
                inventory.appendChild(row);
            });
        }
    })
    .catch(error => {
        console.error('Error fetching inventory:', error);
    });
}

function raiseRequest(item, reason) {
    fetch('/raise_request_route', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ item: item, reason: reason })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Request submitted:', data);
        // Optionally, refresh the request table or show a confirmation message
    })
    .catch(error => {
        console.error('Error submitting request:', error);
    });
}

document.getElementById('request-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const item = document.getElementById('requestItem').value;
    const reason = document.getElementById('requestReason').value;
    raiseRequest(item, reason);
});

