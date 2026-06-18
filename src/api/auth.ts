import apiClient, { AuthTokens } from './client';

export interface PlatformUser {
  id: number;
  phone_number: string;
  preferred_language: string;
  is_admin: boolean;
  created_at: string;
}

export const authApi = {
  requestOtp(phone_number: string, language: 'uz' | 'ru' | 'en') {
    return apiClient.post<{ message: string; expires_in: number; retry_after: number }>(
      '/auth/request-otp',
      { phone_number, language },
    );
  },
  async verifyOtp(phone_number: string, code: string, language: 'uz' | 'ru' | 'en') {
    const tokens = await apiClient.post<AuthTokens>('/auth/verify-otp', {
      phone_number,
      code,
      language,
    });
    apiClient.setTokens(tokens);
    return tokens;
  },
  me() {
    return apiClient.get<PlatformUser>('/auth/me');
  },
  logout() {
    apiClient.clearTokens();
  },
};
