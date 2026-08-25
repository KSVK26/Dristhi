// DRISHTI Field App - "Capture Evidence" screen
// ----------------------------------------------
// The heart of the inspection module:
//   1. Take a photo with the phone camera (image_picker)
//   2. Grab the current GPS position (geolocator)
//   3. Answer the 5-question yes/no checklist
//   4. Upload everything as multipart/form-data to POST /reports
//
// The backend then runs OpenCV face detection on the photo and
// flags 'possible_proxy' if no humans are visible.

import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'main.dart'; // kApiBase

const List<String> kQuestions = [
  'Staff physically present?',
  'Beneficiaries visible on site?',
  'Records / registers available?',
  'Scheme activities running today?',
  'Facilities clean & usable?',
];

class CaptureScreen extends StatefulWidget {
  final Map task;
  const CaptureScreen({super.key, required this.task});
  @override
  State<CaptureScreen> createState() => _CaptureScreenState();
}

class _CaptureScreenState extends State<CaptureScreen> {
  XFile? _photo;
  final Map<int, XFile> _qPhotos = {};   // checklist index -> photo proof
  Position? _position;
  late Map<String, bool> _answers;
  bool _busy = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _answers = {for (final q in kQuestions) q: true};
    _getLocation();
  }

  Future<void> _getLocation() async {
    try {
      // Ask for permission if not granted yet
      var perm = await Geolocator.checkPermission();
      if (perm == LocationPermission.denied) {
        perm = await Geolocator.requestPermission();
      }
      if (perm == LocationPermission.denied ||
          perm == LocationPermission.deniedForever) {
        return; // continue without GPS (backend still accepts)
      }
      final pos = await Geolocator.getCurrentPosition();
      setState(() => _position = pos);
    } catch (_) {/* GPS errors are non-fatal for the demo */}
  }

  Future<void> _takePhoto() async {
    final picker = ImagePicker();
    final photo = await picker.pickImage(
        source: ImageSource.camera, imageQuality: 70, maxWidth: 1280);
    if (photo != null) setState(() => _photo = photo);
  }

  Future<void> _takeQPhoto(int index) async {
    final picker = ImagePicker();
    final photo = await picker.pickImage(
        source: ImageSource.camera, imageQuality: 60, maxWidth: 1024);
    if (photo != null) setState(() => _qPhotos[index] = photo);
  }

  Future<void> _submit() async {
    if (_photo == null) {
      setState(() => _error = 'Please take an evidence photo first.');
      return;
    }
    setState(() { _busy = true; _error = null; });
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token')!;

      final req = http.MultipartRequest('POST', Uri.parse('$kApiBase/reports'))
        ..headers['Authorization'] = 'Bearer $token'
        ..fields['inspection_id'] = widget.task['inspection_id'].toString()
        ..fields['geo_lat'] = (_position?.latitude ?? 0).toString()
        ..fields['geo_lng'] = (_position?.longitude ?? 0).toString()
        ..fields['checklist'] = jsonEncode(_answers)
        ..files.add(await http.MultipartFile.fromPath('photo', _photo!.path));

      // attach per-checklist-item photo proofs (q0_photo … q4_photo)
      for (final entry in _qPhotos.entries) {
        req.files.add(await http.MultipartFile.fromPath(
            'q${entry.key}_photo', entry.value.path));
      }

      final res = await req.send();
      final body = await res.stream.bytesToString();

      if (!mounted) return;
      if (res.statusCode == 200) {
        final data = jsonDecode(body);
        final faces = data['faces_detected'];
        final flags = List<String>.from(data['ai_flags'] ?? []);
        showDialog(context: context, barrierDismissible: false,
          builder: (_) => AlertDialog(
            title: Text(flags.contains('possible_proxy')
                ? '⚠ AI Flag Raised' : '✅ Report Submitted'),
            content: Text(flags.contains('possible_proxy')
                ? 'No human faces detected in your evidence photo. '
                  'The report was flagged as POSSIBLE PROXY and sent to '
                  'the department dashboard.'
                : 'Report saved with $faces face(s) verified. '
                  'Geo-tagged evidence is now visible on the dashboard.'),
            actions: [FilledButton(
              onPressed: () {
                Navigator.pop(context);           // close dialog
                Navigator.pop(context);           // back to tasks
              },
              child: const Text('OK'))],
          ));
      } else {
        setState(() => _error = 'Upload failed ($res.statusCode): $body');
      }
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Evidence — ${widget.task['institute_name']}')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        // ---------- photo ----------
        GestureDetector(
          onTap: _takePhoto,
          child: Container(
            height: 220,
            decoration: BoxDecoration(
              color: Colors.blueGrey.shade50,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: Colors.blueGrey.shade200),
            ),
            clipBehavior: Clip.antiAlias,
            child: _photo == null
                ? const Center(child: Column(mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.camera_alt, size: 44, color: Colors.blueGrey),
                      SizedBox(height: 8),
                      Text('Tap to capture evidence photo'),
                    ]))
                : Image.file(File(_photo!.path), fit: BoxFit.cover),
          ),
        ),
        const SizedBox(height: 8),

        // ---------- GPS ----------
        Row(children: [
          Icon(_position == null ? Icons.location_off : Icons.location_on,
               color: _position == null ? Colors.grey : Colors.green, size: 18),
          const SizedBox(width: 6),
          Expanded(child: Text(_position == null
              ? 'Acquiring GPS…'
              : '📍 ${_position!.latitude.toStringAsFixed(5)}, '
                '${_position!.longitude.toStringAsFixed(5)}',
            style: const TextStyle(fontSize: 13))),
        ]),
        const Divider(height: 28),

        // ---------- checklist (each answer can carry its own photo proof) ----------
        ...List.generate(kQuestions.length, (i) {
          final q = kQuestions[i];
          final qp = _qPhotos[i];
          return Column(children: [
            SwitchListTile(
              title: Text(q, style: const TextStyle(fontSize: 15)),
              value: _answers[q]!,
              activeThumbColor: Colors.green,
              onChanged: (v) => setState(() => _answers[q] = v),
            ),
            Padding(
              padding: const EdgeInsets.only(left: 16, right: 16, bottom: 8),
              child: Row(children: [
                OutlinedButton.icon(
                  onPressed: () => _takeQPhoto(i),
                  icon: const Icon(Icons.photo_camera, size: 18),
                  label: Text(qp == null ? 'Add photo proof' : 'Retake',
                      style: const TextStyle(fontSize: 12)),
                ),
                if (qp != null) ...[
                  const SizedBox(width: 10),
                  GestureDetector(
                    onTap: () => _takeQPhoto(i),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.file(File(qp.path),
                          width: 56, height: 42, fit: BoxFit.cover),
                    ),
                  ),
                  const SizedBox(width: 6),
                  const Icon(Icons.verified, size: 16, color: Colors.green),
                  IconButton(
                    tooltip: 'Remove photo',
                    icon: const Icon(Icons.close, size: 16),
                    onPressed: () => setState(() => _qPhotos.remove(i)),
                  ),
                ],
              ]),
            ),
          ]);
        }),

        if (_error != null)
          Padding(padding: const EdgeInsets.only(top: 10),
            child: Text(_error!, style: const TextStyle(color: Colors.red))),

        const SizedBox(height: 16),
        FilledButton.icon(
          style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(52)),
          icon: _busy
              ? const SizedBox(width: 18, height: 18,
                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
              : const Icon(Icons.cloud_upload),
          label: Text(_busy ? 'Uploading…' : 'Submit Geo-Tagged Report'),
          onPressed: _busy ? null : _submit,
        ),
      ]),
    );
  }
}