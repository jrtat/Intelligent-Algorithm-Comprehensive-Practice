import { ReportCard } from '../ReportCard';
import { EditableField } from '../ui/EditableField';
import { useReport } from '../../context/ReportContext';

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
      <div className="final-recommendation">
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
          <p>{report.final_recommendation}</p>
        )}
      </div>
    </ReportCard>
  );
}