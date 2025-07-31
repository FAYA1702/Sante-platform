"""Paramètres globaux de la plateforme Santé.

Ce module centralise les variables d'environnement et options
utiles à plusieurs sous-modules. Il humanise aussi le code en
laissant des noms explicites en français.

Variables principales
---------------------
DEMO_MODE : bool
    Lorsque vrai, l'administrateur est autorisé à consulter les
    données santé, mais uniquement à des fins de démonstration.
    En production, laissez la variable à `False` pour respecter le
    secret médical et la conformité RGPD.

Utilisation
-----------
>>> from backend.settings import DEMO_MODE
>>> if DEMO_MODE:
...     print("Mode démo activé – attention aux accès étendus !")
"""

from os import getenv

# Lis la variable d'environnement DEMO_MODE ("true"/"false", case-insensible)
DEMO_MODE: bool = getenv("DEMO_MODE", "false").lower() in {"1", "true", "yes"}
