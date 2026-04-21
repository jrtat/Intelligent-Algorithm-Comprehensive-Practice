import { ReportCard } from '../ReportCard';
import { GapCard } from '../ui/GapCard';
import { EditableObjectArray } from '../ui/EditableObjectArray';
import type { FormField } from '../ui/EditModal';
import { useReport } from '../../context/ReportContext';
import type { Gap } from '../../../../types/job';

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

const gapFields: FormField[] = [
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
  {
    key: 'learning_resources',
    label: '学习资源',
    type: 'textarea',
    placeholder: '请输入学习资源（每行一个）',
    maxLength: 500,
  },
];

function renderGapCard(gap: Gap, _index: number, onEdit?: () => void, onDelete?: () => void, onAIPolish?: () => void) {
  return (
    <GapCard
      gap={gap}
      onEdit={onEdit}
      onDelete={onDelete}
      onAIPolish={onAIPolish}
      showActions={true}
    />
  );
}

export function GapAnalysisCard({
  isEditing = false,
  onEdit,
  onSave,
  onCancel,
  onAIPolishModule,
  isPolishing = false,
  saveStatus = 'idle',
}: GapAnalysisCardProps) {
  const { state, updateReport } = useReport();
  const { report } = state;

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
        <div style={{ marginBottom: 24 }}>
          <h4
            style={{
              fontSize: 14,
              fontWeight: 500,
              color: '#333',
              marginBottom: 12,
              paddingBottom: 8,
              borderBottom: '1px solid #E8F4F8',
            }}
          >
            硬技能差距
          </h4>
          {isEditing ? (
            <EditableObjectArray
              items={hard_skills_gaps}
              onChange={(items) => handleGapsChange('hard_skills_gaps', items as Gap[])}
              fields={gapFields}
              renderItem={(item, index) => renderGapCard(item as Gap, index)}
              addLabel="添加硬技能差距"
              addInitialValues={{ skill: '', importance: '中', current_level: '无', target_level: '掌握', learning_resources: [] }}
            />
          ) : (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: 12,
              }}
            >
              {hard_skills_gaps.map((gap, index) => (
                <GapCard key={index} gap={gap} showActions={false} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* 软技能差距 */}
      {soft_skills_gaps && soft_skills_gaps.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <h4
            style={{
              fontSize: 14,
              fontWeight: 500,
              color: '#333',
              marginBottom: 12,
              paddingBottom: 8,
              borderBottom: '1px solid #E8F4F8',
            }}
          >
            软技能差距
          </h4>
          {isEditing ? (
            <EditableObjectArray
              items={soft_skills_gaps}
              onChange={(items) => handleGapsChange('soft_skills_gaps', items as Gap[])}
              fields={gapFields}
              renderItem={(item, index) => renderGapCard(item as Gap, index)}
              addLabel="添加软技能差距"
              addInitialValues={{ skill: '', importance: '中', current_level: '基础', target_level: '熟练', learning_resources: [] }}
            />
          ) : (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: 12,
              }}
            >
              {soft_skills_gaps.map((gap, index) => (
                <GapCard key={index} gap={gap} showActions={false} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* 经验差距 */}
      {experience_gaps && experience_gaps.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <h4
            style={{
              fontSize: 14,
              fontWeight: 500,
              color: '#333',
              marginBottom: 12,
              paddingBottom: 8,
              borderBottom: '1px solid #E8F4F8',
            }}
          >
            经验差距
          </h4>
          {isEditing ? (
            <EditableObjectArray
              items={experience_gaps}
              onChange={(items) => handleGapsChange('experience_gaps', items as Gap[])}
              fields={gapFields}
              renderItem={(item, index) => renderGapCard(item as Gap, index)}
              addLabel="添加经验差距"
              addInitialValues={{ skill: '', importance: '中', current_level: '无', target_level: '具备', learning_resources: [] }}
            />
          ) : (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: 12,
              }}
            >
              {experience_gaps.map((gap, index) => (
                <GapCard key={index} gap={gap} showActions={false} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* 证书需求 */}
      {certification_needs && certification_needs.length > 0 && (
        <div>
          <h4
            style={{
              fontSize: 14,
              fontWeight: 500,
              color: '#333',
              marginBottom: 12,
              paddingBottom: 8,
              borderBottom: '1px solid #E8F4F8',
            }}
          >
            证书需求
          </h4>
          <ul className="list-with-bullets">
            {certification_needs.map((cert, index) => (
              <li key={index}>{cert}</li>
            ))}
          </ul>
        </div>
      )}
    </ReportCard>
  );
}