"""FastAPI application (architecture §4.2–4.4)."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, List, Optional

import pandas as pd
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from restaurant_rec.core.config import AppConfig, load_config, repo_root
from restaurant_rec.phases.phase2.catalog_loader import load_catalog
from restaurant_rec.phases.phase2.filter import distinct_cities, distinct_localities
from restaurant_rec.phases.phase3.orchestration import GenerateFn, recommend
from restaurant_rec.phases.phase4.schemas import RecommendRequest, RecommendResponse

if TYPE_CHECKING:
    pass


def create_app(
    *,
    catalog_df: Optional[pd.DataFrame] = None,
    cfg: Optional[AppConfig] = None,
    generate_fn: Optional[GenerateFn] = None,
    serve_web_ui: bool = True,
) -> FastAPI:
    """
    Build the API app.

    If ``catalog_df`` is omitted, the lifespan loads ``paths.processed_catalog`` from config.
    ``generate_fn`` is passed to Phase 3 (set in tests to avoid calling Gemini).

    When ``serve_web_ui`` is True and ``web/index.html`` exists, ``GET /`` serves the UI
    and ``/static/*`` serves ``web/static/``.
    """
    app_cfg = cfg or load_config()
    preloaded = catalog_df
    llm_override = generate_fn

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.cfg = app_cfg
        app.state.generate_fn = llm_override
        if preloaded is not None:
            app.state.catalog = preloaded
        else:
            app.state.catalog = load_catalog(cfg=app_cfg)
        yield

    app = FastAPI(
        title="Restaurant recommendations",
        description="Phase 4 API — catalog filter + Gemini (see /docs)",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health(request: Request) -> dict[str, Any]:
        cat: pd.DataFrame = request.app.state.catalog
        return {"status": "ok", "catalog_rows": len(cat)}

    @app.get("/")
    def serve_root():
        return JSONResponse(
            {
                "service": "restaurant-rec",
                "docs": "/docs",
                "note": "Next.js UI runs on port 3000.",
            }
        )

    @app.get("/api/v1/localities", response_model=List[str])
    def api_localities(request: Request) -> List[str]:
        cat: pd.DataFrame = request.app.state.catalog
        return distinct_localities(cat)

    @app.get("/api/v1/locations", response_model=List[str])
    def api_locations(request: Request) -> List[str]:
        cat: pd.DataFrame = request.app.state.catalog
        return distinct_cities(cat)

    @app.post("/api/v1/recommend", response_model=RecommendResponse)
    def api_recommend(body: RecommendRequest, request: Request) -> RecommendResponse:
        state = request.app.state
        prefs = body.to_user_preferences()
        result = recommend(
            state.catalog,
            prefs,
            cfg=state.cfg,
            generate_fn=state.generate_fn,
        )
        return RecommendResponse.from_result(result)

    return app


# Uvicorn target: ``uvicorn restaurant_rec.phases.phase4.app:app --reload``
app = create_app()
