// 单条岗位数据
export interface Job {
  岗位编码: string
  岗位名称: string
  公司名称: string
  地址: string
  薪资范围: string
  岗位详情: string
  岗位来源地址: string
  学历要求: string
  毕业院校要求: string
  创新能力: number
  抗压能力: number
  沟通能力: number
  学习能力: number
  实习能力: number
  职业技能: string[]
  证书要求: string[]
  职位晋升: string[]
  月薪范围: number[]
}

// 岗位集合（JSON 格式为对象，key 是岗位编码）
export type JobsMap = Record<string, Job>

// 城市数据
export interface City {
  地址: string
  jobs: string[]
  城市坐标: number[]
  城市水平: string
}
export type CitiesMap = Record<string, City>

// 城市索引签名辅助类型
export interface CitiesByAddress {
  [address: string]: City
}

// 行业数据
export interface Industry {
  所属行业: string
  companies: string[]
}
export type IndustriesMap = Record<string, Industry>

// 行业索引签名辅助类型
export interface IndustriesByName {
  [name: string]: Industry
}

// 筛选条件
export interface FilterState {
  keyword: string
  城市: string
  城市水平: string
  行业: string
  学历: string
}
