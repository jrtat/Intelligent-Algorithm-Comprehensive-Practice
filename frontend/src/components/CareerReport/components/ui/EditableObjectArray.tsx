import { useState } from 'react';
import { EditModal } from './EditModal';
import type { FormField } from './EditModal';
import { ConfirmDialog } from './ConfirmDialog';

interface EditableObjectArrayProps {
  items: Record<string, any>[];
  onChange: (items: Record<string, any>[]) => void;
  fields: FormField[];
  renderItem: (item: Record<string, any>, index: number) => React.ReactNode;
  label?: string;
  addLabel?: string;
  addInitialValues?: Record<string, any>;
}

export function EditableObjectArray({
  items,
  onChange,
  fields,
  renderItem,
  label,
  addLabel = '添加',
  addInitialValues = {},
}: EditableObjectArrayProps) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [isAdding, setIsAdding] = useState(false);
  const [deleteIndex, setDeleteIndex] = useState<number | null>(null);

  const handleEdit = (index: number) => {
    setEditingIndex(index);
  };

  const handleEditSave = (values: Record<string, any>) => {
    if (editingIndex === null) return;
    const newItems = [...items];
    newItems[editingIndex] = values;
    onChange(newItems);
    setEditingIndex(null);
  };

  const handleAdd = () => {
    setIsAdding(true);
  };

  const handleAddSave = (values: Record<string, any>) => {
    onChange([...items, values]);
    setIsAdding(false);
  };

  const handleDelete = (index: number) => {
    setDeleteIndex(index);
  };

  const handleDeleteConfirm = () => {
    if (deleteIndex === null) return;
    const newItems = items.filter((_, i) => i !== deleteIndex);
    onChange(newItems);
    setDeleteIndex(null);
  };

  return (
    <div className="editable-object-array">
      {label && (
        <h4
          style={{
            fontSize: 14,
            fontWeight: 500,
            color: '#333',
            marginBottom: 12,
            paddingBottom: 8,
            borderBottom: '1px solid #E8F4F8',
          }}
        >
          {label}
        </h4>
      )}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: 12,
        }}
      >
        {items.map((item, index) => (
          <div
            key={index}
            className="object-card-wrapper"
            style={{ position: 'relative' }}
          >
            {renderItem(item, index)}

            {/* Action buttons on hover */}
            <div
              className="object-card-actions"
              style={{
                position: 'absolute',
                top: 8,
                right: 8,
                display: 'flex',
                gap: 4,
                opacity: 0,
                transition: 'opacity 0.2s ease',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.opacity = '1')}
              onMouseLeave={(e) => (e.currentTarget.style.opacity = '0')}
            >
              <button
                className="btn-icon"
                onClick={() => handleEdit(index)}
                title="编辑"
                style={{
                  background: 'white',
                  boxShadow: '0 1px 4px rgba(0,0,0,0.1)',
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 16, color: '#666' }}>
                  edit
                </span>
              </button>
              <button
                className="btn-icon"
                onClick={() => handleDelete(index)}
                title="删除"
                style={{
                  background: 'white',
                  boxShadow: '0 1px 4px rgba(0,0,0,0.1)',
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 16, color: '#DC2626' }}>
                  delete
                </span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Add button */}
      <div style={{ marginTop: 16, textAlign: 'center' }}>
        <button
          className="btn btn-primary"
          onClick={handleAdd}
          style={{
            padding: '8px 16px',
            fontSize: 14,
            borderRadius: 8,
          }}
        >
          <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
            add
          </span>
          {addLabel}
        </button>
      </div>

      {/* Edit Modal */}
      {editingIndex !== null && (
        <EditModal
          title="编辑"
          fields={fields}
          initialValues={items[editingIndex]}
          onSave={handleEditSave}
          onCancel={() => setEditingIndex(null)}
        />
      )}

      {/* Add Modal */}
      {isAdding && (
        <EditModal
          title={addLabel}
          fields={fields}
          initialValues={addInitialValues}
          onSave={handleAddSave}
          onCancel={() => setIsAdding(false)}
        />
      )}

      {/* Delete Confirmation */}
      {deleteIndex !== null && (
        <ConfirmDialog
          title="确认删除"
          message="确认删除该项吗？"
          confirmText="删除"
          cancelText="取消"
          onConfirm={handleDeleteConfirm}
          onCancel={() => setDeleteIndex(null)}
        />
      )}
    </div>
  );
}
