from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.middlewares.request_id import RequestIDMiddleware


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestIDMiddleware)
