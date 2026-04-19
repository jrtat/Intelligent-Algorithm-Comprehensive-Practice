import { useMemo, useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import * as echarts from 'echarts';
import ReactECharts from 'echarts-for-react';
import jobsData from '../../data/jobs.json';
import type { Job } from '../../types/job';
import '../JobDashboard/job-dashboard.css';
import './job-map.css';

// 类型定义
interface LocationInfo {
  adcode: number;
  name: string;
  center: [number, number];
  centroid?: [number, number];
  level: string;
  parent?: { adcode: number };
  children?: LocationInfo[];
}

interface LocationData {
  [adcode: string]: LocationInfo;
}

interface ProvinceStat {
  adcode: number;
  name: string;
  count: number;
  jobs: string[];
  center: [number, number];
  ratio: number;
}

interface CityStat {
  adcode: number;
  name: string;
  count: number;
  jobs: string[];
  center: [number, number];
  ratio: number;
}

// 城市名称到省份名称的映射
const cityToProvinceMap: Record<string, string> = {
  '北京': '北京市', '上海': '上海市', '天津': '天津市', '重庆': '重庆市',
  '广州': '广东省', '深圳': '广东省', '东莞': '广东省', '珠海': '广东省', '惠州': '广东省', '中山': '广东省',
  '苏州': '江苏省', '南京': '江苏省', '无锡': '江苏省', '常州': '江苏省',
  '杭州': '浙江省', '宁波': '浙江省', '温州': '浙江省',
  '成都': '四川省', '宜宾': '四川省',
  '武汉': '湖北省',
  '西安': '陕西省',
  '郑州': '河南省', '开封': '河南省',
  '济南': '山东省', '烟台': '山东省', '威海': '山东省', '德州': '山东省', '济宁': '山东省',
  '石家庄': '河北省', '唐山': '河北省', '保定': '河北省', '邢台': '河北省', '张家口': '河北省', '承德': '河北省',
  '大连': '辽宁省', '营口': '辽宁省',
  '昆明': '云南省',
  '贵阳': '贵州省', '遵义': '贵州省', '毕节': '贵州省',
  '合肥': '安徽省',
  '南昌': '江西省', '赣州': '江西省',
  '厦门': '福建省',
  '吉林市': '吉林省',
  '晋中': '山西省',
  '阿克苏': '新疆维吾尔自治区',
};

function getProvinceFromAddress(address: string): string | null {
  if (!address) return null;
  const cityPart = address.split('-')[0];
  return cityToProvinceMap[cityPart] || null;
}

function getCityFromAddress(address: string): string | null {
  if (!address) return null;
  return address.split('-')[0];
}

export function JobMapPage() {
  const [selectedJobName, setSelectedJobName] = useState('');
  const [searchKeyword, setSearchKeyword] = useState('');
  const [loading, setLoading] = useState(false);
  const [locationData, setLocationData] = useState<LocationData>({});
  const [chinaGeo, setChinaGeo] = useState<any>(null);
  const [currentLevel, setCurrentLevel] = useState<'country' | 'province'>('country');
  const [currentProvince, setCurrentProvince] = useState<{ adcode: number; name: string; center: [number, number] } | null>(null);
  const [provinceGeo, setProvinceGeo] = useState<any>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const chartRef = useRef<ReactECharts | null>(null);

  // 生成唯一 key，强制重建地图实例，彻底解决实例残留问题
  const mapKey = useMemo(() => {
    return `${currentLevel}-${currentProvince?.adcode || 'country'}-${selectedJobName}`;
  }, [currentLevel, currentProvince, selectedJobName]);

  // 获取所有唯一的岗位名称
  const jobNames = useMemo(() => {
    const names = new Set<string>();
    Object.values(jobsData as Record<string, Job>).forEach(job => {
      names.add(job.岗位名称);
    });
    return Array.from(names).sort();
  }, []);

  const filteredJobNames = useMemo(() => {
    if (!searchKeyword) return jobNames;
    return jobNames.filter(name => name.toLowerCase().includes(searchKeyword.toLowerCase()));
  }, [jobNames, searchKeyword]);

  // 加载中国地图 GeoJSON
  useEffect(() => {
    fetch('/map/china.json')
      .then(res => res.json())
      .then(data => {
        echarts.registerMap('china', data);
        setChinaGeo(data);
      })
      .catch(err => console.error('加载中国地图失败:', err));
  }, []);

  // 加载 location.json
  useEffect(() => {
    fetch('/map/location.json')
      .then(res => res.json())
      .then(data => {
        const locMap: LocationData = {};
        const process = (items: any) => {
          if (!items) return;
          if (Array.isArray(items)) {
            items.forEach((item: LocationInfo) => {
              locMap[item.adcode] = item;
              if (item.children) process(item.children);
            });
          } else {
            Object.values(items).forEach((item: any) => {
              locMap[item.adcode] = item;
              if (item.children) process(item.children);
            });
          }
        };
        process(data);
        setLocationData(locMap);
      })
      .catch(err => console.error('加载location.json失败:', err));
  }, []);

  // 过滤后的岗位列表
  const filteredJobs = useMemo(() => {
    if (!selectedJobName) return [];
    return Object.values(jobsData as Record<string, Job>).filter(j => j.岗位名称 === selectedJobName);
  }, [selectedJobName]);

  // 全国地图：按省份聚合
  const provinceStats = useMemo((): ProvinceStat[] => {
    if (!selectedJobName || filteredJobs.length === 0 || Object.keys(locationData).length === 0) return [];

    const provinceCountMap = new Map<number, { count: number; jobs: string[]; name: string; center: [number, number] }>();

    filteredJobs.forEach(job => {
      const provinceName = getProvinceFromAddress(job.地址);
      if (!provinceName) return;

      const provinceEntry = Object.values(locationData).find(
        loc => loc.name === provinceName && loc.level === 'province'
      );
      if (!provinceEntry) return;

      const existing = provinceCountMap.get(provinceEntry.adcode) || {
        count: 0,
        jobs: [],
        name: provinceEntry.name,
        center: provinceEntry.center as [number, number],
      };
      existing.count++;
      existing.jobs.push(job.岗位编码);
      provinceCountMap.set(provinceEntry.adcode, existing);
    });

    const total = filteredJobs.length;
    return Array.from(provinceCountMap.entries()).map(([adcode, data]) => ({
      adcode,
      name: data.name,
      count: data.count,
      jobs: data.jobs,
      center: data.center,
      ratio: total > 0 ? (data.count / total) * 100 : 0,
    })).sort((a, b) => b.count - a.count);
  }, [selectedJobName, filteredJobs, locationData]);

  // 省份地图：按城市聚合
  const cityStats = useMemo((): CityStat[] => {
    if (!selectedJobName || !currentProvince || filteredJobs.length === 0 || Object.keys(locationData).length === 0) return [];

    const provinceEntry = Object.values(locationData).find(
      loc => loc.adcode === currentProvince.adcode
    );
    if (!provinceEntry || !provinceEntry.children) return [];

    const cityMap = new Map<string, { adcode: number; center: [number, number] }>();
    provinceEntry.children.forEach((city: LocationInfo) => {
      cityMap.set(city.name, { adcode: city.adcode, center: city.center as [number, number] });
    });

    const cityCountMap = new Map<number, { count: number; jobs: string[]; name: string; center: [number, number] }>();

    filteredJobs.forEach(job => {
      const cityName = getCityFromAddress(job.地址);
      if (!cityName) return;

      const cityInfo = cityMap.get(cityName);
      if (!cityInfo) return;

      const existing = cityCountMap.get(cityInfo.adcode) || {
        count: 0,
        jobs: [],
        name: cityName,
        center: cityInfo.center,
      };
      existing.count++;
      existing.jobs.push(job.岗位编码);
      cityCountMap.set(cityInfo.adcode, existing);
    });

    const totalInProvince = filteredJobs.filter(job => {
      const provinceName = getProvinceFromAddress(job.地址);
      return provinceName === currentProvince.name;
    }).length;

    return Array.from(cityCountMap.entries()).map(([adcode, data]) => ({
      adcode,
      name: data.name,
      count: data.count,
      jobs: data.jobs,
      center: data.center,
      ratio: totalInProvince > 0 ? (data.count / totalInProvince) * 100 : 0,
    })).sort((a, b) => b.count - a.count);
  }, [selectedJobName, currentProvince, filteredJobs, locationData]);

  const maxProvinceCount = useMemo(() => {
    if (provinceStats.length === 0) return 0;
    return Math.max(...provinceStats.map(s => s.count));
  }, [provinceStats]);

  const maxCityCount = useMemo(() => {
    if (cityStats.length === 0) return 0;
    return Math.max(...cityStats.map(c => c.count));
  }, [cityStats]);

  const totalJobs = filteredJobs.length;

  // 计算半径
  const getProvinceRadius = (count: number): number => {
    if (maxProvinceCount === 0) return 8;
    const ratio = count / maxProvinceCount;
    return 8 + ratio * 16;
  };

  const getCityRadius = (count: number): number => {
    if (maxCityCount === 0) return 6;
    const ratio = count / maxCityCount;
    return 6 + ratio * 14;
  };

  // 加载省份地图
  const loadProvinceMap = useCallback(async (adcode: number, name: string, center: [number, number]) => {
    setLoading(true);
    setLoadError(null);
    try {
      const response = await fetch(`/map/province/${adcode}.json`);
      if (!response.ok) {
        throw new Error(`加载省份地图失败: ${response.status}`);
      }
      const geo = await response.json();
      // 注销旧地图（如果存在），避免内存泄漏
      const mapName = `province_${adcode}`;
      if (echarts.getMap(mapName)) {
        // ECharts 没有直接注销地图的方法，但重新注册会覆盖
      }
      echarts.registerMap(mapName, geo);
      setProvinceGeo({ geo, adcode });
      setCurrentProvince({ adcode, name, center });
      setCurrentLevel('province');
    } catch (err) {
      console.error('加载省份地图失败:', err);
      setLoadError(`无法加载${name}地图数据，请稍后重试`);
    } finally {
      setLoading(false);
    }
  }, []);

  // 返回全国
  const backToCountry = useCallback(() => {
    setCurrentLevel('country');
    setCurrentProvince(null);
    setProvinceGeo(null);
    setLoadError(null);
  }, []);

  // 点击图表事件
  const onChartClick = useCallback((params: any) => {
    if (currentLevel === 'country') {
      const stat = provinceStats.find(s => s.name === params.data?.name || s.adcode === params.data?.adcode);
      if (stat && stat.count > 0) {
        loadProvinceMap(stat.adcode, stat.name, stat.center);
      }
    }
  }, [currentLevel, provinceStats, loadProvinceMap]);

  // 切换岗位类别
  const handleJobChange = (jobName: string) => {
    setSelectedJobName(jobName);
    backToCountry();
  };

  // 构建散点图数据
  const getScatterData = (stats: ProvinceStat[] | CityStat[], isProvince: boolean) => {
    return stats.map(stat => ({
      name: stat.name,
      value: [...stat.center, stat.count],
      count: stat.count,
      ratio: stat.ratio,
      adcode: stat.adcode,
      shouldPulse: isProvince ? stat.ratio >= 10 : stat.ratio >= 5,
    }));
  };

  // ECharts 配置（只使用 geo + 散点，不再添加额外的地图系列，彻底解决双地图问题）
  const getOption = useCallback(() => {
    const isCountry = currentLevel === 'country';
    const stats = isCountry ? provinceStats : cityStats;
    const maxCount = isCountry ? maxProvinceCount : maxCityCount;
    const getRadius = isCountry ? getProvinceRadius : getCityRadius;

    // 如果没有数据，返回基础配置
    if (stats.length === 0) {
      const mapName = isCountry ? 'china' : (provinceGeo ? `province_${provinceGeo.adcode}` : 'china');
      return {
        geo: {
          map: mapName,
          roam: true,
          zoom: isCountry ? 1.2 : 1.5,
          center: isCountry ? [105, 36] : (currentProvince?.center || [105, 36]),
          itemStyle: { areaColor: '#e8ecf1', borderColor: '#b8c5d6', borderWidth: 0.6 },
          emphasis: { itemStyle: { areaColor: '#d0d8e4' }, label: { show: false } },
          select: { disabled: true },
        },
        series: [],
        tooltip: { show: false },
      };
    }

    // 颜色函数 - 与图例颜色保持一致
    const getColor = (count: number): string => {
      if (maxCount === 0) return isCountry ? '#66ccff' : '#ffaa66';
      const ratio = count / maxCount;
      if (isCountry) {
        // 全国地图：少=#cce0ff, 中=#4a90d9, 多=#1d4ed8
        if (ratio < 0.4) return '#cce0ff';
        if (ratio < 0.7) return '#4a90d9';
        return '#1d4ed8';
      } else {
        // 省份地图：少=#ffd4a8, 中=#ff9933, 多=#cc3300
        if (ratio < 0.4) return '#ffd4a8';
        if (ratio < 0.7) return '#ff9933';
        return '#cc3300';
      }
    };

    const scatterData = getScatterData(stats as any, !isCountry);
    const pulseData = scatterData.filter(d => d.shouldPulse && d.count > 0);
    const normalData = scatterData.filter(d => !d.shouldPulse && d.count > 0);

    const tooltip = {
      trigger: 'item',
      triggerOn: 'mousemove',
      backgroundColor: 'rgba(0, 0, 0, 0.85)',
      borderRadius: 12,
      padding: [12, 18],
      textStyle: { color: '#fff', fontSize: 13 },
      formatter: (params: any) => {
        const data = params.data;
        if (!data) return '';
        const ratioLabel = isCountry ? '全国占比' : '省内占比';
        return `
          <div style="font-weight: 600; font-size: 15px; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid rgba(255,255,255,0.2);">${data.name}</div>
          <div style="display: flex; justify-content: space-between; margin-top: 6px;"><span style="opacity: 0.7;">岗位类别：</span><span>${selectedJobName}</span></div>
          <div style="display: flex; justify-content: space-between; margin-top: 6px;"><span style="opacity: 0.7;">岗位数量：</span><span style="color: #ffaa66; font-weight: 600;">${data.count}</span></div>
          <div style="display: flex; justify-content: space-between; margin-top: 6px;"><span style="opacity: 0.7;">${ratioLabel}：</span><span>${data.ratio.toFixed(1)}%</span></div>
        `;
      },
    };

    const mapName = isCountry ? 'china' : `province_${provinceGeo?.adcode}`;
    const mapCenter = isCountry ? [105, 36] : currentProvince?.center;

    // geo 组件用于底图和散点图
    const geoComponent = {
      map: mapName,
      roam: true,
      zoom: isCountry ? 1.2 : 1.5,
      center: mapCenter,
      itemStyle: { areaColor: '#e8ecf1', borderColor: '#b8c5d6', borderWidth: 0.6 },
      emphasis: { itemStyle: { areaColor: '#d0d8e4' }, label: { show: false } },
      select: { disabled: true },
    };

    const series: any[] = [];

    // 脉动散点
    if (pulseData.length > 0) {
      series.push({
        type: 'effectScatter',
        coordinateSystem: 'geo',
        geoIndex: 0,
        data: pulseData.map(d => ({ name: d.name, value: [d.value[0], d.value[1], d.value[2]], count: d.count, ratio: d.ratio })),
        symbolSize: (val: any) => getRadius(val[2]),
        showEffectOn: 'emphasis',
        rippleEffect: { brushType: 'stroke', scale: 3, period: 4 },
        itemStyle: { color: (params: any) => getColor(params.data.count), borderColor: '#fff', borderWidth: 2 },
        emphasis: { scale: 1.3 },
      });
    }

    // 普通散点
    if (normalData.length > 0) {
      series.push({
        type: 'scatter',
        coordinateSystem: 'geo',
        geoIndex: 0,
        data: normalData.map(d => ({ name: d.name, value: [d.value[0], d.value[1], d.value[2]], count: d.count, ratio: d.ratio })),
        symbolSize: (val: any) => getRadius(val[2]),
        itemStyle: { color: (params: any) => getColor(params.data.count), borderColor: '#fff', borderWidth: 2 },
        emphasis: { scale: 1.3 },
      });
    }

    return { tooltip, geo: geoComponent, series, animation: true, animationDuration: 800, animationEasing: 'cubicOut' };
  }, [currentLevel, provinceStats, cityStats, maxProvinceCount, maxCityCount, provinceGeo, currentProvince, selectedJobName]);

  const onEvents = useMemo(() => ({
    click: onChartClick,
  }), [onChartClick]);

  return (
    <div className="job-dashboard">
      {/* Breadcrumb */}
      <div className="dashboard-breadcrumb">
        <Link to="/" className="breadcrumb-link">首页</Link>
        <span className="breadcrumb-sep">/</span>
        <span className="breadcrumb-current">岗位分布地图</span>
        {currentLevel === 'province' && currentProvince && (
          <>
            <span className="breadcrumb-sep">/</span>
            <span className="breadcrumb-current">{currentProvince.name}</span>
          </>
        )}
      </div>

      {/* Main Content */}
      <div className="dashboard-main" style={{ height: 'calc(100vh - 60px)', display: 'flex', flexDirection: 'column' }}>
        <div className="dashboard-right" style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
          {/* Filter Bar */}
          <div className="filter-card" style={{ flexShrink: 0 }}>
            <div className="filters">
              <input
                type="text"
                className="filter-input"
                placeholder="搜索岗位名称..."
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
              />
              <select
                className="filter-select"
                value={selectedJobName}
                onChange={(e) => handleJobChange(e.target.value)}
              >
                <option value="">请选择岗位类别</option>
                {filteredJobNames.map(name => (
                  <option key={name} value={name}>{name}</option>
                ))}
              </select>
              {currentLevel === 'province' && (
                <button className="back-btn" onClick={backToCountry}>返回全国地图</button>
              )}
            </div>
          </div>

          {/* 横向布局：图例 + 地图 */}
          <div className="map-content-row" style={{ flex: 1, minHeight: 0, display: 'flex', gap: '12px' }}>
            {/* 图例 */}
            {selectedJobName && totalJobs > 0 && (
              <div className="map-legend-inline" style={{ width: '200px', flexShrink: 0 }}>
                <div className="legend-section-inline">
                  <div className="legend-title">标记说明</div>
                  <div className="legend-items">
                    <div className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#cce0ff' }}></span>
                      <span>数量少</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#4a90d9' }}></span>
                      <span>数量中</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#1d4ed8' }}></span>
                      <span>数量多</span>
                    </div>
                    <div className="legend-item">
                      <div className="pulse-demo"></div>
                      <span>脉动</span>
                    </div>
                  </div>
                </div>
                {currentLevel === 'province' && (
                  <div className="legend-section-inline">
                    <div className="legend-title">城市标记</div>
                    <div className="legend-items">
                      <div className="legend-item">
                        <span className="legend-color" style={{ backgroundColor: '#ffd4a8' }}></span>
                        <span>少</span>
                      </div>
                      <div className="legend-item">
                        <span className="legend-color" style={{ backgroundColor: '#ff9933' }}></span>
                        <span>中</span>
                      </div>
                      <div className="legend-item">
                        <span className="legend-color" style={{ backgroundColor: '#cc3300' }}></span>
                        <span>多</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* 地图容器 */}
            <div className="map-wrapper" style={{ flex: 1, minHeight: 0, position: 'relative' }}>
              {loading && (
                <div className="map-loading" style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fff', zIndex: 10 }}>
                  <div className="spinner"></div>
                  <p>加载地图中...</p>
                </div>
              )}

              {loadError && (
                <div className="map-empty-state" style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                  <div className="empty-icon">⚠️</div>
                  <p>{loadError}</p>
                  <button className="back-btn" onClick={backToCountry} style={{ marginTop: '16px' }}>返回全国地图</button>
                </div>
              )}

              {!loadError && !selectedJobName && (
                <div className="map-empty-state" style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                  <div className="empty-icon">🗺️</div>
                  <p>请在上方选择一个岗位类别</p>
                </div>
              )}

              {!loadError && selectedJobName && totalJobs === 0 && !loading && (
                <div className="map-empty-state" style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                  <div className="empty-icon">📭</div>
                  <p>暂无「{selectedJobName}」岗位分布数据</p>
                </div>
              )}

              {!loadError && selectedJobName && totalJobs > 0 && (
                <ReactECharts
                  key={mapKey}
                  ref={(e) => { if (e) chartRef.current = e; }}
                  option={getOption()}
                  style={{ width: '100%', height: '100%' }}
                  onEvents={onEvents}
                  opts={{ renderer: 'canvas' }}
                  notMerge={true}
                  lazyUpdate={false}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}