interface ConfirmDialogProps {
  title?: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
  type?: 'danger' | 'warning' | 'info';
}

export function ConfirmDialog({
  title = '确认操作',
  message,
  confirmText = '确认',
  cancelText = '取消',
  onConfirm,
  onCancel,
  type = 'danger',
}: ConfirmDialogProps) {
  const typeColors: Record<string, { bg: string; border: string; text: string }> = {
    danger: { bg: '#FEE2E2', border: '#DC2626', text: '#DC2626' },
    warning: { bg: '#FEF3C7', border: '#D97706', text: '#D97706' },
    info: { bg: '#E8F4F8', border: '#2E86AB', text: '#2E86AB' },
  };

  const colors = typeColors[type];

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
        style={{
          width: 360,
          textAlign: 'center',
          padding: '24px',
        }}
      >
        <div
          style={{
            width: 48,
            height: 48,
            borderRadius: '50%',
            backgroundColor: colors.bg,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px',
          }}
        >
          <span
            className="material-symbols-outlined"
            style={{ fontSize: 24, color: colors.text }}
          >
            {type === 'danger' ? 'warning' : type === 'warning' ? 'info' : 'help'}
          </span>
        </div>

        {title && (
          <h3
            style={{
              fontSize: 16,
              fontWeight: 'bold',
              color: '#333',
              marginBottom: 8,
            }}
          >
            {title}
          </h3>
        )}

        <p
          style={{
            fontSize: 14,
            color: '#666',
            marginBottom: 24,
            lineHeight: 1.6,
          }}
        >
          {message}
        </p>

        <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
          <button
            className="btn btn-outline"
            onClick={onCancel}
            style={{ minWidth: 100 }}
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            style={{
              minWidth: 100,
              padding: '8px 16px',
              borderRadius: 8,
              border: `1px solid ${colors.border}`,
              backgroundColor: colors.bg,
              color: colors.text,
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
