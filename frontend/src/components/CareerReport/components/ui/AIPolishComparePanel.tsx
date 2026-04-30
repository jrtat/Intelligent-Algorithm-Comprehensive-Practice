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
    <div className="ai-polish-compare-overlay fixed inset-0 z-[2000] flex items-center justify-center bg-black/50 animate-modal-fade">
      <div
        ref={panelRef}
        className="flex h-[80vh] w-[900px] max-w-[90%] flex-col overflow-hidden rounded-xl bg-white shadow-2xl animate-modal-slide"
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#DCDCDC] bg-[#F5F7FA] px-5 py-4">
          <div className="flex items-center gap-3">
            <h3 className="m-0 text-[16px] font-bold text-[#333]">润色结果对比</h3>
            <span className="rounded bg-[rgba(255,159,67,0.1)] px-2 py-0.5 text-[12px]" style={{ color: '#FF9F43' }}>
              {changes.length} 处修改
            </span>
          </div>
          <div className="flex gap-2">
            <button
              className={`rounded-md border px-3 py-1.5 text-[12px] transition-all ${viewMode === 'split' ? 'bg-[#1677ff] text-white border-[#1677ff]' : 'border-[#DCDCDC] text-[#666] hover:bg-gray-50'}`}
              onClick={() => setViewMode('split')}
            >
              左右对比
            </button>
            <button
              className={`rounded-md border px-3 py-1.5 text-[12px] transition-all ${viewMode === 'vertical' ? 'bg-[#1677ff] text-white border-[#1677ff]' : 'border-[#DCDCDC] text-[#666] hover:bg-gray-50'}`}
              onClick={() => setViewMode('vertical')}
            >
              上下对比
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5">
          {changes.map((change, index) => {
            const segments = computeDiff(change.before, change.after);
            const label = pathToLabel(change.path.split('.'));

            return (
              <div key={index} className="mb-5 overflow-hidden rounded-lg border border-[#DCDCDC]">
                <div className="flex items-center justify-between border-b border-[#DCDCDC] bg-[#F5F7FA] px-4 py-3">
                  <label className="flex cursor-pointer items-center gap-2">
                    <input
                      type="checkbox"
                      checked={selectedPaths.has(change.path)}
                      onChange={() => togglePath(change.path)}
                      className="h-4 w-4 cursor-pointer accent-[#1677ff]"
                    />
                    <span className="text-[14px] font-medium text-[#333]">{label}</span>
                  </label>
                  <button
                    className="rounded px-3 py-1 text-[12px] font-medium text-white transition-colors hover:opacity-90"
                    style={{ backgroundColor: '#FF9F43' }}
                    onClick={() => onApplySingle(change.path)}
                  >
                    应用此句
                  </button>
                </div>

                <div className={`flex ${viewMode === 'split' ? 'flex-row' : 'flex-col'}`}>
                  <div className={`${viewMode === 'split' ? 'flex-1 border-r border-[#DCDCDC]' : 'flex-1 border-b border-[#DCDCDC]'}`}>
                    <div className="mb-2 text-[11px] font-medium uppercase text-[#999]">润色前</div>
                    <div className="text-[14px] leading-relaxed text-[#666]">
                      {segments.map((seg, i) => (
                        <span key={i} className={seg.type === 'changed' ? 'bg-red-100 text-red-500 line-through' : ''}>
                          {seg.type === 'changed' ? seg.before : seg.type === 'same' ? change.before : ''}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="mb-2 text-[11px] font-medium uppercase text-[#999]">润色后</div>
                    <div className="text-[14px] leading-relaxed text-[#333]">
                      {segments.map((seg, i) => (
                        <span key={i} className={seg.type === 'changed' ? 'bg-amber-50 font-medium' : ''} style={{ color: seg.type === 'changed' ? '#E8891F' : undefined }}>
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

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 border-t border-[#DCDCDC] bg-[#F5F7FA] px-5 py-4">
          <button
            className="rounded-lg border border-[#DCDCDC] px-4 py-2 text-[14px] font-medium text-[#666] transition-colors hover:bg-gray-50"
            onClick={onDiscard}
          >
            放弃
          </button>
          <button
            className="rounded-lg border border-[#DCDCDC] px-4 py-2 text-[14px] font-medium text-[#666] transition-colors hover:bg-gray-50 disabled:opacity-50"
            onClick={handleApplyPartial}
            disabled={selectedPaths.size === 0}
          >
            应用选中 ({selectedPaths.size})
          </button>
          <button
            className="rounded-lg px-5 py-2 text-[14px] font-medium text-white transition-all hover:scale-105"
            style={{ backgroundColor: '#FF9F43' }}
            onClick={onApplyAll}
          >
            应用全部
          </button>
        </div>
      </div>
    </div>
  );
}