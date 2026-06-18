import { useEffect, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { careerApi } from '../api';
import { useLanguage } from '../context/LanguageContext';
import { getQuestions, InterestId, ui } from '../data/content';
import { GeneratedQuestion } from '../types';

type Question = GeneratedQuestion;

export function Assessment() {
  const navigate = useNavigate();
  const { language } = useLanguage();
  const t = ui[language];

  const interests: InterestId[] = (() => {
    try {
      return JSON.parse(localStorage.getItem('career_interests') || '[]') as InterestId[];
    } catch {
      return [];
    }
  })();

  const [questions, setQuestions] = useState<Question[]>([]);
  const [loadingQuestions, setLoadingQuestions] = useState(true);
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!interests.length) return;
    setLoadingQuestions(true);
    careerApi
      .generateQuestions({ language, interests })
      .then((data) => {
        if (data && data.length >= 10) {
          setQuestions(data);
        } else {
          setQuestions(getQuestions(language, interests));
        }
      })
      .catch(() => setQuestions(getQuestions(language, interests)))
      .finally(() => setLoadingQuestions(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!interests.length) return <Navigate to="/" replace />;

  if (loadingQuestions) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center px-5">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-slate-200 border-t-teal-700" />
          <h1 className="mt-6 text-2xl font-semibold text-slate-950">
            {language === 'uz' ? 'Savollar tayyorlanmoqda...' : language === 'ru' ? 'Подготовка вопросов...' : 'Preparing questions...'}
          </h1>
          <p className="mt-2 text-slate-500">AI · 25 questions · personalised</p>
        </div>
      </div>
    );
  }

  const current = questions[index];
  if (!current) return null;

  const progress = ((index + 1) / questions.length) * 100;

  const choose = (score: number) => {
    setAnswers((prev) => ({ ...prev, [current.id]: score }));
  };

  const finish = async () => {
    if (Object.keys(answers).length !== questions.length) return;
    setSubmitting(true);
    setError('');
    try {
      const result = await careerApi.analyzeGuide({
        language,
        interests,
        answers: questions.map((q) => ({
          question: q.text,
          category: q.category,
          score: answers[q.id],
        })),
      });
      localStorage.setItem('career_result', JSON.stringify(result));
      navigate('/results');
    } catch {
      setError(t.error);
      setSubmitting(false);
    }
  };

  if (submitting) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center px-5">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-slate-200 border-t-teal-700" />
          <h1 className="mt-6 text-2xl font-semibold text-slate-950">{t.analyzing}</h1>
          <p className="mt-2 text-slate-500">Top 3 · Roadmap · Resources</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-5 py-10 lg:py-16">
      <div className="mb-10">
        <div className="mb-3 flex items-center justify-between text-sm font-semibold">
          <span className="text-teal-700">{t.question} {index + 1} {t.of} {questions.length}</span>
          <span className="text-slate-400">{Math.round(progress)}%</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-slate-200">
          <div className="h-full rounded-full bg-teal-700 transition-all" style={{ width: `${progress}%` }} />
        </div>
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-10">
        <p className="text-sm font-medium text-slate-500">{t.assessmentTitle}</p>
        <h1 className="mt-4 min-h-32 text-2xl font-semibold leading-10 text-slate-950 sm:text-3xl">{current.text}</h1>
        <p className="mt-2 text-sm text-slate-500">{t.assessmentText}</p>

        <div className="mt-10 grid grid-cols-5 gap-2 sm:gap-3">
          {[1, 2, 3, 4, 5].map((score) => (
            <button
              key={score}
              onClick={() => choose(score)}
              className={`h-14 rounded-xl border text-lg font-semibold transition ${
                answers[current.id] === score
                  ? 'border-teal-700 bg-teal-700 text-white'
                  : 'border-slate-200 bg-slate-50 text-slate-700 hover:border-teal-600'
              }`}
            >
              {score}
            </button>
          ))}
        </div>
        <div className="mt-3 flex justify-between text-xs text-slate-400">
          <span>{t.disagree}</span>
          <span>{t.agree}</span>
        </div>
      </div>

      {error && <p className="mt-5 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</p>}

      <div className="mt-7 flex justify-between">
        <button
          onClick={() => setIndex((v) => Math.max(0, v - 1))}
          disabled={index === 0}
          className="rounded-xl px-5 py-3 font-semibold text-slate-600 hover:bg-slate-100 disabled:opacity-30"
        >
          ← {t.back}
        </button>
        {index < questions.length - 1 ? (
          <button
            onClick={() => setIndex((v) => v + 1)}
            disabled={!answers[current.id]}
            className="rounded-xl bg-slate-950 px-6 py-3 font-semibold text-white hover:bg-teal-800 disabled:opacity-30"
          >
            {t.next} →
          </button>
        ) : (
          <button
            onClick={finish}
            disabled={Object.keys(answers).length !== questions.length}
            className="rounded-xl bg-teal-700 px-6 py-3 font-semibold text-white hover:bg-teal-800 disabled:opacity-30"
          >
            {t.analyze} →
          </button>
        )}
      </div>
    </div>
  );
}

export default Assessment;
