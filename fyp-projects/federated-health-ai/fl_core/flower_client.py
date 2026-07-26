"""Flower NumPyClient for a single hospital node.

Run one per hospital container in the distributed deployment:

    python -m fl_core.flower_client --server fl-server:8080 --client-id 1 \
        --num-clients 3 --samples 2000
"""

from __future__ import annotations

import argparse

import flwr as fl
import numpy as np

from fl_core.data import FeatureScaler, generate_patients, partition_dirichlet
from fl_core.torch_model import TorchMLP, evaluate_torch, train_torch


class HospitalClient(fl.client.NumPyClient):
    def __init__(self, X: np.ndarray, y: np.ndarray, local_epochs: int, batch_size: int, lr: float):
        self.X, self.y = X, y
        self.local_epochs = local_epochs
        self.batch_size = batch_size
        self.lr = lr
        self.model = TorchMLP()

    def get_parameters(self, config):
        return self.model.get_ndarrays()

    def fit(self, parameters, config):
        self.model.set_ndarrays(parameters)
        epochs = int(config.get("local_epochs", self.local_epochs))
        loss = train_torch(
            self.model, self.X, self.y, epochs=epochs, batch_size=self.batch_size, lr=self.lr
        )
        return self.model.get_ndarrays(), len(self.X), {"train_loss": loss}

    def evaluate(self, parameters, config):
        self.model.set_ndarrays(parameters)
        loss, acc = evaluate_torch(self.model, self.X, self.y)
        return loss, len(self.X), {"accuracy": acc}


def load_shard(client_id: int, num_clients: int, samples: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Deterministically derive this hospital's non-IID shard of the cohort."""
    X, y = generate_patients(samples * num_clients, seed=seed)
    scaler = FeatureScaler.fit(X)
    Xs = scaler.transform(X)
    parts = partition_dirichlet(y, num_clients, alpha=0.5, seed=seed)
    idx = parts[client_id - 1]
    return Xs[idx], y[idx]


def main() -> None:
    parser = argparse.ArgumentParser(description="Federated hospital client")
    parser.add_argument("--server", default="127.0.0.1:8080")
    parser.add_argument("--client-id", type=int, required=True)
    parser.add_argument("--num-clients", type=int, default=3)
    parser.add_argument("--samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--local-epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    args = parser.parse_args()

    X, y = load_shard(args.client_id, args.num_clients, args.samples, args.seed)
    client = HospitalClient(X, y, args.local_epochs, args.batch_size, args.lr)
    fl.client.start_client(server_address=args.server, client=client.to_client())


if __name__ == "__main__":
    main()
