import { Link, useLocation } from 'react-router-dom';
import { Language, useLanguage } from '../../context/LanguageContext';
import { ui } from '../../data/content';
import { useAuth } from '../../context/AuthContext';

export function Navbar() {
  const location = useLocation();
  const { language, setLanguage } = useLanguage();
  const t = ui[language];
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-5 lg:px-8">
        <Link to="/" className="flex items-center gap-3">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-700 font-bold text-white">C</span>
          <span className="text-lg font-semibold tracking-tight text-slate-950">SkillBridge</span>
        </Link>

        <nav className="hidden items-center gap-6 text-sm font-medium sm:flex">
          <Link className={location.pathname === '/' ? 'text-teal-700' : 'text-slate-500 hover:text-slate-950'} to="/">{t.navHome}</Link>
          <Link className={location.pathname === '/assessment' ? 'text-teal-700' : 'text-slate-500 hover:text-slate-950'} to="/assessment">{t.navAssessment}</Link>
          {localStorage.getItem('skillbridge_learning_path') && (
            <Link className={location.pathname.startsWith('/learning') ? 'text-teal-700' : 'text-slate-500 hover:text-slate-950'} to="/learning">{t.myPath}</Link>
          )}
          {user && <Link className={location.pathname === '/history' ? 'text-teal-700' : 'text-slate-500 hover:text-slate-950'} to="/history">History</Link>}
        </nav>

        <div className="flex items-center gap-3">
          <div className="flex rounded-lg border border-slate-200 bg-slate-50 p-1">
            {(['uz', 'ru', 'en'] as Language[]).map((item) => (
              <button
                key={item}
                onClick={() => setLanguage(item)}
                className={`rounded-md px-2.5 py-1 text-xs font-semibold uppercase ${
                  language === item ? 'bg-white text-slate-950 shadow-sm' : 'text-slate-400'
                }`}
              >
                {item}
              </button>
            ))}
          </div>
          {user ? (
            <button onClick={logout} className="hidden text-sm font-semibold text-slate-500 sm:block">Logout</button>
          ) : (
            <Link to="/login" className="text-sm font-semibold text-teal-700">Kirish</Link>
          )}
        </div>
      </div>
    </header>
  );
}

export default Navbar;
