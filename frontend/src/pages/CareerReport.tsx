import React from 'react';
import { PageDashboard } from '../components/PageDashboard/PageDashboard';

export default function CareerReport() {
  return (
    <PageDashboard
      title="职业报告与行动计划"
      subtitle="资深 UX 架构师路径 • 2024 秋季策略"
      showBreadcrumb
      breadcrumbItems={[
        { label: '首页', href: '/' },
        { label: '职业报告' },
      ]}
    >
    <div className="space-y-8">

      {/* Bento Grid Layout */}
      <div className="grid grid-cols-12 gap-6">
        {/* Main Report Preview (Asymmetric Focus) */}
        <section className="col-span-12 lg:col-span-8 bg-surface-container-lowest rounded-xl p-8 shadow-sm">
          <div className="flex justify-between items-center mb-8">
            <h3 className="text-xl font-bold">执行策略报告</h3>
            <div className="flex gap-2">
              <span className="px-3 py-1 bg-surface-container text-on-surface-variant text-xs font-bold rounded-full">上次同步：2小时前</span>
            </div>
          </div>

          {/* Notion-style Block Editor */}
          <div className="space-y-6 text-on-surface-variant leading-relaxed">
            <div className="group relative">
              <h4 className="text-lg font-bold text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-sm opacity-0 group-hover:opacity-40 absolute -left-6">drag_indicator</span>
                1. 职业轨迹分析
              </h4>
              <p className="mt-2 pl-4 border-l-2 border-primary/20">
                您目前的技能画像在 <span className="text-primary font-medium">交互设计</span> 和 <span className="text-primary font-medium">用户研究</span> 方面拥有坚实的基础。为了向资深架构师转型，识别出的主要差距是 <span className="italic text-tertiary font-medium">可扩展系统思维</span>。
              </p>
            </div>

            <div className="group relative">
              <h4 className="text-lg font-bold text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-sm opacity-0 group-hover:opacity-40 absolute -left-6">drag_indicator</span>
                2. 战略差异化
              </h4>
              <div className="mt-2 bg-surface p-6 rounded-lg italic text-on-surface">
                “候选人应专注于构建能够展示决策框架的作品集，而不仅仅是最终的视觉像素，尤其是在多产品生态系统中。”
              </div>
            </div>

            <div className="group relative">
              <h4 className="text-lg font-bold text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-sm opacity-0 group-hover:opacity-40 absolute -left-6">drag_indicator</span>
                3. 市场契合度
              </h4>
              <p className="mt-2 pl-4 border-l-2 border-primary/20">
                目前金融科技和医疗科技领域的招聘趋势优先考虑理解 <span className="font-medium text-on-surface">SOC2 合规性</span> 和 <span className="font-medium text-on-surface">大规模无障碍设计</span> 的架构师。
              </p>
            </div>

            <div className="mt-8 border-t border-dashed border-outline-variant pt-4 flex items-center gap-4 text-outline cursor-text">
              <span className="material-symbols-outlined">add</span>
              <span className="text-sm">点击添加自定义洞察或笔记...</span>
            </div>
          </div>
        </section>

        {/* Milestone Cards */}
        <aside className="col-span-12 lg:col-span-4 space-y-6">
          <div className="bg-surface-container-low rounded-xl p-6">
            <h3 className="text-sm font-black uppercase tracking-widest text-on-surface-variant mb-6">即将到来的里程碑</h3>
            <div className="space-y-6">
              {/* Milestone 1 */}
              <div className="relative pl-8">
                <div className="absolute left-0 top-0 h-full w-0.5 bg-outline-variant"></div>
                <div className="absolute left-[-5px] top-0 w-3 h-3 rounded-full bg-secondary ring-4 ring-secondary-container/30"></div>
                <p className="text-xs font-bold text-secondary mb-1">已完成</p>
                <h4 className="font-bold text-sm">作品集审计</h4>
                <p className="text-xs mt-1 text-on-surface-variant">根据资深专家的反馈审查 5 个核心项目。</p>
              </div>

              {/* Milestone 2 */}
              <div className="relative pl-8">
                <div className="absolute left-0 top-0 h-full w-0.5 bg-outline-variant"></div>
                <div className="absolute left-[-5px] top-0 w-3 h-3 rounded-full bg-primary ring-4 ring-primary-container/30"></div>
                <p className="text-xs font-bold text-primary mb-1">进行中 (65%)</p>
                <h4 className="font-bold text-sm">面向设计师的 Python</h4>
                <p className="text-xs mt-1 text-on-surface-variant">完成 Coursera 上的自动化模块。</p>
                <div className="w-full bg-surface-container-highest h-1 rounded-full mt-3 overflow-hidden">
                  <div className="bg-primary h-full w-[65%]"></div>
                </div>
              </div>

              {/* Milestone 3 */}
              <div className="relative pl-8">
                <div className="absolute left-[-5px] top-0 w-3 h-3 rounded-full bg-outline-variant"></div>
                <p className="text-xs font-bold text-on-surface-variant mb-1">下周</p>
                <h4 className="font-bold text-sm">设计领导力研讨会</h4>
                <p className="text-xs mt-1 text-on-surface-variant">与 Google 导师进行的 3 小时高强度会议。</p>
              </div>
            </div>
          </div>
        </aside>

        {/* Interactive Timeline (Gantt-Style) */}
        <section className="col-span-12 bg-surface-container-lowest rounded-xl p-8 shadow-sm">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h3 className="text-xl font-bold">执行时间表</h3>
              <p className="text-sm text-on-surface-variant">2024 年第三季度 - 第四季度规划蓝图</p>
            </div>
            <div className="flex bg-surface rounded-lg p-1">
              <button className="px-4 py-1 text-xs font-bold bg-white shadow-sm rounded-md text-on-surface">按月</button>
              <button className="px-4 py-1 text-xs font-bold text-on-surface-variant">按季度</button>
            </div>
          </div>

          <div className="overflow-x-auto no-scrollbar">
            <div className="min-w-[1000px]">
              {/* Timeline Header */}
              <div className="grid grid-cols-12 border-b border-outline-variant pb-4 mb-6">
                <div className="col-span-3 text-xs font-black text-outline uppercase tracking-wider">行动项</div>
                <div className="col-span-3 text-xs font-black text-outline uppercase tracking-wider text-center">九月</div>
                <div className="col-span-3 text-xs font-black text-outline uppercase tracking-wider text-center">十月</div>
                <div className="col-span-3 text-xs font-black text-outline uppercase tracking-wider text-center">十一月</div>
              </div>

              {/* Timeline Rows */}
              <div className="space-y-6">
                {/* Row 1 */}
                <div className="grid grid-cols-12 items-center">
                  <div className="col-span-3 flex items-center gap-3">
                    <span className="material-symbols-outlined text-primary text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>terminal</span>
                    <span className="text-sm font-bold">Python 课程</span>
                  </div>
                  <div className="col-span-9 relative h-8">
                    <div className="absolute left-0 w-2/5 h-full bg-primary/20 rounded-lg flex items-center px-3 border border-primary/30">
                      <span className="text-[10px] font-bold text-primary truncate">模块：自动化与脚本</span>
                    </div>
                  </div>
                </div>

                {/* Row 2 */}
                <div className="grid grid-cols-12 items-center">
                  <div className="col-span-3 flex items-center gap-3">
                    <span className="material-symbols-outlined text-secondary text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>draw</span>
                    <span className="text-sm font-bold">UI 案例研究</span>
                  </div>
                  <div className="col-span-9 relative h-8">
                    <div className="absolute left-[30%] w-1/3 h-full bg-secondary/20 rounded-lg flex items-center px-3 border border-secondary/30">
                      <span className="text-[10px] font-bold text-secondary truncate">撰写高保真视图</span>
                    </div>
                  </div>
                </div>

                {/* Row 3 */}
                <div className="grid grid-cols-12 items-center">
                  <div className="col-span-3 flex items-center gap-3">
                    <span className="material-symbols-outlined text-tertiary text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>work</span>
                    <span className="text-sm font-bold">UX 实习申请</span>
                  </div>
                  <div className="col-span-9 relative h-8">
                    <div className="absolute left-[60%] w-1/4 h-full bg-tertiary/20 rounded-lg flex items-center px-3 border border-tertiary/30">
                      <span className="text-[10px] font-bold text-tertiary truncate">申请：Meta/Adobe</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
    </PageDashboard>
  );
}
