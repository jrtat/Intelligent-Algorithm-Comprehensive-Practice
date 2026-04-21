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
        className={`editable-field-display ${className}`}
        onClick={() => !disabled && setIsEditing(true)}
        style={{
          cursor: disabled ? 'default' : 'text',
          minHeight: multiline ? '40px' : undefined,
          padding: '8px 12px',
          border: '1px solid transparent',
          borderRadius: '6px',
          transition: 'all 0.2s ease',
          position: 'relative',
        }}
      >
        <span style={{ color: value ? '#333' : '#999', lineHeight: 1.6 }}>
          {value || placeholder}
        </span>
        {!disabled && (
          <div
            className="edit-icon-overlay"
            style={{
              position: 'absolute',
              right: 8,
              top: '50%',
              transform: 'translateY(-50%)',
              opacity: 0,
              transition: 'opacity 0.2s ease',
            }}
          >
            {onAIPolish && (
              <button
                className="btn-icon"
                onClick={(e) => {
                  e.stopPropagation();
                  onAIPolish();
                }}
                title="AI润色"
                style={{ marginRight: 4 }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 16, color: '#FF9F43' }}>
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
    <div className={`editable-field-edit ${className}`} style={{ position: 'relative' }}>
      {label && (
        <label style={{
          display: 'block',
          fontSize: 13,
          color: '#999',
          marginBottom: 6,
          fontWeight: 500,
        }}>
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
          className={`form-input ${error ? 'error' : ''}`}
          style={{
            width: '100%',
            minHeight: '80px',
            resize: 'vertical',
            borderColor: error ? '#DC2626' : '#2E86AB',
            paddingRight: onAIPolish ? 60 : 12,
          }}
        />
      ) : (
        <input
          type="text"
          value={editValue}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          placeholder={placeholder}
          className={`form-input ${error ? 'error' : ''}`}
          style={{
            width: '100%',
            borderColor: error ? '#DC2626' : '#2E86AB',
            paddingRight: onAIPolish ? 60 : 12,
          }}
        />
      )}
      {showCharCount && maxLength && (
        <div
          className={`char-count ${editValue.length > maxLength ? 'over-limit' : ''}`}
          style={{
            textAlign: 'right',
            marginTop: 4,
            fontSize: 11,
            color: editValue.length > maxLength ? '#DC2626' : '#999',
          }}
        >
          {editValue.length}/{maxLength}
        </div>
      )}
      {error && (
        <div className="error-message" style={{ color: '#DC2626', fontSize: 12, marginTop: 4 }}>
          {error}
        </div>
      )}
      {isEditing && onAIPolish && (
        <div
          style={{
            position: 'absolute',
            right: 8,
            top: label ? 36 : 8,
            display: 'flex',
            gap: 4,
          }}
        >
          <button
            className="btn-icon"
            onClick={(e) => {
              e.stopPropagation();
              onAIPolish();
            }}
            title="AI润色"
          >
            <span className="material-symbols-outlined" style={{ fontSize: 16, color: '#FF9F43' }}>
              auto_fix_high
            </span>
          </button>
        </div>
      )}
    </div>
  );
}