import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:skillbridge/app.dart';
import 'package:skillbridge/domain/repositories/career_repository.dart';

class FakeCareerRepository implements CareerRepository {
  @override
  Future<bool> hasSession() async => false;

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(() {
    const channel = MethodChannel('plugins.it_nomads.com/flutter_secure_storage');
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (MethodCall methodCall) async {
      if (methodCall.method == 'read') {
        if (methodCall.arguments['key'] == 'is_first_launch') {
          return 'false'; // simulate not first launch
        }
      }
      return null;
    });
  });

  testWidgets('App launches successfully', (WidgetTester tester) async {
    final repository = FakeCareerRepository();
    await tester.pumpWidget(SkillBridgeApp(repository: repository));
    await tester.pumpAndSettle();
    // Verify that the OTP Auth screen is displayed
    expect(find.text('+998'), findsOneWidget);
  });
}
