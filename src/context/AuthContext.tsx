import { createContext, useContext, useEffect, useState } from 'react';
import { authApi, PlatformUser } from '../api/auth';
import apiClient from '../api/client';
import { useLanguage } from './LanguageContext';

type AuthContextValue = {
  user: PlatformUser | null;
  loading: boolean;
  requestOtp: (phone: string) => Promise<void>;
  verifyOtp: (phone: string, code: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { language } = useLanguage();
  const [user, setUser] = useState<PlatformUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!apiClient.getTokens()) {
      setLoading(false);
      return;
    }
    authApi.me().then(setUser).catch(() => authApi.logout()).finally(() => setLoading(false));
  }, []);

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      requestOtp: async (phone) => { await authApi.requestOtp(phone, language); },
      verifyOtp: async (phone, code) => {
        await authApi.verifyOtp(phone, code, language);
        setUser(await authApi.me());
      },
      logout: () => {
        authApi.logout();
        setUser(null);
      },
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth must be used inside AuthProvider');
  return value;
}
