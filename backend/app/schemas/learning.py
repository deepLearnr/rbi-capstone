from pydantic import BaseModel, ConfigDict, Field


class AnswerSubmission(BaseModel):
    question_id: int = Field(gt=0)
    selected_option: int | None = Field(default=None, ge=0)


class AssessmentSubmitRequest(BaseModel):
    answers: list[AnswerSubmission] = Field(min_length=1)


class ProgressUpdateRequest(BaseModel):
    progress_percent: int = Field(ge=0, le=100)


class LearningSectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    section_order: int
