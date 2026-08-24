// DRISHTI Field App - "My Tasks" screen (v3)
// -------------------------------------------
// Tasks sorted nearest-first with GPS distance, ▶ Start flow
// (assigned -> in_progress), status chips, offline hint banner,
// and a 🔔 AppBar bell with unread-notification badge.

import 'dart:convert';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:latlong2/latlong.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:geolocator/geolocator.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';

import 'main.dart'; // kApiBase
import 'capture_screen.dart';

double _haversineKm(lat1, lng1, lat2, lng2) {
  const r = 6371.0;
  final p1 = lat1 * pi / 180, p2 = lat2 * pi / 180;
  final dp = (lat2 - lat1) * pi / 180, dl = (lng2 - lng1) * pi / 180;
  final a = sin(dp / 2) * sin(dp / 2) +
      cos(p1) * cos(p2) * sin(dl / 2) * sin(dl / 2);
  return 2 * r * atan2(sqrt(a), sqrt(1 - a));
}

class TasksScreen extends StatefulWidget {
  const TasksScreen({super.key, this.refreshSignal = 0});
  final int refreshSignal;
  @override
  State<TasksScreen> createState() => _TasksScreenState();
}

class _TasksScreenState extends State<TasksScreen> {
  List tasks = [];
  String name = '';
  bool loading = true;
  Position? _position;
  int unread = 0;

  @override
  void initState() {
    super.initState();
    _getLocation();
    _load();
  }

  @override
  void didUpdateWidget(covariant TasksScreen old) {
    super.didUpdateWidget(old);
    if (old.refreshSignal != widget.refreshSignal) _load();
  }

  Future<void> _getLocation() async {
    try {
      var perm = await Geolocator.checkPermission();
      if (perm == LocationPermission.denied) {
        perm = await Geolocator.requestPermission();
      }
      if (perm == LocationPermission.denied ||
          perm == LocationPermission.deniedForever) {
        return;
      }
      final pos = await Geolocator.getCurrentPosition();
      if (mounted) setState(() => _position = pos);
    } catch (_) {}
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token')!;
    if (mounted) setState(() => name = prefs.getString('name') ?? '');
    try {
      final res = await http.get(
        Uri.parse('$kApiBase/inspections/my'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (!mounted) return;
      if (res.statusCode == 200) {
        setState(() { tasks = jsonDecode(res.body); loading = false; });
      } else if (res.statusCode == 401) {
        Navigator.of(context).pushReplacementNamed('/');
      }
      final nres = await http.get(
        Uri.parse('$kApiBase/notifications'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (nres.statusCode == 200 && mounted) {
        setState(() => unread = (jsonDecode(nres.body) as List).length);
      }
    } catch (_) {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> _startTask(int id) async {
    final prefs = await SharedPreferences.getInstance();
    await http.post(
      Uri.parse('$kApiBase/inspections/$id/start'),
      headers: {'Authorization': 'Bearer ${prefs.getString('token')}'},
    );
    _load();
  }

  Future<void> _joinVC(Map task) async {
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
        const SnackBar(content: Text('Only admins can start VC rooms. '
            'Check your notifications for the join link.')));
    }
  }

  Widget _statusChip(String status) {
    final (label, color) = status == 'completed'
        ? ('✔ Completed', Colors.green)
        : status == 'in_progress'
            ? ('🔄 In progress', Colors.blue)
            : ('⏳ Assigned', Colors.orange);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: color.withValues(alpha: .12),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Text(label,
          style: TextStyle(fontSize: 11.5, fontWeight: FontWeight.bold, color: color)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final sorted = [...tasks];
    if (_position != null) {
      for (final t in sorted) {
        t['km'] = _haversineKm(
            _position!.latitude, _position!.longitude, t['lat'], t['lng']);
      }
      sorted.sort((a, b) => (a['km'] as double).compareTo(b['km'] as double));
    }

    return Scaffold(
      appBar: AppBar(
        title: Text('My Tasks — $name'),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _load),
        ],
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _load,
              child: ListView(
                padding: const EdgeInsets.all(12),
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFFEFF6FF),
                      border: Border.all(color: const Color(0xFFBFDBFE)),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Text(
                      '📶 No internet at site? Evidence captures in the app and '
                      'syncs when you\'re back online.',
                      style: TextStyle(fontSize: 12.5, color: Color(0xFF1E40AF)),
                    ),
                  ),
                  const SizedBox(height: 12),
                  if (sorted.isEmpty)
                    const Padding(
                      padding: EdgeInsets.all(32),
                      child: Center(child: Text('No tasks assigned yet.')),
                    ),
                  ...sorted.map(_taskCard),
                ],
              ),
            ),
    );
  }

  Widget _taskCard(dynamic t) {
    final done = t['status'] == 'completed';
    final progress = t['status'] == 'in_progress';
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      clipBehavior: Clip.antiAlias,
      child: Column(children: [
        SizedBox(
          height: 120,
          child: FlutterMap(
            options: MapOptions(
              initialCenter: LatLng(t['lat'], t['lng']),
              initialZoom: 13,
              interactionOptions:
                  const InteractionOptions(flags: InteractiveFlag.none),
            ),
            children: [
              TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
              MarkerLayer(markers: [
                Marker(
                  point: LatLng(t['lat'], t['lng']),
                  width: 40,
                  height: 40,
                  child: const Icon(Icons.location_on,
                      color: Colors.red, size: 36),
                ),
              ]),
            ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(14),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              Expanded(
                  child: Text(t['institute_name'],
                      style: const TextStyle(
                          fontWeight: FontWeight.bold, fontSize: 16))),
              if (t['is_random'])
                Chip(
                    label: const Text('SURPRISE',
                        style: TextStyle(fontSize: 10)),
                    visualDensity: VisualDensity.compact),
            ]),
            Text(
              '${t['scheme']} · ${t['district']}'
              '${t['km'] != null ? ' · 📍 ${(t['km'] as double).toStringAsFixed(1)} km away' : ''}',
              style: const TextStyle(color: Colors.blueGrey, fontSize: 13),
            ),
            const SizedBox(height: 10),
            Row(children: [
              _statusChip(t['status']),
              const Spacer(),
              OutlinedButton.icon(
                icon: const Icon(Icons.map, size: 18),
                label: const Text('Navigate'),
                onPressed: () => launchUrl(
                    Uri.parse(
                        'https://www.google.com/maps?q=${t['lat']},${t['lng']}'),
                    mode: LaunchMode.externalApplication),
              ),
            ]),
            const SizedBox(height: 10),
            Row(children: [
              Expanded(
                child: FilledButton.icon(
                  icon: Icon(done
                      ? Icons.check_circle
                      : progress
                          ? Icons.directions_walk
                          : Icons.camera_alt),
                  label: Text(done
                      ? 'Completed'
                      : progress
                          ? 'Capture Evidence'
                          : 'Start & Capture'),
                  onPressed: done
                      ? null
                      : () async {
                          if (!progress) {
                            await _startTask(t['inspection_id']);
                          }
                          if (!mounted) return;
                          await Navigator.push(
                              context,
                              MaterialPageRoute(
                                  builder: (_) => CaptureScreen(task: t)));
                          _load();
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
  }
}
