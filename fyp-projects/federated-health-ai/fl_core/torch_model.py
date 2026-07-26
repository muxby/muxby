"""PyTorch mirror of the reference NumPy MLP.

Used by the Flower-based distributed deployment (docker-compose services).
Parameter order matches ``fl_core.nn.MLP.get_parameters`` exactly
(W1, b1, W2, b2, W3, b3), so checkpoints and aggregation code are shared
between backends. Import requires torch; the rest of fl_core does not.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn

from fl_core.data import NUM_FEATURES


class TorchMLP(nn.Module):
    def __init__(self, n_features: int = NUM_FEATURES, hidden: tuple[int, ...] = (64, 32)):
        super().__init__()
        layers: list[nn.Module] = []
        sizes = [n_features, *hidden, 1]
        for i in range(len(sizes) - 1):
            layers.append(nn.Linear(sizes[i], sizes[i + 1]))
            if i < len(sizes) - 2:
                layers.append(nn.ReLU())
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(-1)

    # ---- NDArrays interop (transposed vs nn.Linear's (out, in) layout) ----
    def get_ndarrays(self) -> list[np.ndarray]:
        params: list[np.ndarray] = []
        for module in self.net:
            if isinstance(module, nn.Linear):
                params.append(module.weight.detach().cpu().numpy().T.copy())
                params.append(module.bias.detach().cpu().numpy().copy())
        return params

    def set_ndarrays(self, params: list[np.ndarray]) -> None:
        linears = [m for m in self.net if isinstance(m, nn.Linear)]
        if len(params) != 2 * len(linears):
            raise ValueError(f"expected {2 * len(linears)} arrays, got {len(params)}")
        with torch.no_grad():
            for i, module in enumerate(linears):
                W, b = params[2 * i], params[2 * i + 1]
                module.weight.copy_(torch.from_numpy(np.ascontiguousarray(W.T)).float())
                module.bias.copy_(torch.from_numpy(b).float())


def train_torch(
    model: TorchMLP,
    X: np.ndarray,
    y: np.ndarray,
    epochs: int = 1,
    batch_size: int = 32,
    lr: float = 1e-3,
    device: str = "cpu",
) -> float:
    """Local training loop used by the Flower client; returns final mean loss."""
    model.to(device).train()
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.BCEWithLogitsLoss()
    Xt = torch.from_numpy(X).float().to(device)
    yt = torch.from_numpy(y).float().to(device)
    n = len(Xt)
    final = 0.0
    for _ in range(epochs):
        order = torch.randperm(n)
        losses: list[float] = []
        for start in range(0, n, batch_size):
            idx = order[start : start + batch_size]
            opt.zero_grad()
            loss = loss_fn(model(Xt[idx]), yt[idx])
            loss.backward()
            opt.step()
            losses.append(float(loss.detach()))
        final = float(np.mean(losses))
    return final


@torch.no_grad()
def evaluate_torch(model: TorchMLP, X: np.ndarray, y: np.ndarray, device: str = "cpu") -> tuple[float, float]:
    """Returns (loss, accuracy) on the given set."""
    model.to(device).eval()
    Xt = torch.from_numpy(X).float().to(device)
    yt = torch.from_numpy(y).float().to(device)
    logits = model(Xt)
    loss = float(nn.functional.binary_cross_entropy_with_logits(logits, yt))
    acc = float(((torch.sigmoid(logits) >= 0.5) == (yt >= 0.5)).float().mean())
    return loss, acc
