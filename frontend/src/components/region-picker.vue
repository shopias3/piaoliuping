<template>
  <view v-if="visible" class="rp-mask" @click="$emit('close')">
    <view class="rp-panel" @click.stop>
      <view class="rp-head">
        <text class="rp-title">选择地区</text>
        <text class="rp-close" @click="$emit('close')">✕</text>
      </view>

      <input class="rp-search" v-model="keyword" placeholder="搜索省份 / 城市" />

      <view v-if="recents.length" class="rp-recent">
        <text class="rp-recent-label">最近：</text>
        <text v-for="(r, i) in recents" :key="i" class="rp-recent-chip" @click="pickRecent(r)">{{ r.label }}</text>
      </view>

      <view class="rp-cols">
        <!-- 列 1：省 -->
        <scroll-view scroll-y class="rp-col">
          <view v-for="(p, i) in filteredProvinces" :key="p.id"
            class="rp-item" :class="{ active: i === provIdx }" @click="selectProv(i)">
            {{ p.name }}
          </view>
        </scroll-view>
        <!-- 列 2：市 -->
        <scroll-view scroll-y class="rp-col">
          <view v-for="(c, i) in cities" :key="c.id"
            class="rp-item" :class="{ active: i === cityIdx }" @click="selectCity(i)">
            {{ c.name }}
          </view>
          <view v-if="!cities.length" class="rp-empty">请先选省份</view>
        </scroll-view>
        <!-- 列 3：区县 -->
        <scroll-view scroll-y class="rp-col" v-if="!cityOnly">
          <view v-for="(d, i) in districts" :key="d.id"
            class="rp-item" :class="{ active: i === distIdx }" @click="selectDist(i)">
            {{ d.name }}
          </view>
          <view v-if="!districts.length" class="rp-empty">{{ cityIsMunicipality ? '直辖市两级直达' : '该市为直辖区县' }}</view>
        </scroll-view>
      </view>

      <view class="rp-foot">
        <text class="rp-selected">{{ selectedLabel || '尚未选择' }}</text>
        <view class="rp-btn" :class="{ disabled: !canConfirm }" @click="confirm">确定</view>
      </view>
    </view>
  </view>
</template>

<script>
import { useRegionStore } from '../store/region'

export default {
  name: 'region-picker',
  props: {
    visible: { type: Boolean, default: false },
    cityOnly: { type: Boolean, default: false },   // 投瓶目标城市：省 + 市两级即可确认
    initial: { type: Object, default: null }
  },
  emits: ['confirm', 'close'],
  data() {
    return {
      keyword: '',
      provIdx: -1,
      cityIdx: -1,
      distIdx: -1
    }
  },
  computed: {
    store() { return useRegionStore() },
    provinces() { return this.store.tree || [] },
    filteredProvinces() {
      const kw = (this.keyword || '').trim()
      if (!kw) return this.provinces
      return this.provinces.filter(p => p.name.indexOf(kw) >= 0 ||
        (p.children || []).some(c => c.name.indexOf(kw) >= 0))
    },
    currentProv() { return this.provIdx >= 0 && this.filteredProvinces[this.provIdx] ? this.filteredProvinces[this.provIdx] : null },
    currentCity() { return this.currentProv && this.cityIdx >= 0 ? (this.currentProv.children || [])[this.cityIdx] : null },
    currentDist() { return this.currentCity && this.distIdx >= 0 ? (this.currentCity.children || [])[this.distIdx] : null },
    cities() { return this.currentProv ? (this.currentProv.children || []) : [] },
    districts() { return this.currentCity ? (this.currentCity.children || []) : [] },
    cityIsMunicipality() {
      return !!(this.currentProv && this.currentProv.region_type === '直辖市')
    },
    selectedLabel() {
      if (!this.currentProv) return ''
      let s = this.currentProv.name
      if (this.currentCity) s += ' ' + this.currentCity.name
      if (this.currentDist && !this.cityIsMunicipality) s += ' ' + this.currentDist.name
      return s
    },
    canConfirm() {
      return !!(this.currentProv && this.currentCity)
    },
    recents() { return this.store.recents || [] }
  },
  watch: {
    visible(v) {
      if (v) {
        this.store.loadTree()
        this.syncInitial()
      }
    }
  },
  mounted() {
    this.store.loadTree()
  },
  methods: {
    syncInitial() {
      const init = this.initial || this.store.resident
      this.keyword = ''
      this.provIdx = -1; this.cityIdx = -1; this.distIdx = -1
      if (!init) return
      const list = this.provinces
      const pi = list.findIndex(p => p.name === init.province)
      if (pi >= 0) {
        this.selectProv(pi)
        const ci = (list[pi].children || []).findIndex(c => c.name === init.city)
        if (ci >= 0) this.selectCity(ci)
      }
    },
    selectProv(i) {
      this.provIdx = i
      this.cityIdx = -1
      this.distIdx = -1
    },
    selectCity(i) {
      this.cityIdx = i
      this.distIdx = -1
    },
    selectDist(i) { this.distIdx = i },
    pickRecent(r) {
      this.$emit('confirm', { ...r })
      this.$emit('close')
    },
    confirm() {
      if (!this.canConfirm) return
      const sel = {
        provinceId: this.currentProv.id,
        province: this.currentProv.name,
        cityId: this.currentCity.id,
        city: this.currentCity.name,
        districtId: this.currentDist ? this.currentDist.id : 0,
        district: this.currentDist ? this.currentDist.name : ''
      }
      this.$emit('confirm', sel)
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.rp-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 30, 51, 0.5);
  z-index: 999;
  display: flex;
  align-items: flex-end;
}

.rp-panel {
  width: 100%;
  background: #ffffff;
  border-radius: 20px 20px 0 0;
  padding: 16px 16px calc(16px + env(safe-area-inset-bottom));
  box-sizing: border-box;
}

.rp-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.rp-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f1e33;
}

.rp-close {
  color: #5b6b80;
  font-size: 18px;
  padding: 4px 8px;
}

.rp-search {
  background: #f4f7fb;
  border-radius: 999px;
  padding: 9px 16px;
  font-size: 14px;
  height: 38px;              /* 显式高度：修复内部 input 塌陷 */
  box-sizing: border-box;
  margin-bottom: 10px;
}

.rp-recent {
  margin-bottom: 8px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.rp-recent-label {
  font-size: 12px;
  color: #5b6b80;
}

.rp-recent-chip {
  font-size: 12px;
  color: #1e3a5f;
  background: #e8f0fe;
  border-radius: 999px;
  padding: 4px 10px;
}

.rp-cols {
  display: flex;
  height: 300px;
  gap: 8px;
}

.rp-col {
  flex: 1;
  background: #f4f7fb;
  border-radius: 12px;
  height: 100%;
}

.rp-item {
  padding: 11px 14px;
  font-size: 14px;
  color: #1f2d3d;
}

.rp-item.active {
  color: #ffffff;
  background: linear-gradient(135deg, #1e3a5f, #4f8ef7);
  border-radius: 10px;
  font-weight: 600;
}

.rp-empty {
  padding: 12px;
  font-size: 12px;
  color: #5b6b80;
  text-align: center;
}

.rp-foot {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.rp-selected {
  font-size: 14px;
  color: #1f2d3d;
  flex: 1;
  margin-right: 10px;
}

.rp-btn {
  background: linear-gradient(135deg, #1e3a5f, #4f8ef7);
  color: #ffffff;
  border-radius: 999px;
  padding: 10px 28px;
  font-size: 15px;
  font-weight: 600;
}

.rp-btn.disabled {
  opacity: 0.4;
}
</style>
