import os

__all__ = [f.split(".")[:-1] for f in os.listdir() if not f.startswith("_")]  # type: ignore
