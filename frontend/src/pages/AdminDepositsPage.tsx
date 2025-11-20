import { useState, useEffect } from 'react';
import api from '../lib/api';
import StatusBadge from '../components/StatusBadge';

interface Deposit {
  id: number;
  user_id: number;
  method: string;
  amount: number;
  utr_or_hash: string | null;
  status: string;
  created_at: string;
  verified_at: string | null;
}

interface LedgerEntry {
  id: number;
  source: string;
  method: string;
  utr_or_hash: string;
  amount: number;
  sender: string | null;
  timestamp: string;
  matched: boolean;
}

export default function AdminDepositsPage() {
  const [deposits, setDeposits] = useState<Deposit[]>([]);
  const [ledgerEntries, setLedgerEntries] = useState<LedgerEntry[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [statusFilter]);

  const fetchData = async () => {
    try {
      const [depositsRes, ledgerRes] = await Promise.all([
        api.get('/admin/deposits', { params: statusFilter ? { status: statusFilter } : {} }),
        api.get('/admin/incoming-ledger', { params: { matched: false } }),
      ]);
      setDeposits(depositsRes.data);
      setLedgerEntries(ledgerRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: number) => {
    try {
      await api.post(`/admin/deposits/${id}/approve`);
      fetchData();
    } catch (error) {
      console.error('Failed to approve deposit:', error);
    }
  };

  const handleReject = async (id: number) => {
    try {
      await api.post(`/admin/deposits/${id}/reject`);
      fetchData();
    } catch (error) {
      console.error('Failed to reject deposit:', error);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Admin - Deposits Management</h1>

      <div className="bg-white p-4 rounded-lg shadow">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Filter by Status
        </label>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md"
        >
          <option value="">All</option>
          <option value="PENDING">PENDING</option>
          <option value="SUCCESS">SUCCESS</option>
          <option value="FAILED">FAILED</option>
          <option value="FLAGGED">FLAGGED</option>
        </select>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Deposits</h2>
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">UTR/Hash</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {deposits.map((deposit) => (
                <tr key={deposit.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{deposit.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{deposit.user_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{deposit.method}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{deposit.amount}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {deposit.utr_or_hash || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <StatusBadge status={deposit.status} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {deposit.status === 'PENDING' && (
                      <div className="space-x-2">
                        <button
                          onClick={() => handleApprove(deposit.id)}
                          className="text-green-600 hover:text-green-900"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => handleReject(deposit.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Reject
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Unmatched Ledger Entries</h2>
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">UTR/Hash</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sender</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {ledgerEntries.map((entry) => (
                <tr key={entry.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{entry.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{entry.source}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{entry.method}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500">
                    {entry.utr_or_hash}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{entry.amount}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{entry.sender || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(entry.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

