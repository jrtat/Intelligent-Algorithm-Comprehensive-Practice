import { useState, useEffect } from 'react';

export interface FormField {
  key: string;
  label: string;
  type: 'text' | 'textarea' | 'select' | 'number';
  placeholder?: string;
  options?: { label: string; value: string }[];
  required?: boolean;
  maxLength?: number;
  validation?: (value: any) => string | null;
}

interface EditModalProps {
  title: string;
  fields: FormField[];
  initialValues: Record<string, any>;
  onSave: (values: Record<string, any>) => void;
  onCancel: () => void;
  onAIPolish?: () => void;
  width?: number;
  showAIPolish?: boolean;
}

export function EditModal({
  title,
  fields,
  initialValues,
  onSave,
  onCancel,
  onAIPolish,
  width = 450,
  showAIPolish = true,
}: EditModalProps) {
  const [values, setValues] = useState<Record<string, any>>(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    setValues(initialValues);
  }, [initialValues]);

  const handleChange = (key: string, value: any) => {
    setValues((prev) => ({ ...prev, [key]: value }));
    if (errors[key]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[key];
        return next;
      });
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    let isValid = true;

    fields.forEach((field) => {
      const value = values[field.key];
      if (field.required && (!value || (typeof value === 'string' && !value.trim()))) {
        newErrors[field.key] = '请填写该内容';
        isValid = false;
      }
      if (field.maxLength && typeof value === 'string' && value.length > field.maxLength) {
        newErrors[field.key] = `内容过长，请控制在${field.maxLength}字以内`;
        isValid = false;
      }
      if (field.validation) {
        const error = field.validation(value);
        if (error) {
          newErrors[field.key] = error;
          isValid = false;
        }
      }
    });

    setErrors(newErrors);
    return isValid;
  };

  const handleSave = () => {
    if (validate()) {
      onSave(values);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onCancel();
    }
  };

  const isSaveDisabled = Object.values(errors).some((e) => e) ||
    fields.some((f) => f.required && (!values[f.key] || (typeof values[f.key] === 'string' && !values[f.key].trim())));

  return (
    <div
      className="modal-overlay"
      onClick={onCancel}
      onKeyDown={handleKeyDown}
      role="dialog"
      aria-modal="true"
    >
      <div
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
        style={{ width, maxWidth: '90%' }}
      >
        <div className="modal-header">
          <h3 className="modal-title">{title}</h3>
          <button className="btn-icon" onClick={onCancel}>
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <div className="modal-body" style={{ padding: '16px 0' }}>
          {fields.map((field) => (
            <div key={field.key} className="form-group">
              <label
                className="form-label"
                style={{ color: '#999', fontWeight: 500 }}
              >
                {field.label}
                {field.required && <span style={{ color: '#DC2626' }}> *</span>}
              </label>

              {field.type === 'select' ? (
                <select
                  className={`form-input ${errors[field.key] ? 'error' : ''}`}
                  value={values[field.key] || ''}
                  onChange={(e) => handleChange(field.key, e.target.value)}
                  style={{
                    borderColor: errors[field.key] ? '#DC2626' : undefined,
                    cursor: 'pointer',
                  }}
                >
                  <option value="">请选择</option>
                  {field.options?.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              ) : field.type === 'textarea' ? (
                <div style={{ position: 'relative' }}>
                  <textarea
                    className={`form-input ${errors[field.key] ? 'error' : ''}`}
                    value={values[field.key] || ''}
                    onChange={(e) => handleChange(field.key, e.target.value)}
                    placeholder={field.placeholder}
                    maxLength={field.maxLength}
                    rows={4}
                    style={{
                      width: '100%',
                      minHeight: '100px',
                      resize: 'vertical',
                      borderColor: errors[field.key] ? '#DC2626' : '#2E86AB',
                    }}
                  />
                  {field.maxLength && (
                    <div
                      style={{
                        position: 'absolute',
                        right: 8,
                        bottom: 8,
                        fontSize: 11,
                        color: (values[field.key]?.length || 0) > field.maxLength ? '#DC2626' : '#999',
                      }}
                    >
                      {(values[field.key] || '').length}/{field.maxLength}
                    </div>
                  )}
                </div>
              ) : (
                <input
                  type={field.type}
                  className={`form-input ${errors[field.key] ? 'error' : ''}`}
                  value={values[field.key] || ''}
                  onChange={(e) => handleChange(field.key, e.target.value)}
                  placeholder={field.placeholder}
                  style={{
                    borderColor: errors[field.key] ? '#DC2626' : '#2E86AB',
                  }}
                />
              )}

              {errors[field.key] && (
                <div
                  className="error-message"
                  style={{ color: '#DC2626', fontSize: 12, marginTop: 4 }}
                >
                  {errors[field.key]}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="modal-footer">
          {showAIPolish && onAIPolish && (
            <button className="btn btn-outline" onClick={onAIPolish}>
              <span className="material-symbols-outlined" style={{ fontSize: 16, color: '#FF9F43' }}>
                auto_fix_high
              </span>
              AI润色
            </button>
          )}
          <div style={{ flex: 1 }} />
          <button className="btn btn-outline" onClick={onCancel}>
            取消
          </button>
          <button
            className="btn btn-primary"
            onClick={handleSave}
            disabled={isSaveDisabled}
            style={{
              opacity: isSaveDisabled ? 0.5 : 1,
              cursor: isSaveDisabled ? 'not-allowed' : 'pointer',
            }}
          >
            保存
          </button>
        </div>
      </div>
    </div>
  );
}
