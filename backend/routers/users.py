"""Routes liées à la gestion des utilisateurs et des rôles (RBAC)."""

from fastapi import APIRouter, Depends, HTTPException, status
from beanie import PydanticObjectId

from backend.dependencies.auth import get_current_user, verifier_roles
from backend.models.utilisateur import Utilisateur, Role
from backend.models import Department
from backend.schemas.utilisateur import UtilisateurPublic
from backend.schemas.role_update import RoleUpdate

router = APIRouter(prefix="/users", tags=["utilisateurs"])  # noqa: E305


async def enrichir_utilisateur_avec_departement(user: Utilisateur) -> UtilisateurPublic:
    """Enrichit un utilisateur avec les informations de département."""
    department_name = None
    department_code = None
    
    if user.department_id:
        try:
            # Essaie d'abord de récupérer le département par ObjectId
            department = await Department.get(user.department_id)
            if department:
                department_name = department.name
                department_code = department.code
        except Exception:
            # Si échec (ex: département par défaut avec string ID), utilise des valeurs par défaut
            if user.department_id == 'default-general':
                department_name = 'Médecine Générale'
                department_code = 'GENERAL'
            elif user.department_id == 'default-cardio':
                department_name = 'Cardiologie'
                department_code = 'CARDIO'
            elif user.department_id == 'default-pneumo':
                department_name = 'Pneumologie'
                department_code = 'PNEUMO'
            else:
                department_name = 'Département inconnu'
                department_code = 'UNKNOWN'
    
    return UtilisateurPublic(
        id=str(user.id),
        email=user.email,
        username=user.username,
        role=user.role,
        department_id=user.department_id,
        department_name=department_name,
        department_code=department_code
    )



# ---------------------------------------------------------------------------
# Routes ADMIN – CRUD complet des utilisateurs
# ---------------------------------------------------------------------------

@router.get("/", response_model=list[UtilisateurPublic], dependencies=[Depends(verifier_roles([Role.admin]))])
async def lister_utilisateurs(skip: int = 0, limit: int = 20, q: str | None = None):
    """Liste des utilisateurs avec pagination et recherche (admin).

    - **skip**: nombre d'éléments à ignorer
    - **limit**: taille de page (max 100)
    - **q**: filtre sur email ou username contenant la chaîne (insensible à la casse)
    """
    limit = min(limit, 100)
    filtre = {}
    if q:
        filtre = {"$or": [
            {"email": {"$regex": q, "$options": "i"}},
            {"username": {"$regex": q, "$options": "i"}},
        ]}
    cursor = Utilisateur.find(filtre).skip(skip).limit(limit)
    users = await cursor.to_list()
    # Enrichir chaque utilisateur avec les informations de département
    enriched_users = []
    for user in users:
        enriched_user = await enrichir_utilisateur_avec_departement(user)
        enriched_users.append(enriched_user)
    return enriched_users


from backend.schemas.utilisateur import UtilisateurAdminCreate, UtilisateurUpdate
from backend.utils.auth import hacher_mot_de_passe


@router.post("/", response_model=UtilisateurPublic, status_code=status.HTTP_201_CREATED,
              dependencies=[Depends(verifier_roles([Role.admin]))])
async def creer_utilisateur(payload: UtilisateurAdminCreate):
    """Création d'un utilisateur par un admin."""
    # Vérifie unicité email/username
    if await Utilisateur.find_one({"email": payload.email}):
        raise HTTPException(status_code=409, detail="Email déjà utilisé")
    if await Utilisateur.find_one({"username": payload.username}):
        raise HTTPException(status_code=409, detail="Nom d'utilisateur déjà utilisé")

    user = Utilisateur(
        email=payload.email,
        username=payload.username,
        mot_de_passe_hache=hacher_mot_de_passe(payload.mot_de_passe),
        role=payload.role,
        department_id=payload.department_id,
    )
    await user.insert()
    return await enrichir_utilisateur_avec_departement(user)


@router.patch("/{user_id}", response_model=UtilisateurPublic, dependencies=[Depends(verifier_roles([Role.admin]))])
async def mettre_a_jour_utilisateur(user_id: PydanticObjectId, payload: UtilisateurUpdate):
    """Mise à jour partielle d'un utilisateur (admin)."""
    user = await Utilisateur.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if payload.email is not None:
        # Conflit d'email
        if await Utilisateur.find_one({"email": payload.email, "_id": {"$ne": user.id}}):
            raise HTTPException(status_code=409, detail="Email déjà utilisé")
        user.email = payload.email
    if payload.username is not None:
        if await Utilisateur.find_one({"username": payload.username, "_id": {"$ne": user.id}}):
            raise HTTPException(status_code=409, detail="Nom d'utilisateur déjà utilisé")
        user.username = payload.username
    if payload.role is not None:
        user.role = payload.role
    if payload.department_id is not None:
        user.department_id = payload.department_id

    await user.save()
    return await enrichir_utilisateur_avec_departement(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(verifier_roles([Role.admin]))])
async def supprimer_utilisateur(user_id: PydanticObjectId):
    """Suppression d'un utilisateur (admin)."""
    user = await Utilisateur.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    await user.delete()
    return None


# ---------------------------------------------------------------------------
# Routes spécifiques existantes
# ---------------------------------------------------------------------------

@router.get("/patients", response_model=list[UtilisateurPublic],
            dependencies=[Depends(verifier_roles([Role.medecin, Role.admin]))])
async def lister_patients():
    """Retourne la liste des utilisateurs ayant le rôle patient (pour les médecins/admin)."""
    patients = await Utilisateur.find({"role": Role.patient}).to_list()
    return [UtilisateurPublic(id=str(u.id), email=u.email, username=u.username, role=u.role) for u in patients]


@router.get("/me", response_model=UtilisateurPublic)
async def lire_profil(utilisateur: Utilisateur = Depends(get_current_user)):
    """Renvoie le profil de l'utilisateur connecté."""
    return UtilisateurPublic(
        id=str(utilisateur.id),
        email=utilisateur.email,
        username=utilisateur.username,
        role=utilisateur.role,
    )


@router.patch("/{user_id}/role", response_model=UtilisateurPublic, status_code=status.HTTP_200_OK,
              dependencies=[Depends(verifier_roles([Role.admin]))])
async def changer_role(user_id: PydanticObjectId, payload: RoleUpdate):
    """Permet à un administrateur de changer le rôle d'un utilisateur donné."""
    user = await Utilisateur.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    user.role = payload.role
    await user.save()

    return UtilisateurPublic(
        id=str(user.id),
        email=user.email,
        username=user.username,
        role=user.role,
    )
