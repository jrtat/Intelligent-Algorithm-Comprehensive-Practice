import { useMemo } from 'react';
import { Link, useLocation } from 'react-router-dom';
import jobsData from '../../data/jobs.json';
import citiesData from '../../data/cities.json';
import type { Job, City } from '../../types/job';
import mapImage from '../../assets/map.png';
import './job-map.css';

export function JobMapPage() {
  const location = useLocation();
  const jobName = useMemo(() => {
    return (location.state as { jobName?: string })?.jobName || '';
  }, [location.state]);

  const jobsList = useMemo(() => {
    return Object.values(jobsData as Record<string, Job>);
  }, []);

  const similarJobs = useMemo(() => {
    return jobsList.filter(j => j.岗位名称 === jobName);
  }, [jobName, jobsList]);

  const cities = useMemo(() => {
    return similarJobs.map(j => citiesData[j.地址 as keyof typeof citiesData]).filter(Boolean) as City[];
  }, [similarJobs]);

  const uniqueCities = useMemo(() => {
    return Array.from(new Set(similarJobs.map(j => j.地址)));
  }, [similarJobs]);

  const [lngMin, lngMax] = [73.66, 135.05];
  const [latMin, latMax] = [18.16, 53.55];

  const mapX = useMemo(() => {
    return (lng: number) => ((lng - lngMin) / (lngMax - lngMin)) * 600;
  }, [lngMin, lngMax]);

  const mapY = useMemo(() => {
    return (lat: number) => 500 - ((lat - latMin) / (latMax - latMin)) * 500;
  }, [latMin, latMax]);

  const colors = ['#4a90d9', '#276749', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#e91e63', '#3f51b5'];
  const markerColor = colors[jobName.length % colors.length];

  return (
    <div className="app">
      <div className="map-page">
        <Link to="/" className="back-btn">← 返回列表</Link>
        <h2>{jobName} - 岗位地图分布</h2>
        <p className="subtitle">共 {similarJobs.length} 个岗位 · {uniqueCities.length} 个城市</p>

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
              <span>{jobName} 岗位</span>
            </div>
          </div>
        </div>

        <div className="map-cities-list">
          <h4>城市列表</h4>
          {uniqueCities.map((city, i) => (
            <span key={i} className="city-tag">{city}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
