import { request } from './request'

// 发送短信验证码（60 秒频控，演示模式返回 mock_code）
export const sendSms = (phone) => request('/auth/sms/send', 'POST', { phone })

// 验证码登入：已注册直接登录，未注册自动注册
export const login = ({ phone, code }) =>
  request('/auth/login', 'POST', { phone, code, agreed: true })

// 个人信息 + 活跃度 + 段位
export const getMe = () => request('/user/me', 'GET')

// 更新地区 / 兴趣标签 / 大字模式等
export const updateMe = (data) => request('/user/me', 'PUT', data)
