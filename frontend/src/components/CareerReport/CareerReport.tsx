import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ReportProvider, useReport } from './context/ReportContext';
import { ReportHeader } from './components/ReportHeader';
import { ReportSidebar } from './components/ReportSidebar';
import { BasicInfoCard } from './components/modules/BasicInfoCard';
import { CandidateSummaryCard } from './components/modules/CandidateSummaryCard';
import { MatchAnalysisCard } from './components/modules/MatchAnalysisCard';
import { GapAnalysisCard } from './components/modules/GapAnalysisCard';
import { CareerPathCard } from './components/modules/CareerPathCard';
import { DevelopmentPlanCard } from './components/modules/DevelopmentPlanCard';
import { ActionPlanCard } from './components/modules/ActionPlanCard';
import { FinalRecommendationCard } from './components/modules/FinalRecommendationCard';
import { AIPolishModal, type PolishSettings } from './components/ui/AIPolishModal';
import { AIPolishComparePanel } from './components/ui/AIPolishComparePanel';
import { polishReport } from './components/ui/AIPolishUtils';

function ReportContent() {
  const navigate = useNavigate();
  const { state, dispatch, saveReport, setPolishing, setPolishResult, setShowPolishCompare, setPolishError, setPolishSuccess, clearPolishState, applyPolishResult, setPrinting } = useReport();

  const [showAIPolishModal, setShowAIPolishModal] = useState(false);
  const [editingModuleId, setEditingModuleId] = useState<string | null>(null);
  const [polishSettings, setPolishSettings] = useState<PolishSettings>({
    scope: 'global',
    style: 'formal',
    intensity: 'medium',
  });
  const [polishProgress, setPolishProgress] = useState(0);

  const handleEdit = (moduleId: string) => {
    setEditingModuleId(moduleId);
  };

  const handleSave = () => {
    saveReport();
    setEditingModuleId(null);
  };

  const handleCancel = () => {
    setEditingModuleId(null);
  };

  const handleAIPolishGlobal = () => {
    setPolishSettings({
      scope: 'global',
      style: 'formal',
      intensity: 'medium',
    });
    setShowAIPolishModal(true);
  };

  const handleAIPolishModule = (moduleId: string) => {
    setPolishSettings({
      scope: 'module',
      moduleId,
      style: 'formal',
      intensity: 'medium',
    });
    setShowAIPolishModal(true);
  };

  const handleAIPolishField = (fieldPath: string) => {
    setPolishSettings({
      scope: 'field',
      fieldPath,
      style: 'formal',
      intensity: 'medium',
    });
    setShowAIPolishModal(true);
  };

  const handleStartPolish = async () => {
    if (!state.report) return;

    setShowAIPolishModal(false);
    setPolishing(true);
    setPolishProgress(0);

    const progressInterval = setInterval(() => {
      setPolishProgress(prev => Math.min(prev + 10, 90));
    }, 500);

    try {
      const result = await polishReport(state.report, polishSettings);

      clearInterval(progressInterval);
      setPolishProgress(100);

      if (result.success && result.result) {
        if (result.result.changes.length === 0) {
          setPolishSuccess('当前内容无需润色');
        } else {
          setPolishResult(result.result);
          setShowPolishCompare(true);
        }
      } else {
        setPolishError(result.error || '润色服务异常，请重试');
      }
    } catch (error) {
      clearInterval(progressInterval);
      setPolishError('润色服务异常，请重试');
    } finally {
      setPolishing(false);
    }
  };

  const handleApplyAll = useCallback(() => {
    applyPolishResult();
    setPolishSuccess('润色完成');
  }, [applyPolishResult, setPolishSuccess]);

  const handleApplyPartial = useCallback((selectedPaths: string[]) => {
    applyPolishResult(selectedPaths);
    setPolishSuccess('润色完成');
  }, [applyPolishResult, setPolishSuccess]);

  const handleApplySingle = useCallback((path: string) => {
    applyPolishResult([path]);
  }, [applyPolishResult]);

  const handleDiscard = useCallback(() => {
    clearPolishState();
  }, [clearPolishState]);

  const handleExportPDF = () => {
    // 设置打印状态，展开所有CollapsiblePanel
    setPrinting(true);
    // 收起侧边栏后再打印
    if (!state.sidebarCollapsed) {
      dispatch({ type: 'TOGGLE_SIDEBAR' });
      setTimeout(() => {
        window.print();
        setPrinting(false);
      }, 100);
    } else {
      window.print();
      setPrinting(false);
    }
  };

  const isModuleEditing = (moduleId: string) => editingModuleId === moduleId;

  // No data state
  if (state.noDataReason) {
    const messages: Record<string, { title: string; description: string; buttonText: string; buttonLink: string }> = {
      no_resume: { title: '请先上传简历', description: '在能力分析页面填写您的简历信息，然后进行岗位匹配', buttonText: '前往上传简历', buttonLink: '/capability-analysis' },
      no_job_matched: { title: '请先进行岗位匹配', description: '在岗位匹配页面选择心仪的岗位，生成深度解析报告', buttonText: '前往岗位匹配', buttonLink: '/job-match' },
      no_report: { title: '请生成职业报告', description: '在岗位深度解析页面点击"获取专项提升报告"', buttonText: '前往深度解析', buttonLink: '/job-match' },
    };

    const msg = messages[state.noDataReason];

    return (
      <div className="min-h-[70vh] items-center justify-center !p-10 text-center">
        <div
          className="mb-6 h-20 w-20 items-center justify-center rounded-full"
          style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
        >
          <span className="material-symbols-outlined text-[40px] text-white">description</span>
        </div>
        <h2 className="mb-3 text-[24px] font-bold text-[#333]">{msg.title}</h2>
        <p className="mb-8 max-w-[400px] text-[16px] text-[#666]">{msg.description}</p>
        <button
          onClick={() => navigate(msg.buttonLink)}
          className="inline-flex cursor-pointer items-center gap-2 rounded-lg border-0 !px-8 !py-3 text-[14px] font-bold text-white transition-all hover:scale-105"
          style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
        >
          {msg.buttonText}
          <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
        </button>
      </div>
    );
  }

  return (
    <div className="career-report relative min-h-screen overflow-hidden" style={{ backgroundColor: '#E8F4F8' }}>
      {/* Cache restored notification */}
      {state.showCacheRestored && (
        <div
          className="fixed left-1/2 z-[1000] items-center rounded-lg !px-6 !py-3 text-[14px] shadow-lg animate-slide-down"
          style={{ top: '80px', transform: 'translateX(-50%)', backgroundColor: '#D1FAE5', color: '#059669' }}
        >
          <span className="material-symbols-outlined mr-2 text-[16px]">restore</span>
          已加载上次编辑内容
        </div>
      )}

      {/* Polish success notification */}
      {state.polishSuccess && (
        <div
          className="fixed left-1/2 z-[1000] items-center rounded-lg !px-6 !py-3 text-[14px] shadow-lg animate-slide-down"
          style={{ top: '80px', transform: 'translateX(-50%)', backgroundColor: '#D1FAE5', color: '#059669' }}
        >
          <span className="material-symbols-outlined mr-2 text-[16px]">check_circle</span>
          {state.polishSuccess}
        </div>
      )}

      {/* Polish error notification */}
      {state.polishError && (
        <div
          className="fixed left-1/2 z-[1000] items-center rounded-lg !px-6 !py-3 text-[14px] shadow-lg animate-slide-down"
          style={{ top: '80px', transform: 'translateX(-50%)', backgroundColor: '#FEE2E2', color: '#DC2626' }}
        >
          <span className="material-symbols-outlined mr-2 text-[16px]">error</span>
          {state.polishError}
        </div>
      )}

      {/* Global progress bar */}
      {state.isPolishing && (
        <div className="fixed left-0 right-0 z-[99]" style={{ top: '60px', height: '3px', backgroundColor: '#E8F4F8' }}>
          <div
            className="h-full transition-all duration-300"
            style={{ width: `${polishProgress}%`, background: 'linear-gradient(90deg, #FF9F43, #FFD700)' }}
          />
        </div>
      )}

      <ReportHeader onAIPolish={handleAIPolishGlobal} onExportPDF={handleExportPDF} />
      <ReportSidebar />

      <main
        className="h-[calc(100vh-60px)] overflow-y-auto transition-all duration-300"
        style={{ marginLeft: state.sidebarCollapsed ? '0' : '240px' }}
      >
        <div className="mx-auto flex max-w-[1200px] flex-col gap-5 !p-[30px]">
          <BasicInfoCard
            isEditing={isModuleEditing('basic-info')}
            onEdit={() => handleEdit('basic-info')}
            onSave={handleSave}
            onCancel={handleCancel}
            onAIPolishModule={handleAIPolishModule}
            onAIPolishField={handleAIPolishField}
            isPolishing={state.isPolishing}
            saveStatus={isModuleEditing('basic-info') ? state.saveStatus : 'idle'}
          />
          <CandidateSummaryCard
            isEditing={isModuleEditing('candidate-summary')}
            onEdit={() => handleEdit('candidate-summary')}
            onSave={handleSave}
            onCancel={handleCancel}
            onAIPolishModule={handleAIPolishModule}
            onAIPolishField={handleAIPolishField}
            isPolishing={state.isPolishing}
            saveStatus={isModuleEditing('candidate-summary') ? state.saveStatus : 'idle'}
          />
          <MatchAnalysisCard
            isEditing={isModuleEditing('match-analysis')}
            onEdit={() => handleEdit('match-analysis')}
            onSave={handleSave}
            onCancel={handleCancel}
            onAIPolishModule={handleAIPolishModule}
            onAIPolishField={handleAIPolishField}
            isPolishing={state.isPolishing}
            saveStatus={isModuleEditing('match-analysis') ? state.saveStatus : 'idle'}
          />
          <GapAnalysisCard
            isEditing={isModuleEditing('gap-analysis')}
            onEdit={() => handleEdit('gap-analysis')}
            onSave={handleSave}
            onCancel={handleCancel}
            onAIPolishModule={handleAIPolishModule}
            onAIPolishField={handleAIPolishField}
            isPolishing={state.isPolishing}
            saveStatus={isModuleEditing('gap-analysis') ? state.saveStatus : 'idle'}
          />
          <CareerPathCard
            isEditing={isModuleEditing('career-path')}
            onEdit={() => handleEdit('career-path')}
            onSave={handleSave}
            onCancel={handleCancel}
            onAIPolishModule={handleAIPolishModule}
            onAIPolishField={handleAIPolishField}
            isPolishing={state.isPolishing}
            saveStatus={isModuleEditing('career-path') ? state.saveStatus : 'idle'}
          />
          <DevelopmentPlanCard
            isEditing={isModuleEditing('development-plan')}
            onEdit={() => handleEdit('development-plan')}
            onSave={handleSave}
            onCancel={handleCancel}
            onAIPolishModule={handleAIPolishModule}
            onAIPolishField={handleAIPolishField}
            isPolishing={state.isPolishing}
            saveStatus={isModuleEditing('development-plan') ? state.saveStatus : 'idle'}
          />
          <ActionPlanCard
            isEditing={isModuleEditing('action-plan')}
            onEdit={() => handleEdit('action-plan')}
            onSave={handleSave}
            onCancel={handleCancel}
            onAIPolishModule={handleAIPolishModule}
            onAIPolishField={handleAIPolishField}
            isPolishing={state.isPolishing}
            saveStatus={isModuleEditing('action-plan') ? state.saveStatus : 'idle'}
          />
          <FinalRecommendationCard
            isEditing={isModuleEditing('final-recommendation')}
            onEdit={() => handleEdit('final-recommendation')}
            onSave={handleSave}
            onCancel={handleCancel}
            onAIPolishModule={handleAIPolishModule}
            onAIPolishField={handleAIPolishField}
            isPolishing={state.isPolishing}
            saveStatus={isModuleEditing('final-recommendation') ? state.saveStatus : 'idle'}
          />
        </div>
      </main>

      {/* AI Polishing Modal */}
      <AIPolishModal
        isOpen={showAIPolishModal}
        settings={polishSettings}
        onSettingsChange={setPolishSettings}
        onStart={handleStartPolish}
        onCancel={() => setShowAIPolishModal(false)}
        isPolishing={state.isPolishing}
      />

      {/* AI Polish Compare Panel */}
      {state.polishResult && (
        <AIPolishComparePanel
          isOpen={state.showPolishCompare}
          result={state.polishResult}
          onApplyAll={handleApplyAll}
          onApplyPartial={handleApplyPartial}
          onApplySingle={handleApplySingle}
          onDiscard={handleDiscard}
        />
      )}
    </div>
  );
}

export default function CareerReport() {
  return (
    <ReportProvider>
      <ReportContent />
    </ReportProvider>
  );
}