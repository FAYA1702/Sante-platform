import { useState, useEffect, useCallback } from 'react';
import { Outlet, useNavigate, Link, useLocation, NavLink as RouterNavLink, NavLinkProps } from 'react-router-dom';
import { PropsWithChildren, FC, ReactNode } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import ThemeToggle from './ThemeToggle';
import api from '../api';

type UserRole = 'patient' | 'medecin' | 'admin' | 'technicien';

interface NavItem {
  to: string;
  label: string;
  icon: ReactNode;
  show: boolean;
}

interface AuthState {
  isAuthenticated: boolean;
  role: UserRole | '';
  username: string;
  token?: string;
}

// Icons
const CloseIcon: FC = () => (
  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

const MenuIcon: FC = () => (
  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
  </svg>
);

const BellIcon: FC<{ count?: number }> = ({ count = 0 }) => (
  <div className="relative">
    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
    </svg>
    {count > 0 && (
      <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
        {count}
      </span>
    )}
  </div>
);

// Custom NavLink component with active state
const NavLink: FC<NavLinkProps & { children: ReactNode; className?: string }> = ({ 
  to, 
  children, 
  className = '',
  ...props 
}) => (
  <RouterNavLink
    to={to}
    className={({ isActive }) =>
      `block px-3 py-2 rounded-md text-base font-medium ${className} ${
        isActive
          ? 'bg-primary-50 text-primary-700 dark:bg-gray-700 dark:text-white'
          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white'
      }`
    }
    {...props}
  >
    {children}
  </RouterNavLink>
);

// Mobile menu button component
interface MobileMenuButtonProps {
  isOpen: boolean;
  onClick: () => void;
}

const MobileMenuButton: FC<MobileMenuButtonProps> = ({ isOpen, onClick }) => (
  <div className="flex items-center md:hidden">
    <button
      type="button"
      className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
      onClick={onClick}
      aria-expanded={isOpen}
    >
      <span className="sr-only">Open main menu</span>
      {isOpen ? <CloseIcon /> : <MenuIcon />}
    </button>
  </div>
);

// Footer component
const Footer: FC = () => (
  <footer className="bg-white dark:bg-gray-800 shadow-inner mt-auto">
    <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
      <div className="flex flex-col md:flex-row justify-between items-center">
        <div className="text-sm text-gray-600 dark:text-gray-400">
          &copy; {new Date().getFullYear()} Sante Platform. Tous droits réservés.
        </div>
        <div className="mt-2 md:mt-0 flex items-center">
          <button
            onClick={(e) => {
              e.preventDefault();
              // Handle privacy policy click
            }}
            className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
          >
            Politique de confidentialité
          </button>
          <span className="mx-2 text-gray-400">•</span>
          <button
            onClick={(e) => {
              e.preventDefault();
              // Handle terms of service click
            }}
            className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
          >
            Conditions d'utilisation
          </button>
        </div>
      </div>
    </div>
  </footer>
);

// Auth hook
export const useAuth = (): readonly [AuthState, () => void] => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    role: '',
    username: '',
    token: undefined
  });

  const updateAuth = useCallback(() => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setAuthState({
          isAuthenticated: true,
          role: payload.role || '',
          username: payload.username || '',
          token,
        });
        return;
      }
    } catch (e) {
      console.error('Erreur lors de la lecture du token:', e);
    }
    setAuthState({ isAuthenticated: false, role: '', username: '', token: undefined });
  }, []);

  useEffect(() => {
    updateAuth();
  }, [updateAuth]);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setAuthState({ isAuthenticated: false, role: '', username: '', token: undefined });
  }, []);

  return [authState, logout];
};

const Layout: FC<PropsWithChildren> = ({ children }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { theme } = useTheme();
  const [notifCount, setNotifCount] = useState(0);
  const [scrolled, setScrolled] = useState(false);
  const [pendingDoctorsCount, setPendingDoctorsCount] = useState(0);
  const [authState, logout] = useAuth();
  const { isAuthenticated, role, username } = authState;
  
  const navigate = useNavigate();
  const location = useLocation();

  // Listen for new alert events
  useEffect(() => {
    const listener = () => setNotifCount((c) => c + 1);
    window.addEventListener('new-alert', listener as EventListener);
    
    // Handle scroll for navbar effect
    const handleScroll = () => setScrolled(window.scrollY > 10);
    
    window.addEventListener('scroll', handleScroll);
    return () => {
      window.removeEventListener('new-alert', listener as EventListener);
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  // Fetch pending doctors count for admin
  useEffect(() => {
    const fetchPendingDoctorsCount = async () => {
      if (isAuthenticated && role === 'admin') {
        try {
          const response = await api.get('/admin/medecins-en-attente');
          setPendingDoctorsCount(response.data?.length || 0);
        } catch (error) {
          console.error('Erreur lors de la récupération des médecins en attente:', error);
        }
      }
    };

    fetchPendingDoctorsCount();
    
    // Refresh count every 30 seconds for admin
    const interval = isAuthenticated && role === 'admin' 
      ? setInterval(fetchPendingDoctorsCount, 30000)
      : null;

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isAuthenticated, role]);

  // Reset notification count
  const resetNotif = useCallback(() => {
    setNotifCount(0);
    const target = document.getElementById('alertes-section');
    if (target) {
      const y = target.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  }, []);

  const handleLogout = useCallback(() => {
    logout();
    navigate('/auth');
  }, [logout, navigate]);

  // Navigation items configuration
  const navItems: NavItem[] = [
    {
      to: "/",
      label: "Tableau de bord",
      icon: (
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
        />
      ),
      show: isAuthenticated,
    },
    {
      to: "/medecin",
      label: "Mes Patients",
      icon: (
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM9 9a2 2 0 11-4 0 2 2 0 014 0z"
        />
      ),
      show: isAuthenticated && role === 'medecin',
    },
    {
      to: "/data",
      label: "Données santé",
      icon: (
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        />
      ),
      show: isAuthenticated && role === 'patient', // Seuls les patients saisissent leurs données
    },
    {
      to: "/devices",
      label: "Appareils",
      icon: (
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
        />
      ),
      show: isAuthenticated && (role === 'admin' || role === 'technicien'),
    },
    {
      to: "/users",
      label: "Utilisateurs",
      icon: (
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
        />
      ),
      show: isAuthenticated && role === 'admin', // Seuls les admins gèrent les utilisateurs
    },
    {
      to: "/assignations",
      label: "Assignations",
      icon: (
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
        />
      ),
      show: isAuthenticated && (role === 'admin' || role === 'technicien' || role === 'medecin' || role === 'patient'),
    },
  ];

  return (
    <div className={`min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900 transition-colors duration-200 ${theme}`}>
      {/* Élément de test pour vérifier le chargement de Tailwind */}
      <div className="p-4 bg-blue-100 border-l-4 border-blue-500 text-blue-700 mb-4">
        <p className="font-bold">Test Tailwind CSS</p>
        <p>Si vous voyez ce message, Tailwind est correctement chargé.</p>
      </div>
      
      {/* Navigation Bar */}
      <header
        className={`fixed w-full z-50 transition-all duration-200 ${
          scrolled ? 'bg-white/95 dark:bg-gray-800/95 shadow-md' : 'bg-white dark:bg-gray-800 shadow-sm'
        }`}
        role="banner"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="flex-shrink-0 flex items-center">
                <span className="text-xl font-bold text-primary-600 dark:text-primary-400">SantePlatform</span>
              </Link>
              
              {/* Desktop Navigation */}
              <nav className="hidden md:ml-6 md:flex md:space-x-1">
                {navItems.map(
                  (item) =>
                    item.show && (
                      <NavLink key={item.to} to={item.to}>
                        <span className="flex items-center">
                          <svg className="mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            {item.icon}
                          </svg>
                          {item.label}
                        </span>
                      </NavLink>
                    )
                )}
              </nav>
            </div>

            <div className="flex items-center">
              {isAuthenticated ? (
                <div className="hidden md:flex items-center space-x-4">
                  {/* Admin: Pending doctors notification */}
                  {role === 'admin' && (
                    <Link
                      to="/?section=admin-approval"
                      className="relative p-2 rounded-lg text-gray-600 hover:text-gray-800 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
                      title={`${pendingDoctorsCount} médecin(s) en attente de validation`}
                    >
                      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      {pendingDoctorsCount > 0 && (
                        <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium">
                          {pendingDoctorsCount}
                        </span>
                      )}
                    </Link>
                  )}
                  
                  <button
                    onClick={resetNotif}
                    className="p-1 rounded-full text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    <BellIcon count={notifCount} />
                  </button>
                  
                  <div className="relative group">
                    <button className="flex items-center space-x-2 focus:outline-none">
                      <div className="h-8 w-8 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center text-primary-600 dark:text-primary-200 font-medium">
                        {(username || 'U').charAt(0).toUpperCase()}
                      </div>
                      <span className="hidden md:block text-sm font-medium text-gray-700 dark:text-gray-200">
                        {username}
                      </span>
                    </button>
                    
                    <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 origin-top-right z-10">
                      <div className="py-1" role="menu" aria-orientation="vertical">
                        <Link
                          to="/profile"
                          className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                          role="menuitem"
                        >
                          Mon profil
                        </Link>
                        <button
                          onClick={handleLogout}
                          className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/30"
                          role="menuitem"
                        >
                          Déconnexion
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center space-x-4">
                  <ThemeToggle />
                  <Link
                    to="/auth"
                    className="px-4 py-2 text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-200"
                  >
                    Connexion
                  </Link>
                  <Link
                    to="/auth/register"
                    className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Inscription
                  </Link>
                </div>
              )}

              {/* Mobile menu button */}
              <MobileMenuButton 
                isOpen={mobileMenuOpen}
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              />
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        <div className={`md:hidden ${mobileMenuOpen ? 'block' : 'hidden'}`}>
          <div className="pt-2 pb-3 space-y-1">
            {isAuthenticated ? (
              <>
                {/* User Profile Section */}
                <div className="px-4 pt-4 pb-3 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center">
                    <div className="h-10 w-10 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center text-primary-600 dark:text-primary-200 font-medium">
                      {(username || 'U').charAt(0).toUpperCase()}
                    </div>
                    <div className="ml-3">
                      <div className="text-base font-medium text-gray-800 dark:text-white">
                        {username}
                      </div>
                      <div className="text-sm font-medium text-gray-500 dark:text-gray-400 capitalize">
                        {role}
                      </div>
                    </div>
                    <div className="ml-auto flex items-center space-x-2">
                      {/* Admin: Pending doctors notification */}
                      {role === 'admin' && (
                        <Link
                          to="/?section=admin-approval"
                          className="relative p-1 rounded-full text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                          onClick={() => setMobileMenuOpen(false)}
                          title={`${pendingDoctorsCount} médecin(s) en attente de validation`}
                        >
                          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                          {pendingDoctorsCount > 0 && (
                            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center font-medium">
                              {pendingDoctorsCount}
                            </span>
                          )}
                        </Link>
                      )}
                      
                      <button
                        onClick={resetNotif}
                        className="p-1 rounded-full text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                      >
                        <BellIcon count={notifCount} />
                      </button>
                    </div>
                  </div>
                  <div className="mt-3 space-y-1">
                    <Link
                      to="/profile"
                      className="block px-4 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-700 rounded-md"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      Mon profil
                    </Link>
                    <button
                      onClick={() => {
                        handleLogout();
                        setMobileMenuOpen(false);
                      }}
                      className="block w-full text-left px-4 py-2 text-base font-medium text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/30 rounded-md"
                    >
                      Déconnexion
                    </button>
                  </div>
                </div>

                {/* Navigation Links */}
                <nav className="px-2 pt-2 pb-3 space-y-1">
                  {navItems.map(
                    (item) =>
                      item.show && (
                        <NavLink 
                          key={item.to} 
                          to={item.to}
                          onClick={() => setMobileMenuOpen(false)}
                        >
                          <span className="flex items-center">
                            <svg className="mr-3 h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              {item.icon}
                            </svg>
                            {item.label}
                          </span>
                        </NavLink>
                      )
                  )}
                </nav>
              </>
            ) : (
              <div className="px-2 pt-2 pb-3 space-y-1">
                <Link
                  to="/auth"
                  className="block px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-700"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Connexion
                </Link>
                <Link
                  to="/auth/register"
                  className="block px-3 py-2 text-base font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Inscription
                </Link>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 pt-16" role="main">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Outlet />
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Layout;
