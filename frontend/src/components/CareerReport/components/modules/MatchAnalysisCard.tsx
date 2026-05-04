import { ReportCard } from '../ReportCard.tsx';
import { ScoreBar } from '../ui/ScoreBar.tsx';
import { EditableField } from '../ui/EditableField.tsx';
import { useReport } from '../../context/ReportContext.tsx';

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
        return '#1677ff';
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
      <div className="!mb-5">
        <ScoreBar label="技能匹配" score={skill_match_score} />
        <ScoreBar label="经验匹配" score={experience_match_score} />
        <ScoreBar label="综合评分" score={overall_match_score} />
      </div>

      {/* 综合等级 */}
      <div className="!mb-5 flex items-center !gap-3 rounded-lg bg-[#F5F7FA] !p-3">
        <span className="text-[16px] text-[#666]">匹配等级：</span>
        <span
          className="inline-block rounded-full !px-4 !py-1 text-[16px] font-medium text-white"
          style={{ backgroundColor: getMatchLevelColor(match_level) }}
        >
          {match_level}
        </span>
        <span className="text-[20px] font-bold" style={{ color: '#1677ff' }}>
          {overall_match_score}
        </span>
        <span className="text-[16px] text-[#999]">分</span>
      </div>

      {/* 学历适配说明 */}
      <div>
        <h4 className="!mb-2 text-[16px] font-medium text-[#666]">
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
          <p className="leading-relaxed text-[#333]">{education_fit}</p>
        )}
      </div>
    </ReportCard>
  );
}