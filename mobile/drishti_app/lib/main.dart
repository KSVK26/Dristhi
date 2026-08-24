// DRISHTI Field App - entry point + login screen
// ------------------------------------------------
// The inspector logs in with the same account as the dashboard.
// The JWT token is stored on the phone (shared_preferences) and sent
// with every request to the FastAPI backend.
//
// IMPORTANT for the demo:
//   - Android emulator -> use http://10.0.2.2:8000  (emulator's "localhost")
//   - Physical phone   -> use your PC's WiFi IP, e.g. http://192.168.1.10:8000

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

import 'app_shell.dart';

// Backend URL per platform:
//   Web (Chrome/Edge)  -> localhost works directly
//   Android EMULATOR   -> 10.0.2.2 is the emulator's alias for your PC
//   Physical phone     -> replace with your PC's WiFi IP, e.g. 192.168.1.10
final String kApiBase =
    kIsWeb ? 'http://localhost:8000' : 'http://10.0.2.2:8000';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const DrishtiApp());
}

class DrishtiApp extends StatelessWidget {
  const DrishtiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'DRISHTI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: const Color(0xFF1565C0),
        useMaterial3: true,
      ),
      home: const LoginScreen(),
    );
  }
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _userCtrl = TextEditingController(text: 'ravi');
  final _passCtrl = TextEditingController(text: 'inspector123');
  bool _busy = false;
  String? _error;

  Future<void> _login() async {
    setState(() { _busy = true; _error = null; });
    try {
      final res = await http.post(
        Uri.parse('$kApiBase/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': _userCtrl.text.trim(),
          'password': _passCtrl.text,
        }),
      );
      if (res.statusCode != 200) {
        throw Exception('Login failed (${res.statusCode})');
      }
      final data = jsonDecode(res.body);
      if (data['role'] != 'inspector') {
        throw Exception('This app is for PMU inspectors only.');
      }

      // Save token + name for later screens
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('token', data['token']);
      await prefs.setString('name', data['name']);

      if (!mounted) return;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const AppShell()),
      );
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft, end: Alignment.bottomRight,
            colors: [Color(0xFF0D2137), Color(0xFF143A5E)],
          ),
        ),
        child: Center(
          child: Card(
            margin: const EdgeInsets.all(24),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
            child: Padding(
              padding: const EdgeInsets.all(28),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('👁️', style: TextStyle(fontSize: 48)),
                  const Text('DRISHTI',
                      style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold, letterSpacing: 4)),
                  const Text('PMU Field Inspection App',
                      style: TextStyle(color: Colors.blueGrey)),
                  const SizedBox(height: 24),
                  TextField(
                    controller: _userCtrl,
                    decoration: const InputDecoration(labelText: 'Username', border: OutlineInputBorder()),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _passCtrl,
                    obscureText: true,
                    decoration: const InputDecoration(labelText: 'Password', border: OutlineInputBorder()),
                  ),
                  if (_error != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 12),
                      child: Text(_error!, style: const TextStyle(color: Colors.red)),
                    ),
                  const SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: FilledButton(
                      onPressed: _busy ? null : _login,
                      child: Text(_busy ? 'Signing in…' : 'Sign In'),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}