import React from "react";
import { Loader2 } from "lucide-react";

export const LoadingState = ({ text = "Loading..." }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] w-full animate-fade-in z-10 relative">
      <div className="relative">
        <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full"></div>
        <Loader2 className="w-12 h-12 text-primary animate-spin relative z-10" />
      </div>
      <p className="mt-4 text-muted-foreground font-medium animate-pulse">{text}</p>
    </div>
  );
};
