const API_URL = 'http://localhost:3000/api';

document.getElementById('register-form').addEventListener('submit', async (e) => {
    // Evitamos que la página se recargue de forma tradicional
    e.preventDefault();

    // Capturamos los valores del formulario
    const tipo = document.querySelector('select[name="tipo"]').value;
    const nombre = document.querySelector('input[name="nombre"]').value;
    const correo = document.querySelector('input[name="correo"]').value;

    if (!tipo) {
        alert('Por favor selecciona un tipo de cuenta.');
        return;
    }

    let endpoint = '';
    let bodyData = {};

    // Configuramos la ruta y los datos dependiendo de si es cliente o profesional
    if (tipo === 'cliente') {
        endpoint = `${API_URL}/usuarios/clientes`;
        bodyData = {
            nombre: nombre,
            email: correo
        };
    } else if (tipo === 'profesional') {
        endpoint = `${API_URL}/usuarios/profesionales`;
        bodyData = {
            email: correo,
            tarifaBase: 0 // Valor base requerido por el backend 
        };
    }

    try {
        // Enviamos los datos a la ruta correspondiente en el backend
        const respuesta = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(bodyData)
        });

        const resultado = await respuesta.json();

       if (respuesta.ok) {
            alert('¡Registro exitoso en la base de datos!');
            window.location.href = 'login.html';
        } else {
            // AQUÍ muestre el detalle técnico del error de la base de datos
            alert('Error: ' + (resultado.detalle || resultado.error));
        }

    } catch (error) {
        console.error('Error de red:', error);
        alert('No se pudo conectar con el servidor backend.');
    }
});