import React from "react";

export const HealthScoreCard = ({ score, category, suggestions = [], breakdown = [] }) => {
  const getStrokeColor = (cat, val) => {
    const c = (cat || "").toLowerCase();
    if (c === "excellent" || c === "healthy" || val >= 75) return "#10b981";
    if (c === "moderate" || val >= 50) return "#f59e0b";
    return "#ef4444";
  };

  const getTextColorClass = (cat, val) => {
    const c = (cat || "").toLowerCase();
    if (c === "excellent" || c === "healthy" || val >= 75) return "text-success";
    if (c === "moderate" || val >= 50) return "text-warning";
    return "text-destructive";
  };

  const statusLabel = category || (score >= 75 ? "Healthy" : score >= 50 ? "Good" : "Needs Improvement");
  const strokeColor = getStrokeColor(category, score);
  const textColorClass = getTextColorClass(category, score);

  return (
    <div className="glass-card rounded-2xl p-6">
      <h3 className="text-lg font-semibold text-foreground mb-4">Financial Health</h3>

      <div className="flex items-center mb-6">
        <div className="flex-1">
          <div className="text-4xl font-bold text-foreground">{score}</div>
          <div className={`text-lg font-medium mt-1 ${textColorClass}`}>
            {statusLabel}
          </div>
        </div>
        <div className="relative w-24 h-24 drop-shadow-[0_0_15px_rgba(255,255,255,0.1)]">
          <svg className="w-full h-full" viewBox="0 0 100 100" fill="none">
            <circle
              cx="50"
              cy="50"
              r="40"
              stroke="currentColor"
              strokeWidth="4"
              className="text-white/10"
            />
            <circle
              cx="50"
              cy="50"
              r="40"
              stroke={strokeColor}
              strokeWidth="4"
              fill="none"
              strokeDasharray={`${(score / 100) * 251} 251`}
              className="transform -rotate-90 transition-all duration-1000 ease-out"
              style={{ transformOrigin: "50% 50%" }}
            />
          </svg>
        </div>
      </div>

      {breakdown.length > 0 && (
        <div className="space-y-4 border-t border-white/10 pt-5">
          {breakdown.map((item, idx) => (
            <div key={idx} className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">{item.label}</span>
              <div className="flex items-center space-x-3 w-1/2">
                <div className="flex-1 bg-secondary rounded-full h-2 overflow-hidden shadow-inner">
                  <div
                    className="bg-primary h-full rounded-full transition-all duration-1000 ease-out"
                    style={{ width: `${(item.value / item.max) * 100}%` }}
                  ></div>
                </div>
                <span className="text-sm font-medium text-foreground min-w-[40px] text-right">
                  {item.value}/{item.max}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {suggestions.length > 0 && (
        <div className="space-y-2 border-t border-white/10 pt-5 mt-5">
          <h4 className="text-sm font-semibold text-foreground">Recommendations:</h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
            {suggestions.map((sug, idx) => (
              <li key={idx} className="transition-all duration-300 hover:text-foreground">{sug}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
