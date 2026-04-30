import { ReportCard } from '../ReportCard';
import { useReport } from '../../context/ReportContext';
import { EditableField } from '../ui/EditableField';
import { EditableList } from '../ui/EditableList';

interface CandidateSummaryCardProps {
  isEditing?: boolean;
  onEdit?: () => void;
  onSave?: () => void;
  onCancel?: () => void;
  onAIPolishModule?: (moduleId: string) => void;
  onAIPolishField?: (fieldPath: string) => void;
  isPolishing?: boolean;
  saveStatus?: 'idle' | 'saving' | 'saved' | 'error';
}

export function CandidateSummaryCard({
  isEditing = false,
  onEdit,
  onSave,
  onCancel,
  onAIPolishModule,
  onAIPolishField,
  isPolishing = false,
  saveStatus = 'idle',
}: CandidateSummaryCardProps) {
  const { state, updateNestedField } = useReport();
  const { report } = state;

  if (!report?.candidate_summary) return null;

  const { current_background, core_strengths, areas_for_improvement } = report.candidate_summary;

  const handleFieldChange = (field: string, value: string | string[]) => {
    updateNestedField(['candidate_summary', field], value);
  };

  return (
    <ReportCard
      id="candidate-summary"
      title="候选人总结"
      icon="summarize"
      isEditing={isEditing}
      onEdit={onEdit}
      onSave={onSave}
      onCancel={onCancel}
      onAIPolishModule={onAIPolishModule}
      isPolishing={isPolishing}
      saveStatus={saveStatus}
    >
      {/* 统一的内边距与区块间距 */}
      <div className="!p-4 sm:!p-6 space-y-6">
        {/* 当前背景 */}
        <div>
          <h4 className="!mb-3 border-b border-[#E8F4F8] !pb-2 text-[18px] !font-bold  text-[#333]">当前背景</h4>
          {isEditing ? (
            <EditableField
              value={current_background}
              onChange={(val) => handleFieldChange('current_background', val)}
              onSave={onSave}
              onAIPolish={() => onAIPolishField?.('candidate_summary.current_background')}
              multiline
              placeholder="请输入当前背景"
              maxLength={2000}
              showCharCount
            />
          ) : (
            <p className="cursor-text rounded-lg bg-gray-50 !p-4 leading-relaxed text-gray-800">
              {current_background}
            </p>
          )}
        </div>

        {/* 核心优势 */}
        <div>
          <h4 className="!mb-3 border-b border-[#E8F4F8] !pb-2 text-[18px] !font-bold  text-[#333]">核心优势</h4>
          <EditableList
            items={core_strengths}
            onChange={(items) => handleFieldChange('core_strengths', items)}
            onAIPolishItem={(index) =>
              onAIPolishField?.(`candidate_summary.core_strengths[${index}]`)
            }
            addLabel="添加优势"
            disabled={isPolishing || !isEditing}
          />
        </div>

        {/* 待提升领域 */}
        <div>
          <h4 className="!mb-3 border-b border-[#E8F4F8] !pb-2 text-[18px] !font-bold  text-[#333]">待提升领域</h4>
          <EditableList
            items={areas_for_improvement}
            onChange={(items) => handleFieldChange('areas_for_improvement', items)}
            onAIPolishItem={(index) =>
              onAIPolishField?.(`candidate_summary.areas_for_improvement[${index}]`)
            }
            addLabel="添加领域"
            disabled={isPolishing || !isEditing}
          />
        </div>
      </div>
    </ReportCard>
  );
}