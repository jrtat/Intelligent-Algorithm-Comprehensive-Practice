import { useState } from 'react';
import { ReportCard } from '../ReportCard.tsx';
import { CollapsiblePanel } from '../ui/CollapsiblePanel.tsx';
import { EditableField } from '../ui/EditableField.tsx';
import { EditableList } from '../ui/EditableList.tsx';
import { EditModal } from '../ui/EditModal.tsx';
import type { FormField } from '../ui/EditModal.tsx';
import { EditableObjectArray } from '../ui/EditableObjectArray.tsx';
import { useReport } from '../../context/ReportContext.tsx';
import type { Stage } from '../../../../types/job.ts';

interface CareerPathCardProps {
  isEditing?: boolean;
  onEdit?: () => void;
  onSave?: () => void;
  onCancel?: () => void;
  onAIPolishModule?: (moduleId: string) => void;
  onAIPolishField?: (fieldPath: string) => void;
  isPolishing?: boolean;
  saveStatus?: 'idle' | 'saving' | 'saved' | 'error';
}

const stageFields: FormField[] = [
  { key: 'stage_name', label: '阶段名称', type: 'text', placeholder: '如：初级测试工程师', required: true, maxLength: 50 },
  { key: 'typical_duration', label: '典型时长', type: 'text', placeholder: '如：1-2年' },
  { key: 'core_requirements', label: '核心要求', type: 'textarea', placeholder: '请输入核心要求（每行一个）', maxLength: 300 },
  { key: 'key_responsibilities', label: '关键职责', type: 'textarea', placeholder: '请输入关键职责（每行一个）', maxLength: 300 },
  { key: 'promotion_criteria', label: '晋升标准', type: 'textarea', placeholder: '请输入晋升标准', maxLength: 200 },
];

export function CareerPathCard({
  isEditing = false,
  onEdit,
  onSave,
  onCancel,
  onAIPolishModule,
  onAIPolishField,
  isPolishing = false,
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

  const renderStageCard = (stage: Record<string, any>, _index: number) => (
    <div className="relative !mb-3 rounded-lg bg-[#F5F7FA] !p-3">
      <div className="!mb-2 flex items-center justify-between">
        <span className="font-medium text-[#333]">{stage.stage_name}</span>
        <span className="text-[16px] text-[#999]">{stage.typical_duration}</span>
      </div>
      <div className="text-[16px] text-[#666]">
        <div>
          <strong>核心要求：</strong>
          {Array.isArray(stage.core_requirements) ? stage.core_requirements.join('、') : stage.core_requirements}
        </div>
        <div className="mt-1">
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
      onAIPolishModule={onAIPolishModule}
      isPolishing={isPolishing}
      saveStatus={saveStatus}
    >
    {/* 职业目标 */}
    <div className="mb-5 !p-8">
      <h4 className="!mb-3 border-b border-[#E8F4F8] !pb-2 text-[18px] !font-bold  text-[#333]">
            职业目标
          </h4>
      <ul className="list-none space-y-3 !p-3"></ul>
        {/* 短期目标 */}
        <CollapsiblePanel
          title="短期目标"
          subtitle={`（${career_goals?.short_term?.duration || ''}）`}
          onEdit={isEditing ? () => setEditingGoal('short_term') : undefined}
          onAIPolish={isEditing ? () => onAIPolishField?.('career_path_planning.career_goals.short_term.goal_description') : undefined}
        >
          {isEditing && editingGoal === 'short_term' ? (
            <div>
              <div className="!p-3">
                <label className="!mb-1 block text-[16px] text-[#999]">时长</label>
                <input
                  type="text"
                  className="w-full rounded-md border border-[#1677ff] bg-white !px-4 !py-3 text-[16px] text-[#333] transition-colors focus:border-[#1677ff] focus:outline-none focus:ring-2 focus:ring-[#1677ff]/20"
                  value={career_goals?.short_term?.duration || ''}
                  onChange={(e) => handleGoalFieldChange('short_term', 'duration', e.target.value)}
                  placeholder="如：1-6个月"
                />
              </div>
              <div className="!mb-3">
                <label className="!mb-1 block text-[16px] text-[#999]">目标描述</label>
                <textarea
                  className="w-full rounded-md border border-[#1677ff] bg-white !px-3 !py-2 text-[16px] text-[#333] transition-colors focus:border-[#1677ff] focus:outline-none focus:ring-2 focus:ring-[#1677ff]/20"
                  value={career_goals?.short_term?.goal_description || ''}
                  onChange={(e) => handleGoalFieldChange('short_term', 'goal_description', e.target.value)}
                  rows={3}
                  style={{ minHeight: '80px' }}
                />
              </div>
              <EditableList
                items={career_goals?.short_term?.key_milestones || []}
                onChange={(items) => handleGoalFieldChange('short_term', 'key_milestones', items)}
                onAIPolishItem={(i) => onAIPolishField?.(`career_path_planning.career_goals.short_term.key_milestones[${i}]`)}
                label="关键里程碑"
                addLabel="添加里程碑"
                disabled={isPolishing}
              />
              <button
              className="!mt-3 rounded-lg bg-[#1677ff] !px-3 !py-1.5 text-[16px] font-medium text-white transition-all hover:scale-105"
                onClick={() => setEditingGoal(null)}
              >
                完成编辑
              </button>
            </div>
          ) : (
            <div>
              <p className="!mb-3 leading-relaxed text-[#333]">{career_goals?.short_term?.goal_description}</p>
              <h5 className="!mb-2 text-[16px] font-medium text-[#666]">关键里程碑</h5>
              <ul className="list-none space-y-3 !pl-0">
                {career_goals?.short_term?.key_milestones?.map((m, i) => (
                  <li key={i} className="relative !pl-5 text-[#333] before:absolute before:left-0 before:h-1.5 before:w-1.5 before:rounded-full before:bg-[#1677ff] before:top-2">
                    {m}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CollapsiblePanel>

        {/* 中期目标 */}
        <CollapsiblePanel
          title="中期目标"
          subtitle={`（${career_goals?.mid_term?.duration || ''}）`}
          onEdit={isEditing ? () => setEditingGoal('mid_term') : undefined}
          onAIPolish={isEditing ? () => onAIPolishField?.('career_path_planning.career_goals.mid_term.goal_description') : undefined}
        >
          {isEditing && editingGoal === 'mid_term' ? (
            <div>
              <div className="!mb-3">
                <label className="!mb-1 block text-[16px] text-[#999]">时长</label>
                <input
                  type="text"
                  className="w-full rounded-md border border-[#1677ff] bg-white !px-3 !py-2 text-[16px] text-[#333] transition-colors focus:border-[#1677ff] focus:outline-none focus:ring-2 focus:ring-[#1677ff]/20"
                  value={career_goals?.mid_term?.duration || ''}
                  onChange={(e) => handleGoalFieldChange('mid_term', 'duration', e.target.value)}
                  placeholder="如：6-12个月"
                />
              </div>
              <div className="!mb-3">
                <label className="!mb-1 block text-[16px] text-[#999]">目标描述</label>
                <textarea
                  className="w-full rounded-md border border-[#1677ff] bg-white !px-3 !py-2 text-[16px] text-[#333] transition-colors focus:border-[#1677ff] focus:outline-none focus:ring-2 focus:ring-[#1677ff]/20"
                  value={career_goals?.mid_term?.goal_description || ''}
                  onChange={(e) => handleGoalFieldChange('mid_term', 'goal_description', e.target.value)}
                  rows={3}
                  style={{ minHeight: '80px' }}
                />
              </div>
              <EditableList
                items={career_goals?.mid_term?.key_milestones || []}
                onChange={(items) => handleGoalFieldChange('mid_term', 'key_milestones', items)}
                onAIPolishItem={(i) => onAIPolishField?.(`career_path_planning.career_goals.mid_term.key_milestones[${i}]`)}
                label="关键里程碑"
                addLabel="添加里程碑"
                disabled={isPolishing}
              />
              <button
                className="!mt-3 rounded-lg bg-[#1677ff] !px-3 !py-1.5 text-[16px] font-medium text-white transition-all hover:scale-105"
                onClick={() => setEditingGoal(null)}
              >
                完成编辑
              </button>
            </div>
          ) : (
            <div>
              <p className="!mb-3 leading-relaxed text-[#333]">{career_goals?.mid_term?.goal_description}</p>
              <h5 className="!mb-2 text-[16px] font-medium text-[#666]">关键里程碑</h5>
              <ul className="list-none space-y-3 !pl-0">
                {career_goals?.mid_term?.key_milestones?.map((m, i) => (
                  <li key={i} className="relative !pl-5 text-[#333] before:absolute before:left-0 before:h-1.5 before:w-1.5 before:rounded-full before:bg-[#1677ff] before:top-2">
                    {m}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CollapsiblePanel>

        {/* 长期目标 */}
        <CollapsiblePanel
          title="长期目标"
          subtitle={`（${career_goals?.long_term?.duration || ''}）`}
          onEdit={isEditing ? () => setEditingGoal('long_term') : undefined}
          onAIPolish={isEditing ? () => onAIPolishField?.('career_path_planning.career_goals.long_term.goal_description') : undefined}
        >
          {isEditing && editingGoal === 'long_term' ? (
            <div>
              <div className="!mb-3">
                <label className="!mb-1 block text-[16px] text-[#999]">时长</label>
                <input
                  type="text"
                  className="w-full rounded-md border border-[#1677ff] bg-white !px-3 !py-2 text-[16px] text-[#333] transition-colors focus:border-[#1677ff] focus:outline-none focus:ring-2 focus:ring-[#1677ff]/20"
                  value={career_goals?.long_term?.duration || ''}
                  onChange={(e) => handleGoalFieldChange('long_term', 'duration', e.target.value)}
                  placeholder="如：1年以上"
                />
              </div>
              <div className="!mb-3">
                <label className="!mb-1 block text-[16px] text-[#999]">目标描述</label>
                <textarea
                  className="w-full rounded-md border border-[#1677ff] bg-white !px-3 !py-2 text-[16px] text-[#333] transition-colors focus:border-[#1677ff] focus:outline-none focus:ring-2 focus:ring-[#1677ff]/20"
                  value={career_goals?.long_term?.goal_description || ''}
                  onChange={(e) => handleGoalFieldChange('long_term', 'goal_description', e.target.value)}
                  rows={3}
                  style={{ minHeight: '80px' }}
                />
              </div>
              <EditableList
                items={career_goals?.long_term?.key_milestones || []}
                onChange={(items) => handleGoalFieldChange('long_term', 'key_milestones', items)}
                onAIPolishItem={(i) => onAIPolishField?.(`career_path_planning.career_goals.long_term.key_milestones[${i}]`)}
                label="关键里程碑"
                addLabel="添加里程碑"
                disabled={isPolishing}
              />
              <button
                className="!mt-3 rounded-lg bg-[#1677ff] !px-3 !py-1.5 text-[16px] font-medium text-white transition-all hover:scale-105"
                onClick={() => setEditingGoal(null)}
              >
                完成编辑
              </button>
            </div>
          ) : (
            <div>
              <p className="!mb-3 leading-relaxed text-[#333]">{career_goals?.long_term?.goal_description}</p>
              <h5 className="!mb-2 text-[16px] font-medium text-[#666]">关键里程碑</h5>
              <ul className="list-none space-y-3 !pl-0">
                {career_goals?.long_term?.key_milestones?.map((m, i) => (
                  <li key={i} className="relative !pl-5 text-[#333] before:absolute before:left-0 before:h-1.5 before:w-1.5 before:rounded-full before:bg-[#1677ff] before:top-2">
                    {m}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CollapsiblePanel>
      </div>

      {/* 行业趋势 */}
      {industry_trends && (
        <div className="mb-5 !p-8">
          <h4 className="!mb-3 border-b border-[#E8F4F8] !pb-2 text-[18px] !font-bold  text-[#333]">
            行业趋势
          </h4>
          <div className="space-y-3 !p-3 text-[16px] leading-relaxed text-[#666]">
            {isEditing ? (
              <>
                <EditableField
                  value={industry_trends.social_demand}
                  onChange={(val) => handleIndustryTrendChange('social_demand', val)}
                  onSave={onSave}
                  onAIPolish={() => onAIPolishField?.('career_path_planning.industry_trends.social_demand')}
                  label="市场需求"
                  multiline
                  placeholder="请输入市场需求"
                  maxLength={500}
                  showCharCount
                />
                <EditableField
                  value={industry_trends.technology_trends}
                  onChange={(val) => handleIndustryTrendChange('technology_trends', val)}
                  onSave={onSave}
                  onAIPolish={() => onAIPolishField?.('career_path_planning.industry_trends.technology_trends')}
                  label="技术趋势"
                  multiline
                  placeholder="请输入技术趋势"
                  maxLength={500}
                  showCharCount
                />
                <EditableField
                  value={industry_trends.market_changes}
                  onChange={(val) => handleIndustryTrendChange('market_changes', val)}
                  onSave={onSave}
                  onAIPolish={() => onAIPolishField?.('career_path_planning.industry_trends.market_changes')}
                  label="市场变化"
                  multiline
                  placeholder="请输入市场变化"
                  maxLength={500}
                  showCharCount
                />
                <EditableField
                  value={industry_trends.salary_trends}
                  onChange={(val) => handleIndustryTrendChange('salary_trends', val)}
                  onSave={onSave}
                  onAIPolish={() => onAIPolishField?.('career_path_planning.industry_trends.salary_trends')}
                  label="薪资趋势"
                  multiline
                  placeholder="请输入薪资趋势"
                  maxLength={500}
                  showCharCount
                />
              </>
            ) : (
              <>
                <p><strong>市场需求：</strong>{industry_trends.social_demand}</p>
                <p><strong>技术趋势：</strong>{industry_trends.technology_trends}</p>
                <p><strong>市场变化：</strong>{industry_trends.market_changes}</p>
                <p><strong>薪资趋势：</strong>{industry_trends.salary_trends}</p>
              </>
            )}
          </div>
        </div>
      )}

      {/* 发展路径 */}
      {development_path?.path_stages && development_path.path_stages.length > 0 && (
        <div className="mb-5 !p-8">
          <h4 className="!mb-3 border-b border-[#E8F4F8] !pb-2 text-[18px] !font-bold  text-[#333]">
            发展路径
          </h4>
          <div className="space-y-3 !p-2 text-[16px] leading-relaxed text-[#666]"></div>
          {isEditing ? (
            <EditableObjectArray
              items={development_path.path_stages}
              onChange={handleStageChange}
              fields={stageFields}
              renderItem={renderStageCard}
              addLabel="添加阶段"
              addInitialValues={{ stage_name: '', level: 1, typical_duration: '', core_requirements: [], key_responsibilities: [], promotion_criteria: '' }}
            />
          ) : (
            development_path.path_stages.map((stage, index) => (
              <div key={index} className="mb-3 rounded-lg bg-[#F5F7FA] !p-3">
                <div className="mb-2 flex items-center justify-between">
                  <span className="font-medium text-[#333]">{stage.stage_name}</span>
                  <span className="text-[16px] text-[#999]">{stage.typical_duration}</span>
                </div>
                <div className="text-[16px] text-[#666]">
                  <div>
                    <strong>核心要求：</strong>
                    {Array.isArray(stage.core_requirements) ? stage.core_requirements.join('、') : stage.core_requirements}
                  </div>
                  <div className="mt-1">
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