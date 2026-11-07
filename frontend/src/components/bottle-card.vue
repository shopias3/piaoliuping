<template>
  <view class="bc-mask" @click="$emit('close')">
    <view class="bc-card" @click.stop>
      <!-- 未打开：密封瓶 -->
      <view v-if="!opened" class="bc-sealed">
        <text class="bc-bottle-emoji">🍾</text>
        <view class="bc-type-tag">{{ bottle.type_name }}</view>
        <text class="bc-hint">来自{{ bottle.city_name }}的瓶子 · {{ bottle.target_crowd }}</text>
        <view class="btn-primary bc-open-btn" @click="$emit('open')">打开瓶子</view>
      </view>

      <!-- 已打开：心愿内容 + 操作 -->
      <view v-else class="bc-opened">
        <view class="bc-head">
          <view class="bc-type-tag">{{ bottle.type_name }}</view>
          <text class="bc-meta">{{ bottle.city_name }} · {{ bottle.created_at }}</text>
        </view>
        <view class="bc-content">{{ bottle.content }}</view>
        <view class="bc-warn">⚠️ {{ antiFraud }}</view>

        <!-- 回应输入 -->
        <view v-if="showReply" class="bc-reply">
          <textarea v-model="replyText" class="bc-reply-input" maxlength="200"
            placeholder="写一句温暖的话，封进瓶子漂回去（≤200字）" />
          <view class="bc-reply-actions">
            <view class="btn-ghost bc-mini" @click="showReply = false">取消</view>
            <view class="btn-primary bc-mini" :class="{ disabled: !replyText.trim() }" @click="submitReply">封瓶回应</view>
          </view>
        </view>

        <!-- 举报 -->
        <view v-if="showReport" class="bc-reply">
          <view class="bc-reasons">
            <text v-for="r in reasons" :key="r" class="tag reason" :class="{ active: reason === r }"
              @click="reason = r">{{ r }}</text>
          </view>
          <view class="bc-reply-actions">
            <view class="btn-ghost bc-mini" @click="showReport = false">取消</view>
            <view class="btn-primary bc-mini danger" @click="submitReport">提交举报</view>
          </view>
        </view>

        <view v-if="!showReply && !showReport" class="bc-actions">
          <view class="btn-ghost bc-act" @click="showReply = true">回应</view>
          <view class="btn-ghost bc-act" @click="$emit('back')">放回海里</view>
          <view class="btn-ghost bc-act warn" @click="showReport = true">举报</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'bottle-card',
  props: {
    bottle: { type: Object, required: true },
    opened: { type: Boolean, default: false },
    antiFraud: { type: String, default: '谨防诈骗：请勿向陌生人转账汇款。' }
  },
  emits: ['open', 'back', 'reply', 'report', 'close'],
  data() {
    return {
      showReply: false,
      showReport: false,
      replyText: '',
      reason: '',
      reasons: ['违法违规', '诈骗引导', '色情低俗', '广告导流', '人身攻击', '其他']
    }
  },
  watch: {
    opened(v) {
      if (!v) { this.showReply = false; this.showReport = false }
    }
  },
  methods: {
    submitReply() {
      const text = this.replyText.trim()
      if (!text) return
      this.$emit('reply', text)
      this.showReply = false
      this.replyText = ''
    },
    submitReport() {
      if (!this.reason) {
        uni.showToast({ title: '请选择举报理由', icon: 'none' })
        return
      }
      this.$emit('report', this.reason)
      this.showReport = false
      this.reason = ''
    }
  }
}
</script>

<style scoped>
.bc-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 30, 51, 0.55);
  z-index: 998;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.bc-card {
  width: 100%;
  max-width: 420px;
  background: #ffffff;
  border-radius: 20px;
  padding: 22px 18px;
  box-sizing: border-box;
  box-shadow: 0 12px 40px rgba(15, 30, 51, 0.3);
}

.bc-sealed {
  text-align: center;
  padding: 8px 0;
}

.bc-bottle-emoji {
  font-size: 56px;
  display: block;
  animation: bcBob 2.4s infinite ease-in-out;
}

@keyframes bcBob {
  0%, 100% { transform: rotate(-6deg); }
  50% { transform: rotate(6deg) translateY(-6px); }
}

.bc-type-tag {
  display: inline-block;
  margin-top: 10px;
  padding: 4px 14px;
  border-radius: 999px;
  background: #e8f0fe;
  color: #1e3a5f;
  font-size: 13px;
  font-weight: 600;
}

.bc-hint {
  display: block;
  margin-top: 10px;
  color: #5b6b80;
  font-size: 13px;
}

.bc-open-btn {
  margin: 18px 30px 4px;
}

.bc-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.bc-meta {
  color: #5b6b80;
  font-size: 12px;
}

.bc-content {
  background: #f4f7fb;
  border-radius: 14px;
  padding: 14px;
  font-size: 15px;
  line-height: 1.7;
  color: #1f2d3d;
  white-space: pre-wrap;
  word-break: break-all;
}

.bc-warn {
  margin-top: 10px;
  font-size: 12px;
  color: #b45309;
  background: #fff7ed;
  border-radius: 10px;
  padding: 8px 10px;
}

.bc-reply {
  margin-top: 12px;
}

.bc-reply-input {
  width: 100%;
  height: 90px;
  background: #f4f7fb;
  border-radius: 12px;
  padding: 10px;
  font-size: 14px;
  box-sizing: border-box;
}

.bc-reply-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  justify-content: flex-end;
}

.bc-mini {
  padding: 8px 18px;
  font-size: 13px;
}

.btn-primary.danger {
  background: linear-gradient(135deg, #b91c1c, #ef4444);
}

.bc-reasons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.reason {
  padding: 6px 12px;
}

.bc-actions {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}

.bc-act {
  flex: 1;
  font-size: 14px;
  font-weight: 600;
}

.bc-act.warn {
  color: #b91c1c;
  border-color: #fecaca;
}
</style>
