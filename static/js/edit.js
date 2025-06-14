function toggleDarkMode() {
    var element = document.body;
    element.classList.toggle("dark-mode"); // Button to toggle dark mode
}

function logout() {
    window.location.href = "/logout"; // Button to sign out the user
}

document.addEventListener('DOMContentLoaded', () => { // Waits for html content to be loaded before interacting with
    const form = document.getElementById('editForm'); // Assigns the edit form to 'form' to be used later

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevents the default form submission behaviour (page being refreshed)

        const itemId = document.getElementById('itemId').value; // Get the item ID from the hidden field
        const assignee = document.getElementById('assigneeInput').value; // Get the new assignee from the input field

        fetch(`/item/${itemId}`, {
            method: 'PUT', // PUT request sent to the server to update an existing item
            headers: {
                'Content-Type': 'application/json' // Specifies that the data is in JSON format
            },
            body: JSON.stringify({ assignee: assignee })
        })
        .then(res => res.json())
        .then(data => {
            alert(data.message); // Sends a user friendly popup showing the server's message
            console.log("Item ID:", itemId); // Logs the item ID to the console
            console.log("Assignee:", assignee); // Logs the new assignee to the console
            window.location.href = '/AdminDashboard'; // Redirects the user back to the admin dashboard after they have submitted the edit
        })
        .catch(error => console.error('Error updating item:', error)); // Handles any errors that occur
    });
});