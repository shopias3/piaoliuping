<template>
  <view class="stage">
    <!-- 主题长卷背景：智能运镜（按场景适配缩放/平移参数，随活跃度微调快慢） + 主题专属动态贴图 -->
    <view class="bg-layer" :style="{ background: themeCss }">
      <view class="bg-img kb" :style="kbStyle"></view>
      <!-- 主题专属动态贴图装饰 -->
      <view class="decor-layer">
        <view v-for="d in decorItems" :key="d.key" class="decor-item"
          :class="'decor-' + d.type" :style="d.style">{{ d.icon }}</view>
      </view>
      <view class="bg-stars" v-if="showStars">
        <view v-for="n in 40" :key="n" class="star" :style="starStyle(n)"></view>
      </view>
      <!-- 水域类主题的静态水波装饰 -->
      <view v-if="showWaves">
        <view class="wave wave1"></view>
        <view class="wave wave2"></view>
      </view>
    </view>

    <!-- 漂浮的瓶子：圆形人物头像 + 瓶子绑在一起，横向漂移 + 上下沉浮，可点击有响声 -->
    <view v-for="(f, i) in floaters" :key="'b' + i" class="float-group"
      :style="{ transform: 'translateX(' + f.x + 'px)', top: f.top, fontSize: f.size }"
      @click="onBottleTap(i)">
      <view class="float-inner" :class="{ pop: poppedIdx === i }" :style="{ animationDelay: f.delay }">
        <view class="fa-avatar">{{ f.face }}</view>
        <view class="fa-bottle">🍾</view>
      </view>
    </view>

    <!-- 声音开关 -->
    <view class="sound-toggle" @click="toggleSound">{{ soundOn ? '🔊' : '🔇' }}</view>

    <!-- 主题切换条：兴趣主题排前（★），点击即换背景 -->
    <scroll-view v-if="themeList.length" scroll-x class="theme-strip">
      <view v-for="(t, i) in themeList" :key="t" class="theme-chip"
        :class="{ active: i === themeIdx }" @click="pickTheme(i)">
        {{ t }}<text v-if="favThemes.indexOf(t) >= 0" class="fav-mark">★</text>
      </view>
    </scroll-view>

    <!-- 用户化身：随活跃度漂移 -->
    <view class="avatar-wrap" :style="{ transform: 'translateX(' + avatarX + 'px)' }">
      <view class="avatar">🧑‍✈️</view>
      <view v-if="tierName" class="tier-chip">{{ tierName }}</view>
    </view>

    <slot></slot>
  </view>
</template>

<script>
import { driftSpeed, tierOf } from '../utils/drift'

const FACE_POOL = ['👩‍🎓', '👨‍💼', '🧑‍🌾', '👩‍⚕️', '🧑‍💻', '👵', '👴', '👩‍🍳', '🧑‍🔧', '👨‍🎨']

// 各主题专属动态贴图：type=drift 横向飞过 / rise 升空 / fall 飘落(流星) / twinkle 闪烁光点
const DECOR_THEMES = {
  '城市': [
    { icon: '✈️', type: 'drift', top: 8, size: 26, dur: 34 },
    { icon: '🚁', type: 'drift', top: 18, size: 20, dur: 26, delay: -9 },
    { icon: '☁️', type: 'drift', top: 4, size: 32, dur: 52, delay: -25 },
    { icon: '✦', type: 'twinkle', left: 18, top: 34, size: 11, color: '#ffd76a' },
    { icon: '✦', type: 'twinkle', left: 56, top: 42, size: 8, color: '#ffd76a' },
    { icon: '✦', type: 'twinkle', left: 78, top: 30, size: 13, color: '#ffd76a' },
    { icon: '✦', type: 'twinkle', left: 38, top: 55, size: 9, color: '#ffd76a' }
  ],
  '自然': [
    { icon: '🐦', type: 'drift', top: 12, size: 18, dur: 22 },
    { icon: '🦋', type: 'drift', top: 52, size: 18, dur: 30, delay: -12 },
    { icon: '🍃', type: 'fall', left: 28, size: 15, dur: 13 },
    { icon: '🍃', type: 'fall', left: 66, size: 12, dur: 16, delay: 5 },
    { icon: '✨', type: 'twinkle', left: 82, top: 30, size: 12 }
  ],
  '星空': [
    { icon: '🌠', type: 'fall', left: 24, size: 22, dur: 8 },
    { icon: '🌠', type: 'fall', left: 62, size: 18, dur: 11, delay: 4 },
    { icon: '✦', type: 'twinkle', left: 15, top: 20, size: 12 },
    { icon: '✦', type: 'twinkle', left: 46, top: 12, size: 9 },
    { icon: '✦', type: 'twinkle', left: 72, top: 30, size: 13 },
    { icon: '✨', type: 'twinkle', left: 30, top: 44, size: 12 }
  ],
  '世界景点': [
    { icon: '🎈', type: 'rise', left: 24, size: 22, dur: 22 },
    { icon: '🎈', type: 'rise', left: 70, size: 18, dur: 26, delay: 7 },
    { icon: '🕊️', type: 'drift', top: 14, size: 16, dur: 24 },
    { icon: '☁️', type: 'drift', top: 5, size: 30, dur: 50, delay: -20 }
  ],
  '世界人文': [
    { icon: '🏮', type: 'rise', left: 30, size: 20, dur: 24 },
    { icon: '🏮', type: 'rise', left: 62, size: 17, dur: 28, delay: 9 },
    { icon: '✨', type: 'twinkle', left: 20, top: 35, size: 12 },
    { icon: '✨', type: 'twinkle', left: 76, top: 28, size: 10 },
    { icon: '🎇', type: 'twinkle', left: 50, top: 16, size: 16, color: '#ffd76a' }
  ],
  '科技创新': [
    { icon: '🛸', type: 'drift', top: 12, size: 22, dur: 24 },
    { icon: '🚀', type: 'rise', left: 78, size: 20, dur: 18 },
    { icon: '💫', type: 'drift', top: 38, size: 14, dur: 30, delay: -15 },
    { icon: '✦', type: 'twinkle', left: 22, top: 26, size: 10, color: '#9be7ff' },
    { icon: '✦', type: 'twinkle', left: 52, top: 44, size: 12, color: '#9be7ff' },
    { icon: '✦', type: 'twinkle', left: 84, top: 20, size: 9, color: '#9be7ff' }
  ],
  '漫画': [
    { icon: '✨', type: 'twinkle', left: 24, top: 28, size: 14 },
    { icon: '✨', type: 'twinkle', left: 68, top: 20, size: 11 },
    { icon: '☁️', type: 'drift', top: 8, size: 30, dur: 42, delay: -16 },
    { icon: '🌸', type: 'fall', left: 20, size: 14, dur: 14 },
    { icon: '🌸', type: 'fall', left: 70, size: 12, dur: 18, delay: 6 }
  ],
  '名画': [
    { icon: '✦', type: 'twinkle', left: 20, top: 30, size: 10, color: '#ffe9a8' },
    { icon: '✦', type: 'twinkle', left: 48, top: 52, size: 8, color: '#ffe9a8' },
    { icon: '✦', type: 'twinkle', left: 75, top: 24, size: 12, color: '#ffe9a8' },
    { icon: '🕊️', type: 'drift', top: 16, size: 15, dur: 30 }
  ],
  '交通': [
    { icon: '✈️', type: 'drift', top: 10, size: 26, dur: 26 },
    { icon: '🚁', type: 'drift', top: 24, size: 18, dur: 22, delay: -7 },
    { icon: '☁️', type: 'drift', top: 5, size: 30, dur: 48, delay: -22 },
    { icon: '🕊️', type: 'drift', top: 55, size: 15, dur: 30, delay: -10 }
  ],
  '战争与武器': [
    { icon: '🕊️', type: 'drift', top: 18, size: 16, dur: 28 },
    { icon: '☁️', type: 'drift', top: 8, size: 30, dur: 46, delay: -18 },
    { icon: '⛵', type: 'drift', top: 68, size: 18, dur: 60, delay: -30 },
    { icon: '💨', type: 'drift', top: 60, size: 20, dur: 36, delay: -8 }
  ]
}
const DECOR_FALLBACK = [
  { icon: '☁️', type: 'drift', top: 8, size: 30, dur: 45 },
  { icon: '✨', type: 'twinkle', left: 50, top: 35, size: 12 },
  { icon: '✈️', type: 'drift', top: 16, size: 22, dur: 32, delay: -10 }
]

// 智能运镜：按各自场景环境适配镜头（缩放幅度/平移方向/时长），活跃度高时镜头略快
// s1→s2 缩放范围；x/y1→x/y2 平移范围（元素百分比）；dur 基准时长（秒）
const CAMERA_THEMES = {
  '城市': { s1: 1.05, s2: 1.1, x1: '2.6%', x2: '-2.6%', y1: '0%', y2: '-0.8%', dur: 34 },
  '自然': { s1: 1.09, s2: 1.04, x1: '-1.5%', x2: '1.5%', y1: '1%', y2: '-1%', dur: 30 },
  '星空': { s1: 1.03, s2: 1.1, x1: '1%', x2: '-1%', y1: '0.8%', y2: '-0.8%', dur: 44 },
  '世界景点': { s1: 1.04, s2: 1.09, x1: '3%', x2: '-3%', y1: '0%', y2: '-0.5%', dur: 30 },
  '世界人文': { s1: 1.05, s2: 1.11, x1: '2%', x2: '-2%', y1: '-0.5%', y2: '0.5%', dur: 27 },
  '科技创新': { s1: 1.06, s2: 1.13, x1: '-2.6%', x2: '2.6%', y1: '0%', y2: '-0.6%', dur: 23 },
  '漫画': { s1: 1.04, s2: 1.1, x1: '1.6%', x2: '-1.6%', y1: '0.5%', y2: '-0.5%', dur: 20 },
  '名画': { s1: 1.02, s2: 1.08, x1: '0.9%', x2: '-0.9%', y1: '0%', y2: '-0.4%', dur: 52 },
  '交通': { s1: 1.05, s2: 1.09, x1: '3.6%', x2: '-3.6%', y1: '0%', y2: '-0.4%', dur: 18 },
  '战争与武器': { s1: 1.04, s2: 1.15, x1: '1%', x2: '-1%', y1: '0.4%', y2: '-0.4%', dur: 38 }
}
const CAMERA_FALLBACK = { s1: 1.05, s2: 1.12, x1: '1.5%', x2: '-1.5%', y1: '0.5%', y2: '-0.5%', dur: 28 }

export default {
  name: 'drift-stage',
  props: {
    activityScore: { type: Number, default: 20 },
    themes: { type: Array, default: () => [] },        // 用户兴趣主题（千人千面）
    cssMap: { type: Object, default: () => ({}) },     // 主题 → 渐变（图片加载前兜底）
    urlMap: { type: Object, default: () => ({}) },     // 主题 → 长卷图地址
    initialTheme: { type: String, default: '' }        // 上次手动选择的主题
  },
  emits: ['theme-change', 'theme-rotate'],
  data() {
    return {
      avatarX: 0,
      stageWidth: 375,
      rafId: null,
      lastTs: 0,
      themeIdx: 0,
      themeTimer: null,
      soundOn: uni.getStorageSync('drift_sound') !== 0,
      audioCtxs: [],
      audioBufs: [],      // Web Audio 预解码的音效缓冲
      webAudioCtx: null,  // AudioContext（H5）
      unlocked: false,
      ambientTimer: null,
      poppedIdx: -1,
      floaters: []   // [{face, x, top, size, factor, delay}]
    }
  },
  computed: {
    speed() {
      return driftSpeed(this.activityScore)   // 24–144 px/s
    },
    tierName() {
      return tierOf(this.activityScore).name
    },
    favThemes() {
      return (this.themes || []).filter(t => this.cssMap[t])
    },
    // 自动轮换顺序：兴趣主题优先，其余主题殿后
    themeList() {
      const fav = this.favThemes
      const rest = Object.keys(this.cssMap).filter(t => fav.indexOf(t) < 0)
      const list = fav.concat(rest)
      return list.length ? list : Object.keys(this.cssMap)
    },
    currentTheme() {
      const list = this.themeList
      return list.length ? list[this.themeIdx % list.length] : ''
    },
    themeCss() {
      return this.cssMap[this.currentTheme] || 'linear-gradient(160deg,#0f2027,#203a43 55%,#2c5364)'
    },
    tileBg() {
      const url = this.urlMap[this.currentTheme]
      return url ? 'url(' + url + ')' : 'none'
    },
    // 智能运镜：把当前主题的镜头参数写入 CSS 变量，供 kenburns 关键帧消费；
    // 时长随活跃度反比微调（活跃度越高镜头越快，幅度限制在 ±35%）
    kbStyle() {
      const cam = CAMERA_THEMES[this.currentTheme] || CAMERA_FALLBACK
      const speed = Math.max(this.speed, 24)
      const factor = Math.min(1.35, Math.max(0.7, Math.sqrt(60 / speed)))
      const dur = Math.round(cam.dur * factor)
      return {
        backgroundImage: this.tileBg,
        '--kb-s1': cam.s1,
        '--kb-s2': cam.s2,
        '--kb-x1': cam.x1,
        '--kb-x2': cam.x2,
        '--kb-y1': cam.y1,
        '--kb-y2': cam.y2,
        '--kb-dur': dur + 's'
      }
    },
    showWaves() {
      // 水域类主题显示静态水波装饰；无主题数据时默认海面
      if (!this.currentTheme) return true
      return ['自然', '交通', '战争与武器'].indexOf(this.currentTheme) >= 0
    },
    showStars() {
      if (!this.currentTheme) return true
      return ['星空', '城市'].indexOf(this.currentTheme) >= 0
    },
    decorItems() {
      const conf = DECOR_THEMES[this.currentTheme] || DECOR_FALLBACK
      return conf.map((d, i) => ({
        key: (this.currentTheme || 'def') + '-' + i,
        icon: d.icon,
        type: d.type,
        style: {
          left: (d.left !== undefined ? d.left : 0) + '%',
          top: (d.top || 0) + '%',
          fontSize: (d.size || 16) + 'px',
          color: d.color || '',
          // 闪烁类用短周期（CSS 默认 2.6s），其余用配置时长
          animationDuration: (d.dur || (d.type === 'twinkle' ? 2.6 : 30)) + 's',
          animationDelay: (d.delay || (d.type === 'twinkle' ? (i % 4) * 0.5 : 0)) + 's'
        }
      }))
    }
  },
  watch: {
    themeList(list) {
      // 背景库数据到达后应用上次选择的主题
      if (this.initialTheme && list.indexOf(this.initialTheme) >= 0 && this.currentTheme !== this.initialTheme) {
        this.themeIdx = list.indexOf(this.initialTheme)
        this.$emit('theme-rotate', this.currentTheme)
      }
    }
  },
  mounted() {
    const sys = uni.getSystemInfoSync()
    this.stageWidth = sys.windowWidth || 375
    // #ifdef H5
    const unlock = () => { this.unlockFeedback() }
    document.addEventListener('pointerdown', unlock, { once: true })
    document.addEventListener('keydown', unlock, { once: true })
    // #endif
    // #ifndef H5
    this.unlocked = true
    // #endif
    this.initFloaters()
    this.initAudio()
    this.startDrift()
    this.startAmbient()
    this.themeTimer = setInterval(() => {
      this.themeIdx = (this.themeIdx + 1) % Math.max(this.themeList.length, 1)
      this.$emit('theme-rotate', this.currentTheme)
    }, 12000)
  },
  beforeUnmount() {
    // 及时回收，防低端机发热
    if (this.rafId) cancelAnimationFrame(this.rafId)
    if (this.themeTimer) clearInterval(this.themeTimer)
    if (this.ambientTimer) clearInterval(this.ambientTimer)
    this.audioCtxs.forEach(c => { try { if (typeof c.pause === 'function') c.pause(); if (typeof c.destroy === 'function') c.destroy() } catch (e) { /* 忽略 */ } })
  },
  methods: {
    initFloaters() {
      // 三只瓶子：不同人群头像、不同大小、不同漂速；错开分布在画面上
      const faces = [...FACE_POOL].sort(() => Math.random() - 0.5).slice(0, 3)
      this.floaters = faces.map((face, i) => ({
        face,
        x: this.stageWidth * (0.12 + i * 0.28),
        top: 34 + i * 12 + '%',
        size: 44 + i * 12 + 'px',
        factor: 0.75 + i * 0.25,          // 漂速系数：0.75 / 1.0 / 1.25
        delay: i * 0.8 + 's'
      }))
    },
    pickTheme(i) {
      this.themeIdx = i
      this.$emit('theme-change', this.currentTheme)
    },
    initAudio() {
      const files = ['/static/audio/plink1.wav', '/static/audio/plink2.wav', '/static/audio/plink3.wav', '/static/audio/drop1.wav']
      // H5 用 Web Audio API：预解码 + 即时播放，避免多个 Audio 元素互相打断导致断断续续
      if (typeof window !== 'undefined' && (window.AudioContext || window.webkitAudioContext)) {
        try {
          const AC = window.AudioContext || window.webkitAudioContext
          this.webAudioCtx = new AC()
          files.forEach(f => {
            fetch(f).then(r => r.arrayBuffer()).then(buf =>
              this.webAudioCtx.decodeAudioData(buf).then(dec => { this.audioBufs.push(dec) })
            ).catch(() => { /* 加载失败忽略 */ })
          })
          return
        } catch (e) { /* 回退到 HTML5 Audio */ }
      }
      // 回退：HTML5 Audio / uni 音频
      const useHtml5 = typeof document !== 'undefined' && typeof Audio !== 'undefined'
      this.audioCtxs = files.map(f => {
        if (useHtml5) {
          const a = new Audio(f)
          a.volume = 0.45
          a.preload = 'auto'
          a.style.display = 'none'
          try { document.body.appendChild(a) } catch (e) { /* 忽略 */ }
          return a
        }
        const ctx = uni.createInnerAudioContext()
        ctx.src = f
        ctx.volume = 0.45
        ctx.autoplay = false
        ctx.onError(() => { /* 静默容错 */ })
        return ctx
      })
    },
    startAmbient() {
      // 瓶子沉浮环境音：每 4 秒左右随机轻响一声，85% 概率触发
      this.ambientTimer = setInterval(() => {
        if (!this.soundOn || !this.unlocked) return
        if (Math.random() < 0.85) this.playPlink()
      }, 4000)
    },
    unlockFeedback() {
      // 首次交互后立即轻响一声，让用户马上确认声音已开启
      if (!this.soundOn) return
      this.unlocked = true
      if (this.webAudioCtx && this.webAudioCtx.state === 'suspended') this.webAudioCtx.resume()
      this.playPlink()
    },
    playPlink() {
      // 优先用 Web Audio 播放（无断音、不互相打断）
      if (this.webAudioCtx && this.audioBufs.length) {
        try {
          if (this.webAudioCtx.state === 'suspended') this.webAudioCtx.resume()
          const buf = this.audioBufs[Math.floor(Math.random() * this.audioBufs.length)]
          const src = this.webAudioCtx.createBufferSource()
          src.buffer = buf
          const gain = this.webAudioCtx.createGain()
          gain.gain.value = 0.45
          src.connect(gain).connect(this.webAudioCtx.destination)
          src.start()
          return
        } catch (e) { /* 忽略 */ }
      }
      if (!this.audioCtxs.length) return
      const a = this.audioCtxs[Math.floor(Math.random() * this.audioCtxs.length)]
      try {
        if (typeof a.stop === 'function') a.stop()
        if (typeof a.pause === 'function' && typeof a.currentTime !== 'undefined') { a.currentTime = 0; a.play() }
        else if (typeof a.play === 'function') a.play()
      } catch (e) { /* 忽略 */ }
    },
    toggleSound() {
      this.soundOn = !this.soundOn
      uni.setStorageSync('drift_sound', this.soundOn ? 1 : 0)
      if (this.soundOn) {
        this.unlocked = true
        if (this.webAudioCtx && this.webAudioCtx.state === 'suspended') this.webAudioCtx.resume()
        this.playPlink()
        uni.showToast({ title: '音效已开启', icon: 'none' })
      } else {
        uni.showToast({ title: '已静音', icon: 'none' })
      }
    },
    onBottleTap(i) {
      this.poppedIdx = i
      if (this.soundOn) {
        this.unlocked = true
        this.playPlink()
      }
      setTimeout(() => { if (this.poppedIdx === i) this.poppedIdx = -1 }, 480)
    },
    startDrift() {
      // 背景静止；化身与瓶子组横向漂移（rAF 步进，仅 transform 触发 GPU 合成）
      const step = (ts) => {
        if (!this.lastTs) this.lastTs = ts
        const dt = Math.min((ts - this.lastTs) / 1000, 0.1)   // 秒
        this.lastTs = ts
        this.avatarX += this.speed * dt                        // 化身漂移
        if (this.avatarX >= this.stageWidth) this.avatarX -= this.stageWidth
        for (const f of this.floaters) {
          f.x += this.speed * f.factor * dt                    // 瓶子+头像一起漂
          if (f.x > this.stageWidth + 220) f.x = -220          // 漂出右侧从左侧回来
        }
        this.rafId = requestAnimationFrame(step)
      }
      this.rafId = requestAnimationFrame(step)
    },
    starStyle(n) {
      return {
        left: (n * 37) % 100 + '%',
        top: (n * 53) % 60 + '%',
        opacity: 0.3 + ((n * 17) % 60) / 100,
        animationDelay: (n % 10) * 0.3 + 's'
      }
    }
  }
}
</script>

<style scoped>
.stage {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

/* 主题长卷背景层 */
.bg-layer {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.bg-img {
  position: absolute;
  inset: 0;
  background-size: auto 100%;
  background-position: center;
  background-repeat: no-repeat;
}

/* 缓慢运镜：参数由智能镜头（kbStyle 的 CSS 变量）按主题/活跃度动态注入 */
.bg-img.kb {
  animation: kenburns var(--kb-dur, 28s) ease-in-out infinite alternate;
}

@keyframes kenburns {
  from { transform: scale(var(--kb-s1, 1.06)) translate(var(--kb-x1, 1.2%), var(--kb-y1, 0%)); }
  to { transform: scale(var(--kb-s2, 1.13)) translate(var(--kb-x2, -1.2%), var(--kb-y2, 0%)); }
}

.bg-stars {
  position: absolute;
  inset: 0;
}

/* 主题专属动态贴图层：不拦截点击 */
.decor-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 2;
}

.decor-item {
  position: absolute;
  opacity: 0.8;
  will-change: transform, opacity;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.25));
  line-height: 1;
}

.decor-drift {
  animation-name: decorDrift;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
}

@keyframes decorDrift {
  from { transform: translateX(-14vw); }
  to { transform: translateX(114vw); }
}

.decor-rise {
  animation-name: decorRise;
  animation-timing-function: ease-in;
  animation-iteration-count: infinite;
}

@keyframes decorRise {
  0% { transform: translateY(16vh); opacity: 0; }
  14% { opacity: 0.85; }
  82% { opacity: 0.85; }
  100% { transform: translateY(-42vh); opacity: 0; }
}

.decor-fall {
  animation-name: decorFall;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
}

@keyframes decorFall {
  0% { transform: translateY(-10vh) rotate(0deg); opacity: 0; }
  12% { opacity: 0.9; }
  100% { transform: translateY(46vh) rotate(320deg); opacity: 0; }
}

.decor-twinkle {
  animation-name: decorTwinkle;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
  animation-duration: 2.6s;
  text-shadow: 0 0 8px currentColor;
}

@keyframes decorTwinkle {
  0%, 100% { opacity: 0.12; transform: scale(0.75); }
  50% { opacity: 0.95; transform: scale(1.2); }
}

.star {
  position: absolute;
  width: 2px;
  height: 2px;
  border-radius: 50%;
  background: #ffffff;
  animation: twinkle 2.4s infinite ease-in-out;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.25; }
  50% { opacity: 0.9; }
}

/* 静态水波装饰（不流动） */
.wave {
  position: absolute;
  left: -6%;
  bottom: 0;
  width: 112%;
  height: 24%;
  border-radius: 48% 48% 0 0;
  opacity: 0.32;
}

.wave1 {
  background: rgba(255, 255, 255, 0.16);
}

.wave2 {
  background: rgba(13, 27, 42, 0.32);
  height: 18%;
  opacity: 0.4;
}

/* 瓶子组：外层负责横向漂移（内联 transform），内层负责上下沉浮动画 */
.float-group {
  position: absolute;
  left: 0;
  z-index: 5;
  cursor: pointer;
  filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.35));
  will-change: transform;
}

.float-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.12em;
  animation: bob 3.2s infinite ease-in-out;
}

.float-inner.pop {
  animation: bottlePop 0.48s ease;
}

/* 圆形人物头像：玻璃质感白底 + 描边，位于瓶口上方 */
.fa-avatar {
  width: 2.15em;   /* em 相对头像字号（0.55×组字号），约等于 1.18 倍瓶子大小 */
  height: 2.15em;
  border-radius: 50%;
  font-size: 0.55em;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.88);
  border: 2px solid rgba(255, 255, 255, 0.95);
  box-shadow: 0 3px 8px rgba(15, 30, 51, 0.35);
  overflow: hidden;
}

.fa-bottle {
  font-size: 1em;
  line-height: 1;
}

@keyframes bob {
  0%, 100% { transform: translateY(0) rotate(-8deg); }
  50% { transform: translateY(-10px) rotate(8deg); }
}

@keyframes bottlePop {
  0% { transform: scale(1) rotate(-8deg); }
  40% { transform: scale(1.4) rotate(10deg); }
  70% { transform: scale(0.95) rotate(-4deg); }
  100% { transform: scale(1) rotate(-8deg); }
}

.sound-toggle {
  position: absolute;
  top: calc(env(safe-area-inset-top) + 58px);
  right: 14px;
  z-index: 20;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  background: rgba(15, 30, 51, 0.38);
  backdrop-filter: blur(8px);
  cursor: pointer;
}

.theme-strip {
  position: absolute;
  top: calc(env(safe-area-inset-top) + 62px);
  left: 14px;
  right: 62px;
  z-index: 20;
  white-space: nowrap;
}

.theme-chip {
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  margin-right: 6px;
  border-radius: 999px;
  font-size: 12px;
  color: #ffffff;
  background: rgba(15, 30, 51, 0.42);
  border: 1px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(8px);
  cursor: pointer;
}

.theme-chip.active {
  background: linear-gradient(135deg, #d97706, #f59e0b);
  border-color: rgba(255, 255, 255, 0.4);
  font-weight: 700;
}

.fav-mark {
  font-size: 9px;
  margin-left: 3px;
  color: #fde68a;
}

.avatar-wrap {
  position: absolute;
  bottom: 24%;
  left: 40px;
  z-index: 6;
  text-align: center;
  will-change: transform;
}

.avatar {
  font-size: 40px;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.35));
  animation: bob 2.6s infinite ease-in-out;
}

.tier-chip {
  margin-top: 4px;
  display: inline-block;
  padding: 2px 10px;
  font-size: 11px;
  color: #ffffff;
  background: rgba(30, 58, 95, 0.65);
  border-radius: 999px;
  backdrop-filter: blur(4px);
}
</style>
