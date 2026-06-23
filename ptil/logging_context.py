import logging
import uuid
import json
import hashlib
import contextvars
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from datetime import datetime, timezone


_context: contextvars.ContextVar[Optional["PTILContext"]] = contextvars.ContextVar('_context', default=None)


@dataclass
class PTILContext:
    request_id: str = ""
    timestamp: str = ""
    language: str = ""
    input_hash: str = ""
    component: str = ""

    @classmethod
    def create(cls, language: str = "", input_text: str = "", component: str = "") -> "PTILContext":
        return cls(
            request_id=uuid.uuid4().hex[:12],
            timestamp=datetime.now(timezone.utc).isoformat(),
            language=language,
            input_hash=hashlib.md5(input_text.encode()).hexdigest()[:12] if input_text else "",
            component=component,
        )

    def with_component(self, name: str) -> "PTILContext":
        self.component = name
        return self


def get_context() -> Optional[PTILContext]:
    return _context.get()


def set_context(ctx: Optional[PTILContext]):
    _context.set(ctx)


class PTILogger:
    def __init__(self, name: str, json_format: bool = False):
        self._logger = logging.getLogger(name)
        self._json = json_format

    def _log(self, level: int, msg: str, **extra):
        ctx = get_context()
        if self._json:
            record = {
                "level": logging.getLevelName(level),
                "message": msg,
                "logger": self._logger.name,
            }
            if ctx:
                record["context"] = {k: v for k, v in asdict(ctx).items() if v}
            record.update(extra)
            self._logger.log(level, json.dumps(record))
        else:
            prefix = ""
            if ctx and ctx.request_id:
                prefix = f"[{ctx.request_id}] "
            self._logger.log(level, f"{prefix}{msg}")

    def info(self, msg: str, **extra):
        self._log(logging.INFO, msg, **extra)

    def error(self, msg: str, **extra):
        self._log(logging.ERROR, msg, **extra)

    def warning(self, msg: str, **extra):
        self._log(logging.WARNING, msg, **extra)

    def debug(self, msg: str, **extra):
        self._log(logging.DEBUG, msg, **extra)
