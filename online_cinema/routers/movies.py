from typing import List
from fastapi import APIRouter, Query, Depends
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from online_cinema.database import get_db
from online_cinema.movies.crud import (
    get_movies_list,
    get_movie_by_id,
)
from online_cinema.movies.schemas import (
    MovieBaseSchema,
    MovieListBaseSchema,
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
                "An error occurred during fetching users.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during fetching users."
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


@router.post(
    "/",
    response_model=MovieBaseSchema,
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
async def create_movie():
    """
    Create a new movie if you have the required permissions.
    """
    pass


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
async def update_movie():
    """
    Update a movie if you have the required permissions.
    """
    pass


@router.delete(
    "/{movie_id}",
    # response_model=...,
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
        409: {
            "description":
                "Conflict - "
                "The requested movie was already purchased.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The requested movie was already purchased."
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
async def delete_movie():
    """"
    Delete a movie if you have the required permissions.
    """
    pass


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
    # response_model=...,
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
async def like_movie():
    """
    Like a movie and change votes count.
    """
    pass


@router.post(
    "/{movie_id}/dislike",
    # response_model=...,
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
async def dislike_movie():
    """
    Dislike a movie and change votes count.
    """
    pass


@router.post(
    "/{movie_id}/rate",
    # response_model=...,
    summary="Rate a movie",
    description="Rate a movie in the database",
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
                "An error occurred during rating movie.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during rating movie."
                    }
                }
            },
        },
    }
)
async def rate_movie():
    """
    Rate a movie on a 10-point scale.
    """
    pass
