import api from './client.ts';
import type {
  ResumeData,
  JobData,
  ReportGenInput,
  Report,
  TaskAcceptedResponse,
  TaskStatusResponse,
  ErrorResponse,
} from '../types/job.ts';

/**
 * 提交报告生成任务
 * POST /api/report/generate
 * 返回 202 Accepted，带 taskId
 */
export const submitReport = async (
  input: ReportGenInput
): Promise<TaskAcceptedResponse> => {
  const response = await api.post<TaskAcceptedResponse>(
    '/report/generate',
    input
  );
  return response.data;
};

/**
 * 轮询报告任务状态
 * GET /api/task/{taskId}
 */
export const getReportTaskStatus = async (
  taskId: string
): Promise<TaskStatusResponse> => {
  const response = await api.get<TaskStatusResponse>(`/task/${taskId}`);
  return response.data;
};

/**
 * 轮询配置
 */
const POLL_CONFIG = {
  initialDelay: 2000,
  maxDelay: 5000,
  maxAttempts: 1440,
  timeoutMs: 7200000, // 120分钟
};

export interface ReportPollCallbacks {
  onProgress?: (progress: number) => void;
  onCompleted?: (result: Report, taskId?: string) => void;
  onFailed?: (error: string) => void;
  onTimeout?: () => void;
}

/**
 * 生成专项提升报告并轮询结果
 * @param input - ReportGenInput (resume + job)
 * @param callbacks - 回调函数
 * @returns Promise resolving to Report result
 */
export const processReport = async (
  input: ReportGenInput,
  callbacks?: ReportPollCallbacks
): Promise<Report> => {
  const startTime = Date.now();
  let currentDelay = POLL_CONFIG.initialDelay;
  let attempts = 0;

  callbacks?.onProgress?.(0);

  let acceptedResponse: TaskAcceptedResponse;
  try {
    acceptedResponse = await submitReport(input);
  } catch (error: any) {
    const errorResponse = error.response?.data as ErrorResponse;
    callbacks?.onFailed?.(errorResponse?.message || '提交报告任务失败');
    throw error;
  }

  const { taskId } = acceptedResponse;
  callbacks?.onProgress?.(5);

  while (attempts < POLL_CONFIG.maxAttempts) {
    if (Date.now() - startTime > POLL_CONFIG.timeoutMs) {
      callbacks?.onTimeout?.();
      throw new Error('任务处理超时（120分钟）');
    }

    await new Promise((resolve) => setTimeout(resolve, currentDelay));
    attempts++;

    let statusResponse: TaskStatusResponse;
    try {
      statusResponse = await getReportTaskStatus(taskId);
    } catch (error: any) {
      console.error('轮询失败:', error);
      currentDelay = Math.min(currentDelay + 500, POLL_CONFIG.maxDelay);
      continue;
    }

    const { status, progress, result, error } = statusResponse;

    if (progress !== undefined) {
      callbacks?.onProgress?.(progress);
    } else if (status === 'processing') {
      const estimatedProgress = Math.min(5 + attempts * 2, 95);
      callbacks?.onProgress?.(estimatedProgress);
    }

    if (status === 'completed') {
      callbacks?.onProgress?.(100);
      callbacks?.onCompleted?.(result as unknown as Report, taskId);
      return result as unknown as Report;
    }

    if (status === 'failed') {
      callbacks?.onFailed?.(error || '任务处理失败');
      throw new Error(error || '任务处理失败');
    }

    currentDelay = Math.min(currentDelay + 300, POLL_CONFIG.maxDelay);
  }

  callbacks?.onTimeout?.();
  throw new Error('达到最大轮询次数，任务处理未完成');
};

/**
 * 获取已生成的报告
 * GET /api/report/{task_id}
 */
export const getReport = async (taskId: string): Promise<Report> => {
  const response = await api.get<Report>(`/report/${taskId}`);
  return response.data;
};

/**
 * 取消进行中的轮询
 */
export const createReportAbortController = (): AbortController => new AbortController();