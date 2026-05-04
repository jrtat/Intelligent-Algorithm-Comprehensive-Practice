import api from './client.ts';
import type {
  ResumeData,
  TaskAcceptedResponse,
  TaskStatusResponse,
  ErrorResponse,
} from '../types/job.ts';

/**
 * 提交简历数据进行处理
 * POST /api/resume/process 后端功能接口
 * 返回 202 Accepted，带 taskId
 */
export const submitResume = async (
  resumeData: ResumeData
): Promise<TaskAcceptedResponse> => {
  const response = await api.post<TaskAcceptedResponse>(
    '/resume/process',
    resumeData
  );
  return response.data;
};

/**
 * 轮询任务状态
 * GET /api/task/{taskId}
 */
export const getTaskStatus = async (
  taskId: string
): Promise<TaskStatusResponse> => {
  const response = await api.get<TaskStatusResponse>(`/task/${taskId}`);
  return response.data;
};

/**
 * 轮询配置
 */
const POLL_CONFIG = {
  initialDelay: 2000,    // 初始间隔 2 秒
  maxDelay: 5000,        // 最大间隔 5 秒
  maxAttempts: 1440,      // 最大轮询次数（120 分钟）
  timeoutMs: 7200000,     // 120 分钟超时
};

export interface PollCallbacks {
  onProgress?: (progress: number) => void;
  onCompleted?: (result: TaskStatusResponse['result']) => void;
  onFailed?: (error: string) => void;
  onTimeout?: () => void;
}

/**
 * 处理简历并轮询结果
 * @param resumeData - 简历数据
 * @param callbacks - 回调函数
 * @returns Promise resolving to JobData result
 */
export const processResume = async (
  resumeData: ResumeData,
  callbacks?: PollCallbacks
): Promise<TaskStatusResponse['result']> => {
  const startTime = Date.now();
  let currentDelay = POLL_CONFIG.initialDelay;
  let attempts = 0;

  // Step 1: 提交简历
  callbacks?.onProgress?.(0);

  let acceptedResponse: TaskAcceptedResponse;
  try {
    acceptedResponse = await submitResume(resumeData);
  } catch (error: any) {
    const errorResponse = error.response?.data as ErrorResponse;
    callbacks?.onFailed?.(errorResponse?.message || '提交简历失败');
    throw error;
  }

  const { taskId } = acceptedResponse;
  callbacks?.onProgress?.(5);

  // Step 2: 轮询任务状态
  while (attempts < POLL_CONFIG.maxAttempts) {
    // 检查超时
    if (Date.now() - startTime > POLL_CONFIG.timeoutMs) {
      callbacks?.onTimeout?.();
      throw new Error('任务处理超时（120分钟）');
    }

    // 等待间隔
    await new Promise((resolve) => setTimeout(resolve, currentDelay));
    attempts++;

    // 获取状态
    let statusResponse: TaskStatusResponse;
    try {
      statusResponse = await getTaskStatus(taskId);
    } catch (error: any) {
      console.error('轮询失败:', error);
      // 轮询失败，继续重试
      currentDelay = Math.min(currentDelay + 500, POLL_CONFIG.maxDelay);
      continue;
    }

    const { status, progress, result, error } = statusResponse;

    // 更新进度（粗略估算）
    if (progress !== undefined) {
      callbacks?.onProgress?.(progress);
    } else if (status === 'processing') {
      const estimatedProgress = Math.min(5 + attempts * 2, 95);
      callbacks?.onProgress?.(estimatedProgress);
    }

    // 检查状态
    if (status === 'completed') {
      callbacks?.onProgress?.(100);
      callbacks?.onCompleted?.(result);
      return result!;
    }

    if (status === 'failed') {
      callbacks?.onFailed?.(error || '任务处理失败');
      throw new Error(error || '任务处理失败');
    }

    // pending 或 processing，继续轮询
    // 动态调整间隔：初始 2 秒，逐步递增到 5 秒
    currentDelay = Math.min(currentDelay + 300, POLL_CONFIG.maxDelay);
  }

  // 达到最大轮询次数
  callbacks?.onTimeout?.();
  throw new Error('达到最大轮询次数，任务处理未完成');
};

/**
 * 取消进行中的轮询（需要外部维护 AbortController）
 */
export const createAbortController = (): AbortController => new AbortController();

