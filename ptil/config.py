import os
import json
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class PTILConfig:
    language: str = "en"
    spaCy_model: str = "en_core_web_sm"
    unknown_predicate_strategy: str = "vector_fallback"
    serialization_format: str = "verbose"
    enable_metrics: bool = False
    log_level: str = "INFO"
    log_json: bool = False
    cache_size: int = 512
    cache_ttl_seconds: int = 3600
    batch_size: int = 64
    max_workers: int = 4
    custom_predicate_map: Optional[str] = None
    metrics_port: int = 8000
    request_id_header: str = "X-Request-ID"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PTILConfig":
        valid_keys = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)

    @classmethod
    def from_json(cls, path: str) -> "PTILConfig":
        with open(path) as f:
            return cls.from_dict(json.load(f))

    @classmethod
    def from_env(cls) -> "PTILConfig":
        prefix = "PTIL_"
        env_data = {}
        for key in cls.__dataclass_fields__.keys():
            env_key = f"{prefix}{key.upper()}"
            val = os.environ.get(env_key)
            if val is not None:
                field_info = cls.__dataclass_fields__[key]
                field_type = field_info.type
                try:
                    if field_type is bool:
                        val = val.lower() in ("1", "true", "yes")
                    elif field_type is int:
                        val = int(val)
                except (ValueError, TypeError):
                    continue
                env_data[key] = val
        return cls.from_dict(env_data)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def resolve(self) -> "PTILConfig":
        env_config = PTILConfig.from_env()
        merged = self.to_dict()
        defaults = PTILConfig().__dict__
        for k, v in env_config.to_dict().items():
            if v is None:
                continue
            default_v = defaults.get(k)
            if isinstance(default_v, (list, dict, set)):
                if v != default_v:
                    merged[k] = v
            else:
                if v != default_v:
                    merged[k] = v
        return PTILConfig.from_dict(merged)
