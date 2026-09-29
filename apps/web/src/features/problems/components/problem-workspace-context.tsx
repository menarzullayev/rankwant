"use client";

import { createContext, useContext } from "react";

export type ProblemWorkspaceContextValue = {
  wide: boolean;
  editorCollapsed: boolean;
  setEditorCollapsed: (v: boolean) => void;
};

const ProblemWorkspaceContext = createContext<ProblemWorkspaceContextValue | null>(
  null,
);

export function ProblemWorkspaceProvider({
  value,
  children,
}: {
  value: ProblemWorkspaceContextValue;
  children: React.ReactNode;
}) {
  return (
    <ProblemWorkspaceContext.Provider value={value}>
      {children}
    </ProblemWorkspaceContext.Provider>
  );
}

export function useProblemWorkspace() {
  return useContext(ProblemWorkspaceContext);
}
