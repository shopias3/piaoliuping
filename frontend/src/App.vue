<script>
export default {
  onLaunch() {
    console.log('漂流瓶 App 启动')
  }
}
</script>

<style>
/* ===== 全局基础样式（设计规范：深海蓝主色 + 玻璃拟态卡片 + 大圆角）===== */
page,
body {
  background: #f4f7fb;
  color: #1f2d3d;
  font-family: -apple-system, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

.card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(30, 58, 95, 0.08);
}

.btn-primary {
  background: linear-gradient(135deg, #1e3a5f 0%, #4f8ef7 100%);
  color: #ffffff;
  border-radius: 999px;
  font-weight: 600;
  text-align: center;
  padding: 13px 0;
}

.btn-primary.disabled {
  opacity: 0.45;
}

.btn-ghost {
  background: rgba(255, 255, 255, 0.85);
  color: #1e3a5f;
  border: 1px solid #c9d6f3;
  border-radius: 999px;
  text-align: center;
  padding: 12px 0;
}

.tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  background: #e8f0fe;
  color: #1e3a5f;
}

.tag.active {
  background: linear-gradient(135deg, #1e3a5f, #4f8ef7);
  color: #ffffff;
}

.title-bar {
  font-size: 18px;
  font-weight: 700;
  color: #0f1e33;
}

/* 适老化大字模式：正文 18px */
.font-large {
  font-size: 18px;
}

.muted {
  color: #5b6b80;
  font-size: 12px;
}
</style>
