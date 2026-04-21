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
      className="modal-overlay"
      onClick={onCancel}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      <div
        ref={modalRef}
        className="modal-content"
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
        <div className="modal-header" style={{ cursor: 'move' }}>
          <h3 className="modal-title">AI 润色设置</h3>
          <button className="btn-icon" onClick={onCancel}>
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <div style={{ marginBottom: 20 }}>
          {/* 润色范围 */}
          <div className="form-group">
            <label className="form-label">润色范围</label>
            <div style={{
              padding: '8px 12px',
              background: '#F5F7FA',
              borderRadius: 6,
              fontSize: 14,
              color: '#333',
            }}>
              {scopeLabels[settings.scope]}
              {settings.moduleId && <span style={{ color: '#999', marginLeft: 8 }}>• {settings.moduleId}</span>}
              {settings.fieldPath && <span style={{ color: '#999', marginLeft: 8 }}>• {settings.fieldPath}</span>}
            </div>
          </div>

          {/* 润色风格 */}
          <div className="form-group">
            <label className="form-label">润色风格</label>
            <select
              className="form-input"
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
          <div className="form-group">
            <label className="form-label">润色强度</label>
            <select
              className="form-input"
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

        <div className="modal-footer">
          <button className="btn btn-outline" onClick={onCancel} disabled={isPolishing}>
            取消
          </button>
          <button
            className="btn btn-accent"
            onClick={onStart}
            disabled={isPolishing}
            style={{
              minWidth: 120,
              opacity: isPolishing ? 0.6 : 1,
            }}
          >
            {isPolishing ? (
              <>
                <span className="loading-spinner" style={{ width: 14, height: 14, marginRight: 6 }} />
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