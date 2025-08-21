"""Service d'assignation automatique des patients aux médecins par IA.
Analyse les besoins du patient et assigne le médecin le plus approprié.
"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from backend.db import get_client, MONGO_DB_NAME
from bson import ObjectId
import random


class IAAssignationService:
    """Service IA pour l'assignation automatique patient-médecin."""
    
    def __init__(self):
        self.client = get_client()
        self.db = self.client[MONGO_DB_NAME]
    
    async def assigner_medecin_automatique(self, patient_id: str, department_id: str = None) -> Optional[str]:
        """
        Assigne automatiquement un médecin à un patient selon l'algorithme IA.
        
        Args:
            patient_id: ID du patient
            department_id: Département médical préféré (optionnel)
            
        Returns:
            ID du médecin assigné ou None si échec
        """
        try:
            # 1. Récupérer les informations du patient
            patient = await self.db.utilisateurs.find_one({"_id": ObjectId(patient_id)})
            if not patient:
                print(f"[IA-Assignation] Patient {patient_id} introuvable")
                return None
            
            # 2. Analyser les critères d'assignation
            criteres = await self._analyser_criteres_patient(patient, department_id)
            
            # 3. Trouver les médecins disponibles
            medecins_disponibles = await self._trouver_medecins_disponibles(criteres)
            
            if not medecins_disponibles:
                print(f"[IA-Assignation] Aucun médecin disponible pour {patient['username']}")
                return None
            
            # 4. Algorithme IA de sélection
            medecin_optimal = await self._algorithme_selection_ia(medecins_disponibles, criteres)
            
            # 5. Effectuer l'assignation
            success = await self._effectuer_assignation(patient_id, medecin_optimal['id'])
            
            if success:
                print(f"[IA-Assignation] ✅ {patient['username']} assigné à Dr. {medecin_optimal['username']}")
                return medecin_optimal['id']
            
            return None
            
        except Exception as e:
            print(f"[IA-Assignation] ❌ Erreur: {str(e)}")
            return None
    
    async def _analyser_criteres_patient(self, patient: Dict, department_id: str = None) -> Dict[str, Any]:
        """Analyse les critères du patient pour l'assignation."""
        criteres = {
            "department_preference": department_id or "default-general",
            "patient_age": self._estimer_age_patient(patient),
            "urgence_niveau": "normal",  # Par défaut
            "historique_medical": await self._analyser_historique(patient["_id"])
        }
        
        # Analyse IA basée sur le département
        if department_id == "default-cardio":
            criteres["specialite_requise"] = "cardiologie"
            criteres["priorite"] = "haute"
        elif department_id == "default-pneumo":
            criteres["specialite_requise"] = "pneumologie"
            criteres["priorite"] = "haute"
        else:
            criteres["specialite_requise"] = "generale"
            criteres["priorite"] = "normale"
        
        return criteres
    
    async def _trouver_medecins_disponibles(self, criteres: Dict) -> list:
        """Trouve les médecins disponibles selon les critères."""
        # Mapping des départements
        dept_mapping = {
            "default-general": "medecine_generale",
            "default-cardio": "cardiologie", 
            "default-pneumo": "pneumologie"
        }
        
        department_filter = dept_mapping.get(criteres["department_preference"], "medecine_generale")
        
        # Requête pour trouver les médecins
        query = {
            "role": "medecin",
            "statut": "actif",
            "department_id": department_filter
        }
        
        medecins_cursor = self.db.utilisateurs.find(query)
        medecins = []
        
        async for medecin in medecins_cursor:
            # Calculer la charge de travail
            charge = await self._calculer_charge_medecin(str(medecin["_id"]))
            
            medecins.append({
                "id": str(medecin["_id"]),
                "username": medecin["username"],
                "email": medecin["email"],
                "department_id": medecin.get("department_id", "medecine_generale"),
                "charge_travail": charge,
                "disponibilite": charge < 10  # Max 10 patients par médecin
            })
        
        # Filtrer les médecins disponibles
        return [m for m in medecins if m["disponibilite"]]
    
    async def _calculer_charge_medecin(self, medecin_id: str) -> int:
        """Calcule le nombre de patients assignés à un médecin."""
        count = await self.db.utilisateurs.count_documents({
            "role": "patient",
            "medecin_ids": medecin_id
        })
        return count
    
    async def _algorithme_selection_ia(self, medecins: list, criteres: Dict) -> Dict:
        """Algorithme IA pour sélectionner le médecin optimal."""
        if not medecins:
            return None
        
        # Scoring IA basé sur plusieurs facteurs
        for medecin in medecins:
            score = 0
            
            # 1. Spécialité correspondante (+50 points)
            if criteres["specialite_requise"] in medecin["department_id"]:
                score += 50
            
            # 2. Charge de travail (moins = mieux)
            score += max(0, 30 - (medecin["charge_travail"] * 3))
            
            # 3. Facteur aléatoire pour équilibrer (+0 à 20 points)
            score += random.randint(0, 20)
            
            medecin["score_ia"] = score
        
        # Sélectionner le médecin avec le meilleur score
        medecin_optimal = max(medecins, key=lambda m: m["score_ia"])
        
        print(f"[IA-Assignation] Médecin sélectionné: Dr. {medecin_optimal['username']} (score: {medecin_optimal['score_ia']})")
        
        return medecin_optimal
    
    async def _effectuer_assignation(self, patient_id: str, medecin_id: str) -> bool:
        """Effectue l'assignation dans la base de données."""
        try:
            # Mettre à jour le patient
            await self.db.utilisateurs.update_one(
                {"_id": ObjectId(patient_id)},
                {"$set": {"medecin_ids": [medecin_id]}}
            )
            
            # Mettre à jour le médecin
            await self.db.utilisateurs.update_one(
                {"_id": ObjectId(medecin_id)},
                {"$addToSet": {"patient_ids": patient_id}}
            )
            
            # Créer un log d'assignation
            await self.db.assignation_logs.insert_one({
                "patient_id": patient_id,
                "medecin_id": medecin_id,
                "type": "ia_automatique",
                "date": datetime.utcnow(),
                "statut": "active"
            })
            
            return True
            
        except Exception as e:
            print(f"[IA-Assignation] Erreur lors de l'assignation: {str(e)}")
            return False
    
    def _estimer_age_patient(self, patient: Dict) -> str:
        """Estime l'âge du patient (simulation)."""
        # En production, cela viendrait des données réelles
        return "adulte"
    
    async def _analyser_historique(self, patient_id: ObjectId) -> Dict:
        """Analyse l'historique médical du patient."""
        # Compter les alertes existantes
        alertes_count = await self.db.alertes.count_documents({"user_id": str(patient_id)})
        
        return {
            "alertes_precedentes": alertes_count,
            "risque_niveau": "normal" if alertes_count < 5 else "eleve"
        }


# Instance globale du service
ia_assignation_service = IAAssignationService()
