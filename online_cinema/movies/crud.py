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
