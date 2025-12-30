# 更新日志

## v1.1.3 (2024-12-31) - 动画系统全面升级 + 交互体验优化

### 🎬 动画系统全面升级

#### 缓动函数优化
- **全局统一缓动**：使用 `cubic-bezier(0.4, 0, 0.2, 1)` 作为标准缓动
- **弹性效果**：使用 `cubic-bezier(0.175, 0.885, 0.32, 1.275)` 实现弹跳效果
- **所有transition时间统一**：0.3s-0.4s，体验更一致

#### 数字滚动动画增强
- **缓动函数**：改用 `easeOutExpo`，更自然的减速效果
- **动画时长**：从1.2s延长到1.8s
- **视觉反馈**：数字变化时有scale微动效果
- **颜色变化**：滚动时变为cyan色，完成后恢复
- **完成动画**：新增 `numComplete` 弹跳效果
- **延迟触发**：避免同时触发大量动画

#### 信封拆开动画大升级
| 效果 | 优化内容 |
|------|----------|
| 整体交互 | hover时scale(1.02)，点击时scale(0.98)反馈 |
| 信封盖翻转 | 1.2s → 2.5s，更优雅 |
| 封印动画 | 新增脉冲发光 `seal-pulse`，hover放大1.1 |
| 提示文字 | 新增上下弹跳 `hint-bounce` |
| 信纸展开 | 增加scale效果，延迟增加到2s |
| 粒子特效 | 第一波15个心形粒子 + 第二波8个sparkle上升粒子 |
| 阴影效果 | 打开后发光阴影增强 |

### 📊 图表动画优化

#### 折线图动画顺序调整
- **原来**：先画线，后出现点
- **现在**：先出现点（0.3s起），再连线（2s起）
- **效果**：更符合直觉，像是在"连点成线"

#### 能量爆棚动画延长
- 线条绘制：3s → 5s
- 填充动画：1.5s延迟2s → 2.5s延迟3s

#### 热力图动画优化
- 月份卡片：弹跳进入 + hover上浮5px
- 柱状图：新增弹跳效果（80%时超出5%再回落）
- Tooltip：缩放+位移过渡

### 🎯 全局交互增强（新增）

#### 悬停效果
| 元素 | hover效果 |
|------|-----------|
| 按钮 | scale(1.05) + 阴影，点击scale(0.95) |
| 卡片 | translateY(-5px~-8px) + 阴影增强 |
| 数字 `.num` | scale(1.1) + 变色cyan |
| 头像/图标 | scale(1.2) + rotate(5deg) |
| 标签 | translateY(-2px) + scale(1.05) |
| 进度条 | 统一1.2s cubic-bezier缓动 |

#### 各组件动画优化
| 组件 | 优化内容 |
|------|----------|
| `.section-title` | letter-spacing从15px动画到normal |
| `.section-subtitle` | 新增淡入动画，延迟0.3s |
| `.hero-stat` | 更丰富的弹跳：scale(0.3)→1.15→0.95→1 |
| `.story-line` | 边框颜色动画 + hover右移效果 |
| `.chemistry-card` | 滑入+缩放组合，hover放大1.02 |
| `.number-card` | 顶部彩条展开动画（scaleX） |
| `.festival-card` | 图标hover旋转10deg |

### 🎨 视觉优化

#### 开场动画时间调整
- 问候语"辛苦了"显示：4s → 5.5s
- 热力图展示：7.5s → 10s
- 年度旅程展示：13.5s → 17s
- **总时长增加**：更从容的节奏

#### 布局优化
- **年度洞察**：居中显示，max-width:800px
- **节日图鉴第一名**：改为半行宽度（去掉span 2）
- **年度旅程**：每月显示"最多聊 XXX"
- **默契排行榜第一名**：直接显示，无需点击
- **默契环形圈**：修复动画，正确显示分数

#### 背景效果
- **星星z-index**：0 → 1，更明显
- **水彩线条装饰**：右下角和左上角添加淡淡的渐变水彩效果

### 📁 文件变更
```
修改文件：
└── A_report_generator.py  # 动画系统升级，行数 9388→9550
```

### 💡 技术亮点
- 使用CSS变量实现动态动画参数
- IntersectionObserver实现延迟触发，避免性能问题
- requestAnimationFrame实现平滑数字滚动
- 多阶段关键帧动画实现复杂效果

---

## v1.1.3 (2024-12-31) - 模块化重构 + 性能优化 + 视觉美化

### 🏗️ 架构重构
- **真正的模块化**：CSS和JS从主文件分离，通过 `get_css_styles()` 和 `get_js_scripts()` 函数调用
- **代码精简**：主文件从 9288 行精简到 5908 行（↓36%）
- **模块缺失检测**：缺少模块文件时会报错提示，不再静默失败

### ⚡ 性能优化 (A_scripts.py)
- **DOM操作优化**：使用 `DocumentFragment` 批量插入元素
  - `createFirework()` - 30个火花一次性插入
  - `createStars()` - 100颗星星一次性插入
  - `createHeartParticles()` - 心形粒子批量插入
- **动画帧优化**：用 `requestAnimationFrame` 替代 `setInterval`
  - `createParticles()` - 粒子生成
  - `createMeteors()` - 流星雨
  - `randomFireworks()` - 随机烟花
- **懒加载观察器**：新增 `honorObserver` 和 `socialObserver`

### 🎨 视觉美化 (A_styles.py)

#### 卡片hover效果增强
| 元素 | 新效果 |
|------|--------|
| `.ranking-card` | 上移5px + 阴影 + 顶部渐变条 |
| `.rank-item` | 右移5px + 粉色背景 + 排名变色 |
| `.friend-group` | 上移3px + 阴影 + 角落光晕 |
| `.stat-box` | 放大1.05 + 发光边框 |
| `.data-card` | 上移3px + 紫色边框 + 阴影 |
| `.insight-item` | 右移5px + 背景加深 + 边框变色 |
| `.chemistry-card` | 增强阴影 + 背景变化 |
| `.highlight-card` | 上移5px + 渐变背景叠加 |
| `.honor-card` | 上移5px + 旋转光效 |
| `.title-card` | 上移5px + 放大1.02 + 闪光扫过 |
| `.moment-card` | 右移8px + 青色边框 |

#### 数字发光效果
- `.stat-num` - 添加 `text-shadow` 发光
- `.vs-val` - 大数字脉冲发光动画 `numGlow`
- `.gstat-val` - 群聊统计数字发光
- `.fg-count` - 好友分组数字发光
- `.chemistry-rank` - 排名数字金色发光

#### 进度条动画
- `.rank-fill` - 添加 `shimmer` 闪光扫过效果

#### 结语页面增强
- 添加径向渐变背景光晕 `endingGlow` 动画
- emoji摇摆动画 `endingBounce`
- 标题闪烁效果 `titleShine`
- 高亮区域hover效果 + 毛玻璃

### 📁 文件变更
```
修改文件：
├── A_report_generator.py  # 重构：调用外部模块，行数 9288→5908
├── A_styles.py            # 完整CSS + 美化，行数 ~1800
└── A_scripts.py           # 完整JS，行数 ~1860
```

### 💡 使用说明
三个文件必须在同一目录下，运行：
```bash
python A_report_generator.py
```

---

## v1.1.3 (2024-12-31) - 动画增强版

### 🎬 全局动画系统升级

#### 新增动画关键帧
- `fadeIn` - 基础淡入
- `fadeInLeft` - 从左侧滑入
- `fadeInRight` - 从右侧滑入
- `fadeInScale` - 缩放淡入
- `bounce` - 弹跳效果
- `bounceIn` - 弹跳进入
- `growBar` - 条形图增长（支持CSS变量）
- `growHeight` - 高度增长
- `drawCircle` - 圆环绘制（SVG stroke-dasharray）
- `numberGlow` - 数字光效
- `cardFloat` - 卡片悬浮
- `shimmer` - 闪光扫过
- `ripple` - 脉冲波纹
- `rotateIn` - 旋转进入

### 📊 热力图动画优化
- **月份卡片**：`bounceIn` 弹跳进入，依次延迟 0.1s
- **悬浮效果**：`scale(1.08) translateY(-5px)` + 阴影增强
- **热力条**：`::before` 伪元素实现从下往上的填充动画
- **Tooltip**：增加缩放 + 位移过渡效果

### 📈 排行榜动画优化
- **卡片悬浮**：`translateY(-5px)` + 阴影增强
- **排行项**：`fadeInLeft` 从左侧滑入，支持 `--delay` CSS变量
- **前三名特殊样式**：金/银/铜色 + 字号递减
- **进度条**：`growBar` 动画 + `::after` 闪光扫过效果

### 👤 用户画像卡片优化
- **卡片整体**：悬浮时上移 8px + 紫色阴影
- **闪光扫过**：`::after` 伪元素实现 hover 时光效
- **图标**：持续弹跳动画
- **置信度条**：`growBar` 增长动画，延迟 0.5s
- **标签**：`bounceIn` 弹跳进入，hover 时放大 1.1 倍

### 💕 默契度卡片优化
- **卡片进入**：`translateX(-30px) scale(0.95)` → 原位
- **圆环分数**：SVG `stroke-dasharray` 绘制动画 1.5s
- **数字**：`numberGlow` 光效

### 📋 聊天卡片优化
- **悬浮效果**：`translateX(5px)` + 阴影 + 边框颜色变化
- **展开动画**：`max-height` 过渡 0.5s + `opacity` 淡入

### 🎯 滚动触发动画优化
- **新增类**：`slide-in-left`、`slide-in-right`、`scale-in`、`parallax-item`
- 使用 `cubic-bezier` 缓动曲线

### ⚡ JavaScript 增强
- 新增 `animateCircles()` - SVG圆环绘制动画
- 新增 `initParallax()` - 视差滚动效果
- 优化 `animateBars()` - 支持CSS变量

---

## v1.1.2 (2024-12-30) - 年度来信重构

### 💌 年度来信重构
- **视角反转**：改为好友写给用户的信（原来是用户写给好友）
  - 标题："来自 XXX 的一封信"
  - 称呼：用户昵称
  - 署名：好友名字
- **展开动画优化**
  - 信封盖子使用弹性曲线翻转
  - 封印旋转消失效果
  - 信纸平滑上移+淡入
  - 展开时飘出心形粒子特效 💕✨💗

### 📂 数据目录统一
- 默认数据目录改为 `data` 文件夹
- `A_batch_analyzer.py` 和 `A_report_generator.py` 统一使用
- 目录不存在时给出清晰提示

### 🧭 导航栏改版
- **PC端**：右侧竖向圆点导航，悬浮显示标签，激活状态渐变发光
- **移动端**：底部居中胶囊导航条

### 📐 间距优化
- Section间距缩短约30%（PC端 60px→40px，移动端 80px→30px/50px）

### 🎬 开场动画优化
- 年历→旅程无缝衔接，删除数字爆发阶段
- 总时长：30秒 → 26秒
- 消息片段改为有信息量的内容

### 📱 其他调整
- 删除首页故事介绍
- 音乐/截图按钮移到左侧

---

## v1.1.1 (2024-12-30) - 数据目录统一

### 📂 数据目录统一
- **默认数据目录改为 `data` 文件夹**
- 如果 `data` 目录不存在，会给出清晰的提示信息
- 仍支持命令行参数指定其他目录

### 🧭 导航栏改版
- **PC端**：右侧竖向圆点导航（10px），悬浮显示标签名，激活状态渐变发光，玻璃拟态背景
- **移动端**：底部居中胶囊导航条，可横向滚动

### 📐 间距优化
- Section间距缩短约30%
- 各模块内部间距统一缩短

### 🎬 开场动画优化
- 总时长：30秒 → 26秒
- 热力图bar高度增加：200px → 250px
- 消息片段改为有信息量的内容

### 💌 年度来信优化
- 信封展开动画减慢（0.8s → 1.5s）
- 署名改为用户自己的昵称

### 📱 其他调整
- 删除首页的"最重要的人"和"哪个月最活跃"故事介绍
- 音乐按钮移到左上角
- 截图按钮移到左下角

---

## v1.1.0 (2024-12-30) - 开场动画大升级

### 🎬 开场动画大升级
- **整合聊天年历和年度旅程到开场动画**：30秒沉浸式体验
- **PC端尺寸优化**：热力图柱状图40px宽、最高200px
- **年度旅程改为时间线样式**：垂直排列、左右交替

### 📱 手机端适配优化
- 私聊详情卡片姓名不再被挤掉
- 群聊作息对比改为卡片式布局
- 社交动机进度条加宽至16px
- 结语文案精简

### 🔧 Bug修复
- 社交节奏统计支持多种字段名

### 🎯 章节精简至17个

---

## 文件夹结构

```
项目目录/
├── A_report_generator.py       # 主程序（调用模块）
├── A_batch_analyzer.py         # 批量数据分析
├── A_enhanced_chat_analyzer.py # 单文件分析
├── A_styles.py                 # CSS样式模块 ⭐必需
├── A_scripts.py                # JS脚本模块 ⭐必需
├── README.md
├── CHANGELOG.md
├── PROJECT_INTRO.md
└── data/                       # 数据文件夹
    ├── xxx.json
    └── xxx.xlsx
```

## 使用方法

1. 创建 `data` 文件夹，将所有json和excel文件放入
2. 修改 `A_report_generator.py` 中的 `my_name = '你的昵称'`
3. 确保 `A_styles.py` 和 `A_scripts.py` 在同一目录
4. 运行 `python A_report_generator.py`
5. 在浏览器中打开生成的HTML文件
