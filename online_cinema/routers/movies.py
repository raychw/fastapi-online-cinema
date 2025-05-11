from typing import List
from fastapi import APIRouter, Query, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from online_cinema.accounts.models import UserModel
from security.utils import require_group
from online_cinema.database import get_db
from online_cinema.movies.crud import (
    get_movies_list,
    create_new_movie,
    get_movie_by_id,
    remove_movie,
    update_movie,
    get_genres_list,
    create_new_genre,
    get_genre_by_id,
    update_genre,
    remove_genre,
    get_stars_list,
    create_new_star,
    get_star_by_id,
    update_star,
    remove_star,
)
from online_cinema.movies.schemas import (
    MovieBaseSchema,
    MovieListBaseSchema,
    MovieCreateRequestSchema,
    MovieCreateResponseSchema,
    MessageResponseSchema,
    GenreListBaseSchema,
    GenreCreateRequestSchema,
    GenreCreateResponseSchema,
    StarListBaseSchema,
    StarCreateRequestSchema,
    StarCreateResponseSchema,
)


router = APIRouter()


@router.get(
    "/",
    response_model=List[MovieListBaseSchema],
    summary="Get list of existing movies",
    description="Get list of existing movies in the database",
    status_code=status.HTTP_200_OK,
    responses={
        500: {
            "description":
                "Internal Server Error - "
                "An error occurred during fetching movies.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during fetching movies."
                    }
                }
            },
        },
    }
)
async def get_movies(
    limit: int = Query(5, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a paginated list of movies.
    """
    movies = await get_movies_list(db, limit, offset)

    try:
        return movies
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/genres",
    response_model=List[GenreListBaseSchema],
    summary="Get list of existing genres",
    description="Get list of existing genres in the database",
    status_code=status.HTTP_200_OK,
    responses={
        500: {
            "description":
                "Internal Server Error - "
                "An error occurred during fetching genres.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during fetching genres."
                    }
                }
            },
        },
    }
)
async def get_genres(
    limit: int = Query(5, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a paginated list of genres.
    """
    genres = await get_genres_list(db, limit, offset)

    try:
        return genres
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/stars",
    response_model=List[StarListBaseSchema],
    summary="Get list of existing stars",
    description="Get list of existing stars in the database",
    status_code=status.HTTP_200_OK,
    responses={
        500: {
            "description":
                "Internal Server Error - "
                "An error occurred during fetching stars.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during fetching stars."
                    }
                }
            },
        },
    }
)
async def get_stars(
    limit: int = Query(5, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a paginated list of stars.
    """
    stars = await get_stars_list(db, limit, offset)

    try:
        return stars
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/",
    response_model=MovieCreateResponseSchema,
    summary="Create a new movie",
    description="Create a new movie in the database",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "description":
                "Bad Request - "
                "The request was invalid or cannot be served.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The request was invalid or cannot be served."
                    }
                }
            },
        },
        500: {
            "description":
                "Internal Server Error - "
                "An error occurred during creating movie.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during creating movie."
                    }
                }
            },
        },
    }
)
async def create_movie(
    movie_data: MovieCreateRequestSchema,
    # user: UserModel = Depends(require_group(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new movie if you have the required permissions.
    """
    movie = await create_new_movie(db, movie_data.model_dump())

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The request was invalid or cannot be served."
        )
    try:
        return MovieCreateResponseSchema.model_validate(movie)
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/genres",
    response_model=GenreCreateResponseSchema,
    summary="Create a new genre",
    description="Create a new genre in the database",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "description":
                "Bad Request - "
                "The request was invalid or cannot be served.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The request was invalid or cannot be served."
                    }
                }
            },
        },
        500: {
            "description":
                "Internal Server Error - "
                "An error occurred during creating genre.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during creating genre."
                    }
                }
            },
        },
    }
)
async def create_genre(
    genre_data: GenreCreateRequestSchema,
    # user: UserModel = Depends(require_group(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new genre if you have the required permissions.
    """
    genre = await create_new_genre(db, genre_data.model_dump())

    if not genre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The request was invalid or cannot be served."
        )
    try:
        return GenreCreateResponseSchema.model_validate(genre)
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/stars",
    response_model=StarCreateResponseSchema,
    summary="Create a new star",
    description="Create a new star in the database",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "description":
                "Bad Request - "
                "The request was invalid or cannot be served.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The request was invalid or cannot be served."
                    }
                }
            },
        },
        500: {
            "description":
                "Internal Server Error - "
                "An error occurred during creating star.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during creating star."
                    }
                }
            },
        },
    }
)
async def create_star(
    star_data: StarCreateRequestSchema,
    # user: UserModel = Depends(require_group(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new star if you have the required permissions.
    """
    star = await create_new_star(db, star_data.model_dump())

    if not star:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The request was invalid or cannot be served."
        )
    try:
        return StarCreateResponseSchema.model_validate(star)
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{movie_id}",
    response_model=MovieBaseSchema,
    summary="Get movie by ID",
    description="Get movie by ID from the database",
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "description":
                "Not Found - "
                "The requested movie was not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The requested movie was not found."
                    }
                }
            },
        },
        500: {
            "description":
                "Internal Server Error - "
                "An error occurred during fetching movie.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during fetching movie."
                    }
                }
            },
        },
    }
)
async def get_movie(
        movie_id: int,
        db: AsyncSession = Depends(get_db),
):
    """
    Get a movie by its ID.
    """
    movie = await get_movie_by_id(db, movie_id)

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested movie was not found."
        )

    try:
        return movie
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch(
    "/{movie_id}",
    response_model=MovieListBaseSchema,
    summary="Update movie",
    description="Update movie in the database",
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description":
                "Bad Request - "
                "The request was invalid or cannot be served.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The request was invalid or cannot be served."
                    }
                }
            },
        },
        404: {
            "description":
                "Not Found - "
                "The requested movie was not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The requested movie was not found."
                    }
                }
            },
        },
        500: {
            "description":
                "Internal Server Error - "
                "An error occurred during updating movie.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during updating movie."
                    }
                }
            },
        },
    }
)
async def patch_movie(
        movie_id: int,
        movie_data: MovieCreateRequestSchema,
        # user: UserModel = Depends(require_group(["admin"])),
        db: AsyncSession = Depends(get_db),
):
    """
    Update a movie if you have the required permissions.
    """
    existing_movie = await get_movie_by_id(db, movie_id)

    if not existing_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested movie was not found."
        )
    try:
        updated_movie = await update_movie(
            db,
            movie_id,
            movie_data.model_dump()
        )
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    else:
        return MovieListBaseSchema.model_validate(updated_movie)


@router.patch(
    "/genres/{genre_id}",
    response_model=GenreListBaseSchema,
    summary="Update genre",
    description="Update genre in the database",
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description":
                "Bad Request - "
                "The request was invalid or cannot be served.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The request was invalid or cannot be served."
                    }
                }
            },
        },
        404: {
            "description":
                "Not Found - "
                "The requested genre was not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The requested genre was not found."
                    }
                }
            },
        },
        500: {
            "description":
                "Internal Server Error - "
                "An error occurred during updating genre.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during updating genre."
                    }
                }
            },
        },
    }
)
async def patch_genre(
        genre_id: int,
        genre_data: GenreCreateRequestSchema,
        # user: UserModel = Depends(require_group(["admin"])),
        db: AsyncSession = Depends(get_db),
):
    """
    Update a genre if you have the required permissions.
    """
    existing_genre = await get_genre_by_id(db, genre_id)

    if not existing_genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested genre was not found."
        )
    try:
        updated_genre = await update_genre(
            db,
            genre_id,
            genre_data.model_dump()
        )
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    else:
        return GenreListBaseSchema.model_validate(updated_genre)


@router.patch(
    "/stars/{star_id}",
    response_model=StarListBaseSchema,
    summary="Update star",
    description="Update star in the database",
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description":
                "Bad Request - "
                "The request was invalid or cannot be served.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The request was invalid or cannot be served."
                    }
                }
            },
        },
        404: {
            "description":
                "Not Found - "
                "The requested star was not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The requested star was not found."
                    }
                }
            },
        },
        500: {
            "description":
                "Internal Server Error - "
                "An error occurred during updating star.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during updating star."
                    }
                }
            },
        },
    }
)
async def patch_star(
        star_id: int,
        star_data: StarCreateRequestSchema,
        # user: UserModel = Depends(require_group(["admin"])),
        db: AsyncSession = Depends(get_db),
):
    """
    Update a star if you have the required permissions.
    """
    existing_star = await get_star_by_id(db, star_id)

    if not existing_star:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested star was not found."
        )
    try:
        updated_star = await update_star(
            db,
            star_id,
            star_data.model_dump()
        )
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    else:
        return StarListBaseSchema.model_validate(updated_star)


@router.delete(
    "/{movie_id}",
    summary="Delete movie",
    description="Delete movie from the database",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            "description":
                "Not Found - "
                "The requested movie was not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The requested movie was not found."
                    }
                }
            },
        },
        500: {
            "description":
                "Internal Server Error - "
                "An error occurred during deleting movie.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during deleting movie."
                    }
                }
            },
        },
    }
)
async def delete_movie(
        movie_id: int,
        # user: UserModel = Depends(require_group(["admin"])),
        db: AsyncSession = Depends(get_db),
):
    """"
    Delete a movie if you have the required permissions.
    """
    movie = await get_movie_by_id(db, movie_id)

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested movie was not found."
        )

    try:
        await remove_movie(db, movie_id)
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/genres/{genre_id}",
    summary="Delete genre",
    description="Delete genre from the database",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            "description":
                "Not Found - "
                "The requested genre was not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The requested genre was not found."
                    }
                }
            },
        },
        500: {
            "description":
                "Internal Server Error - "
                "An error occurred during deleting genre.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during deleting genre."
                    }
                }
            },
        },
    }
)
async def delete_genre(
        genre_id: int,
        # user: UserModel = Depends(require_group(["admin"])),
        db: AsyncSession = Depends(get_db),
):
    """"
    Delete a genre if you have the required permissions.
    """
    genre = await get_genre_by_id(db, genre_id)

    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested genre was not found."
        )

    try:
        await remove_genre(db, genre_id)
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/stars/{star_id}",
    summary="Delete star",
    description="Delete star from the database",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            "description":
                "Not Found - "
                "The requested star was not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The requested star was not found."
                    }
                }
            },
        },
        500: {
            "description":
                "Internal Server Error - "
                "An error occurred during deleting star.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during deleting star."
                    }
                }
            },
        },
    }
)
async def delete_star(
        star_id: int,
        # user: UserModel = Depends(require_group(["admin"])),
        db: AsyncSession = Depends(get_db),
):
    """"
    Delete a star if you have the required permissions.
    """
    star = await get_star_by_id(db, star_id)

    if not star:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested star was not found."
        )

    try:
        await remove_star(db, star_id)
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/search",
    response_model=MovieListBaseSchema,
    summary="Search movies",
    description="Search movies in the database",
    status_code=status.HTTP_200_OK,
    responses={
        500: {
            "description":
                "Internal Server Error - "
                "An error occurred during searching movies.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during searching movies."
                    }
                }
            },
        },
    }
)
async def search_movies():
    """
    Search for movies by title, description, actors or directors.
    """
    pass


@router.post(
    "/{movie_id}/like",
    response_model=MessageResponseSchema,
    summary="Like a movie",
    description="Like a movie in the database",
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "description":
                "Not Found - "
                "The requested movie was not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The requested movie was not found."
                    }
                }
            },
        },
        500: {
            "description":
                "Internal Server Error - "
                "An error occurred during liking movie.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during liking movie."
                    }
                }
            },
        },
    }
)
async def like_movie(
        movie_id: int,
        db: AsyncSession = Depends(get_db),
):
    """
    Like a movie and change votes count.
    """
    movie = await get_movie_by_id(db, movie_id)

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested movie was not found."
        )
    try:
        movie.votes += 1
        await db.commit()
        await db.refresh(movie)

        return {"message": "Movie liked successfully."}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/{movie_id}/dislike",
    response_model=MessageResponseSchema,
    summary="Dislike a movie",
    description="Dislike a movie in the database",
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "description":
                "Not Found - "
                "The requested movie was not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The requested movie was not found."
                    }
                }
            },
        },
        500: {
            "description":
                "Internal Server Error - "
                "An error occurred during disliking movie.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during disliking movie."
                    }
                }
            },
        },
    }
)
async def dislike_movie(
        movie_id: int,
        db: AsyncSession = Depends(get_db),
):
    """
    Dislike a movie and change votes count.
    """
    movie = await get_movie_by_id(db, movie_id)

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested movie was not found."
        )
    try:
        movie.votes -= 1
        await db.commit()
        await db.refresh(movie)

        return {"message": "Movie disliked successfully."}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
