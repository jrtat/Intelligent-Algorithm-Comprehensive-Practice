import { ReportCard } from '../ReportCard';
import { ScoreBar } from '../ui/ScoreBar';
import { EditableField } from '../ui/EditableField';
import { useReport } from '../../context/ReportContext';

interface MatchAnalysisCardProps {
  isEditing?: boolean;
  onEdit?: () => void;
  onSave?: () => void;
  onCancel?: () => void;
  onAIPolishModule?: (moduleId: string) => void;
  onAIPolishField?: (fieldPath: string) => void;
  isPolishing?: boolean;
  saveStatus?: 'idle' | 'saving' | 'saved' | 'error';
}

export function MatchAnalysisCard({
  isEditing = false,
  onEdit,
  onSave,
  onCancel,
  onAIPolishModule,
  onAIPolishField,
  isPolishing = false,
  saveStatus = 'idle',
}: MatchAnalysisCardProps) {
  const { state, updateReport } = useReport();
  const { report } = state;

  if (!report?.match_analysis) return null;

  const { skill_match_score, experience_match_score, education_fit, overall_match_score, match_level } = report.match_analysis;

  const getMatchLevelColor = (level: string) => {
    switch (level) {
      case '高':
        return '#059669';
      case '中':
        return '#D97706';
      case '低':
        return '#DC2626';
      default:
        return '#2E86AB';
    }
  };

  const handleFieldChange = (field: string, value: any) => {
    updateReport({
      match_analysis: {
        ...report.match_analysis,
        [field]: value,
      },
    });
  };

  return (
    <ReportCard
      id="match-analysis"
      title="匹配分析"
      icon="trending_up"
      isEditing={isEditing}
      onEdit={onEdit}
      onSave={onSave}
      onCancel={onCancel}
      onAIPolishModule={onAIPolishModule}
      isPolishing={isPolishing}
      saveStatus={saveStatus}
    >
      {/* 评分区域 */}
      <div style={{ marginBottom: 20 }}>
        <ScoreBar label="技能匹配" score={skill_match_score} />
        <ScoreBar label="经验匹配" score={experience_match_score} />
        <ScoreBar label="综合评分" score={overall_match_score} />
      </div>

      {/* 综合等级 */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          marginBottom: 20,
          padding: '12px 16px',
          backgroundColor: '#F5F7FA',
          borderRadius: 8,
        }}
      >
        <span style={{ fontSize: 14, color: '#666' }}>匹配等级：</span>
        <span
          style={{
            display: 'inline-block',
            padding: '4px 16px',
            backgroundColor: getMatchLevelColor(match_level),
            color: 'white',
            borderRadius: 12,
            fontWeight: 500,
            fontSize: 14,
          }}
        >
          {match_level}
        </span>
        <span style={{ fontSize: 20, fontWeight: 'bold', color: '#2E86AB' }}>
          {overall_match_score}
        </span>
        <span style={{ fontSize: 13, color: '#999' }}>分</span>
      </div>

      {/* 学历匹配说明 */}
      <div>
        <h4 style={{ fontSize: 14, color: '#666', marginBottom: 8, fontWeight: 500 }}>
          学历适配说明
        </h4>
        {isEditing ? (
          <EditableField
            value={education_fit}
            onChange={(val) => handleFieldChange('education_fit', val)}
            onSave={onSave}
            onAIPolish={() => onAIPolishField?.('match_analysis.education_fit')}
            multiline
            placeholder="请输入学历适配说明"
            maxLength={500}
            showCharCount
          />
        ) : (
          <p style={{ lineHeight: 1.6, color: '#333' }}>{education_fit}</p>
        )}
      </div>
    </ReportCard>
  );
}