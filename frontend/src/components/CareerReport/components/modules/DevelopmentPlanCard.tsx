import { useState } from 'react';
import { ReportCard } from '../ReportCard';
import { CollapsiblePanel } from '../ui/CollapsiblePanel';
import { EditableList } from '../ui/EditableList';
import { useReport } from '../../context/ReportContext';

interface DevelopmentPlanCardProps {
  isEditing?: boolean;
  onEdit?: () => void;
  onSave?: () => void;
  onCancel?: () => void;
  onAIPolishModule?: (moduleId: string) => void;
  onAIPolishField?: (fieldPath: string) => void;
  isPolishing?: boolean;
  saveStatus?: 'idle' | 'saving' | 'saved' | 'error';
}

export function DevelopmentPlanCard({
  isEditing = false,
  onEdit,
  onSave,
  onCancel,
  onAIPolishModule,
  onAIPolishField,
  isPolishing = false,
  saveStatus = 'idle',
}: DevelopmentPlanCardProps) {
  const { state, updateReport } = useReport();
  const { report } = state;

  const [editingPhase, setEditingPhase] = useState<string | null>(null);

  if (!report?.development_plan) return null;

  const phases = ['phase_1', 'phase_2', 'phase_3', 'phase_4'] as const;
  const phaseLabels: Record<string, string> = {
    phase_1: '第一阶段',
    phase_2: '第二阶段',
    phase_3: '第三阶段',
    phase_4: '第四阶段',
  };

  const handlePhaseFieldChange = (phase: string, field: string, value: any) => {
    updateReport({
      development_plan: {
        ...report.development_plan,
        [phase]: {
          ...report.development_plan?.[phase as keyof typeof report.development_plan],
          [field]: value,
        },
      },
    });
  };

  const calculateProgress = () => 0;

  return (
    <ReportCard
      id="development-plan"
      title="发展计划"
      icon="timeline"
      isEditing={isEditing}
      onEdit={onEdit}
      onSave={onSave}
      onCancel={onCancel}
      onAIPolishModule={onAIPolishModule}
      isPolishing={isPolishing}
      saveStatus={saveStatus}
    >

      {/* 各阶段 */}
      {phases.map((phaseKey) => {
        const phase = report.development_plan?.[phaseKey];
        if (!phase) return null;

        return (
          <CollapsiblePanel
            key={phaseKey}
            title={phaseLabels[phaseKey]}
            subtitle={`（${phase.duration || ''}）`}
            onEdit={isEditing ? () => setEditingPhase(phaseKey) : undefined}
            onAIPolish={() => onAIPolishField?.(`development_plan.${phaseKey}`)}
          >
            {isEditing && editingPhase === phaseKey ? (
              <div>
                <div className="mb-3">
                  <label className="mb-1 block text-[13px] text-[#999]">阶段时长</label>
                  <input
                    type="text"
                    className="w-full rounded-md border border-[#1677ff] bg-white px-3 py-2 text-[14px] text-[#333] transition-colors focus:border-[#1677ff] focus:outline-none focus:ring-2 focus:ring-[#1677ff]/20"
                    value={phase.duration || ''}
                    onChange={(e) => handlePhaseFieldChange(phaseKey, 'duration', e.target.value)}
                    placeholder="如：1-2个月"
                  />
                </div>
                <div className="mb-3 !p-3">
                  <EditableList
                    items={phase.goals || []}
                    onChange={(items) => handlePhaseFieldChange(phaseKey, 'goals', items)}
                    onAIPolishItem={(i) => onAIPolishField?.(`development_plan.${phaseKey}.goals[${i}]`)}
                    label="目标"
                    addLabel="添加目标"
                    disabled={isPolishing}
                  />
                </div>
                <div className="mb-3">
                  <EditableList
                    items={phase.actions || []}
                    onChange={(items) => handlePhaseFieldChange(phaseKey, 'actions', items)}
                    onAIPolishItem={(i) => onAIPolishField?.(`development_plan.${phaseKey}.actions[${i}]`)}
                    label="行动"
                    addLabel="添加行动"
                    disabled={isPolishing}
                  />
                </div>
                <div className="mb-3 !p-3">
                  <EditableList
                    items={phase.milestones || []}
                    onChange={(items) => handlePhaseFieldChange(phaseKey, 'milestones', items)}
                    onAIPolishItem={(i) => onAIPolishField?.(`development_plan.${phaseKey}.milestones[${i}]`)}
                    label="里程碑"
                    addLabel="添加里程碑"
                    disabled={isPolishing}
                  />
                </div>
                <button
                  className="mt-3 rounded-lg bg-[#1677ff] px-3 py-1.5 text-[13px] font-medium text-white transition-all hover:scale-105"
                  onClick={() => setEditingPhase(null)}
                >
                  完成编辑
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <h5 className="mb-2 text-[16px] font-medium text-[#666]">目标</h5>
                  <ul className="list-none space-y-2 pl-0">
                    {phase.goals?.map((goal, i) => (
                      <li key={i} className="relative !pl-5 text-[15px] text-[#333] before:absolute before:left-0 before:top-2 before:h-1.5 before:w-1.5  before:bg-[#1677ff]">
                        {goal}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h5 className="mb-2 text-[16px] font-medium text-[#666]">行动</h5>
                  <ul className="list-none space-y-2 pl-0">
                    {phase.actions?.map((action, i) => (
                      <li key={i} className="relative !pl-5 text-[15px] text-[#333] before:absolute before:left-0 before:top-2 before:h-1.5 before:w-1.5  before:bg-[#1677ff]">
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h5 className="mb-2 text-[16px] font-medium text-[#666]">里程碑</h5>
                  <ul className="list-none space-y-2 pl-0">
                    {phase.milestones?.map((m, i) => (
                      <li key={i} className="relative !pl-5 text-[15px] text-[#333] before:absolute before:left-0 before:top-2 before:h-1.5 before:w-1.5  before:bg-[#1677ff]">
                        {m}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </CollapsiblePanel>
        );
      })}
    </ReportCard>
  );
}