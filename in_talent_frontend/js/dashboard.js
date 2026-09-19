document.addEventListener('DOMContentLoaded', async () => {
    try {
        // 1. Recuperamos el token guardado en el login
        const token = localStorage.getItem('token');

        // 2. Hacemos el fetch enviando el token en los headers de autorización
        const respuestaSolicitudes = await fetch('http://localhost:3000/api/solicitudes', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!respuestaSolicitudes.ok) {
            throw new Error('No se autorizó la sesión o falló la petición');
        }

        const solicitudes = await respuestaSolicitudes.json();
        console.log("Solicitudes cargadas desde la base de datos:", solicitudes);

        // 3. Pintamos los datos en la tabla del HTML
        const tablaBody = document.getElementById('tabla-solicitudes');

        if (tablaBody && Array.isArray(solicitudes)) {
            tablaBody.innerHTML = ''; // Limpiamos la tabla estática de prueba

            solicitudes.forEach(solicitud => {
                const fila = document.createElement('tr');
                const otroUsuario = solicitud.email_profesional || solicitud.cliente_nombre || 'N/A';

                fila.innerHTML = `
                    <td>${solicitud.servicio || 'Sin servicio'}</td>
                    <td>${otroUsuario}</td>
                    <td>$0</td>
                    <td><span class="status-badge">${solicitud.estado || 'PENDIENTE'}</span></td>
                `;
                
                tablaBody.appendChild(fila);
            });
        }

    } catch (error) {
        console.error("Error al conectar con el backend:", error);
    }

    // 4. Lógica para que los botones del menú lateral respondan al hacer clic
    const navLinks = document.querySelectorAll('.sidebar-nav a:not(.logout-link)');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault(); // Evita que la página brinque

            // Quitamos la clase 'active' de todos y se la ponemos al presionado
            navLinks.forEach(item => item.classList.remove('active'));
            link.classList.add('active');

            console.log("Opción seleccionada:", link.textContent.trim());
        });
    });
});