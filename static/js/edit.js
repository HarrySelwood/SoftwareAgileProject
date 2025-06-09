function toggleDarkMode() {
    var element = document.body;
    element.classList.toggle("dark-mode");
}

function logout() {
    window.location.href = "/logout";
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('editForm');

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const itemId = document.getElementById('itemId').value;
        const assignee = document.getElementById('assigneeInput').value;

        fetch(`/item/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ assignee: assignee })
        })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            console.log("Item ID:", itemId);
            console.log("Assignee:", assignee);
            window.location.href = '/AdminDashboard';
        })
        .catch(error => console.error('Error updating item:', error));
    });
});