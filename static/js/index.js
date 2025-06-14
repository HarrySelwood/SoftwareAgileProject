function toggleDarkMode() {
    var element = document.body;
    element.classList.toggle("dark-mode"); // Button to toggle the dark mode
}

function registerUser(firstName, lastName, username, password) { // Function to add a new user into the users table in the database
  fetch('/register', { // Sends a POST request to the server
    method: 'POST',
    headers: {'Content-Type': 'application/json'}, // Specifies that the data is in JSON format
    body: JSON.stringify({ firstName, lastName, username, password })
  })
  .then(response => {
    if (!response.ok) { // If the response is not OK, an error is thrown
        return response.json().then(err => {
        throw new Error(err.error || 'Registration failed');
      });
    }
    return response.json();
  })
    .then(data => {
    alert(data.message || 'Registered successfully!'); // Display a popup with a success message
  })
    .catch(err => {
    alert(err.message); // Shows any errors that have occured
  });
}

document.getElementById('registerForm').addEventListener('submit', function(e) { // Adds a listener to the forms submission
    e.preventDefault();

    // Collect data from input fields
    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    registerUser(firstName, lastName, username, password) // Calls the function to register the user
});