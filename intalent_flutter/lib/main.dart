import 'package:flutter/material.dart';
import 'screens/inicio_page.dart';

void main() {
  runApp(const InTalentApp());
}

class InTalentApp extends StatelessWidget {
  const InTalentApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'InTalent',
      theme: ThemeData(
        useMaterial3: true,
      ),
      home: const InicioPage(),
    );
  }
}