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
  if (!token) return <Navigate to="/auth" state={{ from: location }} replace />;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const role = payload.role as string;

    // En mode démo, l'admin a tous les droits
    if (IS_DEMO && role === 'admin') return children;
    if (!allowedRoles.includes(role)) {
      return <Navigate to="/" state={{ from: location }} replace />;
    }
    return children;
  } catch (err) {
    console.error('Token JWT invalide', err);
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
      <Route
        path="/*"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Dashboard />} />
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
      </Route>
    </Routes>
  );
}