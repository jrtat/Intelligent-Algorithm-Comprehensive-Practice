import { useState } from 'react';
import { EditModal } from './EditModal';
import type { FormField } from './EditModal';
import { ConfirmDialog } from './ConfirmDialog';

interface MilestoneItem {
  id: string;
  name: string;
  deadline?: string;
  status?: 'pending' | 'in_progress' | 'completed';
  description?: string;
  relatedGoal?: string;
  relatedActions?: string[];
}

interface MilestoneEditModalProps {
  milestone: MilestoneItem | null;
  allActions?: { label: string; value: string }[];
  onSave: (milestone: MilestoneItem) => void;
  onDelete?: () => void;
  onCancel: () => void;
  onAIPolish?: () => void;
  mode?: 'quick' | 'detail';
}

const quickEditFields: FormField[] = [
  {
    key: 'name',
    label: '里程碑名称',
    type: 'text',
    placeholder: '请输入里程碑名称',
    required: true,
    maxLength: 100,
  },
  {
    key: 'deadline',
    label: '完成时限',
    type: 'text',
    placeholder: '如：2026-06',
  },
];

const detailEditFields: FormField[] = [
  {
    key: 'name',
    label: '里程碑名称',
    type: 'text',
    placeholder: '请输入里程碑名称',
    required: true,
    maxLength: 100,
  },
  {
    key: 'deadline',
    label: '完成时限',
    type: 'text',
    placeholder: '如：2026-06',
  },
  {
    key: 'relatedGoal',
    label: '关联目标',
    type: 'text',
    placeholder: '请输入关联目标',
    maxLength: 200,
  },
  {
    key: 'description',
    label: '具体要求',
    type: 'textarea',
    placeholder: '请输入具体要求',
    maxLength: 500,
  },
  {
    key: 'status',
    label: '状态',
    type: 'select',
    options: [
      { label: '未开始', value: 'pending' },
      { label: '进行中', value: 'in_progress' },
      { label: '已完成', value: 'completed' },
    ],
  },
];

export const batchEditFields: FormField[] = [
  {
    key: 'status',
    label: '状态',
    type: 'select',
    options: [
      { label: '未开始', value: 'pending' },
      { label: '进行中', value: 'in_progress' },
      { label: '已完成', value: 'completed' },
    ],
  },
  {
    key: 'deadline',
    label: '完成时限',
    type: 'text',
    placeholder: '如：2026-06',
  },
];

interface MilestoneBatchEditModalProps {
  milestones: MilestoneItem[];
  selectedIds: string[];
  onSave: (updates: { status?: string; deadline?: string }) => void;
  onCancel: () => void;
}

export function MilestoneBatchEditModal({
  milestones,
  selectedIds,
  onSave,
  onCancel,
}: MilestoneBatchEditModalProps) {
  const [values, setValues] = useState<{ status?: string; deadline?: string }>({});
  const [showConfirm, setShowConfirm] = useState(false);

  const handleSave = () => {
    setShowConfirm(true);
  };

  const handleConfirm = () => {
    onSave(values);
    setShowConfirm(false);
  };

  const selectedCount = selectedIds.length;

  return (
    <>
      <div className="modal-overlay" onClick={onCancel}>
        <div
          className="modal-content"
          onClick={(e) => e.stopPropagation()}
          style={{ width: 500, maxWidth: '90%' }}
        >
          <div className="modal-header">
            <h3 className="modal-title">批量修改里程碑</h3>
            <button className="btn-icon" onClick={onCancel}>
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>

          <div style={{ padding: '16px 0' }}>
            <p style={{ fontSize: 14, color: '#666', marginBottom: 16 }}>
              已选择 <strong>{selectedCount}</strong> 个里程碑
            </p>

            <div style={{ marginBottom: 16 }}>
              <label className="form-label">统一修改状态</label>
              <select
                className="form-input"
                value={values.status || ''}
                onChange={(e) => setValues({ ...values, status: e.target.value })}
                style={{ cursor: 'pointer' }}
              >
                <option value="">不修改</option>
                <option value="pending">未开始</option>
                <option value="in_progress">进行中</option>
                <option value="completed">已完成</option>
              </select>
            </div>

            <div style={{ marginBottom: 16 }}>
              <label className="form-label">统一修改完成时限</label>
              <input
                type="text"
                className="form-input"
                value={values.deadline || ''}
                onChange={(e) => setValues({ ...values, deadline: e.target.value })}
                placeholder="如：2026-06"
                style={{ borderColor: '#2E86AB' }}
              />
            </div>

            {/* Preview selected milestones */}
            <div
              style={{
                maxHeight: 200,
                overflow: 'auto',
                border: '1px solid #E8F4F8',
                borderRadius: 8,
                padding: 12,
              }}
            >
              {milestones
                .filter((m) => selectedIds.includes(m.id))
                .map((m) => (
                  <div
                    key={m.id}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      padding: '8px 0',
                      borderBottom: '1px solid #E8F4F8',
                    }}
                  >
                    <span style={{ color: '#333' }}>{m.name}</span>
                    <span style={{ color: '#999', fontSize: 12 }}>
                      {m.status === 'pending'
                        ? '未开始'
                        : m.status === 'in_progress'
                          ? '进行中'
                          : '已完成'}
                    </span>
                  </div>
                ))}
            </div>
          </div>

          <div className="modal-footer">
            <button className="btn btn-outline" onClick={onCancel}>
              取消
            </button>
            <button
              className="btn btn-primary"
              onClick={handleSave}
              disabled={!values.status && !values.deadline}
              style={{
                opacity: !values.status && !values.deadline ? 0.5 : 1,
                cursor: !values.status && !values.deadline ? 'not-allowed' : 'pointer',
              }}
            >
              确认批量修改
            </button>
          </div>
        </div>
      </div>

      {showConfirm && (
        <ConfirmDialog
          title="确认批量修改"
          message={`确认批量修改选中的${selectedCount}个里程碑吗？`}
          confirmText="确认修改"
          cancelText="取消"
          onConfirm={handleConfirm}
          onCancel={() => setShowConfirm(false)}
        />
      )}
    </>
  );
}

export function MilestoneEditModal({
  milestone,
  onSave,
  onDelete,
  onCancel,
  onAIPolish,
  mode = 'detail',
}: MilestoneEditModalProps) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  if (!milestone) return null;

  const fields = mode === 'quick' ? quickEditFields : detailEditFields;
  const initialValues = {
    name: milestone.name || '',
    deadline: milestone.deadline || '',
    status: milestone.status || 'pending',
    description: milestone.description || '',
    relatedGoal: milestone.relatedGoal || '',
  };

  const handleSave = (values: Record<string, any>) => {
    onSave({
      ...milestone,
      ...values,
    });
  };

  return (
    <>
      <EditModal
        title={mode === 'quick' ? '快速编辑' : '编辑里程碑'}
        fields={fields}
        initialValues={initialValues}
        onSave={handleSave}
        onCancel={onCancel}
        onAIPolish={onAIPolish}
        width={mode === 'quick' ? 380 : 450}
      />
      {showDeleteConfirm && onDelete && (
        <ConfirmDialog
          title="确认删除"
          message={`确认删除里程碑"${milestone.name}"吗？`}
          confirmText="删除"
          cancelText="取消"
          onConfirm={() => {
            onDelete();
            setShowDeleteConfirm(false);
          }}
          onCancel={() => setShowDeleteConfirm(false)}
        />
      )}
    </>
  );
}
