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
  onAIPolish?: () => void;
  saveStatus?: 'idle' | 'saving' | 'saved' | 'error';
}

export function ActionPlanCard({
  isEditing = false,
  onEdit,
  onSave,
  onCancel,
  onAIPolish,
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
      onAIPolish={onAIPolish}
      saveStatus={saveStatus}
    >
      {/* 短期计划 */}
      {short_term_plan && (
        <CollapsiblePanel
          title="短期计划"
          subtitle={`（${short_term_plan.duration || ''}）`}
          onEdit={isEditing ? () => setEditingSection('short_term') : undefined}
          onAIPolish={onAIPolish}
        >
          {isEditing && editingSection === 'short_term' ? (
            <div>
              <div style={{ marginBottom: 12 }}>
                <EditableField
                  value={short_term_plan.duration || ''}
                  onChange={(val) => handleTopLevelFieldChange('short_term_plan', 'duration', val)}
                  label="计划时长"
                  placeholder="如：1-6个月"
                />
              </div>

              {short_term_plan.learning_path && (
                <div style={{ marginBottom: 16 }}>
                  <h5 style={{ fontSize: 13, fontWeight: 500, color: '#666', marginBottom: 8 }}>
                    学习路径
                  </h5>
                  <EditableList
                    items={short_term_plan.learning_path.courses || []}
                    onChange={(items) => handleFieldChange('short_term_plan', 'learning_path', 'courses', items)}
                    label="课程"
                    addLabel="添加课程"
                  />
                </div>
              )}

              {short_term_plan.certifications && (
                <div style={{ marginBottom: 16 }}>
                  <EditableList
                    items={short_term_plan.certifications}
                    onChange={(items) => handleTopLevelFieldChange('short_term_plan', 'certifications', items)}
                    label="获取证书"
                    addLabel="添加证书"
                  />
                </div>
              )}

              <button
                className="btn btn-primary"
                onClick={() => setEditingSection(null)}
                style={{ padding: '6px 12px', fontSize: 13, marginTop: 12 }}
              >
                完成编辑
              </button>
            </div>
          ) : (
            <div>
              {/* 学习路径 */}
              {short_term_plan.learning_path && (
                <div style={{ marginBottom: 16 }}>
                  <h5 style={{ fontSize: 13, fontWeight: 500, color: '#666', marginBottom: 8 }}>
                    学习路径
                  </h5>
                  <div style={{ fontSize: 13, color: '#333' }}>
                    <p>
                      <strong>课程：</strong>
                      {short_term_plan.learning_path.courses?.join('、')}
                    </p>
                    <p>
                      <strong>书籍：</strong>
                      {short_term_plan.learning_path.books?.join('、')}
                    </p>
                  </div>
                </div>
              )}

              {/* 证书 */}
              {short_term_plan.certifications && short_term_plan.certifications.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <h5 style={{ fontSize: 13, fontWeight: 500, color: '#666', marginBottom: 8 }}>
                    获取证书
                  </h5>
                  <ul className="list-with-bullets">
                    {short_term_plan.certifications.map((cert, i) => (
                      <li key={i}>{cert}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* 量化目标 */}
              {short_term_plan.quantifiable_goals && short_term_plan.quantifiable_goals.length > 0 && (
                <div>
                  <h5 style={{ fontSize: 13, fontWeight: 500, color: '#666', marginBottom: 8 }}>
                    量化目标
                  </h5>
                  {short_term_plan.quantifiable_goals.map((goal, i) => (
                    <div
                      key={i}
                      style={{
                        padding: 8,
                        backgroundColor: '#F5F7FA',
                        borderRadius: 6,
                        marginBottom: 8,
                        fontSize: 13,
                      }}
                    >
                      <strong>{goal.metric}:</strong> {goal.target_value}
                      <div style={{ color: '#999', fontSize: 12 }}>
                        衡量方式: {goal.measurement_method}
                      </div>
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
          onAIPolish={onAIPolish}
        >
          {isEditing && editingSection === 'mid_term' ? (
            <div>
              <div style={{ marginBottom: 12 }}>
                <EditableField
                  value={mid_term_plan.duration || ''}
                  onChange={(val) => handleTopLevelFieldChange('mid_term_plan', 'duration', val)}
                  label="计划时长"
                  placeholder="如：6-12个月"
                />
              </div>

              <button
                className="btn btn-primary"
                onClick={() => setEditingSection(null)}
                style={{ padding: '6px 12px', fontSize: 13, marginTop: 12 }}
              >
                完成编辑
              </button>
            </div>
          ) : (
            <div>
              {mid_term_plan.advanced_learning && (
                <div style={{ marginBottom: 16 }}>
                  <h5 style={{ fontSize: 13, fontWeight: 500, color: '#666', marginBottom: 8 }}>
                    进阶学习
                  </h5>
                  <div style={{ fontSize: 13, color: '#333' }}>
                    <p>
                      <strong>高级课程：</strong>
                      {mid_term_plan.advanced_learning.advanced_courses?.join('、')}
                    </p>
                    <p>
                      <strong>专业培训：</strong>
                      {mid_term_plan.advanced_learning.professional_training?.join('、')}
                    </p>
                  </div>
                </div>
              )}

              {mid_term_plan.industry_engagement && (
                <div style={{ marginBottom: 16 }}>
                  <h5 style={{ fontSize: 13, fontWeight: 500, color: '#666', marginBottom: 8 }}>
                    行业参与
                  </h5>
                  <div style={{ fontSize: 13, color: '#333' }}>
                    <p>
                      <strong>会议：</strong>
                      {mid_term_plan.industry_engagement.conferences?.join('、')}
                    </p>
                    <p>
                      <strong>技术沙龙：</strong>
                      {mid_term_plan.industry_engagement.tech_meetups?.join('、')}
                    </p>
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
          onAIPolish={onAIPolish}
        >
          {isEditing && editingSection === 'evaluation' ? (
            <div>
              <div style={{ marginBottom: 12 }}>
                <EditableField
                  value={evaluation_framework.evaluation_cycles?.self_assessment || ''}
                  onChange={(val) =>
                    handleTopLevelFieldChange('evaluation_framework', 'evaluation_cycles', {
                      ...evaluation_framework.evaluation_cycles,
                      self_assessment: val,
                    })
                  }
                  label="自评周期"
                  multiline
                  placeholder="请输入自评周期说明"
                />
              </div>

              <button
                className="btn btn-primary"
                onClick={() => setEditingSection(null)}
                style={{ padding: '6px 12px', fontSize: 13, marginTop: 12 }}
              >
                完成编辑
              </button>
            </div>
          ) : (
            <div>
              {evaluation_framework.evaluation_cycles && (
                <div style={{ marginBottom: 16 }}>
                  <h5 style={{ fontSize: 13, fontWeight: 500, color: '#666', marginBottom: 8 }}>
                    评估周期
                  </h5>
                  <div style={{ fontSize: 13, color: '#333' }}>
                    <p>
                      <strong>自评：</strong>
                      {evaluation_framework.evaluation_cycles.self_assessment}
                    </p>
                    <p>
                      <strong>深度复盘：</strong>
                      {evaluation_framework.evaluation_cycles.deep_review}
                    </p>
                    <p>
                      <strong>年度总结：</strong>
                      {evaluation_framework.evaluation_cycles.annual_review}
                    </p>
                  </div>
                </div>
              )}

              {evaluation_framework.quantitative_metrics &&
                evaluation_framework.quantitative_metrics.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <h5 style={{ fontSize: 13, fontWeight: 500, color: '#666', marginBottom: 8 }}>
                      量化指标
                    </h5>
                    {evaluation_framework.quantitative_metrics.map((metric, i) => (
                      <div
                        key={i}
                        style={{
                          padding: 8,
                          backgroundColor: '#F5F7FA',
                          borderRadius: 6,
                          marginBottom: 8,
                          fontSize: 13,
                        }}
                      >
                        <strong>{metric.metric_name}:</strong>
                        <div style={{ color: '#666' }}>
                          {metric.scale && <span>范围: {metric.scale}</span>}
                          {metric.unit && <span>单位: {metric.unit}</span>}
                          {' | '}
                          <span style={{ color: '#2E86AB' }}>目标: {metric.target_progression}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

              {evaluation_framework.risk_warning && (
                <div>
                  <h5 style={{ fontSize: 13, fontWeight: 500, color: '#666', marginBottom: 8 }}>
                    风险预警
                  </h5>
                  <div style={{ fontSize: 13, color: '#333' }}>
                    <p>
                      <strong>潜在障碍：</strong>
                      {evaluation_framework.risk_warning.potential_obstacles?.join('、')}
                    </p>
                    <p>
                      <strong>预警信号：</strong>
                      {evaluation_framework.risk_warning.early_warning_signs?.join('、')}
                    </p>
                    <p>
                      <strong>应对方案：</strong>
                      {evaluation_framework.risk_warning.contingency_plans?.join('、')}
                    </p>
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
