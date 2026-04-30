import { useState } from 'react';
import { ConfirmDialog } from './ConfirmDialog';

interface EditableListProps {
  items: string[];
  onChange: (items: string[]) => void;
  onAIPolishItem?: (index: number) => void;
  onAIPolishAll?: () => void;
  label?: string;
  addLabel?: string;
  placeholder?: string;
  maxLength?: number;
  disabled?: boolean;
}

export function EditableList({
  items,
  onChange,
  onAIPolishItem,
  onAIPolishAll,
  label,
  addLabel = '添加',
  placeholder = '请输入内容',
  disabled = false,
}: EditableListProps) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editValue, setEditValue] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [addValue, setAddValue] = useState('');
  const [deleteIndex, setDeleteIndex] = useState<number | null>(null);

  const handleEditStart = (index: number) => {
    if (disabled) return;
    setEditingIndex(index);
    setEditValue(items[index]);
  };

  const handleEditSave = () => {
    if (editingIndex === null) return;
    const newItems = [...items];
    newItems[editingIndex] = editValue;
    onChange(newItems);
    setEditingIndex(null);
    setEditValue('');
  };

  const handleEditCancel = () => {
    setEditingIndex(null);
    setEditValue('');
  };

  const handleAddStart = () => {
    if (disabled) return;
    setIsAdding(true);
    setAddValue('');
  };

  const handleAddSave = () => {
    if (!addValue.trim()) return;
    onChange([...items, addValue.trim()]);
    setIsAdding(false);
    setAddValue('');
  };

  const handleAddCancel = () => {
    setIsAdding(false);
    setAddValue('');
  };

  const handleDeleteConfirm = () => {
    if (deleteIndex === null) return;
    const newItems = items.filter((_, i) => i !== deleteIndex);
    onChange(newItems);
    setDeleteIndex(null);
  };

  return (
    <div className="editable-list">
      {label && (
        <div className="!mb-2 flex items-center justify-between">
          <h4 className="m-0 text-[16px] font-medium text-[#666]">{label}</h4>
          {onAIPolishAll && !disabled && (
            <button
              className="inline-flex items-center !gap-1 rounded-md border border-[#FF9F43] !px-2 !py-1 text-[12px] text-[#FF9F43] transition-colors hover:bg-[rgba(255,159,67,0.1)]"
              onClick={onAIPolishAll}
              title="AI润色"
            >
              <span className="material-symbols-outlined text-[16px]">auto_fix_high</span>
              AI润色
            </button>
          )}
        </div>
      )}

      <ul className="list-none !pl-0" style={{ position: 'relative' }}>
        {items.map((item, index) => (
          <li
            key={index}
            className="group relative !mb-3 flex items-start justify-between"
            style={{ paddingRight: editingIndex === index ? 0 : '80px' }}
          >
            {editingIndex === index ? (
              <div className="flex !flex-1 !gap-2">
                <input
                  type="text"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleEditSave();
                    if (e.key === 'Escape') handleEditCancel();
                  }}
                  autoFocus
                  className="flex-1 rounded-md border border-[#1677ff] bg-white !px-3 !py-2 text-[14px] text-[#333] transition-colors focus:border-[#1677ff] focus:outline-none focus:ring-2 focus:ring-[#1677ff]/20"
                />
                <button
                  className="rounded-md bg-[#1677ff] !px-3 !py-1.5 text-[13px] font-medium text-white transition-transform hover:scale-105"
                  onClick={handleEditSave}
                >
                  保存
                </button>
                <button
                  className="rounded-md border border-[#DCDCDC] !px-3 !py-1.5 text-[13px] font-medium text-[#666] transition-colors hover:bg-gray-50"
                  onClick={handleEditCancel}
                >
                  取消
                </button>
              </div>
            ) : (
              <>
                <span className={`flex-1 ${disabled ? 'cursor-default' : 'cursor-text'} text-[#333]`}>
                  · {item}
                </span>
                {!disabled && (
                  <div
                    className="item-actions absolute right-0 top-0 flex gap-1 bg-white !pl-2 opacity-0 transition-opacity group-hover:opacity-100"
                  >
                    <button
                      className="flex h-8 w-8 items-center justify-center rounded-md hover:bg-[#1677ff]/10"
                      onClick={() => handleEditStart(index)}
                      title="编辑"
                    >
                      <span className="material-symbols-outlined text-[16px]" style={{ color: '#666' }}>
                        edit
                      </span>
                    </button>
                    {onAIPolishItem && (
                      <button
                        className="flex h-8 w-8 items-center justify-center rounded-md hover:bg-[#FF9F43]/10"
                        onClick={() => onAIPolishItem(index)}
                        title="AI润色"
                      >
                        <span className="material-symbols-outlined text-[16px]" style={{ color: '#FF9F43' }}>
                          auto_fix_high
                        </span>
                      </button>
                    )}
                    <button
                      className="flex h-8 w-8 items-center justify-center rounded-md hover:bg-red-50"
                      onClick={() => setDeleteIndex(index)}
                      title="删除"
                    >
                      <span className="material-symbols-outlined text-[16px]" style={{ color: '#DC2626' }}>
                        delete
                      </span>
                    </button>
                  </div>
                )}
              </>
            )}
          </li>
        ))}
      </ul>

      {/* Add button / form */}
      {!disabled && (
        <div className="mt-3 text-center">
          {isAdding ? (
            <div className="flex justify-center gap-2">
              <input
                type="text"
                value={addValue}
                onChange={(e) => setAddValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleAddSave();
                  if (e.key === 'Escape') handleAddCancel();
                }}
                placeholder={placeholder}
                autoFocus
                className="w-[200px] rounded-md border border-[#1677ff] bg-white !px-3 !py-2 text-[14px] text-[#333] transition-colors focus:border-[#1677ff] focus:outline-none focus:ring-2 focus:ring-[#1677ff]/20"
              />
              <button
                className="rounded-md bg-[#1677ff] !px-3 !py-1.5 text-[13px] font-medium text-white transition-transform hover:scale-105 disabled:opacity-50 disabled:hover:scale-100"
                onClick={handleAddSave}
                disabled={!addValue.trim()}
              >
                提交
              </button>
              <button
                className="rounded-md border border-[#DCDCDC] !px-3 !py-1.5 text-[13px] font-medium text-[#666] transition-colors hover:bg-gray-50"
                onClick={handleAddCancel}
              >
                取消
              </button>
            </div>
          ) : (
            <button
              className="inline-flex items-center gap-1 rounded-lg bg-[#1677ff] !px-4 !py-1.5 text-[13px] font-medium text-white transition-transform hover:scale-105"
              onClick={handleAddStart}
            >
              <span className="material-symbols-outlined text-[16px]">add</span>
              {addLabel}
            </button>
          )}
        </div>
      )}

      {/* Delete confirmation */}
      {deleteIndex !== null && (
        <ConfirmDialog
          title="确认删除"
          message={`确认删除该项"${items[deleteIndex]}"吗？`}
          confirmText="删除"
          cancelText="取消"
          onConfirm={handleDeleteConfirm}
          onCancel={() => setDeleteIndex(null)}
        />
      )}
    </div>
  );
}