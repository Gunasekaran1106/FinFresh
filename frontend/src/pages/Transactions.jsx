import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { 
  LayoutDashboard,
  ListOrdered,
  LogOut,
  Search,
  Filter,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import { transactionAPI } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { TransactionTable } from "../components/TransactionTable";
import { LoadingState } from "../components/LoadingState";
import { ErrorState } from "../components/ErrorState";

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filterType, setFilterType] = useState("all");
  const [searchCategory, setSearchCategory] = useState("");
  const { user, logout } = useAuth();

  const fetchTransactions = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        limit: 20,
        ...(filterType !== 'all' && { type: filterType }),
        ...(searchCategory && { category: searchCategory }),
      };
      const { data } = await transactionAPI.list(params);
      setTransactions(data.data || []);
      const total = data.pagination?.total || 0;
      const limit = data.pagination?.limit || 20;
      setTotalPages(Math.ceil(total / limit) || 1);
    } catch (err) {
      setError("Failed to load transactions.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Add a slight debounce for searching
    const timer = setTimeout(() => {
      fetchTransactions();
    }, 300);
    return () => clearTimeout(timer);
  }, [page, filterType, searchCategory]);

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 glass-card border-l-0 border-t-0 border-b-0 hidden md:flex flex-col">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-primary tracking-tight">FinFresh</h2>
        </div>
        <nav className="flex-1 px-4 space-y-2 mt-4">
          <Link to="/dashboard" className="flex items-center space-x-3 px-4 py-3 text-muted-foreground hover:text-foreground hover:bg-secondary/50 rounded-xl font-medium transition-colors">
            <LayoutDashboard className="w-5 h-5" />
            <span>Dashboard</span>
          </Link>
          <Link to="/transactions" className="flex items-center space-x-3 px-4 py-3 bg-primary/10 text-primary rounded-xl font-medium transition-colors">
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

      <main className="flex-1 p-6 md:p-10 overflow-y-auto z-10 animate-fade-in flex flex-col h-screen">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-foreground">Transactions</h1>
          <p className="text-muted-foreground mt-1">View and manage all your financial activities.</p>
        </header>

        <div className="glass-card rounded-2xl p-4 mb-6 flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="flex w-full md:w-auto items-center space-x-4">
            <div className="relative flex-1 md:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input 
                type="text" 
                placeholder="Search category..." 
                className="w-full glass-input rounded-xl py-2 pl-9 pr-4 text-sm"
                value={searchCategory}
                onChange={(e) => {
                  setSearchCategory(e.target.value);
                  setPage(1);
                }}
              />
            </div>
            <div className="relative">
              <select 
                className="glass-input rounded-xl py-2 pl-4 pr-10 text-sm appearance-none cursor-pointer"
                value={filterType}
                onChange={(e) => {
                  setFilterType(e.target.value);
                  setPage(1);
                }}
              >
                <option value="all" className="bg-secondary text-foreground">All Types</option>
                <option value="income" className="bg-secondary text-foreground">Income</option>
                <option value="expense" className="bg-secondary text-foreground">Expense</option>
                <option value="investment" className="bg-secondary text-foreground">Investment</option>
                <option value="debt" className="bg-secondary text-foreground">Debt</option>
              </select>
              <Filter className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
            </div>
          </div>
        </div>

        <div className="flex-1 min-h-0">
          {error ? (
            <ErrorState message={error} onRetry={fetchTransactions} />
          ) : loading && transactions.length === 0 ? (
            <LoadingState text="Loading transactions..." />
          ) : (
            <TransactionTable transactions={transactions} />
          )}
        </div>

        {!error && totalPages > 1 && (
          <div className="mt-6 flex items-center justify-between glass-card p-4 rounded-2xl">
            <button 
              className="premium-btn px-4 py-2 bg-secondary text-foreground rounded-lg flex items-center text-sm"
              disabled={page === 1}
              onClick={() => setPage(p => p - 1)}
            >
              <ChevronLeft className="w-4 h-4 mr-1" /> Previous
            </button>
            <span className="text-sm font-medium text-muted-foreground">
              Page {page} of {totalPages}
            </span>
            <button 
              className="premium-btn px-4 py-2 bg-secondary text-foreground rounded-lg flex items-center text-sm"
              disabled={page === totalPages}
              onClick={() => setPage(p => p + 1)}
            >
              Next <ChevronRight className="w-4 h-4 ml-1" />
            </button>
          </div>
        )}
      </main>
    </div>
  );
};

export default Transactions;
