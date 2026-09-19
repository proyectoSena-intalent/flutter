document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // Evita que la página se recargue sola

            // Capturamos lo que el usuario escribió en los inputs
            const correo = document.getElementById('email').value;
            const contrasena = document.getElementById('password').value;

          try {
                // Hacemos la petición al backend enviando correo y email para asegurar que lo reciba
                const response = await fetch('http://localhost:3000/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ 
                        correo: correo, 
                        email: correo,      
                        contrasena: contrasena,
                        password: contrasena 
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // Guardamos el token que viene del backend antes de redirigir
                    if (data.token) {
                        localStorage.setItem('token', data.token);
                    }
                    
                    alert('¡Inicio de sesión exitoso!');
                    // Si todo sale bien, lo mandamos al dashboard
                    window.location.href = 'dashboard.html';
                } else {
                    // Si el servidor rechaza las credenciales, mostramos el error
                    alert('Error: ' + (data.error || 'Correo o contraseña incorrectos'));
                }
            } catch (error) {
                console.error('Error de conexión:', error);
                alert('No se pudo conectar con el servidor. Revisa que Node.js esté encendido.');
            }
        });
    }
});