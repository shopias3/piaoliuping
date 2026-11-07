import { request } from './request'

// 投瓶：城市 / 人群 / 瓶签 / 心愿内容
export const throwBottle = (data) => request('/bottles', 'POST', data)

// 捞瓶：城市 + 人群 + 想要的瓶签（多选），服务端加权随机
export const pickBottle = (q) => request('/bottles/random', 'GET', q)

// 打开 open / 放回 back / 回应 reply
export const bottleAction = (id, action, extra = {}) =>
  request('/bottles/' + id + '/action', 'POST', { action, ...extra })

// 我的瓶子（投出的 + 回应过的）
export const myBottles = () => request('/bottles/mine', 'GET')
