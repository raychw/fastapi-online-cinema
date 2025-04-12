import decimal
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Integer,
    String,
    Text,
    Float,
    Numeric,
    ForeignKey,
    UniqueConstraint
)

from online_cinema.database import Base


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    uuid: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        unique=True
    )
    name: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
        unique=True
    )
    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    time: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    imdb: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    votes: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    meta_score: Mapped[Optional[float]] = mapped_column(
        Float,
    )
    gross: Mapped[Optional[float]] = mapped_column(
        Float,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    price: Mapped[decimal.Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    certification_id: Mapped[int] = mapped_column(
        ForeignKey("certifications.id", ON_DELETE="CASCADE"),
        nullable=False
    )

    certification: Mapped["Certification"] = relationship(
        "Certification",
        back_populates="movies"
    )
    genres: Mapped[List["Genre"]] = relationship(
        "Genre",
        secondary="movie_genres",
        back_populates="movies"
    )
    directors: Mapped[List["Director"]] = relationship(
        "Director",
        secondary="movie_directors",
        back_populates="movies"
    )
    stars: Mapped[List["Star"]] = relationship(
        "Star",
        secondary="movie_stars",
        back_populates="movies"
    )

    __table_args__ = (UniqueConstraint("name", "year", "time"),)

    def __repr__(self):
        return (
            f"<Movie("
            f"id={self.id}, "
            f"uuid={self.uuid}, "
            f"name={self.name}, "
            f"year={self.year}, "
            f"time={self.time}, "
            f"imdb={self.imdb}, "
            f"votes={self.votes}, "
            f"meta_score={self.meta_score}, "
            f"gross={self.gross}, "
            f"description={self.description}, "
            f"price={self.price})>"
        )


class IdNameModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )


class Star(IdNameModel):
    __tablename__ = "stars"

    movies: Mapped[List["Movie"]] = relationship(
        "Movie",
        secondary="movie_stars",
        back_populates="stars"
    )

    def __repr__(self):
        return (
            f"<Star("
            f"id={self.id}, "
            f"name={self.name})>"
        )


class Genre(IdNameModel):
    __tablename__ = "genres"

    movies: Mapped[List["Movie"]] = relationship(
        "Movie",
        secondary="movie_genres",
        back_populates="genres"
    )

    def __repr__(self):
        return (
            f"<Genre("
            f"id={self.id}, "
            f"name={self.name})>"
        )


class Director(IdNameModel):
    __tablename__ = "directors"

    movies: Mapped[List["Movie"]] = relationship(
        "Movie",
        secondary="movie_directors",
        back_populates="directors"
    )

    def __repr__(self):
        return (
            f"<Director("
            f"id={self.id}, "
            f"name={self.name})>"
        )


class Certification(IdNameModel):
    __tablename__ = "certifications"

    movies: Mapped[List["Movie"]] = relationship(
        "Movie",
        back_populates="certification"
    )

    def __repr__(self):
        return (
            f"<Certification("
            f"id={self.id}, "
            f"name={self.name})>"
        )


class MovieStar(Base):
    __tablename__ = "movie_stars"

    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True
    )
    star_id: Mapped[int] = mapped_column(
        ForeignKey("stars.id", ondelete="CASCADE"),
        primary_key=True
    )

    def __repr__(self):
        return (
            f"<MovieStar("
            f"movie_id={self.movie_id}, "
            f"star_id={self.star_id})>"
        )


class MovieGenre(Base):
    __tablename__ = "movie_genres"

    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True
    )
    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True
    )

    def __repr__(self):
        return (
            f"<MovieGenre("
            f"movie_id={self.movie_id}, "
            f"genre_id={self.genre_id})>"
        )


class MovieDirector(Base):
    __tablename__ = "movie_directors"

    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True
    )
    director_id: Mapped[int] = mapped_column(
        ForeignKey("directors.id", ondelete="CASCADE"),
        primary_key=True
    )

    def __repr__(self):
        return (
            f"<MovieDirector("
            f"movie_id={self.movie_id}, "
            f"director_id={self.director_id})>"
        )
