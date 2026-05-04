import { ReportCard } from '../ReportCard.tsx';
import { EditableField } from '../ui/EditableField.tsx';
import { useReport } from '../../context/ReportContext.tsx';

interface FinalRecommendationCardProps {
  isEditing?: boolean;
  onEdit?: () => void;
  onSave?: () => void;
  onCancel?: () => void;
  onAIPolishModule?: (moduleId: string) => void;
  onAIPolishField?: (fieldPath: string) => void;
  isPolishing?: boolean;
  saveStatus?: 'idle' | 'saving' | 'saved' | 'error';
}

export function FinalRecommendationCard({
  isEditing = false,
  onEdit,
  onSave,
  onCancel,
  onAIPolishModule,
  onAIPolishField,
  isPolishing = false,
  saveStatus = 'idle',
}: FinalRecommendationCardProps) {
  const { state, updateReport } = useReport();
  const { report } = state;

  if (!report?.final_recommendation) return null;

  const handleChange = (value: string) => {
    updateReport({ final_recommendation: value });
  };

  return (
    <ReportCard
      id="final-recommendation"
      title="最终建议"
      icon="lightbulb"
      isEditing={isEditing}
      onEdit={onEdit}
      onSave={onSave}
      onCancel={onCancel}
      onAIPolishModule={onAIPolishModule}
      isPolishing={isPolishing}
      saveStatus={saveStatus}
    >
      <div className="rounded-r-lg border-l-4 !p-2" style={{ backgroundColor: 'rgba(22, 119, 255, 0.1)', borderLeftColor: '#1677ff' }}>
        {isEditing ? (
          
          <EditableField
            value={report.final_recommendation}
            onChange={handleChange}
            onSave={onSave}
            onAIPolish={() => onAIPolishField?.('final_recommendation')}
            multiline
            placeholder="请输入最终建议"
            maxLength={2000}
            showCharCount
          />
        ) : (
          <p className="leading-relaxed !p-3 text-[#333]">{report.final_recommendation}</p>
        )}
      </div>
    </ReportCard>
  );
}