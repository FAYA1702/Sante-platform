"""Configuration pytest globale pour ajouter la racine du projet au PYTHONPATH."""

import sys
from pathlib import Path

# Ajoute la racine du projet (dossier contenant 'backend') au path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
