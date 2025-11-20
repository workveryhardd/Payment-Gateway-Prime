import { useState, useEffect } from 'react';
import api from '../lib/api';
import StatusBadge from '../components/StatusBadge';

interface PaymentAccount {
  id: number;
  account_type: string;
  identifier_name: string;
  status: string;
  details: any;
  is_active: boolean;
  created_at: string;
}

export default function PaymentAccountsPage() {
  const [accounts, setAccounts] = useState<PaymentAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    fetchAccounts();
  }, [filter]);

  const fetchAccounts = async () => {
    try {
      const response = await api.get('/admin/payment-accounts/');
      setAccounts(response.data);
    } catch (error) {
      console.error('Failed to fetch accounts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post('/admin/payment-accounts/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      alert(`Uploaded ${response.data.length} accounts successfully!`);
      fetchAccounts();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to upload file');
    } finally {
      setUploading(false);
      e.target.value = ''; // Reset file input
    }
  };

  const handleApprove = async (id: number) => {
    try {
      await api.post(`/admin/payment-accounts/${id}/approve`);
      fetchAccounts();
    } catch (error) {
      console.error('Failed to approve account:', error);
    }
  };

  const handleReject = async (id: number) => {
    try {
      await api.post(`/admin/payment-accounts/${id}/reject`);
      fetchAccounts();
    } catch (error) {
      console.error('Failed to reject account:', error);
    }
  };

  const handleActivate = async (id: number) => {
    if (!confirm('This will deactivate other accounts of the same type. Continue?')) {
      return;
    }
    try {
      await api.post(`/admin/payment-accounts/${id}/activate`);
      fetchAccounts();
    } catch (error) {
      console.error('Failed to activate account:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this account?')) {
      return;
    }
    try {
      await api.delete(`/admin/payment-accounts/${id}`);
      fetchAccounts();
    } catch (error) {
      console.error('Failed to delete account:', error);
    }
  };

  const filteredAccounts = filter === 'all' 
    ? accounts 
    : accounts.filter(acc => acc.account_type.toLowerCase() === filter);

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Payment Accounts Management</h1>
        <div className="flex gap-4">
          <label className="bg-blue-600 text-white px-4 py-2 rounded-md cursor-pointer hover:bg-blue-700">
            {uploading ? 'Uploading...' : 'Upload JSON File'}
            <input
              type="file"
              accept=".json"
              onChange={handleFileUpload}
              className="hidden"
              disabled={uploading}
            />
          </label>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg shadow">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Filter by Type
        </label>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md"
        >
          <option value="all">All</option>
          <option value="upi">UPI</option>
          <option value="bank">Bank</option>
          <option value="crypto">Crypto</option>
        </select>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Identifier</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Active</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Details</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredAccounts.map((account) => (
              <tr key={account.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{account.id}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{account.account_type}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                  {account.identifier_name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <StatusBadge status={account.status} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {account.is_active ? (
                    <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                      ACTIVE
                    </span>
                  ) : (
                    <span className="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                      Inactive
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  <details className="cursor-pointer">
                    <summary className="text-blue-600 hover:text-blue-800">View Details</summary>
                    <pre className="mt-2 p-2 bg-gray-50 rounded text-xs overflow-auto max-w-md">
                      {JSON.stringify(account.details, null, 2)}
                    </pre>
                  </details>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <div className="flex flex-col gap-1">
                    {account.status === 'PENDING' && (
                      <>
                        <button
                          onClick={() => handleApprove(account.id)}
                          className="text-green-600 hover:text-green-900 text-xs"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => handleReject(account.id)}
                          className="text-red-600 hover:text-red-900 text-xs"
                        >
                          Reject
                        </button>
                      </>
                    )}
                    {account.status === 'ACTIVE' && !account.is_active && (
                      <button
                        onClick={() => handleActivate(account.id)}
                        className="text-blue-600 hover:text-blue-900 text-xs"
                      >
                        Activate
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(account.id)}
                      className="text-red-600 hover:text-red-900 text-xs"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filteredAccounts.length === 0 && (
          <div className="text-center py-8 text-gray-500">No accounts found</div>
        )}
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">📝 JSON File Format</h3>
        <p className="text-sm text-blue-800 mb-2">
          Upload a JSON file with this structure (see <code className="bg-blue-100 px-1 rounded">backend/app/assets/payment_accounts_example.json</code>):
        </p>
        <pre className="bg-blue-100 p-3 rounded text-xs overflow-auto">
{`{
  "upi": [
    {
      "identifier_name": "id1",
      "upi_id": "yourupi@bank",
      "payee_name": "Business Name",
      "qr_location": "path/to/qr.jpg"
    }
  ],
  "bank": [
    {
      "identifier_name": "main_bank",
      "account_number": "...",
      "ifsc": "...",
      ...
    }
  ],
  "crypto": [...]
}`}
        </pre>
      </div>
    </div>
  );
}

