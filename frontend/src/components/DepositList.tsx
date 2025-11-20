import { useEffect, useState } from 'react';
import api from '../lib/api';
import StatusBadge from './StatusBadge';

interface Deposit {
  id: number;
  method: string;
  amount: number;
  utr_or_hash: string | null;
  status: string;
  created_at: string;
  verified_at: string | null;
}

interface DepositListProps {
  isAdmin?: boolean;
}

export default function DepositList({ isAdmin = false }: DepositListProps) {
  const [deposits, setDeposits] = useState<Deposit[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDeposits();
  }, []);

  const fetchDeposits = async () => {
    try {
      const endpoint = isAdmin ? '/admin/deposits' : '/deposits/my';
      const response = await api.get(endpoint);
      setDeposits(response.data);
    } catch (error) {
      console.error('Failed to fetch deposits:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  if (deposits.length === 0) {
    return <div className="text-center py-8 text-gray-500">No deposits found</div>;
  }

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">UTR/Hash</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {deposits.map((deposit) => (
            <tr key={deposit.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{deposit.id}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{deposit.method}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{deposit.amount}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {deposit.utr_or_hash || '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <StatusBadge status={deposit.status} />
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(deposit.created_at).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

