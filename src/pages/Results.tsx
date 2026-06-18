import { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { careerApi } from '../api';
import { useLanguage } from '../context/LanguageContext';
import { ui } from '../data/content';
import { CareerRecommendResponse, RecommendedCareer } from '../types';

function resourceParts(value: string) {
  const match = value.match(/https?:\/\/\S+/);
  return {
    title: value.replace(/—?\s*https?:\/\/\S+/, '').trim(),
    url: match?.[0] || `https://www.google.com/search?q=${encodeURIComponent(value)}`,
  };
}

function improveLegacyReason(
  career: RecommendedCareer,
  results: CareerRecommendResponse,
  language: 'uz' | 'ru' | 'en',
) {
  const legacyStarts = [
    "Bu kasb siz tanlagan asosiy qiziqishlardan biriga mos keladi",
    'Это направление соответствует одному из ваших главных интересов',
    'This path closely matches one of your selected interests',
  ];
  if (!legacyStarts.some((value) => career.reason.startsWith(value))) return career.reason;

  const strengths = results.strengths.slice(0, 3).join(', ');
  if (language === 'uz') {
    return `${career.name} yo'nalishi profilingizdagi “${strengths}” kabi kuchli tomonlarni real loyihalarda ishlatish imkonini beradi. ${career.match_score}% moslik bu kasb faqat qiziqishingizga emas, balki muammoni amaliy yechish va yangi bilimni bosqichma-bosqich o'zlashtirish uslubingizga ham yaqinligini ko'rsatadi. Boshlanishida kasbning asosiy vositalarini o'rganib, har bir mavzuni kichik loyiha bilan mustahkamlang. Keyin portfolio ishlaringizni mutaxassisga ko'rsatib, aynan texnik qarorlar va ish jarayoni bo'yicha fikr oling. Shu usul qiziqishni tekshirilgan ko'nikmaga, ko'nikmani esa ishga tayyor portfolio darajasiga olib chiqadi.`;
  }
  if (language === 'ru') {
    return `Профессия «${career.name}» позволяет применить такие сильные стороны вашего профиля, как «${strengths}», в реальных проектах. Совпадение ${career.match_score}% означает, что направление связано не только с вашим интересом, но и с привычным способом решать задачи и осваивать новые навыки. Начните с основных инструментов профессии и закрепляйте каждую тему небольшим проектом. Затем показывайте работы специалисту и просите оценивать технические решения и сам процесс. Так интерес постепенно превратится в проверяемый навык и убедительное портфолио.`;
  }
  return `${career.name} gives you a practical way to apply profile strengths such as “${strengths}” in real projects. The ${career.match_score}% match reflects more than interest: it also connects with how you solve problems and build new skills step by step. Start with the profession's core tools and reinforce each topic through a small project. Then ask a practitioner to review both the result and your decision-making process. This turns initial interest into demonstrable ability and a portfolio that shows how you work, not only what you completed.`;
}

export function Results() {
  const { language } = useLanguage();
  const navigate = useNavigate();
  const t = ui[language];
  const saved = localStorage.getItem('career_result');
  const [active, setActive] = useState(0);
  const [isBuilding, setIsBuilding] = useState(false);
  const [pathError, setPathError] = useState('');
  if (!saved) return <Navigate to="/" replace />;

  const results: CareerRecommendResponse = JSON.parse(saved);
  const career = results.recommended_careers[active];
  const displayedCareer = {
    ...career,
    reason: improveLegacyReason(career, results, language),
  };

  const buildLearningPath = async () => {
    setIsBuilding(true);
    setPathError('');
    try {
      const path = await careerApi.createLearningPath({
        language,
        career_name: displayedCareer.name,
        career_reason: displayedCareer.reason,
      });
      localStorage.setItem('skillbridge_learning_path', JSON.stringify(path));
      localStorage.setItem('skillbridge_module_progress', JSON.stringify({}));
      navigate('/learning');
    } catch (error) {
      setPathError(error instanceof Error ? error.message : t.error);
      setIsBuilding(false);
    }
  };

  return (
    <div className="bg-[#f7f8f4]">
      <section className="border-b border-slate-200 bg-slate-950 text-white">
        <div className="mx-auto max-w-6xl px-5 py-14 lg:px-8 lg:py-20">
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-300">Career profile</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">{t.resultTitle}</h1>
          <p className="mt-4 max-w-2xl text-lg text-slate-300">{t.resultText}</p>
        </div>
      </section>

      <main className="mx-auto max-w-6xl px-5 py-10 lg:px-8 lg:py-14">
        <section className="grid gap-5 lg:grid-cols-[1.4fr_.6fr]">
          <div className="rounded-2xl border border-slate-200 bg-white p-7">
            <h2 className="text-lg font-semibold text-slate-950">{t.profile}</h2>
            <p className="mt-4 leading-7 text-slate-600">{results.personality_summary}</p>
          </div>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-1">
            <ProfileList title={t.strengths} items={results.strengths} accent="teal" />
            <ProfileList title={t.improve} items={results.weaknesses} accent="amber" />
          </div>
        </section>

        <section className="mt-10">
          <div className="grid gap-4 md:grid-cols-3">
            {results.recommended_careers.map((item, index) => (
              <button
                key={item.name}
                onClick={() => setActive(index)}
                className={`rounded-2xl border p-5 text-left transition ${
                  active === index
                    ? 'border-teal-700 bg-teal-50 ring-2 ring-teal-700/10'
                    : 'border-slate-200 bg-white hover:border-slate-400'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-slate-400">0{index + 1}</span>
                  <span className="rounded-full bg-slate-950 px-3 py-1 text-xs font-semibold text-white">
                    {item.match_score}% {t.match}
                  </span>
                </div>
                <h2 className="mt-7 text-xl font-semibold text-slate-950">{item.name}</h2>
              </button>
            ))}
          </div>
        </section>

        <CareerDetails career={displayedCareer} />

        {pathError && <p className="mt-5 rounded-xl bg-red-50 p-4 text-sm text-red-700">{pathError}</p>}
        <div className="mt-6 flex justify-center">
          <button
            onClick={buildLearningPath}
            disabled={isBuilding}
            className="rounded-xl bg-teal-700 px-7 py-3.5 font-semibold text-white hover:bg-teal-800 disabled:opacity-50"
          >
            {isBuilding ? t.buildingPath : `${t.buildPath} →`}
          </button>
        </div>

        <div className="mt-10 flex justify-center">
          <Link
            to="/"
            onClick={() => localStorage.removeItem('career_result')}
            className="rounded-xl border border-slate-300 bg-white px-6 py-3 font-semibold text-slate-800 hover:border-slate-500"
          >
            ← {t.restart}
          </Link>
        </div>
      </main>
    </div>
  );
}

function ProfileList({ title, items, accent }: { title: string; items: string[]; accent: 'teal' | 'amber' }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6">
      <h2 className="font-semibold text-slate-950">{title}</h2>
      <ul className="mt-4 space-y-3">
        {items.slice(0, 4).map((item) => (
          <li key={item} className="flex gap-3 text-sm leading-6 text-slate-600">
            <span className={`mt-2 h-2 w-2 shrink-0 rounded-full ${accent === 'teal' ? 'bg-teal-600' : 'bg-amber-500'}`} />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

function CareerDetails({ career }: { career: RecommendedCareer }) {
  const { language } = useLanguage();
  const t = ui[language];
  const stages = [
    { title: t.beginner, items: career.roadmap.beginner },
    { title: t.intermediate, items: career.roadmap.intermediate },
    { title: t.advanced, items: career.roadmap.advanced },
  ];
  const resources = [
    ...career.resources.books.map((value) => ({ type: 'Book', value })),
    ...career.resources.courses.map((value) => ({ type: 'Course', value })),
    ...career.resources.youtube_channels.map((value) => ({ type: 'Video', value })),
    ...career.resources.websites.map((value) => ({ type: 'Website', value })),
  ];

  return (
    <section className="mt-6 rounded-3xl border border-slate-200 bg-white p-6 sm:p-9">
      <div className="border-b border-slate-200 pb-8">
        <p className="text-sm font-semibold uppercase tracking-wider text-teal-700">{t.why}</p>
        <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">{career.name}</h2>
        <p className="mt-4 max-w-4xl leading-7 text-slate-600">{career.reason}</p>
      </div>

      <div className="py-8">
        <h3 className="text-xl font-semibold text-slate-950">{t.roadmap}</h3>
        <div className="mt-6 grid gap-5 lg:grid-cols-3">
          {stages.map((stage, stageIndex) => (
            <div key={stage.title} className="rounded-2xl bg-slate-50 p-5">
              <div className="flex items-center gap-3">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-teal-700 text-xs font-bold text-white">
                  {stageIndex + 1}
                </span>
                <h4 className="font-semibold text-slate-950">{stage.title}</h4>
              </div>
              <ol className="mt-5 space-y-4">
                {stage.items.map((item, index) => (
                  <li key={item} className="flex gap-3 text-sm leading-6 text-slate-600">
                    <span className="font-semibold text-slate-400">{index + 1}.</span>{item}
                  </li>
                ))}
              </ol>
            </div>
          ))}
        </div>
      </div>

      <div className="border-t border-slate-200 pt-8">
        <h3 className="text-xl font-semibold text-slate-950">{t.resources}</h3>
        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          {resources.map(({ type, value }) => {
            const resource = resourceParts(value);
            return (
              <a
                key={`${type}-${value}`}
                href={resource.url}
                target="_blank"
                rel="noreferrer"
                className="group flex items-center justify-between rounded-xl border border-slate-200 p-4 hover:border-teal-700 hover:bg-teal-50"
              >
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-teal-700">{type}</p>
                  <p className="mt-1 font-medium text-slate-800">{resource.title}</p>
                </div>
                <span className="ml-4 text-slate-400 group-hover:text-teal-700">↗</span>
              </a>
            );
          })}
        </div>
      </div>
    </section>
  );
}

export default Results;
