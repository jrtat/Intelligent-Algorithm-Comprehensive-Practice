import React, { createContext, useContext, useState, useCallback, useRef } from 'react';

interface ToastOptions {
  message: string;
  onClick?: () => void;
  duration?: number;
}

interface ToastContextType {
  showToast: (options: ToastOptions) => void;
  hideToast: () => void;
  toastVisible: boolean;
  toastMessage: string;
  toastOnClick?: () => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toastVisible, setToastVisible] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastOnClick, setToastOnClick] = useState<(() => void) | undefined>();
  const hideTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const showToast = useCallback((options: ToastOptions) => {
    if (hideTimeoutRef.current) {
      clearTimeout(hideTimeoutRef.current);
    }
    setToastMessage(options.message);
    setToastOnClick(() => options.onClick);
    setToastVisible(true);
  }, []);

  const hideToast = useCallback(() => {
    setToastVisible(false);
    hideTimeoutRef.current = setTimeout(() => {
      setToastVisible(false);
      setToastMessage('');
      setToastOnClick(undefined);
    }, 900);
  }, []);

  return (
    <ToastContext.Provider
      value={{
        showToast,
        hideToast,
        toastVisible,
        toastMessage,
        toastOnClick,
      }}
    >
      {children}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}