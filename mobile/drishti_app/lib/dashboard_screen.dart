// DRISHTI Field App - Dashboard (Home tab)
// -----------------------------------------
// Mirrors the web inspector dashboard: welcome header, 4 stat cards,
// "Next up" hero card (nearest pending task), recent activity feed.

import 'dart:convert';
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';

import 'main.dart'; // kApiBase
import 'capture_screen.dart';

double _haversineKm(lat1, lng1, lat2, lng2) {
  const r = 6371.0;
  final p1 = lat1 * math.pi / 180, p2 = lat2 * math.pi / 180;
  final dp = (lat2 - lat1) * math.pi / 180, dl = (lng2 - lng1) * math.pi / 180;
  final a = math.sin(dp / 2) * math.sin(dp / 2) +
      math.cos(p1) * math.cos(p2) * math.sin(dl / 2) * math.sin(dl / 2);
  return 2 * r * math.asin(math.sqrt(a));
}

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key, this.refreshSignal = 0});
  final int refreshSignal; // parent bumps this to trigger a reload
  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List tasks = [];
  List reports = [];
  Position? _position;
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _getLocation();
    _load();
  }

  @override
  void didUpdateWidget(covariant DashboardScreen old) {
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
    try {
      final tRes = await http.get(
        Uri.parse('$kApiBase/inspections/my'),
        headers: {'Authorization': 'Bearer $token'},
      );
      final rRes = await http.get(
        Uri.parse('$kApiBase/reports'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (mounted && tRes.statusCode == 200 && rRes.statusCode == 200) {
        final allReports = jsonDecode(rRes.body) as List;
        final my = jsonDecode(tRes.body) as List;
        final myIds = my.map((t) => t['inspection_id']).toSet();
        setState(() {
          tasks = my;
          reports = allReports
              .where((r) => myIds.contains(r['inspection_id']))
              .toList();
          loading = false;
        });
      } else if (mounted) {
        setState(() => loading = false);
      }
    } catch (_) {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> _startAndCapture(dynamic t) async {
    final prefs = await SharedPreferences.getInstance();
    if (t['status'] != 'in_progress') {
      await http.post(
        Uri.parse('$kApiBase/inspections/${t['inspection_id']}/start'),
        headers: {'Authorization': 'Bearer ${prefs.getString('token')}'},
      );
    }
    if (!mounted) return;
    await Navigator.push(context,
        MaterialPageRoute(builder: (_) => CaptureScreen(task: t)));
    _load();
  }

  Widget _statCard(IconData icon, Color color, String label, String value) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFFE2E8F0)),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Icon(icon, color: color, size: 22),
          const SizedBox(height: 6),
          Text(value,
              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800)),
          Text(label,
              style: const TextStyle(fontSize: 11, color: Colors.blueGrey),
              overflow: TextOverflow.ellipsis),
        ]),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final pending = tasks.where((t) => t['status'] == 'assigned').length;
    final inProg = tasks.where((t) => t['status'] == 'in_progress').length;
    final done = tasks.where((t) => t['status'] == 'completed').length;
    final proxyFlags =
        reports.where((r) => (r['ai_flags'] as List).isNotEmpty).length;

    // nearest pending task (needs GPS)
    dynamic nextUp;
    if (_position != null) {
      final open = tasks.where((t) => t['status'] != 'completed').toList();
      for (final t in open) {
        t['km'] = _haversineKm(
            _position!.latitude, _position!.longitude, t['lat'], t['lng']);
      }
      open.sort((a, b) => (a['km'] as double).compareTo(b['km'] as double));
      nextUp = open.isEmpty ? null : open.first;
    }

    final today = DateTime.now();
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];

    return RefreshIndicator(
      onRefresh: _load,
      child: loading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Text(
                  '${days[today.weekday - 1].toUpperCase()} · ${today.day} ${months[today.month - 1].toUpperCase()} · ${today.year}',
                  style: const TextStyle(
                      fontSize: 10.5, letterSpacing: 2, color: Colors.blueGrey),
                ),
                FutureBuilder<SharedPreferences>(
                  future: SharedPreferences.getInstance(),
                  builder: (context, snap) {
                    final nm = snap.data?.getString('name') ?? '';
                    return Text.rich(TextSpan(children: [
                      const TextSpan(
                          text: 'Namaste, ',
                          style: TextStyle(
                              fontSize: 26, fontWeight: FontWeight.w800)),
                      TextSpan(
                          text: nm,
                          style: const TextStyle(
                              fontSize: 26,
                              fontWeight: FontWeight.w800,
                              color: Color(0xFF2563EB))),
                    ]));
                  },
                ),
                const SizedBox(height: 16),
                Row(children: [
                  _statCard(Icons.hourglass_top, Colors.orange, 'Pending', '$pending'),
                  const SizedBox(width: 10),
                  _statCard(Icons.directions_walk, Colors.blue, 'In progress', '$inProg'),
                ]),
                const SizedBox(height: 10),
                Row(children: [
                  _statCard(Icons.check_circle, Colors.green, 'Completed', '$done'),
                  const SizedBox(width: 10),
                  _statCard(Icons.warning_amber_rounded, Colors.red, 'Proxy flags', '$proxyFlags'),
                ]),
                const SizedBox(height: 18),

                // ---------- Next up hero ----------
                if (nextUp != null) ...[
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFFE2E8F0)),
                      boxShadow: [
                        BoxShadow(
                            color: Colors.black.withValues(alpha: .05),
                            blurRadius: 12)
                      ],
                    ),
                    child: Column(crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                      const Text('🧭 NEXT UP — NEAREST PENDING TASK',
                          style: TextStyle(
                              fontSize: 10.5, letterSpacing: 1.5,
                              color: Colors.blueGrey,
                              fontWeight: FontWeight.w600)),
                      const SizedBox(height: 8),
                      Text(nextUp['institute_name'],
                          style: const TextStyle(
                              fontSize: 17, fontWeight: FontWeight.bold)),
                      Text(
                        '${nextUp['scheme']} · ${nextUp['district']}'
                        '${nextUp['km'] != null ? ' · 📍 ${(nextUp['km'] as double).toStringAsFixed(1)} km' : ''}',
                        style: const TextStyle(
                            fontSize: 12.5, color: Colors.blueGrey),
                      ),
                      const SizedBox(height: 12),
                      Row(children: [
                        Expanded(
                          child: FilledButton.icon(
                            icon: const Icon(Icons.camera_alt, size: 18),
                            label: const Text('Capture Evidence'),
                            onPressed: () => _startAndCapture(nextUp),
                          ),
                        ),
                        const SizedBox(width: 8),
                        OutlinedButton(
                          onPressed: () => launchUrl(
                              Uri.parse(
                                  'https://www.google.com/maps?q=${nextUp['lat']},${nextUp['lng']}'),
                              mode: LaunchMode.externalApplication),
                          child: const Text('🧭'),
                        ),
                      ]),
                    ]),
                  ),
                  const SizedBox(height: 18),
                ],

                // ---------- recent activity ----------
                const Text('RECENT ACTIVITY',
                    style: TextStyle(
                        fontSize: 10.5, letterSpacing: 1.5,
                        color: Colors.blueGrey, fontWeight: FontWeight.w600)),
                const SizedBox(height: 8),
                if (reports.isEmpty)
                  const Text('No submissions yet.',
                      style: TextStyle(color: Colors.blueGrey)),
                ...reports.take(3).map((r) {
                  final flagged = (r['ai_flags'] as List).isNotEmpty;
                  return Card(
                    margin: const EdgeInsets.only(bottom: 8),
                    child: ListTile(
                      leading: Icon(
                          flagged
                              ? Icons.warning_amber_rounded
                              : Icons.check_circle,
                          color: flagged ? Colors.red : Colors.green),
                      title: Text(r['institute_name'],
                          style: const TextStyle(
                              fontSize: 14, fontWeight: FontWeight.w600)),
                      subtitle: Text(
                          flagged ? '⚠ Proxy flag raised' : '✔ AI verified',
                          style: const TextStyle(fontSize: 12)),
                      trailing: Text(
                          DateTime.parse(r['created_at'])
                              .toString()
                              .substring(0, 10),
                          style: const TextStyle(fontSize: 11)),
                    ),
                  );
                }),
              ],
            ),
    );
  }
}
