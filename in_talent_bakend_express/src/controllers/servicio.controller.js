const Servicio = require('../models/Servicio.model');

// Obtener todos los servicios
exports.obtenerServicios = async (req, res) => {
    try {
        const servicios = await Servicio.find();
        
        // Mapeamos para enviar los nombres de campos exactos que espera Kotlin
        const serviciosFormateados = servicios.map(s => ({
            _id: s._id,
            title: s.titulo || s.nombre || "Servicio sin título",
            description: s.descripcion || "Sin descripción",
            category: s.categoria || "General",
            price: s.precio || 0,
            rating: s.calificacion || 5.0,
            imageUrl: s.imagenUrl || null
        }));

        res.status(200).json(serviciosFormateados);
    } catch (error) {
        console.error("Error al obtener servicios:", error);
        res.status(500).json({ message: "Error interno del servidor", error: error.message });
    }
// Si la base de datos está vacía, devuelve mock data para probar la app Android
if (servicios.length === 0) {
    return res.status(200).json([
        {
            _id: "1",
            title: "Desarrollo Web Full Stack",
            description: "Creación de páginas web con Node.js y React",
            category: "Tecnología",
            price: 150000,
            rating: 4.8
        },
        {
            _id: "2",
            title: "Mantenimiento Técnico",
            description: "Diagnóstico y reparación de equipos de cómputo",
            category: "Soporte",
            price: 80000,
            rating: 5.0
        }
    ]);
}
};