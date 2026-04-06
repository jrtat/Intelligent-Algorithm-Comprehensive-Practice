import { useMemo, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import jobsData from '../../data/jobs.json';
import citiesData from '../../data/cities.json';
import type { Job, City } from '../../types/job';
import mapImage from '../../assets/map.png';
import './job-map.css';

// 颜色调色板 - 相同岗位名称使用相同颜色
const colorPalette = [
  '#4a90d9', '#276749', '#e74c3c', '#f39c12', '#9b59b6',
  '#1abc9c', '#e91e63', '#3f51b5', '#009688', '#795548',
  '#607d8b', '#ff5722', '#cddc39', '#03a9f4', '#9c27b0'
];

export function JobMapPage() {
  const [selectedJobName, setSelectedJobName] = useState('');

  // 获取所有唯一的岗位名称
  const jobNames = useMemo(() => {
    const names = new Set<string>();
    Object.values(jobsData as Record<string, Job>).forEach(job => {
      names.add(job.岗位名称);
    });
    return Array.from(names).sort();
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

  const cities = useMemo(() => {
    return filteredJobs.map(j => citiesData[j.地址 as keyof typeof citiesData]).filter(Boolean) as City[];
  }, [filteredJobs]);

  const uniqueCities = useMemo(() => {
    return Array.from(new Set(filteredJobs.map(j => j.地址)));
  }, [filteredJobs]);

  // 为选中的岗位分配固定颜色
  const getJobColor = (name: string) => {
    if (!name) return '#4a90d9';
    const index = name.length % colorPalette.length;
    return colorPalette[index];
  };

  const markerColor = getJobColor(selectedJobName);

  const [lngMin, lngMax] = [73.66, 135.05];
  const [latMin, latMax] = [18.16, 53.55];

  const mapX = useMemo(() => {
    return (lng: number) => ((lng - lngMin) / (lngMax - lngMin)) * 600;
  }, [lngMin, lngMax]);

  const mapY = useMemo(() => {
    return (lat: number) => 500 - ((lat - latMin) / (latMax - latMin)) * 500;
  }, [latMin, latMax]);

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
              // 更新 URL 查询参数
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
        </div>

        {selectedJobName && (
          <div className="map-container">
            <div className="map-image-wrapper">
              <img src={mapImage} alt="中国地图" className="map-image" />
              {cities.map((city, i) => {
                const [lng, lat] = city.城市坐标 as [number, number];
                const x = mapX(lng);
                const y = mapY(lat);
                return (
                  <div key={i} className="map-marker" style={{ left: `${x}px`, top: `${y}px` }}>
                    <div className="marker-dot" style={{ backgroundColor: markerColor }}></div>
                    <span className="marker-label">{city.地址}</span>
                  </div>
                );
              })}
            </div>

            <div className="map-legend">
              <div className="legend-item">
                <span className="legend-color" style={{ backgroundColor: markerColor }}></span>
                <span>{selectedJobName} 岗位 ({filteredJobs.length} 个职位)</span>
              </div>
            </div>
          </div>
        )}

        {!selectedJobName && (
          <div className="map-empty-state">
            <div className="empty-icon">📍</div>
            <p>请选择上方的岗位名称，或查看全部岗位分布</p>
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
}
