"""Reference neural-network implementation in pure NumPy.

This is the numerical backend the API server and the test suite run on.
``torch_model.py`` provides a parameter-compatible PyTorch mirror used by the
Flower deployment; both expose parameters as ``list[np.ndarray]`` in the same
order, so aggregation and privacy code is backend-agnostic.
"""

from __future__ import annotations

import numpy as np


class Dense:
    """Fully connected layer with He-initialised weights."""

    def __init__(self, n_in: int, n_out: int, rng: np.random.Generator):
        self.W = rng.normal(0.0, np.sqrt(2.0 / n_in), size=(n_in, n_out))
        self.b = np.zeros(n_out)
        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b)
        self._x: np.ndarray | None = None

    def forward(self, x: np.ndarray) -> np.ndarray:
        self._x = x
        return x @ self.W + self.b

    def backward(self, grad: np.ndarray) -> np.ndarray:
        assert self._x is not None, "forward must be called before backward"
        self.dW = self._x.T @ grad
        self.db = grad.sum(axis=0)
        return grad @ self.W.T


class ReLU:
    def __init__(self) -> None:
        self._mask: np.ndarray | None = None

    def forward(self, x: np.ndarray) -> np.ndarray:
        self._mask = x > 0
        return x * self._mask

    def backward(self, grad: np.ndarray) -> np.ndarray:
        assert self._mask is not None
        return grad * self._mask


class MLP:
    """Binary classifier: n_features -> hidden layers -> 1 logit."""

    def __init__(self, n_features: int, hidden: tuple[int, ...] = (64, 32), seed: int = 0):
        rng = np.random.default_rng(seed)
        self.layers: list[Dense | ReLU] = []
        sizes = [n_features, *hidden, 1]
        for i in range(len(sizes) - 1):
            self.layers.append(Dense(sizes[i], sizes[i + 1], rng))
            if i < len(sizes) - 2:
                self.layers.append(ReLU())
        self.n_features = n_features
        self.hidden = hidden

    # ---- inference -------------------------------------------------------
    def forward(self, X: np.ndarray) -> np.ndarray:
        out = X
        for layer in self.layers:
            out = layer.forward(out)
        return out[:, 0]

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return _sigmoid(self.forward(X))

    # ---- training --------------------------------------------------------
    def loss_and_backward(self, X: np.ndarray, y: np.ndarray) -> float:
        """BCE-with-logits loss; leaves gradients in each Dense layer."""
        logits = self.forward(X)
        n = len(y)
        # Numerically stable BCE with logits.
        loss = float(np.mean(np.maximum(logits, 0) - logits * y + np.log1p(np.exp(-np.abs(logits)))))
        grad = ((_sigmoid(logits) - y) / n)[:, None]
        for layer in reversed(self.layers):
            grad = layer.backward(grad)
        return loss

    # ---- parameter access (Flower NDArrays convention) -------------------
    def get_parameters(self) -> list[np.ndarray]:
        params: list[np.ndarray] = []
        for layer in self.layers:
            if isinstance(layer, Dense):
                params.extend([layer.W.copy(), layer.b.copy()])
        return params

    def set_parameters(self, params: list[np.ndarray]) -> None:
        dense = [l for l in self.layers if isinstance(l, Dense)]
        if len(params) != 2 * len(dense):
            raise ValueError(f"expected {2 * len(dense)} arrays, got {len(params)}")
        for i, layer in enumerate(dense):
            W, b = params[2 * i], params[2 * i + 1]
            if W.shape != layer.W.shape or b.shape != layer.b.shape:
                raise ValueError("parameter shape mismatch")
            layer.W = W.copy()
            layer.b = b.copy()

    def gradients(self) -> list[np.ndarray]:
        grads: list[np.ndarray] = []
        for layer in self.layers:
            if isinstance(layer, Dense):
                grads.extend([layer.dW, layer.db])
        return grads

    def num_parameters(self) -> int:
        return int(sum(p.size for p in self.get_parameters()))


class Adam:
    """Adam optimiser over a model's Dense parameters."""

    def __init__(self, model: MLP, lr: float = 1e-3, betas: tuple[float, float] = (0.9, 0.999), eps: float = 1e-8):
        self.model = model
        self.lr = lr
        self.b1, self.b2 = betas
        self.eps = eps
        self.t = 0
        self.m = [np.zeros_like(p) for p in model.get_parameters()]
        self.v = [np.zeros_like(p) for p in model.get_parameters()]

    def step(self) -> None:
        self.t += 1
        dense = [l for l in self.model.layers if isinstance(l, Dense)]
        params_and_grads: list[tuple[np.ndarray, np.ndarray]] = []
        for layer in dense:
            params_and_grads.append((layer.W, layer.dW))
            params_and_grads.append((layer.b, layer.db))
        for i, (p, g) in enumerate(params_and_grads):
            self.m[i] = self.b1 * self.m[i] + (1 - self.b1) * g
            self.v[i] = self.b2 * self.v[i] + (1 - self.b2) * g * g
            m_hat = self.m[i] / (1 - self.b1**self.t)
            v_hat = self.v[i] / (1 - self.b2**self.t)
            p -= self.lr * m_hat / (np.sqrt(v_hat) + self.eps)


def _sigmoid(x: np.ndarray) -> np.ndarray:
    out = np.empty_like(x, dtype=np.float64)
    pos = x >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-x[pos]))
    ex = np.exp(x[~pos])
    out[~pos] = ex / (1.0 + ex)
    return out
