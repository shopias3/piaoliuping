<template>
  <view class="page" :class="{ 'font-large': store.bigFont }">
    <region-picker :visible="true" @confirm="onConfirm" @close="goBack" />
    <view class="tip card" v-if="!regionStore.treeLoaded">正在加载行政区划数据…</view>
  </view>
</template>

<script>
import regionPicker from '../../components/region-picker.vue'
import { useRegionStore } from '../../store/region'
import { useUserStore } from '../../store/user'

export default {
  components: { regionPicker },
  data() {
    return {
      regionStore: useRegionStore(),
      store: useUserStore()
    }
  },
  methods: {
    onConfirm(sel) {
      this.regionStore.setRegion(sel)
      uni.showToast({ title: '常驻地区已保存', icon: 'none' })
      setTimeout(() => uni.navigateBack(), 500)
    },
    goBack() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 20px;
  box-sizing: border-box;
}

.tip {
  margin-top: 30vh;
  text-align: center;
  color: #5b6b80;
}
</style>
