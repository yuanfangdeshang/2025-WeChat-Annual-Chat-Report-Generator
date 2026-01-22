# 微信年度聊天报告生成器 - 项目深度解析

> 本文档为 Claude AI 编写，用于深度理解项目架构、数据流、算法逻辑和代码依赖关系。
> 基于实际生成的HTML文件和源代码分析。

---

## 📁 项目结构概览

```
wechat-annual-report/
├── A_report_generator.py        # 主程序：HTML报告生成器 (5909行)
├── A_batch_analyzer.py          # 批量数据分析器 (1206行)
├── A_enhanced_chat_analyzer.py  # 单文件深度分析器 (708行)
├── A_styles.py                  # CSS样式模块 (必需，提供get_css_styles())
├── A_scripts.py                 # JavaScript脚本模块 (必需，提供get_js_scripts())
├── data/                        # 数据目录
│   ├── *.json                   # 私聊/群聊JSON文件
│   └── *.xlsx                   # 群聊Excel文件
└── bgm.mp3                      # 背景音乐 (可选)
```

---

## 🔄 数据流与模块依赖

```
┌─────────────────────────────────────────────────────────────────┐
│                    A_report_generator.py                        │
│                       (主程序入口)                               │
│                                                                 │
│  导入: from A_batch_analyzer import batch_analyze               │
│        from A_styles import get_css_styles                      │
│        from A_scripts import get_js_scripts                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │         batch_analyze(data_dir)          │
        │         (A_batch_analyzer.py)            │
        │                                          │
        │  导入: from A_enhanced_chat_analyzer     │
        │        import load_chat_json,            │
        │               analyze_chat_full          │
        └─────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ 私聊JSON    │    │ 群聊JSON    │    │ 群聊Excel   │
   │  分析       │    │  分析       │    │  分析       │
   └─────────────┘    └─────────────┘    └─────────────┘
          │
          ▼
   ┌─────────────────────────────────┐
   │    analyze_chat_full(data)      │
   │  (A_enhanced_chat_analyzer.py)  │
   │                                 │
   │  ⚠️ 分析全量数据，不过滤年份     │
   │                                 │
   │  返回12个维度的分析数据:         │
   │  - 基础统计 (total_msgs等)      │
   │  - 消息类型                     │
   │  - 消息长度                     │
   │  - 语言风格                     │
   │  - 表情统计                     │
   │  - 时间分布                     │
   │  - 回复速度                     │
   │  - 内容丰富度                   │
   │  - 深度话题                     │
   │  - 会话结构                     │
   │  - 月度趋势 (monthly字典)       │
   │  - 关怀与邀约                   │
   └─────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │        generate_final_report()          │
        │        (A_report_generator.py)          │
        │                                         │
        │  ⚠️ 部分指标在这里才过滤2025年数据      │
        │                                         │
        │  调用: get_css_styles() (第5456行)      │
        │        get_js_scripts() (第5803行)      │
        │  生成: 单文件HTML报告                    │
        └─────────────────────────────────────────┘
```

---

## ✅ 已修复的问题 (本次更新)

### 1. 数据清洗 - 年份过滤 ✅

**修复内容:**
- `A_enhanced_chat_analyzer.py` 的 `analyze_chat_full()` 新增 `year_filter='2025'` 参数
- `A_batch_analyzer.py` 的 `analyze_group_json()` 新增 `year_filter='2025'` 参数
- `batch_analyze()` 函数新增 `year_filter='2025'` 参数并向下传递

**修复逻辑:**
```python
# 解析消息时同时维护两个列表
parsed = []      # 过滤后的数据（用于所有指标计算）
parsed_all = []  # 全量数据（仅用于月度趋势，便于历史对比）

# 年份过滤
if year_filter is None or dt.strftime('%Y') == str(year_filter):
    parsed.append(msg_data)
```

**影响范围:**
- 所有基础指标（total_msgs, sessions, days, late_night等）现在只统计指定年份
- 月度趋势仍保留全量数据，便于后续添加历史对比功能

### 2. 深夜消息定义统一 ✅

**修复前:** 私聊23-4点(6小时) vs 群聊0-6点(7小时)

**修复后:** 统一为 `[23, 0, 1, 2, 3, 4, 5]` 即 23:00-5:59 (7小时)

### 3. 用户昵称识别 - 说明

**这不是Bug:** `isSend=1` 表示**导出者**发的消息，逻辑是正确的。

如果用"远方的熵"的微信号导出，那么：
- `isSend=1` 的消息 = 远方的熵发的 = `is_me=True`
- `isSend=0` 的消息 = 对方发的 = `is_me=False`

如果用**别人的**微信号导出给你分析，那 `isSend=1` 代表的是那个人发的，不是你。这是数据源的问题，不是代码问题。

---

### 输入数据格式

#### 1. 私聊JSON (由微信导出工具生成)

```json
{
  "session": {
    "wxid": "wxid_xxx",           // 微信ID
    "nickname": "好友昵称",        // 原始昵称
    "remark": "备注名",           // 我给Ta的备注
    "displayName": "显示名",      // 最终显示名
    "type": "私聊",               // 固定为"私聊"
    "messageCount": 1234          // 消息总数
  },
  "messages": [
    {
      "localId": 1,
      "createTime": 1745667905,            // Unix时间戳
      "formattedTime": "2025-04-26 19:45:05", // 格式化时间
      "type": "文本消息",                   // 消息类型
      "localType": 1,                       // 本地类型码
      "content": "消息内容",
      "isSend": 0,                          // 0=对方发送, 1=我发送
      "senderUsername": "wxid_xxx",
      "senderDisplayName": "发送者名称"
    }
  ]
}
```

#### 2. 群聊JSON

```json
{
  "session": {
    "wxid": "xxx@chatroom",       // 群ID
    "nickname": "群名称",
    "type": "群聊",
    "messageCount": 456
  },
  "messages": [
    {
      "formattedTime": "2025-04-26 19:45:05",
      "type": "文本消息",
      "content": "消息内容",
      "isSend": 1,                 // 是否是我发的
      "senderDisplayName": "群成员名" // 发送者名称
    }
  ]
}
```

#### 3. 群聊Excel格式

| 时间 | 发送者昵称 | 消息类型 | 内容 |
|------|-----------|---------|------|
| 2025-04-26 19:45:05 | 张三 | 文本消息 | 今天吃什么 |

---

## 🧮 核心算法详解

### 1. 好友默契度评分 (满分100分)

```python
# 位置: A_report_generator.py 内部函数

def calculate_chemistry_score(chat):
    """五维评分系统"""
    
    # 维度1: 消息平衡度 (20分)
    # 双方消息数越接近，得分越高
    balance = min(their_msgs, my_msgs) / max(their_msgs, my_msgs)
    balance_score = balance * 20
    
    # 维度2: 回复速度匹配度 (20分)
    # 双方回复时间越接近，得分越高
    reply_match = min(their_reply, my_reply) / max(their_reply, my_reply)
    reply_score = reply_match * 20
    
    # 维度3: 会话频率 (20分)
    # 日均会话数越高，得分越高 (上限20分)
    session_score = min(20, daily_sessions * 10)
    
    # 维度4: 深夜陪伴 (20分)
    # 深夜消息数越多，得分越高 (上限20分)
    late_score = min(20, late_night_msgs / 5)
    
    # 维度5: 关心互动 (20分)
    # 双方关心次数的平均值 (上限20分)
    care_score = min(20, (care_them + care_me) / 2)
    
    total = balance_score + reply_score + session_score + late_score + care_score
    return total  # 0-100分
```

**等级划分:**
| 分数区间 | 等级 | 描述 |
|---------|------|------|
| 85-100 | 💎 灵魂伴侣 | 有些人，不用解释，你就懂 |
| 70-84 | 🌟 超级默契 | 聊天像在同一频道上 |
| 55-69 | 💛 心有灵犀 | 一句话就能接得住 |
| 40-54 | 🤝 默契好友 | 聊得开心、聊得自在 |
| 0-39 | 🌱 默契萌芽 | 也许一句"在吗"就是开始 |

### 2. 社交人格四维分析

```python
# 位置: A_report_generator.py - analyze_social_personality()

def analyze_social_personality():
    """四维人格分析"""
    
    # 维度1: 主动指数 (0-100%)
    # 我发起会话数 / 总会话数
    initiative_score = my_init / (my_init + their_init) * 100
    
    # 维度2: 夜猫指数 (0-100%)
    # 深夜消息总数 / 200 (上限100%)
    night_score = min(100, total_late_night / 200 * 100)
    
    # 维度3: 社交广度 (0-100%)
    # 活跃好友数 / 20 (上限100%)
    breadth_score = min(100, active_friends / 20 * 100)
    
    # 维度4: 表达深度 (0-100%)
    # 平均消息长度 / 50 (上限100%)
    length_score = min(100, avg_msg_length / 50 * 100)
```

**人格类型判定逻辑:**
```python
if initiative > 60% and breadth > 50%:
    return "🦋 社交蝴蝶"  # 主动热情，朋友遍天下
elif initiative < 40% and breadth < 50%:
    return "🦪 深海珍珠"  # 不轻易敞开，但交心是一辈子
elif night > 50% and length > 50%:
    return "✒️ 深夜作家"  # 夜深人静时长文倾诉
elif night > 50%:
    return "🌙 月光倾听者"  # 深夜最好的树洞
elif initiative > 60%:
    return "☀️ 温暖发起人"  # 总是先说"在吗"的人
elif breadth > 60%:
    return "🎆 人间烟火"  # 世界热闹而精彩
else:
    return "💧 细水长流"  # 友情不急不缓
```

### 3. 社交健康度算法

```python
# 位置: A_report_generator.py

def calc_social_health():
    """五维健康度评分"""
    
    # 广度分 (15%权重)
    breadth = min(100, active_contacts * 2)
    
    # 深度分 (25%权重) - 深度好友定义为消息>=500条
    depth = min(100, deep_friends * 10)
    
    # 平衡分 (20%权重)
    balance = min(sent, received) / max(sent, received) * 100
    
    # 关怀分 (20%权重)
    care = min(100, total_care / 2)
    
    # 持续分 (20%权重)
    # 长期好友(>6个月)*3 + 超长期好友(>12个月)*5
    persist = min(100, long_term*3 + ultra_long_term*5)
    
    total = breadth*0.15 + depth*0.25 + balance*0.20 + care*0.20 + persist*0.20
```

### 4. 群聊活力指数算法

```python
# 位置: A_report_generator.py - make_group_cards()

def calc_vitality_score(group):
    """群聊活力综合评分"""
    
    vitality = 0
    vitality += min(30, avg_daily * 0.5)      # 日均消息 (最多30分)
    vitality += min(25, member_count * 0.3)   # 成员规模 (最多25分)
    vitality += min(25, active_days / 12)     # 活跃天数 (最多25分)
    vitality += min(20, active_members * 4)   # 活跃人数 (最多20分)
    
    return min(100, int(vitality))
```

### 5. 会话结构分析

```python
# 位置: A_enhanced_chat_analyzer.py - _calc_conversation_structure()

def _calc_conversation_structure(msgs):
    """会话切分与分析"""
    
    sessions = []
    current_session = [msgs[0]]
    
    for i in range(1, len(msgs)):
        # 30分钟(1800秒)无消息 = 新会话
        diff = (msgs[i]['time'] - msgs[i-1]['time']).total_seconds()
        if diff > 1800:
            sessions.append(current_session)
            current_session = [msgs[i]]
        else:
            current_session.append(msgs[i])
    
    # 统计会话发起者
    my_init = sum(1 for s in sessions if s[0]['is_me'])
    their_init = len(sessions) - my_init
    
    return {
        'sessions': len(sessions),
        'my_init': my_init,
        'their_init': their_init,
        'avg_session_len': mean([len(s) for s in sessions]),
        'max_session_len': max([len(s) for s in sessions])
    }
```

---

## 🔧 关键函数索引

### A_report_generator.py (主程序)

| 函数名 | 行号 | 功能 |
|-------|------|------|
| `mask_name()` | 28-52 | 姓名脱敏处理 |
| `generate_poetic_name()` | 63-71 | 生成有意境的文件名 |
| `fmt_time()` | 74-82 | 秒数转可读时间 |
| `generate_final_report()` | 85-5813 | **核心函数：生成HTML报告** |
| ├─ `display_name()` | 104-105 | 脱敏姓名显示 |
| ├─ `generate_story_intro()` | 157-203 | 生成故事开场 |
| ├─ `prepare_intro_animation_data()` | 206-322 | 开场动画数据 |
| ├─ `generate_insights()` | 325-383 | 智能洞察文案 |
| ├─ `generate_annual_titles()` | 386-441 | 年度称号系统 |
| ├─ `analyze_social_personality()` | 444-516 | 社交人格分析 |
| ├─ `generate_special_moments()` | 519-609 | 特殊时刻生成 |
| ├─ `make_annual_titles_card()` | 612-630 | 称号卡片HTML |
| ├─ `make_personality_card()` | 633-677 | 人格卡片HTML |
| ├─ `make_friend_trends()` | 702-817 | 好友趋势图 |
| ├─ `make_private_rankings()` | 818-947 | 私聊排行榜 |
| ├─ `generate_group_insights()` | 950-1008 | 群聊洞察 |
| ├─ `make_group_overview()` | 1011-1134 | 群聊总览 |
| ├─ `make_group_time_comparison()` | 1137-1218 | 群聊时段对比 |
| ├─ `make_group_rankings()` | 1221-1322 | 群聊排行榜 |
| ├─ `make_private_cards()` | 1325-1636 | 私聊详情卡片 |
| ├─ `make_group_cards()` | 1637-1943 | 群聊详情卡片 |
| ├─ `make_friend_groups()` | 1946-1974 | 好友分组 |
| ├─ `make_section_summary()` | 1978-2001 | 小节总结文案 |
| ├─ `make_year_journey()` | 2004-2111 | 年度旅程时间线 |
| ├─ `make_hourly_rhythm()` | 2177-2345 | 24小时社交节奏 |
| ├─ `make_friend_honors()` | 2350-2500 | 好友荣誉榜 |
| ├─ `make_user_profile_card()` | ~2600 | 用户画像卡片 |
| ├─ `make_energy_wave()` | ~2700 | 能量波动图 |
| ├─ `make_share_card()` | ~3000 | 分享卡片 |
| └─ `make_ending_section()` | ~3200 | 结语页面 |

### A_batch_analyzer.py (批量分析器)

| 函数名 | 行号 | 功能 |
|-------|------|------|
| `load_group_excel()` | 23-54 | 加载群聊Excel |
| `analyze_group()` | 57-174 | 分析群聊Excel数据 |
| `analyze_group_json()` | 177-317 | 分析群聊JSON数据 |
| `analyze_private_excel()` | 320-700 | 分析私聊Excel数据 |
| `batch_analyze()` | 780-956 | **核心函数：批量分析** |
| `generate_summary()` | 959-1139 | 生成汇总统计 |
| `save_results()` | 1142-1154 | 保存结果到JSON |

### A_enhanced_chat_analyzer.py (单文件分析器)

| 函数名 | 行号 | 功能 |
|-------|------|------|
| `load_chat_json()` | 74-77 | 加载私聊JSON |
| `analyze_chat_full()` | 80-181 | **核心函数：完整分析** |
| `_calc_overview()` | 185-207 | 基础统计 |
| `_calc_message_types()` | 211-240 | 消息类型分析 |
| `_calc_message_length()` | 244-290 | 消息长度分析 |
| `_calc_language_style()` | 294-370 | 语言风格分析 |
| `_calc_emoji_stats()` | 374-430 | 表情统计 |
| `_calc_time_pattern()` | 434-470 | 时间分布分析 |
| `_calc_response_time()` | 474-530 | 回复速度分析 |
| `_calc_content_richness()` | 534-506 | 内容丰富度分析 |
| `_calc_deep_topics()` | 510-527 | 深度话题分析 |
| `_calc_conversation_structure()` | 531-562 | 会话结构分析 |
| `_calc_monthly_trends()` | 566-592 | 月度趋势分析 |
| `_calc_care_invite()` | 596-621 | 关怀邀约分析 |

---

## ⚠️ 重要设计决策

### 1. 排名数据只使用前100名好友

```python
# A_report_generator.py 第141行
top_100_private = sorted_private[:100]

# 原因：
# - 避免"点头之交"(消息<30条)影响排名公平性
# - 提高排名的统计意义
# - 保护隐私（不展示所有好友）
```

### 2. 2025年数据优先

```python
# 计算2025年消息数的辅助函数
def get_2025_msgs(chat):
    monthly = chat.get('monthly', {})
    return sum(v.get('total', 0) for k, v in monthly.items() if k.startswith('2025'))

# 原因：年度报告应聚焦当年数据
```

### 3. 回复速度字段兼容

```python
# 支持多种字段名获取回复速度
def get_reply_time(c):
    return (c.get('reply_them_median') or 
            c.get('reply_them_avg') or 
            c.get('their_reply_time') or 
            c.get('reply_speed_them') or 0)

# 原因：不同版本的数据导出工具字段名可能不同
```

### 4. 深夜消息定义

```python
# A_enhanced_chat_analyzer.py
late_night = sum(hours.get(h, 0) for h in [23, 0, 1, 2, 3, 4])

# A_batch_analyzer.py (群聊)
late_night = sum(hours[h] for h in range(0, 7))  # 0-6点

# 注意：两个文件定义略有不同
# 私聊: 23:00-4:59 (6小时)
# 群聊: 0:00-6:59 (7小时)
```

### 5. 会话切分阈值

```python
# 30分钟(1800秒)无消息 = 新会话
if diff > 1800:
    sessions.append(current_session)
    current_session = [msgs[i]]
```

---

## 🎨 HTML报告实际结构（基于生成的HTML）

```html
<!DOCTYPE html>
<html>
<head>
    <title>XXX的2025微信年度报告</title>
    <style>
        /* 来自 A_styles.py - get_css_styles() */
    </style>
</head>
<body>
    <!-- 背景层 -->
    <div id="particles"></div>
    <div id="stars"></div>
    <div id="flowingLines"></div>
    <div id="glowOrbs"></div>
    <div id="meteors"></div>
    
    <!-- 导航 + 音乐控制 + 截图按钮 -->
    
    <!-- ===== 实际章节 (19个) ===== -->
    
    <section id="hero">开场页 - 沉浸式动画</section>
    
    <section id="annual-letter">
        💌 年度来信 - 个性化信件
    </section>
    
    <section id="chemistry">
        💫 好友默契度 - 五维评分系统
    </section>
    
    <section id="friend-trends">
        📈 好友互动趋势 - Top5好友月度折线图
    </section>
    
    <section id="private-rank">
        🏆 私聊排行榜 - 17个维度排名
    </section>
    
    <section id="private-detail">
        💬 私聊详情 - 可展开的好友卡片
    </section>
    
    <section id="group-overview">
        🌐 你的群聊宇宙 - 群聊类型分布+角色分析
    </section>
    
    <section id="group-rank">
        👥 群聊排行榜 - 7个维度排名
    </section>
    
    <section id="group-detail">
        📋 群聊详情 - 可展开的群聊卡片
    </section>
    
    <section id="chat-colors">
        🎨 年度聊天色彩 - 五维情感色彩分析
    </section>
    
    <section id="festival">
        🎉 节日聊天图鉴 - 节日消息统计
    </section>
    
    <section id="motivation">
        🎯 你的社交动机 - 雷达图分析
    </section>
    
    <section id="emoji-analysis">
        😊 你的表情气质 - Top表情统计
    </section>
    
    <section id="rhythm">
        🕐 你的社交节奏 - 24小时热力图
    </section>
    
    <section id="energy">
        📈 你的社交能量 - 52周能量波动
    </section>
    
    <section id="user-profile">
        🔮 猜猜你是谁 - 用户画像预测
    </section>
    
    <section id="honors">
        🏅 年度好友荣誉榜 - 特殊称号颁发
    </section>
    
    <section id="numbers">
        🔢 你的年度数字 - 大数字展示
    </section>
    
    <section id="ending">
        结语 + 分享功能
    </section>
    
    <footer>页脚信息</footer>
    
    <script>
        /* 来自 A_scripts.py - get_js_scripts() */
    </script>
</body>
</html>
```

**注意**: 之前概述中提到的"12个月热力图(heatmap)"、"年度旅程时间线(journey)"、"社交健康度(health)"在实际HTML中**不存在**或已被其他模块替代。

---

## 🐛 待修复项

### 🟡 九宫格功能需要优化

当前问题：
- 设计风格不够精致
- 热力图数据是随机的（第7张图）
- 部分数据获取可能失败

建议：
- 重新设计九宫格模板，使用更统一的视觉风格
- 数据从报告中实际提取，而非硬编码或随机

### 🟢 后续功能

1. **历史对比功能**: 支持与前几年数据对比（月度趋势数据已保留全量）

2. **九宫格重设计**: 根据实际需求重新设计模板

---

*文档版本: v1.0*
*生成时间: 2025-01-22*
*作者: Claude AI*
