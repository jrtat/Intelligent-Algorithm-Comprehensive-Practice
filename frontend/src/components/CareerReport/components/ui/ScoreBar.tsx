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
    <div className="mb-3 flex items-center gap-3">
      {showLabel && (
        <span className="w-[120px] text-[14px] text-[#333]">{label}</span>
      )}
      <div className="flex-1 rounded bg-[#F5F7FA]">
        <div
          className="h-2 rounded transition-all"
          style={{ width: `${percentage}%`, backgroundColor: '#1677ff' }}
        />
      </div>
      {showValue && (
        <span className="w-[50px] text-right text-[16px] font-bold" style={{ color: '#1677ff' }}>
          {score}
        </span>
      )}
    </div>
  );
}