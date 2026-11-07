<template>
  <view class="page" :class="{ 'font-large': store.bigFont }">
    <!-- 步骤条 -->
    <view class="steps card">
      <view v-for="(s, i) in stepNames" :key="s" class="step" :class="{ active: step === i + 1, done: step > i + 1 }">
        <text class="step-no">{{ step > i + 1 ? '✓' : i + 1 }}</text>
        <text class="step-name">{{ s }}</text>
      </view>
    </view>

    <!-- 第 1 步 · 选城市 -->
    <view v-if="step === 1" class="card block">
      <view class="title-bar">瓶子投进哪个城市的海？</view>
      <text class="muted tip">默认常驻城市，可切换目标城市——决定瓶池范围</text>
      <view class="city-row">
        <view class="field-input select" @click="showRegion = true">
          📍 {{ targetLabel || '点击选择城市' }}
        </view>
        <view class="btn-ghost use-resident" @click="useResident">用常驻城市</view>
      </view>
      <view class="btn-primary next" @click="step = 2">下一步 · 选人群</view>
    </view>

    <!-- 第 2 步 · 选人群 -->
    <view v-if="step === 2" class="card block">
      <view class="title-bar">希望谁捞起它？</view>
      <text class="muted tip">人群筛选会同时约束捞瓶方的「想要什么」</text>
      <view class="chips">
        <text v-for="c in crowds" :key="c" class="tag crowd" :class="{ active: targetCrowd === c }"
          @click="targetCrowd = c">{{ c }}</text>
      </view>
      <view class="btn-row">
        <view class="btn-ghost half" @click="step = 1">上一步</view>
        <view class="btn-primary half" @click="step = 3">下一步 · 许愿</view>
      </view>
    </view>

    <!-- 第 3 步 · 自己许愿 -->
    <view v-if="step === 3" class="card block">
      <view class="title-bar">把心愿写进瓶子</view>
      <view class="chips type-chips">
        <text v-for="t in types" :key="t.id" class="tag" :class="{ active: type === t.id }"
          @click="type = t.id">{{ t.name }}<text v-if="t.age" class="pill-age"> 18+</text></text>
      </view>
      <view class="ta-wrap">
        <textarea class="ta" v-model="content" maxlength="200" placeholder="写下你的愿望：求资料、找合作、展示好物、求职招聘、交友、寻缘分、出国咨询…"></textarea>
        <text class="ta-count">{{ content.length }}/200</text>
      </view>
      <view class="ai-row">
        <view class="ai-btn">✨ AI 帮写</view>
        <text class="muted">润色能力二期上线</text>
      </view>
      <view class="left-tip muted">今日剩余投瓶次数：{{ throwLeft }}</view>
      <view class="btn-row">
        <view class="btn-ghost half" @click="step = 2">上一步</view>
        <view class="btn-primary half" :class="{ disabled: !content.trim() }" @click="submit">封瓶投入 🌊</view>
      </view>
    </view>

    <region-picker :visible="showRegion" city-only @confirm="onCityConfirm" @close="showRegion = false" />
  </view>
</template>

<script>
import regionPicker from '../../components/region-picker.vue'
import { useUserStore } from '../../store/user'
import { useRegionStore } from '../../store/region'
import { throwBottle } from '../../api/bottle'
import { toastError } from '../../api/request'
import { preCheck } from '../../utils/sensitive'

export default {
  components: { regionPicker },
  data() {
    return {
      store: useUserStore(),
      regionStore: useRegionStore(),
      step: 1,
      stepNames: ['选城市', '选人群', '自己许愿'],
      showRegion: false,
      targetCity: null,
      targetCrowd: '不限',
      crowds: ['不限', '青年16-30', '中坚31-45', '沉淀46-60'],
      types: [
        { id: 1, name: '学习提升瓶' }, { id: 2, name: '合作机会瓶' },
        { id: 3, name: '好物展示瓶' }, { id: 4, name: '求职瓶' },
        { id: 5, name: '交友瓶' }, { id: 6, name: '缘分瓶', age: true },
        { id: 7, name: '招聘瓶' }, { id: 8, name: '出国圆梦瓶' }
      ],
      type: 5,
      content: '',
      throwLeft: '-'
    }
  },
  computed: {
    targetLabel() {
      const c = this.targetCity || this.regionStore.resident
      if (!c) return ''
      return [c.province, c.city].filter(Boolean).join(' · ')
    }
  },
  async onShow() {
    if (this.store.isLoggedIn) {
      try {
        const p = await this.store.fetchProfile()
        if (p) this.throwLeft = p.today.throw_limit - p.today.throw_used
      } catch (e) { /* 忽略 */ }
    }
  },
  methods: {
    useResident() {
      if (!this.regionStore.resident) {
        uni.showToast({ title: '尚未设置常驻地区', icon: 'none' })
        this.showRegion = true
        return
      }
      this.targetCity = null
      this.step = 2
    },
    onCityConfirm(sel) {
      this.targetCity = sel
      this.showRegion = false
    },
    async submit() {
      if (!this.content.trim()) return
      const pre = preCheck(this.content)
      if (!pre.ok) {
        uni.showToast({ title: pre.msg, icon: 'none' })
        return
      }
      const city = this.targetCity || this.regionStore.resident
      if (!city) {
        uni.showToast({ title: '请先选择城市', icon: 'none' })
        this.step = 1
        return
      }
      try {
        const data = await throwBottle({
          city_id: city.cityId,
          target_crowd: this.targetCrowd,
          type: this.type,
          content: this.content.trim()
        })
        this.throwLeft = data.left
        uni.showModal({
          title: '封瓶成功',
          content: '愿它漂到对岸。今日剩余投瓶 ' + data.left + ' 次。',
          showCancel: false,
          success: () => uni.navigateBack()
        })
      } catch (e) {
        toastError(e)
      }
    }
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 16px;
  box-sizing: border-box;
  background: linear-gradient(170deg, #eaf1fb 0%, #f4f7fb 60%);
}

.steps {
  display: flex;
  justify-content: space-around;
  margin-bottom: 14px;
}

.step {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #5b6b80;
  font-size: 13px;
}

.step-no {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #e8f0fe;
  color: #1e3a5f;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.step.active {
  color: #1e3a5f;
  font-weight: 700;
}

.step.active .step-no {
  background: linear-gradient(135deg, #1e3a5f, #4f8ef7);
  color: #ffffff;
}

.step.done .step-no {
  background: #34c77b;
  color: #ffffff;
}

.block {
  max-width: 520px;
  margin: 0 auto;
}

.tip {
  display: block;
  margin: 6px 0 14px;
}

.city-row {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
}

.city-row .field-input {
  flex: 1;
}

.use-resident {
  padding: 0 16px;
  display: flex;
  align-items: center;
  font-size: 13px;
  white-space: nowrap;
}

.field-input {
  background: #f4f7fb;
  border-radius: 12px;
  padding: 12px 14px;
  font-size: 15px;
  box-sizing: border-box;
}

.field-input.select {
  color: #1e3a5f;
  font-weight: 600;
}

.next {
  max-width: 300px;
  margin: 0 auto;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 18px;
}

.tag.crowd {
  padding: 9px 16px;
  font-size: 14px;
}

.type-chips .tag {
  padding: 9px 14px;
  font-size: 14px;
}

.pill-age {
  color: #c62828;
  font-size: 10px;
  font-weight: 800;
}

.type-chips .tag.active .pill-age {
  color: #ffe0e0;
}

.btn-row {
  display: flex;
  gap: 12px;
}

.half {
  flex: 1;
}

.ta-wrap {
  position: relative;
  margin-bottom: 12px;
}

.ta {
  width: 100%;
  height: 130px;
  background: #f4f7fb;
  border-radius: 14px;
  padding: 12px;
  font-size: 15px;
  line-height: 1.7;
  box-sizing: border-box;
}

.ta-count {
  position: absolute;
  right: 12px;
  bottom: 10px;
  font-size: 12px;
  color: #5b6b80;
}

.ai-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.ai-btn {
  font-size: 13px;
  color: #1e3a5f;
  background: #e8f0fe;
  border-radius: 999px;
  padding: 6px 14px;
  opacity: 0.6;
}

.left-tip {
  margin-bottom: 12px;
}
</style>
