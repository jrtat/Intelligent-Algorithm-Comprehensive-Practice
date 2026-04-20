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
  onAIPolish?: () => void;
  saveStatus?: 'idle' | 'saving' | 'saved' | 'error';
}

export function DevelopmentPlanCard({
  isEditing = false,
  onEdit,
  onSave,
  onCancel,
  onAIPolish,
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

  const calculateProgress = () => {
    return 0;
  };

  return (
    <ReportCard
      id="development-plan"
      title="发展计划"
      icon="timeline"
      isEditing={isEditing}
      onEdit={onEdit}
      onSave={onSave}
      onCancel={onCancel}
      onAIPolish={onAIPolish}
      saveStatus={saveStatus}
    >
      {/* 进度概览 */}
      <div className="progress-tracker" style={{ marginBottom: 20 }}>
        <span style={{ fontSize: 14, color: '#666' }}>计划进度</span>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${calculateProgress()}%` }} />
        </div>
        <span className="progress-text">{calculateProgress()}%</span>
      </div>

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
            onAIPolish={onAIPolish}
          >
            {isEditing && editingPhase === phaseKey ? (
              <div>
                <div style={{ marginBottom: 12 }}>
                  <label style={{ fontSize: 13, color: '#999', marginBottom: 4, display: 'block' }}>
                    阶段时长
                  </label>
                  <input
                    type="text"
                    className="form-input"
                    value={phase.duration || ''}
                    onChange={(e) => handlePhaseFieldChange(phaseKey, 'duration', e.target.value)}
                    placeholder="如：1-2个月"
                    style={{ borderColor: '#2E86AB' }}
                  />
                </div>

                <div style={{ marginBottom: 12 }}>
                  <EditableList
                    items={phase.goals || []}
                    onChange={(items) => handlePhaseFieldChange(phaseKey, 'goals', items)}
                    label="目标"
                    addLabel="添加目标"
                  />
                </div>

                <div style={{ marginBottom: 12 }}>
                  <EditableList
                    items={phase.actions || []}
                    onChange={(items) => handlePhaseFieldChange(phaseKey, 'actions', items)}
                    label="行动"
                    addLabel="添加行动"
                  />
                </div>

                <div style={{ marginBottom: 12 }}>
                  <EditableList
                    items={phase.milestones || []}
                    onChange={(items) => handlePhaseFieldChange(phaseKey, 'milestones', items)}
                    label="里程碑"
                    addLabel="添加里程碑"
                  />
                </div>

                <button
                  className="btn btn-primary"
                  onClick={() => setEditingPhase(null)}
                  style={{ padding: '6px 12px', fontSize: 13, marginTop: 12 }}
                >
                  完成编辑
                </button>
              </div>
            ) : (
              <div>
                <div style={{ marginBottom: 12 }}>
                  <h5 style={{ fontSize: 13, fontWeight: 500, color: '#666', marginBottom: 8 }}>目标</h5>
                  <ul className="list-with-bullets">
                    {phase.goals?.map((goal, i) => (
                      <li key={i}>{goal}</li>
                    ))}
                  </ul>
                </div>

                <div style={{ marginBottom: 12 }}>
                  <h5 style={{ fontSize: 13, fontWeight: 500, color: '#666', marginBottom: 8 }}>行动</h5>
                  <ul className="list-with-bullets">
                    {phase.actions?.map((action, i) => (
                      <li key={i}>{action}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h5 style={{ fontSize: 13, fontWeight: 500, color: '#666', marginBottom: 8 }}>里程碑</h5>
                  <ul className="list-with-bullets">
                    {phase.milestones?.map((m, i) => (
                      <li key={i}>{m}</li>
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
