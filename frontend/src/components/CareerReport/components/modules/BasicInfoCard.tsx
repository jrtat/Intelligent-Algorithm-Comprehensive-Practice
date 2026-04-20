import { ReportCard } from '../ReportCard';
import { useReport } from '../../context/ReportContext';
import { EditableField } from '../ui/EditableField';

interface BasicInfoCardProps {
  isEditing?: boolean;
  onEdit?: () => void;
  onSave?: () => void;
  onCancel?: () => void;
  onAIPolish?: () => void;
  saveStatus?: 'idle' | 'saving' | 'saved' | 'error';
}

export function BasicInfoCard({
  isEditing = false,
  onEdit,
  onSave,
  onCancel,
  onAIPolish,
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
      onAIPolish={onAIPolish}
      saveStatus={saveStatus}
    >
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div
          style={{
            backgroundColor: '#F5F7FA',
            padding: '16px 20px',
            borderRadius: 8,
          }}
        >
          <div style={{ fontSize: 13, color: '#999', marginBottom: 4 }}>候选人姓名</div>
          {isEditing ? (
            <EditableField
              value={report.candidate_name}
              onChange={(val) => handleFieldChange('candidate_name', val)}
              placeholder="请输入候选人姓名"
              maxLength={50}
            />
          ) : (
            <div style={{ fontSize: 16, fontWeight: 500, color: '#333' }}>
              {report.candidate_name}
            </div>
          )}
        </div>

        <div
          style={{
            backgroundColor: '#F5F7FA',
            padding: '16px 20px',
            borderRadius: 8,
          }}
        >
          <div style={{ fontSize: 13, color: '#999', marginBottom: 4 }}>目标岗位</div>
          {isEditing ? (
            <EditableField
              value={report.target_job}
              onChange={(val) => handleFieldChange('target_job', val)}
              placeholder="请输入目标岗位"
              maxLength={100}
            />
          ) : (
            <div style={{ fontSize: 16, fontWeight: 500, color: '#333' }}>
              {report.target_job}
            </div>
          )}
        </div>
      </div>
    </ReportCard>
  );
}
