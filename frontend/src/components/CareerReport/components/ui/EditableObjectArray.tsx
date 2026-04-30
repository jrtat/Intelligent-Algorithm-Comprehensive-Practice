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
  containerClassName?: string;
}

export function EditableObjectArray({
  items,
  onChange,
  fields,
  renderItem,
  label,
  addLabel = '添加',
  addInitialValues = {},
  containerClassName = '',
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
        <h4 className="!mb-3 border-b border-[#E8F4F8] !pb-2 text-[16px] font-medium text-[#333]">
          {label}
        </h4>
      )}

      <div className={`grid !gap-3 !grid-cols-1 sm:!grid-cols-1 lg:!grid-cols-1 ${containerClassName}`}>
        {items.map((item, index) => (
          <div
            key={index}
            className="object-card-wrapper group relative"
          >
            {renderItem(item, index)}

            {/* Action buttons on hover */}
            <div
              className="object-card-actions absolute !right-2 !top-2 flex !gap-1 !opacity-0 transition-opacity group-hover:opacity-100"
            >
              <button
                className="flex !h-8 !w-8 items-center justify-center rounded-md bg-white shadow-sm hover:bg-[#1677ff]/10"
                onClick={() => handleEdit(index)}
                title="编辑"
              >
                <span className="material-symbols-outlined text-[16px]" style={{ color: '#666' }}>
                  edit
                </span>
              </button>
              <button
                className="flex !h-8 !w-8 items-center justify-center rounded-md bg-white shadow-sm hover:bg-red-50"
                onClick={() => handleDelete(index)}
                title="删除"
              >
                <span className="material-symbols-outlined text-[16px]" style={{ color: '#DC2626' }}>
                  delete
                </span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Add button */}
      <div className="!mt-4 text-center">
        <button
          className="inline-flex items-center !gap-1 rounded-lg bg-[#1677ff] !px-4 !py-2 text-[16px] font-medium text-white transition-transform hover:scale-105"
          onClick={handleAdd}
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
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