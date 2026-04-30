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
    info: { bg: '#E8F4F8', border: '#1677ff', text: '#1677ff' },
  };

  const colors = typeColors[type];

  return (
    <div
      className="fixed inset-0 z-[1000] flex items-center justify-center bg-black/50 animate-modal-fade"
      onClick={onCancel}
    >
      <div
        className="w-[360px] rounded-xl bg-white p-6 text-center shadow-2xl animate-modal-slide"
        onClick={(e) => e.stopPropagation()}
      >
        <div
          className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full"
          style={{ backgroundColor: colors.bg }}
        >
          <span
            className="material-symbols-outlined"
            style={{ fontSize: 24, color: colors.text }}
          >
            {type === 'danger' ? 'warning' : type === 'warning' ? 'info' : 'help'}
          </span>
        </div>

        {title && (
          <h3 className="mb-2 text-[16px] font-bold text-[#333]">
            {title}
          </h3>
        )}

        <p className="mb-6 text-[14px] leading-relaxed text-[#666]">
          {message}
        </p>

        <div className="flex justify-center gap-3">
          <button
            className="min-w-[100px] rounded-lg border border-[#DCDCDC] px-4 py-2 text-[14px] font-medium text-[#666] transition-colors hover:bg-gray-50"
            onClick={onCancel}
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            className="min-w-[100px] rounded-lg border py-2 text-[14px] font-medium transition-all hover:scale-105"
            style={{
              borderColor: colors.border,
              backgroundColor: colors.bg,
              color: colors.text,
            }}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}