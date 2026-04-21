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
import './CareerReport.css';

function ReportContent() {
  const navigate = useNavigate();
  const { state, saveReport, setPolishing, setPolishResult, setShowPolishCompare, setPolishError, setPolishSuccess, clearPolishState, applyPolishResult } = useReport();

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

    // Simulate progress for UX
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
    window.print();
  };

  const isModuleEditing = (moduleId: string) => editingModuleId === moduleId;

  // 无数据提示
  if (state.noDataReason) {
    const messages = {
      no_resume: {
        title: '请先上传简历',
        description: '在能力分析页面填写您的简历信息，然后进行岗位匹配',
        buttonText: '前往上传简历',
        buttonLink: '/capability-analysis',
      },
      no_job_matched: {
        title: '请先进行岗位匹配',
        description: '在岗位匹配页面选择心仪的岗位，生成深度解析报告',
        buttonText: '前往岗位匹配',
        buttonLink: '/job-match',
      },
      no_report: {
        title: '请生成职业报告',
        description: '在岗位深度解析页面点击"获取专项提升报告"',
        buttonText: '前往深度解析',
        buttonLink: '/job-match',
      },
    };

    const msg = messages[state.noDataReason];

    return (
      <div className="career-report">
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '70vh',
          padding: '40px 20px',
          textAlign: 'center',
        }}>
          <div style={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: 24,
          }}>
            <span className="material-symbols-outlined" style={{ fontSize: 40, color: 'white' }}>
              description
            </span>
          </div>
          <h2 style={{ fontSize: 24, fontWeight: 'bold', color: '#333', marginBottom: 12 }}>
            {msg.title}
          </h2>
          <p style={{ fontSize: 16, color: '#666', marginBottom: 32, maxWidth: 400 }}>
            {msg.description}
          </p>
          <button
            onClick={() => navigate(msg.buttonLink)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              padding: '12px 32px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              borderRadius: 8,
              border: 'none',
              fontWeight: 'bold',
              fontSize: 14,
              cursor: 'pointer',
            }}
          >
            {msg.buttonText}
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
              arrow_forward
            </span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="career-report">
      {/* Cache restored notification */}
      {state.showCacheRestored && (
        <div className="cache-notification">
          <span className="material-symbols-outlined" style={{ fontSize: 16, marginRight: 8 }}>
            restore
          </span>
          已加载上次编辑内容
        </div>
      )}

      {/* Polish success notification */}
      {state.polishSuccess && (
        <div className="polish-notification success">
          <span className="material-symbols-outlined" style={{ fontSize: 16, marginRight: 8 }}>
            check_circle
          </span>
          {state.polishSuccess}
        </div>
      )}

      {/* Polish error notification */}
      {state.polishError && (
        <div className="polish-notification error">
          <span className="material-symbols-outlined" style={{ fontSize: 16, marginRight: 8 }}>
            error
          </span>
          {state.polishError}
        </div>
      )}

      {/* Global progress bar */}
      {state.isPolishing && (
        <div className="polish-progress-bar">
          <div className="polish-progress-fill" style={{ width: `${polishProgress}%` }} />
        </div>
      )}

      <ReportHeader onAIPolish={handleAIPolishGlobal} onExportPDF={handleExportPDF} />
      <ReportSidebar />

      <main className="report-main">
        <div className="report-content" id="report-content">
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