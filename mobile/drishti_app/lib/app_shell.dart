// DRISHTI Field App - App shell with bottom navigation
// -----------------------------------------------------
// Home (dashboard) · My Tasks · Alerts (notifications).
// IndexedStack keeps each tab's state alive across switches.

import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import 'dashboard_screen.dart';
import 'notifications_screen.dart';
import 'tasks_screen.dart';
import 'main.dart'; // kApiBase

class AppShell extends StatefulWidget {
  const AppShell({super.key});
  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _tab = 0;
  int _refreshSignal = 0; // bump to make other tabs reload their data
  int _unread = 0;

  @override
  void initState() {
    super.initState();
    _loadUnread();
  }

  Future<void> _loadUnread() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final res = await http.get(
        Uri.parse('$kApiBase/notifications'),
        headers: {'Authorization': 'Bearer ${prefs.getString('token')}'},
      );
      if (res.statusCode == 200 && mounted) {
        setState(() => _unread = (jsonDecode(res.body) as List).length);
      }
    } catch (_) {}
  }

  void _onTabTapped(int i) {
    setState(() {
      _tab = i;
      _refreshSignal++; // tabs refresh their data when revisited
    });
    _loadUnread();
  }

  @override
  Widget build(BuildContext context) {
    final screens = [
      DashboardScreen(refreshSignal: _refreshSignal),
      TasksScreen(refreshSignal: _refreshSignal),
      const NotificationsScreen(),
    ];

    return Scaffold(
      body: IndexedStack(index: _tab, children: screens),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: _onTabTapped,
        destinations: [
          const NavigationDestination(
              icon: Icon(Icons.dashboard_outlined),
              selectedIcon: Icon(Icons.dashboard),
              label: 'Home'),
          const NavigationDestination(
              icon: Icon(Icons.checklist_outlined),
              selectedIcon: Icon(Icons.checklist),
              label: 'My Tasks'),
          NavigationDestination(
              icon: Badge(
                  label: Text('$_unread'),
                  isLabelVisible: _unread > 0,
                  child: const Icon(Icons.notifications_outlined)),
              selectedIcon: const Icon(Icons.notifications),
              label: 'Alerts'),
        ],
      ),
    );
  }
}
