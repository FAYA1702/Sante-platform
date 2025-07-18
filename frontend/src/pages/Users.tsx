
/**
 * Comment utiliser / tester la protection RBAC frontend sur /users :
 * 1. Connecte-toi avec un compte non-admin (patient, technicien, médecin).
 * 2. Essaie d’accéder à /users via l’URL (barre d’adresse ou lien direct).
 * 3. Tu verras une alerte « Accès refusé » et tu seras immédiatement redirigé vers le dashboard.
 *
 * Cette protection empêche tout utilisateur non autorisé de consulter ou manipuler la gestion des utilisateurs,
 * même en cas de tentative d’accès direct par l’URL.
 */
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Loader from '../components/Loader';

/**
 * Page Gestion utilisateurs (protégée RBAC frontend)
 * Seul un administrateur peut accéder à cette page.
 */
export default function Users() {
  const navigate = useNavigate();
  let role = '';
  try {
    const payload = JSON.parse(atob(localStorage.getItem('token')?.split('.')[1] || ''));
    role = payload.role || '';
  } catch {}

  const [showAlert, setShowAlert] = useState(false);
  useEffect(() => {
    if (role !== 'admin') {
      setShowAlert(true);
      setTimeout(() => {
        setShowAlert(false);
        navigate('/');
      }, 2000); // Affiche l’alerte 2s puis redirige
    }
  }, [role, navigate]);

  if (role !== 'admin') return (
    <>
      {showAlert && (
        <div style={{position: 'fixed', top: 24, left: '50%', transform: 'translateX(-50%)', zIndex: 50}}>
          <div className="bg-red-100 border border-red-300 text-red-800 px-6 py-3 rounded shadow-lg flex items-center gap-3 animate-fade-in">
            <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" className="fill-red-200" />
              <path d="M12 8v4m0 4h.01" strokeLinecap="round" />
            </svg>
            <span className="font-semibold">Accès refusé : seuls les administrateurs peuvent accéder à la gestion des utilisateurs.</span>
          </div>
        </div>
      )}
      <Loader />
    </>
  );

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Gestion des utilisateurs</h1>
      {/* Ici, tu ajoutes la liste, création, édition des utilisateurs... */}
      <p>Seuls les administrateurs peuvent voir cette page.</p>
    </div>
  );
}
