/**
 * 统一请求封装：token 注入、统一 code/msg/data 结构、401 处理。
 * H5 走 vite 代理（相对路径）；App 打包时改 BASE 为服务器域名。
 */
// #ifdef H5
const BASE = '/api/v1'
// #endif
// #ifndef H5
// App / 小程序：打包前改成你的服务器地址（需 HTTPS + 备案域名）
const BASE = 'http://127.0.0.1:8010/api/v1'
// #endif

// 供 uni.uploadFile 等直接拼地址使用（含 /api/v1 前缀）
export const API_BASE = BASE

export function getToken() {
  return uni.getStorageSync('token') || ''
}

export function request(url, method = 'GET', data = {}) {
  return new Promise((resolve, reject) => {
    const token = getToken()
    uni.request({
      url: BASE + url,
      method,
      data,
      timeout: 10000,
      header: token ? { Authorization: 'Bearer ' + token } : {},
      success(res) {
        const body = res.data
        if (res.statusCode === 200 && body && body.code === 0) {
          resolve(body.data)
          return
        }
        if (res.statusCode === 401) {
          uni.removeStorageSync('token')
          uni.showToast({ title: (body && body.detail) || '请先登录', icon: 'none' })
          reject(new Error((body && body.detail) || '未登录'))
          return
        }
        const msg = (body && (body.detail || body.msg)) || ('请求失败 HTTP ' + res.statusCode)
        reject(new Error(msg))
      },
      fail(err) {
        reject(new Error((err && err.errMsg) || '网络异常，请稍后再试'))
      }
    })
  })
}

export function toastError(e) {
  uni.showToast({ title: (e && e.message) || '操作失败', icon: 'none' })
}
