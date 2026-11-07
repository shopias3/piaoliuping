<template>
  <view class="page" :class="{ 'font-large': store.bigFont }">
    <drift-stage :activity-score="store.score" :themes="themes" :css-map="cssMap"
      :url-map="urlMap" :initial-theme="preferredTheme" @theme-change="onThemeChange" @theme-rotate="onThemeRotate">
      <!-- 顶部导航：登入（左）· 地区选择（中）· 关于我们（右） -->
      <view class="topbar">
        <view class="top-item left" @click="onAvatarTap">
          <image v-if="store.isLoggedIn && profile && profile.avatar_url" :src="profile.avatar_url"
            class="top-avatar" mode="aspectFill" />
          <text v-else class="avatar-mini">{{ store.isLoggedIn ? '👤' : '🔑' }}</text>
          <text class="top-label">{{ topLabel }}</text>
        </view>
        <view class="top-item center" @click="showRegion = true">
          <text class="region-emoji">📍</text>
          <text class="top-label strong">{{ regionLabel }}</text>
        </view>
        <view class="top-item right" @click="goAbout">
          <text class="top-label">关于我们</text>
        </view>
      </view>

      <!-- 中央标语：随主题切换的情感文案 -->
      <view class="hero">
        <text class="hero-title" :key="heroTitle">{{ heroTitle }}</text>
        <text class="hero-sub" v-if="store.isLoggedIn">
          活跃度 {{ store.score }} · 段位「{{ store.tier }}」 · 漂移速度 {{ driftSpeedPerMin(store.score) }} 米/分
        </text>
        <text class="hero-sub" v-else>另一座城市的陌生人，会捞起它并回应你</text>
      </view>

      <!-- 底部悬浮双大按钮 -->
      <view class="dock">
        <view class="dock-btn throw" @click="go('/pages/throw/throw')">
          <text class="dock-emoji">🍾</text>
          <text class="dock-label">投漂流瓶</text>
        </view>
        <view class="dock-btn pick" @click="go('/pages/pick/pick')">
          <text class="dock-emoji">🥅</text>
          <text class="dock-label">收漂流瓶</text>
        </view>
      </view>
    </drift-stage>

    <!-- 地区选择弹层 -->
    <region-picker :visible="showRegion" @confirm="onRegionConfirm" @close="showRegion = false" />

    <!-- 个人中心弹层（已登录） -->
    <view v-if="showProfile" class="pp-mask" @click="showProfile = false">
      <view class="pp-panel card" @click.stop>
        <view class="pp-head">
          <view class="pp-head-left">
            <image v-if="profile.avatar_url" :src="profile.avatar_url" class="pp-avatar" mode="aspectFill" />
            <text v-else class="pp-avatar pp-avatar-fallback">👤</text>
            <text class="pp-nickname">{{ profile.nickname }}</text>
          </view>
          <text class="pp-tier tag">{{ profile.tier }}</text>
        </view>
        <view class="pp-row"><text class="pp-k">手机号</text><text class="pp-v">{{ profile.phone_masked || '已绑定' }}</text></view>
        <view class="pp-row"><text class="pp-k">性别 / 年龄</text><text class="pp-v">{{ profile.gender }}{{ profile.age ? ' · ' + profile.age + ' 岁' : '' }}</text></view>
        <view class="pp-row"><text class="pp-k">民族</text><text class="pp-v">{{ profile.ethnicity || '未填写' }}</text></view>
        <view class="pp-row"><text class="pp-k">现住址</text><text class="pp-v">{{ profile.address || '未填写' }}</text></view>
        <view class="pp-row"><text class="pp-k">常驻地区</text><text class="pp-v">{{ regionLabel }}</text></view>
        <view class="pp-row"><text class="pp-k">活跃度</text><text class="pp-v">{{ profile.activity_score }} / 100（{{ profile.tier }}）</text></view>
        <view class="pp-row pp-tier-tip">
          <text class="pp-k">段位说明</text>
          <text class="pp-v muted">静水深流 → 微波荡漾 → 川流不息 → 乘风破浪 → 潮头弄浪，登录/投捞/互动越多活跃度越高，漂移越快、瓶子越容易被捞起</text>
        </view>
        <view class="pp-row">
          <text class="pp-k">今日次数</text>
          <text class="pp-v">投 {{ profile.today.throw_used }}/{{ profile.today.throw_limit }} · 捞 {{ profile.today.pick_used }}/{{ profile.today.pick_limit }}</text>
        </view>
        <view class="pp-row">
          <text class="pp-k">大字模式</text>
          <switch :checked="store.bigFont" color="#4f8ef7" @change="onToggleFont" />
        </view>
        <view class="btn-ghost pp-logout" @click="onLogout">退出登录</view>
      </view>
    </view>
  </view>
</template>

<script>
import driftStage from '../../components/drift-stage.vue'
import regionPicker from '../../components/region-picker.vue'
import { useUserStore } from '../../store/user'
import { useRegionStore } from '../../store/region'
import { getBackgrounds } from '../../api/common'
import { driftSpeedPerMin } from '../../utils/drift'

// 主题 → 中央标题情感文案（AI 诗意句子，随兴趣分类切换）
const THEME_COPY = {
  '城市': '霓虹漫过心事，总有一盏灯为你亮着',
  '自然': '山野收藏四季，也收藏你说不出口的秘密',
  '星空': '每颗星都曾是一个愿望，今夜轮到你许愿',
  '世界景点': '海的那一边，有人正替你路过风景',
  '世界人文': '灯火与烟火，都在等一句迟到的问候',
  '科技创新': '信号跨越山海，把心事递给未来的人',
  '漫画': '把烦恼画进四格，让世界替你温柔收尾',
  '名画': '颜料会褪色，而你投出的心事不会',
  '交通': '列车驶向远方，捎去那句没说完的话',
  '战争与武器': '烽烟散尽处，家书是最温柔的牵挂',
  '': '把愿望装进瓶子，投向大海'
}

export default {
  components: { driftStage, regionPicker },
  data() {
    return {
      store: useUserStore(),
      regionStore: useRegionStore(),
      showRegion: false,
      showProfile: false,
      cssMap: {},
      urlMap: {},
      profile: null,
      preferredTheme: uni.getStorageSync('drift_theme') || '',
      currentTheme: uni.getStorageSync('drift_theme') || ''   // 当前展示主题（驱动中央文案）
    }
  },
  computed: {
    heroTitle() {
      // 中央标题随主题切换：默认诗词文案，未匹配时回退到大海主题
      return THEME_COPY[this.currentTheme] || THEME_COPY['']
    },
    themes() {
      return this.profile ? this.profile.interest_tags || [] : []
    },
    regionLabel() {
      const r = this.regionStore.resident
      if (!r) return '选择地区'
      return [r.province, r.city].filter(Boolean).join(' · ')
    },
    topLabel() {
      if (!this.store.isLoggedIn) return '登入'
      return this.profile ? this.profile.nickname : '我'
    }
  },
  onShow() {
    this.init()
  },
  methods: {
    driftSpeedPerMin,
    async init() {
      try {
        const bgs = await getBackgrounds()
        const map = {}
        const urls = {}
        for (const b of bgs) {
          map[b.theme] = b.css
          if (b.oss_url) urls[b.theme] = b.oss_url
        }
        this.cssMap = map
        this.urlMap = urls
      } catch (e) { /* 后端未就绪时使用组件内置默认 */ }
      if (this.store.isLoggedIn) {
        try {
          this.profile = await this.store.fetchProfile()
        } catch (e) { /* token 失效已由 request 统一处理 */ }
      }
    },
    go(url) { uni.navigateTo({ url }) },
    onThemeChange(t) {
      // 手动选择主题：更新中央文案 + 记住偏好
      this.currentTheme = t
      this.preferredTheme = t
      uni.setStorageSync('drift_theme', t)
    },
    onThemeRotate(t) {
      // 自动轮换：只更新中央文案，不改偏好
      this.currentTheme = t
    },
    goAbout() { this.go('/pages/about/about') },
    onAvatarTap() {
      if (!this.store.isLoggedIn) { this.go('/pages/auth/login'); return }
      if (this.profile) this.showProfile = true
    },
    async onRegionConfirm(sel) {
      this.regionStore.setRegion(sel)
      this.showRegion = false
      if (this.store.isLoggedIn) {
        try { await this.store.updateProfile({ region_id: sel.cityId }) } catch (e) {}
      }
      uni.showToast({ title: '已切换：' + [sel.province, sel.city].join(' '), icon: 'none' })
    },
    async onToggleFont() {
      await this.store.toggleBigFont()
    },
    onLogout() {
      this.store.logout()
      this.showProfile = false
      this.profile = null
      uni.showToast({ title: '已退出登录', icon: 'none' })
    }
  }
}
</script>

<style scoped>
.page {
  height: 100vh;
}

.topbar {
  position: absolute;
  top: calc(env(safe-area-inset-top) + 12px);
  left: 16px;
  right: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 10;
}

.top-item {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #ffffff;
  padding: 7px 12px;
  border-radius: 999px;
  background: rgba(15, 30, 51, 0.38);
  backdrop-filter: blur(8px);
}

.top-label {
  font-size: 13px;
  color: #ffffff;
}

.top-label.strong {
  font-weight: 700;
}

.avatar-mini {
  font-size: 14px;
}

.hero {
  position: absolute;
  top: 26%;
  left: 24px;
  right: 24px;
  z-index: 10;
  text-align: center;
}

.hero-title {
  display: block;
  color: #ffffff;
  font-size: 24px;
  font-weight: 800;
  letter-spacing: 2px;
  text-shadow: 0 3px 12px rgba(0, 0, 0, 0.45);
  animation: heroFade 0.9s ease;
}

@keyframes heroFade {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: none; }
}

.hero-sub {
  display: block;
  margin-top: 10px;
  color: rgba(255, 255, 255, 0.85);
  font-size: 13px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.dock {
  position: absolute;
  bottom: calc(env(safe-area-inset-bottom) + 26px);
  left: 24px;
  right: 24px;
  display: flex;
  gap: 18px;
  z-index: 10;
}

.dock-btn {
  flex: 1;
  border-radius: 999px;
  padding: 18px 0;
  text-align: center;
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.28);
}

.dock-btn.throw {
  background: linear-gradient(135deg, #d97706, #f59e0b);
}

.dock-btn.pick {
  background: linear-gradient(135deg, #1e3a5f, #4f8ef7);
}

.dock-emoji {
  font-size: 22px;
  margin-right: 8px;
}

.dock-label {
  color: #ffffff;
  font-size: 17px;
  font-weight: 700;
}

/* 个人中心弹层 */
.pp-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 30, 51, 0.5);
  z-index: 999;
  display: flex;
  align-items: flex-end;
}

.pp-panel {
  width: 100%;
  border-radius: 20px 20px 0 0;
  padding-bottom: calc(20px + env(safe-area-inset-bottom));
}

.pp-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.pp-nickname {
  font-size: 18px;
  font-weight: 700;
  color: #0f1e33;
}

.pp-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eef2f8;
}

.pp-k {
  color: #5b6b80;
  font-size: 14px;
}

.pp-v {
  color: #1f2d3d;
  font-size: 14px;
}

.pp-row.top-item .top-avatar {
  width: 22px;
  height: 22px;
  border-radius: 50%;
}

.pp-head-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pp-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #e8f0fe;
  text-align: center;
  line-height: 44px;
}

.pp-avatar-fallback {
  display: inline-block;
  font-size: 22px;
}

.pp-tier-tip .pp-v {
  font-size: 11px;
  line-height: 1.6;
  max-width: 65%;
  text-align: right;
}

.pp-logout {
  margin-top: 14px;
  color: #b91c1c;
  border-color: #fecaca;
}
</style>
