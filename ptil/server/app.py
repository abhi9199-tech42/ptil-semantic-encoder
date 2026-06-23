"""
PTIL REST API server — FastAPI-based HTTP interface for semantic encoding.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from ..encoder import PTILEncoder
from ..config import PTILConfig
from ..logging_context import PTILContext, set_context
from ..metrics import MetricsCollector


class EncodeRequest(BaseModel):
    text: str = Field(..., max_length=10000)
    format: str = "verbose"


class EncodeBatchRequest(BaseModel):
    texts: List[str] = Field(..., max_length=100)
    format: str = "verbose"


class EncodeResponse(BaseModel):
    text: str
    csc: str
    format: str
    language: str


class EncodeBatchResponse(BaseModel):
    results: List[EncodeResponse]


class IntentResponse(BaseModel):
    text: str
    intent: str
    confidence: float
    root: str
    ops: List[str]
    roles: dict
    meta: str
    ultra_compact: str


class IntentBatchRequest(BaseModel):
    texts: List[str]


class IntentBatchResponse(BaseModel):
    results: List[IntentResponse]


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.5.0"


def create_app(config: Optional[PTILConfig] = None) -> FastAPI:
    cfg = config or PTILConfig()
    encoder = PTILEncoder(config=cfg)
    metrics = MetricsCollector()

    app = FastAPI(
        title="PTIL Semantic Encoder API",
        version="0.4.0",
        description="Deterministic semantic abstraction to Compressed Semantic Code",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.allowed_origins if hasattr(cfg, 'allowed_origins') and cfg.allowed_origins else ["http://localhost:8000"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup():
        pass

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    async def health():
        return HealthResponse()

    @app.post("/encode", response_model=EncodeResponse, tags=["encode"])
    async def encode(req: EncodeRequest, request: Request):
        ctx = PTILContext.create(
            language=cfg.language,
            input_text=req.text,
            component="api",
        )
        set_context(ctx)
        rid = request.headers.get(cfg.request_id_header, ctx.request_id)

        try:
            result = encoder.encode_and_serialize(req.text, format=req.format)
            return EncodeResponse(
                text=req.text,
                csc=result,
                format=req.format,
                language=cfg.language,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/encode/batch", response_model=EncodeBatchResponse, tags=["encode"])
    async def encode_batch(req: EncodeBatchRequest, request: Request):
        try:
            results = encoder.encode_and_serialize_batch(req.texts, format=req.format)
            return EncodeBatchResponse(
                results=[
                    EncodeResponse(text=t, csc=r, format=req.format, language=cfg.language)
                    for t, r in zip(req.texts, results)
                ]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/intent", response_model=IntentResponse, tags=["classify"])
    async def classify_intent(req: EncodeRequest, request: Request):
        ctx = PTILContext.create(
            language=cfg.language,
            input_text=req.text,
            component="intent",
        )
        set_context(ctx)

        try:
            cscs = encoder.encode(req.text)
            if not cscs:
                raise HTTPException(status_code=422, detail="Could not classify text")

            csc = cscs[0]
            ultra = encoder.ultra_compact_serializer.serialize_multiple(cscs)

            intent = csc.root.value.lower()
            confidence = 0.9 if csc.ops else 0.7

            return IntentResponse(
                text=req.text,
                intent=intent,
                confidence=confidence,
                root=csc.root.value,
                ops=[op.value for op in csc.ops],
                roles={role.value: entity.text for role, entity in csc.roles.items()},
                meta=csc.meta.value if csc.meta else None,
                ultra_compact=ultra,
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/intent/batch", response_model=IntentBatchResponse, tags=["classify"])
    async def classify_intent_batch(req: IntentBatchRequest, request: Request):
        try:
            results = []
            for text in req.texts:
                cscs = encoder.encode(text)
                if cscs:
                    csc = cscs[0]
                    ultra = encoder.ultra_compact_serializer.serialize_multiple(cscs)
                    results.append(IntentResponse(
                        text=text,
                        intent=csc.root.value.lower(),
                        confidence=0.9 if csc.ops else 0.7,
                        root=csc.root.value,
                        ops=[op.value for op in csc.ops],
                        roles={role.value: entity.text for role, entity in csc.roles.items()},
                        meta=csc.meta.value if csc.meta else None,
                        ultra_compact=ultra,
                    ))
            return IntentBatchResponse(results=results)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/metrics", tags=["system"])
    async def get_metrics():
        snap = metrics.snapshot()
        lines = []
        for name, mv in snap.get("timings", {}).items():
            lines.append(f'# HELP ptil_{name}_count Timing count for {name}')
            lines.append(f'# TYPE ptil_{name}_count counter')
            lines.append(f'ptil_{name}_count {mv["count"]}')
            lines.append(f'ptil_{name}_avg_ms {mv["avg_ms"]}')
            lines.append(f'ptil_{name}_max_ms {mv["max_ms"]}')
        for name, count in snap.get("counters", {}).items():
            lines.append(f'# HELP ptil_{name} Counter for {name}')
            lines.append(f'# TYPE ptil_{name} counter')
            lines.append(f'ptil_{name} {count}')
        return PlainTextResponse("\n".join(lines))

    @app.get("/cache/stats", tags=["system"])
    async def cache_stats():
        return encoder.get_cache_stats()

    @app.post("/cache/clear", tags=["system"])
    async def cache_clear():
        encoder.clear_cache()
        return {"status": "cleared"}

    return app


def run_server(config: Optional[PTILConfig] = None, host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    app = create_app(config)
    uvicorn.run(app, host=host, port=port, log_level="info")
