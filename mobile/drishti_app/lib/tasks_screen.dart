// DRISHTI Field App - "My Tasks" screen
// --------------------------------------
// Lists every inspection assigned to the logged-in inspector.
// Each card shows the institute on a mini OpenStreetMap and offers:
//   * Capture Evidence  -> camera + GPS + checklist submission
//   * Join Surprise VC  -> opens the Jitsi room in a browser

import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:latlong2/latlong.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';

import 'main.dart'; // kApiBase
import 'capture_screen.dart';

class TasksScreen extends StatefulWidget {
  const TasksScreen({super.key});
  @override
  State<TasksScreen> createState() => _TasksScreenState();
}

class _TasksScreenState extends State<TasksScreen> {
  List tasks = [];
  String name = '';
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token')!;
    setState(() => name = prefs.getString('name') ?? '');

    final res = await http.get(
      Uri.parse('$kApiBase/inspections/my'),
      headers: {'Authorization': 'Bearer $token'},
    );
    if (!mounted) return;
    if (res.statusCode == 200) {
      setState(() { tasks = jsonDecode(res.body); loading = false; });
    } else if (res.statusCode == 401) {
      // token expired -> back to login
      Navigator.of(context).pushReplacementNamed('/');
    }
  }

  Future<void> _joinVC(Map task) async {
    // Ask backend to create a surprise VC room for this institute
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token')!;
    final res = await http.post(
      Uri.parse('$kApiBase/vc/start'),
      headers: {'Authorization': 'Bearer $token',
                'Content-Type': 'application/json'},
      body: jsonEncode({'institute_id': task['institute_id']}),
    );
    if (!mounted) return;
    if (res.statusCode == 200) {
      final url = jsonDecode(res.body)['url'] as String;
      await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Only admins can start VC rooms.')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('My Tasks — $name'),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _load),
        ],
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : tasks.isEmpty
              ? const Center(child: Text('No inspections assigned yet.'))
              : ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: tasks.length,
                  itemBuilder: (_, i) {
                    final t = tasks[i];
                    final done = t['status'] == 'completed';
                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      clipBehavior: Clip.antiAlias,
                      child: Column(children: [
                        // mini map showing where the institute is
                        SizedBox(
                          height: 130,
                          child: FlutterMap(
                            options: MapOptions(
                              initialCenter: LatLng(t['lat'], t['lng']),
                              initialZoom: 13,
                              interactionOptions: const InteractionOptions(flags: InteractiveFlag.none),
                            ),
                            children: [
                              TileLayer(urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
                              MarkerLayer(markers: [
                                Marker(
                                  point: LatLng(t['lat'], t['lng']),
                                  width: 40, height: 40,
                                  child: const Icon(Icons.location_on, color: Colors.red, size: 36),
                                ),
                              ]),
                            ],
                          ),
                        ),
                        Padding(
                          padding: const EdgeInsets.all(14),
                          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                            Row(children: [
                              Expanded(child: Text(t['institute_name'],
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16))),
                              if (t['is_random'])
                                Chip(label: const Text('SURPRISE', style: TextStyle(fontSize: 10)),
                                     visualDensity: VisualDensity.compact),
                            ]),
                            Text('${t['scheme']} · ${t['district']}',
                                style: const TextStyle(color: Colors.blueGrey)),
                            const SizedBox(height: 10),
                            Row(children: [
                              Expanded(
                                child: FilledButton.icon(
                                  icon: Icon(done ? Icons.check_circle : Icons.camera_alt),
                                  label: Text(done ? 'Completed' : 'Capture Evidence'),
                                  onPressed: done ? null : () async {
                                    await Navigator.push(context, MaterialPageRoute(
                                      builder: (_) => CaptureScreen(task: t)));
                                    _load(); // refresh status after submit
                                  },
                                ),
                              ),
                              const SizedBox(width: 8),
                              OutlinedButton.icon(
                                icon: const Icon(Icons.videocam),
                                label: const Text('Join VC'),
                                onPressed: () => _joinVC(t),
                              ),
                            ]),
                          ]),
                        ),
                      ]),
                    );
                  },
                ),
    );
  }
}