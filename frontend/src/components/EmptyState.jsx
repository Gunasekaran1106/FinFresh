import React from "react";
import { FolderOpen } from "lucide-react";

export const EmptyState = ({ message = "No data available", description }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center animate-fade-in">
      <div className="w-16 h-16 bg-secondary/50 rounded-full flex items-center justify-center mb-4 ring-1 ring-white/10">
        <FolderOpen className="w-8 h-8 text-muted-foreground" />
      </div>
      <h3 className="text-lg font-medium text-foreground">{message}</h3>
      {description && (
        <p className="text-sm text-muted-foreground mt-1 max-w-sm">
          {description}
        </p>
      )}
    </div>
  );
};
