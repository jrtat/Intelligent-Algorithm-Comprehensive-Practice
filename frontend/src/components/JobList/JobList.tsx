import { FilterBar } from '../FilterBar/FilterBar';
import { JobCard } from './JobCard';
import { useJobFilter } from '../../hooks/useJobFilter';
import './job-list.css';

export function JobList() {
  const {
    filter,
    updateFilter,
    resetFilters,
    filteredJobs,
    allCities,
    allLevels,
    allDegrees,
    allIndustries,
    jobsListLength
  } = useJobFilter();

  return (
    <div className="app">
      <header className="header">
        <h1>📊 岗位数据看板</h1>
        <p className="subtitle">共 {jobsListLength} 条岗位 · 当前展示 {filteredJobs.length} 条</p>
      </header>

      <FilterBar
        filter={filter}
        updateFilter={updateFilter}
        resetFilters={resetFilters}
        allCities={allCities}
        allLevels={allLevels}
        allDegrees={allDegrees}
        allIndustries={allIndustries}
      />

      <div className="job-list">
        {filteredJobs.length === 0 ? (
          <p className="empty">没有找到匹配的岗位 😢</p>
        ) : (
          filteredJobs.map(job => <JobCard key={job.岗位编码} job={job} />)
        )}
      </div>
    </div>
  );
}
