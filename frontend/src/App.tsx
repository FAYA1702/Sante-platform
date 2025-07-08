import { Route, Routes, Navigate } from 'react-router-dom';
import LoginRegister from './pages/LoginRegister';
import Dashboard from './pages/Dashboard';
import { useEffect, useState } from 'react';

function PrivateRoute({ children }: { children: JSX.Element }) {
  const [token, setToken] = useState<string | null>(null);
  useEffect(() => {
    setToken(localStorage.getItem('token'));
  }, []);
  if (!token) return <Navigate to="/auth" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/auth" element={<LoginRegister />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />
    </Routes>
  );
}
