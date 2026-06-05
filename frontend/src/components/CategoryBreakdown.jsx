import React from "react";
import { formatCurrency } from "../utils/formatCurrency";
import { EmptyState } from "./EmptyState";

export const CategoryBreakdown = ({ categories = {} }) => {
  const sorted = Object.entries(categories)
    .map(([name, amount]) => ({ name, amount }))
    .sort((a, b) => b.amount - a.amount);

  if (sorted.length === 0) {
    return (
      <div className="glass-card rounded-2xl p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4">
          Category Breakdown
        </h3>
        <EmptyState message="No transactions yet" />
      </div>
    );
  }

  return (
    <div className="glass-card rounded-2xl p-6">
      <h3 className="text-lg font-semibold text-foreground mb-4">
        Category Breakdown
      </h3>
      <div className="space-y-4">
        {sorted.map((item, idx) => (
          <div key={idx} className="flex justify-between items-center p-3 rounded-xl hover:bg-secondary/30 transition-colors">
            <span className="text-muted-foreground font-medium">{item.name}</span>
            <span className="font-bold text-foreground">
              {formatCurrency(item.amount)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
