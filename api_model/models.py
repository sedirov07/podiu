from pydantic import BaseModel


class TextToAnswer(BaseModel): 
    question: str


class NewQuestion(BaseModel):
    question: str
    answer: str


class EditQuestion(BaseModel):
    id: int
    question: str
    answer: str


class EditKeywords(BaseModel):
    id: int
    keywords: str


class DeleteQuestion(BaseModel):
    id: int
