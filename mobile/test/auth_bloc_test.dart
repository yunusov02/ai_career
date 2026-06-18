import 'package:flutter_test/flutter_test.dart';
import 'package:skillbridge/domain/repositories/career_repository.dart';
import 'package:skillbridge/domain/usecases/verify_otp.dart';
import 'package:skillbridge/presentation/blocs/auth/auth_bloc.dart';
import 'package:skillbridge/presentation/blocs/auth/auth_event.dart';
import 'package:skillbridge/presentation/blocs/auth/auth_state.dart';

class FakeCareerRepository implements CareerRepository {
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class FakeVerifyOtpUseCase extends VerifyOtpUseCase {
  FakeVerifyOtpUseCase(super.repository);

  bool sendOtpShouldSucceed = true;
  bool verifyOtpShouldSucceed = true;
  bool sendOtpShouldThrow = false;
  bool verifyOtpShouldThrow = false;

  @override
  Future<bool> sendOtp(String phoneNumber, {String locale = 'uz'}) async {
    if (sendOtpShouldThrow) throw Exception('API error');
    return sendOtpShouldSucceed;
  }

  @override
  Future<bool> verifyOtp({
    required String phoneNumber,
    required String otp,
    String locale = 'uz',
  }) async {
    if (verifyOtpShouldThrow) throw Exception('API error');
    return verifyOtpShouldSucceed;
  }
}

void main() {
  group('AuthBloc Tests', () {
    late FakeVerifyOtpUseCase useCase;
    late AuthBloc bloc;

    setUp(() {
      final repository = FakeCareerRepository();
      useCase = FakeVerifyOtpUseCase(repository);
      bloc = AuthBloc(verifyOtpUseCase: useCase);
    });

    tearDown(() {
      bloc.close();
    });

    test('initial state is AuthInitial', () {
      expect(bloc.state, const AuthInitial());
    });

    test('SendOtpEvent with invalid phone number emits AuthError', () async {
      bloc.add(const SendOtpEvent('invalid_phone'));
      
      expectLater(
        bloc.stream,
        emits(const AuthError(
          errorKey: 'invalidPhone',
          previousState: AuthInitial(),
        )),
      );
    });

    test('SendOtpEvent with valid phone number sends OTP successfully and emits OtpSent', () async {
      bloc.add(const SendOtpEvent('901234567'));

      expectLater(
        bloc.stream,
        emitsInOrder([
          const OtpSending(),
          const OtpSent('901234567'),
        ]),
      );
    });

    test('SendOtpEvent with API failure emits AuthError', () async {
      useCase.sendOtpShouldSucceed = false;
      bloc.add(const SendOtpEvent('901234567'));

      expectLater(
        bloc.stream,
        emitsInOrder([
          const OtpSending(),
          const AuthError(
            errorKey: 'error',
            previousState: AuthInitial(),
          ),
        ]),
      );
    });

    test('SendOtpEvent with exception emits AuthError', () async {
      useCase.sendOtpShouldThrow = true;
      bloc.add(const SendOtpEvent('901234567'));

      expectLater(
        bloc.stream,
        emitsInOrder([
          const OtpSending(),
          const AuthError(
            errorKey: 'error',
            previousState: AuthInitial(),
          ),
        ]),
      );
    });

    test('VerifyOtpEvent with invalid OTP format emits AuthError', () async {
      // Setup state first to have a valid phone number stored
      bloc.add(const SendOtpEvent('901234567'));
      await bloc.stream.skip(1).first; // Wait until OtpSent is emitted

      bloc.add(const VerifyOtpEvent('123')); // Invalid (must be 6 digits)

      expectLater(
        bloc.stream,
        emits(const AuthError(
          errorKey: 'invalidOtp',
          previousState: OtpSent('901234567'),
        )),
      );
    });

    test('VerifyOtpEvent with correct OTP emits OtpVerified', () async {
      bloc.add(const SendOtpEvent('901234567'));
      await bloc.stream.skip(1).first;

      bloc.add(const VerifyOtpEvent('123456'));

      expectLater(
        bloc.stream,
        emitsInOrder([
          const OtpVerifying(),
          const OtpVerified(),
        ]),
      );
    });

    test('VerifyOtpEvent with incorrect OTP emits AuthError', () async {
      bloc.add(const SendOtpEvent('901234567'));
      await bloc.stream.skip(1).first;

      useCase.verifyOtpShouldSucceed = false;
      bloc.add(const VerifyOtpEvent('123456'));

      expectLater(
        bloc.stream,
        emitsInOrder([
          const OtpVerifying(),
          const AuthError(
            errorKey: 'invalidOtp',
            previousState: OtpSent('901234567'),
          ),
        ]),
      );
    });

    test('ResetAuthEvent returns state to AuthInitial', () async {
      bloc.add(const SendOtpEvent('901234567'));
      await bloc.stream.skip(1).first;

      bloc.add(const ResetAuthEvent());

      expectLater(
        bloc.stream,
        emits(const AuthInitial()),
      );
    });
  });
}
