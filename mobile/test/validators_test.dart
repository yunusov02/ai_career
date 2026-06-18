import 'package:flutter_test/flutter_test.dart';
import 'package:skillbridge/core/utils/validators.dart';

void main() {
  group('Validators Utility Tests', () {
    test('isValidPhoneNumber validates Uzbekistan mobile numbers correctly', () {
      // Valid phone numbers (9 digits starting with 3, 5, 7, 8, 9)
      expect(Validators.isValidPhoneNumber('901234567'), true);
      expect(Validators.isValidPhoneNumber('339998877'), true);
      expect(Validators.isValidPhoneNumber('771112233'), true);
      expect(Validators.isValidPhoneNumber('884445566'), true);
      expect(Validators.isValidPhoneNumber('997776655'), true);

      // Cleaned formatting chars
      expect(Validators.isValidPhoneNumber('90-123-45-67'), true);
      expect(Validators.isValidPhoneNumber('(90) 123 45 67'), true);

      // Invalid formats
      expect(Validators.isValidPhoneNumber('12345'), false); // Too short
      expect(Validators.isValidPhoneNumber('9012345678'), false); // Too long
      expect(Validators.isValidPhoneNumber('221234567'), false); // Invalid prefix digit 2
      expect(Validators.isValidPhoneNumber('90123abcd'), false); // Non-digits
    });

    test('isValidOtp validates 6-digit verification code correctly', () {
      expect(Validators.isValidOtp('123456'), true);
      expect(Validators.isValidOtp('000000'), true);
      expect(Validators.isValidOtp('999999'), true);

      expect(Validators.isValidOtp('12345'), false); // Too short
      expect(Validators.isValidOtp('1234567'), false); // Too long
      expect(Validators.isValidOtp('123a56'), false); // Non-digit characters
    });

    test('formatPhoneNumber formats raw 9-digit phone numbers into readable format', () {
      expect(
        Validators.formatPhoneNumber('901234567'),
        '+998 90 123 45 67',
      );
      expect(
        Validators.formatPhoneNumber('339998877'),
        '+998 33 999 88 77',
      );

      // Non-9 digit strings are fallback formats
      expect(
        Validators.formatPhoneNumber('12345'),
        '+998 12345',
      );
    });
  });
}
