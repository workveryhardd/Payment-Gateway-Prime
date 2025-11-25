import { useState } from 'react';
import api from '../lib/api';

interface Deposit {
  id: number;
  method: string;
  amount: number;
  utr_or_hash: string | null;
  status: string;
}

interface DepositFormProps {
  onSuccess: (deposit: Deposit) => void;
}

type DepositMethod = 'UPI' | 'BANK' | 'CRYPTO' | 'CARD' | 'PAYPAL';

export default function DepositForm({ onSuccess }: DepositFormProps) {
  const [method, setMethod] = useState<DepositMethod>('UPI');
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/deposits/create', {
        method,
        amount: parseFloat(amount),
      });
      onSuccess(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create deposit');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">Create Deposit</h2>
      {error && <div className="mb-4 text-red-600">{error}</div>}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Payment Method
        </label>
        <select
          value={method}
          onChange={(e) => setMethod(e.target.value as DepositMethod)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        >
          <option value="UPI">UPI</option>
          <option value="BANK">Bank Transfer (NEFT/IMPS/RTGS)</option>
          <option value="CRYPTO">Crypto</option>
          <option value="CARD">Credit / Debit Card</option>
          <option value="PAYPAL">Secure Online Payment</option>
        </select>
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Amount
        </label>
        <input
          type="number"
          step="0.01"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Creating...' : 'Create Deposit'}
      </button>
    </form>
  );
}

