"""Routeur pour la consultation des recommandations."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from bson import ObjectId
import motor.motor_asyncio as motor_asyncio
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

from backend.models.recommandation import Recommandation
from backend.schemas.recommandation import RecommandationEnDB
from backend.dependencies.auth import get_current_user, verifier_roles
from backend.models.utilisateur import Role

router = APIRouter(tags=["recommendations"])

# Initialisation du client MongoDB
mongo_client = motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://mongo:27017"))
db = mongo_client[os.getenv("MONGODB_DB", "sante_db")]

def format_recommendation(doc: dict) -> dict:
    """Formate un document de recommandation brut en un format compatible avec le frontend."""
    try:
        # Extraire les champs avec des valeurs par défaut
        reco_id = str(doc.get('_id', ''))
        user_id = str(doc.get('user_id', ''))
        contenu = doc.get('contenu', '')
        
        # Déterminer le titre
        titre = doc.get('titre')
        if not titre and contenu:
            contenu_str = str(contenu)
            if "**" in contenu_str and "\n" in contenu_str:
                titre_part, _ = contenu_str.split("\n", 1)
                titre = titre_part.replace("**", "").strip()
            elif ":" in contenu_str:
                titre, _ = contenu_str.split(":", 1)
                titre = titre.strip()
            else:
                words = contenu_str.split()
                titre = ' '.join(words[:5]) + '...' if len(words) > 5 else contenu_str
        
        # Déterminer la description
        description = doc.get('description')
        if not description and contenu:
            description = str(contenu)
        
        # Valeurs par défaut si toujours pas de titre/description
        titre = titre or "Recommandation de santé"
        description = description or "Aucune description disponible"
        
        # Ajouter des émojis selon le contenu
        description_lower = description.lower()
        if any(term in description_lower for term in ["tachycardie", "cardiaque", "cœur", "coeur"]):
            titre = f"⚠️ {titre}"
        elif any(term in description_lower for term in ["hypoxie", "respiratoire", "oxygène", "oxygene"]):
            titre = f"🫁 {titre}"
        elif not any(emoji in titre for emoji in ["💡", "⚠️", "🫁"]):
            titre = f"💡 {titre}"
        
        # Formater la date
        date = doc.get('date', datetime.utcnow())
        if isinstance(date, str):
            try:
                date = datetime.fromisoformat(date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                date = datetime.utcnow()
        
        return {
            "id": reco_id,
            "user_id": user_id,
            "titre": titre[:100],  # Limiter la longueur
            "description": description[:500],
            "date": date.isoformat() if hasattr(date, 'isoformat') else date
        }
        
    except Exception as e:
        print(f"Erreur lors du formatage d'une recommandation (ID: {doc.get('_id', 'inconnu')}): {e}")
        # Retourner une recommandation minimale en cas d'erreur
        return {
            "id": str(doc.get('_id', '')),
            "user_id": str(doc.get('user_id', '')),
            "titre": "Recommandation de santé",
            "description": "Contenu non disponible",
            "date": datetime.utcnow().isoformat()
        }

@router.post("/recommendations", response_model=RecommandationEnDB, status_code=201,
             dependencies=[Depends(verifier_roles([Role.medecin, Role.admin]))])
async def creer_recommandation(reco: dict, current_user=Depends(get_current_user)):
    """Crée une recommandation pour un patient (utilisable par un médecin ou l'IA)."""
    try:
        # S'assurer que les champs requis sont présents
        if not isinstance(reco, dict):
            reco = reco.dict()
            
        # Préparer le document à insérer
        doc = {
            "user_id": str(reco.get('user_id', current_user.id)),
            "titre": reco.get('titre', 'Nouvelle recommandation'),
            "description": reco.get('description', ''),
            "contenu": reco.get('contenu', ''),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insérer le document directement dans MongoDB
        result = await db.recommandations.insert_one(doc)
        
        # Récupérer le document inséré
        inserted_doc = await db.recommandations.find_one({"_id": result.inserted_id})
        
        # Retourner le document formaté
        return format_recommendation(inserted_doc)
        
    except Exception as e:
        print(f"Erreur lors de la création d'une recommandation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de la recommandation: {str(e)}"
        )

@router.get("/recommendations", response_model=List[RecommandationEnDB])
async def lister_recommandations(current_user=Depends(get_current_user)):
    """Renvoie les recommandations du patient connecté.
    
    Le format de réponse est adapté pour correspondre aux attentes du frontend :
    - id: identifiant unique
    - user_id: ID du patient
    - titre: titre court de la recommandation
    - description: contenu détaillé
    - date: date de création
    """
    try:
        # Récupérer les documents bruts
        cursor = db.recommandations.find({
            "user_id": str(current_user.id), 
            "is_active": True
        })
        
        # Formater chaque recommandation
        recommendations = []
        async for doc in cursor:
            formatted = format_recommendation(doc)
            if formatted:
                recommendations.append(formatted)
        
        return recommendations
        
    except Exception as e:
        print(f"Erreur critique lors de la récupération des recommandations: {e}")
        # Retourner une liste vide en cas d'erreur critique
        return []


@router.patch("/recommandations/{reco_id}/marquer-vue")
async def marquer_recommandation_vue(reco_id: str, current_user=Depends(get_current_user)):
    """Marque une recommandation comme vue par l'utilisateur connecté."""
    from backend.models.utilisateur import Utilisateur, Role
    
    try:
        reco = await Recommandation.find_one(Recommandation.id == ObjectId(reco_id))
        if not reco:
            raise HTTPException(status_code=404, detail="Recommandation introuvable")
        
        # Vérifier les permissions selon le rôle
        if current_user.role == Role.medecin:
            # Pour un médecin : vérifier que le patient lui est assigné
            patient = await Utilisateur.find_one(Utilisateur.id == ObjectId(reco.user_id))
            if not patient or str(current_user.id) not in patient.medecin_ids:
                raise HTTPException(status_code=403, detail="Patient non assigné à ce médecin")
        elif current_user.role == Role.patient:
            # Pour un patient : vérifier que c'est sa propre recommandation
            if reco.user_id != str(current_user.id):
                raise HTTPException(status_code=403, detail="Accès non autorisé à cette recommandation")
        else:
            # Admin peut marquer toutes les recommandations comme vues
            pass
        
        # Marquer comme vue
        reco.statut = "vue"
        reco.vue_par = str(current_user.id)
        reco.date_vue = datetime.utcnow()
        reco.updated_at = datetime.utcnow()
        
        await reco.save()
        
        return {"message": "Recommandation marquée comme vue"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du marquage: {str(e)}")
