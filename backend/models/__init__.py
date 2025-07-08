"""Regroupe tous les modèles Beanie pour l'application."""

from .device import Device
from .donnee import Donnee
from .alerte import Alerte
from .recommandation import Recommandation

__all__ = [
    "Device",
    "Donnee",
    "Alerte",
    "Recommandation",
]
