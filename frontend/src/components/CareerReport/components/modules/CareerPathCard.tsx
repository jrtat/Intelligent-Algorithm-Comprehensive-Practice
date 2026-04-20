import { useState } from 'react';
import { ReportCard } from '../ReportCard';
import { CollapsiblePanel } from '../ui/CollapsiblePanel';
import { EditableField } from '../ui/EditableField';
import { EditableList } from '../ui/EditableList';
import { EditModal } from '../ui/EditModal';
import type { FormField } from '../ui/EditModal';
import { EditableObjectArray } from '../ui/EditableObjectArray';
import { useReport } from '../../context/ReportContext';
import type { Stage } from '../../../../types/job';

interface CareerPathCardProps {
  isEditing?: boolean;
  onEdit?: () => void;
  onSave?: () => void;
  onCancel?: () => void;
  onAIPolish?: () => void;
  saveStatus?: 'idle' | 'saving' | 'saved' | 'error';
}

const stageFields: FormField[] = [
  {
    key: 'stage_name',
    label: '阶段名称',
    type: 'text',
    placeholder: '如：初级测试工程师',
    required: true,
    maxLength: 50,
  },
  {
    key: 'typical_duration',
    label: '典型时长',
    type: 'text',
    placeholder: '如：1-2年',
  },
  {
    key: 'core_requirements',
    label: '核心要求',
    type: 'textarea',
    placeholder: '请输入核心要求（每行一个）',
    maxLength: 300,
  },
  {
    key: 'key_responsibilities',
    label: '关键职责',
    type: 'textarea',
    placeholder: '请输入关键职责（每行一个）',
    maxLength: 300,
  },
  {
    key: 'promotion_criteria',
    label: '晋升标准',
    type: 'textarea',
    placeholder: '请输入晋升标准',
    maxLength: 200,
  },
];

export function CareerPathCard({
  isEditing = false,
  onEdit,
  onSave,
  onCancel,
  onAIPolish,
  saveStatus = 'idle',
}: CareerPathCardProps) {
  const { state, updateReport, updateNestedField } = useReport();
  const { report } = state;

  const [editingStageIndex, setEditingStageIndex] = useState<number | null>(null);
  const [editingGoal, setEditingGoal] = useState<string | null>(null);

  if (!report?.career_path_planning) return null;

  const { career_goals, industry_trends, development_path } = report.career_path_planning;

  const handleGoalFieldChange = (goalType: string, field: string, value: any) => {
    updateNestedField(['career_path_planning', 'career_goals', goalType, field], value);
  };

  const handleStageChange = (stages: Record<string, any>[]) => {
    updateReport({
      career_path_planning: {
        ...report.career_path_planning,
        development_path: {
          ...report.career_path_planning.development_path,
          path_stages: stages as Stage[],
        },
      },
    });
  };

  const handleIndustryTrendChange = (field: string, value: string) => {
    updateReport({
      career_path_planning: {
        ...report.career_path_planning,
        industry_trends: {
          ...report.career_path_planning.industry_trends,
          [field]: value,
        },
      },
    });
  };

  const renderStageCard = (stage: Record<string, any>, index: number) => (
    <div
      style={{
        padding: 12,
        backgroundColor: '#F5F7FA',
        borderRadius: 8,
        marginBottom: 12,
        position: 'relative',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
        <span style={{ fontWeight: 500, color: '#333' }}>{stage.stage_name}</span>
        <span style={{ fontSize: 12, color: '#999' }}>{stage.typical_duration}</span>
      </div>
      <div style={{ fontSize: 13, color: '#666' }}>
        <div>
          <strong>核心要求：</strong>
          {Array.isArray(stage.core_requirements)
            ? stage.core_requirements.join('、')
            : stage.core_requirements}
        </div>
        <div style={{ marginTop: 4 }}>
          <strong>晋升标准：</strong>
          {stage.promotion_criteria}
        </div>
      </div>
    </div>
  );

  return (
    <ReportCard
      id="career-path"
      title="职业路径规划"
      icon="route"
      isEditing={isEditing}
      onEdit={onEdit}
      onSave={onSave}
      onCancel={onCancel}
      onAIPolish={onAIPolish}
      saveStatus={saveStatus}
    >
      {/* 进度概览 */}
      <div className="progress-tracker" style={{ marginBottom: 20 }}>
        <span style={{ fontSize: 14, color: '#666' }}>规划进度</span>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: '0%' }} />
        </div>
        <span className="progress-text">0%</span>
      </div>

      {/* 职业目标 */}
      <div style={{ marginBottom: 20 }}>
        <CollapsiblePanel
          title="短期目标"
          subtitle={`（${career_goals?.short_term?.duration || ''}）`}
          onEdit={isEditing ? () => setEditingGoal('short_term') : undefined}
          onAIPolish={onAIPolish}
        >
          {isEditing && editingGoal === 'short_term' ? (
            <div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 13, color: '#999', marginBottom: 4, display: 'block' }}>时长</label>
                <input
                  type="text"
                  className="form-input"
                  value={career_goals?.short_term?.duration || ''}
                  onChange={(e) => handleGoalFieldChange('short_term', 'duration', e.target.value)}
                  placeholder="如：1-6个月"
                  style={{ borderColor: '#2E86AB' }}
                />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 13, color: '#999', marginBottom: 4, display: 'block' }}>目标描述</label>
                <textarea
                  className="form-input"
                  value={career_goals?.short_term?.goal_description || ''}
                  onChange={(e) => handleGoalFieldChange('short_term', 'goal_description', e.target.value)}
                  rows={3}
                  style={{ borderColor: '#2E86AB', minHeight: '80px' }}
                />
              </div>
              <EditableList
                items={career_goals?.short_term?.key_milestones || []}
                onChange={(items) => handleGoalFieldChange('short_term', 'key_milestones', items)}
                label="关键里程碑"
                addLabel="添加里程碑"
              />
              <div style={{ marginTop: 12 }}>
                <button
                  className="btn btn-primary"
                  onClick={() => setEditingGoal(null)}
                  style={{ padding: '6px 12px', fontSize: 13 }}
                >
                  完成编辑
                </button>
              </div>
            </div>
          ) : (
            <div>
              <p style={{ lineHeight: 1.6, color: '#333', marginBottom: 12 }}>
                {career_goals?.short_term?.goal_description}
              </p>
              <h5 style={{ fontSize: 13, fontWeight: 500, color: '#666', marginBottom: 8 }}>关键里程碑</h5>
              <ul className="list-with-bullets">
                {career_goals?.short_term?.key_milestones?.map((m, i) => (
                  <li key={i}>{m}</li>
                ))}
              </ul>
            </div>
          )}
        </CollapsiblePanel>

        <CollapsiblePanel
          title="中期目标"
          subtitle={`（${career_goals?.mid_term?.duration || ''}）`}
          onEdit={isEditing ? () => setEditingGoal('mid_term') : undefined}
          onAIPolish={onAIPolish}
        >
          {isEditing && editingGoal === 'mid_term' ? (
            <div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 13, color: '#999', marginBottom: 4, display: 'block' }}>时长</label>
                <input
                  type="text"
                  className="form-input"
                  value={career_goals?.mid_term?.duration || ''}
                  onChange={(e) => handleGoalFieldChange('mid_term', 'duration', e.target.value)}
                  placeholder="如：6-12个月"
                  style={{ borderColor: '#2E86AB' }}
                />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 13, color: '#999', marginBottom: 4, display: 'block' }}>目标描述</label>
                <textarea
                  className="form-input"
                  value={career_goals?.mid_term?.goal_description || ''}
                  onChange={(e) => handleGoalFieldChange('mid_term', 'goal_description', e.target.value)}
                  rows={3}
                  style={{ borderColor: '#2E86AB', minHeight: '80px' }}
                />
              </div>
              <EditableList
                items={career_goals?.mid_term?.key_milestones || []}
                onChange={(items) => handleGoalFieldChange('mid_term', 'key_milestones', items)}
                label="关键里程碑"
                addLabel="添加里程碑"
              />
              <div style={{ marginTop: 12 }}>
                <button
                  className="btn btn-primary"
                  onClick={() => setEditingGoal(null)}
                  style={{ padding: '6px 12px', fontSize: 13 }}
                >
                  完成编辑
                </button>
              </div>
            </div>
          ) : (
            <div>
              <p style={{ lineHeight: 1.6, color: '#333', marginBottom: 12 }}>
                {career_goals?.mid_term?.goal_description}
              </p>
              <h5 style={{ fontSize: 13, fontWeight: 500, color: '#666', marginBottom: 8 }}>关键里程碑</h5>
              <ul className="list-with-bullets">
                {career_goals?.mid_term?.key_milestones?.map((m, i) => (
                  <li key={i}>{m}</li>
                ))}
              </ul>
            </div>
          )}
        </CollapsiblePanel>

        <CollapsiblePanel
          title="长期目标"
          subtitle={`（${career_goals?.long_term?.duration || ''}）`}
          onEdit={isEditing ? () => setEditingGoal('long_term') : undefined}
          onAIPolish={onAIPolish}
        >
          {isEditing && editingGoal === 'long_term' ? (
            <div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 13, color: '#999', marginBottom: 4, display: 'block' }}>时长</label>
                <input
                  type="text"
                  className="form-input"
                  value={career_goals?.long_term?.duration || ''}
                  onChange={(e) => handleGoalFieldChange('long_term', 'duration', e.target.value)}
                  placeholder="如：1年以上"
                  style={{ borderColor: '#2E86AB' }}
                />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 13, color: '#999', marginBottom: 4, display: 'block' }}>目标描述</label>
                <textarea
                  className="form-input"
                  value={career_goals?.long_term?.goal_description || ''}
                  onChange={(e) => handleGoalFieldChange('long_term', 'goal_description', e.target.value)}
                  rows={3}
                  style={{ borderColor: '#2E86AB', minHeight: '80px' }}
                />
              </div>
              <EditableList
                items={career_goals?.long_term?.key_milestones || []}
                onChange={(items) => handleGoalFieldChange('long_term', 'key_milestones', items)}
                label="关键里程碑"
                addLabel="添加里程碑"
              />
              <div style={{ marginTop: 12 }}>
                <button
                  className="btn btn-primary"
                  onClick={() => setEditingGoal(null)}
                  style={{ padding: '6px 12px', fontSize: 13 }}
                >
                  完成编辑
                </button>
              </div>
            </div>
          ) : (
            <div>
              <p style={{ lineHeight: 1.6, color: '#333', marginBottom: 12 }}>
                {career_goals?.long_term?.goal_description}
              </p>
              <h5 style={{ fontSize: 13, fontWeight: 500, color: '#666', marginBottom: 8 }}>关键里程碑</h5>
              <ul className="list-with-bullets">
                {career_goals?.long_term?.key_milestones?.map((m, i) => (
                  <li key={i}>{m}</li>
                ))}
              </ul>
            </div>
          )}
        </CollapsiblePanel>
      </div>

      {/* 行业趋势 */}
      {industry_trends && (
        <div style={{ marginBottom: 20 }}>
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
            行业趋势
          </h4>
          <div style={{ fontSize: 13, color: '#666', lineHeight: 1.8 }}>
            {isEditing ? (
              <>
                <div style={{ marginBottom: 12 }}>
                  <EditableField
                    value={industry_trends.social_demand}
                    onChange={(val) => handleIndustryTrendChange('social_demand', val)}
                    label="市场需求"
                    multiline
                    placeholder="请输入市场需求"
                    maxLength={500}
                    showCharCount
                  />
                </div>
                <div style={{ marginBottom: 12 }}>
                  <EditableField
                    value={industry_trends.technology_trends}
                    onChange={(val) => handleIndustryTrendChange('technology_trends', val)}
                    label="技术趋势"
                    multiline
                    placeholder="请输入技术趋势"
                    maxLength={500}
                    showCharCount
                  />
                </div>
                <div style={{ marginBottom: 12 }}>
                  <EditableField
                    value={industry_trends.market_changes}
                    onChange={(val) => handleIndustryTrendChange('market_changes', val)}
                    label="市场变化"
                    multiline
                    placeholder="请输入市场变化"
                    maxLength={500}
                    showCharCount
                  />
                </div>
                <div>
                  <EditableField
                    value={industry_trends.salary_trends}
                    onChange={(val) => handleIndustryTrendChange('salary_trends', val)}
                    label="薪资趋势"
                    multiline
                    placeholder="请输入薪资趋势"
                    maxLength={500}
                    showCharCount
                  />
                </div>
              </>
            ) : (
              <>
                <p>
                  <strong>市场需求：</strong>
                  {industry_trends.social_demand}
                </p>
                <p>
                  <strong>技术趋势：</strong>
                  {industry_trends.technology_trends}
                </p>
                <p>
                  <strong>市场变化：</strong>
                  {industry_trends.market_changes}
                </p>
                <p>
                  <strong>薪资趋势：</strong>
                  {industry_trends.salary_trends}
                </p>
              </>
            )}
          </div>
        </div>
      )}

      {/* 发展路径 */}
      {development_path?.path_stages && development_path.path_stages.length > 0 && (
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
            发展阶段
          </h4>
          {isEditing ? (
            <EditableObjectArray
              items={development_path.path_stages}
              onChange={handleStageChange}
              fields={stageFields}
              renderItem={renderStageCard}
              addLabel="添加阶段"
              addInitialValues={{
                stage_name: '',
                level: 1,
                typical_duration: '',
                core_requirements: [],
                key_responsibilities: [],
                promotion_criteria: '',
              }}
            />
          ) : (
            development_path.path_stages.map((stage, index) => (
              <div
                key={index}
                style={{
                  padding: 12,
                  backgroundColor: '#F5F7FA',
                  borderRadius: 8,
                  marginBottom: 12,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ fontWeight: 500, color: '#333' }}>{stage.stage_name}</span>
                  <span style={{ fontSize: 12, color: '#999' }}>{stage.typical_duration}</span>
                </div>
                <div style={{ fontSize: 13, color: '#666' }}>
                  <div>
                    <strong>核心要求：</strong>
                    {Array.isArray(stage.core_requirements)
                      ? stage.core_requirements.join('、')
                      : stage.core_requirements}
                  </div>
                  <div style={{ marginTop: 4 }}>
                    <strong>晋升标准：</strong>
                    {stage.promotion_criteria}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Stage Edit Modal */}
      {editingStageIndex !== null && development_path?.path_stages && (
        <EditModal
          title="编辑阶段"
          fields={stageFields}
          initialValues={development_path.path_stages[editingStageIndex]}
          onSave={(values) => {
            const newStages = [...development_path.path_stages];
            newStages[editingStageIndex] = values as Stage;
            handleStageChange(newStages);
            setEditingStageIndex(null);
          }}
          onCancel={() => setEditingStageIndex(null)}
        />
      )}
    </ReportCard>
  );
}
