import type { Gap } from '../../../../types/job';

interface GapCardProps {
  gap: Gap;
  onEdit?: () => void;
  onDelete?: () => void;
  onAIPolish?: () => void;
  showActions?: boolean;
}

export function GapCard({
  gap,
  onEdit,
  onDelete,
  onAIPolish,
  showActions = true,
}: GapCardProps) {
  const importanceClass = gap.importance === '高' ? 'high' : 'medium';

  return (
    <div
      className="gap-card"
      style={{ position: 'relative', paddingRight: showActions ? 48 : undefined }}
    >
      <div className="gap-card-header">
        <span className="gap-card-title">{gap.skill}</span>
        <span className={`gap-card-importance ${importanceClass}`}>
          {gap.importance}
        </span>
      </div>

      <div className="gap-card-level">
        <span>当前水平：{gap.current_level}</span>
        <span>目标水平：{gap.target_level}</span>
      </div>

      {Array.isArray(gap.learning_resources) && gap.learning_resources.length > 0 && (
        <ul className="gap-card-resources">
          {gap.learning_resources.map((resource, index) => (
            <li key={index}>{resource}</li>
          ))}
        </ul>
      )}

      {/* Action buttons on hover */}
      {showActions && (onEdit || onDelete || onAIPolish) && (
        <div
          className="gap-card-actions"
          style={{
            position: 'absolute',
            top: 8,
            right: 8,
            display: 'flex',
            gap: 4,
            opacity: 0,
            transition: 'opacity 0.2s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.opacity = '1')}
          onMouseLeave={(e) => (e.currentTarget.style.opacity = '0')}
        >
          {onAIPolish && (
            <button
              className="btn-icon"
              onClick={onAIPolish}
              title="AI润色"
              style={{ background: 'white', boxShadow: '0 1px 4px rgba(0,0,0,0.1)' }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: 14, color: '#FF9F43' }}>
                auto_fix_high
              </span>
            </button>
          )}
          {onEdit && (
            <button
              className="btn-icon"
              onClick={onEdit}
              title="编辑"
              style={{ background: 'white', boxShadow: '0 1px 4px rgba(0,0,0,0.1)' }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: 14, color: '#666' }}>
                edit
              </span>
            </button>
          )}
          {onDelete && (
            <button
              className="btn-icon"
              onClick={onDelete}
              title="删除"
              style={{ background: 'white', boxShadow: '0 1px 4px rgba(0,0,0,0.1)' }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: 14, color: '#DC2626' }}>
                delete
              </span>
            </button>
          )}
        </div>
      )}
    </div>
  );
}
