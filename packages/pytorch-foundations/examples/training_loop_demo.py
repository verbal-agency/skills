"""Deterministic CPU training and evaluation example for the package."""

import torch
from torch import nn


def main() -> dict[str, object]:
    torch.manual_seed(7)
    x = torch.tensor([[0.0], [1.0], [2.0], [3.0]])
    y = 2 * x + 1
    model = nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    loss_fn = nn.MSELoss()
    losses: list[float] = []

    model.train()
    for _ in range(40):
        optimizer.zero_grad()
        loss = loss_fn(model(x), y)
        loss.backward()
        optimizer.step()
        losses.append(float(loss.detach()))

    model.eval()
    with torch.no_grad():
        predictions = model(x)
        eval_loss = float(loss_fn(predictions, y))

    assert losses[-1] < losses[0]
    assert eval_loss < 0.02
    assert not predictions.requires_grad
    return {
        "loss_start": round(losses[0], 6),
        "loss_end": round(losses[-1], 6),
        "eval_loss": round(eval_loss, 6),
        "output_requires_grad": predictions.requires_grad,
    }


if __name__ == "__main__":
    print(main())
