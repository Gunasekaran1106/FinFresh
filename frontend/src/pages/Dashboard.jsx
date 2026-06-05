import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { 
  ArrowUpRight, 
  ArrowDownRight, 
  PiggyBank, 
  TrendingUp,
  LayoutDashboard,
  ListOrdered,
  LogOut
} from "lucide-react";
import { dashboardAPI } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { SummaryCard } from "../components/SummaryCard";
import { HealthScoreCard } from "../components/HealthScoreCard";
import { CategoryBreakdown } from "../components/CategoryBreakdown";
import { LoadingState } from "../components/LoadingState";
import { ErrorState } from "../components/ErrorState";
import { formatCurrency } from "../utils/formatCurrency";
import { parseNumber } from "../utils/parseNumber";

const Dashboard = () => {
  const [data, setData] = useState({ summary: null, health: null });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user, logout } = useAuth();

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [summaryRes, healthRes] = await Promise.all([
          dashboardAPI.getSummary(),
          dashboardAPI.getFinancialHealth(),
        ]);
        setData({
          summary: summaryRes.data,
          health: healthRes.data,
        });
      } catch (err) {
        setError("Failed to load dashboard data. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (loading) return <LoadingState text="Loading Dashboard..." />;
  if (error) return <ErrorState message={error} />;

  const { summary, health } = data;

  const income = parseNumber(summary?.income);
  const expense = parseNumber(summary?.expense);
  const savings = parseNumber(summary?.savings);
  const rate = parseNumber(summary?.savingsRate);
  const score = parseNumber(health?.score);
  const category = health?.category || "";
  const suggestions = health?.suggestions || [];
  
  const rawBreakdown = health?.breakdown || {};
  const breakdown = [
    { label: "Emergency Fund", value: parseNumber(rawBreakdown.emergencyFund ?? rawBreakdown.emergency_fund), max: 25 },
    { label: "Savings Rate", value: parseNumber(rawBreakdown.savingsRate ?? rawBreakdown.savings_rate), max: 25 },
    { label: "Debt Ratio", value: parseNumber(rawBreakdown.debtRatio ?? rawBreakdown.debt_ratio), max: 25 },
    { label: "Investment Ratio", value: parseNumber(rawBreakdown.investmentRatio ?? rawBreakdown.investment_ratio), max: 25 },
  ];
  const categories = summary?.categories || {};

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 glass-card border-l-0 border-t-0 border-b-0 hidden md:flex flex-col">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-primary tracking-tight">FinFresh</h2>
        </div>
        <nav className="flex-1 px-4 space-y-2 mt-4">
          <Link to="/dashboard" className="flex items-center space-x-3 px-4 py-3 bg-primary/10 text-primary rounded-xl font-medium transition-colors">
            <LayoutDashboard className="w-5 h-5" />
            <span>Dashboard</span>
          </Link>
          <Link to="/transactions" className="flex items-center space-x-3 px-4 py-3 text-muted-foreground hover:text-foreground hover:bg-secondary/50 rounded-xl font-medium transition-colors">
            <ListOrdered className="w-5 h-5" />
            <span>Transactions</span>
          </Link>
        </nav>
        <div className="p-4 border-t border-white/10">
          <div className="flex items-center justify-between px-4 py-2">
            <span className="text-sm font-medium text-foreground truncate">{user?.name || 'User'}</span>
            <button onClick={logout} className="text-muted-foreground hover:text-destructive transition-colors">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </aside>

      <main className="flex-1 p-6 md:p-10 overflow-y-auto z-10 animate-fade-in">
        <header className="mb-8 flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Welcome back, {user?.name || 'User'}!</h1>
            <p className="text-muted-foreground mt-1">Here is your financial overview.</p>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <SummaryCard title="Total Income" amount={income} icon={ArrowUpRight} color="success" />
          <SummaryCard title="Total Expense" amount={expense} icon={ArrowDownRight} color="danger" />
          <SummaryCard title="Total Savings" amount={savings} icon={PiggyBank} color="primary" />
          <div className="glass-card border-warning/20 bg-warning/5 rounded-2xl p-6 transition-all duration-300 hover:scale-[1.02]">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm font-medium">Savings Rate</p>
                <p className="text-2xl font-bold text-foreground mt-2">{rate}%</p>
              </div>
              <div className="p-3 rounded-xl bg-background/50 backdrop-blur-sm shadow-inner text-warning">
                <TrendingUp className="w-6 h-6" />
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <HealthScoreCard score={score} category={category} suggestions={suggestions} breakdown={breakdown} />
          <CategoryBreakdown categories={categories} />
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
