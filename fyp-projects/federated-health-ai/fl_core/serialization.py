"""Parameter (de)serialisation for storing model versions."""

from __future__ import annotations

import io

import numpy as np

NDArrays = list[np.ndarray]


def params_to_bytes(params: NDArrays) -> bytes:
    """Serialise a parameter list to compressed npz bytes, order-preserving."""
    buf = io.BytesIO()
    np.savez_compressed(buf, **{f"arr_{i}": p for i, p in enumerate(params)})
    return buf.getvalue()


def params_from_bytes(blob: bytes) -> NDArrays:
    buf = io.BytesIO(blob)
    with np.load(buf) as data:
        return [data[f"arr_{i}"] for i in range(len(data.files))]
