import { useMemo, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
  ZoomableGroup,
} from 'react-simple-maps';
import jobsData from '../../data/jobs.json';
import citiesData from '../../data/cities.json';
import type { Job } from '../../types/job';
import './job-map.css';

const GEO_URL = '/map/china.json';

// 中国地图 GeoJSON

// 类型定义
interface CityStat {
  name: string;
  count: number;
  centroid: [number, number] | null;
  jobs: string[];
}

export function JobMapPage() {
  const [selectedJobName, setSelectedJobName] = useState('');
  const [geoData, setGeoData] = useState<any>(null);
  const [hoveredCity, setHoveredCity] = useState<{ name: string; count: number } | null>(null);

  // 获取所有唯一的岗位名称
  const jobNames = useMemo(() => {
    const names = new Set<string>();
    Object.values(jobsData as Record<string, Job>).forEach(job => {
      names.add(job.岗位名称);
    });
    return Array.from(names).sort();
  }, []);

  // 加载 GeoJSON 地图数据
  useEffect(() => {
    fetch(GEO_URL)
      .then(res => res.json())
      .then(data => setGeoData(data))
      .catch(err => console.error('加载地图数据失败:', err));
  }, []);

  // 加载路由中的岗位名称（如果有）
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const jobNameFromUrl = urlParams.get('jobName');
    if (jobNameFromUrl) {
      setSelectedJobName(jobNameFromUrl);
    }
  }, []);

  // 根据选择的岗位名称过滤数据
  const filteredJobs = useMemo(() => {
    if (!selectedJobName) return [];
    return Object.values(jobsData as Record<string, Job>).filter(j => j.岗位名称 === selectedJobName);
  }, [selectedJobName]);

  // 按城市聚合统计
  const cityStats = useMemo((): CityStat[] | null => {
    if (!selectedJobName || !geoData) return null;

    // 统计每个城市的岗位数量
    const countMap = new Map<string, { count: number; jobs: string[] }>();
    filteredJobs.forEach(job => {
      const city = job.地址;
      if (!city) return;
      const existing = countMap.get(city) || { count: 0, jobs: [] };
      existing.count++;
      existing.jobs.push(job.岗位编码);
      countMap.set(city, existing);
    });

    const stats: CityStat[] = [];

    for (const [cityName, data] of countMap.entries()) {
      // 尝试从 citiesData 获取坐标
      const cityInfo = citiesData[cityName as keyof typeof citiesData];
      if (cityInfo && cityInfo.城市坐标) {
        stats.push({
          name: cityName,
          count: data.count,
          centroid: cityInfo.城市坐标 as [number, number],
          jobs: data.jobs,
        });
      }
    }

    return stats.sort((a, b) => b.count - a.count);
  }, [selectedJobName, filteredJobs, geoData]);

  // 总记录数
  const totalCount = useMemo(() => {
    if (!cityStats) return 0;
    return cityStats.reduce((sum, s) => sum + s.count, 0);
  }, [cityStats]);

  const maxCount = useMemo(() => {
    if (!cityStats || cityStats.length === 0) return 0;
    return Math.max(...cityStats.map(s => s.count));
  }, [cityStats]);

  // 根据数量和最大值计算颜色 (绿 -> 红)
  const getColor = (count: number): string => {
    if (maxCount === 0) return '#10b981';
    const ratio = count / maxCount;
    const hue = 120 - ratio * 120;
    return `hsl(${hue}, 70%, 55%)`;
  };

  // 计算半径
  const getRadius = (count: number): number => {
    if (maxCount === 0) return 7;
    const base = 7;
    const ratio = count / maxCount;
    return base + ratio * 10;
  };

  // 判断是否占比 > 10%
  const isHighRatio = (count: number): boolean => {
    if (totalCount === 0) return false;
    return count / totalCount > 0.1;
  };

  // 确认按钮点击
  const handleConfirm = () => {
    // 实际统计已通过 useMemo 自动响应
  };

  const uniqueCities = useMemo(() => {
    return Array.from(new Set(filteredJobs.map(j => j.地址)));
  }, [filteredJobs]);

  return (
    <div className="app">
      <div className="map-page">
        <Link to="/" className="back-btn">← 返回列表</Link>
        <h2>岗位坐标 - 地理分布可视化</h2>
        <p className="subtitle">请选择一个岗位名称查看其在全国的分布情况</p>

        {/* 岗位名称选择器 */}
        <div className="job-selector-container">
          <label htmlFor="job-select">选择岗位名称：</label>
          <select
            id="job-select"
            className="job-select"
            value={selectedJobName}
            onChange={(e) => {
              setSelectedJobName(e.target.value);
              const params = new URLSearchParams(window.location.search);
              if (e.target.value) {
                params.set('jobName', e.target.value);
              } else {
                params.delete('jobName');
              }
              window.history.replaceState({}, '', `${window.location.pathname}?${params.toString()}`);
            }}
          >
            <option value="">全部岗位</option>
            {jobNames.map(name => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>

          <button
            className="confirm-btn"
            onClick={handleConfirm}
            disabled={!selectedJobName}
          >
            确认分布
          </button>

          {totalCount > 0 && (
            <div className="stats-info">
              📊 {selectedJobName} · 共 {totalCount} 个职位 · {cityStats?.length || 0} 个城市
            </div>
          )}
        </div>

        {selectedJobName && (
          <div className="map-wrapper">
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
                {cityStats && cityStats.map((stat) => {
                  if (!stat.centroid) return null;
                  const [lng, lat] = stat.centroid;
                  const color = getColor(stat.count);
                  const radius = getRadius(stat.count);
                  const highRatio = isHighRatio(stat.count);
                  const isHovered = hoveredCity?.name === stat.name;
                  const displayRadius = isHovered ? radius + 4 : radius;

                  return (
                    <Marker
                      key={stat.name}
                      coordinates={[lng, lat]}
                      onMouseEnter={() => setHoveredCity({ name: stat.name, count: stat.count })}
                      onMouseLeave={() => setHoveredCity(null)}
                    >
                      <g className="marker-group">
                        {/* 脉动外圈 */}
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
            {hoveredCity && (
              <div className="tooltip-hover">
                📍 {hoveredCity.name} · 岗位数 {hoveredCity.count}
              </div>
            )}
          </div>
        )}

        {!selectedJobName && (
          <div className="map-empty-state">
            <div className="empty-icon">📍</div>
            <p>请选择上方的岗位名称，或查看全部岗位分布</p>
          </div>
        )}

        {selectedJobName && (
          <div className="map-legend">
            <div className="legend-item">
              <span className="legend-color" style={{ backgroundColor: '#10b981' }}></span>
              <span>{selectedJobName} 岗位 ({filteredJobs.length} 个职位)</span>
            </div>
          </div>
        )}

        {selectedJobName && (
          <div className="map-cities-list">
            <h4>城市列表 ({uniqueCities.length} 个)</h4>
            {uniqueCities.map((city, i) => (
              <span key={i} className="city-tag">{city}</span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};