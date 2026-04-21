import type { Report } from '../../../../types/job';
import type { PolishSettings, PolishStyle, PolishIntensity } from './AIPolishModal';

const API_KEY = import.meta.env.VITE_ALIYUN_BAILIAN_API_KEY;
const API_URL = import.meta.env.VITE_ALIYUN_BAILIAN_API_URL || 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions';
const MODEL = import.meta.env.VITE_ALIYUN_BAILIAN_MODEL || 'qwen-plus';

const GLOBAL_REPORT_POLISH_PROMPT = `你是一名专业的人力资源发展顾问和职业报告润色专家。请对用户提供的完整职业发展报告（JSON 格式）进行全局润色。你的任务是在不改变任何核心信息与数据结构的前提下，提升整篇报告的语言质量、专业性和可读性。

### 润色规则（必须严格遵守）
1. **绝对不修改任何核心信息**
   - 不修改姓名、目标岗位、所有得分（包括 match_score、overall_match_score、probability_percentage 等）、百分比、等级（如 match_level）。
   - 不修改阶段名称、时长（duration）、目标值（target_value）、衡量方法（measurement_method）、里程碑（milestones）、成功标准（success_criteria）、风险项（major_risks）等。
   - 不新增、不删除、不合并任何结构字段，不改变数组元素的数量。

2. **只润色以下内容**
   - 所有描述性文本（如 current_background、goal_description、social_demand、technology_trends 等）
   - 总结性语句（如 core_strengths、areas_for_improvement 中的每条说明）
   - 分析类文字（如 gap_analysis 中的 skill、importance、current_level、target_level 描述）
   - 行动计划与规划描述（如 actions、learning_path.courses、practice_arrangements.projects 等）
   - 建议类、说明类文字（如 improvement_suggestions、final_recommendation、mitigation_strategies 等）

3. **润色风格要求**
   - 正式、专业、商务、严谨
   - 语句通顺、逻辑清晰、表达精炼
   - 符合职业发展报告或咨询报告的官方文风
   - 去掉口语化、啰嗦、重复、模糊的表达（例如将"可能大概也许"改为"可能"；"做的东西"改为"负责的工作"）

4. **数组内容（string[]）必须逐条润色**
   - 保持数组元素数量不变
   - 保持每条内容的原意不变，只优化表达

5. **必须保持原有 JSON 结构**
   - 你只能返回**润色后的完整 JSON 对象**
   - 不能返回任何解释、对话、前言、后缀
   - 不能加 Markdown 代码块标记（如 \`\`\`json）
   - 必须是合法可解析的纯 JSON

6. **如果内容为空，保持为空**
   - 空字符串 "" 或空数组 [] 保持不变
   - 数字、布尔值保持不变

请开始润色，直接输出 JSON。`;

const MODULE_POLISH_PROMPT = `你是一名专业的人力资源发展顾问和职业报告润色专家。用户将提供一个完整的职业发展报告（JSON）以及一个**目标模块路径**（如 "candidate_summary"、"match_analysis"、"gap_analysis" 等）。你只需对该模块下的所有文本内容进行润色，其余模块保持原样输出。模块路径可能嵌套（如 "career_path_planning.career_goals.short_term"），你需要精确润色该路径对应的对象或数组。

### 润色规则（必须严格遵守）
1. **绝对不修改任何核心信息**
   - 不修改姓名、目标岗位、任何得分、百分比、等级、阶段、时长、目标值、衡量方法、里程碑、成功标准、风险项等硬数据。
   - 不新增、删除、合并任何结构字段，不改变数组元素数量。

2. **只润色指定模块内的以下内容**
   - 描述性文本、总结性语句、分析类文字、行动计划描述、建议类说明文字。
   - 若模块包含数组（如 core_strengths[]），则逐条润色每个字符串元素。
   - 不润色其他模块的任何内容（即使其他模块中有可优化的文字，也保持原样）。

3. **必须保持原有 JSON 结构**
   - 你只能返回**润色后的完整 JSON 对象**（即整个报告，但只有目标模块被修改）
   - 不能返回任何解释、对话、前言、后缀
   - 不能加 Markdown 代码块标记
   - 必须是合法可解析的纯 JSON

请按照要求润色指定模块，直接输出完整 JSON。`;

const FIELD_POLISH_PROMPT = `你是一名专业的人力资源发展顾问和职业报告润色专家。用户将提供一个完整的职业发展报告（JSON）、一个**目标字段路径**（如 "candidate_summary.current_background" 或 "action_plan.short_term_plan.learning_path.courses[0]"），以及该字段当前的值。你只需对该字段的文本内容进行精准润色，报告中其他所有字段（包括同模块下的其他字段）保持原样输出。

### 润色规则（必须严格遵守）
1. **绝对不修改任何核心信息**
   - 不修改姓名、目标岗位、任何得分、百分比、等级、阶段、时长、目标值、衡量方法、里程碑、成功标准、风险项等硬数据。

2. **只润色指定字段内的文本内容**
   - 该字段必须是字符串类型（string）或字符串数组中的某个元素（string）。
   - 如果是字符串数组中的特定元素，只润色该元素，数组其他元素不变。

3. **必须保持原有 JSON 结构**
   - 你只能返回**润色后的完整 JSON 对象**（整个报告，只有目标字段被修改）
   - 不能返回任何解释、对话、前言、后缀
   - 不能加 Markdown 代码块标记
   - 必须是合法可解析的纯 JSON

请按照要求润色指定字段，直接输出完整 JSON。`;

// Build style and intensity modifiers based on settings
function buildModifierPrompt(style: PolishStyle, intensity: PolishIntensity): string {
  const styleMap: Record<PolishStyle, string> = {
    concise: '简洁专业：语言精炼、用词精准、表达直接',
    formal: '正式商务：措辞严谨、结构规范、语气正式',
    persuasive: '更有说服力：论证有力、逻辑严密、表达有力',
    brief: '更精炼简短：删除冗余、压缩篇幅、保留精华',
  };

  const intensityMap: Record<PolishIntensity, string> = {
    light: '仅修正语句不通顺处，保持原文结构基本不变',
    medium: '适度优化表达，提升专业度，可能调整部分句子结构',
    deep: '深度重组织语言，强化表达效果，可能重新组织段落结构',
  };

  return `润色风格要求：${styleMap[style]}。润色强度：${intensityMap[intensity]}。请根据上述要求进行润色。`;
}

interface PolishAPIResponse {
  success: boolean;
  data?: Report;
  error?: string;
}

async function callPolishAPI(prompt: string, report: Report): Promise<PolishAPIResponse> {
  if (!API_KEY || API_KEY === 'your_api_key_here') {
    return { success: false, error: '请在 .env 文件中配置 VITE_ALIYUN_BAILIAN_API_KEY' };
  }

  let apiUrl = API_URL;
  if (!apiUrl.endsWith('/chat/completions')) {
    apiUrl = apiUrl.replace(/\/$/, '') + '/chat/completions';
  }

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`,
      },
      body: JSON.stringify({
        model: MODEL,
        messages: [
          { role: 'system', content: prompt },
          { role: 'user', content: `请对以下职业报告JSON进行润色，直接输出润色后的完整JSON：\n${JSON.stringify(report)}` },
        ],
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `API Error ${response.status}`);
    }

    const data = await response.json();

    if (data.choices && data.choices[0]) {
      let content = data.choices[0].message.content.trim();

      // Clean markdown wrappers
      if (content.startsWith('```json')) {
        content = content.replace(/^```json\n?/, '');
      }
      if (content.startsWith('```')) {
        content = content.replace(/^```\n?/, '');
      }
      if (content.endsWith('```')) {
        content = content.replace(/\n?```$/, '');
      }

      const polished = JSON.parse(content);
      return { success: true, data: polished };
    }

    return { success: false, error: '无效的API响应格式' };
  } catch (error) {
    console.error('AI Polish API Error:', error);
    return { success: false, error: error instanceof Error ? error.message : '润色服务异常' };
  }
}

function detectChanges(original: any, polished: any, path: string[] = []): Array<{ path: string; before: string; after: string }> {
  const changes: Array<{ path: string; before: string; after: string }> = [];

  if (original === polished) return changes;

  if (typeof original === 'string' && typeof polished === 'string') {
    if (original !== polished) {
      changes.push({ path: path.join('.'), before: original, after: polished });
    }
    return changes;
  }

  if (Array.isArray(original) && Array.isArray(polished)) {
    for (let i = 0; i < Math.max(original.length, polished.length); i++) {
      changes.push(...detectChanges(original[i], polished[i], [...path, String(i)]));
    }
    return changes;
  }

  if (typeof original === 'object' && typeof polished === 'object' && original !== null && polished !== null) {
    const allKeys = new Set([...Object.keys(original), ...Object.keys(polished)]);
    for (const key of allKeys) {
      changes.push(...detectChanges(original[key], polished[key], [...path, key]));
    }
    return changes;
  }

  return changes;
}

export function getTextPaths(report: Report, basePath: string[] = []): string[] {
  const paths: string[] = [];

  const textFields = (obj: any, currentPath: string[]) => {
    if (typeof obj === 'string' && obj.length > 0) {
      paths.push(currentPath.join('.'));
    } else if (Array.isArray(obj)) {
      obj.forEach((item, i) => textFields(item, [...currentPath, String(i)]));
    } else if (typeof obj === 'object' && obj !== null) {
      Object.entries(obj).forEach(([key, value]) => {
        textFields(value, [...currentPath, key]);
      });
    }
  };

  textFields(report, basePath);
  return paths;
}

export interface PolishResult {
  original: Report;
  polished: Report;
  changes: Array<{ path: string; before: string; after: string }>;
}

export async function polishReport(
  report: Report,
  settings: PolishSettings
): Promise<{ success: boolean; result?: PolishResult; error?: string }> {
  let prompt = '';

  switch (settings.scope) {
    case 'global':
      prompt = GLOBAL_REPORT_POLISH_PROMPT + '\n\n' + buildModifierPrompt(settings.style, settings.intensity);
      break;
    case 'module':
      if (!settings.moduleId) {
        return { success: false, error: '缺少模块路径' };
      }
      prompt = MODULE_POLISH_PROMPT + '\n\n' + buildModifierPrompt(settings.style, settings.intensity);
      prompt += `\n\n目标模块路径：${settings.moduleId}`;
      break;
    case 'field':
      if (!settings.fieldPath) {
        return { success: false, error: '缺少字段路径' };
      }
      prompt = FIELD_POLISH_PROMPT + '\n\n' + buildModifierPrompt(settings.style, settings.intensity);
      prompt += `\n\n目标字段路径：${settings.fieldPath}`;
      break;
  }

  const response = await callPolishAPI(prompt, report);

  if (!response.success || !response.data) {
    return { success: false, error: response.error };
  }

  const changes = detectChanges(report, response.data);

  if (changes.length === 0) {
    return { success: true, result: { original: report, polished: response.data, changes: [] } };
  }

  return {
    success: true,
    result: {
      original: report,
      polished: response.data,
      changes,
    },
  };
}

export function applyPolishChanges(
  report: Report,
  polished: Report,
  pathsToApply: string[]
): Report {
  const result = JSON.parse(JSON.stringify(report)) as Report;
  const pathSet = new Set(pathsToApply);

  function applyPath(obj: any, polishedObj: any, pathParts: string[], depth: number = 0) {
    if (pathParts.length === 0) return;

    const currentKey = pathParts[0];

    if (pathParts.length === 1) {
      if (pathSet.has(pathParts.join('.'))) {
        obj[currentKey] = polishedObj[currentKey];
      }
      return;
    }

    if (obj[currentKey] !== undefined && polishedObj[currentKey] !== undefined) {
      applyPath(obj[currentKey], polishedObj[currentKey], pathParts.slice(1), depth + 1);
    }
  }

  const polishedJson = polished as any;
  const resultJson = result as any;

  for (const path of pathSet) {
    const pathParts = path.split('.');
    applyPath(resultJson, polishedJson, pathParts);
  }

  return result;
}

export function getModulePaths(): Array<{ id: string; label: string; path: string[] }> {
  return [
    { id: 'candidate-summary', label: '候选人总结', path: ['candidate_summary'] },
    { id: 'match-analysis', label: '匹配分析', path: ['match_analysis'] },
    { id: 'gap-analysis', label: '差距分析', path: ['gap_analysis'] },
    { id: 'career-path', label: '职业路径规划', path: ['career_path_planning'] },
    { id: 'development-plan', label: '发展计划', path: ['development_plan'] },
    { id: 'action-plan', label: '行动计划', path: ['action_plan'] },
    { id: 'final-recommendation', label: '最终推荐', path: ['final_recommendation'] },
  ];
}