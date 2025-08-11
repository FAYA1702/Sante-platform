"""Script de migration pour ajouter les départements et enrichir les utilisateurs existants.
Migration douce qui préserve toutes les données existantes.
"""

import asyncio
from datetime import datetime
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from ..models import Department, Utilisateur
from ..settings import MONGODB_URL, DATABASE_NAME


async def create_default_departments():
    """Créer les départements par défaut."""
    departments_data = [
        {
            "name": "Médecine Générale",
            "code": "GENERAL",
            "description": "Médecine générale et soins de première ligne"
        },
        {
            "name": "Cardiologie",
            "code": "CARDIO",
            "description": "Spécialité des maladies cardiovasculaires"
        },
        {
            "name": "Ophtalmologie",
            "code": "OPHTALMO",
            "description": "Spécialité des maladies des yeux"
        },
        {
            "name": "Odontologie",
            "code": "DENTAIRE",
            "description": "Soins dentaires et chirurgie buccale"
        },
        {
            "name": "Pédiatrie",
            "code": "PEDIATRIE",
            "description": "Médecine des enfants et adolescents"
        },
        {
            "name": "Dermatologie",
            "code": "DERMATO",
            "description": "Spécialité des maladies de la peau"
        }
    ]
    
    created_departments = []
    for dept_data in departments_data:
        # Vérifier si le département existe déjà
        existing = await Department.find_one({"code": dept_data["code"]})
        if not existing:
            department = Department(**dept_data)
            await department.insert()
            created_departments.append(department)
            print(f"✅ Département créé: {department.name} ({department.code})")
        else:
            created_departments.append(existing)
            print(f"ℹ️  Département existant: {existing.name} ({existing.code})")
    
    return created_departments


async def migrate_existing_users(departments):
    """Migrer les utilisateurs existants sans département."""
    # Trouver le département "Médecine Générale" par défaut
    general_dept = next((d for d in departments if d.code == "GENERAL"), None)
    if not general_dept:
        print("❌ Département 'Médecine Générale' non trouvé")
        return
    
    # Migrer les médecins sans département
    medecins_sans_dept = await Utilisateur.find({
        "role": "medecin",
        "department_id": None
    }).to_list()
    
    for medecin in medecins_sans_dept:
        medecin.department_id = str(general_dept.id)
        medecin.updated_at = datetime.utcnow()
        await medecin.save()
        print(f"✅ Médecin assigné à Médecine Générale: {medecin.username}")
    
    # Les patients restent sans département (assignation à la demande)
    patients_count = await Utilisateur.find({"role": "patient"}).count()
    print(f"ℹ️  {patients_count} patients conservent leur statut (assignation à la demande)")
    
    # Statistiques finales
    admins_count = await Utilisateur.find({"role": "admin"}).count()
    techniciens_count = await Utilisateur.find({"role": "technicien"}).count()
    
    print(f"ℹ️  {admins_count} admins et {techniciens_count} techniciens (accès global)")


async def main():
    """Fonction principale de migration."""
    print("🚀 Début de la migration des départements...")
    
    # Connexion à MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    database = client[DATABASE_NAME]
    
    # Initialiser Beanie avec tous les modèles
    from ..models import Device, Donnee, Alerte, Recommandation
    await init_beanie(
        database=database,
        document_models=[
            Utilisateur, Device, Donnee, Alerte, Recommandation,
            Department  # Nouveau modèle
        ]
    )
    
    try:
        # Étape 1: Créer les départements par défaut
        print("\n📋 Étape 1: Création des départements...")
        departments = await create_default_departments()
        
        # Étape 2: Migrer les utilisateurs existants
        print("\n👥 Étape 2: Migration des utilisateurs existants...")
        await migrate_existing_users(departments)
        
        print("\n✅ Migration terminée avec succès!")
        print(f"   - {len(departments)} départements disponibles")
        print("   - Médecins assignés au département Médecine Générale")
        print("   - Patients prêts pour assignation à la demande")
        print("   - Toutes les données existantes préservées")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
