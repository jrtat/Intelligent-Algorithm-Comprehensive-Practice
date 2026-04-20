import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import mammoth from 'mammoth';
import { processResume } from '../api/resumeApi';
import { useToast } from '../context/ToastContext';
import { PageDashboard } from '../components/PageDashboard/PageDashboard';
import type { ResumeData } from '../types/job';

interface CapabilityAnalysisProps {}

const ArrayInput = ({ label, values, onChange, required = false }: { label: string, values: string[], onChange: (newValues: string[]) => void, required?: boolean }) => {
  const handleAdd = () => onChange([...values, '']);
  const handleChange = (index: number, val: string) => {
    const newValues = [...values];
    newValues[index] = val;
    onChange(newValues);
  };
  const handleRemove = (index: number) => {
    const newValues = values.filter((_, i) => i !== index);
    onChange(newValues);
  };

  return (
    <div className="md:col-span-2">
      <label className="block text-sm font-bold mb-2">{label} {required && <span className="text-error">*</span>}</label>
      <div className="space-y-3">
        {values.map((val, idx) => (
          <div key={idx} className="flex items-start gap-2">
            <span className="mt-3 w-1.5 h-1.5 rounded-full bg-primary shrink-0"></span>
            <textarea
              value={val}
              onChange={(e) => handleChange(idx, e.target.value)}
              className="flex-1 p-3 rounded-lg border border-outline-variant bg-surface focus:ring-2 focus:ring-primary/20 outline-none transition-all min-h-[60px]"
              placeholder={`请输入${label}`}
            />
            <button onClick={() => handleRemove(idx)} className="p-2 text-outline hover:text-error transition-colors mt-1" title="删除">
              <span className="material-symbols-outlined">delete</span>
            </button>
          </div>
        ))}
        <button onClick={handleAdd} className="flex items-center gap-1 text-sm text-primary font-bold hover:opacity-80 transition-opacity">
          <span className="material-symbols-outlined text-sm">add</span> 添加一项
        </button>
      </div>
    </div>
  );
};

const RadarLabel = ({ className, title, explanation, tooltipPos = 'top' }: { className: string, title: string, explanation: string, tooltipPos?: 'top' | 'bottom' | 'left' | 'right' }) => {
  const posClasses = {
    top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
    left: "right-full top-1/2 -translate-y-1/2 mr-2",
    right: "left-full top-1/2 -translate-y-1/2 ml-2"
  };
  const arrowClasses = {
    top: "top-full left-1/2 -translate-x-1/2 border-t-surface-container-highest",
    bottom: "bottom-full left-1/2 -translate-x-1/2 border-b-surface-container-highest",
    left: "left-full top-1/2 -translate-y-1/2 border-l-surface-container-highest",
    right: "right-full top-1/2 -translate-y-1/2 border-r-surface-container-highest"
  };

  return (
    <div className={`absolute ${className} text-[10px] font-bold uppercase bg-surface/90 px-3 py-1.5 rounded-full shadow-[0_2px_8px_-2px_rgba(0,0,0,0.1),inset_0_1px_2px_rgba(255,255,255,0.5)] border border-outline-variant/30 hover:shadow-[0_4px_12px_-2px_rgba(0,0,0,0.15)] transition-all cursor-default group z-10`}>
      {title}
      {explanation && (
        <div className={`absolute opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 w-48 bg-surface-container-highest text-on-surface p-3 rounded-xl text-xs font-normal shadow-xl border border-outline-variant/20 z-50 pointer-events-none ${posClasses[tooltipPos]}`}>
          {explanation}
          <div className={`absolute border-[5px] border-transparent ${arrowClasses[tooltipPos]}`}></div>
        </div>
      )}
    </div>
  );
};

export default function CapabilityAnalysis({}: CapabilityAnalysisProps = {}) {
  const navigate = useNavigate();
  const [isParsing, setIsParsing] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [fileName, setFileName] = useState('');
  const [rawText, setRawText] = useState('');
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [showTextInputModal, setShowTextInputModal] = useState(false);
  const [hoveredPoint, setHoveredPoint] = useState<number | null>(null);
  const { showToast } = useToast();
  const [resumeData, setResumeData] = useState<ResumeData>(() => {
    const saved = localStorage.getItem('resumeData');
    if (saved) {
      try { 
        const parsed = JSON.parse(saved); 
        if (!parsed.scores) {
          parsed.scores = { adaptability: 0, technicalDepth: 0, communication: 0, stressTolerance: 0, innovation: 0 };
        }
        if (!parsed.scoreExplanations) {
          parsed.scoreExplanations = {
            completeness: '', technicalDepth: '', adaptability: '', communication: '', stressTolerance: '', innovation: '', competitiveness: ''
          };
        }
        if (parsed.completeness === undefined) {
          parsed.completeness = 0;
        }
        if (parsed.targetRole === undefined) {
          parsed.targetRole = '';
        }
        if (!Array.isArray(parsed.skills)) parsed.skills = parsed.skills ? [parsed.skills] : [];
        if (!Array.isArray(parsed.certificates)) parsed.certificates = parsed.certificates ? [parsed.certificates] : [];
        if (!Array.isArray(parsed.projectExperience)) parsed.projectExperience = parsed.projectExperience ? [parsed.projectExperience] : [];
        if (!Array.isArray(parsed.internshipExperience)) parsed.internshipExperience = parsed.internshipExperience ? [parsed.internshipExperience] : [];
        if (!Array.isArray(parsed.practicalExperience)) parsed.practicalExperience = parsed.practicalExperience ? [parsed.practicalExperience] : [];
        if (!Array.isArray(parsed.hobbies)) parsed.hobbies = parsed.hobbies ? [parsed.hobbies] : [];
        return parsed;
      } catch (e) {}
    }
    return {
      name: '', age: '', education: '', major: '', skills: [],
      certificates: [], projectExperience: [], internshipExperience: [],
      practicalExperience: [], hobbies: [] as string[], summary: '', other: '',
      targetRole: '',
      completeness: 0,
      scores: { adaptability: 0, technicalDepth: 0, communication: 0, stressTolerance: 0, innovation: 0 }
    };
  });

  // Auto-save to localStorage whenever resumeData changes
  useEffect(() => {
    localStorage.setItem('resumeData', JSON.stringify(resumeData));
  }, [resumeData]);

  const extractTextFromPDF = async (file: File) => {
    if (!(window as any).pdfjsLib) {
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
      document.body.appendChild(script);
      await new Promise(resolve => script.onload = resolve);
      (window as any).pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
    }
    
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await (window as any).pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    let text = '';
    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const content = await page.getTextContent();
      const pageText = content.items.map((item: any) => item.str).join(' ');
      text += pageText + '\n';
    }
    return text;
  };

  const extractTextFromDocx = async (file: File) => {
    const arrayBuffer = await file.arrayBuffer();
    const result = await mammoth.extractRawText({ arrayBuffer });
    return result.value;
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setFileName(file.name);
    setIsParsing(true);
    
    try {
      let text = '';
      if (file.name.endsWith('.pdf')) {
        text = await extractTextFromPDF(file);
      } else if (file.name.endsWith('.docx')) {
        text = await extractTextFromDocx(file);
      } else if (file.name.endsWith('.doc')) {
        const rawText = await file.text();
        text = rawText.replace(/[^\x20-\x7E\u4E00-\u9FA5]/g, ' ');
      } else {
        text = await file.text();
      }
      
      if (!text || text.trim().length < 20) {
        setToastMessage('文档中未识别到文字内容，请上传包含可编辑文本的简历（非图片型文档）');
        setTimeout(() => setToastMessage(''), 3000);
        setIsParsing(false);
        return;
      }

      await parseWithLLM(text);
    } catch (error) {
      console.error('File parsing error:', error);
      setToastMessage('文件读取失败，请重试');
      setTimeout(() => setToastMessage(''), 2000);
    } finally {
      setIsParsing(false);
    }
  };

  const parseWithLLM = async (text: string) => {
    const apiKey = import.meta.env.VITE_ALIYUN_BAILIAN_API_KEY;
    let apiUrl = import.meta.env.VITE_ALIYUN_BAILIAN_API_URL || 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions';
    const model = import.meta.env.VITE_ALIYUN_BAILIAN_MODEL || 'qwen-plus';

    // 修复 URL：如果环境变量中只配置了 base URL，自动补全 endpoint
    if (!apiUrl.endsWith('/chat/completions')) {
      apiUrl = apiUrl.replace(/\/$/, '') + '/chat/completions';
    }

    if (!apiKey || apiKey === 'your_api_key_here') {
      setToastMessage('请在 .env 文件中配置 VITE_ALIYUN_BAILIAN_API_KEY');
      setTimeout(() => setToastMessage(''), 3000);
      return;
    }

    try {
      const RESUME_PARSER_PROMPT = `
你是一个极为专业的资深 HR 及简历内容抓取解析器。请尽全力从下列用户提供的未格式化的简历文本串中，抽取并结构化出下面所定义的 JSON 数据对象。要求如下：
1、根据简历提供的信息丰富程度，给出一个“简历完整度”评分（1-100分）。
2、你必须根据这份简历面向的行业，客观地对这份简历涉及的技术栈进行“技术深度”评分（1-100分），请较为严苛地打分。
3、依据简历提到的项目经历，实习经历，兴趣爱好和个人总结等信息，来对其 “适应能力”，“沟通表达能力”，“抗压能力”，“创新能力”评分（1-100分）。注意对没有提到相关内容的默认给出低分，对提到的内容酌情加分。比如没有实习经历和项目经历就默认抗压能力比较弱，并且未提到有关表明自己抗压能力优秀的信息，那么给出低分（30左右）。必须依据简历内容全局考量。
4、对于你给出的所有评分（简历完整度、技术深度、适应能力、沟通表达能力、抗压能力、创新能力），以及基于这五维能力得出的“就业竞争力”综合评价，必须给出一段简短的解释性说明（20-50字），说明打分依据或提升建议。

### JSON 数据结构模板：
\`\`\`json
{
  "name": "姓名（如张三）",
  "age": "年龄（如25）",
  "education": "学历（如本科）",
  "major": "就读专业",
  "skills": ["熟练掌握 React", "了解 Node.js"],
  "certificates": ["大学英语六级", "计算机二级"],
  "projectExperience": ["项目A：负责前端架构...", "项目B：实现核心业务..."],
  "internshipExperience": ["公司A：前端实习生..."],
  "practicalExperience": ["活动A：组织策划..."],
  "hobbies": ["爱好A", "爱好B"],
  "summary": "个人总结（总结性的话语）",
  "other": "其他提取出的杂项信息",
  "targetRole": "主攻路径（如：前端开发工程师、产品经理等，根据简历内容推断最匹配的岗位）",
  "completeness": 58,
  "scores": {
    "adaptability": 55,
    "technicalDepth": 50,
    "communication": 52,
    "stressTolerance": 55,
    "innovation": 52
  },
  "scoreExplanations": {
    "completeness": "简历缺少项目经历和证书，完整度一般，建议补充更多细节。",
    "technicalDepth": "掌握了React等基础前端技术，但缺乏底层原理和复杂架构经验。",
    "adaptability": "没有实习经历，适应新环境的能力有待验证，需在实际项目中锻炼。",
    "communication": "个人总结表达清晰，具备基本的沟通能力，但缺乏团队协作的具体案例。",
    "stressTolerance": "缺乏高压项目经验，抗压能力暂不明确，建议补充克服困难的经历。",
    "innovation": "未体现出创新性的项目或想法，可尝试参与开源或独立设计作品。",
    "competitiveness": "综合来看，目前处于初级水平，竞争力较弱，建议增加实战经验和深度技术积累。"
  }
}
\`\`\`

### 解析要求与规则：
1. **严格返回 JSON**：你的回复必须且只能包含一个合法的 JSON 对象，不要含有任何 Markdown 的 \`\`\`json 标记，绝对不要带有任何除了 JSON 对象外的解析说明、思考过程文字等。
2. **灵活兼容补全**：如果某些字段在原文本中无法找到，请填入空字符串 \`""\`。切勿瞎编乱造或者留 \`null\`。
3. **格式规整**：经历描述文字如果很长，请合理添加换行符 \`\\n\` 以保证排版美观。
4. **智能归类**：尝试分辨诸如“籍贯”、“婚姻状况”以及json格式中未提到但是简历中出现的杂项信息，如果发现请放入 \`other\` 字段中。
5. **禁止幻觉**：必须依照所给信息进行提取获评分。
6. **数组格式输出**：专业技能（skills）、证书（certificates）、项目经历（projectExperience）、实习经历（internshipExperience）、实践活动经历（practicalExperience）这五个字段必须是字符串数组（Array of Strings）。数组的每个元素标明某一类专业技能、证书或某一条经历。所有内容必须尽量保持与原文相近，保留如“熟练掌握”、“了解”等字眼。其他非数组字段必须是纯字符串（String）。
`;

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          model: model,
          messages: [
            {
              role: 'system',
              content: RESUME_PARSER_PROMPT
            },
            {
              role: 'user',
              content: `待解析原文如下：\n${text.substring(0, 50000)}`
            }
          ],
          response_format: { type: 'json_object' }
        })
      });

      const data = await response.json();
      
      if (!response.ok) {
        console.error('LLM API Error:', data);
        throw new Error(data.message || `API Error ${response.status}`);
      }

      if (data.choices && data.choices[0]) {
        let replyContent = data.choices[0].message.content.trim();
        
        // 剔除可能会附带的 markdown json 标记
        if (replyContent.startsWith("```json")) {
          replyContent = replyContent.replace(/^```json\n?/, "");
        }
        if (replyContent.startsWith("```")) {
            replyContent = replyContent.replace(/^```\n?/, "");
        }
        if (replyContent.endsWith("```")) {
          replyContent = replyContent.replace(/\n?```$/, "");
        }
        
        const parsed = JSON.parse(replyContent);
        
        // 检查是否真正解析出了内容
        const hasMeaningfulContent = 
          (parsed.name && parsed.name.trim().length > 0) || 
          (parsed.education && parsed.education.trim().length > 0) || 
          (parsed.skills && parsed.skills.length > 0) || 
          (parsed.projectExperience && parsed.projectExperience.length > 0) ||
          (parsed.internshipExperience && parsed.internshipExperience.length > 0);

        if (!hasMeaningfulContent) {
          setToastMessage('未从传入文件中解析出文本');
          setTimeout(() => setToastMessage(''), 3000);
          return;
        }

        // 防御性处理：确保数组字段是数组，文本字段是字符串
        const arrayFields = ['skills', 'certificates', 'projectExperience', 'internshipExperience', 'practicalExperience', 'hobbies'];
        for (const field of arrayFields) {
          if (parsed[field] !== undefined && parsed[field] !== null) {
             if (!Array.isArray(parsed[field])) {
                if (typeof parsed[field] === 'string') {
                   parsed[field] = parsed[field].split('\n').filter(Boolean);
                } else {
                   parsed[field] = [String(parsed[field])];
                }
             } else {
                parsed[field] = parsed[field].map(String);
             }
          } else {
             parsed[field] = [];
          }
        }

        const stringFields = ['name', 'age', 'education', 'major', 'summary', 'other', 'targetRole'];
        for (const field of stringFields) {
          if (parsed[field] !== undefined && parsed[field] !== null) {
            if (typeof parsed[field] === 'object') {
              if (Array.isArray(parsed[field])) {
                parsed[field] = parsed[field].map((item: any) => typeof item === 'object' ? JSON.stringify(item) : String(item)).join('\n');
              } else {
                parsed[field] = JSON.stringify(parsed[field]);
              }
            } else {
              parsed[field] = String(parsed[field]);
            }
          }
        }
        
        setResumeData(prev => ({ ...prev, ...parsed }));
      } else {
        throw new Error('Invalid response from LLM');
      }
    } catch (error) {
      console.error('LLM Parsing error:', error);
      setToastMessage('简历解析失败，请重试');
      setTimeout(() => setToastMessage(''), 2000);
    }
  };

  const handleSubmit = async () => {
    const { name, age, education, major, skills } = resumeData;

    const isFieldValid = (val: any) => String(val || '').trim().length > 0;
    const isSkillsValid = Array.isArray(skills) && skills.length > 0 && skills.some(s => String(s || '').trim().length > 0);

    if (!isFieldValid(name) || !isFieldValid(age) || !isFieldValid(education) || !isFieldValid(major) || !isSkillsValid) {
      setToastMessage('请填写所有带 * 号的必填项');
      setTimeout(() => setToastMessage(''), 2000);
      return;
    }

    // 不阻塞用户操作，后台处理
    processResume(resumeData, {
      onProgress: () => {
        // 静默更新进度，不打扰用户
      },
      onCompleted: (result) => {
        localStorage.setItem('matchResult', JSON.stringify(result));
        showToast({
          message: '职业匹配已完成，点击查看匹配结果！',
          onClick: () => navigate('/job-match'),
          duration: 5000,
        });
      },
      onFailed: (error) => {
        showToast({
          message: `匹配失败: ${error}`,
          duration: 5000,
        });
      },
    });

    showToast({
      message: '正在分析匹配度，请稍候...',
      duration: 3000,
    });
  };

  const handleRawTextSubmit = async () => {
    if (!rawText || rawText.trim().length < 20) {
      setToastMessage('请输入至少20个字符的简历文本');
      setTimeout(() => setToastMessage(''), 3000);
      return;
    }
    setFileName('手动输入文本');
    setIsParsing(true);
    setShowTextInputModal(false);
    await parseWithLLM(rawText);
    setIsParsing(false);
  };

  const clearData = () => {
    setShowClearConfirm(true);
  };

  const confirmClearData = () => {
    setResumeData({
      name: '', age: '', education: '', major: '', skills: [],
      certificates: [], projectExperience: [], internshipExperience: [],
      practicalExperience: [], hobbies: [] as string[], summary: '', other: '',
      targetRole: '',
      completeness: 0,
      scores: { adaptability: 0, technicalDepth: 0, communication: 0, stressTolerance: 0, innovation: 0 },
      scoreExplanations: { completeness: '', technicalDepth: '', adaptability: '', communication: '', stressTolerance: '', innovation: '', competitiveness: '' }
    });
    localStorage.removeItem('resumeData');
    setFileName('');
    setRawText('');
    setShowClearConfirm(false);
    setToastMessage('数据已清空');
    setTimeout(() => setToastMessage(''), 2000);
  };

  const competitiveness = Math.round(
    ((resumeData.scores?.adaptability || 0) +
    (resumeData.scores?.technicalDepth || 0) +
    (resumeData.scores?.communication || 0) +
    (resumeData.scores?.stressTolerance || 0) +
    (resumeData.scores?.innovation || 0)) / 5
  );

  return (
    <PageDashboard
      title="能力分析"
      subtitle="基于您的职业经历与项目积累，分析专业架构的多维图谱"
      showBreadcrumb
      breadcrumbItems={[
        { label: '首页', href: '/' },
        { label: '能力分析' },
      ]}
    >
    <div className="space-y-8">
      {toastMessage && (
        <div className="fixed top-20 left-1/2 -translate-x-1/2 z-[100] bg-error text-white px-6 py-3 rounded-lg shadow-lg font-bold animate-in fade-in slide-in-from-top-4">
          {toastMessage}
        </div>
        
      )}

      {/* Clear Confirmation Modal */}
      {showClearConfirm && createPortal(
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 backdrop-blur-sm animate-in fade-in">
          <div className="bg-surface rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl border border-outline-variant/20 animate-in zoom-in-95">
            <div className="flex items-center gap-4 mb-4 text-error">
              <span className="material-symbols-outlined text-4xl">warning</span>
              <h3 className="text-2xl font-bold text-on-surface">清空数据</h3>
            </div>
            <p className="text-on-surface-variant mb-8 text-lg">
              确定要清空所有简历数据吗？此操作不可恢复。
            </p>
            <div className="flex justify-end gap-4">
              <button 
                onClick={() => setShowClearConfirm(false)}
                className="px-6 py-2.5 rounded-xl font-bold text-on-surface border border-outline-variant hover:bg-surface-container transition-colors"
              >
                取消
              </button>
              <button 
                onClick={confirmClearData}
                className="px-6 py-2.5 rounded-xl font-bold bg-error text-white shadow-md shadow-error/20 hover:opacity-90 active:scale-95 transition-all"
              >
                确定清空
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}

      {/* Text Input Modal */}
      {showTextInputModal && createPortal(
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 backdrop-blur-sm animate-in fade-in">
          <div className="bg-surface rounded-2xl p-6 max-w-2xl w-full mx-4 shadow-2xl border border-outline-variant/20 animate-in zoom-in-95 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-bold text-on-surface">粘贴简历文本</h3>
              <button onClick={() => setShowTextInputModal(false)} className="p-2 hover:bg-surface-container rounded-full text-on-surface-variant transition-colors">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            <div className="relative">
              <textarea 
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                placeholder="在此处粘贴您的非结构化简历文本..."
                className="w-full p-4 rounded-xl border border-outline-variant bg-surface focus:ring-2 focus:ring-primary/20 outline-none transition-all text-sm resize-none h-[300px] pb-16"
              />
              <button 
                onClick={handleRawTextSubmit}
                disabled={isParsing || rawText.trim().length < 20}
                className="absolute bottom-4 right-4 px-6 py-2 bg-primary text-white font-bold rounded-lg shadow-md hover:opacity-90 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <span className="material-symbols-outlined text-sm">send</span>
                <span>开始解析</span>
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}

      {/* Bento Grid Layout */}
      <div className="grid grid-cols-12 gap-6">
        {/* 1. File Upload */}
        <div className="col-span-12 lg:col-span-4 bg-surface-container-low rounded-xl p-8 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <h3 className="text-xl font-bold">更新数据源</h3>
              <button 
                onClick={clearData}
                className="p-1.5 text-outline hover:text-primary hover:bg-primary/10 rounded-full transition-colors group relative flex items-center justify-center"
              >
                <span className="material-symbols-outlined text-xl">refresh</span>
                <div className="absolute top-1/2 left-full -translate-y-1/2 ml-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap bg-surface-container-highest text-on-surface text-xs py-1.5 px-3 rounded shadow-sm border border-outline-variant/20 z-50">
                  清空所有内容
                  <div className="absolute top-1/2 right-full -translate-y-1/2 border-[4px] border-transparent border-r-surface-container-highest"></div>
                </div>
              </button>
            </div>
            <p className="text-sm text-on-surface-variant mb-6">上传您最新的简历或作品集以完善个人资料。</p>
            <input type="file" accept=".pdf,.doc,.docx" className="hidden" id="resume-upload" onChange={handleFileUpload} />
            <label htmlFor="resume-upload" className="border-2 border-dashed border-outline-variant rounded-xl p-10 flex flex-col items-center justify-center group hover:bg-white/50 transition-all cursor-pointer relative overflow-hidden">
              {isParsing ? (
                <div className="flex flex-col items-center">
                  <span className="material-symbols-outlined text-4xl text-primary mb-4 animate-spin">sync</span>
                  <p className="text-sm font-semibold">正在解析简历...</p>
                </div>
              ) : (
                <>
                  <span className="material-symbols-outlined text-4xl text-primary mb-4">cloud_upload</span>
                  <p className="text-sm font-semibold">点击或将 PDF/DOC/DOCX 拖放到此处</p>
                  <p className="text-xs text-outline mt-1">最大 10MB • 自动启动解析</p>
                </>
              )}
            </label>
            
            <div className="mt-4">
              <button 
                onClick={() => setShowTextInputModal(true)}
                className="w-full py-3 px-4 rounded-xl border border-outline-variant bg-surface hover:bg-surface-container-low transition-all text-sm font-bold text-on-surface flex items-center justify-center gap-2 group"
              >
                <span className="material-symbols-outlined text-primary group-hover:scale-110 transition-transform">edit_document</span>
                手动输入/粘贴简历文本
              </button>
            </div>
          </div>
          <div className="mt-8 space-y-3">
            <div className="flex items-center justify-between text-xs font-bold uppercase tracking-widest text-outline">
              <span>最后同步</span>
              <span>{fileName ? '刚刚' : '2023年10月24日'}</span>
            </div>
            <div className="flex items-center gap-3 p-3 bg-white rounded-lg">
              <span className="material-symbols-outlined text-secondary">description</span>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-bold truncate">{fileName || 'senior_architect_v4.pdf'}</p>
                <p className="text-[10px] text-outline">{isParsing ? '解析中...' : '解析完成'}</p>
              </div>
              {!isParsing && <span className="material-symbols-outlined text-primary text-sm">check_circle</span>}
            </div>
          </div>
        </div>

        {/* 2. Large Radar Chart */}
        <div className="col-span-12 lg:col-span-8 bg-surface-container-lowest rounded-xl p-8">
          <div className="flex flex-col items-start mb-8">
            <div className="flex items-center gap-4 mb-2">
              <h3 className="text-xl font-bold">维度掌控力</h3>
              <span className="px-3 py-1 bg-primary/10 text-primary text-xs font-bold rounded-full">主攻路径：{resumeData.targetRole || '暂无'}</span>
            </div>
            <p className="text-sm text-on-surface-variant">跨核心能力分布。</p>
          </div>
          <div className="relative aspect-square max-h-[400px] mx-auto flex items-center justify-center">
            <svg className="w-full h-full max-w-[350px]" viewBox="0 0 400 400">
              {/* Radar Grid */}
              {[20, 40, 60, 80, 100].map(level => {
                const points = [0, 72, 144, 216, 288].map(angle => {
                  const angleRad = (angle - 90) * (Math.PI / 180);
                  const r = 150 * (level / 100);
                  return `${200 + r * Math.cos(angleRad)},${200 + r * Math.sin(angleRad)}`;
                }).join(' ');
                return <polygon key={level} points={points} fill="none" stroke="#e2e8f0" strokeWidth="2" />;
              })}
              
              {/* Radar Axes */}
              {[0, 72, 144, 216, 288].map(angle => {
                const angleRad = (angle - 90) * (Math.PI / 180);
                const r = 150;
                return <line key={angle} x1="200" y1="200" x2={200 + r * Math.cos(angleRad)} y2={200 + r * Math.sin(angleRad)} stroke="#e2e8f0" strokeWidth="2" />;
              })}

              {/* Data Area */}
              <polygon 
                points={[0, 72, 144, 216, 288].map((angle, i) => {
                  const scores = [
                    resumeData.scores?.technicalDepth || 0,
                    resumeData.scores?.adaptability || 0,
                    resumeData.scores?.communication || 0,
                    resumeData.scores?.stressTolerance || 0,
                    resumeData.scores?.innovation || 0
                  ];
                  const angleRad = (angle - 90) * (Math.PI / 180);
                  const r = 150 * (scores[i] / 100);
                  return `${200 + r * Math.cos(angleRad)},${200 + r * Math.sin(angleRad)}`;
                }).join(' ')}
                fill="rgba(0, 91, 191, 0.2)" 
                stroke="#005bbf" 
                strokeWidth="2" 
              />

              {/* Data Points */}
              {[0, 72, 144, 216, 288].map((angle, i) => {
                const scores = [
                  resumeData.scores?.technicalDepth || 0,
                  resumeData.scores?.adaptability || 0,
                  resumeData.scores?.communication || 0,
                  resumeData.scores?.stressTolerance || 0,
                  resumeData.scores?.innovation || 0
                ];
                const angleRad = (angle - 90) * (Math.PI / 180);
                const r = 150 * (scores[i] / 100);
                const cx = 200 + r * Math.cos(angleRad);
                const cy = 200 + r * Math.sin(angleRad);
                return (
                  <g 
                    key={angle} 
                    onMouseEnter={() => setHoveredPoint(i)} 
                    onMouseLeave={() => setHoveredPoint(null)}
                    className="cursor-pointer"
                  >
                    <circle cx={cx} cy={cy} r="16" fill="transparent" />
                    <circle 
                      cx={cx} 
                      cy={cy} 
                      fill={hoveredPoint === i ? "#00428a" : "#005bbf"} 
                      r={hoveredPoint === i ? "6" : "4"} 
                      className="transition-all duration-200" 
                    />
                  </g>
                );
              })}
            </svg>

            {/* Hover Tooltip Overlay */}
            {hoveredPoint !== null && (() => {
              const angle = [0, 72, 144, 216, 288][hoveredPoint];
              const scores = [
                resumeData.scores?.technicalDepth || 0,
                resumeData.scores?.adaptability || 0,
                resumeData.scores?.communication || 0,
                resumeData.scores?.stressTolerance || 0,
                resumeData.scores?.innovation || 0
              ];
              const labels = ['技术深度', '适应能力', '沟通表达能力', '抗压能力', '创新能力'];
              const angleRad = (angle - 90) * (Math.PI / 180);
              const r = 150 * (scores[hoveredPoint] / 100);
              const cx = 200 + r * Math.cos(angleRad);
              const cy = 200 + r * Math.sin(angleRad);
              const leftPct = (cx / 400) * 100;
              const topPct = (cy / 400) * 100;

              return (
                <div 
                  className="absolute z-30 pointer-events-none flex flex-col items-center animate-in fade-in zoom-in-95 duration-200"
                  style={{ 
                    left: `${leftPct}%`, 
                    top: `${topPct}%`,
                    transform: 'translate(-50%, -100%)',
                    marginTop: '-12px'
                  }}
                >
                  <div className="bg-surface-container-highest text-on-surface px-3 py-1.5 rounded-lg shadow-xl border border-outline-variant/20 flex flex-col items-center gap-0.5">
                    <span className="text-[10px] text-on-surface-variant font-bold uppercase">{labels[hoveredPoint]}</span>
                    <span className="text-primary font-black text-sm">{scores[hoveredPoint]}<span className="text-[10px] text-on-surface ml-0.5">分</span></span>
                  </div>
                  <div className="w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[6px] border-t-surface-container-highest"></div>
                </div>
              );
            })()}

            {/* Labels */}
            <RadarLabel className="top-[8%] left-1/2 -translate-x-1/2" title="技术深度" explanation={resumeData.scoreExplanations?.technicalDepth || ''} tooltipPos="bottom" />
            <RadarLabel className="top-[35%] right-[8%]" title="适应能力" explanation={resumeData.scoreExplanations?.adaptability || ''} tooltipPos="left" />
            <RadarLabel className="bottom-[15%] right-[18%]" title="沟通表达能力" explanation={resumeData.scoreExplanations?.communication || ''} tooltipPos="top" />
            <RadarLabel className="bottom-[15%] left-[18%]" title="抗压能力" explanation={resumeData.scoreExplanations?.stressTolerance || ''} tooltipPos="top" />
            <RadarLabel className="top-[35%] left-[8%]" title="创新能力" explanation={resumeData.scoreExplanations?.innovation || ''} tooltipPos="right" />
          </div>
        </div>

        {/* 3. Overall Metrics */}
        <div className="col-span-12 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-surface-container-lowest rounded-xl p-8 border border-outline-variant/10 flex flex-col justify-between gap-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold mb-1">就业竞争力</h3>
                <p className="text-sm text-on-surface-variant">基于五维能力模型的综合评估均值</p>
              </div>
              <div className="text-5xl font-black text-primary">{competitiveness}<span className="text-2xl text-outline ml-1">分</span></div>
            </div>
            {resumeData.scoreExplanations?.competitiveness && (
              <div className="bg-primary/5 p-4 rounded-lg text-sm text-on-surface border border-primary/10">
                <span className="font-bold text-primary mr-2">分析说明:</span>
                {resumeData.scoreExplanations.competitiveness}
              </div>
            )}
          </div>
          <div className="bg-surface-container-lowest rounded-xl p-8 border border-outline-variant/10 flex flex-col justify-between gap-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold mb-1">简历完整度</h3>
                <p className="text-sm text-on-surface-variant">评估的简历信息丰富程度</p>
              </div>
              <div className="text-5xl font-black text-secondary">{resumeData.completeness || 0}<span className="text-2xl text-outline ml-1">分</span></div>
            </div>
            {resumeData.scoreExplanations?.completeness && (
              <div className="bg-secondary/5 p-4 rounded-lg text-sm text-on-surface border border-secondary/10">
                <span className="font-bold text-secondary mr-2">分析说明:</span>
                {resumeData.scoreExplanations.completeness}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Resume Structured Info Form */}
      <div className="bg-surface-container-lowest rounded-xl p-8 border border-outline-variant/10">
        <h3 className="text-xl font-bold mb-6">简历结构化信息确认</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-bold mb-2">姓名 <span className="text-error">*</span></label>
            <input value={resumeData.name || ''} onChange={e => setResumeData({...resumeData, name: e.target.value})} className="w-full p-3 rounded-lg border border-outline-variant bg-surface focus:ring-2 focus:ring-primary/20 outline-none transition-all" placeholder="请输入姓名" />
          </div>
          <div>
            <label className="block text-sm font-bold mb-2">年龄 <span className="text-error">*</span></label>
            <input value={resumeData.age || ''} onChange={e => setResumeData({...resumeData, age: e.target.value})} className="w-full p-3 rounded-lg border border-outline-variant bg-surface focus:ring-2 focus:ring-primary/20 outline-none transition-all" placeholder="请输入年龄" />
          </div>
          <div>
            <label className="block text-sm font-bold mb-2">学历 <span className="text-error">*</span></label>
            <input value={resumeData.education || ''} onChange={e => setResumeData({...resumeData, education: e.target.value})} className="w-full p-3 rounded-lg border border-outline-variant bg-surface focus:ring-2 focus:ring-primary/20 outline-none transition-all" placeholder="请输入学历" />
          </div>
          <div>
            <label className="block text-sm font-bold mb-2">就读专业 <span className="text-error">*</span></label>
            <input value={resumeData.major || ''} onChange={e => setResumeData({...resumeData, major: e.target.value})} className="w-full p-3 rounded-lg border border-outline-variant bg-surface focus:ring-2 focus:ring-primary/20 outline-none transition-all" placeholder="请输入就读专业" />
          </div>
          <ArrayInput 
            label="掌握的专业技能" 
            values={resumeData.skills || []} 
            onChange={newVals => setResumeData({...resumeData, skills: newVals})} 
            required 
          />
          <ArrayInput 
            label="证书" 
            values={resumeData.certificates || []} 
            onChange={newVals => setResumeData({...resumeData, certificates: newVals})} 
          />
          <ArrayInput 
            label="项目经历" 
            values={resumeData.projectExperience || []} 
            onChange={newVals => setResumeData({...resumeData, projectExperience: newVals})} 
          />
          <ArrayInput 
            label="实习经历" 
            values={resumeData.internshipExperience || []} 
            onChange={newVals => setResumeData({...resumeData, internshipExperience: newVals})} 
          />
          <ArrayInput 
            label="实践活动经历" 
            values={resumeData.practicalExperience || []} 
            onChange={newVals => setResumeData({...resumeData, practicalExperience: newVals})} 
          />
          <ArrayInput
            label="兴趣爱好"
            values={resumeData.hobbies || []}
            onChange={newVals => setResumeData({...resumeData, hobbies: newVals})}
          />
          <div className="md:col-span-2">
            <label className="block text-sm font-bold mb-2">个人总结</label>
            <textarea value={resumeData.summary || ''} onChange={e => setResumeData({...resumeData, summary: e.target.value})} className="w-full p-3 rounded-lg border border-outline-variant bg-surface h-32 focus:ring-2 focus:ring-primary/20 outline-none transition-all" placeholder="请输入个人总结" />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-bold mb-2">其他（杂项）</label>
            <textarea value={resumeData.other || ''} onChange={e => setResumeData({...resumeData, other: e.target.value})} className="w-full p-3 rounded-lg border border-outline-variant bg-surface h-24 focus:ring-2 focus:ring-primary/20 outline-none transition-all" placeholder="其他提取出的杂项信息" />
          </div>
        </div>
        <div className="mt-8 flex justify-end">
          <button onClick={handleSubmit} className="px-8 py-3 bg-primary text-white font-bold rounded-xl shadow-md shadow-primary/20 hover:opacity-90 active:scale-95 transition-all">
            生成职业匹配
          </button>
        </div>
      </div>
      </div>
    </PageDashboard>
  );
}
