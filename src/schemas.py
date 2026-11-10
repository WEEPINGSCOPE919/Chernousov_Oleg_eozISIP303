from pydantic import BaseModel, Field, ConfigDict


# ---------- Справочники ----------

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: str
    role: str


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class StatusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


# ---------- Комментарии ----------

class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    request_id: int
    user_id: int
    text: str
    created_at: str


class CommentCreate(BaseModel):
    user_id: int
    text: str = Field(..., min_length=1)


# ---------- Заявки ----------

class RequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None
    created_at: str
    category_id: int
    status_id: int
    applicant_id: int
    executor_id: int | None
    category: CategoryOut
    status: StatusOut
    applicant: UserOut
    executor: UserOut | None
    comments: list[CommentOut] = []


class RequestCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    category_id: int
    status_id: int
    applicant_id: int
    executor_id: int | None = None


class RequestUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    category_id: int | None = None
    status_id: int | None = None
    executor_id: int | None = None


class StatusChange(BaseModel):
    status_id: int


class AssignExecutor(BaseModel):
    user_id: int


class ErrorResponse(BaseModel):
    detail: str