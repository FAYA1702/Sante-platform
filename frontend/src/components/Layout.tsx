// Layout.tsx — Tailwind
import { Outlet, useNavigate, Link } from 'react-router-dom';
import { PropsWithChildren } from 'react';

export default function Layout({ children }: PropsWithChildren) {
  const navigate = useNavigate();
  // Récupération du rôle utilisateur depuis le JWT (pour menus conditionnels)
  let role = '';
  let username = '';
  try {
    const payload = JSON.parse(atob(localStorage.getItem('token')?.split('.')[1] || ''));
    role = payload.role || '';
    username = payload.username || '';
  } catch {}
  const isAuthenticated = Boolean(localStorage.getItem('token'));

  const logout = () => {
    localStorage.removeItem('token');
    navigate('/auth');
  };

  return (
    <>
      <header className="bg-slate-800 text-white">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="text-lg font-semibold">
            Sante Platform
          </Link>

          {/* Menus conditionnels selon le rôle utilisateur */}
          {isAuthenticated && (
            <nav className="flex items-center space-x-4">
              <Link to="/" className="hover:text-slate-300">
                Tableau de bord
              </Link>
              {/* Menu Gestion utilisateurs : admin uniquement */}
              {role === 'admin' && (
                <Link to="/users" className="hover:text-yellow-300 font-semibold">
                  Gestion utilisateurs
                </Link>
              )}
              {/* Menu Appareils : admin et technicien */}
              {(role === 'admin' || role === 'technicien') && (
                <Link to="/devices" className="hover:text-blue-300">
                  Appareils
                </Link>
              )}
              {/* Menu Données : patient et medecin */}
              {(role === 'patient' || role === 'medecin') && (
                <Link to="/data" className="hover:text-green-300">
                  Données santé
                </Link>
              )}
              {/* Badge rôle à droite */}
              <span className={`ml-3 px-2 py-1 rounded text-xs font-semibold bg-${role === 'admin' ? 'red' : role === 'medecin' ? 'green' : role === 'technicien' ? 'yellow' : 'blue'}-100 text-${role === 'admin' ? 'red' : role === 'medecin' ? 'green' : role === 'technicien' ? 'yellow' : 'blue'}-700 flex items-center`}>
                {/* Icône spéciale selon le rôle */}
                {role === 'admin' && <svg className="inline mr-1" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4" /><path d="M5.5 21a7.5 7.5 0 0 1 13 0" /><path d="M12 2v2m6 2l-1.5 1.5"/></svg>}
                {role === 'medecin' && <svg className="inline mr-1" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4" /><path d="M5.5 21a7.5 7.5 0 0 1 13 0" /><path d="M12 12v4m0 0h4m-4 0h-4"/></svg>}
                {role === 'technicien' && <svg className="inline mr-1" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4" /><path d="M5.5 21a7.5 7.5 0 0 1 13 0" /><path d="M16 2l2 2m-2 0l2-2"/></svg>}
                {role === 'patient' && <svg className="inline mr-1" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4" /><path d="M5.5 21a7.5 7.5 0 0 1 13 0" /></svg>}
                {role.charAt(0).toUpperCase() + role.slice(1)}
              </span>
              {/* Bouton d’aide adapté au rôle */}
              <button
                className={`flex items-center gap-2 px-3 py-1 rounded bg-${role === 'admin' ? 'red' : role === 'medecin' ? 'green' : role === 'technicien' ? 'yellow' : 'blue'}-600 hover:bg-${role === 'admin' ? 'red' : role === 'medecin' ? 'green' : role === 'technicien' ? 'yellow' : 'blue'}-700 text-white font-semibold shadow transition`}
                onClick={() => window.open(role === 'admin' ? 'mailto:support@sante-platform.fr?subject=Aide%20admin' : role === 'medecin' ? 'mailto:support@sante-platform.fr?subject=Aide%20médecin' : role === 'technicien' ? 'mailto:support@sante-platform.fr?subject=Aide%20technicien' : 'mailto:support@sante-platform.fr?subject=Aide%20patient', '_blank')}
                title={role === 'admin' ? "Contacter l’assistance admin" : role === 'medecin' ? "Contacter l’assistance médecin" : role === 'technicien' ? "Contacter l’assistance technicien" : "Contacter l’assistance patient"}
              >
                Aide
              </button>
              <button
                onClick={logout}
                className="px-3 py-1 rounded bg-red-600 hover:bg-red-700 text-sm"
              >
                Déconnexion
              </button>
            </nav>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {children ?? <Outlet />}
      </main>
    </>
  );
}