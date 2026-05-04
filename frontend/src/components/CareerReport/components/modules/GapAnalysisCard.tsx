import { useState, useEffect } from 'react';
import { ReportCard } from '../ReportCard.tsx';
import { GapCard } from '../ui/GapCard.tsx';
import { EditableList } from '../ui/EditableList.tsx';
import type { FormField } from '../ui/EditModal.tsx';
import { useReport } from '../../context/ReportContext.tsx';
import type { Gap } from '../../../../types/job.ts';
import { ConfirmDialog } from '../ui/ConfirmDialog.tsx';

interface GapAnalysisCardProps {
  isEditing?: boolean;
  onEdit?: () => void;
  onSave?: () => void;
  onCancel?: () => void;
  onAIPolishModule?: (moduleId: string) => void;
  onAIPolishField?: (fieldPath: string) => void;
  isPolishing?: boolean;
  saveStatus?: 'idle' | 'saving' | 'saved' | 'error';
}

const importanceOptions = [
  { label: '高', value: '高' },
  { label: '中', value: '中' },
  { label: '低', value: '低' },
];

const levelOptions = [
  { label: '无', value: '无' },
  { label: '基础', value: '基础' },
  { label: '掌握', value: '掌握' },
  { label: '熟悉', value: '熟悉' },
  { label: '熟练', value: '熟练' },
  { label: '精通', value: '精通' },
];

// 不含 learning_resources 的字段定义，用于基础编辑
const gapBaseFields: FormField[] = [
  {
    key: 'skill',
    label: '技能名称',
    type: 'text',
    placeholder: '请输入技能名称',
    required: true,
    maxLength: 100,
  },
  {
    key: 'importance',
    label: '重要性',
    type: 'select',
    options: importanceOptions,
    required: true,
  },
  {
    key: 'current_level',
    label: '当前水平',
    type: 'select',
    options: levelOptions,
  },
  {
    key: 'target_level',
    label: '目标水平',
    type: 'select',
    options: levelOptions,
  },
];

// 学习资源内嵌编辑器
interface LearningResourcesEditorProps {
  resources: string[];
  onChange: (resources: string[]) => void;
}

function LearningResourcesEditor({ resources, onChange }: LearningResourcesEditorProps) {
  const [isAdding, setIsAdding] = useState(false);
  const [addValue, setAddValue] = useState('');
  const [deleteIndex, setDeleteIndex] = useState<number | null>(null);

  const handleAddSave = () => {
    if (!addValue.trim()) return;
    onChange([...resources, addValue.trim()]);
    setAddValue('');
    setIsAdding(false);
  };

  const handleDeleteConfirm = () => {
    if (deleteIndex === null) return;
    onChange(resources.filter((_, i) => i !== deleteIndex));
    setDeleteIndex(null);
  };

  return (
    <div className="learning-resources-editor">
      {resources.length > 0 && (
        <ul className="list-none !pl-0 !mb-2 space-y-2">
          {resources.map((resource, index) => (
            <li key={index} className="group relative flex items-center gap-2">
              <span className="flex items-center justify-center w-4 text-[#1677ff]">·</span>
              <span className="flex-1 text-[14px] text-[#333]">{resource}</span>
              <div className="item-actions absolute right-0 top-0 flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                <button
                  className="flex h-7 w-7 items-center justify-center rounded-md hover:bg-red-50"
                  onClick={() => setDeleteIndex(index)}
                  title="删除"
                >
                  <span className="material-symbols-outlined text-[14px]" style={{ color: '#DC2626' }}>delete</span>
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
      <div className="mt-2 text-center">
        {isAdding ? (
          <div className="flex justify-center gap-2">
            <input
              type="text"
              value={addValue}
              onChange={(e) => setAddValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleAddSave();
                if (e.key === 'Escape') { setIsAdding(false); setAddValue(''); }
              }}
              placeholder="请输入学习资源"
              autoFocus
              className="w-[200px] rounded-md border border-[#1677ff] bg-white !px-3 !py-2 text-[14px] text-[#333] transition-colors focus:border-[#1677ff] focus:outline-none focus:ring-2 focus:ring-[#1677ff]/20"
            />
            <button
              className="rounded-md bg-[#1677ff] !px-3 !py-1.5 text-[13px] font-medium text-white transition-transform hover:scale-105"
              onClick={handleAddSave}
              disabled={!addValue.trim()}
            >
              提交
            </button>
            <button
              className="rounded-md border border-[#DCDCDC] !px-3 !py-1.5 text-[13px] font-medium text-[#666] transition-colors hover:bg-gray-50"
              onClick={() => { setIsAdding(false); setAddValue(''); }}
            >
              取消
            </button>
          </div>
        ) : (
          <button
            className="inline-flex items-center gap-1 rounded-lg bg-[#f5f7fa] border border-[#dcdcdc] !px-3 !py-1.5 text-[13px] font-medium text-[#666] transition-colors hover:bg-[#1677ff]/10 hover:border-[#1677ff] hover:text-[#1677ff]"
            onClick={() => setIsAdding(true)}
          >
            <span className="material-symbols-outlined text-[16px]">add</span>
            添加表单项
          </button>
        )}
      </div>
      {deleteIndex !== null && (
        <ConfirmDialog
          title="确认删除"
          message={`确认删除该项"${resources[deleteIndex]}"吗？`}
          confirmText="删除"
          cancelText="取消"
          onConfirm={handleDeleteConfirm}
          onCancel={() => setDeleteIndex(null)}
        />
      )}
    </div>
  );
}

// 自定义 Gap 编辑弹窗（learning_resources 使用内嵌列表）
interface GapEditModalProps {
  isOpen: boolean;
  title: string;
  initialValues: Gap;
  onSave: (gap: Gap) => void;
  onCancel: () => void;
}

function GapEditModal({ isOpen, title, initialValues, onSave, onCancel }: GapEditModalProps) {
  const [values, setValues] = useState<Gap>(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    setValues(initialValues);
  }, [initialValues]);

  const handleChange = (key: keyof Gap, val: string) => {
    setValues((prev) => ({ ...prev, [key]: val }));
    if (errors[key]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[key];
        return next;
      });
    }
  };

  const handleResourcesChange = (resources: string[]) => {
    setValues((prev) => ({ ...prev, learning_resources: resources }));
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!values.skill?.trim()) {
      newErrors.skill = '请填写技能名称';
    }
    if (!values.importance) {
      newErrors.importance = '请选择重要性';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (validate()) {
      onSave(values);
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[1000] flex items-center justify-center bg-black/50 animate-modal-fade"
      onClick={onCancel}
    >
      <div
        className="max-h-[80vh] w-[450px] max-w-[90%] overflow-y-auto rounded-xl bg-white !p-6 shadow-2xl animate-modal-slide"
        onClick={(e) => e.stopPropagation()}
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
          {gapBaseFields.map((field) => (
            <div key={field.key} className="mb-4">
              <label className="mb-1.5 block text-[13px] font-medium text-[#999]">
                {field.label}
                {field.required && <span className="text-red-500"> *</span>}
              </label>
              {field.type === 'select' ? (
                <select
                  className={`w-full rounded-md border bg-white !px-3 !py-2 text-[14px] text-[#333] transition-colors focus:outline-none focus:ring-2 ${errors[field.key] ? 'border-red-500 focus:ring-red-500/20' : 'border-[#DCDCDC] focus:border-[#1677ff] focus:ring-[#1677ff]/20'}`}
                  value={values[field.key as keyof Gap] as string}
                  onChange={(e) => handleChange(field.key as keyof Gap, e.target.value)}
                  style={{ cursor: 'pointer' }}
                >
                  <option value="">请选择</option>
                  {field.options?.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              ) : (
                <input
                  type="text"
                  className={`w-full rounded-md border bg-white !px-3 !py-2 text-[14px] text-[#333] transition-colors focus:outline-none focus:ring-2 ${errors[field.key] ? 'border-red-500 focus:ring-red-500/20' : 'border-[#DCDCDC] focus:border-[#1677ff] focus:ring-[#1677ff]/20'}`}
                  value={values[field.key as keyof Gap] as string}
                  onChange={(e) => handleChange(field.key as keyof Gap, e.target.value)}
                  placeholder={field.placeholder}
                />
              )}
              {errors[field.key] && (
                <div className="mt-1 text-[12px] text-red-500">{errors[field.key]}</div>
              )}
            </div>
          ))}

          {/* 学习资源 - 内嵌列表编辑器 */}
          <div className="mb-4">
            <label className="mb-1.5 block text-[13px] font-medium text-[#999]">学习资源</label>
            <LearningResourcesEditor
              resources={values.learning_resources}
              onChange={handleResourcesChange}
            />
          </div>
        </div>

        <div className="mt-6 flex items-center justify-end gap-3">
          <button
            className="rounded-lg border border-[#DCDCDC] !px-4 !py-2 text-[14px] font-medium text-[#666] transition-colors hover:bg-gray-50"
            onClick={onCancel}
          >
            取消
          </button>
          <button
            className="rounded-lg bg-[#1677ff] !px-4 !py-2 text-[14px] font-medium text-white transition-all hover:scale-105"
            onClick={handleSave}
          >
            保存
          </button>
        </div>
      </div>
    </div>
  );
}

export function GapAnalysisCard({
  isEditing = false,
  onEdit,
  onSave,
  onCancel,
  onAIPolishModule,
  onAIPolishField,
  isPolishing = false,
  saveStatus = 'idle',
}: GapAnalysisCardProps) {
  const { state, updateReport } = useReport();
  const { report } = state;

  const [editingGap, setEditingGap] = useState<{ category: string; index: number; gap: Gap } | null>(null);
  const [addingCategory, setAddingCategory] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<{ category: string; index: number } | null>(null);

  if (!report?.gap_analysis) return null;

  const { hard_skills_gaps, soft_skills_gaps, experience_gaps, certification_needs } = report.gap_analysis;

  const handleGapsChange = (category: string, items: Gap[]) => {
    updateReport({
      gap_analysis: {
        ...report.gap_analysis,
        [category]: items,
      },
    });
  };

  const handleCertChange = (items: string[]) => {
    updateReport({
      gap_analysis: {
        ...report.gap_analysis,
        certification_needs: items,
      },
    });
  };

  const handleEditGap = (category: string, index: number) => {
    const items = report.gap_analysis[category as keyof typeof report.gap_analysis] as Gap[];
    setEditingGap({ category, index, gap: { ...items[index] } });
  };

  const handleDeleteGap = (category: string, index: number) => {
    setDeleteTarget({ category, index });
  };

  const handleEditSave = (gap: Gap) => {
    if (!editingGap) return;
    const category = editingGap.category;
    const items = [...(report.gap_analysis[category as keyof typeof report.gap_analysis] as Gap[])];
    items[editingGap.index] = gap;
    handleGapsChange(category, items);
    setEditingGap(null);
  };

  const handleAddSave = (gap: Gap) => {
    if (!addingCategory) return;
    const items = [...(report.gap_analysis[addingCategory as keyof typeof report.gap_analysis] as Gap[])];
    items.push(gap);
    handleGapsChange(addingCategory, items);
    setAddingCategory(null);
  };

  const handleDeleteConfirm = () => {
    if (!deleteTarget) return;
    const items = [...(report.gap_analysis[deleteTarget.category as keyof typeof report.gap_analysis] as Gap[])];
    items.splice(deleteTarget.index, 1);
    handleGapsChange(deleteTarget.category, items);
    setDeleteTarget(null);
  };

  const renderGapCard = (gap: Gap, index: number, category: string) => (
    <GapCard
      gap={gap}
      onEdit={isEditing ? () => handleEditGap(category, index) : undefined}
      onDelete={isEditing ? () => handleDeleteGap(category, index) : undefined}
      showActions={isEditing}
    />
  );

  return (
    <ReportCard
      id="gap-analysis"
      title="差距分析"
      icon="analytics"
      isEditing={isEditing}
      onEdit={onEdit}
      onSave={onSave}
      onCancel={onCancel}
      onAIPolishModule={onAIPolishModule}
      isPolishing={isPolishing}
      saveStatus={saveStatus}
    >
      {/* 硬技能差距 */}
      {hard_skills_gaps && hard_skills_gaps.length > 0 && (
        <>
          <h4 className="!mb-3 border-b border-[#E8F4F8] !pb-2 text-[18px] !font-bold  text-[#333]">
            硬技能差距
          </h4>
          <div className="w-full !p-4">
            {hard_skills_gaps.map((gap, index) => renderGapCard(gap, index, 'hard_skills_gaps'))}
          </div>
        </>
      )}
      {isEditing && (
        <div className="!mt-2 text-center">
          <button
            className="inline-flex items-center !gap-1 rounded-lg bg-[#1677ff] !px-4 !py-2 text-[16px] font-medium text-white transition-transform hover:scale-105"
            onClick={() => setAddingCategory('hard_skills_gaps')}
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            添加硬技能差距
          </button>
        </div>
      )}

      {/* 软技能差距 */}
      {soft_skills_gaps && soft_skills_gaps.length > 0 && (
        <>
          <h4 className="!mb-3 border-b border-[#E8F4F8] !pb-2 text-[18px] !font-bold  text-[#333]">
            软技能差距
          </h4>
          <div className="w-full !p-3">
            {soft_skills_gaps.map((gap, index) => renderGapCard(gap, index, 'soft_skills_gaps'))}
          </div>
        </>
      )}
      {isEditing && (
        <div className="!mt-2 text-center">
          <button
            className="inline-flex items-center !gap-1 rounded-lg bg-[#1677ff] !px-4 !py-2 text-[16px] font-medium text-white transition-transform hover:scale-105"
            onClick={() => setAddingCategory('soft_skills_gaps')}
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            添加软技能差距
          </button>
        </div>
      )}

      {/* 经验差距 */}
      {experience_gaps && experience_gaps.length > 0 && (
        <>
          <h4 className="!mb-3 border-b border-[#E8F4F8] !pb-2 text-[18px] !font-bold text-[#333]">
            经验差距
          </h4>
          <div className="w-full !p-3">
            {experience_gaps.map((gap, index) => renderGapCard(gap, index, 'experience_gaps'))}
          </div>
        </>
      )}
      {isEditing && (
        <div className="!mt-2 text-center">
          <button
            className="inline-flex items-center !gap-1 rounded-lg bg-[#1677ff] !px-4 !py-2 text-[16px] font-medium text-white transition-transform hover:scale-105"
            onClick={() => setAddingCategory('experience_gaps')}
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            添加经验差距
          </button>
        </div>
      )}

      {/* 证书需求 */}
      {certification_needs && certification_needs.length > 0 && (
        <div>
          <h4 className="!mb-3 border-b border-[#E8F4F8] !pb-2 text-[18px] !font-bold  text-[#333]">
            证书需求
          </h4>
          {isEditing ? (
            <EditableList
              items={certification_needs}
              onChange={handleCertChange}
              label=""
              addLabel="添加证书"
              disabled={isPolishing}
            />
          ) : (
            <ul className="list-none space-y-3 !p-3">
              {certification_needs.map((cert, index) => (
                <li key={index} className="relative !p-3 text-[16px] font-medium text-[#333] before:absolute before:left-0 before:text-[#1677ff] before:content-['-']">
                  {cert}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Gap 编辑弹窗 */}
      {editingGap && (
        <GapEditModal
          isOpen={true}
          title="编辑差距"
          initialValues={editingGap.gap}
          onSave={handleEditSave}
          onCancel={() => setEditingGap(null)}
        />
      )}

      {/* Gap 添加弹窗 */}
      {addingCategory && (
        <GapEditModal
          isOpen={true}
          title={
            addingCategory === 'hard_skills_gaps' ? '添加硬技能差距' :
            addingCategory === 'soft_skills_gaps' ? '添加软技能差距' : '添加经验差距'
          }
          initialValues={{
            skill: '',
            importance: '中',
            current_level: addingCategory === 'experience_gaps' ? '无' : '无',
            target_level: addingCategory === 'experience_gaps' ? '具备' : '掌握',
            learning_resources: [],
          }}
          onSave={handleAddSave}
          onCancel={() => setAddingCategory(null)}
        />
      )}

      {/* 删除确认 */}
      {deleteTarget && (
        <ConfirmDialog
          title="确认删除"
          message="确认删除该项吗？"
          confirmText="删除"
          cancelText="取消"
          onConfirm={handleDeleteConfirm}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </ReportCard>
  );
}