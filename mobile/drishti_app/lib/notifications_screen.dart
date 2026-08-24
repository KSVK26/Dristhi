// DRISHTI Field App - Alerts tab content (unread notifications)
// --------------------------------------------------------------
// Rendered inside the app shell's bottom-navigation. Mark read per
// item or all at once; auto-refreshes every 15 s.

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

import 'main.dart'; // kApiBase

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key, this.refreshSignal = 0});
  final int refreshSignal;
  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  List items = [];
  bool busy = false;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _load();
    _timer = Timer.periodic(const Duration(seconds: 15), (_) => _load());
  }

  @override
  void didUpdateWidget(covariant NotificationsScreen old) {
    super.didUpdateWidget(old);
    if (old.refreshSignal != widget.refreshSignal) _load();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token')!;
    try {
      final res = await http.get(
        Uri.parse('$kApiBase/notifications'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200 && mounted) {
        setState(() => items = jsonDecode(res.body));
      }
    } catch (_) {}
  }

  Future<void> _markOne(int id) async {
    final prefs = await SharedPreferences.getInstance();
    await http.post(
      Uri.parse('$kApiBase/notifications/$id/read'),
      headers: {'Authorization': 'Bearer ${prefs.getString('token')}'},
    );
    _load();
  }

  Future<void> _markAll() async {
    setState(() => busy = true);
    final prefs = await SharedPreferences.getInstance();
    await http.post(
      Uri.parse('$kApiBase/notifications/read-all'),
      headers: {'Authorization': 'Bearer ${prefs.getString('token')}'},
    );
    setState(() => busy = false);
    _load();
  }

  Color _sevColor(String s) =>
      s == 'high' ? Colors.red : s == 'medium' ? Colors.orange : Colors.green;

  @override
  Widget build(BuildContext context) {
    // Tab content — the app shell provides the Scaffold + bottom nav.
    return Column(children: [
      Padding(
        padding: const EdgeInsets.fromLTRB(16, 12, 8, 0),
        child: Row(children: [
          Text('Alerts (${items.length} unread)',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const Spacer(),
          TextButton(
            onPressed: (busy || items.isEmpty) ? null : _markAll,
            child: const Text('Mark all read'),
          ),
        ]),
      ),
      Expanded(
        child: RefreshIndicator(
          onRefresh: _load,
          child: items.isEmpty
              ? const Center(
                  child: Text('🎉 All caught up — no unread notifications.'))
              : ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: items.length,
                  itemBuilder: (_, i) {
                    final n = items[i];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 10),
                      child: ListTile(
                        leading: CircleAvatar(
                          radius: 5,
                          backgroundColor: _sevColor(n['severity']),
                        ),
                        title: Text(
                          n['message'],
                          style: const TextStyle(fontSize: 13.5),
                        ),
                        subtitle: Text(
                          '${n['type'].toString().replaceAll('_', ' ')} · '
                          '${n['created_at'].toString().substring(0, 16)}',
                          style: const TextStyle(fontSize: 11.5),
                        ),
                        trailing: TextButton(
                          onPressed: () => _markOne(n['id']),
                          child: const Text('Mark read'),
                        ),
                      ),
                    );
                  },
                ),
        ),
      ),
    ]);
  }
}
