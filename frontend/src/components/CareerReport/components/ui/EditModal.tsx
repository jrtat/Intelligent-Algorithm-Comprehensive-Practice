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
      className="fixed inset-0 z-[1000] flex items-center justify-center bg-black/50 animate-modal-fade"
      onClick={onCancel}
      onKeyDown={handleKeyDown}
      role="dialog"
      aria-modal="true"
    >
      <div
        className="max-h-[80vh] w-[450px] max-w-[90%] overflow-y-auto rounded-xl bg-white !p-6 shadow-2xl animate-modal-slide"
        onClick={(e) => e.stopPropagation()}
        style={{ width }}
      >
        <div className="mb-4 flex items-center justify-between">
          <h3 className="!m-0 text-[16px] font-bold text-[#333]">{title}</h3>
          <button
            className="flex !h-8 !w-8 items-center justify-center rounded-md hover:bg-[#1677ff]/10"
            onClick={onCancel}
          >
            <span className="material-symbols-outlined text-[20px]" style={{ color: '#666' }}>close</span>
          </button>
        </div>

        <div className="space-y-4 !py-4">
          {fields.map((field) => (
            <div key={field.key} className="mb-4">
              <label className="mb-1.5 block text-[13px] font-medium text-[#999]">
                {field.label}
                {field.required && <span className="text-red-500"> *</span>}
              </label>

              {field.type === 'select' ? (
                <select
                  className={`w-full rounded-md border bg-white !px-3 !py-2 text-[14px] text-[#333] transition-colors focus:outline-none focus:ring-2 ${errors[field.key] ? 'border-red-500 focus:ring-red-500/20' : 'border-[#DCDCDC] focus:border-[#1677ff] focus:ring-[#1677ff]/20'}`}
                  value={values[field.key] || ''}
                  onChange={(e) => handleChange(field.key, e.target.value)}
                  style={{ cursor: 'pointer' }}
                >
                  <option value="">请选择</option>
                  {field.options?.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              ) : field.type === 'textarea' ? (
                <div className="relative">
                  <textarea
                    className={`w-full resize-y rounded-md border bg-white !px-3 !py-2 text-[14px] text-[#333] transition-colors focus:outline-none focus:ring-2 ${errors[field.key] ? 'border-red-500 focus:ring-red-500/20' : 'border-[#1677ff] focus:ring-[#1677ff]/20'}`}
                    value={values[field.key] || ''}
                    onChange={(e) => handleChange(field.key, e.target.value)}
                    placeholder={field.placeholder}
                    maxLength={field.maxLength}
                    rows={4}
                    style={{ minHeight: '100px' }}
                  />
                  {field.maxLength && (
                    <div
                      className="absolute !bottom-2 !right-2 text-[11px]"
                      style={{ color: (values[field.key]?.length || 0) > field.maxLength ? '#DC2626' : '#999' }}
                    >
                      {(values[field.key] || '').length}/{field.maxLength}
                    </div>
                  )}
                </div>
              ) : (
                <input
                  type={field.type}
                  className={`w-full rounded-md border bg-white !px-3 !py-2 text-[14px] text-[#333] transition-colors focus:outline-none focus:ring-2 ${errors[field.key] ? 'border-red-500 focus:ring-red-500/20' : 'border-[#1677ff] focus:ring-[#1677ff]/20'}`}
                  value={values[field.key] || ''}
                  onChange={(e) => handleChange(field.key, e.target.value)}
                  placeholder={field.placeholder}
                />
              )}

              {errors[field.key] && (
                <div className="mt-1 text-[12px] text-red-500">
                  {errors[field.key]}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="mt-6 flex items-center justify-end gap-3">
          {showAIPolish && onAIPolish && (
            <button className="inline-flex items-center gap-1 rounded-lg border border-[#DCDCDC] !px-4 !py-2 text-[14px] font-medium text-[#666] transition-colors hover:bg-gray-50">
              <span className="material-symbols-outlined text-[16px]" style={{ color: '#FF9F43' }}>
                auto_fix_high
              </span>
              AI润色
            </button>
          )}
          <div className="flex-1" />
          <button className="rounded-lg border border-[#DCDCDC] !px-4 !py-2 text-[14px] font-medium text-[#666] transition-colors hover:bg-gray-50" onClick={onCancel}>
            取消
          </button>
          <button
            className="rounded-lg bg-[#1677ff] !px-4 !py-2 text-[14px] font-medium text-white transition-all hover:scale-105 disabled:opacity-50 disabled:hover:scale-100"
            onClick={handleSave}
            disabled={isSaveDisabled}
          >
            保存
          </button>
        </div>
      </div>
    </div>
  );
}