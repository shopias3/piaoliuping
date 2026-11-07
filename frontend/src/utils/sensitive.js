// 前端敏感词预检（与后端 audit.py 词库一致；生产由 AI 机审兜底）
const SENSITIVE_WORDS = [
  '赌博', '博彩', '赌球', '赌场', '六合彩', '外围下注',
  '代开发票', '办证刻章', '办假证', '洗钱', '套现',
  '色情', '裸聊', '援交', '约炮',
  '毒品', '冰毒', '大麻', '枪支买卖', '买枪', '爆炸物',
  '刷单', '兼职刷信誉', '高利贷', '套路贷',
  '加微信转账', '先转账', '汇款到安全账户', '给我转账', '打钱给我',
  '反动', '分裂国家', '恐怖袭击',
  '贷款包过', '无抵押放款', '内部渠道买分',
  '加我QQ', '加我微信', '加V', '威信同号', '飞机号'
]

export function preCheck(text) {
  const cleaned = (text || '').trim()
  if (!cleaned) return { ok: false, msg: '先写点什么放进瓶子里吧' }
  if (cleaned.length > 200) return { ok: false, msg: '心愿最多 200 字' }
  for (const w of SENSITIVE_WORDS) {
    if (cleaned.indexOf(w) >= 0) return { ok: false, msg: '内容含违禁词「' + w + '」，请修改' }
  }
  if (/https?:\/\/|www\./i.test(cleaned)) return { ok: false, msg: '请勿在心愿中留链接' }
  return { ok: true, msg: '' }
}
