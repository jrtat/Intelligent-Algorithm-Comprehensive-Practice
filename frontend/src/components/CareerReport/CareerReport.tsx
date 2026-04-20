import { useState, useEffect } from 'react';
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
import './CareerReport.css';

function ReportContent() {
  const { state, startEditing, cancelEditing, saveReport } = useReport();
  const [showAIPolishModal, setShowAIPolishModal] = useState(false);
  const [editingModuleId, setEditingModuleId] = useState<string | null>(null);

  useEffect(() => {
    setEditingModuleId(state.editingModule);
  }, [state.editingModule]);

  if (state.isLoading) {
    return (
      <div className="career-report" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="loading-spinner" style={{ width: 40, height: 40 }} />
      </div>
    );
  }

  if (!state.report) {
    return (
      <div className="career-report" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p>暂无报告数据</p>
      </div>
    );
  }

  const handleEdit = (moduleId: string) => {
    setEditingModuleId(moduleId);
    startEditing(moduleId);
  };

  const handleSave = () => {
    saveReport();
    setEditingModuleId(null);
  };

  const handleCancel = () => {
    cancelEditing();
    setEditingModuleId(null);
  };

  const handleAIPolish = () => {
    setShowAIPolishModal(true);
  };

  const handleExportPDF = () => {
    window.print();
  };

  const isModuleEditing = (moduleId: string) => editingModuleId === moduleId;

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

      <ReportHeader onAIPolish={handleAIPolish} onExportPDF={handleExportPDF} />
      <ReportSidebar />

      <main className="report-main">
        <div className="report-content" id="report-content">
          <BasicInfoCard
            isEditing={isModuleEditing('basic-info')}
            onEdit={() => handleEdit('basic-info')}
            onSave={handleSave}
            onCancel={handleCancel}
            onAIPolish={handleAIPolish}
            saveStatus={isModuleEditing('basic-info') ? state.saveStatus : 'idle'}
          />
          <CandidateSummaryCard
            isEditing={isModuleEditing('candidate-summary')}
            onEdit={() => handleEdit('candidate-summary')}
            onSave={handleSave}
            onCancel={handleCancel}
            onAIPolish={handleAIPolish}
            saveStatus={isModuleEditing('candidate-summary') ? state.saveStatus : 'idle'}
          />
          <MatchAnalysisCard
            isEditing={isModuleEditing('match-analysis')}
            onEdit={() => handleEdit('match-analysis')}
            onSave={handleSave}
            onCancel={handleCancel}
            onAIPolish={handleAIPolish}
            saveStatus={isModuleEditing('match-analysis') ? state.saveStatus : 'idle'}
          />
          <GapAnalysisCard
            isEditing={isModuleEditing('gap-analysis')}
            onEdit={() => handleEdit('gap-analysis')}
            onSave={handleSave}
            onCancel={handleCancel}
            onAIPolish={handleAIPolish}
            saveStatus={isModuleEditing('gap-analysis') ? state.saveStatus : 'idle'}
          />
          <CareerPathCard
            isEditing={isModuleEditing('career-path')}
            onEdit={() => handleEdit('career-path')}
            onSave={handleSave}
            onCancel={handleCancel}
            onAIPolish={handleAIPolish}
            saveStatus={isModuleEditing('career-path') ? state.saveStatus : 'idle'}
          />
          <DevelopmentPlanCard
            isEditing={isModuleEditing('development-plan')}
            onEdit={() => handleEdit('development-plan')}
            onSave={handleSave}
            onCancel={handleCancel}
            onAIPolish={handleAIPolish}
            saveStatus={isModuleEditing('development-plan') ? state.saveStatus : 'idle'}
          />
          <ActionPlanCard
            isEditing={isModuleEditing('action-plan')}
            onEdit={() => handleEdit('action-plan')}
            onSave={handleSave}
            onCancel={handleCancel}
            onAIPolish={handleAIPolish}
            saveStatus={isModuleEditing('action-plan') ? state.saveStatus : 'idle'}
          />
          <FinalRecommendationCard
            isEditing={isModuleEditing('final-recommendation')}
            onEdit={() => handleEdit('final-recommendation')}
            onSave={handleSave}
            onCancel={handleCancel}
            onAIPolish={handleAIPolish}
            saveStatus={isModuleEditing('final-recommendation') ? state.saveStatus : 'idle'}
          />
        </div>
      </main>

      {/* AI Polishing Modal Placeholder */}
      {showAIPolishModal && (
        <div className="modal-overlay" onClick={() => setShowAIPolishModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">AI 润色设置</h3>
              <button className="btn-icon" onClick={() => setShowAIPolishModal(false)}>
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            <p style={{ color: '#666', marginBottom: 16 }}>
              AI 润色功能正在开发中，敬请期待...
            </p>
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setShowAIPolishModal(false)}>
                关闭
              </button>
            </div>
          </div>
        </div>
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
