import React from "react";
import { formatCurrency, formatDate } from "../utils/formatCurrency";
import { EmptyState } from "./EmptyState";

export const TransactionTable = ({ transactions = [] }) => {
  if (transactions.length === 0) {
    return <EmptyState message="No transactions found" />;
  }

  const getTypeStyles = (type) => {
    const types = {
      income: "bg-success/10 text-success border-success/20",
      expense: "bg-destructive/10 text-destructive border-destructive/20",
      investment: "bg-primary/10 text-primary border-primary/20",
      debt: "bg-warning/10 text-warning border-warning/20",
    };
    return types[type?.toLowerCase()] || "bg-secondary text-muted-foreground border-white/10";
  };

  return (
    <div className="w-full overflow-hidden rounded-2xl glass-card">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/10 bg-secondary/50">
              <th className="px-6 py-4 text-sm font-semibold text-muted-foreground">Date</th>
              <th className="px-6 py-4 text-sm font-semibold text-muted-foreground">Type</th>
              <th className="px-6 py-4 text-sm font-semibold text-muted-foreground">Category</th>
              <th className="px-6 py-4 text-sm font-semibold text-muted-foreground text-right">Amount</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {transactions.map((tx) => (
              <tr key={tx.id} className="hover:bg-white/5 transition-colors group">
                <td className="px-6 py-4 text-sm text-foreground whitespace-nowrap">
                  {formatDate(tx.date)}
                </td>
                <td className="px-6 py-4 text-sm whitespace-nowrap">
                  <span className={`px-3 py-1.5 rounded-full text-xs font-semibold capitalize border ${getTypeStyles(tx.type)}`}>
                    {tx.type}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-muted-foreground whitespace-nowrap">
                  {tx.category}
                </td>
                <td className="px-6 py-4 text-sm font-bold text-foreground text-right whitespace-nowrap group-hover:text-primary transition-colors">
                  {formatCurrency(tx.amount)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
