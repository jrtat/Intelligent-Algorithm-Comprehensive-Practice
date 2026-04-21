import { useState, useRef, useEffect } from 'react';

export interface PolishResult {
  original: any;
  polished: any;
  changes: Array<{
    path: string;
    before: string;
    after: string;
  }>;
}

interface AIPolishComparePanelProps {
  isOpen: boolean;
  result: PolishResult;
  onApplyAll: () => void;
  onApplyPartial: (selectedPaths: string[]) => void;
  onApplySingle: (path: string) => void;
  onDiscard: () => void;
}

interface DiffSegment {
  type: 'same' | 'changed';
  before?: string;
  after?: string;
}

function computeDiff(before: string, after: string): DiffSegment[] {
  if (before === after) return [{ type: 'same' }];

  const beforeWords = before.split(/(\s+)/);
  const afterWords = after.split(/(\s+)/);

  const segments: DiffSegment[] = [];
  let i = 0, j = 0;

  while (i < beforeWords.length || j < afterWords.length) {
    if (i < beforeWords.length && j < afterWords.length && beforeWords[i] === afterWords[j]) {
      segments.push({ type: 'same' });
      i++;
      j++;
    } else {
      let beforeChunk = '';
      let afterChunk = '';

      while (i < beforeWords.length && (j >= afterWords.length || beforeWords[i] !== afterWords[j])) {
        beforeChunk += beforeWords[i];
        i++;
      }

      while (j < afterWords.length && (i >= beforeWords.length || afterWords[j] !== beforeWords[i])) {
        afterChunk += afterWords[j];
        j++;
      }

      if (beforeChunk || afterChunk) {
        segments.push({
          type: 'changed',
          before: beforeChunk.trim(),
          after: afterChunk.trim(),
        });
      }
    }
  }

  return segments.filter(s => s.type === 'same' || (s.before && s.after));
}

function pathToLabel(path: string[]): string {
  const moduleLabels: Record<string, string> = {
    candidate_summary: '候选人总结',
    match_analysis: '匹配分析',
    gap_analysis: '差距分析',
    career_path_planning: '职业路径规划',
    development_plan: '发展计划',
    action_plan: '行动计划',
    final_recommendation: '最终推荐',
  };

  const fieldLabels: Record<string, string> = {
    current_background: '当前背景',
    core_strengths: '核心优势',
    areas_for_improvement: '待提升领域',
    goal_description: '目标描述',
    social_demand: '社会需求',
    technology_trends: '技术趋势',
    actions: '行动',
    milestones: '里程碑',
    courses: '课程',
    books: '书籍',
    projects: '项目',
  };

  if (path.length === 1) {
    return moduleLabels[path[0]] || path[0];
  }

  const lastKey = path[path.length - 1];
  if (lastKey.match(/^\d+$/)) {
    return `${path[path.length - 2]}[${lastKey}]`;
  }

  return fieldLabels[lastKey] || lastKey;
}

export function AIPolishComparePanel({
  isOpen,
  result,
  onApplyAll,
  onApplyPartial,
  onApplySingle,
  onDiscard,
}: AIPolishComparePanelProps) {
  const [selectedPaths, setSelectedPaths] = useState<Set<string>>(new Set());
  const [viewMode, setViewMode] = useState<'split' | 'vertical'>('split');
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      setSelectedPaths(new Set());
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const { changes } = result;

  const togglePath = (path: string) => {
    const newSelected = new Set(selectedPaths);
    if (newSelected.has(path)) {
      newSelected.delete(path);
    } else {
      newSelected.add(path);
    }
    setSelectedPaths(newSelected);
  };

  const handleApplyPartial = () => {
    onApplyPartial(Array.from(selectedPaths));
  };

  return (
    <div className="ai-polish-compare-overlay">
      <div ref={panelRef} className="ai-polish-compare-panel">
        <div className="compare-header">
          <div className="compare-title-row">
            <h3>润色结果对比</h3>
            <span className="changes-count">{changes.length} 处修改</span>
          </div>
          <div className="compare-view-toggle">
            <button
              className={`toggle-btn ${viewMode === 'split' ? 'active' : ''}`}
              onClick={() => setViewMode('split')}
            >
              左右对比
            </button>
            <button
              className={`toggle-btn ${viewMode === 'vertical' ? 'active' : ''}`}
              onClick={() => setViewMode('vertical')}
            >
              上下对比
            </button>
          </div>
        </div>

        <div className="compare-content">
          {changes.map((change, index) => {
            const segments = computeDiff(change.before, change.after);
            const label = pathToLabel(change.path.split('.'));

            return (
              <div key={index} className="compare-item">
                <div className="compare-item-header">
                  <label className="compare-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedPaths.has(change.path)}
                      onChange={() => togglePath(change.path)}
                    />
                    <span className="compare-item-label">{label}</span>
                  </label>
                  <button
                    className="btn-apply-single"
                    onClick={() => onApplySingle(change.path)}
                  >
                    应用此句
                  </button>
                </div>

                <div className={`compare-body ${viewMode}`}>
                  <div className="compare-before">
                    <div className="compare-label">润色前</div>
                    <div className="compare-text original">
                      {segments.map((seg, i) => (
                        <span key={i} className={seg.type === 'changed' ? 'text-changed' : ''}>
                          {seg.type === 'changed' ? seg.before : seg.type === 'same' ? change.before : ''}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="compare-after">
                    <div className="compare-label">润色后</div>
                    <div className="compare-text polished">
                      {segments.map((seg, i) => (
                        <span key={i} className={seg.type === 'changed' ? 'text-highlight' : ''}>
                          {seg.type === 'changed' ? seg.after : seg.type === 'same' ? change.after : ''}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="compare-footer">
          <button className="btn btn-outline" onClick={onDiscard}>
            放弃
          </button>
          <button
            className="btn btn-outline"
            onClick={handleApplyPartial}
            disabled={selectedPaths.size === 0}
          >
            应用选中 ({(selectedPaths.size)})
          </button>
          <button className="btn btn-accent" onClick={onApplyAll}>
            应用全部
          </button>
        </div>
      </div>
    </div>
  );
}