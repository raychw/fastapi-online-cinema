from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from online_cinema.movies.models import Movie


async def get_movies_list(
    db: AsyncSession,
    limit: int = 5,
    offset: int = 0
):
    stmt = (
        select(Movie)
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_movie_by_id(db: AsyncSession, movie_id: int):
    stmt = select(Movie).where(Movie.id == movie_id)
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


async def remove_movie(db: AsyncSession, movie_id: int):
    stmt = select(Movie).where(Movie.id == movie_id)
    result = await db.execute(stmt)
    movie = result.scalars().first()

    if not movie:
        return None

    await db.delete(movie)
    await db.commit()
    return movie
