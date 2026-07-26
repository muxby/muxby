"""Flower aggregation server for the distributed deployment.

    python -m fl_core.flower_server --rounds 10 --min-clients 3 \
        --checkpoint /data/global_model.npz
"""

from __future__ import annotations

import argparse
import pathlib

import flwr as fl
import numpy as np

from fl_core.data import FeatureScaler, generate_patients, train_test_split
from fl_core.serialization import params_to_bytes
from fl_core.torch_model import TorchMLP, evaluate_torch


def make_evaluate_fn(checkpoint: pathlib.Path | None, seed: int):
    """Centralised evaluation on a held-out synthetic cohort + checkpointing."""
    X, y = generate_patients(4000, seed=seed + 1)
    scaler = FeatureScaler.fit(X)
    _, _, X_test, y_test = train_test_split(scaler.transform(X), y, test_fraction=0.5, seed=seed)
    model = TorchMLP()

    def evaluate_fn(server_round: int, parameters: list[np.ndarray], config: dict):
        model.set_ndarrays(parameters)
        loss, acc = evaluate_torch(model, X_test, y_test)
        if checkpoint is not None:
            checkpoint.parent.mkdir(parents=True, exist_ok=True)
            checkpoint.write_bytes(params_to_bytes(parameters))
        return loss, {"accuracy": acc}

    return evaluate_fn


def main() -> None:
    parser = argparse.ArgumentParser(description="Federated aggregation server")
    parser.add_argument("--address", default="0.0.0.0:8080")
    parser.add_argument("--rounds", type=int, default=10)
    parser.add_argument("--min-clients", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--checkpoint", type=pathlib.Path, default=None)
    args = parser.parse_args()

    initial = TorchMLP().get_ndarrays()
    strategy = fl.server.strategy.FedAvg(
        min_fit_clients=args.min_clients,
        min_evaluate_clients=args.min_clients,
        min_available_clients=args.min_clients,
        initial_parameters=fl.common.ndarrays_to_parameters(initial),
        evaluate_fn=make_evaluate_fn(args.checkpoint, args.seed),
        on_fit_config_fn=lambda server_round: {"local_epochs": 2},
    )
    fl.server.start_server(
        server_address=args.address,
        config=fl.server.ServerConfig(num_rounds=args.rounds),
        strategy=strategy,
    )


if __name__ == "__main__":
    main()
