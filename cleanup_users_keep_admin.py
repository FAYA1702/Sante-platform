#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

def safe_print(text):
    """Impression sécurisée pour éviter les erreurs d'encodage"""
    try:
        text = text.replace('✓', '[OK]').replace('✗', '[ERR]').replace('→', '->')
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='replace').decode('ascii'))

def main():
    try:
        # Connexion à MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["sante_db"]
        
        safe_print("=== NETTOYAGE UTILISATEURS - GARDER ADMIN SEULEMENT ===\n")
        
        # 1. Identifier l'utilisateur admin
        admin_user = db.utilisateurs.find_one({"role": "admin"})
        if not admin_user:
            safe_print("ERREUR: Aucun utilisateur admin trouvé")
            return
        
        admin_id = str(admin_user['_id'])
        safe_print(f"Admin identifié: {admin_user.get('username', 'N/A')} (ID: {admin_id})")
        
        # 2. Lister tous les utilisateurs non-admin
        users_to_delete = list(db.utilisateurs.find({
            "role": {"$ne": "admin"}
        }))
        
        safe_print(f"\nUtilisateurs à supprimer: {len(users_to_delete)}")
        for user in users_to_delete:
            safe_print(f"  - {user.get('username', 'N/A')} ({user.get('role', 'N/A')}) - ID: {user['_id']}")
        
        if len(users_to_delete) == 0:
            safe_print("Aucun utilisateur à supprimer")
            return
        
        # Confirmation
        safe_print(f"\nATTENTION: Cette opération va supprimer {len(users_to_delete)} utilisateur(s)")
        safe_print("Auto-confirmation activée")
        
        # Auto-confirmation pour script
        confirmation = "y"
        
        if confirmation.lower() != 'y':
            safe_print("Opération annulée")
            return
        
        # 3. Collecter les IDs des utilisateurs à supprimer
        user_ids_to_delete = [str(user['_id']) for user in users_to_delete]
        safe_print(f"\nIDs à supprimer: {len(user_ids_to_delete)}")
        
        # 4. Supprimer les données liées aux utilisateurs
        safe_print("\n=== SUPPRESSION DONNÉES LIÉES ===")
        
        # Supprimer les données vitales
        result_donnees = db.donnees_vitales.delete_many({
            "user_id": {"$in": user_ids_to_delete}
        })
        safe_print(f"Données vitales supprimées: {result_donnees.deleted_count}")
        
        # Supprimer les alertes
        result_alertes = db.alertes.delete_many({
            "user_id": {"$in": user_ids_to_delete}
        })
        safe_print(f"Alertes supprimées: {result_alertes.deleted_count}")
        
        # Supprimer les recommandations (patient_id et medecin_id)
        result_recos_patient = db.recommandations.delete_many({
            "patient_id": {"$in": user_ids_to_delete}
        })
        result_recos_medecin = db.recommandations.delete_many({
            "medecin_id": {"$in": user_ids_to_delete}
        })
        safe_print(f"Recommandations supprimées: {result_recos_patient.deleted_count + result_recos_medecin.deleted_count}")
        
        # Supprimer les appareils
        result_appareils = db.appareils.delete_many({
            "user_id": {"$in": user_ids_to_delete}
        })
        safe_print(f"Appareils supprimés: {result_appareils.deleted_count}")
        
        # Supprimer les assignations
        result_assignations = db.assignations.delete_many({
            "$or": [
                {"patient_ids": {"$in": user_ids_to_delete}},
                {"medecin_ids": {"$in": user_ids_to_delete}}
            ]
        })
        safe_print(f"Assignations supprimées: {result_assignations.deleted_count}")
        
        # Supprimer les notifications
        result_notifications = db.notifications.delete_many({
            "user_id": {"$in": user_ids_to_delete}
        })
        safe_print(f"Notifications supprimées: {result_notifications.deleted_count}")
        
        # 5. Supprimer les utilisateurs
        safe_print("\n=== SUPPRESSION UTILISATEURS ===")
        
        result_users = db.utilisateurs.delete_many({
            "_id": {"$in": [ObjectId(uid) for uid in user_ids_to_delete]}
        })
        safe_print(f"Utilisateurs supprimés: {result_users.deleted_count}")
        
        # 6. Vérification finale
        safe_print("\n=== VÉRIFICATION FINALE ===")
        
        remaining_users = list(db.utilisateurs.find())
        safe_print(f"Utilisateurs restants: {len(remaining_users)}")
        
        for user in remaining_users:
            safe_print(f"  - {user.get('username', 'N/A')} ({user.get('role', 'N/A')})")
        
        # Vérifier que l'admin est toujours là
        admin_check = db.utilisateurs.find_one({"_id": ObjectId(admin_id)})
        if admin_check:
            safe_print(f"[OK] Admin préservé: {admin_check.get('username', 'N/A')}")
        else:
            safe_print("[ERR] Admin supprimé par erreur!")
        
        # 7. Statistiques finales
        safe_print("\n=== STATISTIQUES FINALES ===")
        
        stats = {
            "utilisateurs": db.utilisateurs.count_documents({}),
            "donnees_vitales": db.donnees_vitales.count_documents({}),
            "alertes": db.alertes.count_documents({}),
            "recommandations": db.recommandations.count_documents({}),
            "appareils": db.appareils.count_documents({}),
            "assignations": db.assignations.count_documents({}),
            "notifications": db.notifications.count_documents({})
        }
        
        for collection, count in stats.items():
            safe_print(f"{collection}: {count}")
        
        safe_print("\n=== NETTOYAGE TERMINÉ ===")
        safe_print("Base de données nettoyée, seul l'admin reste")
        
    except Exception as e:
        safe_print(f"Erreur lors du nettoyage: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    main()
