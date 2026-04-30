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
      <div
        className="fixed inset-0 z-[1000] flex items-center justify-center bg-black/50 animate-modal-fade"
        onClick={onCancel}
      >
        <div
          className="w-[500px] max-h-[80vh] max-w-[90%] overflow-y-auto rounded-xl bg-white p-6 shadow-2xl animate-modal-slide"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="mb-4 flex items-center justify-between">
            <h3 className="m-0 text-[16px] font-bold text-[#333]">批量修改里程碑</h3>
            <button
              className="flex h-8 w-8 items-center justify-center rounded-md hover:bg-[#1677ff]/10"
              onClick={onCancel}
            >
              <span className="material-symbols-outlined text-[20px]" style={{ color: '#666' }}>close</span>
            </button>
          </div>

          <div className="py-4">
            <p className="mb-4 text-[14px] text-[#666]">
              已选择 <strong>{selectedCount}</strong> 个里程碑
            </p>

            <div className="mb-4">
              <label className="mb-1.5 block text-[13px] font-medium text-[#999]">统一修改状态</label>
              <select
                className="w-full rounded-md border border-[#DCDCDC] bg-white px-3 py-2 text-[14px] text-[#333] transition-colors focus:border-[#1677ff] focus:outline-none focus:ring-2 focus:ring-[#1677ff]/20"
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

            <div className="mb-4">
              <label className="mb-1.5 block text-[13px] font-medium text-[#999]">统一修改完成时限</label>
              <input
                type="text"
                className="w-full rounded-md border border-[#1677ff] bg-white px-3 py-2 text-[14px] text-[#333] transition-colors focus:border-[#1677ff] focus:outline-none focus:ring-2 focus:ring-[#1677ff]/20"
                value={values.deadline || ''}
                onChange={(e) => setValues({ ...values, deadline: e.target.value })}
                placeholder="如：2026-06"
              />
            </div>

            {/* Preview selected milestones */}
            <div className="max-h-[200px] overflow-auto rounded-lg border border-[#E8F4F8] p-3">
              {milestones
                .filter((m) => selectedIds.includes(m.id))
                .map((m) => (
                  <div
                    key={m.id}
                    className="flex items-center justify-between border-b border-[#E8F4F8] py-2 last:border-b-0"
                  >
                    <span className="text-[#333]">{m.name}</span>
                    <span className="text-[12px] text-[#999]">
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

          <div className="mt-6 flex items-center justify-end gap-3">
            <button
              className="rounded-lg border border-[#DCDCDC] px-4 py-2 text-[14px] font-medium text-[#666] transition-colors hover:bg-gray-50"
              onClick={onCancel}
            >
              取消
            </button>
            <button
              className="rounded-lg bg-[#1677ff] px-4 py-2 text-[14px] font-medium text-white transition-all hover:scale-105 disabled:opacity-50 disabled:hover:scale-100"
              onClick={handleSave}
              disabled={!values.status && !values.deadline}
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