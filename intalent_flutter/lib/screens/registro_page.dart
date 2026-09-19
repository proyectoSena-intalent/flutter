import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class RegistroPage extends StatefulWidget {
  const RegistroPage({super.key});

  @override
  State<RegistroPage> createState() => _RegistroPageState();
}

class _RegistroPageState extends State<RegistroPage> {
  String tipoUsuario = 'Cliente';

  final TextEditingController nombreController =
      TextEditingController();

  final TextEditingController correoController =
    TextEditingController();

  final TextEditingController telefonoController =
    TextEditingController();

  final TextEditingController passwordController =
    TextEditingController();

  final TextEditingController confirmarPasswordController =
    TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,

      appBar: AppBar(
        title: const Text('Crear cuenta'),
        backgroundColor: Colors.white,
        elevation: 0,
      ),

      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(30),

          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [

              const SizedBox(height: 20),

              // Ícono
              Center(
                child: Icon(
                  Icons.person_add_alt_1,
                  size: 75,
                  color: Colors.blue.shade700,
                ),
              ),

              const SizedBox(height: 25),

              // Título
              const Center(
                child: Text(
                  'Crea tu cuenta',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),

              const SizedBox(height: 10),

              // Descripción
              const Center(
                child: Text(
                  'Regístrate en InTalent y comienza a conectar con personas.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.black54,
                  ),
                ),
              ),

              const SizedBox(height: 35),

              // Nombre
              const Text(
                'Nombre completo',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),

              const SizedBox(height: 8),

              TextField(
                controller: nombreController,
                decoration: InputDecoration(
                  hintText: 'Ingresa tu nombre completo',
                  prefixIcon: const Icon(Icons.person_outline),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),

              const SizedBox(height: 20),

              // Correo
              const Text(
                'Correo electrónico',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),

              const SizedBox(height: 8),

              TextField(
                controller: correoController,
                keyboardType: TextInputType.emailAddress,
                decoration: InputDecoration(
                  hintText: 'ejemplo@correo.com',
                  prefixIcon: const Icon(Icons.email_outlined),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),

              const SizedBox(height: 20),

              // Teléfono
              const Text(
                'Número de teléfono',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),

              const SizedBox(height: 8),

              TextField(
                controller: telefonoController,
                keyboardType: TextInputType.phone,
                inputFormatters: [
  FilteringTextInputFormatter.digitsOnly,
  LengthLimitingTextInputFormatter(10),
],
                decoration: InputDecoration(
                  hintText: '300 000 0000',
                  prefixIcon: const Icon(Icons.phone_outlined),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),

              const SizedBox(height: 20),

              // Contraseña
              const Text(
                'Contraseña',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),

              const SizedBox(height: 8),

              TextField(
                controller: passwordController,
                obscureText: true,
                decoration: InputDecoration(
                  hintText: 'Crea una contraseña',
                  prefixIcon: const Icon(Icons.lock_outline),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),

              const SizedBox(height: 20),

              const Text(
  'Confirmar contraseña',
  style: TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w600,
  ),
),

const SizedBox(height: 8),

TextField(
  controller: confirmarPasswordController,
  obscureText: true,
  decoration: InputDecoration(
    hintText: 'Repite tu contraseña',
    prefixIcon: const Icon(Icons.lock_outline),
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
    ),
  ),
),

const SizedBox(height: 25),

              // Tipo de usuario
              const Text(
                '¿Qué quieres hacer en InTalent?',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),

              const SizedBox(height: 10),

              RadioListTile<String>(
                title: const Text('Buscar servicios'),
                subtitle: const Text(
                  'Necesito contratar a una persona.',
                ),
                value: 'Cliente',
                groupValue: tipoUsuario,
                onChanged: (value) {
                  setState(() {
                    tipoUsuario = value!;
                  });
                },
              ),

              RadioListTile<String>(
                title: const Text('Ofrecer servicios'),
                subtitle: const Text(
                  'Quiero ofrecer mis servicios.',
                ),
                value: 'Proveedor',
                groupValue: tipoUsuario,
                onChanged: (value) {
                  setState(() {
                    tipoUsuario = value!;
                  });
                },
              ),

              const SizedBox(height: 25),

              // Botón registrar
              SizedBox(
                width: double.infinity,
                height: 55,
                child: ElevatedButton(
                  onPressed: () {
                    // Validar nombre
  if (nombreController.text.trim().isEmpty) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Por favor ingresa tu nombre completo'),
      ),
    );
    return;
  }

  // Validar correo vacío
  if (correoController.text.trim().isEmpty) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Por favor ingresa tu correo electrónico'),
      ),
    );
    return;
  }

  // Validar formato básico del correo
  if (!correoController.text.contains('@') ||
      !correoController.text.contains('.')) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Ingresa un correo electrónico válido'),
      ),
    );
    return;
  }

  // Validar teléfono vacío
if (telefonoController.text.trim().isEmpty) {
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(
      content: Text('Por favor ingresa tu número de teléfono'),
    ),
  );
  return;
}

// Validar que tenga exactamente 10 dígitos
if (telefonoController.text.trim().length != 10) {
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(
      content: Text('El número de teléfono debe tener 10 dígitos'),
    ),
  );
  return;
}

// Validar que empiece por 3
if (!telefonoController.text.trim().startsWith('3')) {
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(
      content: Text('El número de teléfono debe comenzar por 3'),
    ),
  );
  return;
}

// Obtener contraseña
String password = passwordController.text;

// Validar contraseña vacía
if (password.trim().isEmpty) {
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(
      content: Text('Por favor ingresa una contraseña'),
    ),
  );
  return;
}

// Validar mínimo 8 caracteres
if (password.length < 8) {
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(
      content: Text('La contraseña debe tener mínimo 8 caracteres'),
    ),
  );
  return;
}

// Validar mínimo una mayúscula
if (!password.contains(RegExp(r'[A-Z]'))) {
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(
      content: Text(
        'La contraseña debe tener al menos una letra mayúscula',
      ),
    ),
  );
  return;
}

// Validar mínimo un número
if (!password.contains(RegExp(r'[0-9]'))) {
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(
      content: Text(
        'La contraseña debe tener al menos un número',
      ),
    ),
  );
  return;
}

// Validar mínimo un carácter especial
if (!password.contains(RegExp(r'[!@#$%^&*(),.?":{}|<>_\-\\\/\[\]~`+=;]'))) {
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(
      content: Text(
        'La contraseña debe tener al menos un carácter especial',
      ),
    ),
  );
  return;
}
// Validar que las contraseñas coincidan
if (password != confirmarPasswordController.text) {
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(
      content: Text(
        'Las contraseñas no coinciden',
      ),
    ),
  );
  return;
}

  ScaffoldMessenger.of(context).showSnackBar(
  const SnackBar(
    content: Text(
      'Cuenta creada correctamente',
    ),
  ),
);
                  },

                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue.shade700,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: const Text(
                    'Crear cuenta',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 15),

              // Volver
              Center(
                child: TextButton(
                  onPressed: () {
                    Navigator.pop(context);
                  },
                  child: const Text(
                    'Volver',
                    style: TextStyle(
                      fontSize: 16,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}