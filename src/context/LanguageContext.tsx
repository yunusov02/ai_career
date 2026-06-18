import { createContext, useContext, useMemo, useState } from 'react';

export type Language = 'uz' | 'ru' | 'en';

type LanguageContextValue = {
  language: Language;
  setLanguage: (language: Language) => void;
};

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>(
    () => (localStorage.getItem('career_language') as Language) || 'uz'
  );

  const value = useMemo(() => ({
    language,
    setLanguage: (nextLanguage: Language) => {
      localStorage.setItem('career_language', nextLanguage);
      setLanguageState(nextLanguage);
    },
  }), [language]);

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) throw new Error('useLanguage must be used within LanguageProvider');
  return context;
}
