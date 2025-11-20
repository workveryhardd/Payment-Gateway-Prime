import DepositList from '../components/DepositList';

export default function DashboardPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">My Deposits</h1>
      <DepositList />
    </div>
  );
}

