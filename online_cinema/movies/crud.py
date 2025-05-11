from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from online_cinema.movies.models import (
    Movie,
    Genre,
    Star,
)


async def get_movies_list(
    db: AsyncSession,
    year: int | None = None,
    imdb_min: float | None = None,
    imdb_max: float | None = None,
    limit: int = 5,
    offset: int = 0,
):
    stmt = select(Movie)

    conditions = []
    if year is not None:
        conditions.append(Movie.year == year)
    if imdb_min is not None:
        conditions.append(Movie.imdb >= imdb_min)
    if imdb_max is not None:
        conditions.append(Movie.imdb <= imdb_max)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_genres_list(
    db: AsyncSession,
    limit: int = 5,
    offset: int = 0
):
    stmt = (
        select(Genre)
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_stars_list(
    db: AsyncSession,
    limit: int = 5,
    offset: int = 0
):
    stmt = (
        select(Star)
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_movie_by_id(db: AsyncSession, movie_id: int):
    stmt = select(Movie).where(Movie.id == movie_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_genre_by_id(db: AsyncSession, genre_id: int):
    stmt = select(Genre).where(Genre.id == genre_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_star_by_id(db: AsyncSession, star_id: int):
    stmt = select(Star).where(Star.id == star_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_new_movie(db: AsyncSession, movie_data: dict):
    new_movie = Movie(
        uuid=movie_data["uuid"],
        name=movie_data["name"],
        year=movie_data["year"],
        time=movie_data["time"],
        imdb=movie_data["imdb"],
        votes=movie_data["votes"],
        meta_score=movie_data["meta_score"],
        gross=movie_data["gross"],
        description=movie_data["description"],
        price=movie_data["price"],
        certification_id=movie_data["certification_id"],
    )

    db.add(new_movie)
    await db.commit()
    await db.refresh(new_movie)
    return new_movie


async def create_new_genre(db: AsyncSession, genre_data: dict):
    new_genre = Genre(
        name=genre_data["name"],
    )

    db.add(new_genre)
    await db.commit()
    await db.refresh(new_genre)
    return new_genre


async def create_new_star(db: AsyncSession, star_data: dict):
    new_star = Star(
        name=star_data["name"],
    )

    db.add(new_star)
    await db.commit()
    await db.refresh(new_star)
    return new_star


async def update_movie(db: AsyncSession, movie_id: int, movie_data: dict):
    stmt = select(Movie).where(Movie.id == movie_id)
    result = await db.execute(stmt)
    movie = result.scalars().first()

    if not movie:
        return None

    for key, value in movie_data.items():
        setattr(movie, key, value)

    await db.commit()
    await db.refresh(movie)
    return movie


async def update_genre(db: AsyncSession, genre_id: int, genre_data: dict):
    stmt = select(Genre).where(Genre.id == genre_id)
    result = await db.execute(stmt)
    genre = result.scalars().first()

    if not genre:
        return None

    for key, value in genre_data.items():
        setattr(genre, key, value)

    await db.commit()
    await db.refresh(genre)
    return genre


async def update_star(db: AsyncSession, star_id: int, star_data: dict):
    stmt = select(Star).where(Star.id == star_id)
    result = await db.execute(stmt)
    star = result.scalars().first()

    if not star:
        return None

    for key, value in star_data.items():
        setattr(star, key, value)

    await db.commit()
    await db.refresh(star)
    return star


async def remove_movie(db: AsyncSession, movie_id: int):
    stmt = select(Movie).where(Movie.id == movie_id)
    result = await db.execute(stmt)
    movie = result.scalars().first()

    if not movie:
        return None

    await db.delete(movie)
    await db.commit()
    return movie


async def remove_genre(db: AsyncSession, genre_id: int):
    stmt = select(Genre).where(Genre.id == genre_id)
    result = await db.execute(stmt)
    genre = result.scalars().first()

    if not genre:
        return None

    await db.delete(genre)
    await db.commit()
    return genre


async def remove_star(db: AsyncSession, star_id: int):
    stmt = select(Star).where(Star.id == star_id)
    result = await db.execute(stmt)
    star = result.scalars().first()

    if not star:
        return None

    await db.delete(star)
    await db.commit()
    return star
