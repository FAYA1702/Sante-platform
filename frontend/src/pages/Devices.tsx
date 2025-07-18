import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Loader from '../components/Loader';

/**
 * Page Appareils (protégée RBAC frontend)
 * Seuls les administrateurs et techniciens peuvent accéder à cette page.
 */
export default function Devices() {
  const navigate = useNavigate();
  let role = '';
  try {
    const payload = JSON.parse(atob(localStorage.getItem('token')?.split('.')[1] || ''));
    role = payload.role || '';
  } catch {}

  const [showAlert, setShowAlert] = useState(false);
  useEffect(() => {
    if (role !== 'admin' && role !== 'technicien') {
      setShowAlert(true);
      setTimeout(() => {
        setShowAlert(false);
        navigate('/');
      }, 2000);
    }
  }, [role, navigate]);

  if (role !== 'admin' && role !== 'technicien') return (
    <>
      {showAlert && (
        <div style={{position: 'fixed', top: 24, left: '50%', transform: 'translateX(-50%)', zIndex: 50}}>
          <div className="bg-red-100 border border-red-300 text-red-800 px-6 py-3 rounded shadow-lg flex items-center gap-3 animate-fade-in">
            <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" className="fill-red-200" />
              <path d="M12 8v4m0 4h.01" strokeLinecap="round" />
            </svg>
            <span className="font-semibold">Accès refusé : seuls les administrateurs et techniciens peuvent accéder à la gestion des appareils.</span>
          </div>
        </div>
      )}
      <Loader />
    </>
  );

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Gestion des appareils</h1>
      {/* Ici, tu ajoutes la liste, création, édition des appareils... */}
      <p>Seuls les administrateurs et techniciens peuvent voir cette page.</p>
    </div>
  );
}
