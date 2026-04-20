import type { ReactNode } from 'react';

interface ReportCardProps {
  id: string;
  title: string;
  icon?: string;
  children: ReactNode;
  onEdit?: () => void;
  onAIPolish?: () => void;
  onSave?: () => void;
  onCancel?: () => void;
  isLoading?: boolean;
  isEditing?: boolean;
  saveStatus?: 'idle' | 'saving' | 'saved' | 'error';
  className?: string;
}

export function ReportCard({
  id,
  title,
  icon,
  children,
  onEdit,
  onAIPolish,
  onSave,
  onCancel,
  isLoading,
  isEditing = false,
  saveStatus = 'idle',
  className = '',
}: ReportCardProps) {
  return (
    <section
      id={`section-${id}`}
      className={`report-card ${className} ${isEditing ? 'editing' : ''}`}
      style={{
        border: isEditing ? '1px solid #2E86AB' : undefined,
      }}
    >
      <div className="report-card-header">
        <h2 className="report-card-title">
          {icon && <span className="material-symbols-outlined">{icon}</span>}
          {title}
        </h2>

        <div className="report-card-actions">
          {isLoading ? (
            <div className="loading-spinner" />
          ) : (
            <>
              {/* Save status feedback */}
              {saveStatus === 'saving' && (
                <span className="save-status saving">保存中...</span>
              )}
              {saveStatus === 'saved' && (
                <span className="save-status saved">
                  <span className="material-symbols-outlined" style={{ fontSize: 14, marginRight: 4 }}>
                    check_circle
                  </span>
                  保存成功
                </span>
              )}
              {saveStatus === 'error' && (
                <span className="save-status error">
                  <span className="material-symbols-outlined" style={{ fontSize: 14, marginRight: 4 }}>
                    error
                  </span>
                  保存失败
                </span>
              )}

              {/* Action buttons */}
              {isEditing ? (
                <>
                  <button
                    className="btn btn-outline"
                    onClick={onCancel}
                    style={{ padding: '6px 12px', fontSize: 13 }}
                  >
                    取消
                  </button>
                  <button
                    className="btn btn-primary"
                    onClick={onSave}
                    disabled={saveStatus === 'saving'}
                    style={{
                      padding: '6px 12px',
                      fontSize: 13,
                      opacity: saveStatus === 'saving' ? 0.5 : 1,
                    }}
                  >
                    保存
                  </button>
                </>
              ) : (
                <>
                  {onEdit && (
                    <button
                      className="btn-icon edit-entry"
                      onClick={onEdit}
                      title="编辑"
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 4,
                        padding: '6px 12px',
                        borderRadius: 8,
                        color: '#2E86AB',
                      }}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
                        edit
                      </span>
                      <span style={{ fontSize: 13 }}>编辑</span>
                    </button>
                  )}
                  {onAIPolish && (
                    <button
                      className="btn-icon"
                      onClick={onAIPolish}
                      title="AI润色"
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 18, color: '#FF9F43' }}>
                        auto_fix_high
                      </span>
                    </button>
                  )}
                </>
              )}
            </>
          )}
        </div>
      </div>

      <div className="report-card-content">{children}</div>
    </section>
  );
}
