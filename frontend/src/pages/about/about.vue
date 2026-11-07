<template>
  <view class="page" :class="{ 'font-large': store.bigFont }">
    <!-- 出品方卡片 -->
    <view class="card operator">
      <view class="op-logo">🌊</view>
      <view class="op-name">{{ config.app_name || '漂流瓶' }}</view>
      <view class="op-slogan">{{ config.slogan || '愿每一个愿望，都能漂到对岸' }}</view>
      <view class="tag op-tag">出品与运营：{{ config.operator || '微信公众号 Daboshik' }}</view>
      <view class="muted op-contact">{{ config.contact }}</view>
    </view>

    <!-- 漂流瓶规则 -->
    <view class="card section">
      <view class="title-bar">漂流瓶规则</view>
      <view v-for="r in config.rules || []" :key="r.title" class="rule">
        <text class="rule-title">· {{ r.title }}</text>
        <text class="rule-desc">{{ r.desc }}</text>
      </view>
    </view>

    <!-- 合规声明 -->
    <view class="card section">
      <view class="title-bar">合规声明</view>
      <text class="statement">{{ config.statement }}</text>
    </view>

    <!-- 协议入口 -->
    <view class="card section">
      <view class="title-bar">协议入口</view>
      <view v-for="(text, key) in config.agreements || {}" :key="key" class="agree"
        @click="expanded = expanded === key ? '' : key">
        <text class="agree-title">{{ (agreementNames[key] || key) }} {{ expanded === key ? '▾' : '▸' }}</text>
        <text v-if="expanded === key" class="agree-body">{{ text }}</text>
      </view>
    </view>

    <!-- 设置 -->
    <view class="card section">
      <view class="title-bar">设置</view>
      <view class="setting-row">
        <text class="setting-k">适老化大字模式（正文 18px）</text>
        <switch :checked="store.bigFont" color="#4f8ef7" @change="onToggleFont" />
      </view>
      <view class="setting-row" v-if="store.isLoggedIn">
        <text class="setting-k">账号</text>
        <text class="btn-ghost logout-mini" @click="onLogout">退出登录</text>
      </view>
    </view>

    <view class="muted version">v{{ config.version || '1.0.0' }} · 公测期投瓶捞瓶全免费</view>
  </view>
</template>

<script>
import { useUserStore } from '../../store/user'
import { getAboutConfig } from '../../api/common'
import { toastError } from '../../api/request'

export default {
  data() {
    return {
      store: useUserStore(),
      config: {},
      expanded: '',
      agreementNames: { user: '用户协议', privacy: '隐私政策', logout: '账号注销指引' }
    }
  },
  async onLoad() {
    try {
      this.config = await getAboutConfig()
    } catch (e) {
      toastError(e)
    }
  },
  methods: {
    async onToggleFont() {
      await this.store.toggleBigFont()
    },
    onLogout() {
      this.store.logout()
      uni.showToast({ title: '已退出登录', icon: 'none' })
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

.operator {
  text-align: center;
  padding: 26px 16px;
  background: linear-gradient(135deg, #1e3a5f 0%, #4f8ef7 100%);
}

.op-logo {
  font-size: 40px;
}

.op-name {
  color: #ffffff;
  font-size: 22px;
  font-weight: 800;
  margin-top: 6px;
}

.op-slogan {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  margin-top: 6px;
}

.op-tag {
  margin-top: 12px;
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

.op-contact {
  margin-top: 10px;
  color: rgba(255, 255, 255, 0.75);
}

.section {
  margin-top: 14px;
  max-width: 560px;
}

.rule {
  margin-top: 10px;
}

.rule-title {
  display: block;
  font-weight: 700;
  color: #0f1e33;
  font-size: 14px;
}

.rule-desc {
  display: block;
  color: #5b6b80;
  font-size: 13px;
  line-height: 1.7;
  margin-top: 2px;
}

.statement {
  display: block;
  margin-top: 10px;
  font-size: 13px;
  line-height: 1.8;
  color: #1f2d3d;
  background: #f0fdfa;
  border-left: 4px solid #14b8a6;
  border-radius: 8px;
  padding: 12px;
}

.agree {
  margin-top: 10px;
}

.agree-title {
  font-size: 14px;
  color: #1e3a5f;
  font-weight: 600;
}

.agree-body {
  display: block;
  margin-top: 6px;
  font-size: 13px;
  color: #5b6b80;
  line-height: 1.7;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
}

.setting-k {
  font-size: 14px;
  color: #1f2d3d;
}

.logout-mini {
  font-size: 12px;
  padding: 6px 14px;
  color: #b91c1c;
  border-color: #fecaca;
}

.version {
  text-align: center;
  margin: 18px 0 8px;
}
</style>
