"""Toy experiment: logistic regression on a small noisy synthetic dataset, with optional label smoothing."""
import math, os, random, sys

seed = int(os.environ.get("LAB_SEED", 0))
ls = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
steps = int(sys.argv[2]) if len(sys.argv) > 2 else 400
rng = random.Random(seed)
w_true = [rng.gauss(0, 1) for _ in range(20)]

def sample(n, noise):
    xs, ys = [], []
    for _ in range(n):
        x = [rng.gauss(0, 1) for _ in range(20)]
        y = 1 if sum(a * b for a, b in zip(w_true, x)) > 0 else 0
        if rng.random() < noise:
            y = 1 - y
        xs.append(x); ys.append(y)
    return xs, ys

xtr, ytr = sample(300, 0.15)
xte, yte = sample(2000, 0.0)
w = [0.0] * 20
for step in range(steps):
    g = [0.0] * 20
    for x, y in zip(xtr, ytr):
        p = 1 / (1 + math.exp(-sum(a * b for a, b in zip(w, x))))
        t = y * (1 - ls) + ls / 2
        for i in range(20):
            g[i] += (p - t) * x[i] / len(xtr) + 0.002 * w[i]
    w = [a - 0.5 * b for a, b in zip(w, g)]
acc = sum((sum(a * b for a, b in zip(w, x)) > 0) == y for x, y in zip(xte, yte)) / len(xte)
print(f"seed={seed} label_smoothing={ls} steps={steps}")
print(f"LAB_METRIC test_acc={acc:.4f}")
