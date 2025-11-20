import { useState, useEffect } from 'react';
import api from '../lib/api';
import DepositForm from '../components/DepositForm';

interface Deposit {
  id: number;
  method: string;
  amount: number;
  utr_or_hash: string | null;
  status: string;
}

export default function DepositPage() {
  const [currentDeposit, setCurrentDeposit] = useState<Deposit | null>(null);
  const [utr, setUtr] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [instructions, setInstructions] = useState<any>(null);

  useEffect(() => {
    fetchInstructions();
  }, []);

  const fetchInstructions = async () => {
    // In a real app, these would come from the backend API
    // For now, we'll use placeholder data
    setInstructions({
      upi: { id: 'yourupi@bank', name: 'Your Business Name' },
      bank: {
        account: '123456789012',
        ifsc: 'BANK0001234',
        bank: 'Bank Name',
        branch: 'Branch Name',
      },
      crypto: {
        btc: 'bc1qexamplebtcaddress000000000000000000',
        eth: '0xExampleEthereumAddress0000000000000000000000',
        usdt_trc20: 'TYExampleTronAddress0000000000000000',
        usdt_erc20: '0xExampleERC20Address00000000000000000000',
        usdt_bep20: '0xExampleBSCAddress000000000000000000000',
      },
    });
  };

  const handleDepositCreated = (deposit: Deposit) => {
    setCurrentDeposit(deposit);
  };

  const handleSubmitProof = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentDeposit) return;

    setLoading(true);
    setError('');

    try {
      await api.post('/deposits/submit-proof', {
        deposit_id: currentDeposit.id,
        utr_or_hash: utr,
      });
      setCurrentDeposit(null);
      setUtr('');
      alert('Proof submitted successfully!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit proof');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Create Deposit</h1>
      
      {!currentDeposit ? (
        <DepositForm onSuccess={handleDepositCreated} />
      ) : (
        <div className="space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h2 className="text-lg font-semibold text-green-800 mb-2">
              Deposit Created Successfully!
            </h2>
            <p className="text-green-700">
              Deposit ID: {currentDeposit.id} | Amount: ₹{currentDeposit.amount} | Method: {currentDeposit.method}
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Payment Instructions</h2>
            {currentDeposit.method === 'UPI' && instructions?.upi && (
              <div className="space-y-4">
                <div>
                  <p className="text-gray-700 mb-2">Pay to UPI ID:</p>
                  <p className="text-lg font-mono font-semibold text-blue-600">{instructions.upi.upi_id || instructions.upi.id}</p>
                  <p className="text-sm text-gray-600">Payee: {instructions.upi.payee_name || instructions.upi.name}</p>
                  {instructions.upi.identifier_name && (
                    <p className="text-xs text-gray-500">Account: {instructions.upi.identifier_name}</p>
                  )}
                </div>
                <div className="flex justify-center">
                  <img 
                    src="/api/payment/qr-code" 
                    alt="UPI QR Code" 
                    className="w-64 h-64 border-2 border-gray-300 rounded-lg"
                    onError={(e) => {
                      // Hide image if it fails to load
                      e.currentTarget.style.display = 'none';
                    }}
                  />
                </div>
                <p className="text-xs text-gray-500 text-center">Scan this QR code with any UPI app to pay</p>
              </div>
            )}
            {currentDeposit.method === 'BANK' && instructions?.bank && (
              <div className="space-y-2">
                <p className="text-gray-700">Bank Transfer Details:</p>
                {instructions.bank.identifier_name && (
                  <p className="text-xs text-gray-500">Account: {instructions.bank.identifier_name}</p>
                )}
                <div className="bg-gray-50 p-4 rounded">
                  <p><strong>Account Number:</strong> {instructions.bank.account_number || instructions.bank.account}</p>
                  <p><strong>IFSC:</strong> {instructions.bank.ifsc}</p>
                  <p><strong>Bank:</strong> {instructions.bank.bank_name || instructions.bank.bank}</p>
                  {instructions.bank.branch && (
                    <p><strong>Branch:</strong> {instructions.bank.branch}</p>
                  )}
                </div>
              </div>
            )}
            {currentDeposit.method === 'CRYPTO' && instructions?.crypto && (
              <div className="space-y-4">
                <p className="text-gray-700">Crypto Wallet Addresses:</p>
                {instructions.crypto.identifier_name && (
                  <p className="text-xs text-gray-500">Account: {instructions.crypto.identifier_name}</p>
                )}
                <div className="bg-gray-50 p-4 rounded space-y-2">
                  {instructions.crypto.btc && (
                    <div>
                      <p className="font-semibold">BTC:</p>
                      <p className="font-mono text-sm break-all">{instructions.crypto.btc}</p>
                    </div>
                  )}
                  {instructions.crypto.eth && (
                    <div>
                      <p className="font-semibold">ETH:</p>
                      <p className="font-mono text-sm break-all">{instructions.crypto.eth}</p>
                    </div>
                  )}
                  {instructions.crypto.usdt_trc20 && (
                    <div>
                      <p className="font-semibold">USDT (TRC20):</p>
                      <p className="font-mono text-sm break-all">{instructions.crypto.usdt_trc20}</p>
                    </div>
                  )}
                  {instructions.crypto.usdt_erc20 && (
                    <div>
                      <p className="font-semibold">USDT (ERC20):</p>
                      <p className="font-mono text-sm break-all">{instructions.crypto.usdt_erc20}</p>
                    </div>
                  )}
                  {instructions.crypto.usdt_bep20 && (
                    <div>
                      <p className="font-semibold">USDT (BEP20):</p>
                      <p className="font-mono text-sm break-all">{instructions.crypto.usdt_bep20}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Submit Payment Proof</h2>
            {error && <div className="mb-4 text-red-600">{error}</div>}
            <form onSubmit={handleSubmitProof}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  UTR / Reference Number / Transaction Hash
                </label>
                <input
                  type="text"
                  value={utr}
                  onChange={(e) => setUtr(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="Enter UTR, reference number, or transaction hash"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Submitting...' : 'Submit Proof'}
              </button>
            </form>
            <button
              onClick={() => setCurrentDeposit(null)}
              className="mt-4 w-full bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300"
            >
              Create Another Deposit
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

