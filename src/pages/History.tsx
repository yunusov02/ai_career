import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { historyApi, UserHistory } from '../api/history';
import { useLanguage } from '../context/LanguageContext';

const copy = {
  uz: { title: 'Tarix', assessments: 'Assessment natijalari', paths: 'Learning pathlar', open: 'Natijani ochish', resume: 'Davom ettirish', modules: 'modul', empty: 'Hali ma’lumot yo‘q.' },
  ru: { title: 'История', assessments: 'Результаты тестов', paths: 'Учебные планы', open: 'Открыть результат', resume: 'Продолжить', modules: 'модулей', empty: 'Данных пока нет.' },
  en: { title: 'History', assessments: 'Assessment results', paths: 'Learning paths', open: 'Open result', resume: 'Continue', modules: 'modules', empty: 'No data yet.' },
};

export function History() {
  const { language } = useLanguage();
  const text = copy[language];
  const [history, setHistory] = useState<UserHistory | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    historyApi.getAll().then(setHistory).catch((value) => setError(value.message));
  }, []);

  const openAssessment = (result: UserHistory['assessments'][number]['result']) => {
    localStorage.setItem('career_result', JSON.stringify(result));
  };

  const openPath = (item: UserHistory['learning_paths'][number]) => {
    localStorage.setItem('skillbridge_learning_path', JSON.stringify({ ...item.path, id: item.id }));
    localStorage.setItem('skillbridge_module_progress', JSON.stringify(item.progress));
  };

  if (error) return <p className="mx-auto max-w-4xl p-8 text-red-700">{error}</p>;
  if (!history) return <div className="min-h-[60vh]" />;

  return (
    <div className="mx-auto max-w-6xl px-5 py-12 lg:px-8">
      <h1 className="text-4xl font-semibold text-slate-950">{text.title}</h1>
      <h2 className="mt-10 text-xl font-semibold">{text.assessments}</h2>
      <div className="mt-4 grid gap-4 md:grid-cols-2">
        {!history.assessments.length && <p className="text-slate-500">{text.empty}</p>}
        {history.assessments.map((item) => (
          <article key={item.id} className="rounded-2xl border border-slate-200 bg-white p-5">
            <p className="text-sm text-slate-400">{new Date(item.created_at).toLocaleString()}</p>
            <h3 className="mt-3 text-lg font-semibold">{item.result.recommended_careers[0]?.name}</h3>
            <p className="mt-2 text-sm text-slate-500">{item.interests.join(', ')}</p>
            <Link onClick={() => openAssessment(item.result)} to="/results" className="mt-4 inline-block font-semibold text-teal-700">
              {text.open} →
            </Link>
          </article>
        ))}
      </div>
      <h2 className="mt-10 text-xl font-semibold">{text.paths}</h2>
      <div className="mt-4 grid gap-4 md:grid-cols-2">
        {!history.learning_paths.length && <p className="text-slate-500">{text.empty}</p>}
        {history.learning_paths.map((item) => (
          <article key={item.id} className="rounded-2xl border border-slate-200 bg-white p-5">
            <p className="text-sm text-slate-400">{new Date(item.updated_at).toLocaleString()}</p>
            <h3 className="mt-3 text-lg font-semibold">{item.career_name}</h3>
            <p className="mt-2 text-sm text-slate-500">{Object.values(item.progress).filter(Boolean).length}/{item.path.modules.length} {text.modules}</p>
            <Link onClick={() => openPath(item)} to="/learning" className="mt-4 inline-block font-semibold text-teal-700">
              {text.resume} →
            </Link>
          </article>
        ))}
      </div>
    </div>
  );
}
