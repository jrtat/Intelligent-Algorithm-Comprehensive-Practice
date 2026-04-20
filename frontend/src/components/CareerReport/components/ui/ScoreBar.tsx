interface ScoreBarProps {
  label: string;
  score: number;
  maxScore?: number;
  showLabel?: boolean;
  showValue?: boolean;
}

export function ScoreBar({
  label,
  score,
  maxScore = 100,
  showLabel = true,
  showValue = true,
}: ScoreBarProps) {
  const percentage = Math.min((score / maxScore) * 100, 100);

  return (
    <div className="score-bar-container">
      {showLabel && (
        <span className="score-bar-label">{label}</span>
      )}
      <div className="score-bar-track">
        <div
          className="score-bar-fill"
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showValue && (
        <span className="score-bar-value">{score}</span>
      )}
    </div>
  );
}
