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


class DeleteQuestion(BaseModel):
    id: int

class NewChunk(BaseModel):
    text: str

class EditChunk(BaseModel):
    id: int
    text: str
