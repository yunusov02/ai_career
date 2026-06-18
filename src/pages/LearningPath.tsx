import { Link, Navigate } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { ui } from '../data/content';
import { LearningPath as LearningPathType } from '../types';

function readProgress(): Record<string, boolean> {
  try {
    return JSON.parse(localStorage.getItem('skillbridge_module_progress') || '{}');
  } catch {
    return {};
  }
}

export function LearningPath() {
  const { language } = useLanguage();
  const t = ui[language];
  const saved = localStorage.getItem('skillbridge_learning_path');
  if (!saved) return <Navigate to="/results" replace />;

  const path: LearningPathType = JSON.parse(saved);
  const progress = readProgress();
  const completedCount = path.modules.filter((module) => progress[module.id]).length;
  const percent = Math.round((completedCount / path.modules.length) * 100);

  return (
    <div className="mx-auto max-w-6xl px-5 py-10 lg:px-8 lg:py-14">
      <section className="rounded-3xl bg-slate-950 p-7 text-white sm:p-10">
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-teal-300">{t.myPath}</p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight">{path.career_name}</h1>
        <p className="mt-4 max-w-3xl leading-7 text-slate-300">{path.overview}</p>
        <div className="mt-8 grid gap-5 sm:grid-cols-3">
          <Stat value={`${path.modules.length}`} label={t.modules} />
          <Stat value={path.total_duration} label="Total duration" />
          <Stat value={`${percent}%`} label={t.completed} />
        </div>
        <div className="mt-6 h-2 overflow-hidden rounded-full bg-white/15">
          <div className="h-full rounded-full bg-teal-400" style={{ width: `${percent}%` }} />
        </div>
      </section>

      <section className="mt-9 grid gap-5 md:grid-cols-2">
        {path.modules.map((module, index) => {
          const done = Boolean(progress[module.id]);
          return (
            <article key={module.id} className="rounded-2xl border border-slate-200 bg-white p-6">
              <div className="flex items-start justify-between gap-4">
                <span className={`flex h-10 w-10 items-center justify-center rounded-xl text-sm font-bold ${
                  done ? 'bg-teal-700 text-white' : 'bg-slate-100 text-slate-500'
                }`}>
                  {done ? '✓' : index + 1}
                </span>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-500">
                  {module.duration}
                </span>
              </div>
              <h2 className="mt-5 text-xl font-semibold text-slate-950">{module.title}</h2>
              <p className="mt-2 min-h-12 text-sm leading-6 text-slate-600">{module.description}</p>
              <div className="mt-5 flex flex-wrap gap-2 text-xs text-slate-500">
                <span className="rounded-md bg-slate-50 px-2 py-1">{module.lessons.length} lessons</span>
                <span className="rounded-md bg-slate-50 px-2 py-1">{module.resources.length} resources</span>
                <span className="rounded-md bg-slate-50 px-2 py-1">{module.quiz.length} quiz questions</span>
              </div>
              <Link
                to={`/learning/${module.id}`}
                className="mt-6 inline-flex rounded-xl bg-slate-950 px-5 py-2.5 text-sm font-semibold text-white hover:bg-teal-800"
              >
                {done ? t.continueLearning : t.openModule} →
              </Link>
            </article>
          );
        })}
      </section>
    </div>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="rounded-xl bg-white/10 p-4">
      <p className="text-xl font-semibold">{value}</p>
      <p className="mt-1 text-xs uppercase tracking-wider text-slate-400">{label}</p>
    </div>
  );
}

export default LearningPath;
