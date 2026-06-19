import { FormEvent, useMemo, useState } from 'react';
import { Link, Navigate, useParams } from 'react-router-dom';
import { careerApi } from '../api';
import { useLanguage } from '../context/LanguageContext';
import { ui } from '../data/content';
import { Markdown } from '../components/ui/Markdown';
import { ChatMessage, LearningPath, ResourceType } from '../types';

const resourceLabels: Record<ResourceType, string> = {
  book: 'Book',
  course: 'Course',
  article: 'Article',
  video: 'Video',
  documentation: 'Docs',
  community: 'Community',
};

function readJson<T>(key: string, fallback: T): T {
  try {
    return JSON.parse(localStorage.getItem(key) || '') as T;
  } catch {
    return fallback;
  }
}

export function LearningModule() {
  const { moduleId } = useParams<{ moduleId: string }>();
  const { language } = useLanguage();
  const t = ui[language];
  const [path, setPath] = useState<LearningPath | null>(() => (
    readJson<LearningPath | null>('skillbridge_learning_path', null)
  ));
  const module = path?.modules.find((item) => item.id === moduleId);
  const chatKey = `skillbridge_chat_${moduleId}`;
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [quizChecked, setQuizChecked] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>(() => readJson(chatKey, []));
  const [question, setQuestion] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [pathRefreshing, setPathRefreshing] = useState(false);
  const [pathRefreshError, setPathRefreshError] = useState('');
  const [completed, setCompleted] = useState(() => {
    const progress = readJson<Record<string, boolean>>('skillbridge_module_progress', {});
    return moduleId ? Boolean(progress[moduleId]) : false;
  });

  const score = useMemo(() => {
    if (!module) return 0;
    return module.quiz.filter((item) => answers[item.id] === item.correct_option_id).length;
  }, [answers, module]);

  if (!path || !module) return <Navigate to="/learning" replace />;

  const moduleContext = [
    module.description,
    `Objectives: ${module.objectives.join('; ')}`,
    `Lessons: ${module.lessons.join('; ')}`,
    `Project: ${module.project}`,
    module.quiz.length > 0
      ? `Quiz topics: ${module.quiz.map((q) => q.question).join('; ')}`
      : '',
  ].filter(Boolean).join('\n');

  const submitChat = async (
    event: FormEvent | { preventDefault: () => void },
    suggestedQuestion?: string,
  ) => {
    event.preventDefault();
    const content = (suggestedQuestion || question).trim();
    if (!content || chatLoading) return;
    const userMessage: ChatMessage = { role: 'user', content };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setQuestion('');
    setChatLoading(true);
    setStreamingContent('');
    const payload = {
      language,
      career_name: path.career_name,
      module_title: module.title,
      module_context: moduleContext,
      learning_path_id: path.id,
      module_id: module.id,
      messages: nextMessages.slice(-10),
    };
    try {
      let full = '';
      let streamedSuggestions: string[] = [];
      for await (const chunk of careerApi.streamChatWithTutor(payload, (q) => { streamedSuggestions = q; })) {
        full += chunk;
        setStreamingContent(full);
      }
      const updated: ChatMessage[] = [...nextMessages, { role: 'assistant', content: full }];
      setMessages(updated);
      setSuggestions(streamedSuggestions);
      localStorage.setItem(chatKey, JSON.stringify(updated));
    } catch {
      const errorText = language === 'uz'
        ? "Tutor bilan bog'lanib bo'lmadi. Backend va API sozlamalarini tekshiring."
        : language === 'ru'
        ? 'Не удалось связаться с наставником. Проверьте backend и настройки API.'
        : 'Could not reach the tutor. Check the backend and API settings.';
      const updated: ChatMessage[] = [...nextMessages, { role: 'assistant', content: errorText }];
      setMessages(updated);
      localStorage.setItem(chatKey, JSON.stringify(updated));
    } finally {
      setChatLoading(false);
      setStreamingContent(null);
    }
  };

  const completeModule = async () => {
    const progress = readJson<Record<string, boolean>>('skillbridge_module_progress', {});
    progress[module.id] = true;
    localStorage.setItem('skillbridge_module_progress', JSON.stringify(progress));
    if (path.id) {
      await careerApi.updateProgress(path.id, module.id, true);
    }
    setCompleted(true);
  };

  const refreshLearningPath = async () => {
    setPathRefreshing(true);
    setPathRefreshError('');
    try {
      const refreshed = await careerApi.createLearningPath({
        language,
        career_name: path.career_name,
        career_reason: '',
      });
      localStorage.setItem('skillbridge_learning_path', JSON.stringify(refreshed));
      setPath(refreshed);
      setAnswers({});
      setQuizChecked(false);
    } catch (error) {
      setPathRefreshError(error instanceof Error ? error.message : t.error);
    } finally {
      setPathRefreshing(false);
    }
  };

  const staleQuiz = module.quiz.length < 5
    || new Set(module.quiz.map((item) => item.question)).size !== module.quiz.length;

  return (
    <div className="mx-auto max-w-6xl px-5 py-8 lg:px-8 lg:py-12">
      <Link to="/learning" className="text-sm font-semibold text-teal-700">← {t.myPath}</Link>

      <header className="mt-5 rounded-3xl bg-slate-950 p-7 text-white sm:p-9">
        <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-start">
          <div>
            <p className="text-sm text-teal-300">{path.career_name}</p>
            <h1 className="mt-2 text-3xl font-semibold">{module.title}</h1>
            <p className="mt-3 max-w-3xl leading-7 text-slate-300">{module.description}</p>
          </div>
          <span className="shrink-0 rounded-full bg-white/10 px-4 py-2 text-sm">{module.duration}</span>
        </div>
      </header>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.2fr_.8fr]">
        <main className="space-y-6">
          <Section title={t.moduleGoals}>
            <ul className="space-y-3">
              {module.objectives.map((item) => <CheckItem key={item} text={item} />)}
            </ul>
          </Section>

          <Section title={t.lessons}>
            <ol className="space-y-3">
              {module.lessons.map((lesson, index) => (
                <li key={lesson} className="flex gap-3 rounded-xl bg-slate-50 p-4 text-sm text-slate-700">
                  <span className="font-semibold text-teal-700">{index + 1}.</span>{lesson}
                </li>
              ))}
            </ol>
          </Section>

          <Section title={t.practicalProject}>
            <p className="rounded-xl border border-teal-200 bg-teal-50 p-5 leading-7 text-slate-700">{module.project}</p>
          </Section>

          <Section title={t.moduleResources}>
            <div className="grid gap-3 sm:grid-cols-2">
              {module.resources.map((resource) => (
                <a
                  key={resource.url}
                  href={resource.url}
                  target="_blank"
                  rel="noreferrer"
                  className="rounded-xl border border-slate-200 p-4 hover:border-teal-700 hover:bg-teal-50"
                >
                  <p className="text-xs font-semibold uppercase tracking-wider text-teal-700">{resourceLabels[resource.type]}</p>
                  <p className="mt-1 font-medium text-slate-800">{resource.title} ↗</p>
                </a>
              ))}
            </div>
          </Section>

          <Section title={t.moduleTest}>
            {staleQuiz && (
              <div className="mb-6 rounded-xl border border-amber-200 bg-amber-50 p-4">
                <p className="text-sm leading-6 text-amber-900">
                  {language === 'uz'
                    ? 'Bu modul eski test formatida saqlangan. Yangi, mavzuga mos 5 ta testni yuklang.'
                    : language === 'ru'
                    ? 'Этот модуль сохранен в старом формате. Загрузите 5 новых вопросов по теме.'
                    : 'This module uses the old quiz format. Load 5 new topic-specific questions.'}
                </p>
                <button
                  onClick={refreshLearningPath}
                  disabled={pathRefreshing}
                  className="mt-3 rounded-lg bg-amber-900 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
                >
                  {pathRefreshing
                    ? '...'
                    : language === 'uz'
                    ? 'Testlarni yangilash'
                    : language === 'ru'
                    ? 'Обновить тесты'
                    : 'Refresh quizzes'}
                </button>
                {pathRefreshError && <p className="mt-2 text-sm text-red-700">{pathRefreshError}</p>}
              </div>
            )}
            <div className="space-y-6">
              {module.quiz.map((item, questionIndex) => (
                <div key={item.id}>
                  <p className="font-semibold text-slate-900">{questionIndex + 1}. {item.question}</p>
                  <div className="mt-3 grid gap-2">
                    {item.options.map((option) => {
                      const selected = answers[item.id] === option.id;
                      const correct = quizChecked && option.id === item.correct_option_id;
                      const wrong = quizChecked && selected && !correct;
                      return (
                        <button
                          key={option.id}
                          onClick={() => !quizChecked && setAnswers((current) => ({ ...current, [item.id]: option.id }))}
                          className={`rounded-xl border p-3 text-left text-sm ${
                            correct ? 'border-emerald-600 bg-emerald-50' :
                            wrong ? 'border-red-500 bg-red-50' :
                            selected ? 'border-teal-700 bg-teal-50' : 'border-slate-200'
                          }`}
                        >
                          {option.text}
                        </button>
                      );
                    })}
                  </div>
                  {quizChecked && <p className="mt-2 text-sm text-slate-500">{item.explanation}</p>}
                </div>
              ))}
            </div>
            <div className="mt-6 flex flex-wrap items-center gap-4">
              <button
                onClick={() => setQuizChecked(true)}
                disabled={Object.keys(answers).length !== module.quiz.length}
                className="rounded-xl bg-slate-950 px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-40"
              >
                {t.checkAnswers}
              </button>
              {quizChecked && <p className="font-semibold text-teal-700">{t.testResult}: {score}/{module.quiz.length} {t.correct}</p>}
            </div>
          </Section>

          <button
            onClick={completeModule}
            className={`w-full rounded-xl px-6 py-3.5 font-semibold text-white ${completed ? 'bg-emerald-600' : 'bg-teal-700 hover:bg-teal-800'}`}
          >
            {completed ? `✓ ${t.completed}` : t.finishModule}
          </button>
        </main>

        <aside className="h-fit rounded-2xl border border-slate-200 bg-white p-5 lg:sticky lg:top-24">
          <h2 className="text-lg font-semibold text-slate-950">{t.aiTutor}</h2>
          <p className="mt-1 text-sm text-slate-500">{module.title}</p>
          <div className="mt-5 max-h-[520px] space-y-3 overflow-y-auto rounded-xl bg-slate-50 p-3">
            {messages.length === 0 && (
              <p className="p-3 text-sm leading-6 text-slate-500">
                {language === 'uz' ? "Mavzu bo'yicha savol bering yoki mashq so'rang." :
                 language === 'ru' ? 'Задайте вопрос по теме или попросите упражнение.' :
                 'Ask about the topic or request an exercise.'}
              </p>
            )}
            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={`rounded-xl p-3 text-sm ${
                  message.role === 'user'
                    ? 'ml-6 bg-teal-700 leading-6 text-white'
                    : 'mr-4 border border-slate-200 bg-white text-slate-700'
                }`}
              >
                {message.role === 'user' ? (
                  message.content
                ) : (
                  <Markdown content={message.content} />
                )}
              </div>
            ))}
            {streamingContent !== null && (
              <div className="mr-4 rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-700">
                {streamingContent ? <Markdown content={streamingContent} /> : <span className="text-slate-400">...</span>}
              </div>
            )}
            {chatLoading && streamingContent === null && (
              <p className="p-3 text-sm text-slate-400">...</p>
            )}
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {(suggestions.length ? suggestions : language === 'uz'
              ? ['Oddiy misol ber', 'Mashq tuzib ber', 'Meni test qil']
              : language === 'ru'
              ? ['Приведи простой пример', 'Дай упражнение', 'Проведи тест']
              : ['Give a simple example', 'Give me an exercise', 'Quiz me']
            ).map((suggestion) => (
              <button
                key={suggestion}
                onClick={(event) => submitChat(event, suggestion)}
                className="rounded-full border border-slate-200 px-3 py-1.5 text-xs text-slate-600 hover:border-teal-600"
              >
                {suggestion}
              </button>
            ))}
          </div>
          <form onSubmit={submitChat} className="mt-4 flex gap-2">
            <input
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder={t.askTutor}
              className="min-w-0 flex-1 rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-teal-700"
            />
            <button className="rounded-xl bg-teal-700 px-4 text-sm font-semibold text-white">{t.send}</button>
          </form>
        </aside>
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6">
      <h2 className="mb-5 text-xl font-semibold text-slate-950">{title}</h2>
      {children}
    </section>
  );
}

function CheckItem({ text }: { text: string }) {
  return (
    <li className="flex gap-3 text-sm leading-6 text-slate-700">
      <span className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-teal-100 text-xs text-teal-700">✓</span>
      {text}
    </li>
  );
}

export default LearningModule;
