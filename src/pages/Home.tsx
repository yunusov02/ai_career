import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { careerApi } from '../api';
import { useLanguage } from '../context/LanguageContext';
import { interests as staticInterests, ui } from '../data/content';
import { CareerPathItem } from '../types';

type SelectableItem = { slug: string; icon: string; title: string; description: string };

function toSelectable(item: CareerPathItem): SelectableItem {
  return { slug: item.slug, icon: item.icon, title: item.title, description: item.description };
}

function staticToSelectable(language: string): SelectableItem[] {
  return staticInterests.map((item) => ({
    slug: item.id,
    icon: item.icon,
    title: item.title[language as 'uz' | 'ru' | 'en'] ?? item.title.en,
    description: item.description[language as 'uz' | 'ru' | 'en'] ?? item.description.en,
  }));
}

export function Home() {
  const navigate = useNavigate();
  const { language } = useLanguage();
  const t = ui[language];

  const [paths, setPaths] = useState<SelectableItem[]>(() => staticToSelectable(language));
  const [selected, setSelected] = useState<string[]>(() => {
    try {
      return JSON.parse(localStorage.getItem('career_interests') || '[]') as string[];
    } catch {
      return [];
    }
  });

  // Fetch canonical paths from API; fall back to static list on error
  useEffect(() => {
    careerApi.getCareerPaths(language)
      .then((data) => setPaths(data.map(toSelectable)))
      .catch(() => setPaths(staticToSelectable(language)));
  }, [language]);

  const toggleInterest = (slug: string) => {
    setSelected((current) => {
      if (current.includes(slug)) return current.filter((item) => item !== slug);
      if (current.length === 5) return current;
      return [...current, slug];
    });
  };

  const startAssessment = () => {
    if (!selected.length) return;
    localStorage.setItem('career_interests', JSON.stringify(selected));
    localStorage.removeItem('career_result');
    navigate('/assessment');
  };

  return (
    <div>
      <section className="border-b border-slate-200 bg-[#f7f8f4]">
        <div className="mx-auto grid max-w-6xl gap-12 px-5 py-16 lg:grid-cols-[1.1fr_.9fr] lg:px-8 lg:py-24">
          <div className="flex flex-col justify-center">
            <p className="mb-5 text-sm font-semibold uppercase tracking-[0.18em] text-teal-700">{t.heroEyebrow}</p>
            <h1 className="max-w-3xl text-4xl font-semibold leading-[1.08] tracking-tight text-slate-950 sm:text-6xl">
              {t.heroTitle}
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">{t.heroText}</p>
          </div>
          <div className="rounded-3xl bg-slate-950 p-7 text-white shadow-xl shadow-slate-900/10 sm:p-9">
            <p className="text-sm font-medium text-teal-300">25 questions · 10–12 min</p>
            <div className="mt-8 space-y-6">
              {t.benefits.map((benefit, index) => (
                <div key={benefit} className="flex gap-4">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-teal-400 text-sm font-bold text-slate-950">
                    {index + 1}
                  </span>
                  <p className="pt-1 text-slate-200">{benefit}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-16 lg:px-8 lg:py-20">
        <div className="mb-9 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <h2 className="text-3xl font-semibold tracking-tight text-slate-950">{t.selectTitle}</h2>
            <p className="mt-2 text-slate-600">{t.selectText}</p>
          </div>
          <p className="text-sm font-semibold text-teal-700">{selected.length}/5 {t.selected}</p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {paths.map((path) => {
            const active = selected.includes(path.slug);
            return (
              <button
                key={path.slug}
                type="button"
                onClick={() => toggleInterest(path.slug)}
                className={`min-h-44 rounded-2xl border p-5 text-left transition ${
                  active
                    ? 'border-teal-700 bg-teal-50 ring-2 ring-teal-700/10'
                    : 'border-slate-200 bg-white hover:-translate-y-0.5 hover:border-slate-400 hover:shadow-lg'
                }`}
              >
                <div className="flex items-start justify-between">
                  <span className="text-sm font-semibold text-slate-400">{path.icon}</span>
                  <span className={`flex h-6 w-6 items-center justify-center rounded-full border text-xs ${
                    active ? 'border-teal-700 bg-teal-700 text-white' : 'border-slate-300 text-transparent'
                  }`}>✓</span>
                </div>
                <h3 className="mt-8 text-lg font-semibold text-slate-950">{path.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-500">{path.description}</p>
              </button>
            );
          })}
        </div>

        <div className="mt-10 flex justify-center">
          <button
            onClick={startAssessment}
            disabled={!selected.length}
            className="rounded-xl bg-slate-950 px-7 py-3.5 font-semibold text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:opacity-35"
          >
            {t.continue} <span className="ml-2">→</span>
          </button>
        </div>
      </section>
    </div>
  );
}

export default Home;
