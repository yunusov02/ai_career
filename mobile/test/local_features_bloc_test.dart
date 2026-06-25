import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:skillbridge/presentation/blocs/local_features/local_features_bloc.dart';
import 'package:skillbridge/presentation/blocs/local_features/local_features_event.dart';
import 'package:skillbridge/presentation/blocs/local_features/local_features_state.dart';

class FakeSecureStorage implements FlutterSecureStorage {
  final Map<String, String> _data = {};

  @override
  Future<String?> read({
    required String key,
    AppleOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    AppleOptions? mOptions,
    WindowsOptions? wOptions,
  }) async {
    return _data[key];
  }

  @override
  Future<void> write({
    required String key,
    required String? value,
    AppleOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    AppleOptions? mOptions,
    WindowsOptions? wOptions,
  }) async {
    if (value == null) {
      _data.remove(key);
    } else {
      _data[key] = value;
    }
  }

  @override
  Future<void> delete({
    required String key,
    AppleOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    AppleOptions? mOptions,
    WindowsOptions? wOptions,
  }) async {
    _data.remove(key);
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  group('LocalFeaturesBloc Tests', () {
    late FakeSecureStorage storage;
    late LocalFeaturesBloc bloc;

    setUp(() {
      storage = FakeSecureStorage();
      bloc = LocalFeaturesBloc(storage: storage);
    });

    tearDown(() {
      bloc.close();
    });

    test('initial state has empty fields', () {
      expect(bloc.state, const LocalFeaturesState());
      expect(bloc.state.level, 1);
      expect(bloc.state.currentLevelProgressXp, 0);
      expect(bloc.state.nextLevelXp, 500);
    });

    test('AddXpEvent when no userId is set saves to default and updates state', () async {
      bloc.add(const AddXpEvent(50));
      
      await expectLater(
        bloc.stream,
        emits(const LocalFeaturesState(xp: 50)),
      );

      final savedDefaultXp = await storage.read(key: 'user_default_xp');
      expect(savedDefaultXp, '50');
    });

    test('LoadLocalFeaturesEvent merges offline guest default data into logged-in user', () async {
      // 1. Setup guest data
      await storage.write(key: 'user_default_xp', value: '75');
      await storage.write(key: 'user_default_badges', value: jsonEncode(['first_badge']));
      await storage.write(key: 'user_default_pomodoro_sessions', value: '2');
      await storage.write(key: 'user_default_total_minutes', value: '50');
      await storage.write(key: 'user_default_notes', value: jsonEncode({'module_1': 'Guest note'}));
      await storage.write(key: 'user_default_checklist', value: jsonEncode({'task_1': true}));

      // 2. Setup existing user data
      await storage.write(key: 'user_user123_xp', value: '100');
      await storage.write(key: 'user_user123_badges', value: jsonEncode(['old_badge']));

      // 3. Dispatch load
      bloc.add(const LoadLocalFeaturesEvent('user123'));

      await expectLater(
        bloc.stream,
        emitsInOrder([
          const LocalFeaturesState(userId: 'user123', isLoading: true),
          const LocalFeaturesState(
            userId: 'user123',
            xp: 175,
            unlockedBadges: ['old_badge', 'first_badge'],
            pomodoroSessions: 2,
            totalMinutesStudied: 50,
            notes: {'module_1': 'Guest note'},
            checklist: {'task_1': true},
            isLoading: false,
          ),
        ]),
      );

      // Verify guest data is wiped out
      expect(await storage.read(key: 'user_default_xp'), isNull);
      expect(await storage.read(key: 'user_default_badges'), isNull);
      expect(await storage.read(key: 'user_default_pomodoro_sessions'), isNull);
      expect(await storage.read(key: 'user_default_total_minutes'), isNull);
      expect(await storage.read(key: 'user_default_notes'), isNull);
      expect(await storage.read(key: 'user_default_checklist'), isNull);

      // Verify merged data is stored under user key
      expect(await storage.read(key: 'user_user123_xp'), '175');
      expect(jsonDecode((await storage.read(key: 'user_user123_badges'))!), containsAll(['old_badge', 'first_badge']));
    });

    test('AddPomodoroSessionEvent updates focus stats and saves to storage', () async {
      bloc.add(const AddPomodoroSessionEvent(25));

      await expectLater(
        bloc.stream,
        emits(const LocalFeaturesState(
          pomodoroSessions: 1,
          totalMinutesStudied: 25,
        )),
      );

      expect(await storage.read(key: 'user_default_pomodoro_sessions'), '1');
      expect(await storage.read(key: 'user_default_total_minutes'), '25');
    });

    test('Level calculations are correct', () {
      var state = const LocalFeaturesState(xp: 499);
      expect(state.level, 1);
      expect(state.currentLevelProgressXp, 499);
      expect(state.nextLevelXp, 500);

      state = const LocalFeaturesState(xp: 500);
      expect(state.level, 2);
      expect(state.currentLevelProgressXp, 0);
      expect(state.nextLevelXp, 1000);

      state = const LocalFeaturesState(xp: 1200);
      expect(state.level, 3);
      expect(state.currentLevelProgressXp, 200);
      expect(state.nextLevelXp, 1500);
    });
  });
}
