"""Routeur pour la consultation des recommandations."""

from typing import List

from fastapi import APIRouter, Depends


from backend.models.recommandation import Recommandation
from backend.schemas.recommandation import RecommandationEnDB, RecommandationCreation

from backend.dependencies.auth import get_current_user, verifier_roles
from backend.models.utilisateur import Role

router = APIRouter(tags=["recommendations"])




@router.post("/recommendations", response_model=RecommandationEnDB, status_code=201,
             dependencies=[Depends(verifier_roles([Role.medecin, Role.admin]))])
async def creer_recommandation(reco: RecommandationCreation, current_user=Depends(get_current_user)):
    """Crée une recommandation pour un patient (utilisable par un médecin ou l’IA)."""
    doc = Recommandation(user_id=reco.user_id if hasattr(reco, 'user_id') else str(current_user.id),
                         titre=reco.titre, description=reco.description, date=reco.date)
    await doc.insert()
    return RecommandationEnDB(id=str(doc.id), user_id=doc.user_id, titre=doc.titre, description=doc.description, date=doc.date)


@router.get("/recommendations", response_model=List[RecommandationEnDB])
async def lister_recommandations(current_user=Depends(get_current_user)):
    """Renvoie les recommandations du patient connecté.
    Si aucune recommandation n'est trouvée, renvoie une liste vide (le frontend affichera des exemples fictifs).
    
    Le format de réponse est adapté pour correspondre aux attentes du frontend :
    - id: identifiant unique
    - titre: titre court de la recommandation
    - description: contenu détaillé
    - date: date de création
    """
    # Récupérer toutes les recommandations actives pour l'utilisateur
    docs = await Recommandation.find({"user_id": str(current_user.id), "is_active": True}).to_list()
    
    # Si pas de recommandations, on retourne une liste vide
    if not docs:
        return []
        
    recommendations = []
    for d in docs:
        try:
            # Vérifier si la recommandation a un titre et un contenu séparés
            if hasattr(d, 'titre') and hasattr(d, 'contenu'):
                titre = d.titre
                description = d.contenu
            # Sinon, essayer d'extraire un titre du contenu
            else:
                contenu = getattr(d, 'contenu', 'Recommandation de santé personnalisée')
                
                # Essayer de détecter un titre dans le contenu
                if isinstance(contenu, str):
                    # Format avec **titre**
                    if "**" in contenu and "\n" in contenu:
                        titre_part, *desc_parts = contenu.split("\n", 1)
                        titre = titre_part.replace("**", "").strip()
                        description = desc_parts[0].strip() if desc_parts else ""
                    # Format avec :
                    elif ":" in contenu:
                        titre_part, *desc_parts = contenu.split(":", 1)
                        titre = titre_part.strip()
                        description = desc_parts[0].strip() if desc_parts else ""
                    # Format par défaut
                    else:
                        # Prendre les premiers mots comme titre
                        words = contenu.split()
                        if len(words) > 5:
                            titre = ' '.join(words[:5]) + '...'
                            description = contenu
                        else:
                            titre = contenu
                            description = ""
                else:
                    titre = "Recommandation de santé"
                    description = str(contenu)
            
            # Ajouter des émojis selon le type d'alerte
            contenu_lower = str(contenu).lower()
            if any(term in contenu_lower for term in ["tachycardie", "cardiaque", "cœur", "coeur"]):
                titre = f"⚠️ {titre}"
            elif any(term in contenu_lower for term in ["hypoxie", "respiratoire", "oxygène", "oxygene"]):
                titre = f"🫁 {titre}"
            elif not titre.startswith(('💡', '⚠️', '🫁')):
                titre = f"💡 {titre}"
            
            # Formater la date correctement
            date_value = getattr(d, 'date', None)
            if hasattr(date_value, 'isoformat'):
                date_str = date_value.isoformat()
            elif isinstance(date_value, str):
                date_str = date_value
            else:
                date_str = ""
            
            recommendations.append({
                "id": str(d.id),
                "titre": titre[:100],  # Limiter la longueur du titre
                "description": description[:500],  # Limiter la longueur de la description
                "date": date_str
            })
            
        except Exception as e:
            print(f"Erreur lors du traitement d'une recommandation: {e}")
            continue
            
    return recommendations
