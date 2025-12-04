import torch
import os
import sys

# Patch for Numpy 2.0 compatibility
import numpy as np

if "numpy._core" not in sys.modules:
    try:
        from numpy import core

        sys.modules["numpy._core"] = core
        sys.modules["numpy._core.multiarray"] = core.multiarray
    except ImportError:
        pass

try:
    data = torch.load("ai_engine/graph_data.pt")
    print("Metadata:", data.metadata())
except Exception as e:
    print(f"Error: {e}")
