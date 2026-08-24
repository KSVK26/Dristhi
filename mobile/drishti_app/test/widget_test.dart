// DRISHTI - basic widget smoke test
// Verifies the login screen renders with the app title.

import 'package:flutter_test/flutter_test.dart';
import 'package:drishti_app/main.dart';

void main() {
  testWidgets('login screen renders', (tester) async {
    await tester.pumpWidget(const DrishtiApp());
    expect(find.text('DRISHTI'), findsOneWidget);
    expect(find.text('Sign In'), findsOneWidget);
  });
}