function toggleDarkMode() {
    var element = document.body;
    element.classList.toggle("dark-mode");
}

function registerUser(firstName, lastName, username, password) {
    fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ firstName, lastName, username, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.message) alert(data.message)
        else if (data.error) alert(data.error)
    })
    .catch(() => alert('Network error'))
}

document.getElementById('registerForm').addEventListener('submit', function(e) {
  e.preventDefault();  // VERY IMPORTANT to prevent normal form submission

  const firstName = document.getElementById('firstName').value.trim();
  const lastName = document.getElementById('lastName').value.trim();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;

  fetch('/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ firstName, lastName, username, password })
  })
  .then(response => response.json())
  .then(data => {
    alert(data.message || 'Registered successfully!');
  })
  .catch(error => {
    alert('Registration failed');
    console.error(error);
  });
});