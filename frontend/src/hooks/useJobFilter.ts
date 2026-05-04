import { useState, useMemo } from 'react';
import jobsData from '../data/jobs.json';
import citiesData from '../data/cities.json';
import industriesData from '../data/industries.json';
import type { Job, FilterState, City, Industry } from '../types/job.ts';

const jobsList: Job[] = Object.values(jobsData);
const allCities = Object.keys(citiesData);
const allLevels = [...new Set(Object.values(citiesData as Record<string, City>).map((c: City) => c.城市水平))].sort();
const allDegrees = [...new Set(jobsList.map(j => j.学历要求))].sort();
const allIndustries = Object.keys(industriesData);

const getCityInfo = (address: string) => {
  const cities = citiesData as unknown as Record<string, City>;
  return cities[address];
};

const getIndustryInfo = (industry: string) => {
  const industries = industriesData as unknown as Record<string, Industry>;
  return industries[industry];
};

export const useJobFilter = () => {
  const [filter, setFilter] = useState<FilterState>({
    keyword: '',
    城市: '',
    城市水平: '',
    行业: '',
    学历: '',
  });

  const filteredJobs = useMemo(() => {
    return jobsList.filter((job) => {
      if (filter.keyword) {
        const kw = filter.keyword.toLowerCase();
        const matchKeyword =
          job.岗位名称.toLowerCase().includes(kw) ||
          job.公司名称.toLowerCase().includes(kw) ||
          job.职业技能.some(s => s.toLowerCase().includes(kw));
        if (!matchKeyword) return false;
      }
      if (filter.城市 && job.地址 !== filter.城市) return false;
      if (filter.城市水平) {
        const cityInfo = getCityInfo(job.地址);
        if (!cityInfo || cityInfo.城市水平 !== filter.城市水平) return false;
      }
      if (filter.学历 && job.学历要求 !== filter.学历) return false;
      if (filter.行业) {
        const industry = getIndustryInfo(filter.行业);
        if (!industry || !industry.companies.includes(job.公司名称)) return false;
      }
      return true;
    });
  }, [filter]);

  const updateFilter = (key: keyof FilterState, value: string) => {
    setFilter(prev => ({ ...prev, [key]: value }));
  };

  const resetFilters = () => {
    setFilter({ keyword: '', 城市: '', 城市水平: '', 行业: '', 学历: '' });
  };

  return {
    filter,
    updateFilter,
    resetFilters,
    filteredJobs,
    allCities,
    allLevels,
    allDegrees,
    allIndustries,
    jobsListLength: jobsList.length
  };
};
