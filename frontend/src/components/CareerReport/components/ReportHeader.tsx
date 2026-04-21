import { useReport } from '../context/ReportContext';

interface ReportHeaderProps {
  onAIPolish: () => void;
  onExportPDF: () => void;
}

export function ReportHeader({ onAIPolish, onExportPDF }: ReportHeaderProps) {
  const { state, saveReport } = useReport();
  const { report, saveStatus } = state;

  const getSeason = () => {
    const month = new Date().getMonth();
    if (month >= 0 && month < 3) return '冬季';
    if (month >= 3 && month < 6) return '春季';
    if (month >= 6 && month < 9) return '夏季';
    return '秋季';
  };

  const currentYear = new Date().getFullYear();

  return (
    <header className="report-header">
      <div className="report-header-left">
        <h1 className="report-header-title">职业报告与行动计划</h1>
        <p className="report-header-subtitle">
          {report?.target_job || '目标岗位'} · {currentYear} {getSeason()}策略
        </p>
      </div>

      <div className="report-header-actions">
        {saveStatus !== 'idle' && (
          <span className={`save-status ${saveStatus}`}>
            {saveStatus === 'saving' && '保存中...'}
            {saveStatus === 'saved' && '已保存'}
            {saveStatus === 'error' && '保存失败'}
          </span>
        )}

        <button className="btn btn-accent" onClick={onAIPolish}>
          <span className="material-symbols-outlined" style={{ fontSize: 18 }}>auto_fix_high</span>
          AI润色
        </button>

        <button className="btn btn-primary" onClick={saveReport}>
          <span className="material-symbols-outlined" style={{ fontSize: 18 }}>save</span>
          保存
        </button>

        <button className="btn btn-outline" onClick={onExportPDF}>
          <span className="material-symbols-outlined" style={{ fontSize: 18 }}>picture_as_pdf</span>
          导出PDF
        </button>
      </div>
    </header>
  );
}
