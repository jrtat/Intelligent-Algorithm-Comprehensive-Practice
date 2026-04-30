import { useState, useRef, useEffect } from 'react';

export type PolishScope = 'global' | 'module' | 'field';
export type PolishStyle = 'concise' | 'formal' | 'persuasive' | 'brief';
export type PolishIntensity = 'light' | 'medium' | 'deep';

export interface PolishSettings {
  scope: PolishScope;
  moduleId?: string;
  fieldPath?: string;
  style: PolishStyle;
  intensity: PolishIntensity;
}

interface AIPolishModalProps {
  isOpen: boolean;
  settings: PolishSettings;
  onSettingsChange: (settings: PolishSettings) => void;
  onStart: () => void;
  onCancel: () => void;
  isPolishing: boolean;
}

const styleLabels: Record<PolishStyle, string> = {
  concise: '简洁专业',
  formal: '正式商务',
  persuasive: '更有说服力',
  brief: '更精炼简短',
};

const intensityLabels: Record<PolishIntensity, string> = {
  light: '轻度（仅修正语句、通顺化）',
  medium: '中度（优化逻辑、提升专业度）',
  deep: '深度（重组织语言、强化表达）',
};

const scopeLabels: Record<PolishScope, string> = {
  global: '全局润色',
  module: '模块润色',
  field: '字段润色',
};

export function AIPolishModal({
  isOpen,
  settings,
  onSettingsChange,
  onStart,
  onCancel,
  isPolishing,
}: AIPolishModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const dragOffset = useRef({ x: 0, y: 0 });

  useEffect(() => {
    if (isOpen && modalRef.current) {
      const rect = modalRef.current.getBoundingClientRect();
      setPosition({
        x: (window.innerWidth - rect.width) / 2,
        y: (window.innerHeight - rect.height) / 2,
      });
    }
  }, [isOpen]);

  const handleMouseDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('.modal-header')) {
      setIsDragging(true);
      dragOffset.current = {
        x: e.clientX - position.x,
        y: e.clientY - position.y,
      };
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - dragOffset.current.x,
        y: e.clientY - dragOffset.current.y,
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[1000] flex items-center justify-center bg-black/50 animate-modal-fade"
      onClick={onCancel}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      <div
        ref={modalRef}
        className="max-h-[80vh] w-[450px] max-w-[90%] overflow-y-auto rounded-xl bg-white !p-6 shadow-2xl animate-modal-slide"
        style={{
          position: 'fixed',
          left: position.x,
          top: position.y,
          cursor: isDragging ? 'grabbing' : 'default',
          userSelect: isDragging ? 'none' : 'auto',
        }}
        onClick={(e) => e.stopPropagation()}
        onMouseDown={handleMouseDown}
      >
        <div className="mb-5" style={{ cursor: 'move' }}>
          <div className="mb-4 flex items-center justify-between">
            <h3 className="m-0 text-[16px] font-bold text-[#333]">AI 润色设置</h3>
            <button className="flex h-8 w-8 items-center justify-center rounded-md hover:bg-[#1677ff]/10" onClick={onCancel}>
              <span className="material-symbols-outlined text-[20px]" style={{ color: '#666' }}>close</span>
            </button>
          </div>

          <div className="space-y-4">
            {/* 润色范围 */}
            <div className="mb-4">
              <label className="mb-1.5 block text-[13px] font-medium text-[#999]">润色范围</label>
              <div className="rounded-md bg-[#F5F7FA] px-3 py-2 text-[14px] text-[#333]">
                {scopeLabels[settings.scope]}
                {settings.moduleId && <span className="ml-2 text-[#999]">• {settings.moduleId}</span>}
                {settings.fieldPath && <span className="ml-2 text-[#999]">• {settings.fieldPath}</span>}
              </div>
            </div>

            {/* 润色风格 */}
            <div className="mb-4">
              <label className="mb-1.5 block text-[13px] font-medium text-[#999]">润色风格</label>
              <select
                className="w-full rounded-md border border-[#DCDCDC] bg-white px-3 py-2 text-[14px] text-[#333] transition-colors focus:border-[#1677ff] focus:outline-none focus:ring-2 focus:ring-[#1677ff]/20"
                value={settings.style}
                onChange={(e) => onSettingsChange({ ...settings, style: e.target.value as PolishStyle })}
                style={{ cursor: 'pointer' }}
              >
                {(Object.keys(styleLabels) as PolishStyle[]).map((key) => (
                  <option key={key} value={key}>{styleLabels[key]}</option>
                ))}
              </select>
            </div>

            {/* 润色强度 */}
            <div className="mb-4">
              <label className="mb-1.5 block text-[13px] font-medium text-[#999]">润色强度</label>
              <select
                className="w-full rounded-md border border-[#DCDCDC] bg-white px-3 py-2 text-[14px] text-[#333] transition-colors focus:border-[#1677ff] focus:outline-none focus:ring-2 focus:ring-[#1677ff]/20"
                value={settings.intensity}
                onChange={(e) => onSettingsChange({ ...settings, intensity: e.target.value as PolishIntensity })}
                style={{ cursor: 'pointer' }}
              >
                {(Object.keys(intensityLabels) as PolishIntensity[]).map((key) => (
                  <option key={key} value={key}>{intensityLabels[key]}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="mt-6 flex items-center justify-end gap-3">
          <button
            className="rounded-lg border border-[#DCDCDC] !px-4 !py-2 text-[14px] font-medium text-[#666] transition-colors hover:bg-gray-50 disabled:opacity-50"
            onClick={onCancel}
            disabled={isPolishing}
          >
            取消
          </button>
          <button
            className="inline-flex items-center gap-1 rounded-lg !px-5 !py-2 text-[14px] font-medium text-white transition-all hover:scale-105 disabled:opacity-50"
            style={{ backgroundColor: '#FF9F43' }}
            onClick={onStart}
            disabled={isPolishing}
          >
            {isPolishing ? (
              <>
                <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                润色中...
              </>
            ) : (
              '开始润色'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}