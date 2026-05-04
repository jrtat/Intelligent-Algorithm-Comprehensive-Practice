import { Link } from 'react-router-dom';
import { useReport } from '../context/ReportContext.tsx';

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
    <header
      className="report-header sticky z-[100] flex items-center justify-between bg-white !px-6 no-print"
      style={{
        height: '60px',
        borderBottom: '1px solid #DCDCDC',
        top: '0px',
      }}
    >
      {/* Left: Breadcrumb */}
      <div className="flex items-center">
        <span className="flex items-center !text-[16px]">
          <Link to="/" className="text-[#666] no-underline transition-colors hover:text-[#1677ff]">首页 </Link>
          <span className="mx-2 text-[#999] !p-1"> / </span>
          <span className="text-[#1677ff] font-medium"> 职业报告</span>
        </span>
      </div>

      {/* Center: Title and Subtitle */}
      <div className="absolute left-1/2 transform -translate-x-1/2 flex flex-col items-center">
        <h1 className="m-0 text-[18px] font-bold text-[#333]">职业报告与行动计划</h1>
        <p className="m-0 text-[12px] text-[#999]">
          {report?.target_job || '目标岗位'} · {currentYear} {getSeason()}策略
        </p>
      </div>

      {/* Right: Action Buttons */}
      <div className="flex items-center gap-3">
        {saveStatus !== 'idle' && (
          <span
            className={`save-status rounded !px-3 !py-1 text-[12px] ${
              saveStatus === 'saving'
                ? 'bg-[#E8F4F8] text-[#1677ff]'
                : saveStatus === 'saved'
                  ? 'bg-green-100 text-green-600'
                  : 'bg-red-100 text-red-600'
            }`}
          >
            {saveStatus === 'saving' && '保存中...'}
            {saveStatus === 'saved' && '已保存'}
            {saveStatus === 'error' && '保存失败'}
          </span>
        )}

        <button
          className="inline-flex items-center gap-1 rounded-lg !px-4 !py-2 text-[14px] font-medium text-white transition-all hover:scale-105"
          style={{ backgroundColor: '#FF9F43' }}
          onClick={onAIPolish}
        >
          <span className="material-symbols-outlined text-[18px]">auto_fix_high</span>
          AI润色
        </button>

        <button
          className="inline-flex items-center gap-1 rounded-lg bg-[#1677ff] !px-4 !py-2 text-[14px] font-medium text-white transition-all hover:scale-105"
          onClick={saveReport}
        >
          <span className="material-symbols-outlined text-[18px]">save</span>
          保存
        </button>

        <button
          className="inline-flex items-center gap-1 rounded-lg border border-[#DCDCDC] !px-4 !py-2 text-[14px] font-medium text-[#666] transition-colors hover:bg-gray-50"
          onClick={onExportPDF}
        >
          <span className="material-symbols-outlined text-[18px]">picture_as_pdf</span>
          导出PDF
        </button>
      </div>
    </header>
  );
}