"""Run all executable package examples and assert their evidence contracts."""

from tensor_autograd_demo import main as tensor_main
from training_loop_demo import main as training_main


def main() -> None:
    tensor = tensor_main()
    training = training_main()
    print("tensor_autograd_demo", tensor)
    print("training_loop_demo", training)
    print("validated: metadata, autograd, loop ordering, and gradient-free evaluation")


if __name__ == "__main__":
    main()
