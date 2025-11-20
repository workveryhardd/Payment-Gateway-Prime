import { Outlet, Link } from 'react-router-dom';
// AUTHENTICATION DISABLED - Logout removed
// import { removeToken } from '../lib/auth';

export default function Layout() {
  // AUTHENTICATION DISABLED - No logout needed
  // const navigate = useNavigate();
  // const handleLogout = () => {
  //   removeToken();
  //   navigate('/login');
  // };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link to="/" className="flex items-center px-2 py-2 text-gray-700 hover:text-gray-900">
                Dashboard
              </Link>
              <Link to="/deposit" className="flex items-center px-2 py-2 text-gray-700 hover:text-gray-900">
                Create Deposit
              </Link>
              <Link to="/admin" className="flex items-center px-2 py-2 text-gray-700 hover:text-gray-900">
                Admin
              </Link>
              <Link to="/admin/payment-accounts" className="flex items-center px-2 py-2 text-gray-700 hover:text-gray-900">
                Payment Accounts
              </Link>
            </div>
            {/* AUTHENTICATION DISABLED - Logout button removed */}
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}

