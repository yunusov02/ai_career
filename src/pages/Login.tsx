import { FormEvent, useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

const copy = {
  uz: {
    phoneTitle: 'Telefon orqali kirish',
    codeTitle: 'Tasdiqlash kodi',
    phoneText: 'O‘zbekiston telefon raqamingizni kiriting.',
    codeText: 'Hozircha kod backend terminalida SKILLBRIDGE OTP sifatida chiqadi.',
    getCode: 'Kod olish',
    login: 'Kirish',
    changePhone: 'Raqamni o‘zgartirish',
    error: 'Kirishda xatolik yuz berdi',
  },
  ru: {
    phoneTitle: 'Вход по телефону',
    codeTitle: 'Код подтверждения',
    phoneText: 'Введите номер телефона Узбекистана.',
    codeText: 'Пока код выводится в терминале backend как SKILLBRIDGE OTP.',
    getCode: 'Получить код',
    login: 'Войти',
    changePhone: 'Изменить номер',
    error: 'Ошибка входа',
  },
  en: {
    phoneTitle: 'Sign in by phone',
    codeTitle: 'Verification code',
    phoneText: 'Enter your Uzbekistan phone number.',
    codeText: 'For now, the code appears in the backend terminal as SKILLBRIDGE OTP.',
    getCode: 'Get code',
    login: 'Sign in',
    changePhone: 'Change phone number',
    error: 'Authentication failed',
  },
};

export function Login() {
  const { user, requestOtp, verifyOtp } = useAuth();
  const { language } = useLanguage();
  const text = copy[language];
  const navigate = useNavigate();
  const location = useLocation();
  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');
  const [step, setStep] = useState<'phone' | 'code'>('phone');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const from = (location.state as { from?: string } | null)?.from || '/';

  if (user) return <Navigate to={from} replace />;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (step === 'phone') {
        await requestOtp(phone);
        setStep('code');
      } else {
        await verifyOtp(phone, code);
        navigate(from, { replace: true });
      }
    } catch (value) {
      setError(value instanceof Error ? value.message : text.error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md items-center px-5 py-12">
      <form onSubmit={submit} className="w-full rounded-3xl border border-slate-200 bg-white p-7 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wider text-teal-700">SkillBridge</p>
        <h1 className="mt-3 text-3xl font-semibold text-slate-950">
          {step === 'phone' ? text.phoneTitle : text.codeTitle}
        </h1>
        <p className="mt-3 text-sm leading-6 text-slate-500">
          {step === 'phone' ? text.phoneText : text.codeText}
        </p>
        {step === 'phone' ? (
          <input
            value={phone}
            onChange={(event) => setPhone(event.target.value)}
            placeholder="+998 90 123 45 67"
            className="mt-6 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-teal-700"
            required
          />
        ) : (
          <input
            value={code}
            onChange={(event) => setCode(event.target.value.replace(/\D/g, '').slice(0, 6))}
            placeholder="000000"
            inputMode="numeric"
            className="mt-6 w-full rounded-xl border border-slate-300 px-4 py-3 text-center text-2xl tracking-[0.4em] outline-none focus:border-teal-700"
            required
          />
        )}
        {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
        <button
          disabled={loading || (step === 'code' && code.length !== 6)}
          className="mt-5 w-full rounded-xl bg-teal-700 py-3 font-semibold text-white disabled:opacity-50"
        >
          {loading ? '...' : step === 'phone' ? text.getCode : text.login}
        </button>
        {step === 'code' && (
          <button type="button" onClick={() => setStep('phone')} className="mt-3 w-full text-sm text-slate-500">
            {text.changePhone}
          </button>
        )}
      </form>
    </div>
  );
}
