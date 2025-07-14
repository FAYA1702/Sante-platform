// Layout.tsx — Tailwind
import { Outlet, useNavigate } from 'react-router-dom';

export default function Layout() {
  const navigate = useNavigate();
  const isAuthenticated = Boolean(localStorage.getItem('token'));

  const logout = () => {
    localStorage.removeItem('token');
    navigate('/auth');
  };

  return (
    <>
      <header className="bg-slate-800 text-white">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <a href="/" className="text-lg font-semibold">
            Sante Platform
          </a>

          {isAuthenticated && (
            <nav className="flex items-center space-x-4">
              <a href="/" className="hover:text-slate-300">
                Tableau de bord
              </a>
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
        <Outlet />
      </main>
    </>
  );
}