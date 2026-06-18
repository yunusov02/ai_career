"""Public career guide request schemas."""

from typing import List, Literal

from pydantic import BaseModel, Field


class GuideAnswer(BaseModel):
    question: str = Field(..., min_length=3)
    category: str = Field(..., min_length=2)
    score: int = Field(..., ge=1, le=5)


class GuideAnalyzeRequest(BaseModel):
    language: Literal["en", "ru", "uz"] = "en"
    interests: List[str] = Field(..., min_length=1, max_length=5)
    answers: List[GuideAnswer] = Field(..., min_length=25, max_length=25)


class LearningPathRequest(BaseModel):
    language: Literal["en", "ru", "uz"] = "en"
    career_name: str = Field(..., min_length=2, max_length=150)
    career_reason: str = Field(default="", max_length=2000)


class LearningResource(BaseModel):
    title: str
    url: str
    type: Literal["book", "course", "article", "video", "documentation", "community"]


class QuizOption(BaseModel):
    id: str
    text: str


class ModuleQuizQuestion(BaseModel):
    id: str
    question: str
    options: List[QuizOption] = Field(..., min_length=2, max_length=5)
    correct_option_id: str
    explanation: str


class LearningModule(BaseModel):
    id: str
    title: str
    description: str
    duration: str
    objectives: List[str] = Field(..., min_length=2)
    lessons: List[str] = Field(..., min_length=3)
    project: str
    resources: List[LearningResource] = Field(..., min_length=2)
    quiz: List[ModuleQuizQuestion] = Field(..., min_length=5, max_length=7)


class LearningPathResponse(BaseModel):
    id: int | None = None
    career_name: str
    overview: str
    total_duration: str
    modules: List[LearningModule] = Field(..., min_length=5)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)


class ModuleChatRequest(BaseModel):
    learning_path_id: int | None = None
    module_id: str = Field(default="", max_length=160)
    language: Literal["en", "ru", "uz"] = "en"
    career_name: str = Field(..., min_length=2, max_length=150)
    module_title: str = Field(..., min_length=2, max_length=200)
    module_context: str = Field(..., min_length=3, max_length=6000)
    messages: List[ChatMessage] = Field(..., min_length=1, max_length=20)


class ModuleChatResponse(BaseModel):
    answer: str
    suggested_questions: List[str] = Field(default_factory=list, max_length=3)


class ModuleProgressRequest(BaseModel):
    completed: bool = True


class CareerPathOut(BaseModel):
    id: int
    slug: str
    icon: str
    title: str
    description: str


class GenerateQuestionsRequest(BaseModel):
    language: Literal["en", "ru", "uz"] = "en"
    interests: List[str] = Field(..., min_length=1, max_length=5)


class GeneratedQuestion(BaseModel):
    id: int
    text: str
    category: str
    interest: str
