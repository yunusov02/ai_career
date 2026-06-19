import apiClient from './client';
import {
  CareerPathItem,
  CareerRecommendResponse,
  ChatMessage,
  GeneratedQuestion,
  GuideAnalyzeRequest,
  LearningPath,
  ModuleChatResponse,
} from '../types';

export const careerApi = {
  getCareerPaths(language: string): Promise<CareerPathItem[]> {
    return apiClient.get<CareerPathItem[]>(`/guide/career-paths?language=${language}`);
  },
  generateQuestions(data: { language: string; interests: string[] }): Promise<GeneratedQuestion[]> {
    return apiClient.post<GeneratedQuestion[]>('/guide/generate-questions', data);
  },
  analyzeGuide(data: GuideAnalyzeRequest): Promise<CareerRecommendResponse> {
    return apiClient.post<CareerRecommendResponse>('/guide/analyze', data);
  },
  createLearningPath(data: {
    language: 'uz' | 'ru' | 'en';
    career_name: string;
    career_reason: string;
  }): Promise<LearningPath> {
    return apiClient.post<LearningPath>('/guide/learning-path', data);
  },
  chatWithTutor(data: {
    language: 'uz' | 'ru' | 'en';
    career_name: string;
    module_title: string;
    module_context: string;
    learning_path_id?: number;
    module_id?: string;
    messages: ChatMessage[];
  }): Promise<ModuleChatResponse> {
    return apiClient.post<ModuleChatResponse>('/guide/chat', data);
  },
  streamChatWithTutor(
    data: {
      language: 'uz' | 'ru' | 'en';
      career_name: string;
      module_title: string;
      module_context: string;
      learning_path_id?: number;
      module_id?: string;
      messages: ChatMessage[];
    },
    onSuggestedQuestions?: (questions: string[]) => void,
  ): AsyncGenerator<string> {
    return apiClient.streamPost('/guide/chat/stream', data, onSuggestedQuestions);
  },
  updateProgress(pathId: number, moduleId: string, completed: boolean) {
    return apiClient.put<Record<string, boolean>>(
      `/guide/learning-path/${pathId}/modules/${moduleId}`,
      { completed },
    );
  },
};

export default careerApi;
