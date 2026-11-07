import { defineStore } from 'pinia'
import { getMe, login as apiLogin, updateMe } from '../api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: uni.getStorageSync('token') || '',
    profile: null,          // {id, nickname, region, interest_tags, activity_score, tier, today...}
    bigFont: uni.getStorageSync('big_font') === 1,
    loading: false
  }),
  getters: {
    isLoggedIn: (s) => !!s.token,
    score: (s) => (s.profile ? s.profile.activity_score : 0),
    tier: (s) => (s.profile ? s.profile.tier : '静水深流')
  },
  actions: {
    async login(phone, code) {
      const data = await apiLogin({ phone, code })
      this.token = data.token
      uni.setStorageSync('token', data.token)
      this.profile = data.profile
      return data.profile
    },
    async fetchProfile() {
      if (!this.token) return null
      this.loading = true
      try {
        this.profile = await getMe()
        if (this.profile.big_font !== undefined) {
          this.bigFont = !!this.profile.big_font
          uni.setStorageSync('big_font', this.bigFont ? 1 : 0)
        }
        return this.profile
      } finally {
        this.loading = false
      }
    },
    async updateProfile(data) {
      await updateMe(data)
      await this.fetchProfile()
    },
    async toggleBigFont() {
      this.bigFont = !this.bigFont
      uni.setStorageSync('big_font', this.bigFont ? 1 : 0)
      if (this.token) {
        try { await updateMe({ big_font: this.bigFont }) } catch (e) { /* 离线容忍 */ }
      }
    },
    logout() {
      this.token = ''
      this.profile = null
      uni.removeStorageSync('token')
    }
  }
})
