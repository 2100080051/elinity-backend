from pydantic import BaseModel


class QuestionCardQuery(BaseModel):
    count: int = 25
    
