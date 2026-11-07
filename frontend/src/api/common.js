import { request } from './request'

// 三级行政区划树
export const getRegionTree = () => request('/regions/tree', 'GET')

// 背景主题库（10 大主题）
export const getBackgrounds = (theme) =>
  request('/backgrounds' + (theme ? '?theme=' + encodeURIComponent(theme) : ''), 'GET')

// 关于我们页内容（规则 + 合规声明 + 协议）
export const getAboutConfig = () => request('/config/about', 'GET')

// 一键举报
export const reportTarget = (data) => request('/reports', 'POST', data)
