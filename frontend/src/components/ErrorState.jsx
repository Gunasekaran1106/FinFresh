import React from "react";
import { AlertCircle } from "lucide-react";

export const ErrorState = ({ message = "Something went wrong", onRetry }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] text-center animate-fade-in z-10 relative">
      <div className="w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center mb-4 ring-1 ring-destructive/20 shadow-[0_0_15px_rgba(239,68,68,0.2)]">
        <AlertCircle className="w-8 h-8 text-destructive" />
      </div>
      <h3 className="text-xl font-bold text-foreground mb-2">Error Occurred</h3>
      <p className="text-muted-foreground max-w-md mb-6">{message}</p>
      
      {onRetry && (
        <button
          onClick={onRetry}
          className="premium-btn bg-secondary hover:bg-secondary/80 text-foreground px-6 py-2 rounded-lg"
        >
          Try Again
        </button>
      )}
    </div>
  );
};
