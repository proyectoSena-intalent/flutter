// js/app.js

// Esta es la dirección base del servidor 
const API_URL = 'http://localhost:3000/api';

// Función asíncrona para traer los servicios 
async function cargarServicios() {
    try {
        const respuesta = await fetch(`${API_URL}/servicios`);
        const servicios = await respuesta.json();
        
        // Buscamos el contenedor. Cambia '.grid' por el ID o clase real de tu HTML si es diferente
        const contenedorGrid = document.querySelector('.grid') || document.getElementById('lista-servicios');
        
        if (!contenedorGrid) return;

        contenedorGrid.innerHTML = '';
        
        servicios.forEach(servicio => {
            // Nota: usamos 'descripcion' y 'tarifaPromedio' que vienen directos de tu backend en MySQL
            const tarjetaHTML = `
                <div class="card">
                    <span class="badge">${servicio.categoria || 'General'}</span>
                    <h3>${servicio.descripcion || 'Servicio Profesional'}</h3>
                    <p>Servicio calificado para el hogar</p>
                    <div class="price">Tarifa: $${servicio.tarifaPromedio || 'Por cotizar'}</div>
                    <a href="login.html" class="btn-card">Solicitar Servicio</a>
                </div>
            `;
            
            contenedorGrid.innerHTML += tarjetaHTML;
        });

    } catch (error) {
        console.error('Error al conectar con el backend:', error);
        const contenedorGrid = document.querySelector('.grid') || document.getElementById('lista-servicios');
        if (contenedorGrid) {
            contenedorGrid.innerHTML = '<p style="color: red; grid-column: 1 / -1; text-align: center;">Error al cargar los servicios. Verifica que el servidor backend esté corriendo en el puerto 3000.</p>';
        }
    }
}

// Ejecutamos al cargar la página
document.addEventListener('DOMContentLoaded', cargarServicios);

//chat//
function toggleChat() {
  const chatContainer = document.getElementById('chatContainer');
  chatContainer.classList.toggle('active');
}

function sendMessage() {
  const input = document.getElementById('userInput');
  const text = input.value.trim();
  if (!text) return;

  // 1. Mostrar mensaje del usuario
  appendMsg(text, 'user');
  input.value = '';

  // 2. Generar respuesta del bot basada en palabras clave
  setTimeout(() => {
    const botResponse = getBotResponse(text);
    appendMsg(botResponse, 'bot');
  }, 500);
}

function getBotResponse(userText) {
  const text = userText.toLowerCase();

  // Saludos
  if (text.includes('hola') || text.includes('buenas') || text.includes('inicio')) {
    return "¡Hola! ¿En qué puedo ayudarte hoy? Puedes preguntarme por servicios de plomería, cerrajería, carpintería, precios o registro.";
  }

  // Plomería
  if (text.includes('plomero') || text.includes('plomería') || text.includes('fuga') || text.includes('tubo')) {
    return "Contamos con expertos en plomería para solución de fugas, destapes e instalación de sanitarios. La tarifa promedio es de $50.000 COP.";
  }

  // Cerrajería
  if (text.includes('cerrajero') || text.includes('cerrajería') || text.includes('llave') || text.includes('chapa') || text.includes('puerta')) {
    return "Ofrecemos cerrajería residencial 24/7, apertura de puertas y cambio de guardas. La tarifa promedio es de $45.000 COP.";
  }

  // Carpintería
  if (text.includes('carpintero') || text.includes('carpintería') || text.includes('mueble') || text.includes('madera')) {
    return "Nuestros carpinteros realizan fabricación y reparación de muebles a medida, closets y puertas. La tarifa promedio es de $80.000 COP.";
  }

  // Clases o Educación
  if (text.includes('clase') || text.includes('profesor') || text.includes('curso') || text.includes('tarea')) {
    return "Tenemos profesores particulares para refuerzo escolar, matemáticas, ciencias e idiomas. La tarifa promedio es de $40.000 COP/hora.";
  }

  // Precios / Tarifas
  if (text.includes('precio') || text.includes('cuanto cuesta') || text.includes('costo') || text.includes('tarifa') || text.includes('valor')) {
    return "Los precios varían según el servicio: Plomería ($50k), Cerrajería ($45k), Carpintería ($80k), Clases ($40k). ¿Cuál te interesa?";
  }

  // Registro / Login
  if (text.includes('cuenta') || text.includes('registro') || text.includes('registrarse') || text.includes('iniciar')) {
    return "Puedes hacer clic en el botón 'Iniciar Sesión' en el menú superior para acceder o crear tu cuenta como cliente o profesional.";
  }

  // Agradecimientos
  if (text.includes('gracias') || text.includes('vale') || text.includes('ok')) {
    return "¡Con gusto! Estoy aquí para lo que necesites.";
  }

  // Respuesta por defecto si no entiende la palabra
  return "Entiendo. Para brindarte una mejor atención sobre ese tema, puedes dejar tu mensaje o ingresar al menú de Servicios o Iniciar Sesión para agendar directamente.";
}

function appendMsg(text, sender) {
  const box = document.getElementById('chatBox');
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${sender}`;

  if (sender === 'bot') {
    msgDiv.innerHTML = `
      <div class="msg-avatar">🤖</div>
      <div class="msg-text">${text}</div>
    `;
  } else {
    msgDiv.innerHTML = `
      <div class="msg-text">${text}</div>
    `;
  }

  box.appendChild(msgDiv);
  box.scrollTop = box.scrollHeight;
}

function handleKeyPress(e) {
  if (e.key === 'Enter') sendMessage();
}