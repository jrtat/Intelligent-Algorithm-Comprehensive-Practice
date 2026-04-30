import { useState } from 'react';
import { ReportCard } from '../ReportCard';
import { CollapsiblePanel } from '../ui/CollapsiblePanel';
import { EditableList } from '../ui/EditableList';
import { EditableField } from '../ui/EditableField';
import { useReport } from '../../context/ReportContext';

interface ActionPlanCardProps {
  isEditing?: boolean;
  onEdit?: () => void;
  onSave?: () => void;
  onCancel?: () => void;
  onAIPolishModule?: (moduleId: string) => void;
  onAIPolishField?: (fieldPath: string) => void;
  isPolishing?: boolean;
  saveStatus?: 'idle' | 'saving' | 'saved' | 'error';
}

export function ActionPlanCard({
  isEditing = false,
  onEdit,
  onSave,
  onCancel,
  onAIPolishModule,
  onAIPolishField,
  isPolishing = false,
  saveStatus = 'idle',
}: ActionPlanCardProps) {
  const { state, updateReport } = useReport();
  const { report } = state;

  const [editingSection, setEditingSection] = useState<string | null>(null);

  if (!report?.action_plan) return null;

  const { short_term_plan, mid_term_plan, evaluation_framework } = report.action_plan;

  const handleFieldChange = (section: string, subsection: string, field: string, value: any) => {
    updateReport({
      action_plan: {
        ...report.action_plan,
        [section]: {
          ...(report.action_plan as any)[section],
          [subsection]: {
            ...(report.action_plan as any)[section]?.[subsection],
            [field]: value,
          },
        },
      },
    });
  };

  const handleTopLevelFieldChange = (section: string, field: string, value: any) => {
    updateReport({
      action_plan: {
        ...report.action_plan,
        [section]: {
          ...(report.action_plan as any)[section],
          [field]: value,
        },
      },
    });
  };

  return (
    <ReportCard
      id="action-plan"
      title="行动计划"
      icon="checklist"
      isEditing={isEditing}
      onEdit={onEdit}
      onSave={onSave}
      onCancel={onCancel}
      onAIPolishModule={onAIPolishModule}
      isPolishing={isPolishing}
      saveStatus={saveStatus}
    >
      {/* 短期计划 */}
      {short_term_plan && (
        <CollapsiblePanel
          title="短期计划"
          subtitle={`（${short_term_plan.duration || ''}）`}
          onEdit={isEditing ? () => setEditingSection('short_term') : undefined}
          onAIPolish={() => onAIPolishField?.('action_plan.short_term_plan')}
        >
          {isEditing && editingSection === 'short_term' ? (
            <div>
              <div className="mb-3">
                <EditableField
                  value={short_term_plan.duration || ''}
                  onChange={(val) => handleTopLevelFieldChange('short_term_plan', 'duration', val)}
                  onSave={onSave}
                  label="计划时长"
                  placeholder="如：1-6个月"
                />
              </div>
              {short_term_plan.learning_path && (
                <div className="mb-4">
                  <h5 className="mb-2 text-[16px] font-medium text-[#666]">学习路径</h5>
                  <EditableList
                    items={short_term_plan.learning_path.courses || []}
                    onChange={(items) => handleFieldChange('short_term_plan', 'learning_path', 'courses', items)}
                    onAIPolishItem={(i) => onAIPolishField?.(`action_plan.short_term_plan.learning_path.courses[${i}]`)}
                    label="课程"
                    addLabel="添加课程"
                    disabled={isPolishing}
                  />
                </div>
              )}
              {short_term_plan.certifications && (
                <div className="mb-4">
                  <EditableList
                    items={short_term_plan.certifications}
                    onChange={(items) => handleTopLevelFieldChange('short_term_plan', 'certifications', items)}
                    onAIPolishItem={(i) => onAIPolishField?.(`action_plan.short_term_plan.certifications[${i}]`)}
                    label="获取证书"
                    addLabel="添加证书"
                    disabled={isPolishing}
                  />
                </div>
              )}
              <button
                className="mt-3 rounded-lg bg-[#1677ff] !px-3 !py-1.5 text-[13px] font-medium text-white transition-all hover:scale-105"
                onClick={() => setEditingSection(null)}
              >
                完成编辑
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {short_term_plan.learning_path && (
                <div>
                  <h5 className="mb-2 text-[16px] font-medium text-[#666]">学习路径</h5>
                  <div className="text-[15px] text-[#333]">
                    <p><strong>课程：</strong>{short_term_plan.learning_path.courses?.join('、')}</p>
                    <p><strong>书籍：</strong>{short_term_plan.learning_path.books?.join('、')}</p>
                  </div>
                </div>
              )}
              {short_term_plan.certifications && short_term_plan.certifications.length > 0 && (
                <div>
                  <h5 className="mb-2 text-[16px] font-medium text-[#666]">获取证书</h5>
                  <ul className="list-none space-y-2 pl-0">
                    {short_term_plan.certifications.map((cert, i) => (
                      <li key={i} className="relative !pl-5 text-[#333] before:absolute before:left-0 before:top-2 before:h-1.5 before:w-1.5 before:rounded-full before:bg-[#1677ff]">
                        {cert}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {short_term_plan.quantifiable_goals && short_term_plan.quantifiable_goals.length > 0 && (
                <div>
                  <h5 className="mb-2 text-[16px] font-medium text-[#666]">量化目标</h5>
                  {short_term_plan.quantifiable_goals.map((goal, i) => (
                    <div key={i} className="mb-2 rounded-md bg-[#F5F7FA] p-2 text-[15px]">
                      <strong>{goal.metric}:</strong> {goal.target_value}
                      <div className="mt-1 text-[12px] text-[#999]">衡量方式: {goal.measurement_method}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </CollapsiblePanel>
      )}

      {/* 中期计划 */}
      {mid_term_plan && (
        <CollapsiblePanel
          title="中期计划"
          subtitle={`（${mid_term_plan.duration || ''}）`}
          onEdit={isEditing ? () => setEditingSection('mid_term') : undefined}
          onAIPolish={() => onAIPolishField?.('action_plan.mid_term_plan')}
        >
          {isEditing && editingSection === 'mid_term' ? (
            <div>
              <div className="mb-3">
                <EditableField
                  value={mid_term_plan.duration || ''}
                  onChange={(val) => handleTopLevelFieldChange('mid_term_plan', 'duration', val)}
                  onSave={onSave}
                  label="计划时长"
                  placeholder="如：6-12个月"
                />
              </div>
              <button
                className="mt-3 rounded-lg bg-[#1677ff] px-3 py-1.5 text-[13px] font-medium text-white transition-all hover:scale-105"
                onClick={() => setEditingSection(null)}
              >
                完成编辑
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {mid_term_plan.advanced_learning && (
                <div>
                  <h5 className="mb-2 text-[16px] font-medium text-[#666]">进阶学习</h5>
                  <div className="text-[15px] text-[#333]">
                    <p><strong>高级课程：</strong>{mid_term_plan.advanced_learning.advanced_courses?.join('、')}</p>
                    <p><strong>专业培训：</strong>{mid_term_plan.advanced_learning.professional_training?.join('、')}</p>
                  </div>
                </div>
              )}
              {mid_term_plan.industry_engagement && (
                <div>
                  <h5 className="mb-2 text-[16px] font-medium text-[#666]">行业参与</h5>
                  <div className="text-[15px] text-[#333]">
                    <p><strong>会议：</strong>{mid_term_plan.industry_engagement.conferences?.join('、')}</p>
                    <p><strong>技术沙龙：</strong>{mid_term_plan.industry_engagement.tech_meetups?.join('、')}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </CollapsiblePanel>
      )}

      {/* 评估框架 */}
      {evaluation_framework && (
        <CollapsiblePanel
          title="评估框架"
          onEdit={isEditing ? () => setEditingSection('evaluation') : undefined}
          onAIPolish={() => onAIPolishField?.('action_plan.evaluation_framework')}
        >
          {isEditing && editingSection === 'evaluation' ? (
            <div>
              <div className="mb-3">
                <EditableField
                  value={evaluation_framework.evaluation_cycles?.self_assessment || ''}
                  onChange={(val) =>
                    handleTopLevelFieldChange('evaluation_framework', 'evaluation_cycles', {
                      ...evaluation_framework.evaluation_cycles,
                      self_assessment: val,
                    })
                  }
                  onSave={onSave}
                  label="自评周期"
                  multiline
                  placeholder="请输入自评周期说明"
                />
              </div>
              <button
                className="mt-3 rounded-lg bg-[#1677ff] px-3 py-1.5 text-[13px] font-medium text-white transition-all hover:scale-105"
                onClick={() => setEditingSection(null)}
              >
                完成编辑
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {evaluation_framework.evaluation_cycles && (
                <div>
                  <h5 className="mb-2 text-[16px] font-medium text-[#666]">评估周期</h5>
                  <div className="text-[15px] text-[#333]">
                    <p><strong>自评：</strong>{evaluation_framework.evaluation_cycles.self_assessment}</p>
                    <p><strong>深度复盘：</strong>{evaluation_framework.evaluation_cycles.deep_review}</p>
                    <p><strong>年度总结：</strong>{evaluation_framework.evaluation_cycles.annual_review}</p>
                  </div>
                </div>
              )}
              {evaluation_framework.quantitative_metrics && evaluation_framework.quantitative_metrics.length > 0 && (
                <div>
                  <h5 className="mb-2 text-[16px] font-medium text-[#666]">量化指标</h5>
                  {evaluation_framework.quantitative_metrics.map((metric, i) => (
                    <div key={i} className="mb-2 rounded-md bg-[#F5F7FA] p-2 text-[15px]">
                      <strong>{metric.metric_name}:</strong>
                      <div className="mt-1 text-[#666]">
                        {'scale' in metric && metric.scale && <span>范围: {metric.scale}</span>}
                        {'unit' in metric && metric.unit && <span>单位: {metric.unit}</span>}
                        {' | '}
                        <span style={{ color: '#1677ff' }}>目标: {metric.target_progression}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {evaluation_framework.risk_warning && (
                <div>
                  <h5 className="mb-2 text-[16px] font-medium text-[#666]">风险预警</h5>
                  <div className="text-[15px] text-[#333]">
                    <p><strong>潜在障碍：</strong>{evaluation_framework.risk_warning.potential_obstacles?.join('、')}</p>
                    <p><strong>预警信号：</strong>{evaluation_framework.risk_warning.early_warning_signs?.join('、')}</p>
                    <p><strong>应对方案：</strong>{evaluation_framework.risk_warning.contingency_plans?.join('、')}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </CollapsiblePanel>
      )}
    </ReportCard>
  );
}