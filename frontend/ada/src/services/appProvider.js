import React, { createContext, useContext, useState } from 'react';

// Create a Context
export const AppStateContext = createContext();

export const useAppStateContext = () => {
  return useContext(AppStateContext);
};


export const AppStateProvider = ({ children }) => {
  const [showRefs, setShowRefs] = useState(false);

  // The value prop is where you provide the data you want to share
  return (
    <AppStateContext.Provider value={{ showRefs, setShowRefs }}>
      {children}
    </AppStateContext.Provider>
  );
};