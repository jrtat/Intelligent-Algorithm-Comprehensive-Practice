import { useState, useRef, useEffect } from 'react';
import type { KeyboardEvent, ChangeEvent } from 'react';

interface EditableFieldProps {
  value: string;
  onChange: (value: string) => void;
  onSave?: () => void;
  onCancel?: () => void;
  onAIPolish?: () => void;
  placeholder?: string;
  maxLength?: number;
  multiline?: boolean;
  disabled?: boolean;
  className?: string;
  label?: string;
  error?: string;
  showCharCount?: boolean;
}

export function EditableField({
  value,
  onChange,
  onSave,
  onCancel,
  onAIPolish,
  placeholder = '请输入内容',
  maxLength,
  multiline = false,
  disabled = false,
  className = '',
  label,
  error,
  showCharCount = false,
}: EditableFieldProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setEditValue(value);
  }, [value]);

  useEffect(() => {
    if (isEditing && multiline && textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [isEditing, multiline]);

  const handleSave = () => {
    onChange(editValue);
    setIsEditing(false);
    onSave?.();
  };

  const handleCancel = () => {
    setEditValue(value);
    setIsEditing(false);
    onCancel?.();
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !multiline) {
      e.preventDefault();
      handleSave();
    }
    if (e.key === 'Escape') {
      handleCancel();
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    if (maxLength && newValue.length > maxLength) return;
    setEditValue(newValue);
    onChange(newValue);
  };

  const handleBlur = () => {
    if (editValue !== value) {
      handleSave();
    } else {
      setIsEditing(false);
    }
  };

  if (!isEditing) {
    return (
      <div
        className={`group relative cursor-text rounded-md border border-transparent !px-3 !py-2 transition-all hover:border-[#1677ff]/20 hover:bg-[#1677ff]/5 ${disabled ? 'cursor-default' : ''} ${className}`}
        onClick={() => !disabled && setIsEditing(true)}
      >
        <span className={`leading-relaxed ${value ? 'text-[#333]' : 'text-[#999]'}`}>
          {value || placeholder}
        </span>
        {!disabled && (
          <div className="edit-icon-overlay absolute right-2 top-1/2 -translate-y-1/2 opacity-0 transition-opacity group-hover:opacity-100">
            {onAIPolish && (
              <button
                className="flex !h-7 !w-7 items-center justify-center rounded-md hover:bg-[#1677ff]/10"
                onClick={(e) => {
                  e.stopPropagation();
                  onAIPolish();
                }}
                title="AI润色"
              >
                <span className="material-symbols-outlined text-[16px]" style={{ color: '#FF9F43' }}>
                  auto_fix_high
                </span>
              </button>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      {label && (
        <label className="!mb-1.5 block text-[16px] font-medium text-[#999]">
          {label}
        </label>
      )}
      {multiline ? (
        <textarea
          ref={textareaRef}
          value={editValue}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          placeholder={placeholder}
          className={`!w-full resize-none rounded-md border bg-white px-3 !py-2 text-[16px] text-[#333] transition-colors focus:outline-none focus:ring-2 ${error ? 'border-red-500 focus:ring-red-500/20' : 'border-[#1677ff] focus:ring-[#1677ff]/20'}`}
          style={{ minHeight: '80px', paddingRight: onAIPolish ? '50px' : '12px' }}
        />
      ) : (
        <input
          type="text"
          value={editValue}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          placeholder={placeholder}
          className={`!w-full rounded-md border bg-white !px-3 !py-2 text-[16px] text-[#333] transition-colors focus:outline-none focus:ring-2 ${error ? 'border-red-500 focus:ring-red-500/20' : 'border-[#1677ff] focus:ring-[#1677ff]/20'}`}
          style={{ paddingRight: onAIPolish ? '50px' : '12px' }}
        />
      )}
      {showCharCount && maxLength && (
        <div className={`!mt-1 text-right text-[11px] ${editValue.length > maxLength ? 'text-red-500' : 'text-[#999]'}`}>
          {editValue.length}/{maxLength}
        </div>
      )}
      {error && (
        <div className="!mt-1 text-[12px] text-red-500">
          {error}
        </div>
      )}
      {isEditing && onAIPolish && (
        <div
          className="absolute !right-0 flex items-start !gap-1"
          style={{ top: label ? '36px' : '10px' }}
        >
          <button
            className="flex h-7 w-7 items-center justify-center rounded-md hover:bg-[#FF9F43]/10"
            onClick={(e) => {
              e.stopPropagation();
              onAIPolish();
            }}
            title="AI润色"
          >
            <span className="material-symbols-outlined text-[16px]" style={{ color: '#FF9F43' }}>
              auto_fix_high
            </span>
          </button>
        </div>
      )}
    </div>
  );
}