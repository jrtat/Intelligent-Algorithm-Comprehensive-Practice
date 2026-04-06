interface AbilityBarProps {
  label: string;
  level: number;
  maxLevel?: number;
}

export function AbilityBar({ label, level, maxLevel = 5 }: AbilityBarProps) {
  return (
    <div className="ability-item">
      <span className="ability-label">{label}</span>
      <div className="ability-bar">
        {[...Array(maxLevel)].map((_, i) => (
          <div
            key={i}
            className={`ability-dot ${i < level ? 'active' : ''}`}
          />
        ))}
      </div>
      <span className="ability-value">{level}/{maxLevel}</span>
    </div>
  );
}
