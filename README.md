# 漂流瓶 App（drift-bottle）

以「漂流瓶」为核心交互的融合型社交应用：把愿望装进瓶子投向大海，另一座城市的陌生人捞起瓶子、读到心愿并回应。
本仓库依据《漂流瓶 App 开发框架 v1.0》（微信公众号 Daboshik 出品）搭建，一套 uni-app 代码可发布 **Android APK + iOS + H5**。

## 项目结构

```
D:\piaoliuping\
├─ backend\                 FastAPI 后端（Python 3.12）
│  ├─ app\
│  │  ├─ main.py            入口：/api/v1 路由 + CORS + 自动建表与种子数据
│  │  ├─ config.py          配置（密钥/库连接/次数上限/频控参数）
│  │  ├─ database.py        SQLAlchemy（默认 SQLite，可切 MySQL）
│  │  ├─ models.py          8 张核心表：users/regions/bottles/bottle_opens/
│  │  │                     activity_logs/audit_tasks/reports/backgrounds
│  │  ├─ security.py        JWT + 手机号哈希/脱敏
│  │  ├─ audit.py           敏感词机审（生产接内容安全 API + LLM）
│  │  ├─ limiter.py         60 秒短信频控 + 验证码存储（生产换 Redis）
│  │  ├─ activity.py        活跃度算法 + 加权随机捞瓶
│  │  ├─ seed.py            种子：34 省级行政区划、10 主题背景、演示瓶子
│  │  └─ routers\           auth / users / regions / backgrounds /
│  │                        bottles / reports / config(about)
│  ├─ scripts\              一次性迁移脚本（如挂接主题长卷图）
│  └─ data\driftbottle.db   SQLite 数据文件（自动生成）
├─ frontend\                uni-app（Vue 3 + pinia + Vite）
│  ├─ src\pages\            6 页面：index(漂移舞台) / auth(登录) / region(地区)
│  │                        / throw(投瓶) / pick(捞瓶) / about(关于我们)
│  ├─ src\components\       drift-stage(漂移舞台) / region-picker(三级联动)
│  │                        / bottle-card(瓶子卡片)
│  ├─ src\api\              request(统一封装) / auth / bottle / common
│  ├─ src\store\            user / region（pinia）
│  ├─ src\utils\            drift(活跃度→漂移速度) / sensitive(敏感词预检)
│  ├─ src\static\themes\    10 大主题长卷背景图（AI 生成，演示版权安全）
│  └─ src\static\audio\     瓶子音效（玻璃叮声/水滴，代码合成无版权）
└─ README.md
```

## 本地运行（已验证）

### 1. 后端（端口 8010，本机 8000 被其他应用占用）

```powershell
cd D:\piaoliuping\backend
python -m venv .venv                      # 首次
.venv\Scripts\python.exe -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

启动时自动建表 + 灌入种子数据（行政区划 / 主题背景 / 演示用户与瓶子）。
- 健康检查：http://127.0.0.1:8010/api/v1/health
- 接口文档：http://127.0.0.1:8010/docs

### 2. 前端 H5（端口 5173，代理 /api → 8010）

```powershell
cd D:\piaoliuping\frontend
npm install --registry=https://registry.npmmirror.com   # 首次
npm run dev:h5
```

打开 http://127.0.0.1:5173/ 即可体验（开发模式，改动热更新）。
一键脚本：`powershell -File D:\piaoliuping\start-backend.ps1`、`start-frontend.ps1`。

### 3. 生产模式（灯塔模式：单端口对外）

双击桌面「**启动漂流瓶**」快捷方式即可：后端自动启动并同端口托管已构建的 H5（界面+接口统一 `http://<本机IP>:8010`，绑定 `0.0.0.0` 支持外网/局域网访问）。

```powershell
# 前端改动后重新打包（构建产物由后端托管）
cd D:\piaoliuping\frontend ; npm run build:h5
# 重启后端
powershell -File D:\piaoliuping\start-backend.ps1
```

> 首次外网访问如不通，需在 Windows 防火墙放行 8010 入站（需管理员：`netsh advfirewall firewall add rule name="DriftBottle" dir=in action=allow protocol=TCP localport=8010`），云电脑/云服务器还需在服务商安全组放行 8010。

### 4. 演示登录

登录页输入任意 11 位手机号 → 获取验证码（**演示模式自动回显**）→ 勾选协议登入 →
首次引导：**上传头像（可选）+ 年龄/性别/民族/现住址 + 常驻地区 + 3 个兴趣主题（决定首页背景轮换偏好）+ 人群**。

## 已实现功能（对应开发框架）

| 模块 | 说明 |
| --- | --- |
| 首页漂移舞台 | 主题长卷背景**智能运镜**（每主题专属缩放/平移参数 + 随活跃度微调快慢）+ **主题专属动态贴图**（城市飞机/灯火、星空流星、自然飞鸟蝴蝶、民俗孔明灯、科技飞碟、交通海鸥…随环境而变）、头像+瓶子随活跃度漂移、瓶子点击弹跳+音效、🔊 声音开关、10 主题切换条（兴趣主题 ★ 优先，12 秒自动轮换，选择持久化） |
| 登录注册 | 手机号+验证码一键登入，未注册自动创建；60 秒频控；首次引导：**头像上传（≤2MB，JPG/PNG/WebP）+ 年龄/性别/民族（56 民族）/现住址** + 地区/兴趣/人群；个人中心同步展示 |
| 地区选择 | 省→市→区县三级联动、搜索、最近使用记忆；直辖市两级直达；港澳台省级完整列出 |
| 投瓶 | 三步表单：城市→人群→心愿（8 瓶签、200 字、敏感词前端预检）；每日 5 次（高活跃 +1）；同内容 24h 防重复 |
| 捞瓶 | 本市/全省/全国三重筛选 + 人群 + 瓶签多选；加权随机（活跃度上浮权重 0.6~1.6）；每日 10 次；打开/放回/回应/举报；瓶卡内置防诈骗提示 |
| 关于我们 | 出品方（公众号 Daboshik）、漂流瓶规则、合规声明（框架 7.4 全文）、协议入口、适老化**大字模式**开关 |
| 活跃度体系 | 登录 40% + 漂流 30% + 互动 30%（单项封顶防刷）；五档段位：静水深流→微波荡漾→川流不息→乘风破浪→潮头弄浪 |
| 内容安全 | 前端敏感词预检 + 后端机审（audit_tasks 留痕）；先审后显；举报 24h 响应 |

## 打包 Android APK / iOS

1. 用 HBuilderX 打开 `frontend\` 目录（CLI 工程，可直接导入）。
2. 生产前修改 `src/api/request.js` 中非 H5 的 `BASE` 为正式服务器域名（HTTPS）。
3. 菜单「发行 → 原生 App-云打包」生成 APK / IPA；iOS 需 Apple 开发者账号（$99/年）。
4. 上架前完成：ICP 备案、App 备案、软件著作权、内容审核接入（见框架第七章合规清单）。

## 切换生产组件

| 演示实现 | 生产替换 |
| --- | --- |
| SQLite（`data/driftbottle.db`） | 环境变量 `DRIFT_DATABASE_URL=mysql+pymysql://user:pass@host:3306/driftbottle?charset=utf8mb4` |
| 内存频控/验证码（limiter.py） | Redis（接口一致，直接换实现） |
| 演示短信（验证码回显） | 阿里云/腾讯云短信模板（config.py `SMS_MOCK=0`） |
| 本地敏感词机审 | 阿里云内容安全 / 数美 / 易盾 + LLM 存疑人审 |
| 本地长卷图 `/static/themes/*.jpg` | OSS/CDN WebP（backgrounds.oss_url） |
| 无推送 | uni-push（瓶子被捞起/收到回应提醒） |

## 已知演示限制

- 演示数据为 34 省级 + 代表性城市区县子集；生产接入民政部 GB/T 2260 全量（3000+ 条）。
- 瓶子回应暂无实时推送，仅在对方个人中心可见（V2 规划：私信/uni-push）。
- 音效首次播放需用户先点击页面一次（浏览器自动播放策略）；App 端无此限制。
- 头像存本地 `data/uploads/avatars/`，生产替换为 OSS。

> AI生成
