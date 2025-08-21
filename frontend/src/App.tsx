import React, { ReactElement } from 'react';
import { Route, Routes, Navigate, useLocation } from 'react-router-dom';
import './config/chart';

// Composants
import Layout from './components/Layout';
import LoginRegister from './pages/LoginRegister';
import Dashboard from './pages/Dashboard';
import Data from './pages/Data';
import Devices from './pages/Devices';
import Users from './pages/Users';
import PatientPage from './pages/PatientPage';
import MedecinDashboard from './pages/MedecinDashboard';
import TechnicienAssignations from './pages/TechnicienAssignations';
import PatientProfile from './pages/PatientProfile';
// import Recommendations from './pages/Recommendations'; // Fichier supprimé

// Lecture du mode (demo | production)
const IS_DEMO = import.meta.env.VITE_APP_MODE === 'demo';

/**
 * Route privée avec contrôle de rôle.
 * allowedRoles : rôles autorisés (par défaut tous).
 */
import { PropsWithChildren } from 'react';

interface PrivateRouteProps extends PropsWithChildren {
  allowedRoles?: string[];
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({
  children,
  allowedRoles = ['patient', 'medecin', 'technicien', 'admin'],
}) => {
  const location = useLocation();
  const token = localStorage.getItem('token');
  
  // Vider le localStorage si token invalide après nettoyage DB
  if (!token) {
    localStorage.clear();
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const role = payload.role as string;
    const userId = payload.sub || payload.user_id;

    // Vérifier si le token est encore valide (utilisateur existe)
    if (!userId) {
      localStorage.clear();
      return <Navigate to="/auth" state={{ from: location }} replace />;
    }

    // En mode démo, l'admin a tous les droits
    if (IS_DEMO && role === 'admin') return children;
    if (!allowedRoles.includes(role)) {
      return <Navigate to="/" state={{ from: location }} replace />;
    }
    return children;
  } catch (err) {
    console.error('Token JWT invalide', err);
    localStorage.clear();
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }
};

/**
 * Accès aux données santé.
 * Prod : patient & medecin.
 * Démo : + admin.
 */
const HealthDataRoute: React.FC<PropsWithChildren> = ({ children }) => (
  <PrivateRoute
    allowedRoles={IS_DEMO ? ['patient', 'medecin', 'admin'] : ['patient', 'medecin']}
  >
    {children}
  </PrivateRoute>
);

export default function App() {
  return (
    <Routes>
      <Route path="/auth" element={<LoginRegister />} />
      <Route path="/users" element={<Users />} />
      <Route path="/data" element={<Data />} />
      <Route path="/devices" element={<Devices />} />
      {/* <Route path="/assignments" element={<Assignations />} /> */}
      {/* <Route path="/recommendations" element={<Recommendations />} /> */}
      <Route path="/medecin" element={<MedecinDashboard />} />
      <Route path="/profile" element={<PatientProfile />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route
          path="medecin"
          element={
            <PrivateRoute allowedRoles={['medecin']}>
              <MedecinDashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="data"
          element={
            <HealthDataRoute>
              <Data />
            </HealthDataRoute>
          }
        />
        <Route
          path="devices"
          element={
            <PrivateRoute allowedRoles={['technicien', 'admin']}>
              <Devices />
            </PrivateRoute>
          }
        />
        <Route
          path="users"
          element={
            <PrivateRoute allowedRoles={['admin']}>
              <Users />
            </PrivateRoute>
          }
        />
        <Route path="patients/:id" element={<PatientPage />} />
        <Route path="/assignations" element={
              <PrivateRoute allowedRoles={['technicien']}>
                <TechnicienAssignations />
              </PrivateRoute>
            } />
      </Route>
    </Routes>
  );
}