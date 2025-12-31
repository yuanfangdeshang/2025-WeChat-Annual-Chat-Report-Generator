# -*- coding: utf-8 -*-
"""
enhanced_chat_analyzer.py - 增强版私聊分析器
包含所有指标：消息长度、语言风格、表情、时间、回复速度、内容丰富度、深度话题、会话结构、月度趋势
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict, Counter
from statistics import median, mean

# ==================== 配置 ====================
# 语气词分类
MODAL_WORDS = {
    '亲密/撒娇': ['嘛', '呀', '啦', '哒', '嘿嘿', '嘻嘻', '呐', '咯', '鸭', '呢'],
    '思考/犹豫': ['嗯', '唔', '额', '呃', 'emmm', 'emm', '嘶', 'hmm'],
    '确认/肯定': ['嗯嗯', '好的', '行', '可以', 'ok', 'OK', '好', '是的', '对', '好滴', '行的', '可', '好嘞'],
    '笑声': ['哈哈', '哈哈哈', '233', 'hhh', '笑死', '哈', 'hhhh', '2333', 'xswl', '笑'],
}

# 深度话题关键词
DEEP_TOPICS = {
    '情感/内心': ['开心', '难过', '伤心', '压力', '烦', '累', '想念', '喜欢', '爱', '感动', '焦虑', '孤独', '失落', '担心', '紧张', '害怕', '激动', '兴奋', '感觉', '心情', '情绪', '崩溃', '郁闷'],
    '家庭/亲人': ['爸', '妈', '家人', '家里', '哥', '姐', '弟', '妹', '父母', '奶奶', '爷爷', '外公', '外婆', '老爸', '老妈', '家', '回家'],
    '价值观/思考': ['觉得', '认为', '应该', '意义', '价值', '为什么', '怎么想', '看法', '观点', '思考', '理解', '道理'],
    '身体/健康': ['头疼', '感冒', '失眠', '健身', '生病', '休息', '累了', '困', '胃', '疼', '难受', '不舒服', '发烧', '体重', '睡眠', '熬夜', '身体'],
    '未来/规划': ['计划', '打算', '目标', '梦想', '未来', '工作', '努力', '考试', '面试', '毕业', '以后', '将来', '准备'],
    '回忆/过去': ['以前', '之前', '记得', '回忆', '曾经', '那时候', '小时候', '当时', '过去', '原来'],
}

# 词汇层次
VOCAB_LEVELS = {
    '正式/书面': ['因此', '然而', '但是', '所以', '并且', '虽然', '尽管', '由于', '关于', '针对', '基于', '鉴于', '综上', '总之', '首先', '其次', '最后', '此外', '另外', '而且'],
    '口语化': ['咋', '啥', '咱', '俺', '整', '搞', '弄', '干嘛', '咋整', '得了', '行吧', '算了', '随便', '无所谓', '管他', '爱咋咋', '凑合'],
    '网络流行语': ['yyds', '绝绝子', '无语子', '真的会谢', 'awsl', '笑死', 'xswl', '破防', '上头', '下头', '社死', '摆烂', 'duck不必', '蚌埠住', '芭比Q', '栓Q', '小丑竟是我', '绷不住', 'emo', '我裂开', '麻了', '蒜了', '红温', 'CPU', '确实', '6'],
}

def load_chat_json(filepath):
    """加载私聊JSON文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_chat_full(data, contact_name=None):
    """完整分析单个私聊，返回所有指标"""
    session = data.get('session', {})
    messages = data.get('messages', [])
    
    if not messages:
        return None
    
    if not contact_name:
        contact_name = session.get('remark') or session.get('nickname') or session.get('displayName', '联系人')
    
    # 解析消息
    parsed = []
    for m in messages:
        try:
            msg_type = m.get('type', '')
            content = m.get('content', '')
            time_str = m.get('formattedTime', '')
            is_send = m.get('isSend', 0) == 1
            
            if '系统消息' in msg_type:
                continue
            
            # 解析时间
            dt = None
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M:%S']:
                try:
                    dt = datetime.strptime(time_str, fmt)
                    break
                except:
                    continue
            if not dt:
                continue
            
            parsed.append({
                'time': dt,
                'type': msg_type,
                'content': content,
                'is_me': is_send,
            })
        except:
            continue
    
    if not parsed:
        return None
    
    parsed.sort(key=lambda x: x['time'])
    
    # ========== 分析各模块 ==========
    result = {'name': contact_name}
    
    # 1. 基础统计
    result.update(_calc_overview(parsed))
    
    # 2. 消息类型
    result.update(_calc_message_types(parsed))
    
    # 3. 消息长度
    result.update(_calc_message_length(parsed))
    
    # 4. 语言风格
    result.update(_calc_language_style(parsed))
    
    # 5. 表情统计
    result.update(_calc_emoji_stats(parsed))
    
    # 6. 时间分布
    result.update(_calc_time_pattern(parsed))
    
    # 7. 回复速度
    result.update(_calc_response_time(parsed))
    
    # 8. 内容丰富度
    result.update(_calc_content_richness(parsed))
    
    # 9. 深度话题
    result.update(_calc_deep_topics(parsed))
    
    # 10. 会话结构
    result.update(_calc_conversation_structure(parsed))
    
    # 11. 月度趋势
    result.update(_calc_monthly_trends(parsed))
    
    # 12. 关怀与邀约
    result.update(_calc_care_invite(parsed))
    
    # 13. 收集消息样本（用于开场动画）
    msg_samples = []
    for m in parsed:
        # 匹配'文本'或'文本消息'
        if ('文本' in m['type']) and m['content'] and len(m['content']) < 50:
            content = m['content'].strip()
            if content and not content.startswith('[') and not content.startswith('http'):
                msg_samples.append({
                    'text': content,
                    'is_me': m['is_me'],
                    'month': m['time'].strftime('%Y-%m'),
                })
    result['msg_samples'] = msg_samples[:100]  # 每个私聊最多保留100条样本
    
    return result


# ==================== 1. 基础统计 ====================
def _calc_overview(msgs):
    total = len(msgs)
    my_msgs = [m for m in msgs if m['is_me']]
    their_msgs = [m for m in msgs if not m['is_me']]
    
    dates = set(m['time'].strftime('%Y-%m-%d') for m in msgs)
    
    # 计算总字数
    my_chars = sum(len(m['content']) for m in my_msgs if '文本' in m['type'])
    their_chars = sum(len(m['content']) for m in their_msgs if '文本' in m['type'])
    
    return {
        'total_msgs': total,
        'my_msgs': len(my_msgs),
        'their_msgs': len(their_msgs),
        'my_pct': round(len(my_msgs) / total * 100, 1) if total else 0,
        'their_pct': round(len(their_msgs) / total * 100, 1) if total else 0,
        'total_chars': my_chars + their_chars,
        'my_chars': my_chars,
        'their_chars': their_chars,
        'days': len(dates),
        'date_range': (min(dates), max(dates)) if dates else ('', ''),
    }


# ==================== 2. 消息类型 ====================
def _calc_message_types(msgs):
    types_me = defaultdict(int)
    types_them = defaultdict(int)
    
    type_keywords = {
        '文本消息': ['文本'],
        '引用消息': ['引用'],
        '图片消息': ['图片'],
        '语音消息': ['语音'],
        '视频消息': ['视频'],
        '表情消息': ['表情', '动画'],
        '链接': ['链接', '分享'],
        '文件': ['文件'],
    }
    
    for m in msgs:
        target = types_me if m['is_me'] else types_them
        matched = False
        for type_name, keywords in type_keywords.items():
            if any(k in m['type'] for k in keywords):
                target[type_name] += 1
                matched = True
                break
        if not matched:
            target['其他'] += 1
    
    return {
        'msg_types_me': dict(types_me),
        'msg_types_them': dict(types_them),
        'quote_me': types_me.get('引用消息', 0),
        'quote_them': types_them.get('引用消息', 0),
        'quote_ratio': round(types_them.get('引用消息', 0) / max(types_me.get('引用消息', 1), 1), 2),
    }


# ==================== 3. 消息长度 ====================
def _calc_message_length(msgs):
    my_text = [m for m in msgs if m['is_me'] and '文本' in m['type']]
    their_text = [m for m in msgs if not m['is_me'] and '文本' in m['type']]
    
    my_lens = [len(m['content']) for m in my_text if m['content']]
    their_lens = [len(m['content']) for m in their_text if m['content']]
    
    def calc_stats(lens):
        if not lens:
            return {'total': 0, 'avg': 0, 'median': 0, 'max': 0}
        return {
            'total': sum(lens),
            'avg': round(mean(lens), 1),
            'median': int(median(lens)),
            'max': max(lens),
        }
    
    def calc_dist(lens):
        if not lens:
            return {'short': 0, 'medium': 0, 'long': 0}
        n = len(lens)
        return {
            'short': round(sum(1 for l in lens if l <= 10) / n * 100, 1),
            'medium': round(sum(1 for l in lens if 10 < l <= 30) / n * 100, 1),
            'long': round(sum(1 for l in lens if l > 50) / n * 100, 1),
        }
    
    return {
        'len_me': calc_stats(my_lens),
        'len_them': calc_stats(their_lens),
        'len_dist_me': calc_dist(my_lens),
        'len_dist_them': calc_dist(their_lens),
    }


# ==================== 4. 语言风格 ====================
def _calc_language_style(msgs):
    my_text = [m['content'] for m in msgs if m['is_me'] and '文本' in m['type']]
    their_text = [m['content'] for m in msgs if not m['is_me'] and '文本' in m['type']]
    
    def sentence_types(texts):
        q, e, s = 0, 0, 0
        for t in texts:
            if '?' in t or '？' in t or any(w in t for w in ['吗', '什么', '怎么', '哪', '谁', '为什么', '几']):
                q += 1
            elif '!' in t or '！' in t:
                e += 1
            else:
                s += 1
        total = q + e + s
        if total == 0:
            return {'question': 0, 'exclaim': 0, 'statement': 0}
        return {
            'question': round(q / total * 100, 1),
            'exclaim': round(e / total * 100, 1),
            'statement': round(s / total * 100, 1),
        }
    
    def modal_analysis(texts):
        result = {cat: 0 for cat in MODAL_WORDS}
        word_counts = Counter()
        for t in texts:
            t_lower = t.lower()
            for cat, words in MODAL_WORDS.items():
                for w in words:
                    cnt = t_lower.count(w.lower())
                    result[cat] += cnt
                    if cnt > 0:
                        word_counts[w] += cnt
        return result, word_counts.most_common(10)
    
    my_modal, my_top_modal = modal_analysis(my_text)
    their_modal, their_top_modal = modal_analysis(their_text)
    
    return {
        'sentence_me': sentence_types(my_text),
        'sentence_them': sentence_types(their_text),
        'modal_me': my_modal,
        'modal_them': their_modal,
        'top_modal_me': my_top_modal,
        'top_modal_them': their_top_modal,
    }


# ==================== 5. 表情统计 ====================
def _calc_emoji_stats(msgs):
    my_wechat = Counter()  # 微信表情 [xx]
    my_unicode = Counter()  # Unicode emoji
    their_wechat = Counter()
    their_unicode = Counter()
    
    # Unicode emoji 正则
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"
        "\u3030"
        "]+", flags=re.UNICODE
    )
    
    for m in msgs:
        content = m['content']
        wechat_target = my_wechat if m['is_me'] else their_wechat
        unicode_target = my_unicode if m['is_me'] else their_unicode
        
        # 微信表情
        wechat_emojis = re.findall(r'\[([^\]]+)\]', content)
        for e in wechat_emojis:
            wechat_target[f'[{e}]'] += 1
        
        # Unicode emoji
        unicode_emojis = emoji_pattern.findall(content)
        for e in unicode_emojis:
            unicode_target[e] += 1
    
    return {
        'emoji_me_total': sum(my_wechat.values()) + sum(my_unicode.values()),
        'emoji_them_total': sum(their_wechat.values()) + sum(their_unicode.values()),
        'wechat_emoji_me': sum(my_wechat.values()),
        'wechat_emoji_them': sum(their_wechat.values()),
        'unicode_emoji_me': sum(my_unicode.values()),
        'unicode_emoji_them': sum(their_unicode.values()),
        'top_emoji_me': (my_wechat + my_unicode).most_common(5),
        'top_emoji_them': (their_wechat + their_unicode).most_common(5),
    }


# ==================== 6. 时间分布 ====================
def _calc_time_pattern(msgs):
    hours = {h: 0 for h in range(24)}
    weekdays = {i: 0 for i in range(7)}
    daily = defaultdict(int)
    
    for m in msgs:
        hours[m['time'].hour] += 1
        weekdays[m['time'].weekday()] += 1
        daily[m['time'].strftime('%Y-%m-%d')] += 1
    
    # 找峰值
    peak_hour = max(hours.keys(), key=lambda h: hours[h])
    peak_weekday = max(weekdays.keys(), key=lambda w: weekdays[w])
    quiet_weekday = min(weekdays.keys(), key=lambda w: weekdays[w])
    
    weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    
    # 深夜消息 (23:00 - 4:00)
    late_night = sum(hours.get(h, 0) for h in [23, 0, 1, 2, 3, 4])
    
    return {
        'hours': hours,
        'weekdays': weekdays,
        'peak_hour': peak_hour,
        'peak_weekday': weekday_names[peak_weekday],
        'peak_weekday_count': weekdays[peak_weekday],
        'quiet_weekday': weekday_names[quiet_weekday],
        'quiet_weekday_count': weekdays[quiet_weekday],
        'late_night': late_night,
        'late_night_pct': round(late_night / len(msgs) * 100, 1) if msgs else 0,
    }


# ==================== 7. 回复速度 ====================
def _calc_response_time(msgs):
    my_reply = []
    their_reply = []
    
    # 分时段
    my_by_period = {'工作日白天': [], '工作日晚上': [], '周末白天': [], '周末晚上': []}
    their_by_period = {'工作日白天': [], '工作日晚上': [], '周末白天': [], '周末晚上': []}
    
    prev = None
    for m in msgs:
        if prev and prev['is_me'] != m['is_me']:
            diff = (m['time'] - prev['time']).total_seconds()
            if 0 < diff < 3600:  # 1小时内的回复才算
                hour = m['time'].hour
                weekday = m['time'].weekday()
                is_weekend = weekday >= 5
                is_night = hour >= 18 or hour < 6
                
                if is_weekend:
                    period = '周末晚上' if is_night else '周末白天'
                else:
                    period = '工作日晚上' if is_night else '工作日白天'
                
                if m['is_me']:
                    my_reply.append(diff)
                    my_by_period[period].append(diff)
                else:
                    their_reply.append(diff)
                    their_by_period[period].append(diff)
        prev = m
    
    def safe_median(lst):
        return int(median(lst)) if lst else 0
    
    def safe_mean(lst):
        return int(mean(lst)) if lst else 0
    
    return {
        'reply_me_median': safe_median(my_reply),
        'reply_them_median': safe_median(their_reply),
        'reply_me_avg': safe_mean(my_reply),
        'reply_them_avg': safe_mean(their_reply),
        'reply_me_by_period': {k: safe_median(v) for k, v in my_by_period.items()},
        'reply_them_by_period': {k: safe_median(v) for k, v in their_by_period.items()},
    }


# ==================== 8. 内容丰富度 ====================
def _calc_content_richness(msgs):
    my_text = [m['content'] for m in msgs if m['is_me'] and '文本' in m['type']]
    their_text = [m['content'] for m in msgs if not m['is_me'] and '文本' in m['type']]
    
    def analyze_richness(texts):
        if not texts:
            return {'unique_chars': 0, 'diversity': 0, 'english_pct': 0, 'english_words': 0}
        
        all_text = ''.join(texts)
        unique = len(set(all_text))
        diversity = round(unique / len(all_text) * 100, 2) if all_text else 0
        
        english_msgs = sum(1 for t in texts if re.search(r'[a-zA-Z]', t))
        english_pct = round(english_msgs / len(texts) * 100, 1)
        
        english_words = len(re.findall(r'[a-zA-Z]+', all_text))
        
        return {
            'unique_chars': unique,
            'diversity': diversity,
            'english_pct': english_pct,
            'english_words': english_words,
        }
    
    def analyze_vocab(texts):
        result = {cat: 0 for cat in VOCAB_LEVELS}
        all_text = ' '.join(texts).lower()
        for cat, words in VOCAB_LEVELS.items():
            for w in words:
                result[cat] += all_text.count(w.lower())
        return result
    
    return {
        'richness_me': analyze_richness(my_text),
        'richness_them': analyze_richness(their_text),
        'vocab_me': analyze_vocab(my_text),
        'vocab_them': analyze_vocab(their_text),
    }


# ==================== 9. 深度话题 ====================
def _calc_deep_topics(msgs):
    my_topics = {t: 0 for t in DEEP_TOPICS}
    their_topics = {t: 0 for t in DEEP_TOPICS}
    
    for m in msgs:
        if '文本' not in m['type']:
            continue
        content = m['content'].lower()
        target = my_topics if m['is_me'] else their_topics
        
        for topic, keywords in DEEP_TOPICS.items():
            if any(k in content for k in keywords):
                target[topic] += 1
    
    return {
        'topics_me': my_topics,
        'topics_them': their_topics,
    }


# ==================== 10. 会话结构 ====================
def _calc_conversation_structure(msgs):
    if not msgs:
        return {'sessions': 0, 'my_init': 0, 'their_init': 0}
    
    sessions = []
    current_session = [msgs[0]]
    
    for i in range(1, len(msgs)):
        diff = (msgs[i]['time'] - msgs[i-1]['time']).total_seconds()
        if diff > 1800:  # 30分钟算新会话
            sessions.append(current_session)
            current_session = [msgs[i]]
        else:
            current_session.append(msgs[i])
    
    if current_session:
        sessions.append(current_session)
    
    my_init = sum(1 for s in sessions if s[0]['is_me'])
    their_init = len(sessions) - my_init
    
    session_lens = [len(s) for s in sessions]
    
    return {
        'sessions': len(sessions),
        'my_init': my_init,
        'their_init': their_init,
        'my_init_pct': round(my_init / len(sessions) * 100, 1) if sessions else 0,
        'their_init_pct': round(their_init / len(sessions) * 100, 1) if sessions else 0,
        'avg_session_len': round(mean(session_lens), 1) if session_lens else 0,
        'max_session_len': max(session_lens) if session_lens else 0,
    }


# ==================== 11. 月度趋势 ====================
def _calc_monthly_trends(msgs):
    months_me = defaultdict(int)
    months_them = defaultdict(int)
    daily_counts = defaultdict(int)
    
    for m in msgs:
        key = m['time'].strftime('%Y-%m')
        day_key = m['time'].strftime('%Y-%m-%d')
        daily_counts[day_key] += 1
        if m['is_me']:
            months_me[key] += 1
        else:
            months_them[key] += 1
    
    all_months = sorted(set(months_me.keys()) | set(months_them.keys()))
    
    return {
        'monthly': {
            month: {
                'me': months_me.get(month, 0),
                'them': months_them.get(month, 0),
                'total': months_me.get(month, 0) + months_them.get(month, 0)
            }
            for month in all_months
        },
        'daily': dict(daily_counts)
    }


# ==================== 12. 关怀与邀约 ====================
def _calc_care_invite(msgs):
    care_words = ['好点了', '怎么样了', '还好吗', '注意', '照顾', '保重', '休息', '早点睡', '别太累', '加油', '辛苦', '小心', '多喝水', '好好吃饭', '注意身体', '早睡']
    invite_words = ['一起', '要不要', '去不去', '来不来', '走不走', '约', '出来', '见面', '吃饭', '聚']
    
    my_care, their_care = 0, 0
    my_invite, their_invite = 0, 0
    
    for m in msgs:
        c = m['content']
        if any(w in c for w in care_words):
            if m['is_me']:
                my_care += 1
            else:
                their_care += 1
        if any(w in c for w in invite_words):
            if m['is_me']:
                my_invite += 1
            else:
                their_invite += 1
    
    return {
        'care_me': my_care,
        'care_them': their_care,
        'invite_me': my_invite,
        'invite_them': their_invite,
    }


# ==================== 测试 ====================
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python A_enhanced_chat_analyzer.py <json文件路径>")
        print("示例: python A_enhanced_chat_analyzer.py data/张三_123456.json")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not os.path.exists(filepath):
        print(f"⚠️  文件不存在: {filepath}")
        sys.exit(1)
    
    print(f"📂 加载: {filepath}")
    data = load_chat_json(filepath)
    result = analyze_chat_full(data)
    
    if result:
        print(f"\n{'='*60}")
        print(f"📊 完整分析: {result['name']}")
        print(f"{'='*60}")
        
        print(f"\n【1. 基础统计】")
        print(f"  总消息: {result['total_msgs']} | 总字数: {result['total_chars']}")
        print(f"  我: {result['my_msgs']} ({result['my_pct']}%) | Ta: {result['their_msgs']} ({result['their_pct']}%)")
        print(f"  聊天天数: {result['days']} | 时间: {result['date_range'][0]} ~ {result['date_range'][1]}")
        
        print(f"\n【2. 消息类型】")
        print(f"  我: {result['msg_types_me']}")
        print(f"  Ta: {result['msg_types_them']}")
        print(f"  引用比(Ta/我): {result['quote_ratio']}")
        
        print(f"\n【3. 消息长度】")
        print(f"  我: 平均{result['len_me']['avg']}字 | 中位{result['len_me']['median']}字 | 最长{result['len_me']['max']}字")
        print(f"  Ta: 平均{result['len_them']['avg']}字 | 中位{result['len_them']['median']}字 | 最长{result['len_them']['max']}字")
        print(f"  分布(我): 短{result['len_dist_me']['short']}% | 中{result['len_dist_me']['medium']}% | 长{result['len_dist_me']['long']}%")
        
        print(f"\n【4. 语言风格】")
        print(f"  句式(我): 疑问{result['sentence_me']['question']}% | 感叹{result['sentence_me']['exclaim']}% | 陈述{result['sentence_me']['statement']}%")
        print(f"  句式(Ta): 疑问{result['sentence_them']['question']}% | 感叹{result['sentence_them']['exclaim']}% | 陈述{result['sentence_them']['statement']}%")
        print(f"  语气词(我): {result['modal_me']}")
        print(f"  语气词(Ta): {result['modal_them']}")
        
        print(f"\n【5. 表情统计】")
        print(f"  我: {result['emoji_me_total']} (微信{result['wechat_emoji_me']} + Unicode{result['unicode_emoji_me']})")
        print(f"  Ta: {result['emoji_them_total']} (微信{result['wechat_emoji_them']} + Unicode{result['unicode_emoji_them']})")
        print(f"  我的Top: {result['top_emoji_me'][:3]}")
        print(f"  Ta的Top: {result['top_emoji_them'][:3]}")
        
        print(f"\n【6. 时间分布】")
        print(f"  峰值时段: {result['peak_hour']}:00")
        print(f"  最活跃: {result['peak_weekday']} ({result['peak_weekday_count']}条)")
        print(f"  最安静: {result['quiet_weekday']} ({result['quiet_weekday_count']}条)")
        print(f"  深夜消息: {result['late_night']}条 ({result['late_night_pct']}%)")
        
        print(f"\n【7. 回复速度】")
        print(f"  我回复Ta: 中位{result['reply_me_median']}秒 | 平均{result['reply_me_avg']}秒")
        print(f"  Ta回复我: 中位{result['reply_them_median']}秒 | 平均{result['reply_them_avg']}秒")
        print(f"  分时段(Ta): {result['reply_them_by_period']}")
        
        print(f"\n【8. 内容丰富度】")
        print(f"  我: 字符{result['richness_me']['unique_chars']} | 多样性{result['richness_me']['diversity']}% | 英文{result['richness_me']['english_pct']}%")
        print(f"  Ta: 字符{result['richness_them']['unique_chars']} | 多样性{result['richness_them']['diversity']}% | 英文{result['richness_them']['english_pct']}%")
        print(f"  词汇(我): {result['vocab_me']}")
        print(f"  词汇(Ta): {result['vocab_them']}")
        
        print(f"\n【9. 深度话题】")
        print(f"  我: {result['topics_me']}")
        print(f"  Ta: {result['topics_them']}")
        
        print(f"\n【10. 会话结构】")
        print(f"  总会话: {result['sessions']}次")
        print(f"  我发起: {result['my_init']} ({result['my_init_pct']}%) | Ta发起: {result['their_init']} ({result['their_init_pct']}%)")
        print(f"  平均长度: {result['avg_session_len']}条 | 最长: {result['max_session_len']}条")
        
        print(f"\n【11. 月度趋势】")
        for month, data in result['monthly'].items():
            print(f"  {month}: 我{data['me']} + Ta{data['them']} = {data['total']}")
        
        print(f"\n【12. 关怀统计】")
        print(f"  我关心Ta: {result['care_me']}次 | Ta关心我: {result['care_them']}次")
        print(f"  我邀约Ta: {result['invite_me']}次 | Ta邀约我: {result['invite_them']}次")
