<template>
  <view class="page" :class="{ 'font-large': store.bigFont }">
    <!-- 第 1 步：手机号 + 验证码登入 -->
    <view v-if="step === 1" class="card form">
      <view class="title-bar">手机号一键登入</view>
      <text class="muted tip">已注册直接登录 · 未注册自动创建账号</text>

      <view class="field">
        <text class="field-label">手机号</text>
        <input class="field-input" type="number" maxlength="11" v-model="phone" placeholder="请输入 11 位手机号" />
      </view>

      <view class="field">
        <text class="field-label">验证码</text>
        <view class="code-row">
          <input class="field-input" type="number" maxlength="6" v-model="code" placeholder="6 位验证码" />
          <view class="send-btn" :class="{ disabled: sending || countdown > 0 || !phoneValid }" @click="send">
            {{ countdown > 0 ? countdown + 's' : '获取验证码' }}
          </view>
        </view>
      </view>

      <view class="agree-row" @click="agreed = !agreed">
        <view class="checkbox" :class="{ checked: agreed }">{{ agreed ? '✓' : '' }}</view>
        <text class="agree-text">我已阅读并同意《用户协议》与《隐私政策》</text>
      </view>

      <view class="btn-primary submit" :class="{ disabled: !canSubmit }" @click="doLogin">登 入</view>
      <text class="muted center-tip">演示环境验证码自动回显，无需真实短信</text>
    </view>

    <!-- 第 2 步：首次引导（地区 + 兴趣主题 + 人群） -->
    <view v-else class="card form">
      <view class="title-bar">完成初次引导</view>
      <text class="muted tip">上传头像、完善资料，选常驻地区 + 挑 3 个兴趣主题（决定首页背景）</text>

      <!-- 头像上传 -->
      <view class="avatar-upload" @click="chooseAvatar">
        <view class="avatar-ring">
          <image v-if="avatarUrl" :src="avatarUrl" class="avatar-img" mode="aspectFill" />
          <text v-else class="avatar-plus">📷</text>
        </view>
        <text class="avatar-tip">{{ avatarUploading ? '上传中…' : (avatarUrl ? '点击更换头像' : '上传头像（可选）') }}</text>
      </view>

      <view class="field">
        <text class="field-label">常驻地区</text>
        <view class="field-input select" @click="showRegion = true">
          {{ regionLabel || '点击选择省 / 市 / 区县' }}
        </view>
      </view>

      <view class="field-row">
        <view class="field half-field">
          <text class="field-label">年龄（16-60 岁）</text>
          <input class="field-input num" type="number" maxlength="2" v-model="age" placeholder="如 28" />
        </view>
        <view class="field half-field">
          <text class="field-label">性别</text>
          <view class="chips gender-chips">
            <text v-for="g in genders" :key="g" class="tag" :class="{ active: gender === g }"
              @click="gender = g">{{ g }}</text>
          </view>
        </view>
      </view>

      <view class="field">
        <text class="field-label">民族</text>
        <picker mode="selector" :range="ethnicities" @change="onEthnicityChange">
          <view class="field-input select">{{ ethnicity || '点击选择民族' }}</view>
        </picker>
      </view>

      <view class="field">
        <text class="field-label">现住址（详细地址，选填）</text>
        <input class="field-input" type="text" v-model="address" maxlength="60" placeholder="如：××区××街道××小区" />
      </view>

      <view class="field">
        <text class="field-label">兴趣主题（选 3 个）</text>
        <view class="chips">
          <text v-for="t in allThemes" :key="t" class="tag"
            :class="{ active: interestTags.indexOf(t) >= 0 }" @click="toggleTheme(t)">{{ t }}</text>
        </view>
      </view>

      <view class="field">
        <text class="field-label">人群年龄段</text>
        <view class="chips">
          <text v-for="c in crowds" :key="c" class="tag"
            :class="{ active: crowd === c }" @click="crowd = c">{{ c }}</text>
        </view>
      </view>

      <view class="btn-primary submit" @click="finishOnboarding">完成，进入漂流瓶</view>
    </view>

    <region-picker :visible="showRegion" @confirm="onRegionConfirm" @close="showRegion = false" />
  </view>
</template>

<script>
import regionPicker from '../../components/region-picker.vue'
import { useUserStore } from '../../store/user'
import { useRegionStore } from '../../store/region'
import { sendSms } from '../../api/auth'
import { getBackgrounds } from '../../api/common'
import { toastError, API_BASE, getToken } from '../../api/request'

export default {
  components: { regionPicker },
  data() {
    return {
      store: useUserStore(),
      regionStore: useRegionStore(),
      step: 1,
      phone: '',
      code: '',
      agreed: false,
      sending: false,
      countdown: 0,
      showRegion: false,
      allThemes: ['城市', '自然', '星空', '世界景点', '世界人文', '科技创新', '漫画', '名画', '交通', '战争与武器'],
      interestTags: [],
      crowd: '不限',
      crowds: ['不限', '青年16-30', '中坚31-45', '沉淀46-60'],
      selectedRegion: null,
      avatarUrl: '',
      avatarUploading: false,
      age: '',
      gender: '保密',
      genders: ['男', '女', '保密'],
      ethnicity: '',
      ethnicities: ['汉族', '蒙古族', '回族', '藏族', '维吾尔族', '苗族', '彝族', '壮族', '布依族', '朝鲜族', '满族', '侗族', '瑶族', '白族', '土家族', '哈尼族', '哈萨克族', '傣族', '黎族', '傈僳族', '佤族', '畲族', '高山族', '拉祜族', '水族', '东乡族', '纳西族', '景颇族', '柯尔克孜族', '土族', '达斡尔族', '仫佬族', '羌族', '布朗族', '撒拉族', '毛南族', '仡佬族', '锡伯族', '阿昌族', '普米族', '塔吉克族', '怒族', '乌孜别克族', '俄罗斯族', '鄂温克族', '德昂族', '保安族', '裕固族', '京族', '塔塔尔族', '独龙族', '鄂伦春族', '赫哲族', '门巴族', '珞巴族', '基诺族'],
      address: ''
    }
  },
  computed: {
    phoneValid() { return /^1[3-9]\d{9}$/.test(this.phone) },
    canSubmit() { return this.phoneValid && this.code.length >= 4 && this.agreed },
    regionLabel() {
      const r = this.selectedRegion
      return r ? [r.province, r.city, r.district].filter(Boolean).join(' ') : ''
    }
  },
  methods: {
    async send() {
      if (this.countdown > 0 || !this.phoneValid) return
      this.sending = true
      try {
        const data = await sendSms(this.phone)
        uni.showToast({ title: '验证码已发送', icon: 'none' })
        if (data && data.mock_code) this.code = data.mock_code   // 演示模式自动填入
        this.countdown = 60
        const t = setInterval(() => {
          this.countdown -= 1
          if (this.countdown <= 0) clearInterval(t)
        }, 1000)
      } catch (e) {
        toastError(e)
      } finally {
        this.sending = false
      }
    },
    async doLogin() {
      if (!this.canSubmit) return
      try {
        const profile = await this.store.login(this.phone, this.code)
        if (profile.is_new) {
          this.step = 2
        } else {
          uni.reLaunch({ url: '/pages/index/index' })
        }
      } catch (e) {
        toastError(e)
      }
    },
    async loadThemes() {
      try {
        const bgs = await getBackgrounds()
        const themes = [...new Set(bgs.map(b => b.theme))]
        if (themes.length === 10) this.allThemes = themes
      } catch (e) { /* 使用内置清单 */ }
    },
    toggleTheme(t) {
      const i = this.interestTags.indexOf(t)
      if (i >= 0) this.interestTags.splice(i, 1)
      else if (this.interestTags.length < 3) this.interestTags.push(t)
      else uni.showToast({ title: '最多选 3 个兴趣主题', icon: 'none' })
    },
    onRegionConfirm(sel) {
      this.selectedRegion = sel
      this.regionStore.setRegion(sel)
      this.showRegion = false
    },
    onEthnicityChange(e) {
      this.ethnicity = this.ethnicities[Number(e.detail.value)] || ''
    },
    chooseAvatar() {
      if (this.avatarUploading) return
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        success: (res) => {
          const filePath = res.tempFilePaths && res.tempFilePaths[0]
          if (filePath) this.uploadAvatar(filePath)
        }
      })
    },
    uploadAvatar(filePath) {
      this.avatarUploading = true
      uni.uploadFile({
        url: API_BASE + '/user/avatar',
        filePath,
        name: 'file',
        header: { Authorization: 'Bearer ' + getToken() },
        success: (res) => {
          try {
            const body = JSON.parse(res.data)
            if (body.code === 0) {
              this.avatarUrl = body.data.avatar_url + '?t=' + Date.now()
              uni.showToast({ title: '头像已设置', icon: 'success' })
            } else {
              uni.showToast({ title: body.detail || '上传失败', icon: 'none' })
            }
          } catch (e) {
            uni.showToast({ title: '上传失败', icon: 'none' })
          }
        },
        fail: () => uni.showToast({ title: '上传失败，请重试', icon: 'none' }),
        complete: () => { this.avatarUploading = false }
      })
    },
    async finishOnboarding() {
      if (!this.selectedRegion) {
        uni.showToast({ title: '请选择常驻地区', icon: 'none' })
        return
      }
      if (this.interestTags.length < 3) {
        uni.showToast({ title: '请挑选 3 个兴趣主题', icon: 'none' })
        return
      }
      const ageNum = parseInt(this.age, 10)
      if (!ageNum || ageNum < 16 || ageNum > 60) {
        uni.showToast({ title: '请填写 16-60 岁的年龄', icon: 'none' })
        return
      }
      try {
        await this.store.updateProfile({
          region_id: this.selectedRegion.cityId,
          interest_tags: this.interestTags,
          crowd: this.crowd,
          age: ageNum,
          gender: this.gender,
          ethnicity: this.ethnicity,
          address: this.address.trim()
        })
        uni.reLaunch({ url: '/pages/index/index' })
      } catch (e) {
        toastError(e)
      }
    }
  },
  onLoad() {
    this.loadThemes()
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 24px 16px;
  box-sizing: border-box;
  background: linear-gradient(170deg, #eaf1fb 0%, #f4f7fb 60%);
}

.form {
  max-width: 460px;
  margin: 12vh auto 0;
}

.tip {
  display: block;
  margin: 6px 0 18px;
}

/* 头像上传 */
.avatar-upload {
  text-align: center;
  margin-bottom: 18px;
}

.avatar-ring {
  width: 84px;
  height: 84px;
  margin: 0 auto;
  border-radius: 50%;
  border: 2px dashed #4f8ef7;
  background: #f0f5ff;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  cursor: pointer;
}

.avatar-img {
  width: 100%;
  height: 100%;
}

.avatar-plus {
  font-size: 30px;
}

.avatar-tip {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #5b6b80;
}

.field-row {
  display: flex;
  gap: 12px;
}

.half-field {
  flex: 1;
}

.field-input.num {
  height: 48px;
  display: flex;
  align-items: center;
}

.gender-chips {
  display: flex;
  gap: 8px;
}

.gender-chips .tag {
  padding: 10px 16px;
}

.field {
  margin-bottom: 16px;
}

.field-label {
  display: block;
  font-size: 13px;
  color: #5b6b80;
  margin-bottom: 8px;
}

.field-input {
  background: #f4f7fb;
  border-radius: 12px;
  padding: 12px 14px;
  font-size: 15px;
  width: 100%;
  height: 48px;              /* 显式高度：修复 uni-input 内部 input height:100% 塌陷为 0 导致无法点击输入 */
  box-sizing: border-box;
  display: flex;
  align-items: center;
}

.field-input.select {
  color: #1e3a5f;
  font-weight: 600;
}

.code-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.code-row .field-input {
  flex: 1;
}

.send-btn {
  background: #e8f0fe;
  color: #1e3a5f;
  font-size: 13px;
  font-weight: 600;
  border-radius: 999px;
  padding: 11px 14px;
  white-space: nowrap;
}

.send-btn.disabled {
  opacity: 0.5;
}

.agree-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 6px 0 18px;
}

.checkbox {
  width: 18px;
  height: 18px;
  border-radius: 6px;
  border: 1.5px solid #c9d6f3;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #ffffff;
  flex-shrink: 0;
}

.checkbox.checked {
  background: linear-gradient(135deg, #1e3a5f, #4f8ef7);
  border-color: #4f8ef7;
}

.agree-text {
  font-size: 12px;
  color: #5b6b80;
}

.submit {
  margin-top: 6px;
}

.center-tip {
  display: block;
  text-align: center;
  margin-top: 12px;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
