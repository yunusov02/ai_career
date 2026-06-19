const configuredApiUrl = import.meta.env.VITE_API_URL as string | undefined;
const API_BASE_URL = (configuredApiUrl || 'http://localhost:8000/api/v1').replace(/\/$/, '');

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

class ApiClient {
  constructor(private readonly baseUrl: string) {}

  getTokens(): AuthTokens | null {
    try {
      return JSON.parse(localStorage.getItem('skillbridge_tokens') || 'null');
    } catch {
      return null;
    }
  }

  setTokens(tokens: AuthTokens) {
    localStorage.setItem('skillbridge_tokens', JSON.stringify(tokens));
  }

  clearTokens() {
    localStorage.removeItem('skillbridge_tokens');
  }

  private async refresh(): Promise<boolean> {
    const tokens = this.getTokens();
    if (!tokens?.refresh_token) return false;
    const response = await fetch(`${this.baseUrl}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: tokens.refresh_token }),
    });
    if (!response.ok) {
      this.clearTokens();
      return false;
    }
    this.setTokens(await response.json());
    return true;
  }

  async request<T>(endpoint: string, options: RequestInit = {}, retry = true): Promise<T> {
    const tokens = this.getTokens();
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(tokens?.access_token ? { Authorization: `Bearer ${tokens.access_token}` } : {}),
        ...(options.headers as Record<string, string> | undefined),
      },
    });

    if (response.status === 401 && retry && await this.refresh()) {
      return this.request<T>(endpoint, options, false);
    }

    if (!response.ok) {
      const payload = await response.json().catch(() => null);
      const detail = payload?.detail || payload?.error;
      throw new Error(typeof detail === 'string' ? detail : `Request failed (${response.status})`);
    }
    if (response.status === 204) return {} as T;
    return response.json() as Promise<T>;
  }

  get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data === undefined ? undefined : JSON.stringify(data),
    });
  }

  put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data === undefined ? undefined : JSON.stringify(data),
    });
  }

  async *streamPost(
    endpoint: string,
    data: unknown,
    onSuggestedQuestions?: (questions: string[]) => void,
  ): AsyncGenerator<string> {
    const tokens = this.getTokens();
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(tokens?.access_token ? { Authorization: `Bearer ${tokens.access_token}` } : {}),
      },
      body: JSON.stringify(data),
    });
    if (!response.ok || !response.body) {
      throw new Error(`Stream request failed (${response.status})`);
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const payload = line.slice(6).trim();
          if (payload === '[DONE]') return;
          let obj: Record<string, unknown>;
          try {
            obj = JSON.parse(payload) as Record<string, unknown>;
          } catch {
            continue;
          }
          if (typeof obj.chunk === 'string') yield obj.chunk;
          if (typeof obj.error === 'string') throw new Error(obj.error);
          if (Array.isArray(obj.suggested_questions) && onSuggestedQuestions) {
            onSuggestedQuestions(obj.suggested_questions as string[]);
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
export default apiClient;
