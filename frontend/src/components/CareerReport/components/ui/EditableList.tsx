import { useState } from 'react';
import { ConfirmDialog } from './ConfirmDialog';

interface EditableListProps {
  items: string[];
  onChange: (items: string[]) => void;
  onAIPolish?: (index: number) => void;
  label?: string;
  addLabel?: string;
  placeholder?: string;
  maxLength?: number;
}

export function EditableList({
  items,
  onChange,
  onAIPolish,
  label,
  addLabel = '添加',
  placeholder = '请输入内容',
  maxLength = 500,
}: EditableListProps) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editValue, setEditValue] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [addValue, setAddValue] = useState('');
  const [deleteIndex, setDeleteIndex] = useState<number | null>(null);

  const handleEditStart = (index: number) => {
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
        <h4
          style={{
            fontSize: 14,
            fontWeight: 500,
            color: '#666',
            marginBottom: 8,
          }}
        >
          {label}
        </h4>
      )}

      <ul className="list-with-bullets" style={{ position: 'relative' }}>
        {items.map((item, index) => (
          <li
            key={index}
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              justifyContent: 'space-between',
              paddingRight: editingIndex === index ? 0 : 60,
            }}
          >
            {editingIndex === index ? (
              <div style={{ flex: 1, display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                <input
                  type="text"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleEditSave();
                    if (e.key === 'Escape') handleEditCancel();
                  }}
                  autoFocus
                  className="form-input"
                  style={{
                    flex: 1,
                    borderColor: '#2E86AB',
                  }}
                />
                <button
                  className="btn btn-primary"
                  onClick={handleEditSave}
                  style={{ padding: '6px 12px', fontSize: 13 }}
                >
                  保存
                </button>
                <button
                  className="btn btn-outline"
                  onClick={handleEditCancel}
                  style={{ padding: '6px 12px', fontSize: 13 }}
                >
                  取消
                </button>
              </div>
            ) : (
              <>
                <span
                  style={{
                    color: '#333',
                    flex: 1,
                    cursor: 'text',
                  }}
                >
                  {item}
                </span>
                <div
                  className="item-actions"
                  style={{
                    display: 'flex',
                    gap: 4,
                    opacity: 0,
                    transition: 'opacity 0.2s ease',
                    position: 'absolute',
                    right: 0,
                    top: 0,
                    background: 'white',
                    paddingLeft: 8,
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.opacity = '1')}
                  onMouseLeave={(e) => (e.currentTarget.style.opacity = '0')}
                >
                  <button
                    className="btn-icon"
                    onClick={() => handleEditStart(index)}
                    title="编辑"
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: 16, color: '#666' }}>
                      edit
                    </span>
                  </button>
                  {onAIPolish && (
                    <button
                      className="btn-icon"
                      onClick={() => onAIPolish(index)}
                      title="AI润色"
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 16, color: '#FF9F43' }}>
                        auto_fix_high
                      </span>
                    </button>
                  )}
                  <button
                    className="btn-icon"
                    onClick={() => setDeleteIndex(index)}
                    title="删除"
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: 16, color: '#DC2626' }}>
                      delete
                    </span>
                  </button>
                </div>
              </>
            )}
          </li>
        ))}
      </ul>

      {/* Add button / form */}
      <div style={{ marginTop: 12, textAlign: 'center' }}>
        {isAdding ? (
          <div style={{ display: 'flex', gap: 8, justifyContent: 'center' }}>
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
              className="form-input"
              style={{ width: 200, borderColor: '#2E86AB' }}
            />
            <button
              className="btn btn-primary"
              onClick={handleAddSave}
              disabled={!addValue.trim()}
              style={{ padding: '6px 12px', fontSize: 13 }}
            >
              提交
            </button>
            <button
              className="btn btn-outline"
              onClick={handleAddCancel}
              style={{ padding: '6px 12px', fontSize: 13 }}
            >
              取消
            </button>
          </div>
        ) : (
          <button
            className="btn btn-primary"
            onClick={handleAddStart}
            style={{
              padding: '6px 16px',
              fontSize: 13,
              borderRadius: 8,
            }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
              add
            </span>
            {addLabel}
          </button>
        )}
      </div>

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
