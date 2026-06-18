export interface Roadmap {
  beginner: string[];
  intermediate: string[];
  advanced: string[];
}

export interface Resources {
  books: string[];
  courses: string[];
  youtube_channels: string[];
  websites: string[];
}

export interface RecommendedCareer {
  name: string;
  match_score: number;
  reason: string;
  roadmap: Roadmap;
  resources: Resources;
}

export interface CareerRecommendResponse {
  personality_summary: string;
  strengths: string[];
  weaknesses: string[];
  recommended_careers: RecommendedCareer[];
}

export interface GuideAnalyzeRequest {
  language: 'uz' | 'ru' | 'en';
  interests: string[];
  answers: {
    question: string;
    category: string;
    score: number;
  }[];
}

export type ResourceType = 'book' | 'course' | 'article' | 'video' | 'documentation' | 'community';

export interface LearningResource {
  title: string;
  url: string;
  type: ResourceType;
}

export interface QuizOption {
  id: string;
  text: string;
}

export interface ModuleQuizQuestion {
  id: string;
  question: string;
  options: QuizOption[];
  correct_option_id: string;
  explanation: string;
}

export interface LearningModule {
  id: string;
  title: string;
  description: string;
  duration: string;
  objectives: string[];
  lessons: string[];
  project: string;
  resources: LearningResource[];
  quiz: ModuleQuizQuestion[];
}

export interface LearningPath {
  id?: number;
  career_name: string;
  overview: string;
  total_duration: string;
  modules: LearningModule[];
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ModuleChatResponse {
  answer: string;
  suggested_questions: string[];
}

export interface CareerPathItem {
  id: number;
  slug: string;
  icon: string;
  title: string;
  description: string;
}

export interface GeneratedQuestion {
  id: number;
  text: string;
  category: string;
  interest: string;
}
