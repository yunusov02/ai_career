import apiClient from './client';
import { CareerRecommendResponse, LearningPath } from '../types';

export interface UserHistory {
  assessments: {
    id: number;
    language: string;
    interests: string[];
    result: CareerRecommendResponse;
    created_at: string;
  }[];
  learning_paths: {
    id: number;
    career_name: string;
    path: LearningPath;
    progress: Record<string, boolean>;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  }[];
}

export const historyApi = {
  getAll() {
    return apiClient.get<UserHistory>('/history');
  },
};
