import type { Gap } from '../../../../types/job';

interface GapCardProps {
  gap: Gap;
  onEdit?: () => void;
  onDelete?: () => void;
  onAIPolish?: () => void;
  showActions?: boolean;
}

export function GapCard({
  gap,
  onEdit,
  onDelete,
  onAIPolish,
  showActions = true,
}: GapCardProps) {
  const importanceClass = gap.importance === '高' ? 'high' : gap.importance === '低' ? 'low' : 'medium';

  return (
    <div className="group relative mb-3 w-full rounded-lg bg-[#F5F7FA] !p-4">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-[16px] font-bold text-[#333]">{gap.skill}</span>
        <span className={`rounded !px-2 !py-0.5 text-[16px] font-medium ${importanceClass === 'high' ? 'bg-red-100 text-red-600' : importanceClass === 'low' ? 'bg-blue-100 text-blue-600' : 'bg-amber-100 text-amber-600'}`}>
          {gap.importance}
        </span>
      </div>

      <div className="mb-2 flex gap-134 text-[16px] text-[#666] justify-start">
        <strong>当前水平：{gap.current_level}</strong>
        <strong>目标水平：{gap.target_level}</strong>
      </div>

      {Array.isArray(gap.learning_resources) && gap.learning_resources.length > 0 && (
        <ul className="list-none !pl-0 text-[16px] text-[#999]">
          {gap.learning_resources.map((resource, index) => (
            <li key={index} className="relative !pl-4 before:absolute before:left-0 before:text-[#1677ff] before:content-['→']">
              {resource}
            </li>
          ))}
        </ul>
      )}

      {/* Action buttons */}
      {showActions && (onEdit || onDelete || onAIPolish) && (
        <div className="absolute right-2 top-2 flex !gap-4 opacity-0 transition-opacity group-hover:opacity-100">
          {onAIPolish && (
            <button
              className="flex h-7 w-7 items-center justify-center rounded-md bg-white shadow-sm hover:bg-[#FF9F43]/10"
              onClick={onAIPolish}
              title="AI润色"
            >
              <span className="material-symbols-outlined text-[14px]" style={{ color: '#FF9F43' }}>
                auto_fix_high
              </span>
            </button>
          )}
          {onEdit && (
            <button
              className="flex h-7 w-7 items-center justify-center rounded-md bg-white shadow-sm hover:bg-[#1677ff]/10"
              onClick={onEdit}
              title="编辑"
            >
              <span className="material-symbols-outlined text-[14px]" style={{ color: '#666' }}>
                edit
              </span>
            </button>
          )}
          {onDelete && (
            <button
              className="flex h-7 w-7 items-center justify-center rounded-md bg-white shadow-sm hover:bg-red-50"
              onClick={onDelete}
              title="删除"
            >
              <span className="material-symbols-outlined text-[14px]" style={{ color: '#DC2626' }}>
                delete
              </span>
            </button>
          )}
        </div>
      )}
    </div>
  );
}