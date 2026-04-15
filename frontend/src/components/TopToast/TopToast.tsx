import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';

interface TopToastProps {
  visible: boolean;
  message: string;
  onClick?: () => void;
  onDismiss?: () => void;
  duration?: number;
}

export default function TopToast({
  visible,
  message,
  onClick,
  onDismiss,
  duration = 5000,
}: TopToastProps) {
  const [isShowing, setIsShowing] = useState(false);

  useEffect(() => {
    if (visible) {
      setIsShowing(true);
      const timer = setTimeout(() => {
        setIsShowing(false);
        setTimeout(() => {
          onDismiss?.();
        }, 900); // Wait for bounce-top animation to complete
      }, duration);
      return () => clearTimeout(timer);
    } else {
      setIsShowing(false);
    }
  }, [visible, duration, onDismiss]);

  if (!visible && !isShowing) return null;

  return createPortal(
    <div
      className={`fixed top-20 left-1/2 -translate-x-1/2 z-[9999] bounce-top cursor-pointer`}
      onClick={onClick}
      style={{ pointerEvents: visible ? 'auto' : 'none' }}
    >
      <div className="bg-primary text-white px-6 py-3 rounded-lg shadow-lg shadow-primary/30 font-bold flex items-center gap-3">
        <span className="material-symbols-outlined text-xl">auto_awesome</span>
        <span>{message}</span>
        {onClick && (
          <span className="text-sm opacity-80 hover:opacity-100">点击查看 →</span>
        )}
      </div>
    </div>,
    document.body
  );
}