import decimal

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


class GenreListBaseSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }


class StarListBaseSchema(GenreListBaseSchema):
    pass


class MovieCreateRequestSchema(BaseModel):
    uuid: str
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: float | None
    gross: float | None
    description: str
    price: decimal.Decimal
    certification_id: int

    model_config = {
        "from_attributes": True
    }


class GenreCreateRequestSchema(BaseModel):
    name: str

    model_config = {
        "from_attributes": True
    }


class StarCreateRequestSchema(GenreCreateRequestSchema):
    pass


class MovieCreateResponseSchema(MovieBaseSchema):
    pass


class GenreCreateResponseSchema(GenreListBaseSchema):
    pass


class StarCreateResponseSchema(StarListBaseSchema):
    pass


class MessageResponseSchema(BaseModel):
    message: str
