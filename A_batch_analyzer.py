# -*- coding: utf-8 -*-
"""
batch_analyzer.py - 批量分析器
处理目录下所有私聊JSON和群聊Excel，生成汇总数据
"""

import os
import json
from datetime import datetime
from collections import defaultdict
from statistics import median, mean, stdev

from A_enhanced_chat_analyzer import load_chat_json, analyze_chat_full

# 尝试导入pandas用于群聊分析
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def load_group_excel(filepath):
    """加载群聊Excel文件"""
    if not HAS_PANDAS:
        raise ImportError("需要安装 pandas: pip install pandas openpyxl")
    
    df = pd.read_excel(filepath, header=None)
    
    # 查找表头行
    header_row = None
    for i in range(min(10, len(df))):
        row_values = df.iloc[i].astype(str).tolist()
        if '时间' in row_values and '内容' in row_values:
            header_row = i
            break
    
    if header_row is None:
        raise ValueError("无法找到表头行")
    
    df = pd.read_excel(filepath, header=header_row)
    
    # 获取群名
    df_meta = pd.read_excel(filepath, header=None, nrows=header_row)
    group_name = "群聊"
    for i in range(len(df_meta)):
        row = df_meta.iloc[i].astype(str).tolist()
        if '昵称' in row:
            idx = row.index('昵称')
            if idx + 1 < len(row) and row[idx + 1] != 'nan':
                group_name = row[idx + 1]
                break
    
    return df, group_name


def analyze_group(df, group_name, my_name=None):
    """分析群聊数据"""
    messages = []
    
    for _, row in df.iterrows():
        try:
            time_val = row.get('时间', '')
            sender = str(row.get('发送者昵称', '') or row.get('发送者备注', ''))
            msg_type = str(row.get('消息类型', ''))
            content = str(row.get('内容', ''))
            
            if pd.isna(time_val) or not sender or sender == 'nan':
                continue
            
            # 解析时间
            dt = None
            if isinstance(time_val, datetime):
                dt = time_val
            else:
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M:%S']:
                    try:
                        dt = datetime.strptime(str(time_val), fmt)
                        break
                    except:
                        continue
            
            if not dt:
                continue
            
            if '系统消息' in msg_type:
                continue
            
            messages.append({
                'time': dt,
                'sender': sender.strip(),
                'type': msg_type,
                'content': content,
            })
        except:
            continue
    
    if not messages:
        return None
    
    messages.sort(key=lambda x: x['time'])
    
    # 基础统计
    total = len(messages)
    members = set(m['sender'] for m in messages)
    member_count = len(members)
    dates = set(m['time'].strftime('%Y-%m-%d') for m in messages)
    days = len(dates)
    date_range = (min(dates), max(dates)) if dates else ('', '')
    
    # 成员发言统计
    member_msgs = defaultdict(int)
    member_chars = defaultdict(int)
    for m in messages:
        member_msgs[m['sender']] += 1
        if '文本' in m['type']:
            member_chars[m['sender']] += len(m['content'])
    
    top_talkers = sorted(member_msgs.items(), key=lambda x: -x[1])[:10]
    
    # 时间分布
    hours = {h: 0 for h in range(24)}
    weekdays = {i: 0 for i in range(7)}
    for m in messages:
        hours[m['time'].hour] += 1
        weekdays[m['time'].weekday()] += 1
    
    peak_hour = max(hours.keys(), key=lambda h: hours[h])
    late_night = sum(hours.get(h, 0) for h in [23, 0, 1, 2, 3, 4, 5])
    
    # 统计"我"的消息数
    my_msgs = 0
    my_sender_name = None
    
    if my_name:
        for sender, count in member_msgs.items():
            # 模糊匹配
            clean_sender = ''.join(c for c in sender if c.isalnum() or '\u4e00' <= c <= '\u9fff')
            clean_my = ''.join(c for c in my_name if c.isalnum() or '\u4e00' <= c <= '\u9fff')
            if clean_sender and clean_my and (clean_my in clean_sender or clean_sender in clean_my):
                my_msgs = count
                my_sender_name = sender
                break
    
    my_pct = round(my_msgs / total * 100, 1) if total else 0
    
    # 我在群里的排名
    my_rank = 0
    if my_msgs > 0:
        sorted_members = sorted(member_msgs.items(), key=lambda x: -x[1])
        for i, (name, count) in enumerate(sorted_members, 1):
            if count == my_msgs or name == my_sender_name:
                my_rank = i
                break
    
    return {
        'name': group_name,
        'total_msgs': total,
        'member_count': member_count,
        'days': days,
        'date_range': date_range,
        'avg_daily': round(total / max(days, 1), 1),
        'top_talkers': top_talkers,
        'member_msgs': dict(member_msgs),
        'hours': hours,
        'weekdays': weekdays,
        'peak_hour': peak_hour,
        'late_night': late_night,
        'late_night_pct': round(late_night / total * 100, 1) if total else 0,
        'my_msgs': my_msgs,
        'my_pct': my_pct,
        'my_rank': my_rank,
        'my_sender_name': my_sender_name,
    }


def analyze_group_json(filepath, my_name=None, year_filter='2025'):
    """分析群聊JSON文件
    
    Args:
        filepath: JSON文件路径
        my_name: 我的昵称
        year_filter: 年份过滤，默认'2025'，设为None则不过滤
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    session = data.get('session', {})
    messages = data.get('messages', [])
    
    group_name = session.get('displayName', '') or session.get('nickname', '') or '群聊'
    
    if not messages:
        return None
    
    # 解析消息
    parsed = []
    parsed_all = []  # 全量数据用于月度趋势
    for m in messages:
        try:
            msg_type = m.get('type', '')
            if '系统消息' in msg_type:
                continue
            
            time_val = m.get('formattedTime', '') or m.get('createTime', 0)
            if isinstance(time_val, int):
                dt = datetime.fromtimestamp(time_val)
            else:
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M:%S']:
                    try:
                        dt = datetime.strptime(str(time_val), fmt)
                        break
                    except:
                        continue
                else:
                    continue
            
            sender = m.get('senderDisplayName', '') or m.get('senderNickname', '') or ''
            content = m.get('content', '') or ''
            is_send = m.get('isSend', 0)  # 1表示自己发的
            
            if not sender:
                continue
            
            msg_data = {
                'time': dt,
                'sender': sender,
                'type': msg_type,
                'content': content,
                'is_send': is_send,
            }
            
            parsed_all.append(msg_data)
            
            # 年份过滤
            if year_filter is None or dt.strftime('%Y') == str(year_filter):
                parsed.append(msg_data)
        except:
            continue
    
    if not parsed:
        return None
    
    parsed.sort(key=lambda x: x['time'])
    parsed_all.sort(key=lambda x: x['time'])
    total = len(parsed)
    
    # 统计成员消息数
    member_msgs = defaultdict(int)
    for m in parsed:
        member_msgs[m['sender']] += 1
    
    member_count = len(member_msgs)
    
    # 统计"我"的消息数
    my_msgs = 0
    my_sender_name = None
    
    # 方法1：通过isSend字段
    for m in parsed:
        if m.get('is_send') == 1:
            my_msgs += 1
            if not my_sender_name:
                my_sender_name = m['sender']
    
    # 方法2：如果isSend没用，通过my_name匹配
    if my_msgs == 0 and my_name:
        for sender, count in member_msgs.items():
            # 模糊匹配（去掉特殊字符）
            clean_sender = ''.join(c for c in sender if c.isalnum() or '\u4e00' <= c <= '\u9fff')
            clean_my = ''.join(c for c in my_name if c.isalnum() or '\u4e00' <= c <= '\u9fff')
            if clean_sender and clean_my and (clean_my in clean_sender or clean_sender in clean_my):
                my_msgs = count
                my_sender_name = sender
                break
    
    my_pct = round(my_msgs / total * 100, 1) if total else 0
    
    # 我在群里的排名
    my_rank = 0
    if my_msgs > 0:
        sorted_members = sorted(member_msgs.items(), key=lambda x: -x[1])
        for i, (name, count) in enumerate(sorted_members, 1):
            if count == my_msgs or name == my_sender_name:
                my_rank = i
                break
    
    # 活跃天数
    active_days = set(m['time'].strftime('%Y-%m-%d') for m in parsed)
    days = len(active_days)
    
    # 时间分布
    hours = defaultdict(int)
    weekdays = defaultdict(int)
    for m in parsed:
        hours[m['time'].hour] += 1
        weekdays[m['time'].weekday()] += 1
    
    # 深夜消息 (23-5点，统一标准)
    late_night = sum(hours[h] for h in [23, 0, 1, 2, 3, 4, 5])
    
    # 高峰时段
    peak_hour = max(hours.keys(), key=lambda h: hours[h]) if hours else 12
    
    # 月度分布（使用全量数据）
    monthly = defaultdict(int)
    for m in parsed_all:
        monthly[m['time'].strftime('%Y-%m')] += 1
    
    # 话痨排行
    top_talkers = sorted(member_msgs.items(), key=lambda x: -x[1])[:10]
    
    return {
        'name': group_name,
        'total_msgs': total,
        'member_count': member_count,
        'days': days,
        'avg_daily': round(total / max(days, 1), 1),
        'top_talkers': top_talkers,
        'member_msgs': dict(member_msgs),
        'hours': dict(hours),
        'weekdays': dict(weekdays),
        'monthly': dict(monthly),
        'peak_hour': peak_hour,
        'late_night': late_night,
        'my_msgs': my_msgs,
        'my_pct': my_pct,
        'my_rank': my_rank,
        'my_sender_name': my_sender_name,
        'late_night_pct': round(late_night / total * 100, 1) if total else 0,
    }


def analyze_private_excel(df, chat_name, my_name=None):
    """分析私聊Excel数据（包括点头之交：只有一方发消息）"""
    from A_enhanced_chat_analyzer import (
        MODAL_WORDS, DEEP_TOPICS, VOCAB_LEVELS,
        _calc_message_length, _calc_language_style, _calc_emoji_stats,
        _calc_time_pattern, _calc_response_time, _calc_content_richness,
        _calc_deep_topics, _calc_conversation_structure, _calc_monthly_trends, _calc_care_invite
    )
    
    messages = []
    senders = set()
    
    for _, row in df.iterrows():
        try:
            time_val = row.get('时间', '')
            sender = str(row.get('发送者昵称', '') or row.get('发送者备注', '')).strip()
            msg_type = str(row.get('消息类型', ''))
            content = str(row.get('内容', ''))
            
            if pd.isna(time_val) or not sender or sender == 'nan':
                continue
            if '系统消息' in msg_type:
                continue
            # 排除群名本身
            if sender == chat_name:
                continue
            
            dt = None
            if isinstance(time_val, datetime):
                dt = time_val
            else:
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M:%S']:
                    try:
                        dt = datetime.strptime(str(time_val), fmt)
                        break
                    except:
                        continue
            
            if not dt:
                continue
            
            senders.add(sender)
            messages.append({
                'time': dt,
                'sender': sender,
                'type': msg_type,
                'content': content,
            })
        except:
            continue
    
    if not messages:
        return None
    
    messages.sort(key=lambda x: x['time'])
    
    # 确定"我"和"Ta"
    sender_list = list(senders)
    
    if len(senders) == 2:
        # 正常私聊：两人都发过消息
        if my_name and my_name in senders:
            me = my_name
            them = [s for s in sender_list if s != my_name][0]
        else:
            # 默认：发送消息较多的是"我"
            counts = defaultdict(int)
            for m in messages:
                counts[m['sender']] += 1
            sorted_senders = sorted(counts.items(), key=lambda x: -x[1])
            me = sorted_senders[0][0]
            them = sorted_senders[1][0]
    elif len(senders) == 1:
        # 点头之交：只有一方发消息
        only_sender = sender_list[0]
        if my_name and only_sender == my_name:
            # 我发了消息，对方没回 → 对方名字从chat_name获取
            me = my_name
            them = chat_name
        else:
            # 对方发了消息，我没回
            me = my_name if my_name else "我"
            them = only_sender
    else:
        return None
    
    # 标记is_me
    for m in messages:
        m['is_me'] = (m['sender'] == me)
    
    # 转换为enhanced_chat_analyzer需要的格式
    parsed = messages
    
    # 基础统计
    total = len(parsed)
    my_msgs = [m for m in parsed if m['is_me']]
    their_msgs = [m for m in parsed if not m['is_me']]
    dates = set(m['time'].strftime('%Y-%m-%d') for m in parsed)
    
    my_chars = sum(len(m['content']) for m in my_msgs if '文本' in m['type'])
    their_chars = sum(len(m['content']) for m in their_msgs if '文本' in m['type'])
    
    result = {
        'name': them,  # 对方名字作为聊天名
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
    
    # 消息类型
    types_me = defaultdict(int)
    types_them = defaultdict(int)
    type_keywords = {
        '文本消息': ['文本'],
        '引用消息': ['引用'],
        '图片消息': ['图片'],
        '语音消息': ['语音'],
        '视频消息': ['视频'],
        '表情消息': ['表情', '动画'],
    }
    for m in parsed:
        target = types_me if m['is_me'] else types_them
        for type_name, keywords in type_keywords.items():
            if any(k in m['type'] for k in keywords):
                target[type_name] += 1
                break
    
    result['msg_types_me'] = dict(types_me)
    result['msg_types_them'] = dict(types_them)
    result['quote_me'] = types_me.get('引用消息', 0)
    result['quote_them'] = types_them.get('引用消息', 0)
    result['quote_ratio'] = round(types_them.get('引用消息', 0) / max(types_me.get('引用消息', 1), 1), 2)
    
    # 消息长度
    my_text = [m for m in parsed if m['is_me'] and '文本' in m['type']]
    their_text = [m for m in parsed if not m['is_me'] and '文本' in m['type']]
    my_lens = [len(m['content']) for m in my_text if m['content']]
    their_lens = [len(m['content']) for m in their_text if m['content']]
    
    def calc_len_stats(lens):
        if not lens:
            return {'total': 0, 'avg': 0, 'median': 0, 'max': 0}
        return {'total': sum(lens), 'avg': round(mean(lens), 1), 'median': int(median(lens)), 'max': max(lens)}
    
    def calc_len_dist(lens):
        if not lens:
            return {'short': 0, 'medium': 0, 'long': 0}
        n = len(lens)
        return {
            'short': round(sum(1 for l in lens if l <= 10) / n * 100, 1),
            'medium': round(sum(1 for l in lens if 10 < l <= 30) / n * 100, 1),
            'long': round(sum(1 for l in lens if l > 50) / n * 100, 1),
        }
    
    result['len_me'] = calc_len_stats(my_lens)
    result['len_them'] = calc_len_stats(their_lens)
    result['len_dist_me'] = calc_len_dist(my_lens)
    result['len_dist_them'] = calc_len_dist(their_lens)
    
    # 语言风格
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
        return {'question': round(q/total*100, 1), 'exclaim': round(e/total*100, 1), 'statement': round(s/total*100, 1)}
    
    MODAL_WORDS_LOCAL = {
        '亲密/撒娇': ['嘛', '呀', '啦', '哒', '嘿嘿', '嘻嘻', '呐', '咯', '鸭', '呢'],
        '思考/犹豫': ['嗯', '唔', '额', '呃', 'emmm', 'emm', '嘶', 'hmm'],
        '确认/肯定': ['嗯嗯', '好的', '行', '可以', 'ok', 'OK', '好', '是的', '对', '好滴', '行的'],
        '笑声': ['哈哈', '哈哈哈', '233', 'hhh', '笑死', '哈', 'hhhh', '2333', 'xswl'],
    }
    
    def modal_analysis(texts):
        result = {cat: 0 for cat in MODAL_WORDS_LOCAL}
        word_counts = defaultdict(int)
        for t in texts:
            t_lower = t.lower()
            for cat, words in MODAL_WORDS_LOCAL.items():
                for w in words:
                    cnt = t_lower.count(w.lower())
                    result[cat] += cnt
                    if cnt > 0:
                        word_counts[w] += cnt
        top = sorted(word_counts.items(), key=lambda x: -x[1])[:10]
        return result, top
    
    my_texts = [m['content'] for m in my_text]
    their_texts = [m['content'] for m in their_text]
    
    result['sentence_me'] = sentence_types(my_texts)
    result['sentence_them'] = sentence_types(their_texts)
    my_modal, my_top = modal_analysis(my_texts)
    their_modal, their_top = modal_analysis(their_texts)
    result['modal_me'] = my_modal
    result['modal_them'] = their_modal
    result['top_modal_me'] = my_top
    result['top_modal_them'] = their_top
    
    # 表情统计
    import re
    emoji_pattern = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\u2600-\u2B55]+")
    
    my_wechat, my_unicode, their_wechat, their_unicode = defaultdict(int), defaultdict(int), defaultdict(int), defaultdict(int)
    for m in parsed:
        content = m['content']
        wechat_target = my_wechat if m['is_me'] else their_wechat
        unicode_target = my_unicode if m['is_me'] else their_unicode
        for e in re.findall(r'\[([^\]]+)\]', content):
            wechat_target[f'[{e}]'] += 1
        for e in emoji_pattern.findall(content):
            unicode_target[e] += 1
    
    result['emoji_me_total'] = sum(my_wechat.values()) + sum(my_unicode.values())
    result['emoji_them_total'] = sum(their_wechat.values()) + sum(their_unicode.values())
    result['wechat_emoji_me'] = sum(my_wechat.values())
    result['wechat_emoji_them'] = sum(their_wechat.values())
    result['unicode_emoji_me'] = sum(my_unicode.values())
    result['unicode_emoji_them'] = sum(their_unicode.values())
    from collections import Counter
    result['top_emoji_me'] = (Counter(my_wechat) + Counter(my_unicode)).most_common(5)
    result['top_emoji_them'] = (Counter(their_wechat) + Counter(their_unicode)).most_common(5)
    
    # 时间分布
    hours = {h: 0 for h in range(24)}
    weekdays = {i: 0 for i in range(7)}
    for m in parsed:
        hours[m['time'].hour] += 1
        weekdays[m['time'].weekday()] += 1
    
    peak_hour = max(hours.keys(), key=lambda h: hours[h])
    peak_wd = max(weekdays.keys(), key=lambda w: weekdays[w])
    quiet_wd = min(weekdays.keys(), key=lambda w: weekdays[w])
    wd_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    late_night = sum(hours.get(h, 0) for h in [23, 0, 1, 2, 3, 4, 5])
    
    result['hours'] = hours
    result['weekdays'] = weekdays
    result['peak_hour'] = peak_hour
    result['peak_weekday'] = wd_names[peak_wd]
    result['peak_weekday_count'] = weekdays[peak_wd]
    result['quiet_weekday'] = wd_names[quiet_wd]
    result['quiet_weekday_count'] = weekdays[quiet_wd]
    result['late_night'] = late_night
    result['late_night_pct'] = round(late_night / len(parsed) * 100, 1) if parsed else 0
    
    # 回复速度
    my_reply, their_reply = [], []
    my_by_period = {'工作日白天': [], '工作日晚上': [], '周末白天': [], '周末晚上': []}
    their_by_period = {'工作日白天': [], '工作日晚上': [], '周末白天': [], '周末晚上': []}
    prev = None
    for m in parsed:
        if prev and prev['is_me'] != m['is_me']:
            diff = (m['time'] - prev['time']).total_seconds()
            if 0 < diff < 3600:
                hour = m['time'].hour
                weekday = m['time'].weekday()
                is_weekend = weekday >= 5
                is_night = hour >= 18 or hour < 6
                period = ('周末' if is_weekend else '工作日') + ('晚上' if is_night else '白天')
                if m['is_me']:
                    my_reply.append(diff)
                    my_by_period[period].append(diff)
                else:
                    their_reply.append(diff)
                    their_by_period[period].append(diff)
        prev = m
    
    def safe_median(lst):
        return int(median(lst)) if lst else 0
    
    result['reply_me_median'] = safe_median(my_reply)
    result['reply_them_median'] = safe_median(their_reply)
    result['reply_me_avg'] = int(mean(my_reply)) if my_reply else 0
    result['reply_them_avg'] = int(mean(their_reply)) if their_reply else 0
    result['reply_me_by_period'] = {k: safe_median(v) for k, v in my_by_period.items()}
    result['reply_them_by_period'] = {k: safe_median(v) for k, v in their_by_period.items()}
    
    # 内容丰富度
    def analyze_richness(texts):
        if not texts:
            return {'unique_chars': 0, 'diversity': 0, 'english_pct': 0, 'english_words': 0}
        all_text = ''.join(texts)
        unique = len(set(all_text))
        diversity = round(unique / len(all_text) * 100, 2) if all_text else 0
        english_msgs = sum(1 for t in texts if re.search(r'[a-zA-Z]', t))
        english_pct = round(english_msgs / len(texts) * 100, 1)
        english_words = len(re.findall(r'[a-zA-Z]+', all_text))
        return {'unique_chars': unique, 'diversity': diversity, 'english_pct': english_pct, 'english_words': english_words}
    
    VOCAB_LEVELS_LOCAL = {
        '正式/书面': ['因此', '然而', '但是', '所以', '并且', '虽然', '尽管', '由于', '关于'],
        '口语化': ['咋', '啥', '咱', '俺', '整', '搞', '弄', '干嘛', '咋整', '得了', '行吧'],
        '网络流行语': ['yyds', '绝绝子', '无语子', 'awsl', '笑死', 'xswl', '破防', '上头', '摆烂', 'emo'],
    }
    
    def analyze_vocab(texts):
        result = {cat: 0 for cat in VOCAB_LEVELS_LOCAL}
        all_text = ' '.join(texts).lower()
        for cat, words in VOCAB_LEVELS_LOCAL.items():
            for w in words:
                result[cat] += all_text.count(w.lower())
        return result
    
    result['richness_me'] = analyze_richness(my_texts)
    result['richness_them'] = analyze_richness(their_texts)
    result['vocab_me'] = analyze_vocab(my_texts)
    result['vocab_them'] = analyze_vocab(their_texts)
    
    # 深度话题
    DEEP_TOPICS_LOCAL = {
        '情感/内心': ['开心', '难过', '伤心', '压力', '烦', '累', '想念', '喜欢', '爱', '感动', '焦虑', '孤独'],
        '家庭/亲人': ['爸', '妈', '家人', '家里', '哥', '姐', '弟', '妹', '父母', '奶奶', '爷爷'],
        '价值观/思考': ['觉得', '认为', '应该', '意义', '价值', '为什么', '怎么想'],
        '身体/健康': ['头疼', '感冒', '失眠', '健身', '生病', '休息', '累了', '困'],
        '未来/规划': ['计划', '打算', '目标', '梦想', '未来', '工作', '努力', '考试'],
        '回忆/过去': ['以前', '之前', '记得', '回忆', '曾经', '那时候', '小时候'],
    }
    
    topics_me = {t: 0 for t in DEEP_TOPICS_LOCAL}
    topics_them = {t: 0 for t in DEEP_TOPICS_LOCAL}
    for m in parsed:
        if '文本' not in m['type']:
            continue
        content = m['content'].lower()
        target = topics_me if m['is_me'] else topics_them
        for topic, keywords in DEEP_TOPICS_LOCAL.items():
            if any(k in content for k in keywords):
                target[topic] += 1
    
    result['topics_me'] = topics_me
    result['topics_them'] = topics_them
    
    # 会话结构 - 使用统计方法判断
    # 计算所有时间间隔
    time_diffs = []
    for i in range(1, len(parsed)):
        diff = (parsed[i]['time'] - parsed[i-1]['time']).total_seconds()
        if diff > 0:
            time_diffs.append(diff)
    
    # 用统计方法确定分割阈值
    # 思路：短间隔是连续回复，长间隔是另起话题
    # 用中位数的3倍或10分钟取较大值作为阈值
    if time_diffs:
        median_diff = median(time_diffs)
        threshold = max(median_diff * 3, 600)  # 至少10分钟，或中位数的3倍
        threshold = min(threshold, 7200)  # 最多2小时
    else:
        threshold = 1800  # 默认30分钟
    
    sessions = []
    current = [parsed[0]] if parsed else []
    for i in range(1, len(parsed)):
        diff = (parsed[i]['time'] - parsed[i-1]['time']).total_seconds()
        if diff > threshold:
            sessions.append(current)
            current = [parsed[i]]
        else:
            current.append(parsed[i])
    if current:
        sessions.append(current)
    
    my_init = sum(1 for s in sessions if s[0]['is_me'])
    their_init = len(sessions) - my_init
    session_lens = [len(s) for s in sessions]
    
    result['sessions'] = len(sessions)
    result['my_init'] = my_init
    result['their_init'] = their_init
    result['my_init_pct'] = round(my_init / len(sessions) * 100, 1) if sessions else 0
    result['their_init_pct'] = round(their_init / len(sessions) * 100, 1) if sessions else 0
    result['avg_session_len'] = round(mean(session_lens), 1) if session_lens else 0
    result['max_session_len'] = max(session_lens) if session_lens else 0
    result['session_threshold'] = int(threshold)  # 记录使用的阈值
    
    # 收集消息样本（用于开场动画）
    msg_samples = []
    for m in parsed:
        if '文本' in m['type'] and m['content'] and len(m['content']) < 50:
            # 过滤掉太长的和特殊内容
            content = m['content'].strip()
            if content and not content.startswith('[') and not content.startswith('http'):
                msg_samples.append({
                    'text': content,
                    'is_me': m['is_me'],
                    'month': m['time'].strftime('%Y-%m'),
                })
    result['msg_samples'] = msg_samples[:100]  # 每个私聊最多保留100条样本
    
    # 月度趋势
    months_me = defaultdict(int)
    months_them = defaultdict(int)
    for m in parsed:
        key = m['time'].strftime('%Y-%m')
        if m['is_me']:
            months_me[key] += 1
        else:
            months_them[key] += 1
    all_months = sorted(set(months_me.keys()) | set(months_them.keys()))
    result['monthly'] = {m: {'me': months_me.get(m, 0), 'them': months_them.get(m, 0), 'total': months_me.get(m, 0) + months_them.get(m, 0)} for m in all_months}
    
    # 每日统计（用于节日分析）
    daily_counts = defaultdict(int)
    for m in parsed:
        day_key = m['time'].strftime('%Y-%m-%d')
        daily_counts[day_key] += 1
    result['daily'] = dict(daily_counts)
    
    # 关怀统计
    care_words = ['好点了', '怎么样了', '还好吗', '注意', '照顾', '保重', '休息', '早点睡', '别太累', '加油', '辛苦', '小心', '多喝水']
    invite_words = ['一起', '要不要', '去不去', '来不来', '走不走', '约', '出来', '见面', '吃饭']
    
    my_care, their_care, my_invite, their_invite = 0, 0, 0, 0
    for m in parsed:
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
    
    result['care_me'] = my_care
    result['care_them'] = their_care
    result['invite_me'] = my_invite
    result['invite_them'] = their_invite
    
    return result


def batch_analyze(data_dir, my_name=None, analyze_excel=True, exclude_file_helper=True, year_filter='2025'):
    """
    批量分析目录下所有数据文件
    JSON文件必须分析，Excel文件可选（analyze_excel参数控制）
    Excel文件自动判断：2人=私聊，>2人=群聊
    
    Args:
        data_dir: 数据目录路径
        my_name: 我的微信昵称（用于识别自己）
        analyze_excel: 是否分析Excel文件（默认True，设为False可跳过以加快速度）
        exclude_file_helper: 是否剔除"文件传输助手"（默认True）
        year_filter: 年份过滤，默认'2025'，设为None则不过滤
    
    Returns:
        dict: 包含所有分析结果的字典
    """
    private_chats = []
    group_chats = []
    errors = []
    skipped = []  # 跳过的文件
    
    # 用于去重
    seen_private = set()  # 已处理的私聊（对方名字）
    seen_groups = set()   # 已处理的群聊（群名+消息数）
    
    files = os.listdir(data_dir)
    all_json_files = [f for f in files if f.endswith('.json')]
    excel_files = [f for f in files if f.endswith('.xlsx') or f.endswith('.xls')]
    
    # 区分JSON私聊和群聊
    json_files = []  # 私聊
    group_json_files = []  # 群聊
    
    for f in all_json_files:
        try:
            filepath = os.path.join(data_dir, f)
            with open(filepath, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
            session = data.get('session', {})
            chat_type = session.get('type', '')
            if chat_type == '群聊':
                group_json_files.append(f)
            else:
                json_files.append(f)
        except:
            json_files.append(f)  # 出错的默认当私聊处理
    
    print(f"📁 扫描目录: {data_dir}")
    print(f"   找到 {len(json_files)} 个私聊JSON + {len(group_json_files)} 个群聊JSON + {len(excel_files)} 个Excel")
    if my_name:
        print(f"   我的昵称: {my_name}")
    print()
    
    # 处理JSON私聊
    if json_files:
        print("🔄 分析JSON私聊...")
        for i, f in enumerate(json_files, 1):
            filepath = os.path.join(data_dir, f)
            try:
                data = load_chat_json(filepath)
                result = analyze_chat_full(data, year_filter=year_filter)
                if result:
                    # 检查是否是"文件传输助手"
                    if exclude_file_helper and result['name'] == '文件传输助手':
                        skipped.append((f, "文件传输助手"))
                        print(f"   [{i}/{len(json_files)}] ⏭ {result['name']}: 跳过（文件传输助手）")
                        continue
                    # 检查是否跟自己聊天
                    if my_name and result['name'] == my_name:
                        skipped.append((f, "跟自己的私聊"))
                        print(f"   [{i}/{len(json_files)}] ⏭ {result['name']}: 跳过（自己）")
                        continue
                    # 去重
                    if result['name'] in seen_private:
                        skipped.append((f, "重复"))
                        print(f"   [{i}/{len(json_files)}] ⏭ {result['name']}: 跳过（重复）")
                        continue
                    seen_private.add(result['name'])
                    private_chats.append(result)
                    print(f"   [{i}/{len(json_files)}] ✓ 私聊 {result['name']}: {result['total_msgs']}条")
            except Exception as e:
                errors.append((f, str(e)))
                print(f"   [{i}/{len(json_files)}] ✗ {f}: {e}")
    print()
    
    # 处理群聊JSON
    if group_json_files:
        print("🔄 分析JSON群聊...")
        for i, f in enumerate(group_json_files, 1):
            filepath = os.path.join(data_dir, f)
            try:
                result = analyze_group_json(filepath, my_name, year_filter=year_filter)
                if result:
                    # 去重
                    group_key = f"{result['name']}_{result['total_msgs']}"
                    if group_key in seen_groups:
                        skipped.append((f, "重复"))
                        print(f"   [{i}/{len(group_json_files)}] ⏭ {result['name']}: 跳过（重复）")
                        continue
                    seen_groups.add(group_key)
                    group_chats.append(result)
                    print(f"   [{i}/{len(group_json_files)}] ✓ {result['name']}: {result['total_msgs']}条, {result['member_count']}人")
            except Exception as e:
                errors.append((f, str(e)))
                print(f"   [{i}/{len(group_json_files)}] ✗ {f}: {e}")
        print()
    
    # 处理Excel（自动判断私聊/群聊）- 根据analyze_excel参数决定是否分析
    if HAS_PANDAS and excel_files and analyze_excel:
        print("🔄 分析Excel文件（自动判断私聊/群聊）...")
        for i, f in enumerate(excel_files, 1):
            filepath = os.path.join(data_dir, f)
            try:
                df, name = load_group_excel(filepath)
                
                # 统计发送者数量（排除系统消息和群名本身）
                senders = set()
                for _, row in df.iterrows():
                    sender = str(row.get('发送者昵称', '') or row.get('发送者备注', '')).strip()
                    msg_type = str(row.get('消息类型', ''))
                    if sender and sender != 'nan' and '系统消息' not in msg_type:
                        # 排除群名本身作为发送者
                        if sender != name:
                            senders.add(sender)
                
                # 判断是否是私聊还是群聊
                # 私聊：1-2人（可能对方没发过消息）
                # 群聊：>2人
                if len(senders) <= 2:
                    # 可能是私聊（包括点头之交：对方一条没发）
                    # 排除：会话名就是自己（文件传输助手等）
                    if my_name and name == my_name:
                        skipped.append((f, "自己的会话"))
                        print(f"   [{i}/{len(excel_files)}] ⏭ {name}: 跳过（自己的会话）")
                        continue
                    
                    # 排除：文件传输助手
                    if exclude_file_helper and name == '文件传输助手':
                        skipped.append((f, "文件传输助手"))
                        print(f"   [{i}/{len(excel_files)}] ⏭ {name}: 跳过（文件传输助手）")
                        continue
                    
                    result = analyze_private_excel(df, name, my_name)
                    if result:
                        # 检查是否是"文件传输助手"（从结果中再次确认）
                        if exclude_file_helper and result['name'] == '文件传输助手':
                            skipped.append((f, "文件传输助手"))
                            print(f"   [{i}/{len(excel_files)}] ⏭ 私聊 {result['name']}: 跳过（文件传输助手）")
                            continue
                        # 检查是否跟自己聊天（对方名字是自己）
                        if my_name and result['name'] == my_name:
                            skipped.append((f, "跟自己的私聊"))
                            print(f"   [{i}/{len(excel_files)}] ⏭ 私聊 {result['name']}: 跳过（自己）")
                            continue
                        # 去重
                        if result['name'] in seen_private:
                            skipped.append((f, "重复"))
                            print(f"   [{i}/{len(excel_files)}] ⏭ 私聊 {result['name']}: 跳过（重复）")
                            continue
                        seen_private.add(result['name'])
                        private_chats.append(result)
                        print(f"   [{i}/{len(excel_files)}] ✓ 私聊 {result['name']}: {result['total_msgs']}条")
                else:
                    # 群聊（>2人）
                    result = analyze_group(df, name, my_name)
                    if result:
                        # 去重（用群名+消息数作为标识）
                        group_key = f"{result['name']}_{result['total_msgs']}"
                        if group_key in seen_groups:
                            skipped.append((f, "重复"))
                            print(f"   [{i}/{len(excel_files)}] ⏭ 群聊 {result['name']}: 跳过（重复）")
                            continue
                        seen_groups.add(group_key)
                        group_chats.append(result)
                        print(f"   [{i}/{len(excel_files)}] ✓ 群聊 {result['name']}: {result['total_msgs']}条, {result['member_count']}人")
            except Exception as e:
                errors.append((f, str(e)))
                print(f"   [{i}/{len(excel_files)}] ✗ {f}: {e}")
    
    print()
    print(f"✅ 完成! 私聊 {len(private_chats)} 个, 群聊 {len(group_chats)} 个, 跳过 {len(skipped)} 个, 失败 {len(errors)} 个")
    
    return {
        'private_chats': private_chats,
        'group_chats': group_chats,
        'errors': errors,
        'summary': generate_summary(private_chats, group_chats),
    }


def generate_summary(private_chats, group_chats):
    """生成汇总统计"""
    
    if not private_chats:
        return {}
    
    # === 私聊汇总 ===
    
    # 基础汇总
    total_private_msgs = sum(c['total_msgs'] for c in private_chats)
    total_private_chars = sum(c['total_chars'] for c in private_chats)
    total_private_days = len(set(
        d for c in private_chats 
        for d in [c['date_range'][0], c['date_range'][1]] if d
    ))
    total_sessions = sum(c['sessions'] for c in private_chats)
    
    # 排行榜生成函数
    def make_ranking(key, reverse=True, formatter=None):
        """生成排行榜"""
        valid = [(c['name'], c.get(key, 0)) for c in private_chats if c.get(key, 0)]
        if not valid:
            return {'top': [], 'stats': {}}
        
        sorted_list = sorted(valid, key=lambda x: x[1], reverse=reverse)
        values = [v for _, v in valid]
        
        return {
            'top': sorted_list[:10],
            'bottom': sorted_list[-3:] if len(sorted_list) > 3 else [],
            'stats': {
                'max': max(values),
                'min': min(values),
                'avg': round(mean(values), 2),
                'median': round(median(values), 2),
                'std': round(stdev(values), 2) if len(values) > 1 else 0,
            }
        }
    
    rankings = {
        # 消息量排行
        'total_msgs': make_ranking('total_msgs'),
        'total_chars': make_ranking('total_chars'),
        'days': make_ranking('days'),
        'sessions': make_ranking('sessions'),
        
        # 回复速度（越小越好）
        'reply_them_median': make_ranking('reply_them_median', reverse=False),
        'reply_me_median': make_ranking('reply_me_median', reverse=False),
        
        # 发起率
        'their_init_pct': make_ranking('their_init_pct'),
        'my_init_pct': make_ranking('my_init_pct'),
        
        # 深夜消息
        'late_night': make_ranking('late_night'),
        'late_night_pct': make_ranking('late_night_pct'),
        
        # 关怀
        'care_them': make_ranking('care_them'),
        'care_me': make_ranking('care_me'),
        
        # 引用
        'quote_them': make_ranking('quote_them'),
        'quote_ratio': make_ranking('quote_ratio'),
        
        # 会话长度
        'max_session_len': make_ranking('max_session_len'),
        'avg_session_len': make_ranking('avg_session_len'),
    }
    
    # 特殊排行榜（带标题和文案）
    special_rankings = {
        '💬 聊得最多': {
            'key': 'total_msgs',
            'data': rankings['total_msgs'],
            'unit': '条消息',
            'desc': '和你消息最多的人',
        },
        '⚡ 秒回冠军': {
            'key': 'reply_them_median',
            'data': rankings['reply_them_median'],
            'unit': '秒',
            'desc': '谁回复你最快',
        },
        '📌 你的置顶': {
            'key': 'reply_me_median',
            'data': rankings['reply_me_median'],
            'unit': '秒',
            'desc': '你回复谁最快',
        },
        '🔍 最常找你': {
            'key': 'their_init_pct',
            'data': rankings['their_init_pct'],
            'unit': '%',
            'desc': '谁最主动找你聊天',
        },
        '💭 你最想找': {
            'key': 'my_init_pct',
            'data': rankings['my_init_pct'],
            'unit': '%',
            'desc': '你最主动找谁聊天',
        },
        '🌙 深夜陪伴': {
            'key': 'late_night',
            'data': rankings['late_night'],
            'unit': '条',
            'desc': '深夜聊天最多的人',
        },
        '❤️ 最关心你': {
            'key': 'care_them',
            'data': rankings['care_them'],
            'unit': '次',
            'desc': '谁最常对你嘘寒问暖',
        },
        '🔥 聊到停不下来': {
            'key': 'max_session_len',
            'data': rankings['max_session_len'],
            'unit': '条/次',
            'desc': '单次会话最长记录',
        },
        '👀 认真倾听者': {
            'key': 'quote_them',
            'data': rankings['quote_them'],
            'unit': '次引用',
            'desc': '谁最常引用你的消息',
        },
    }
    
    # 好友分组
    def categorize_friends():
        categories = {
            '💎 密友 (500+条)': [],
            '💛 好友 (100-500条)': [],
            '🤝 熟人 (30-100条)': [],
            '👋 点头之交 (<30条)': [],
        }
        for c in private_chats:
            total = c['total_msgs']
            if total >= 500:
                categories['💎 密友 (500+条)'].append((c['name'], total))
            elif total >= 100:
                categories['💛 好友 (100-500条)'].append((c['name'], total))
            elif total >= 30:
                categories['🤝 熟人 (30-100条)'].append((c['name'], total))
            else:
                categories['👋 点头之交 (<30条)'].append((c['name'], total))
        
        # 每组内按消息量排序
        for k in categories:
            categories[k].sort(key=lambda x: -x[1])
        
        return categories
    
    # === 群聊汇总 ===
    group_summary = {}
    if group_chats:
        total_group_msgs = sum(g['total_msgs'] for g in group_chats)
        group_summary = {
            'count': len(group_chats),
            'total_msgs': total_group_msgs,
            'top_groups': sorted(group_chats, key=lambda x: -x['total_msgs'])[:10],
        }
    
    return {
        'private': {
            'count': len(private_chats),
            'total_msgs': total_private_msgs,
            'total_chars': total_private_chars,
            'total_sessions': total_sessions,
            'rankings': rankings,
            'special_rankings': special_rankings,
            'friend_categories': categorize_friends(),
        },
        'group': group_summary,
        'overall': {
            'total_msgs': total_private_msgs + (group_summary.get('total_msgs', 0)),
            'private_count': len(private_chats),
            'group_count': len(group_chats),
        }
    }


def save_results(results, output_path):
    """保存分析结果到JSON文件"""
    
    # 转换不可序列化的对象
    def convert(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=convert)
    
    print(f"💾 结果已保存: {output_path}")


# ==================== 测试 ====================
if __name__ == '__main__':
    import sys
    
    data_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    
    # 检查data目录是否存在
    if not os.path.exists(data_dir):
        print(f"⚠️  数据目录 '{data_dir}' 不存在！")
        print(f"   请创建 {data_dir} 文件夹并将json/excel文件放入其中")
        sys.exit(1)
    
    results = batch_analyze(data_dir)
    
    # 打印汇总
    summary = results['summary']
    
    print("\n" + "="*60)
    print("📊 汇总统计")
    print("="*60)
    
    if summary.get('private'):
        p = summary['private']
        print(f"\n【私聊】")
        print(f"  联系人数: {p['count']}")
        print(f"  总消息数: {p['total_msgs']:,}")
        print(f"  总字数: {p['total_chars']:,}")
        print(f"  总会话数: {p['total_sessions']}")
        
        print(f"\n【私聊排行榜】")
        for title, data in p['special_rankings'].items():
            if data['data']['top']:
                top1 = data['data']['top'][0]
                print(f"  {title}: {top1[0]} ({top1[1]} {data['unit']})")
        
        print(f"\n【好友分组】")
        for cat, friends in p['friend_categories'].items():
            print(f"  {cat}: {len(friends)}人")
    
    if summary.get('group'):
        g = summary['group']
        print(f"\n【群聊】")
        print(f"  群数量: {g['count']}")
        print(f"  总消息数: {g['total_msgs']:,}")
        if g.get('top_groups'):
            print(f"  最活跃群: {g['top_groups'][0]['name']} ({g['top_groups'][0]['total_msgs']}条)")
    
    # 保存结果
    save_results(results, 'analysis_results.json')
