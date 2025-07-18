import { Route, Routes, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import LoginRegister from './pages/LoginRegister';
import Dashboard from './pages/Dashboard';
import Data from './pages/Data';

function PrivateRoute({ children }: { children: JSX.Element }) {
  const token = localStorage.getItem('token');
  if (!token) return <Navigate to="/auth" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/auth" element={<LoginRegister />} />
      <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
        <Route index element={<Dashboard />} />
        <Route path="data" element={<Data />} />
      </Route>
    </Routes>
  );
}

