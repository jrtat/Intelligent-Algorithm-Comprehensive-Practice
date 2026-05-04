import { ReportCard } from '../ReportCard.tsx';
import { useReport } from '../../context/ReportContext.tsx';
import { EditableField } from '../ui/EditableField.tsx';

interface BasicInfoCardProps {
  isEditing?: boolean;
  onEdit?: () => void;
  onSave?: () => void;
  onCancel?: () => void;
  onAIPolishModule?: (moduleId: string) => void;
  onAIPolishField?: (fieldPath: string) => void;
  isPolishing?: boolean;
  saveStatus?: 'idle' | 'saving' | 'saved' | 'error';
}

export function BasicInfoCard({
  isEditing = false,
  onEdit,
  onSave,
  onCancel,
  onAIPolishModule,
  isPolishing = false,
  saveStatus = 'idle',
}: BasicInfoCardProps) {
  const { state, updateReport } = useReport();
  const { report } = state;

  if (!report) return null;

  const handleFieldChange = (field: string, value: string) => {
    updateReport({ [field]: value });
  };

  return (
    <ReportCard
      id="basic-info"
      title="基础信息"
      icon="person"
      isEditing={isEditing}
      onEdit={onEdit}
      onSave={onSave}
      onCancel={onCancel}
      onAIPolishModule={onAIPolishModule}
      isPolishing={isPolishing}
      saveStatus={saveStatus}
    >
      <div className="grid grid-cols-2 !gap-32 !p-4">
        <div className="rounded-lg bg-[#F5F7FA] !p-4">
          <div className="mb-1 !text-[16px] text-[#999]">候选人姓名</div>
          {isEditing ? (
            <EditableField
              value={report.candidate_name}
              onChange={(val) => handleFieldChange('candidate_name', val)}
              placeholder="请输入候选人姓名"
              maxLength={50}
            />
          ) : (
            <div className="text-[16px] font-medium text-[#333]">
              {report.candidate_name}
            </div>
          )}
        </div>

        <div className="rounded-lg bg-[#F5F7FA] !p-4">
          <div className="mb-1 !text-[16px] text-[#999]">目标岗位</div>
          {isEditing ? (
            <EditableField
              value={report.target_job}
              onChange={(val) => handleFieldChange('target_job', val)}
              placeholder="请输入目标岗位"
              maxLength={100}
            />
          ) : (
            <div className="text-![16px] font-medium text-[#333]">
              {report.target_job}
            </div>
          )}
        </div>
      </div>
    </ReportCard>
  );
}