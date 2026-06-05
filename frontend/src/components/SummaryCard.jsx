import React from "react";
import { formatCurrency } from "../utils/formatCurrency";

export const SummaryCard = ({ title, amount, icon: Icon, color = "primary" }) => {
  const colorClasses = {
    primary: "border-primary/20 bg-primary/5",
    success: "border-success/20 bg-success/5",
    warning: "border-warning/20 bg-warning/5",
    danger: "border-destructive/20 bg-destructive/5",
  };

  const iconColorClasses = {
    primary: "text-primary",
    success: "text-success",
    warning: "text-warning",
    danger: "text-destructive",
  };

  return (
    <div className={`glass-card ${colorClasses[color]} rounded-2xl p-6 transition-all duration-300 hover:scale-[1.02]`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-muted-foreground text-sm font-medium">{title}</p>
          <p className="text-2xl font-bold text-foreground mt-2">
            {formatCurrency(amount)}
          </p>
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl bg-background/50 backdrop-blur-sm shadow-inner ${iconColorClasses[color]}`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>
    </div>
  );
};
