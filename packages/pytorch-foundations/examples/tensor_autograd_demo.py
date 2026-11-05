"""Small deterministic tensor and autograd example for the package."""

import torch


def main() -> dict[str, object]:
    x = torch.tensor([[1.0, 2.0], [3.0, 4.0]], dtype=torch.float32, requires_grad=True)
    loss = (x.square()).mean()
    loss.backward()
    result = {
        "shape": list(x.shape),
        "dtype": str(x.dtype),
        "device": str(x.device),
        "grad_fn": type(loss.grad_fn).__name__ if loss.grad_fn else None,
        "grad": x.grad.tolist() if x.grad is not None else None,
    }
    assert result["shape"] == [2, 2]
    assert result["dtype"] == "torch.float32"
    assert result["device"] == "cpu"
    assert result["grad_fn"] is not None
    assert result["grad"] == [[0.5, 1.0], [1.5, 2.0]]
    return result


if __name__ == "__main__":
    print(main())
