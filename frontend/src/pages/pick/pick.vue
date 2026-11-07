<template>
  <view class="page" :class="{ 'font-large': store.bigFont }">
    <!-- 第 1 步 · 三重筛选 -->
    <view class="card block">
      <view class="title-bar">你想捞到什么？</view>
      <text class="muted tip">三重筛选：范围 + 人群 + 想要什么（八大瓶签）</text>

      <view class="filter-label">范围</view>
      <view class="chips">
        <text v-for="s in scopes" :key="s.value" class="tag" :class="{ active: scope === s.value }"
          @click="scope = s.value">{{ s.label }}</text>
      </view>
      <view class="scope-city muted" @click="showRegion = true">
        📍 {{ poolLabel }}
      </view>

      <view class="filter-label">人群</view>
      <view class="chips">
        <text v-for="c in crowds" :key="c" class="tag" :class="{ active: crowd === c }"
          @click="crowd = c">{{ c }}</text>
      </view>

      <view class="filter-label">想要的瓶签（多选）</view>
      <view class="chips">
        <text v-for="t in types" :key="t.id" class="tag" :class="{ active: typeSet.indexOf(t.id) >= 0 }"
          @click="toggleType(t.id)">{{ t.name }}</text>
      </view>

      <view class="left-tip muted">今日剩余捞瓶次数：{{ pickLeft }}</view>
      <view class="btn-primary cast" :class="{ disabled: casting }" @click="cast">
        {{ casting ? '撒网中…' : '撒网捞瓶 🥅' }}
      </view>
    </view>

    <!-- 捞瓶动画 -->
    <view v-if="casting" class="cast-anim">
      <text class="net">🥅</text>
      <text class="muted">正在打捞…</text>
    </view>

    <region-picker :visible="showRegion" @confirm="onRegionConfirm" @close="showRegion = false" />

    <!-- 第 3 步 · 瓶子卡片（打开 / 回应 / 放回） -->
    <bottle-card v-if="current" :bottle="current" :opened="opened" :anti-fraud="antiFraud"
      @open="onOpen" @back="onBack" @reply="onReply" @report="onReport" @close="current = null" />
  </view>
</template>

<script>
import bottleCard from '../../components/bottle-card.vue'
import regionPicker from '../../components/region-picker.vue'
import { useUserStore } from '../../store/user'
import { useRegionStore } from '../../store/region'
import { pickBottle, bottleAction } from '../../api/bottle'
import { reportTarget } from '../../api/common'
import { toastError } from '../../api/request'

export default {
  components: { bottleCard, regionPicker },
  data() {
    return {
      store: useUserStore(),
      regionStore: useRegionStore(),
      scopes: [
        { value: 'city', label: '本市' },
        { value: 'province', label: '全省' },
        { value: 'nation', label: '全国' }
      ],
      scope: 'city',
      crowd: '不限',
      crowds: ['不限', '青年16-30', '中坚31-45', '沉淀46-60'],
      types: [
        { id: 1, name: '学习提升瓶' }, { id: 2, name: '合作机会瓶' },
        { id: 3, name: '好物展示瓶' }, { id: 4, name: '求职瓶' },
        { id: 5, name: '交友瓶' }, { id: 6, name: '缘分瓶' },
        { id: 7, name: '招聘瓶' }, { id: 8, name: '出国圆梦瓶' }
      ],
      typeSet: [],
      showRegion: false,
      pickCity: null,
      casting: false,
      current: null,
      opened: false,
      antiFraud: '谨防诈骗：请勿向陌生人转账汇款，如遇诱导请立即举报。',
      pickLeft: '-'
    }
  },
  computed: {
    poolLabel() {
      const c = this.pickCity || this.regionStore.resident
      if (this.scope === 'nation') return '全国瓶池'
      if (!c) return '请选择城市'
      const suffix = this.scope === 'province' ? '（全省）' : ''
      return [c.province, c.city].filter(Boolean).join(' ') + suffix
    }
  },
  async onShow() {
    if (this.store.isLoggedIn) {
      try {
        const p = await this.store.fetchProfile()
        if (p) this.pickLeft = p.today.pick_limit - p.today.pick_used
      } catch (e) { /* 忽略 */ }
    }
  },
  methods: {
    toggleType(id) {
      const i = this.typeSet.indexOf(id)
      if (i >= 0) this.typeSet.splice(i, 1)
      else this.typeSet.push(id)
    },
    onRegionConfirm(sel) {
      this.pickCity = sel
      this.regionStore.setRegion(sel)
      this.showRegion = false
    },
    async cast() {
      if (this.casting) return
      if (this.scope !== 'nation' && !(this.pickCity || this.regionStore.resident)) {
        uni.showToast({ title: '请先选择城市', icon: 'none' })
        this.showRegion = true
        return
      }
      const city = this.pickCity || this.regionStore.resident
      this.casting = true
      this.current = null
      try {
        const data = await pickBottle({
          scope: this.scope,
          city_id: this.scope === 'nation' ? '' : (city ? city.cityId : ''),
          crowd: this.crowd,
          types: this.typeSet.join(',')
        })
        this.pickLeft = data.left
        if (!data.bottle) {
          uni.showToast({ title: '这片海面暂时没有匹配的瓶子，稍后再试试', icon: 'none' })
        } else {
          this.current = data.bottle
          this.opened = false
        }
      } catch (e) {
        toastError(e)
      } finally {
        this.casting = false
      }
    },
    async onOpen() {
      try {
        const data = await bottleAction(this.current.id, 'open')
        this.current = { ...this.current, ...data }
        this.antiFraud = data.anti_fraud || this.antiFraud
        this.opened = true
      } catch (e) {
        toastError(e)
      }
    },
    async onBack() {
      try {
        await bottleAction(this.current.id, 'back')
        this.current = null
        uni.showToast({ title: '已放回海里，瓶子继续漂流', icon: 'none' })
      } catch (e) {
        toastError(e)
      }
    },
    async onReply(text) {
      try {
        await bottleAction(this.current.id, 'reply', { reply_content: text })
        this.current = null
        uni.showToast({ title: '回应已封好漂回给对方', icon: 'none' })
      } catch (e) {
        toastError(e)
      }
    },
    async onReport(reason) {
      try {
        await reportTarget({ target_type: 'bottle', target_id: this.current.id, reason })
        this.current = null
        uni.showToast({ title: '举报已提交，24 小时内处理', icon: 'none' })
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

.block {
  max-width: 520px;
  margin: 0 auto;
}

.tip {
  display: block;
  margin: 6px 0 12px;
}

.filter-label {
  font-size: 13px;
  color: #5b6b80;
  margin: 12px 0 8px;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 8px 14px;
  font-size: 13px;
}

.scope-city {
  font-size: 13px;
  color: #1e3a5f;
  background: #eef5ff;
  border-radius: 10px;
  padding: 8px 12px;
  margin-top: 8px;
  display: inline-block;
}

.left-tip {
  margin: 16px 0 10px;
}

.cast {
  max-width: 300px;
  margin: 0 auto;
}

.cast-anim {
  text-align: center;
  padding: 24px 0;
}

.net {
  font-size: 42px;
  display: block;
  animation: swing 1s infinite ease-in-out;
}

@keyframes swing {
  0%, 100% { transform: rotate(-14deg); }
  50% { transform: rotate(14deg) translateY(8px); }
}
</style>
