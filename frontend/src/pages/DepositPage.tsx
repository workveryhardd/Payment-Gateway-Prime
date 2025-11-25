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
    
    // Handle PayPal return
    const urlParams = new URLSearchParams(window.location.search);
    const paymentId = urlParams.get('paymentId');
    const payerId = urlParams.get('PayerID');
    const depositId = urlParams.get('deposit_id');
    const paymentSuccess = urlParams.get('payment_success');
    const paymentCancelled = urlParams.get('payment_cancelled');
    
    if (paymentSuccess === 'true' && paymentId && payerId && depositId) {
      // Execute PayPal payment
      handlePayPalExecute(parseInt(depositId), paymentId, payerId);
    } else if (paymentCancelled === 'true') {
      setError('Payment was cancelled. Please try again.');
    }
  }, []);
  
  const handlePayPalExecute = async (depositId: number, paymentId: string, payerId: string) => {
    try {
      setLoading(true);
      const response = await api.post('/paypal/execute', {
        payment_id: paymentId,
        payer_id: payerId,
        deposit_id: depositId,
      });
      
      if (response.data.success) {
        alert('Payment completed successfully!');
        setCurrentDeposit(null);
        // Clean URL
        window.history.replaceState({}, document.title, '/deposit');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to complete payment');
    } finally {
      setLoading(false);
    }
  };

  const fetchInstructions = async () => {
    try {
      const response = await api.get('/payment/payment-instructions');
      setInstructions(response.data);
    } catch (error) {
      console.error('Failed to load payment instructions, using defaults', error);
      setInstructions({
        upi: { upi_id: 'yourupi@bank', payee_name: 'Your Business Name' },
        bank: {
          account_number: '123456789012',
          ifsc: 'BANK0001234',
          bank_name: 'Bank Name',
          branch: 'Branch Name',
        },
        crypto: {
          btc: 'bc1qexamplebtcaddress000000000000000000',
          eth: '0xExampleEthereumAddress0000000000000000000000',
          usdt_trc20: 'TYExampleTronAddress0000000000000000',
          usdt_erc20: '0xExampleERC20Address00000000000000000000',
          usdt_bep20: '0xExampleBSCAddress000000000000000000000',
        },
        card: {
          provider: 'Card Gateway',
          instructions: 'Use the shared payment link to pay via card.',
          support_contact: 'payments@example.com',
        },
      });
    }
  };

  const handleDepositCreated = async (deposit: Deposit) => {
    setCurrentDeposit(deposit);
    
    // If PayPal, create payment and redirect
    if (deposit.method === 'PAYPAL') {
      try {
        setLoading(true);
        setError(''); // Clear any previous errors
        
        const response = await api.post('/paypal/create', {
          amount: deposit.amount,
          currency: 'USD',
          description: `Payment for Deposit #${deposit.id}`,
          deposit_id: deposit.id,
          return_url: `${window.location.origin}/deposit?payment_success=true&deposit_id=${deposit.id}`,
          cancel_url: `${window.location.origin}/deposit?payment_cancelled=true&deposit_id=${deposit.id}`,
        });
        
        console.log('PayPal payment created:', response.data);
        
        // Redirect to PayPal approval URL
        if (response.data && response.data.approval_url) {
          // Immediate redirect
          window.location.href = response.data.approval_url;
        } else {
          throw new Error('No approval URL received from payment gateway');
        }
      } catch (err: any) {
        console.error('PayPal payment creation error:', err);
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to create payment. Please try again.';
        setError(errorMessage);
        setLoading(false);
        // Don't set currentDeposit to null so user can see the error
      }
    }
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
            {currentDeposit.method === 'CARD' && instructions?.card && (
              <div className="space-y-4">
                <p className="text-gray-700">Card Payment Instructions:</p>
                {instructions.card.identifier_name && (
                  <p className="text-xs text-gray-500">Account: {instructions.card.identifier_name}</p>
                )}
                <div className="bg-gray-50 p-4 rounded space-y-2">
                  {instructions.card.provider && (
                    <p><strong>Provider:</strong> {instructions.card.provider}</p>
                  )}
                  {instructions.card.instructions && (
                    <p><strong>Steps:</strong> {instructions.card.instructions}</p>
                  )}
                  {instructions.card.payment_link && (
                    <p>
                      <strong>Payment Link:</strong>{' '}
                      <a href={instructions.card.payment_link} className="text-blue-600 underline" target="_blank" rel="noreferrer">
                        {instructions.card.payment_link}
                      </a>
                    </p>
                  )}
                  {instructions.card.support_contact && (
                    <p><strong>Support:</strong> {instructions.card.support_contact}</p>
                  )}
                </div>
              </div>
            )}
            {currentDeposit.method === 'PAYPAL' && (
              <div className="space-y-4">
                {error ? (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800 font-semibold mb-2">Payment Error</p>
                    <p className="text-red-700 text-sm">{error}</p>
                    <button
                      onClick={() => {
                        setError('');
                        setCurrentDeposit(null);
                      }}
                      className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                    >
                      Try Again
                    </button>
                  </div>
                ) : (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-blue-800 font-semibold mb-2">Redirecting to secure payment...</p>
                    <p className="text-blue-700 text-sm">
                      You will be redirected to complete your payment securely. 
                      Your payment will be processed immediately and securely.
                    </p>
                    {loading && (
                      <div className="mt-4">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                        <p className="text-center text-blue-600 text-sm mt-2">Creating payment...</p>
                      </div>
                    )}
                    {!loading && (
                      <p className="text-blue-600 text-sm mt-2">If you are not redirected automatically, please check the console for errors.</p>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {currentDeposit.method !== 'PAYPAL' && (
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
          )}
        </div>
      )}
    </div>
  );
}

