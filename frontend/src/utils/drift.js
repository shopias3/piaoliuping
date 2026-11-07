// 活跃度 → 漂移速度/段位/上浮权重（与后端 activity.py 公式一致）

// 活跃度 0–100：登录 40% + 漂流 30% + 互动 30%，单项封顶防刷
export function activityScore(d) {
  const part = (w, v, cap) => Math.min(v / cap, 1) * w * 100
  return Math.round(part(0.4, d.loginDays, 20)
    + part(0.3, d.bottleTimes, 30)
    + part(0.3, d.replyTimes, 40))
}

// 漂移速度：24–144 px/s，随活跃度线性增长
export function driftSpeed(score) {
  return Math.round(24 + score * 1.2)
}

// 瓶子上浮权重：捞瓶加权随机的关键参数（与速度分档一致）
export function floatWeight(score) {
  if (score > 80) return 1.6
  if (score > 60) return 1.3
  if (score > 40) return 1.0
  if (score > 20) return 0.8
  return 0.6
}

// 漂移五档段位（轻量荣誉体系）
export const TIERS = [
  { min: 0, name: '静水深流', desc: '活跃度 0-20 · 漂移 24-48 米/分' },
  { min: 21, name: '微波荡漾', desc: '活跃度 21-40 · 漂移 48-72 米/分' },
  { min: 41, name: '川流不息', desc: '活跃度 41-60 · 漂移 72-96 米/分' },
  { min: 61, name: '乘风破浪', desc: '活跃度 61-80 · 漂移 96-120 米/分' },
  { min: 81, name: '潮头弄浪', desc: '活跃度 81-100 · 漂移 120-144 米/分' }
]

export function tierOf(score) {
  let t = TIERS[0]
  for (const item of TIERS) {
    if (score >= item.min) t = item
  }
  return t
}

// 漂移速度（现实单位展示）：动画内部仍用 px/s 驱动，
// 展示按 1px = 1米/分钟 折算：24-144 米/分 ≈ 0.4-2.4 米/秒，符合真实水流漂速
export function driftSpeedPerMin(score) {
  return driftSpeed(score)
}
