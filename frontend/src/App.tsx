import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
// AUTHENTICATION DISABLED - Login page removed, all pages accessible
// import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import DepositPage from './pages/DepositPage';
import AdminDepositsPage from './pages/AdminDepositsPage';
import PaymentAccountsPage from './pages/PaymentAccountsPage';
import Layout from './components/Layout';

function App() {
  return (
    <Router>
      <Routes>
        {/* Login route removed - authentication disabled */}
        <Route path="/login" element={<Navigate to="/" replace />} />
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="deposit" element={<DepositPage />} />
          <Route path="admin" element={<AdminDepositsPage />} />
          <Route path="admin/payment-accounts" element={<PaymentAccountsPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;

