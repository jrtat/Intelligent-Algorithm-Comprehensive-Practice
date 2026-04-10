// CareerAssistant.tsx
import React, { useState, useRef, useEffect } from 'react';
import type { DragEvent, ChangeEvent } from 'react';
import './CareerAssistant.css';

// 类型定义
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ResumeField {
  id: string;
  key: string;
  value: string;
}

// 模拟从PDF提取结构化数据 (实际项目中可替换为真实解析)
const mockExtractFromPDF = (fileName: string): ResumeField[] => {
  // 根据文件名生成一些演示数据
  const baseFields: ResumeField[] = [
    { id: '1', key: '姓名', value: '张明轩' },
    { id: '2', key: '学校', value: '上海交通大学' },
    { id: '3', key: '专业', value: '计算机科学与技术' },
    { id: '4', key: '学历', value: '本科 2022级' },
    { id: '5', key: '电话', value: '188-1234-5678' },
    { id: '6', key: '邮箱', value: 'mingxuan.zhang@sjtu.edu.cn' },
    { id: '7', key: '技能', value: 'Python, React, 数据分析, 机器学习' },
    { id: '8', key: '实习经历', value: '腾讯云 开发实习生 (2024.07-2024.09)' },
  ];
  return baseFields;
};

const CareerAssistant: React.FC = () => {
  // 聊天状态
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '你好！我是你的AI职业规划助手。你可以上传简历，我会结合你的背景为你提供个性化的职业建议。',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 简历面板状态
  const [collapsed, setCollapsed] = useState(false);
  const [resumeFields, setResumeFields] = useState<ResumeField[]>([]);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [isDragActive, setIsDragActive] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 处理发送消息
  const handleSendMessage = async () => {
    const trimmed = inputValue.trim();
    if (!trimmed || isSending) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: trimmed,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsSending(true);

    // 构建简历对象 (key-value)
    const resumeObject = resumeFields.reduce((acc, field) => {
      if (field.key.trim()) {
        acc[field.key.trim()] = field.value;
      }
      return acc;
    }, {} as Record<string, string>);

    // 准备请求体 (接口设计)
    const payload = {
      message: trimmed,
      resume: resumeObject,
      timestamp: new Date().toISOString(),
    };

    console.log('📤 发送到后端接口 /api/chat :', payload);

    try {
      // 模拟后端调用 (实际项目中替换为真实fetch)
      // const response = await fetch('/api/chat', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(payload),
      // });
      // const data = await response.json();
      
      // 模拟AI回复 (延迟效果)
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const aiReply: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: resumeFields.length > 0 
          ? '已收到你的消息和简历信息。根据你的背景，我建议可以关注AI工程化或全栈开发方向，需要具体规划吗？'
          : '我收到了你的消息。不过你还没有上传简历，建议上传简历让我更了解你，以便给出针对性建议。',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiReply]);
    } catch (error) {
      console.error('发送失败', error);
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content: '抱歉，消息发送失败，请稍后重试。',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // 处理PDF上传 (模拟提取)
  const processFile = (file: File) => {
    if (file.type !== 'application/pdf') {
      alert('请上传PDF格式的简历');
      return;
    }
    setUploadedFileName(file.name);
    // 模拟提取结构化数据
    const extracted = mockExtractFromPDF(file.name);
    setResumeFields(extracted);
  };

  // 拖拽事件
  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragActive(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragActive(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      processFile(files[0]);
    }
  };

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      processFile(files[0]);
    }
    // 清空input，允许再次上传同一文件
    e.target.value = '';
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  // 简历字段操作
  const updateField = (id: string, key: string, value: string) => {
    setResumeFields(prev => prev.map(f => f.id === id ? { ...f, key, value } : f));
  };

  const deleteField = (id: string) => {
    setResumeFields(prev => prev.filter(f => f.id !== id));
  };

  const addNewField = () => {
    const newField: ResumeField = {
      id: `field-${Date.now()}`,
      key: '',
      value: '',
    };
    setResumeFields(prev => [...prev, newField]);
  };

  return (
    <div className="app-container">
      {/* 左侧聊天区域 */}
      <section className="chat-section">
        <header className="chat-header">
          <h1>🎓 职途 · AI规划助手</h1>
        </header>

        <div className="messages-container">
          {messages.map(msg => (
            <div key={msg.id} className={`message ${msg.role}`}>
              <div className="message-bubble">{msg.content}</div>
              <div className="message-time">
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <div className="input-wrapper">
            <textarea
              ref={textareaRef}
              className="message-input"
              placeholder="输入你的问题，例如：我想了解前端开发职业路径..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              disabled={isSending}
            />
            <button 
              className="send-button" 
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isSending}
              aria-label="发送"
            >
              ↑
            </button>
          </div>
        </div>
      </section>

      {/* 右侧简历面板 */}
      <aside className={`resume-section ${collapsed ? 'collapsed' : ''}`}>
        <div className="resume-header">
          <h2>
            <span>📄</span> 
            {!collapsed && '简历信息'}
          </h2>
          <button 
            className="collapse-toggle" 
            onClick={() => setCollapsed(!collapsed)}
            aria-label={collapsed ? '展开' : '收起'}
          >
            {collapsed ? '◀' : '▶'}
          </button>
        </div>

        <div className="resume-content">
          {/* 上传区域 */}
          <div
            className={`upload-area ${isDragActive ? 'drag-active' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={triggerFileInput}
          >
            <div className="upload-icon">📎</div>
            <div className="upload-text">
              {uploadedFileName ? `已上传: ${uploadedFileName}` : '拖拽PDF简历或点击上传'}
            </div>
            <div className="upload-hint">支持 .pdf 格式，上传后将自动提取关键信息</div>
            <input
              type="file"
              ref={fileInputRef}
              className="hidden-input"
              accept=".pdf,application/pdf"
              onChange={handleFileSelect}
            />
          </div>

          {uploadedFileName && (
            <div className="file-info">
              <span>✅</span>
              <span>{uploadedFileName}</span>
            </div>
          )}

          {/* 结构化字段编辑器 */}
          <div className="fields-editor">
            {resumeFields.length === 0 ? (
              <div className="empty-fields">
                暂无结构化信息，请上传简历或手动添加
              </div>
            ) : (
              resumeFields.map(field => (
                <div key={field.id} className="field-item">
                  <div className="field-inputs">
                    <input
                      type="text"
                      className="field-key-input"
                      placeholder="字段"
                      value={field.key}
                      onChange={(e) => updateField(field.id, e.target.value, field.value)}
                    />
                    <input
                      type="text"
                      className="field-value-input"
                      placeholder="内容"
                      value={field.value}
                      onChange={(e) => updateField(field.id, field.key, e.target.value)}
                    />
                  </div>
                  <button 
                    className="delete-field-btn" 
                    onClick={() => deleteField(field.id)}
                    aria-label="删除字段"
                  >
                    🗑️
                  </button>
                </div>
              ))
            )}
            
            <button className="add-field-btn" onClick={addNewField}>
              <span>+</span> 添加字段
            </button>
          </div>
          
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '8px', textAlign: 'center' }}>
            点击发送时将携带以上信息
          </div>
        </div>
      </aside>
    </div>
  );
};

export default CareerAssistant;