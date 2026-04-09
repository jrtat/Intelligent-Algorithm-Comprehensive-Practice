// App.tsx
import React, { useState, useEffect, useMemo } from 'react';
import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
  ZoomableGroup,
} from 'react-simple-maps';
import { geoCentroid } from 'd3-geo';
import * as XLSX from 'xlsx';
import './App.css';

// 中国地图 GeoJSON (存放在 public/map/china.json)
const GEO_URL = '/map/china.json';
// 默认 Excel 数据文件路径
const DATA_URL = '/data/城市分类_地址_公司规模_薪资_岗位详情HTML_清洗后招聘信息.xlsx';

// 类型定义
interface JobRecord {
  岗位名称?: string;
  省?: string;
  [key: string]: any;
}

interface ProvinceStat {
  name: string;        // 标准化后的省名（用于匹配）
  originalName: string;
  count: number;
  centroid: [number, number] | null;
  feature: any;
}

// 标准化省份名称，用于匹配 GeoJSON 中的 name 字段
const normalizeProvince = (name: string): string => {
  if (!name) return '';
  let cleaned = name.trim();
  // 移除常见后缀
  cleaned = cleaned
    .replace(/省$/, '')
    .replace(/市$/, '')
    .replace(/自治区$/, '')
    .replace(/壮族自治区$/, '')
    .replace(/回族自治区$/, '')
    .replace(/维吾尔自治区$/, '')
    .replace(/特别行政区$/, '');
  // 特殊简称映射
  const map: Record<string, string> = {
    '广西': '广西',
    '内蒙古': '内蒙古',
    '宁夏': '宁夏',
    '新疆': '新疆',
    '西藏': '西藏',
    '香港': '香港',
    '澳门': '澳门',
  };
  return map[cleaned] || cleaned;
};

const App: React.FC = () => {
  const [excelData, setExcelData] = useState<JobRecord[]>([]);
  const [jobTitles, setJobTitles] = useState<string[]>([]);
  const [selectedJob, setSelectedJob] = useState<string>('');
  const [geoData, setGeoData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [hoveredProvince, setHoveredProvince] = useState<{ name: string; count: number } | null>(null);

  // 加载 GeoJSON 地图数据
  useEffect(() => {
    fetch(GEO_URL)
      .then(res => res.json())
      .then(data => setGeoData(data))
      .catch(err => console.error('加载地图数据失败:', err));
  }, []);

  // 自动从 public/data/ 目录加载默认 Excel 文件
  useEffect(() => {
    const loadDefaultExcel = async () => {
      try {
        setLoading(true);
        const response = await fetch(DATA_URL);
        if (!response.ok) {
          throw new Error(`文件加载失败: ${response.status}`);
        }
        const arrayBuffer = await response.arrayBuffer();
        const workbook = XLSX.read(arrayBuffer, { type: 'array' });
        const sheetName = workbook.SheetNames[0];
        const sheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json<JobRecord>(sheet);
        setExcelData(jsonData);

        // 提取去重后的岗位名称
        const titles = Array.from(
          new Set(
            jsonData
              .map(row => row['岗位名称']?.toString().trim())
              .filter((name): name is string => !!name)
          )
        ).sort();
        setJobTitles(titles);
      } catch (error) {
        console.error('自动加载 Excel 失败:', error);
        alert('无法加载招聘数据，请确保 public/data/jobs.xlsx 文件存在。');
      } finally {
        setLoading(false);
      }
    };

    loadDefaultExcel();
  }, []);

  // 根据选中岗位计算省份统计
  const provinceStats = useMemo((): ProvinceStat[] | null => {
    if (!selectedJob || !geoData) return null;

    const filtered = excelData.filter(
      row => row['岗位名称']?.toString().trim() === selectedJob && row['省']?.toString().trim()
    );

    // 按省聚合
    const countMap = new Map<string, number>();
    filtered.forEach(row => {
      const raw = row['省']!.toString().trim();
      if (!raw) return;
      const normalized = normalizeProvince(raw);
      countMap.set(normalized, (countMap.get(normalized) || 0) + 1);
    });

    // 构建统计数组并匹配 GeoJSON feature
    const features = geoData.features;
    const stats: ProvinceStat[] = [];

    for (const [normName, count] of countMap.entries()) {
      // 在 GeoJSON 中寻找匹配的省份 (properties.name 标准化后比较)
      const feature = features.find((f: any) => {
        const propName = f.properties?.name;
        if (!propName) return false;
        return normalizeProvince(propName) === normName;
      });

      if (feature) {
        const centroid = geoCentroid(feature);
        stats.push({
          name: normName,
          originalName: feature.properties.name,
          count,
          centroid,
          feature,
        });
      } else {
        console.warn(`未找到匹配的地理信息: ${normName}`);
      }
    }

    return stats.sort((a, b) => b.count - a.count);
  }, [selectedJob, excelData, geoData]);

  // 总记录数（用于占比计算）
  const totalCount = useMemo(() => {
    if (!provinceStats) return 0;
    return provinceStats.reduce((sum, s) => sum + s.count, 0);
  }, [provinceStats]);

  const maxCount = useMemo(() => {
    if (!provinceStats || provinceStats.length === 0) return 0;
    return Math.max(...provinceStats.map(s => s.count));
  }, [provinceStats]);

  // 根据数量和最大值计算颜色 (绿 -> 红)
  const getColor = (count: number): string => {
    if (maxCount === 0) return '#10b981'; // 绿色
    const ratio = count / maxCount;
    // 绿色 hsl(120, 70%, 50%) → 红色 hsl(0, 70%, 50%)
    const hue = 120 - ratio * 120;
    return `hsl(${hue}, 70%, 55%)`;
  };

  // 计算半径 (基础6，根据数量增大)
  const getRadius = (count: number): number => {
    if (maxCount === 0) return 7;
    const base = 7;
    const ratio = count / maxCount;
    return base + ratio * 10; // 最大约17
  };

  // 判断是否占比 > 10%
  const isHighRatio = (count: number): boolean => {
    if (totalCount === 0) return false;
    return count / totalCount > 0.1;
  };

  // 确认按钮点击（触发视图更新）
  const handleConfirm = () => {
    // 实际统计已通过 useMemo 自动响应
  };

  return (
    <div className="app-container">
      <div className="control-panel">
        <div className="select-wrapper">
          <span className="select-label">选择岗位：</span>
          <select
            className="job-select"
            value={selectedJob}
            onChange={(e) => setSelectedJob(e.target.value)}
            disabled={jobTitles.length === 0}
          >
            <option value="">-- 请选择 --</option>
            {jobTitles.map(title => (
              <option key={title} value={title}>{title}</option>
            ))}
          </select>
        </div>

        <button
          className="confirm-btn"
          onClick={handleConfirm}
          disabled={!selectedJob}
        >
          确认分布
        </button>

        {totalCount > 0 && (
          <div className="stats-info">
            📊 {selectedJob} · 共 {totalCount} 个职位 · {provinceStats?.length || 0} 个省份
          </div>
        )}
      </div>

      <div className="map-wrapper">
        {loading && <div className="loading-overlay">加载数据中...</div>}

        <ComposableMap
          projection="geoMercator"
          projectionConfig={{
            scale: 700,
            center: [105, 36],
          }}
          style={{ width: '100%', height: '100%' }}
        >
          <ZoomableGroup zoom={1} maxZoom={5} center={[105, 36]}>
            {/* 绘制中国地图底图 */}
            <Geographies geography={geoData}>
              {({ geographies }) =>
                geographies.map((geo) => (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    fill="#d9e2ec"
                    stroke="#a0b8cc"
                    strokeWidth={0.6}
                    style={{
                      default: { outline: 'none' },
                      hover: { fill: '#cbd6e4', outline: 'none' },
                      pressed: { outline: 'none' },
                    }}
                  />
                ))
              }
            </Geographies>

            {/* 渲染标记点 */}
            {provinceStats && provinceStats.map((stat) => {
              if (!stat.centroid) return null;
              const [lng, lat] = stat.centroid;
              const color = getColor(stat.count);
              const radius = getRadius(stat.count);
              const highRatio = isHighRatio(stat.count);
              const isHovered = hoveredProvince?.name === stat.name;
              const displayRadius = isHovered ? radius + 4 : radius;

              return (
                <Marker
                  key={stat.name}
                  coordinates={[lng, lat]}
                  onMouseEnter={() => setHoveredProvince({ name: stat.name, count: stat.count })}
                  onMouseLeave={() => setHoveredProvince(null)}
                >
                  <g className="marker-group">
                    {/* 脉动外圈：SVG animate 保证圆心不变 */}
                    {highRatio && (
                      <circle
                        cx={0}
                        cy={0}
                        fill="none"
                        stroke={color}
                        strokeWidth={2.5}
                        r={displayRadius}
                        opacity="0.7"
                      >
                        <animate
                          attributeName="r"
                          values={`${displayRadius};${displayRadius * 2.2};${displayRadius}`}
                          dur="2.2s"
                          repeatCount="indefinite"
                        />
                        <animate
                          attributeName="opacity"
                          values="0.7;0.1;0.7"
                          dur="2.2s"
                          repeatCount="indefinite"
                        />
                      </circle>
                    )}
                    {/* 主标记圆 */}
                    <circle
                      cx={0}
                      cy={0}
                      r={displayRadius}
                      fill={color}
                      stroke="#ffffff"
                      strokeWidth={1.8}
                      style={{ transition: 'r 0.15s ease, fill 0.2s', cursor: 'pointer' }}
                    />
                    {/* 内圈高亮 */}
                    <circle
                      cx={0}
                      cy={0}
                      r={displayRadius * 0.4}
                      fill="rgba(255,255,255,0.35)"
                      pointerEvents="none"
                    />
                  </g>
                </Marker>
              );
            })}
          </ZoomableGroup>
        </ComposableMap>

        {/* 悬停提示 */}
        {hoveredProvince && (
          <div className="tooltip-hover">
            📍 {hoveredProvince.name} · 岗位数 {hoveredProvince.count}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;