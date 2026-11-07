import { defineStore } from 'pinia'
import { getRegionTree } from '../api/common'

const RESIDENT_KEY = 'resident_region'
const RECENT_KEY = 'recent_regions'

export const useRegionStore = defineStore('region', {
  state: () => ({
    tree: [],                 // 三级行政区划树
    treeLoaded: false,
    resident: uni.getStorageSync(RESIDENT_KEY) || null,   // 常驻地区 {provinceId, cityId, province, city, district}
    recents: uni.getStorageSync(RECENT_KEY) || []          // 最近使用
  }),
  actions: {
    async loadTree(force = false) {
      if (this.treeLoaded && !force) return this.tree
      const data = await getRegionTree()
      this.tree = data || []
      this.treeLoaded = true
      return this.tree
    },
    persist() {
      uni.setStorageSync(RESIDENT_KEY, this.resident)
      uni.setStorageSync(RECENT_KEY, this.recents.slice(0, 5))
    },
    setRegion(sel, { remember = true } = {}) {
      // sel: {provinceId, cityId, districtId?, province, city, district?}
      this.resident = sel
      if (remember) {
        const label = [sel.province, sel.city, sel.district].filter(Boolean).join(' ')
        this.recents = [ { label, ...sel },
          ...this.recents.filter(r => r.label !== label) ].slice(0, 5)
      }
      this.persist()
    },
    get cityId() {
      return this.resident ? this.resident.cityId : 0
    }
  }
})
