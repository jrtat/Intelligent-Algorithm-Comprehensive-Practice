import './filter-bar.css';

interface FilterBarProps {
  filter: {
    keyword: string;
    城市: string;
    城市水平: string;
    行业: string;
    学历: string;
  };
  updateFilter: (key: keyof FilterBarState, value: string) => void;
  resetFilters: () => void;
  allCities: string[];
  allLevels: string[];
  allDegrees: string[];
  allIndustries: string[];
}

export interface FilterBarState {
  keyword: string;
  城市: string;
  城市水平: string;
  行业: string;
  学历: string;
}

export function FilterBar({
  filter,
  updateFilter,
  resetFilters,
  allCities,
  allLevels,
  allDegrees,
  allIndustries,
}: FilterBarProps) {
  return (
    <div className="filters">
      <input
        type="text"
        className="filter-input"
        placeholder="🔍 搜索岗位名称 / 公司名 / 技能..."
        value={filter.keyword}
        onChange={(e) => updateFilter('keyword', e.target.value)}
      />

      <select
        className="filter-select"
        value={filter.城市}
        onChange={(e) => updateFilter('城市', e.target.value)}
      >
        <option value="">全部城市</option>
        {allCities.map((city) => (
          <option key={city} value={city}>
            {city}
          </option>
        ))}
      </select>

      <select
        className="filter-select"
        value={filter.城市水平}
        onChange={(e) => updateFilter('城市水平', e.target.value)}
      >
        <option value="">全部等级</option>
        {allLevels.map((level) => (
          <option key={level} value={level}>
            {level}
          </option>
        ))}
      </select>

      <select
        className="filter-select"
        value={filter.学历}
        onChange={(e) => updateFilter('学历', e.target.value)}
      >
        <option value="">全部学历</option>
        {allDegrees.map((deg) => (
          <option key={deg} value={deg}>
            {deg}
          </option>
        ))}
      </select>

      <select
        className="filter-select"
        value={filter.行业}
        onChange={(e) => updateFilter('行业', e.target.value)}
      >
        <option value="">全部行业</option>
        {allIndustries.map((ind) => (
          <option key={ind} value={ind}>
            {ind}
          </option>
        ))}
      </select>

      <button className="reset-btn" onClick={resetFilters}>
        重置
      </button>
    </div>
  );
}
