import { createContext, useContext, useReducer, useEffect, useCallback, useState, useRef } from 'react';
import type { Dispatch, ReactNode } from 'react';
import type { Report } from '../../../types/job';
import type { PolishResult } from '../components/ui/AIPolishUtils';
import { getReport } from '../../../api/reportApi';

export type NoDataReason = 'no_resume' | 'no_job_matched' | 'no_report';

interface ReportState {
  report: Report | null;
  isLoading: boolean;
  noDataReason: NoDataReason | null;
  sidebarCollapsed: boolean;
  activeSection: string;
  editingModule: string | null;
  aiPolishingModule: string | null;
  saveStatus: 'idle' | 'saving' | 'saved' | 'error';
  hasUnsavedChanges: boolean;
  validationErrors: Record<string, string>;
  showCacheRestored: boolean;
  // AI Polish state
  isPolishing: boolean;
  polishResult: PolishResult | null;
  showPolishCompare: boolean;
  polishError: string | null;
  polishSuccess: string | null;
  // Print state
  isPrinting: boolean;
}

type ReportAction =
  | { type: 'SET_REPORT'; payload: Report }
  | { type: 'UPDATE_REPORT'; payload: Partial<Report> }
  | { type: 'UPDATE_NESTED_FIELD'; payload: { path: string[]; value: any } }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'TOGGLE_SIDEBAR' }
  | { type: 'SET_ACTIVE_SECTION'; payload: string }
  | { type: 'SET_EDITING_MODULE'; payload: string | null }
  | { type: 'SET_AI_POLISHING_MODULE'; payload: string | null }
  | { type: 'SET_SAVE_STATUS'; payload: 'idle' | 'saving' | 'saved' | 'error' }
  | { type: 'SET_UNSAVED_CHANGES'; payload: boolean }
  | { type: 'SET_VALIDATION_ERRORS'; payload: Record<string, string> }
  | { type: 'CLEAR_VALIDATION_ERROR'; payload: string }
  | { type: 'SHOW_CACHE_RESTORED'; payload: boolean }
  | { type: 'SET_POLISHING'; payload: boolean }
  | { type: 'SET_POLISH_RESULT'; payload: PolishResult | null }
  | { type: 'SET_SHOW_POLISH_COMPARE'; payload: boolean }
  | { type: 'SET_POLISH_ERROR'; payload: string | null }
  | { type: 'SET_POLISH_SUCCESS'; payload: string | null }
  | { type: 'CLEAR_POLISH_STATE' }
  | { type: 'SET_NO_DATA_REASON'; payload: NoDataReason | null }
  | { type: 'SET_PRINTING'; payload: boolean };

const initialState: ReportState = {
  report: null,
  isLoading: true,
  noDataReason: null,
  sidebarCollapsed: false,
  activeSection: 'basic-info',
  editingModule: null,
  aiPolishingModule: null,
  saveStatus: 'idle',
  hasUnsavedChanges: false,
  validationErrors: {},
  showCacheRestored: false,
  isPolishing: false,
  polishResult: null,
  showPolishCompare: false,
  polishError: null,
  polishSuccess: null,
  isPrinting: false,
};

function reportReducer(state: ReportState, action: ReportAction): ReportState {
  switch (action.type) {
    case 'SET_REPORT':
      return { ...state, report: action.payload, isLoading: false };
    case 'UPDATE_REPORT':
      return state.report
        ? { ...state, report: { ...state.report, ...action.payload } }
        : state;
    case 'UPDATE_NESTED_FIELD': {
      if (!state.report) return state;
      const newReport = JSON.parse(JSON.stringify(state.report));
      let current: any = newReport;
      for (let i = 0; i < action.payload.path.length - 1; i++) {
        current = current[action.payload.path[i]];
      }
      current[action.payload.path[action.payload.path.length - 1]] = action.payload.value;
      return { ...state, report: newReport };
    }
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'TOGGLE_SIDEBAR':
      return { ...state, sidebarCollapsed: !state.sidebarCollapsed };
    case 'SET_ACTIVE_SECTION':
      return { ...state, activeSection: action.payload };
    case 'SET_EDITING_MODULE':
      return { ...state, editingModule: action.payload };
    case 'SET_AI_POLISHING_MODULE':
      return { ...state, aiPolishingModule: action.payload };
    case 'SET_SAVE_STATUS':
      return { ...state, saveStatus: action.payload };
    case 'SET_UNSAVED_CHANGES':
      return { ...state, hasUnsavedChanges: action.payload };
    case 'SET_VALIDATION_ERRORS':
      return { ...state, validationErrors: action.payload };
    case 'CLEAR_VALIDATION_ERROR': {
      const newErrors = { ...state.validationErrors };
      delete newErrors[action.payload];
      return { ...state, validationErrors: newErrors };
    }
    case 'SHOW_CACHE_RESTORED':
      return { ...state, showCacheRestored: action.payload };
    case 'SET_POLISHING':
      return { ...state, isPolishing: action.payload };
    case 'SET_POLISH_RESULT':
      return { ...state, polishResult: action.payload };
    case 'SET_SHOW_POLISH_COMPARE':
      return { ...state, showPolishCompare: action.payload };
    case 'SET_POLISH_ERROR':
      return { ...state, polishError: action.payload };
    case 'SET_POLISH_SUCCESS':
      return { ...state, polishSuccess: action.payload };
    case 'CLEAR_POLISH_STATE':
      return { ...state, isPolishing: false, polishResult: null, showPolishCompare: false, polishError: null, polishSuccess: null };
    case 'SET_NO_DATA_REASON':
      return { ...state, noDataReason: action.payload, isLoading: false };
    case 'SET_PRINTING':
      return { ...state, isPrinting: action.payload };
    default:
      return state;
  }
}

interface ValidationRule {
  required?: boolean;
  pattern?: RegExp;
  maxLength?: number;
  minLength?: number;
  max?: number;
  min?: number;
  custom?: (value: any) => string | null;
}

interface FieldValidation {
  [key: string]: ValidationRule;
}

const VALIDATION_RULES: FieldValidation = {
  candidate_name: { required: true, maxLength: 50 },
  target_job: { required: true, maxLength: 100 },
  current_background: { maxLength: 2000 },
  skill: { required: true, maxLength: 100 },
  milestone_name: { required: true, maxLength: 100 },
  deadline: { pattern: /^\d{4}-\d{2}(-\d{2})?$/ },
  duration: { pattern: /^\d+-\d+个月$/ },
  score: { min: 0, max: 100 },
  probability_percentage: { min: 0, max: 100 },
};

export function validateField(path: string, value: any): string | null {
  const key = path.split('.').pop() || '';
  const rules = VALIDATION_RULES[key];

  if (!rules) return null;

  if (rules.required) {
    if (value === undefined || value === null || value === '' || (typeof value === 'string' && !value.trim())) {
      return '请填写该内容';
    }
  }

  if (rules.maxLength && typeof value === 'string' && value.length > rules.maxLength) {
    return `内容过长，请控制在${rules.maxLength}字以内`;
  }

  if (rules.minLength && typeof value === 'string' && value.length < rules.minLength) {
    return `内容过短，至少${rules.minLength}字`;
  }

  if (rules.pattern && typeof value === 'string' && value) {
    if (!rules.pattern.test(value)) {
      if (key === 'deadline') return '请按格式输入（如2026-06）';
      if (key === 'duration') return '请按格式输入（如1-6个月）';
      return '格式不正确';
    }
  }

  if ((rules.max !== undefined || rules.min !== undefined) && typeof value === 'number') {
    if (rules.max !== undefined && value > rules.max) {
      return `数值不能超过${rules.max}`;
    }
    if (rules.min !== undefined && value < rules.min) {
      return `数值不能小于${rules.min}`;
    }
  }

  if (rules.custom) {
    return rules.custom(value);
  }

  return null;
}

interface EditRecord {
  timestamp: number;
  moduleId: string;
  data: Partial<Report>;
}

interface ReportContextType {
  state: ReportState;
  dispatch: Dispatch<ReportAction>;
  loadReport: () => void;
  updateReport: (updates: Partial<Report>) => void;
  updateNestedField: (path: string[], value: any) => void;
  saveReport: () => void;
  scrollToSection: (sectionId: string) => void;
  startEditing: (moduleId: string) => void;
  cancelEditing: () => void;
  validateField: (path: string, value: any) => string | null;
  validateAll: (fields: { path: string; value: any }[]) => boolean;
  clearCache: () => void;
  getCacheRecords: () => EditRecord[];
  // AI Polish methods
  setPolishing: (polishing: boolean) => void;
  setPolishResult: (result: PolishResult | null) => void;
  setShowPolishCompare: (show: boolean) => void;
  setPolishError: (error: string | null) => void;
  setPolishSuccess: (message: string | null) => void;
  clearPolishState: () => void;
  applyPolishResult: (pathsToApply?: string[]) => void;
  setPrinting: (printing: boolean) => void;
}

const ReportContext = createContext<ReportContextType | null>(null);

const STORAGE_KEY = 'careerReport';
const CACHE_HISTORY_KEY = 'careerReportHistory';
const MAX_CACHE_RECORDS = 10;

export function ReportProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reportReducer, initialState);
  const [initialized, setInitialized] = useState(false);
  const originalDataRef = useRef<Partial<Report>>({});

  const loadReport = useCallback(async () => {
    dispatch({ type: 'SET_LOADING', payload: true });

    const cached = localStorage.getItem(STORAGE_KEY);
    if (cached) {
      try {
        const parsed = JSON.parse(cached);
        dispatch({ type: 'SET_REPORT', payload: parsed });
        setInitialized(true);

        const history = localStorage.getItem(CACHE_HISTORY_KEY);
        if (history) {
          const records: EditRecord[] = JSON.parse(history);
          if (records.length > 0) {
            dispatch({ type: 'SHOW_CACHE_RESTORED', payload: true });
            setTimeout(() => {
              dispatch({ type: 'SHOW_CACHE_RESTORED', payload: false });
            }, 3000);
          }
        }
        return;
      } catch {
        // Invalid cache
      }
    }

    // 尝试从后端获取报告
    const taskId = localStorage.getItem('reportTaskId');
    if (taskId) {
      try {
        const report = await getReport(taskId);
        dispatch({ type: 'SET_REPORT', payload: report });
        localStorage.setItem(STORAGE_KEY, JSON.stringify(report));
        setInitialized(true);
        // 清除历史缓存，避免旧报告影响
        localStorage.removeItem(CACHE_HISTORY_KEY);
        return;
      } catch (error) {
        console.error('从后端获取报告失败:', error);
        // 后端获取失败时，检查本地是否有简历数据
        const resumeData = localStorage.getItem('resumeData');
        if (!resumeData) {
          dispatch({ type: 'SET_NO_DATA_REASON', payload: 'no_resume' });
          setInitialized(true);
          return;
        }
        // 有简历但没有报告，检查是否有匹配结果
        const matchResult = localStorage.getItem('matchResult');
        if (!matchResult) {
          dispatch({ type: 'SET_NO_DATA_REASON', payload: 'no_job_matched' });
          setInitialized(true);
          return;
        }
        // 有简历和匹配结果但没有报告
        dispatch({ type: 'SET_NO_DATA_REASON', payload: 'no_report' });
        setInitialized(true);
        return;
      }
    }

    // 检查简历数据
    const resumeData = localStorage.getItem('resumeData');
    if (!resumeData) {
      dispatch({ type: 'SET_NO_DATA_REASON', payload: 'no_resume' });
      setInitialized(true);
      return;
    }

    // 有简历但没有岗位匹配结果
    const matchResult = localStorage.getItem('matchResult');
    if (!matchResult) {
      dispatch({ type: 'SET_NO_DATA_REASON', payload: 'no_job_matched' });
      setInitialized(true);
      return;
    }

    // 有简历和匹配结果但没有报告
    dispatch({ type: 'SET_NO_DATA_REASON', payload: 'no_report' });
    setInitialized(true);
  }, []);

  const updateReport = useCallback((updates: Partial<Report>) => {
    dispatch({ type: 'UPDATE_REPORT', payload: updates });
    dispatch({ type: 'SET_UNSAVED_CHANGES', payload: true });
    dispatch({ type: 'SET_SAVE_STATUS', payload: 'saving' });
  }, []);

  const updateNestedField = useCallback((path: string[], value: any) => {
    dispatch({ type: 'UPDATE_NESTED_FIELD', payload: { path, value } });
    dispatch({ type: 'SET_UNSAVED_CHANGES', payload: true });
    dispatch({ type: 'SET_SAVE_STATUS', payload: 'saving' });
  }, []);

  const saveReport = useCallback(() => {
    if (!state.report) return;

    dispatch({ type: 'SET_SAVE_STATUS', payload: 'saving' });

    try {
      // Save current state
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.report));

      // Update cache history
      const historyStr = localStorage.getItem(CACHE_HISTORY_KEY);
      const history: EditRecord[] = historyStr ? JSON.parse(historyStr) : [];

      const newRecord: EditRecord = {
        timestamp: Date.now(),
        moduleId: state.editingModule || 'unknown',
        data: JSON.parse(JSON.stringify(state.report)),
      };

      history.push(newRecord);

      // Keep only last MAX_CACHE_RECORDS
      if (history.length > MAX_CACHE_RECORDS) {
        history.splice(0, history.length - MAX_CACHE_RECORDS);
      }

      localStorage.setItem(CACHE_HISTORY_KEY, JSON.stringify(history));

      dispatch({ type: 'SET_SAVE_STATUS', payload: 'saved' });
      dispatch({ type: 'SET_UNSAVED_CHANGES', payload: false });
      dispatch({ type: 'SET_EDITING_MODULE', payload: null });

      setTimeout(() => {
        dispatch({ type: 'SET_SAVE_STATUS', payload: 'idle' });
      }, 2000);
    } catch {
      dispatch({ type: 'SET_SAVE_STATUS', payload: 'error' });
    }
  }, [state.report, state.editingModule]);

  const scrollToSection = useCallback((sectionId: string) => {
    const element = document.getElementById(`section-${sectionId}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      dispatch({ type: 'SET_ACTIVE_SECTION', payload: sectionId });
    }
  }, []);

  const startEditing = useCallback((moduleId: string) => {
    originalDataRef.current = JSON.parse(JSON.stringify(state.report));
    dispatch({ type: 'SET_EDITING_MODULE', payload: moduleId });
  }, [state.report]);

  const cancelEditing = useCallback(() => {
    if (state.hasUnsavedChanges && originalDataRef.current) {
      if (window.confirm('修改未保存，是否放弃？')) {
        dispatch({ type: 'UPDATE_REPORT', payload: originalDataRef.current as Partial<Report> });
        dispatch({ type: 'SET_EDITING_MODULE', payload: null });
        dispatch({ type: 'SET_UNSAVED_CHANGES', payload: false });
      }
    } else {
      dispatch({ type: 'SET_EDITING_MODULE', payload: null });
    }
  }, [state.hasUnsavedChanges]);

  const validateAll = useCallback((fields: { path: string; value: any }[]): boolean => {
    const errors: Record<string, string> = {};
    let isValid = true;

    fields.forEach(({ path, value }) => {
      const error = validateField(path, value);
      if (error) {
        errors[path] = error;
        isValid = false;
      }
    });

    dispatch({ type: 'SET_VALIDATION_ERRORS', payload: errors });
    return isValid;
  }, []);

  const clearCache = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(CACHE_HISTORY_KEY);
  }, []);

  const getCacheRecords = useCallback((): EditRecord[] => {
    const historyStr = localStorage.getItem(CACHE_HISTORY_KEY);
    return historyStr ? JSON.parse(historyStr) : [];
  }, []);

  // AI Polish methods
  const setPolishing = useCallback((polishing: boolean) => {
    dispatch({ type: 'SET_POLISHING', payload: polishing });
  }, []);

  const setPolishResult = useCallback((result: PolishResult | null) => {
    dispatch({ type: 'SET_POLISH_RESULT', payload: result });
  }, []);

  const setShowPolishCompare = useCallback((show: boolean) => {
    dispatch({ type: 'SET_SHOW_POLISH_COMPARE', payload: show });
  }, []);

  const setPolishError = useCallback((error: string | null) => {
    dispatch({ type: 'SET_POLISH_ERROR', payload: error });
    if (error) {
      setTimeout(() => {
        dispatch({ type: 'SET_POLISH_ERROR', payload: null });
      }, 3000);
    }
  }, []);

  const setPolishSuccess = useCallback((message: string | null) => {
    dispatch({ type: 'SET_POLISH_SUCCESS', payload: message });
    if (message) {
      setTimeout(() => {
        dispatch({ type: 'SET_POLISH_SUCCESS', payload: null });
      }, 3000);
    }
  }, []);

  const clearPolishState = useCallback(() => {
    dispatch({ type: 'CLEAR_POLISH_STATE' });
  }, []);

  const setPrinting = useCallback((printing: boolean) => {
    dispatch({ type: 'SET_PRINTING', payload: printing });
  }, []);

  const applyPolishResult = useCallback((pathsToApply?: string[]) => {
    if (!state.polishResult || !state.report) return;

    const { polished } = state.polishResult;

    if (pathsToApply && pathsToApply.length > 0) {
      // Apply only selected paths
      const pathSet = new Set(pathsToApply);
      const result = JSON.parse(JSON.stringify(state.report)) as Report;

      function applyPath(obj: any, polishedObj: any, pathParts: string[]) {
        if (pathParts.length === 0) return;
        const currentKey = pathParts[0];

        if (pathParts.length === 1) {
          if (pathSet.has(pathParts.join('.'))) {
            obj[currentKey] = polishedObj[currentKey];
          }
          return;
        }

        if (obj[currentKey] !== undefined && polishedObj[currentKey] !== undefined) {
          applyPath(obj[currentKey], polishedObj[currentKey], pathParts.slice(1));
        }
      }

      const polishedJson = polished as any;
      for (const path of pathSet) {
        const pathParts = path.split('.');
        applyPath(result, polishedJson, pathParts);
      }

      dispatch({ type: 'UPDATE_REPORT', payload: result });
    } else {
      // Apply all
      dispatch({ type: 'UPDATE_REPORT', payload: polished });
    }

    dispatch({ type: 'SET_UNSAVED_CHANGES', payload: true });
    dispatch({ type: 'SET_SAVE_STATUS', payload: 'saving' });
    dispatch({ type: 'CLEAR_POLISH_STATE' });
  }, [state.polishResult, state.report]);

  // Auto-save on changes (debounced)
  useEffect(() => {
    if (!initialized || !state.report) return;

    if (state.saveStatus === 'saving' && state.hasUnsavedChanges) {
      const timer = setTimeout(() => {
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(state.report));
          dispatch({ type: 'SET_SAVE_STATUS', payload: 'saved' });

          // Update history
          const historyStr = localStorage.getItem(CACHE_HISTORY_KEY);
          const history: EditRecord[] = historyStr ? JSON.parse(historyStr) : [];
          history.push({
            timestamp: Date.now(),
            moduleId: state.editingModule || 'unknown',
            data: JSON.parse(JSON.stringify(state.report)),
          });
          if (history.length > MAX_CACHE_RECORDS) {
            history.splice(0, history.length - MAX_CACHE_RECORDS);
          }
          localStorage.setItem(CACHE_HISTORY_KEY, JSON.stringify(history));

          setTimeout(() => {
            if (state.saveStatus === 'saved') {
              dispatch({ type: 'SET_SAVE_STATUS', payload: 'idle' });
            }
          }, 2000);
        } catch {
          dispatch({ type: 'SET_SAVE_STATUS', payload: 'error' });
        }
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [state.report, state.saveStatus, state.hasUnsavedChanges, initialized, state.editingModule]);

  // Warn on unsaved changes before unload
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (state.hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [state.hasUnsavedChanges]);

  // Initial load
  useEffect(() => {
    loadReport().catch(console.error);
  }, [loadReport]);

  return (
    <ReportContext.Provider
      value={{
        state,
        dispatch,
        loadReport,
        updateReport,
        updateNestedField,
        saveReport,
        scrollToSection,
        startEditing,
        cancelEditing,
        validateField,
        validateAll,
        clearCache,
        getCacheRecords,
        setPolishing,
        setPolishResult,
        setShowPolishCompare,
        setPolishError,
        setPolishSuccess,
        clearPolishState,
        applyPolishResult,
        setPrinting,
      }}
    >
      {children}
    </ReportContext.Provider>
  );
}

export function useReport() {
  const context = useContext(ReportContext);
  if (!context) {
    throw new Error('useReport must be used within a ReportProvider');
  }
  return context;
}
