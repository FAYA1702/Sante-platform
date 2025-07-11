"""Regroupe tous les modèles Beanie pour l'application.
Inclut également le modèle Utilisateur pour les tests RBAC."""

from .device import Device
from .donnee import Donnee
from .alerte import Alerte
from .recommandation import Recommandation
from .utilisateur import Utilisateur

__all__ = [
    "Device",
    "Donnee",
    "Alerte",
    "Recommandation",
    "Utilisateur",
]
