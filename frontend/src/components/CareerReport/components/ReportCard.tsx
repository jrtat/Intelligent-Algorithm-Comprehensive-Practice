import type { ReactNode } from 'react';

interface ReportCardProps {
  id: string;
  title: string;
  icon?: string;
  children: ReactNode;
  onEdit?: () => void;
  onAIPolishModule?: (moduleId: string) => void;
  onSave?: () => void;
  onCancel?: () => void;
  isLoading?: boolean;
  isEditing?: boolean;
  isPolishing?: boolean;
  saveStatus?: 'idle' | 'saving' | 'saved' | 'error';
  className?: string;
}

export function ReportCard({
  id,
  title,
  icon,
  children,
  onEdit,
  onAIPolishModule,
  onSave,
  onCancel,
  isLoading,
  isEditing = false,
  isPolishing = false,
  saveStatus = 'idle',
  className = '',
}: ReportCardProps) {
  const moduleId = id;

  return (
    <section
      id={`section-${id}`}
      className={`group relative rounded-xl bg-white !p-6 shadow-md transition-all hover:shadow-lg ${isEditing ? 'ring-2 ring-[#1677ff] shadow-lg' : ''} ${className}`}
    >
      <div className="!mb-4 items-center justify-between">
        <h2 className="m-0 items-center gap-2 text-[24px] font-bold" style={{ color: '#1677ff' }}>
          {icon && <span className="material-symbols-outlined">{icon}</span>}
          {title}
        </h2>

        <div className="report-card-actions !gap-2 opacity-0 transition-opacity group-hover:opacity-100">
          {isLoading ? (
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-[#DCDCDC] border-t-[#1677ff]" />
          ) : (
            <>
              {/* Save status feedback */}
              {saveStatus === 'saving' && (
                <span className="inline-flex items-center rounded bg-[#E8F4F8] !px-3 !py-1 text-[12px]" style={{ color: '#1677ff' }}>
                  保存中...
                </span>
              )}
              {saveStatus === 'saved' && (
                <span className="inline-flex items-center rounded bg-green-100 !px-3 !py-1 text-[12px] text-green-600">
                  <span className="material-symbols-outlined mr-1 text-[14px]">check_circle</span>
                  保存成功
                </span>
              )}
              {saveStatus === 'error' && (
                <span className="inline-flex items-center rounded bg-red-100 !px-3 !py-1 text-[12px] text-red-600">
                  <span className="material-symbols-outlined mr-1 text-[14px]">error</span>
                  保存失败
                </span>
              )}

              {/* Polishing indicator */}
              {isPolishing && (
                <div className="polishing-indicator items-center">
                  <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-[#DCDCDC] border-t-[#FF9F43]" />
                </div>
              )}

              {/* Action buttons */}
              {isEditing ? (
                <>
                  <button
                    className="rounded-lg border border-[#DCDCDC] !px-3 !py-1.5 text-[13px] font-medium text-[#666] transition-colors hover:bg-gray-50"
                    onClick={onCancel}
                  >
                    取消
                  </button>
                  <button
                    className="rounded-lg bg-[#1677ff] !px-3 !py-1.5 text-[13px] font-medium text-white transition-all hover:scale-105 disabled:opacity-50"
                    onClick={onSave}
                    disabled={saveStatus === 'saving'}
                  >
                    保存
                  </button>
                </>
              ) : (
                <>
                  {onEdit && (
                    <button
                      className="edit-entry inline-flex items-center gap-1 rounded-lg border border-[#1677ff] !px-3 !py-1.5 text-[13px] transition-all hover:bg-[#1677ff]/10 hover:shadow"
                      onClick={onEdit}
                      title="编辑"
                      style={{ color: '#1677ff' }}
                    >
                      <span className="material-symbols-outlined text-[18px]">edit</span>
                      <span>编辑</span>
                    </button>
                  )}
                  {onAIPolishModule && (
                    <button
                      className="btn-ai-polish-module h-9 w-9 items-center justify-center rounded-lg hover:bg-[#FF9F43]/10 disabled:opacity-50"
                      onClick={() => onAIPolishModule(moduleId)}
                      title="AI润色"
                      disabled={isPolishing}
                    >
                      <span className="material-symbols-outlined text-[18px]" style={{ color: '#FF9F43' }}>
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