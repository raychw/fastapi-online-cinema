from pydantic import BaseModel


class MovieBaseSchema(BaseModel):
    id: int
    uuid: str
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: float | None
    gross: float | None
    description: str
    price: float | None
    certification_id: int

    model_config = {
        "from_attributes": True
    }


class MovieListBaseSchema(BaseModel):
    id: int
    uuid: str
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: float | None
    price: float | None


    model_config = {
        "from_attributes": True
    }
