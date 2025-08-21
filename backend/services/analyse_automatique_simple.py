#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Service d'analyse automatique des données de santé - Version simplifiée
Génère des alertes et recommandations automatiquement lors de la saisie de données
"""

from datetime import datetime
from typing import Dict, Any
from bson import ObjectId
from pymongo import MongoClient


def analyser_donnee_sync(donnee_id: str) -> Dict[str, Any]:
    """Analyse une donnée et génère alertes/recommandations si nécessaire - Version synchrone"""
    try:
        # Connexion MongoDB directe
        client = MongoClient("mongodb://localhost:27017/")
        db = client["sante_db"]
        
        # Récupérer la donnée
        donnee = db.donnees_vitales.find_one({"_id": ObjectId(donnee_id)})
        if not donnee:
            return {"error": "Donnée introuvable"}
        
        # Récupérer le patient
        patient = db.utilisateurs.find_one({"_id": ObjectId(donnee['user_id'])})
        if not patient:
            return {"error": "Patient introuvable"}
        
        # Récupérer le médecin référent
        medecin_referent_id = patient.get('medecin_referent')
        medecin = None
        if medecin_referent_id:
            medecin = db.utilisateurs.find_one({"_id": ObjectId(medecin_referent_id)})
        
        alertes_creees = []
        recommandations_creees = []
        
        # Seuils d'alerte
        seuils = {
            'fc_min': 60, 'fc_max': 100, 'fc_critique_min': 40, 'fc_critique_max': 150,
            'spo2_min': 95, 'spo2_critique': 90,
            'pa_sys_max': 140, 'pa_sys_critique': 180, 'pa_sys_min': 90
        }
        
        # Analyser fréquence cardiaque
        if donnee.get('frequence_cardiaque'):
            fc = donnee['frequence_cardiaque']
            alerte = None
            
            if fc <= seuils['fc_critique_min']:
                alerte = {
                    "user_id": donnee['user_id'],
                    "message": f"Bradycardie sévère détectée: {fc} bpm",
                    "niveau": "critical",
                    "date": datetime.utcnow(),
                    "statut": "nouvelle",
                    "donnee_id": str(donnee['_id']),
                    "type_parametre": "frequence_cardiaque",
                    "valeur": fc
                }
            elif fc >= seuils['fc_critique_max']:
                alerte = {
                    "user_id": donnee['user_id'],
                    "message": f"Tachycardie sévère détectée: {fc} bpm",
                    "niveau": "critical",
                    "date": datetime.utcnow(),
                    "statut": "nouvelle",
                    "donnee_id": str(donnee['_id']),
                    "type_parametre": "frequence_cardiaque",
                    "valeur": fc
                }
            elif fc < seuils['fc_min'] or fc > seuils['fc_max']:
                alerte = {
                    "user_id": donnee['user_id'],
                    "message": f"Fréquence cardiaque anormale: {fc} bpm",
                    "niveau": "warning",
                    "date": datetime.utcnow(),
                    "statut": "nouvelle",
                    "donnee_id": str(donnee['_id']),
                    "type_parametre": "frequence_cardiaque",
                    "valeur": fc
                }
            
            if alerte:
                result = db.alertes.insert_one(alerte)
                alerte['_id'] = result.inserted_id
                alertes_creees.append(alerte)
                
                # L'alerte sera visible par le médecin qui créera manuellement la recommandation
        
        # Analyser saturation en oxygène
        if donnee.get('taux_oxygene'):
            spo2 = donnee['taux_oxygene']
            alerte = None
            
            if spo2 <= seuils['spo2_critique']:
                alerte = {
                    "user_id": donnee['user_id'],
                    "message": f"Hypoxie sévère détectée: {spo2}%",
                    "niveau": "critical",
                    "date": datetime.utcnow(),
                    "statut": "nouvelle",
                    "donnee_id": str(donnee['_id']),
                    "type_parametre": "taux_oxygene",
                    "valeur": spo2
                }
            elif spo2 < seuils['spo2_min']:
                alerte = {
                    "user_id": donnee['user_id'],
                    "message": f"Saturation en oxygène basse: {spo2}%",
                    "niveau": "warning",
                    "date": datetime.utcnow(),
                    "statut": "nouvelle",
                    "donnee_id": str(donnee['_id']),
                    "type_parametre": "taux_oxygene",
                    "valeur": spo2
                }
            
            if alerte:
                result = db.alertes.insert_one(alerte)
                alerte['_id'] = result.inserted_id
                alertes_creees.append(alerte)
                
                # L'alerte sera visible par le médecin qui créera manuellement la recommandation
        
        # Analyser pression artérielle
        if donnee.get('pression_arterielle'):
            pa = donnee['pression_arterielle']
            alerte = None
            
            if pa >= seuils['pa_sys_critique']:
                alerte = {
                    "user_id": donnee['user_id'],
                    "message": f"Hypertension sévère détectée: {pa} mmHg",
                    "niveau": "critical",
                    "date": datetime.utcnow(),
                    "statut": "nouvelle",
                    "donnee_id": str(donnee['_id']),
                    "type_parametre": "pression_arterielle",
                    "valeur": pa
                }
            elif pa > seuils['pa_sys_max'] or pa < seuils['pa_sys_min']:
                alerte = {
                    "user_id": donnee['user_id'],
                    "message": f"Pression artérielle anormale: {pa} mmHg",
                    "niveau": "warning",
                    "date": datetime.utcnow(),
                    "statut": "nouvelle",
                    "donnee_id": str(donnee['_id']),
                    "type_parametre": "pression_arterielle",
                    "valeur": pa
                }
            
            if alerte:
                result = db.alertes.insert_one(alerte)
                alerte['_id'] = result.inserted_id
                alertes_creees.append(alerte)
                
                # L'alerte sera visible par le médecin qui créera manuellement la recommandation
        
        # 4. Notifier le médecin référent des nouvelles alertes
        # Le médecin devra consulter les alertes et créer manuellement les recommandations
        if medecin_referent_id and alertes_creees:
            def notifier_medecin_alertes(medecin_id: str, patient_id: str, nb_alertes: int, db) -> bool:
                """Notifie le médecin référent des nouvelles alertes de son patient"""
                try:
                    # Récupérer les informations du patient
                    patient = db.utilisateurs.find_one({"_id": ObjectId(patient_id)})
                    if not patient:
                        return False
                    
                    # Créer une notification pour le médecin
                    notification = {
                        "user_id": medecin_id,
                        "type": "nouvelles_alertes",
                        "titre": f"Nouvelles alertes - {patient.get('username', 'Patient')}",
                        "message": f"{nb_alertes} nouvelle(s) alerte(s) nécessitent votre attention",
                        "patient_id": patient_id,
                        "date_creation": datetime.utcnow(),
                        "vue": False,
                        "priorite": "haute"
                    }
                    
                    db.notifications.insert_one(notification)
                    return True
                    
                except Exception as e:
                    print(f"Erreur notification médecin: {e}")
                    return False

            notifier_medecin_alertes(medecin_referent_id, donnee['user_id'], len(alertes_creees), db)
            print(f"Médecin {medecin_referent_id} notifié de {len(alertes_creees)} nouvelle(s) alerte(s)")
        
        return {
            "alertes_creees": len(alertes_creees),
            "medecin_notifie": bool(medecin_referent_id and alertes_creees)
        }
        
    except Exception as e:
        return {"error": f"Erreur lors de l'analyse: {str(e)}"}


# Point d'entrée pour traiter une nouvelle donnée de santé
def traiter_nouvelle_donnee_sync(donnee_id: str) -> Dict[str, Any]:
    """Point d'entrée synchrone pour traiter une nouvelle donnée de santé"""
    return analyser_donnee_sync(donnee_id)
