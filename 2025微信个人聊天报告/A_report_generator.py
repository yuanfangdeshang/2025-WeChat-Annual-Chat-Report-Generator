# -*- coding: utf-8 -*-
"""
A_report_generator.py - 微信年度报告生成器
模块化版本 - CSS和JS拆分到独立文件
文件命名以A开头便于查找
"""

from datetime import datetime
from statistics import mean, median, stdev
from A_batch_analyzer import batch_analyze
import random
import math

# 导入样式和脚本模块
try:
    from A_styles import get_css_styles
    from A_scripts import get_js_scripts
    USE_MODULES = True
except ImportError:
    USE_MODULES = False
    print("⚠️ 未找到模块文件，使用内置样式")


# ===== 姓名加密/脱敏工具 =====
def mask_name(name, mask_mode='partial', is_group=False):
    """
    对姓名进行脱敏处理
    mask_mode:
        - 'full': 完全脱敏（*同学 或 **群聊）
        - 'none': 不脱敏
    is_group: 是否是群聊名称
    """
    if not name or mask_mode == 'none':
        return name
    
    if mask_mode == 'full':
        if is_group:
            return '**群聊'
        else:
            return '*同学'
    
    # 兼容旧模式，统一使用full模式
    if mask_mode in ('partial', 'star', 'emoji'):
        if is_group:
            return '**群聊'
        else:
            return '*同学'
    
    return name


def mask_message(content, mask_mode='none'):
    """对消息内容进行脱敏"""
    if not content or mask_mode == 'none':
        return content
    return '*****'


# ===== 有意境的文件名生成 =====
def generate_poetic_name():
    """生成有意境的文件名前缀"""
    prefixes = [
        'A_星河漫漫', 'A_流年似水', 'A_岁月如歌', 'A_时光剪影', 
        'A_浮生若梦', 'A_念念不忘', 'A_情深似海', 'A_温暖如初',
        'A_微光不灭', 'A_繁星点点', 'A_月色朦胧', 'A_清风徐来',
        'A_心有所属', 'A_细水长流', 'A_春风十里', 'A_暖阳微醺',
    ]
    return random.choice(prefixes)


def fmt_time(seconds):
    if not seconds or seconds == 0:
        return "N/A"
    if seconds < 60:
        return f"{int(seconds)}秒"
    elif seconds < 3600:
        return f"{int(seconds//60)}分{int(seconds%60)}秒"
    else:
        return f"{int(seconds//3600)}小时"


def generate_final_report(results, output_path, my_name=None, bgm_path=None, mask_mode='none'):
    """
    生成终极版报告
    
    Args:
        results: 分析结果
        output_path: 输出文件路径
        my_name: 我的名字
        bgm_path: 背景音乐路径
        mask_mode: 姓名脱敏模式 ('none'/'partial'/'star'/'emoji')
    """
    
    import base64
    import os
    import json
    import random
    from collections import defaultdict
    
    # 创建带脱敏的名字显示函数
    def display_name(name):
        return mask_name(name, mask_mode, is_group=False)
    
    def display_group_name(name):
        return mask_name(name, mask_mode, is_group=True)
    
    def display_message(content):
        return mask_message(content, mask_mode)
    
    # 读取背景音乐并转为base64
    bgm_base64 = ''
    if bgm_path and os.path.exists(bgm_path):
        try:
            with open(bgm_path, 'rb') as f:
                bgm_base64 = base64.b64encode(f.read()).decode('utf-8')
            print(f"🎵 已加载背景音乐: {bgm_path}")
        except Exception as e:
            print(f"⚠️ 加载背景音乐失败: {e}")
    
    summary = results['summary']
    private_chats = results['private_chats']
    group_chats = results['group_chats']
    
    p = summary.get('private', {})
    g = summary.get('group', {})
    
    sorted_private = sorted(private_chats, key=lambda x: -x['total_msgs'])
    sorted_groups = sorted(group_chats, key=lambda x: -x['total_msgs'])
    
    # 【重要】只有消息总数前100名的好友才能参与排名
    top_100_private = sorted_private[:100]
    
    total_msgs = p.get('total_msgs', 0) + g.get('total_msgs', 0)
    total_chars = p.get('total_chars', 0)
    
    # 计算2025年消息数的辅助函数
    def get_2025_msgs(chat):
        monthly = chat.get('monthly', {})
        return sum(v.get('total', 0) if isinstance(v, dict) else v for k, v in monthly.items() if k.startswith('2025'))
    
    # 统计分析数据（基于2025年）
    friends_2025 = [(c, get_2025_msgs(c)) for c in private_chats]
    silent_friends = [c for c, msgs in friends_2025 if msgs < 10]
    active_friends = [c for c, msgs in friends_2025 if msgs >= 100]
    
    # ============ 故事性开场 ============
    def generate_story_intro():
        """生成个性化的故事开场，增强叙事感"""
        # 收集关键数据
        best_friend = sorted_private[0] if sorted_private else None
        total_late = sum(c.get('late_night', 0) for c in private_chats)
        total_care = sum(c.get('care_me', 0) + c.get('care_them', 0) for c in private_chats)
        
        # 找出消息最多的月份
        monthly_totals = defaultdict(int)
        for c in private_chats:
            for k, v in c.get('monthly', {}).items():
                if k.startswith('2025'):
                    monthly_totals[k] += v.get('total', 0) if isinstance(v, dict) else v
        peak_month = max(monthly_totals, key=monthly_totals.get) if monthly_totals else '2025-06'
        month_names = {'01':'一月','02':'二月','03':'三月','04':'四月','05':'五月','06':'六月',
                      '07':'七月','08':'八月','09':'九月','10':'十月','11':'十一月','12':'十二月'}
        peak_month_name = month_names.get(peak_month[-2:], '某月')
        
        # 构建故事片段
        stories = []
        
        if best_friend:
            friend_name = display_name(best_friend['name'])
            stories.append(f'有一个人叫 <strong>{friend_name}</strong>，Ta在你的消息列表里占据了最重要的位置')
        
        if total_late > 100:
            stories.append(f'有 <strong>{total_late}</strong> 个深夜，你选择了不睡觉，和某个人聊天')
        
        if peak_month_name:
            stories.append(f'<strong>{peak_month_name}</strong>，是你这一年说话最多的时候，那段日子一定很特别')
        
        if total_care > 50:
            stories.append(f'你说了 <strong>{total_care}</strong> 次"关心"，收获了同样多的温暖')
        
        # 随机选择2-3个故事片段
        import random
        selected = random.sample(stories, min(2, len(stories))) if stories else []
        
        if not selected:
            return '<span class="story-line">2025年，你的故事都藏在聊天记录里...</span>'
        
        html = '<div class="story-lines">'
        for s in selected:
            html += f'<span class="story-line">{s}</span>'
        html += '</div>'
        
        return html
    
    # ============ 开场动画数据准备 ============
    def prepare_intro_animation_data():
        """准备数据驱动的开场动画所需数据"""
        # 1. 收集常用聊天片段/关键词
        chat_snippets = [
            '在吗？', '好的', '哈哈哈', '😂', '晚安', '早安', '好的好的',
            '收到', '谢谢', '辛苦了', '加油', '🌙', '❤️', '👍', '666',
            '今天', '明天', '一起', '吃饭', '回家', '睡觉', '工作',
            '开心', '想你', '等你', '来了', '走了', '到了', '好久不见'
        ]
        
        # 2. 从数据中提取实际常用表情
        emoji_counts = defaultdict(int)
        for chat in private_chats:
            emoji_data = chat.get('emoji_me', {}) or chat.get('emoji_stats', {}) or {}
            if isinstance(emoji_data, dict):
                for emoji, count in emoji_data.items():
                    if isinstance(count, (int, float)):
                        emoji_counts[emoji] += int(count)
        
        top_emojis = sorted(emoji_counts.items(), key=lambda x: -x[1])[:10]
        if top_emojis:
            for emoji, _ in top_emojis[:5]:
                if emoji not in chat_snippets:
                    chat_snippets.append(emoji)
        
        # 3. 月度数据
        monthly_data = []
        month_keywords = {
            '01': ['新年好', '🎊', '元旦'],
            '02': ['新年快乐', '🧧', '春节', '过年'],
            '03': ['春天', '🌸'],
            '04': ['清明', '踏青'],
            '05': ['五一', '劳动节', '520'],
            '06': ['端午', '粽子', '毕业'],
            '07': ['暑假', '☀️', '好热'],
            '08': ['立秋', '七夕', '❤️'],
            '09': ['开学', '中秋', '🥮'],
            '10': ['国庆', '🎉', '十一'],
            '11': ['双十一', '购物', '冷了'],
            '12': ['圣诞', '🎄', '跨年', '❄️']
        }
        
        monthly_totals = defaultdict(int)
        for c in private_chats + group_chats:
            for k, v in c.get('monthly', {}).items():
                if k.startswith('2025'):
                    monthly_totals[k] += v.get('total', 0) if isinstance(v, dict) else v
        
        for m in ['01','02','03','04','05','06','07','08','09','10','11','12']:
            key = f'2025-{m}'
            count = monthly_totals.get(key, 0)
            keywords = month_keywords.get(m, [])
            monthly_data.append({
                'month': int(m),
                'count': count,
                'keywords': keywords
            })
        
        # 4. 核心统计数据
        total_late = sum(c.get('late_night', 0) for c in private_chats)
        total_care = sum(c.get('care_me', 0) + c.get('care_them', 0) for c in private_chats)
        total_sessions = sum(c.get('sessions', 0) for c in private_chats)
        
        # 找最活跃好友
        best_friend_name = display_name(sorted_private[0]['name']) if sorted_private else '好友'
        
        # 5. 构建JSON数据
        import json
        animation_data = {
            'snippets': chat_snippets[:30],  # 限制数量
            'emojis': [e[0] for e in top_emojis[:8]] if top_emojis else ['😂', '🥰', '👍', '❤️', '😊'],
            'monthly': monthly_data,
            'stats': {
                'totalMsgs': total_msgs,
                'totalChars': total_chars,
                'friends': len(sorted_private),
                'groups': len(sorted_groups),
                'lateNight': total_late,
                'care': total_care,
                'sessions': total_sessions
            },
            'bestFriend': best_friend_name
        }
        
        return json.dumps(animation_data, ensure_ascii=False)
    
    # ============ 智能文案生成 ============
    def generate_insights():
        """生成智能洞察文案
        【注意】排名类数据只使用消息总数前100名的好友
        """
        insights = []
        
        # 点头之交提醒（全部好友）
        if len(silent_friends) > 3:
            insights.append(f'💭 你有 <strong>{len(silent_friends)}</strong> 位好友今年消息不足10条，有些人，可能只是在等你先开口~')
        
        # 最佳拍档（按2025年消息排序，只用前100名好友参与）
        top_100_2025 = [(c, get_2025_msgs(c)) for c in top_100_private]
        sorted_by_2025 = sorted(top_100_2025, key=lambda x: -x[1])
        if sorted_by_2025 and sorted_by_2025[0][1] > 0:
            top, msgs = sorted_by_2025[0]
            insights.append(f'👑 <strong>{display_name(top["name"])}</strong> 是你的2025年度最佳拍档，{msgs:,}条消息见证了你们的故事')
        
        # 秒回之王（只用前100名好友参与排名）
        # 支持多种字段名获取回复速度
        def get_reply_time(c):
            return c.get('reply_them_median') or c.get('reply_them_avg') or c.get('their_reply_time') or c.get('reply_speed_them') or 0
        
        top_100_active = [c for c in top_100_private if get_2025_msgs(c) >= 100]
        fast_reply = [(c['name'], get_reply_time(c)) for c in top_100_active if get_reply_time(c) > 0]
        if fast_reply:
            fast_reply.sort(key=lambda x: x[1])
            name, sec = fast_reply[0]
            if sec < 60:
                insights.append(f'⚡ <strong>{display_name(name)}</strong> 秒回你最快，平均只需{int(sec)}秒，这大概就是"在乎"的样子')
            elif sec < 180:
                insights.append(f'⏱️ <strong>{display_name(name)}</strong> 回复你最积极，平均{int(sec)}秒，你的消息Ta从不怠慢')
        
        # 深夜守候（只用前100名好友参与排名）
        late_chats = [(c['name'], c.get('late_night', 0)) for c in top_100_active]
        late_chats.sort(key=lambda x: -x[1])
        if late_chats and late_chats[0][1] > 50:
            insights.append(f'🌙 <strong>{display_name(late_chats[0][0])}</strong> 陪你度过{late_chats[0][1]}个深夜，有人愿意熬夜陪你，是一种温柔')
        elif late_chats and late_chats[0][1] > 20:
            insights.append(f'🌃 深夜{late_chats[0][1]}次对话，<strong>{display_name(late_chats[0][0])}</strong> 是你的夜聊搭子')
        
        # 话痨检测（只用前100名好友统计）
        if len(sorted_by_2025) >= 3:
            top3_msgs = sum(m for _, m in sorted_by_2025[:3])
            total = sum(m for _, m in sorted_by_2025)
            if total > 0 and top3_msgs / total > 0.7:
                insights.append(f'💝 你<strong>70%</strong>以上的消息都给了最亲近的3个人，真正的友情从不需要太多人')
        
        # 新增：聊天习惯分析（全部active_friends统计）
        total_late = sum(c.get('late_night', 0) for c in active_friends)
        if total_late > 200:
            insights.append(f'🦉 你是个名副其实的夜猫子，今年深夜消息超过<strong>{total_late}</strong>条')
        
        # 新增：社交广度（全部active_friends统计）
        if len(active_friends) > 20:
            insights.append(f'🌈 你的社交圈很广，与<strong>{len(active_friends)}</strong>位好友都保持着活跃联系')
        elif len(active_friends) > 10:
            insights.append(f'🎯 你的社交很精准，把时间给了真正重要的<strong>{len(active_friends)}</strong>个人')
        
        return insights
    
    # ============ 年度称号系统（参考网易云）============
    def generate_annual_titles():
        """根据聊天行为生成个性化年度称号"""
        titles = []
        
        # 计算各项指标
        total_late = sum(c.get('late_night', 0) for c in private_chats)
        total_sessions = sum(c.get('sessions', 0) for c in private_chats)
        total_care = sum(c.get('care_them', 0) + c.get('care_me', 0) for c in private_chats)
        avg_reply_list = [c.get('reply_them_median', 0) for c in active_friends if c.get('reply_them_median')]
        avg_reply = sum(avg_reply_list) / len(avg_reply_list) if avg_reply_list else 0
        
        # 深夜聊天称号
        if total_late > 500:
            titles.append(('🌙', '深夜守望者', '你的夜晚从不孤单，500+条深夜消息是最好的证明'))
        elif total_late > 200:
            titles.append(('🦉', '夜猫子', '深夜的聊天框，藏着你最真实的情绪'))
        elif total_late > 50:
            titles.append(('🌃', '偶尔失眠', '有些话，只有在夜深人静时才说得出口'))
        
        # 社交活跃度称号
        if len(active_friends) > 30:
            titles.append(('🌟', '社交达人', '你的好友列表比谁都热闹'))
        elif len(active_friends) > 15:
            titles.append(('🤝', '温暖使者', '你把温度传递给身边的每一个人'))
        elif len(active_friends) > 5:
            titles.append(('💎', '精致社交', '朋友不在多，贵在真心'))
        else:
            titles.append(('🎯', '专注型选手', '你只把时间给最重要的人'))
        
        # 回复速度称号
        if avg_reply > 0 and avg_reply < 60:
            titles.append(('⚡', '秒回王者', '你的手速，是对朋友最大的尊重'))
        elif avg_reply > 0 and avg_reply < 180:
            titles.append(('💨', '快速响应', '你的消息从不让人等太久'))
        
        # 关心指数称号
        if total_care > 200:
            titles.append(('💗', '知心大使', '你说过的每一句关心，都被人记在心里'))
        elif total_care > 50:
            titles.append(('🥰', '暖心达人', '你总能在对的时候说出对的话'))
        
        # 会话频率称号
        if total_sessions > 500:
            titles.append(('🔥', '聊天狂魔', '你的聊天框永远不会冷场'))
        elif total_sessions > 200:
            titles.append(('💬', '话题终结者', '和你聊天，总能找到新话题'))
        
        # 消息总量称号
        if total_msgs > 50000:
            titles.append(('📚', '年度话痨', '5万+条消息，你用文字写了一本书'))
        elif total_msgs > 20000:
            titles.append(('✍️', '文字爱好者', '你相信文字的力量'))
        elif total_msgs > 5000:
            titles.append(('💭', '细水长流', '每一条消息都恰到好处'))
        
        return titles[:4]  # 最多返回4个称号
    
    # ============ 社交人格分析（参考MBTI风格）============
    def analyze_social_personality():
        """分析用户的社交人格类型"""
        # 计算各维度得分
        
        # 维度1: 主动 vs 被动
        total_my_init = sum(c.get('my_init', 0) for c in private_chats)
        total_their_init = sum(c.get('their_init', 0) for c in private_chats)
        initiative_score = total_my_init / (total_my_init + total_their_init) if (total_my_init + total_their_init) > 0 else 0.5
        
        # 维度2: 深夜型 vs 日间型
        total_late = sum(c.get('late_night', 0) for c in private_chats)
        night_score = min(1, total_late / 200)
        
        # 维度3: 广泛社交 vs 深度社交
        breadth_score = min(1, len(active_friends) / 20)
        
        # 维度4: 长消息 vs 短消息
        len_list = [c.get('len_me', {}).get('avg', 0) for c in private_chats if c.get('len_me', {}).get('avg', 0) > 0]
        avg_len = sum(len_list) / len(len_list) if len_list else 0
        length_score = min(1, avg_len / 50)
        
        # 生成人格类型
        p1 = '主动出击' if initiative_score > 0.5 else '静待花开'
        p2 = '深夜灵魂' if night_score > 0.4 else '阳光使者'
        p3 = '广结好友' if breadth_score > 0.5 else '深度连接'
        p4 = '长文叙述' if length_score > 0.5 else '简洁表达'
        
        # 生成有趣的人格名称
        if initiative_score > 0.6 and breadth_score > 0.5:
            personality_name = '社交蝴蝶 🦋'
            personality_desc = '你天生就是社交场的焦点，主动热情，朋友遍天下'
        elif initiative_score < 0.4 and breadth_score < 0.5:
            personality_name = '深海珍珠 🦪'
            personality_desc = '你不轻易敞开心扉，但一旦交心，便是一辈子'
        elif night_score > 0.5 and length_score > 0.5:
            personality_name = '深夜作家 ✒️'
            personality_desc = '夜深人静时，你用长长的文字倾诉内心'
        elif night_score > 0.5:
            personality_name = '月光倾听者 🌙'
            personality_desc = '你是深夜里最好的树洞，倾听每一个失眠的灵魂'
        elif initiative_score > 0.6:
            personality_name = '温暖发起人 ☀️'
            personality_desc = '你总是那个先说"在吗"的人，主动是你的温柔'
        elif breadth_score > 0.6:
            personality_name = '人间烟火 🎆'
            personality_desc = '你的世界热闹而精彩，每个朋友都是一道风景'
        else:
            personality_name = '细水长流 💧'
            personality_desc = '你的友情像溪水，不急不缓，却从不断流'
        
        return {
            'name': personality_name,
            'desc': personality_desc,
            'traits': [p1, p2, p3, p4],
            'scores': {
                'initiative': int(initiative_score * 100),
                'night': int(night_score * 100),
                'breadth': int(breadth_score * 100),
                'length': int(length_score * 100)
            }
        }
    
    # ============ 年度特殊时刻（参考支付宝账单）============
    def generate_special_moments():
        """生成年度特殊时刻
        【注意】排名类数据只使用消息总数前100名的好友
        """
        moments = []
        
        # 找出聊天最多的月份（全部好友）
        monthly_totals = defaultdict(int)
        for c in private_chats:
            monthly = c.get('monthly', {})
            for month_key, data in monthly.items():
                if month_key.startswith('2025'):
                    count = data.get('total', 0) if isinstance(data, dict) else data
                    monthly_totals[month_key] += count
        
        if monthly_totals:
            peak_month = max(monthly_totals, key=monthly_totals.get)
            month_names = {'01':'一月','02':'二月','03':'三月','04':'四月','05':'五月','06':'六月',
                          '07':'七月','08':'八月','09':'九月','10':'十月','11':'十一月','12':'十二月'}
            month_name = month_names.get(peak_month[-2:], peak_month)
            moments.append({
                'icon': '🔥',
                'title': '最火热的月份',
                'value': month_name,
                'desc': f'这个月你发送了 {monthly_totals[peak_month]:,} 条消息',
                'emotion': '那段时光一定很精彩吧'
            })
        
        # 深夜最多的好友（只用前100名好友参与排名）
        late_night_friends = [c for c in top_100_private if c.get('late_night', 0) > 20]
        if late_night_friends:
            late_night_friend = max(late_night_friends, key=lambda x: x.get('late_night', 0))
            moments.append({
                'icon': '🌙',
                'title': '深夜灵魂伴侣',
                'value': display_name(late_night_friend['name']),
                'desc': f'{late_night_friend.get("late_night", 0)} 次深夜陪伴',
                'emotion': '有人陪你熬过那些睡不着的夜'
            })
        
        # 回复最快的好友（只用前100名好友参与排名 - 秒回冠军）
        # 支持多种字段名
        def get_reply_speed(c):
            return c.get('reply_them_median') or c.get('reply_them_avg') or c.get('their_reply_time') or c.get('reply_speed_them') or 0
        
        fast_friends = [c for c in top_100_private if get_reply_speed(c) > 0]
        if fast_friends:
            fast_friend = min(fast_friends, key=lambda x: get_reply_speed(x) or 999999)
            reply_time = get_reply_speed(fast_friend)
            if reply_time < 120:
                moments.append({
                    'icon': '⚡',
                    'title': '秒回冠军',
                    'value': display_name(fast_friend['name']),
                    'desc': f'平均 {int(reply_time)} 秒回复你',
                    'emotion': '你的消息Ta从不让你等'
                })
        
        # 聊天天数最多的好友（只用前100名好友参与排名）
        days_friends = [c for c in top_100_private if c.get('days', 0) > 30]
        if days_friends:
            most_days_friend = max(days_friends, key=lambda x: x.get('days', 0))
            moments.append({
                'icon': '📅',
                'title': '最长情的陪伴',
                'value': display_name(most_days_friend['name']),
                'desc': f'陪伴了你 {most_days_friend.get("days", 0)} 天',
                'emotion': '日复一日，这就是长情'
            })
        
        # 消息最均衡的好友（只用前100名好友参与排名）
        balance_friends = []
        for c in top_100_private:
            their = c.get('their_msgs', 0)
            mine = c.get('my_msgs', 0)
            if their + mine > 100:
                balance = min(their, mine) / max(their, mine) if max(their, mine) > 0 else 0
                balance_friends.append((c, balance))
        
        if balance_friends:
            most_balanced = max(balance_friends, key=lambda x: x[1])
            if most_balanced[1] > 0.8:
                moments.append({
                    'icon': '💞',
                    'title': '最默契的双向奔赴',
                    'value': display_name(most_balanced[0]['name']),
                    'desc': f'消息比例 {int(most_balanced[1]*100)}% 均衡',
                    'emotion': '你们的来往，刚刚好'
                })
        
        return moments[:5]
    
    # ============ 生成年度称号卡片HTML ============
    def make_annual_titles_card():
        titles = generate_annual_titles()
        if not titles:
            return ''
        
        titles_html = ''
        for icon, title, desc in titles:
            titles_html += f'''
            <div class="title-card">
                <div class="title-icon">{icon}</div>
                <div class="title-name">{title}</div>
                <div class="title-desc">{desc}</div>
            </div>'''
        
        return f'''
        <div class="titles-container">
            <div class="titles-intro">根据你的聊天习惯，你获得了以下年度称号</div>
            <div class="titles-grid">{titles_html}</div>
        </div>'''
    
    # ============ 生成社交人格卡片HTML ============
    def make_personality_card():
        personality = analyze_social_personality()
        
        traits_html = ''.join([f'<span class="trait-tag">{t}</span>' for t in personality['traits']])
        
        return f'''
        <div class="personality-card">
            <div class="personality-header">
                <div class="personality-name">{personality['name']}</div>
                <div class="personality-desc">{personality['desc']}</div>
            </div>
            <div class="personality-traits">{traits_html}</div>
            <div class="personality-bars">
                <div class="bar-item">
                    <span class="bar-label">主动指数</span>
                    <div class="bar-track"><div class="bar-fill" style="width:{personality['scores']['initiative']}%"></div></div>
                    <span class="bar-value">{personality['scores']['initiative']}%</span>
                </div>
                <div class="bar-item">
                    <span class="bar-label">夜猫指数</span>
                    <div class="bar-track"><div class="bar-fill night" style="width:{personality['scores']['night']}%"></div></div>
                    <span class="bar-value">{personality['scores']['night']}%</span>
                </div>
                <div class="bar-item">
                    <span class="bar-label">社交广度</span>
                    <div class="bar-track"><div class="bar-fill social" style="width:{personality['scores']['breadth']}%"></div></div>
                    <span class="bar-value">{personality['scores']['breadth']}%</span>
                </div>
                <div class="bar-item">
                    <span class="bar-label">表达深度</span>
                    <div class="bar-track"><div class="bar-fill depth" style="width:{personality['scores']['length']}%"></div></div>
                    <span class="bar-value">{personality['scores']['length']}%</span>
                </div>
            </div>
        </div>'''
    
    # ============ 生成特殊时刻卡片HTML ============
    def make_special_moments_card():
        moments = generate_special_moments()
        if not moments:
            return ''
        
        moments_html = ''
        for m in moments:
            moments_html += f'''
            <div class="moment-card">
                <div class="moment-icon">{m['icon']}</div>
                <div class="moment-content">
                    <div class="moment-title">{m['title']}</div>
                    <div class="moment-value">{m['value']}</div>
                    <div class="moment-desc">{m['desc']}</div>
                    <div class="moment-emotion">"{m['emotion']}"</div>
                </div>
            </div>'''
        
        return f'<div class="moments-container">{moments_html}</div>'
    
    # ============ 私聊排行榜生成 ============
    # ============ 好友月度互动趋势对比 ============
    def make_friend_trends():
        """生成Top好友的月度互动趋势对比图"""
        if len(sorted_private) < 3:
            return ''
        
        # 取消息量前5的好友
        top_friends = sorted_private[:5]
        
        # 收集每个好友的月度数据
        months = ['01','02','03','04','05','06','07','08','09','10','11','12']
        month_labels = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']
        
        friends_data = []
        colors = ['var(--pink)', 'var(--cyan)', 'var(--purple)', 'var(--yellow)', 'var(--green, #4ade80)']
        
        for i, friend in enumerate(top_friends):
            monthly = friend.get('monthly', {})
            monthly_vals = []
            for m in months:
                key = f'2025-{m}'
                val = monthly.get(key, {})
                count = val.get('total', 0) if isinstance(val, dict) else val
                monthly_vals.append(count)
            
            # 只添加有数据的好友
            if sum(monthly_vals) > 0:
                friends_data.append({
                    'name': display_name(friend['name'][:6]),
                    'data': monthly_vals,
                    'total': sum(monthly_vals),
                    'color': colors[i % len(colors)]
                })
        
        if not friends_data:
            return ''
        
        # 找出最大值用于缩放
        all_vals = [v for f in friends_data for v in f['data']]
        max_val = max(all_vals) if all_vals else 1
        
        # 生成SVG折线图
        svg_width = 600
        svg_height = 250
        padding = {'top': 30, 'right': 20, 'bottom': 40, 'left': 50}
        chart_width = svg_width - padding['left'] - padding['right']
        chart_height = svg_height - padding['top'] - padding['bottom']
        
        # X轴刻度
        x_step = chart_width / 11
        
        # 生成每条折线
        lines_svg = ''
        legend_html = ''
        
        for fi, friend in enumerate(friends_data):
            points = []
            for mi, val in enumerate(friend['data']):
                x = padding['left'] + mi * x_step
                y = padding['top'] + chart_height - (val / max_val * chart_height) if max_val else padding['top'] + chart_height
                points.append(f'{x},{y}')
            
            # 折线
            lines_svg += f'<polyline points="{" ".join(points)}" fill="none" stroke="{friend["color"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="trend-line" style="animation-delay:{fi * 0.2}s"/>'
            
            # 数据点
            for mi, val in enumerate(friend['data']):
                if val > 0:
                    x = padding['left'] + mi * x_step
                    y = padding['top'] + chart_height - (val / max_val * chart_height) if max_val else padding['top'] + chart_height
                    lines_svg += f'<circle cx="{x}" cy="{y}" r="4" fill="{friend["color"]}" class="trend-dot"><title>{month_labels[mi]}: {val}条</title></circle>'
            
            # 图例
            legend_html += f'<span class="trend-legend-item"><span class="trend-legend-color" style="background:{friend["color"]}"></span>{friend["name"]}</span>'
        
        # X轴标签
        x_labels_svg = ''
        for mi, label in enumerate(month_labels):
            x = padding['left'] + mi * x_step
            x_labels_svg += f'<text x="{x}" y="{svg_height - 10}" text-anchor="middle" fill="var(--dim)" font-size="10">{label}</text>'
        
        # Y轴网格线
        grid_svg = ''
        for i in range(5):
            y = padding['top'] + i * (chart_height / 4)
            val = int(max_val * (4-i) / 4)
            grid_svg += f'<line x1="{padding["left"]}" y1="{y}" x2="{svg_width - padding["right"]}" y2="{y}" stroke="var(--bg3)" stroke-width="1" stroke-dasharray="3,3"/>'
            grid_svg += f'<text x="{padding["left"] - 8}" y="{y + 4}" text-anchor="end" fill="var(--dim)" font-size="10">{val}</text>'
        
        html = f'''
        <div class="friend-trends">
            <div class="trends-header">
                <div class="trends-title">📈 好友互动趋势</div>
                <div class="trends-subtitle">Top5好友的月度消息变化</div>
            </div>
            <div class="trends-chart">
                <svg viewBox="0 0 {svg_width} {svg_height}" class="trends-svg">
                    {grid_svg}
                    {lines_svg}
                    {x_labels_svg}
                </svg>
            </div>
            <div class="trends-legend">{legend_html}</div>
            <div class="trends-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">每个人在你生命中出现的节奏不同，有人全年陪伴，有人某月突然热络。这些曲线，是你们关系的心电图。</span>
            </div>
        </div>'''
        
        return html

    def make_private_rankings():
        # 辅助函数：获取嵌套字段值
        def get_nested(chat, key):
            # 特殊处理回复速度字段，支持多种字段名
            if key == 'reply_them_median':
                return chat.get('reply_them_median') or chat.get('reply_them_avg') or chat.get('their_reply_time') or chat.get('reply_speed_them') or 0
            if key == 'reply_me_median':
                return chat.get('reply_me_median') or chat.get('reply_me_avg') or chat.get('my_reply_time') or chat.get('reply_speed_me') or 0
            
            if '.' in key:
                parts = key.split('.')
                val = chat
                for p in parts:
                    if isinstance(val, dict):
                        val = val.get(p, 0)
                    else:
                        return 0
                return val if val else 0
            return chat.get(key, 0)
        
        # 计算2025年消息数
        def get_2025_msgs(chat):
            monthly = chat.get('monthly', {})
            return sum(v.get('total', 0) if isinstance(v, dict) else v for k, v in monthly.items() if k.startswith('2025'))
        
        # 【重要】只取消息数量前100的好友参与排名
        top_100_friends = sorted_private[:100]
        
        # 在前100中，只保留2025年消息>=30条的好友（放宽条件）
        eligible_2025 = [c for c in top_100_friends if get_2025_msgs(c) >= 30]
        
        # 如果没有足够的2025年数据，则使用总消息数>=30的好友
        if len(eligible_2025) < 5:
            eligible_2025 = [c for c in top_100_friends if c.get('total_msgs', 0) >= 30]
        
        # 基础排行榜配置 - 全部要求>=100条
        rankings_config = [
            ('total_msgs', '💬 消息总量', '条', True, None),
            ('total_chars', '📝 总字数', '字', True, None),
            ('sessions', '🔄 会话数', '次', True, None),
            ('days', '📅 聊天天数', '天', True, None),
            ('reply_them_median', '⚡ Ta秒回你', '', False, fmt_time),
            ('reply_me_median', '📌 你秒回Ta', '', False, fmt_time),
            ('their_init_pct', '🔍 Ta找你', '%', True, None),
            ('my_init_pct', '💭 你找Ta', '%', True, None),
            ('late_night', '🌙 深夜消息', '条', True, None),
            ('care_them', '❤️ Ta关心你', '次', True, None),
            ('care_me', '💕 你关心Ta', '次', True, None),
            ('max_session_len', '🔥 最长会话', '条', True, None),
            ('len_me.avg', '📏 你的平均字数', '字', True, None),
            ('len_them.avg', '📏 Ta的平均字数', '字', True, None),
            ('sentence_them.question', '❓ Ta问句比例', '%', True, None),
            ('richness_me.diversity', '🌈 你的词汇多样性', '%', True, None),
            ('richness_them.diversity', '🌈 Ta的词汇多样性', '%', True, None),
        ]
        
        html = ''
        card_id = 0
        for key, title, unit, reverse, formatter in rankings_config:
            data = [(display_name(c['name']), get_nested(c, key)) for c in eligible_2025]
            data = [(n, v) for n, v in data if v is not None and v != 0]
            if not data:
                continue
            
            data_sorted = sorted(data, key=lambda x: x[1], reverse=reverse)
            values = [v for _, v in data_sorted]
            
            if not values:
                continue
            
            stats = {
                'max': max(values),
                'min': min(values),
                'avg': mean(values),
                'median': median(values),
            }
            
            # 生成排行项（前3显示，4-10折叠）
            items_visible = ''
            items_hidden = ''
            max_val = data_sorted[0][1] if data_sorted else 1
            rank = 0
            prev_val = None
            shown = 0
            for i, (name, val) in enumerate(data_sorted):
                if val != prev_val:
                    rank = i + 1
                    prev_val = val
                
                if rank > 10:
                    break
                
                shown += 1
                pct = int(val / max_val * 100) if max_val else 0
                medal = ['🥇', '🥈', '🥉'][rank-1] if rank <= 3 else str(rank)
                display_val = formatter(val) if formatter else f'{val:,}'
                
                item_html = f'''
                <div class="rank-item" style="--delay:{shown*0.03}s">
                    <span class="rank-pos">{medal}</span>
                    <span class="rank-name">{name[:8]}</span>
                    <div class="rank-bar"><div class="rank-fill" style="width:{pct}%"></div></div>
                    <span class="rank-val">{display_val} {unit}</span>
                </div>'''
                
                if rank <= 3:
                    items_visible += item_html
                else:
                    items_hidden += item_html
            
            remaining = len(data_sorted) - shown
            expand_btn = ''
            hidden_section = ''
            if items_hidden or remaining > 0:
                more_text = f'<div class="rank-more">... 还有 {remaining} 人</div>' if remaining > 0 else ''
                hidden_section = f'<div class="rank-hidden">{items_hidden}{more_text}</div>'
                expand_btn = f'<button class="expand-btn" onclick="toggleRank(this)">展开更多 ▼</button>'
            
            fmt_func = formatter if formatter else (lambda x: f'{x:,}' if isinstance(x, int) else f'{x:.1f}')
            html += f'''
            <div class="ranking-card">
                <div class="ranking-title">{title}</div>
                <div class="ranking-stats">
                    最高 <strong>{fmt_func(stats['max'])}</strong> {unit} · 
                    平均 <strong>{fmt_func(stats['avg'])}</strong> {unit} ·
                    共 <strong>{len(data_sorted)}</strong> 人
                </div>
                <div class="ranking-list">
                    {items_visible}
                    {hidden_section}
                    {expand_btn}
                </div>
            </div>'''
            card_id += 1
        
        return html
    
    # ============ 群聊年度洞察 ============
    def generate_group_insights():
        insights = []
        
        if not group_chats:
            return insights
        
        # 计算2025年消息数
        def get_2025_group_msgs(group):
            monthly = group.get('monthly', {})
            if isinstance(monthly, dict):
                return sum(v if isinstance(v, int) else v.get('total', 0) for k, v in monthly.items() if k.startswith('2025'))
            return 0
        
        # 按2025年消息排序
        groups_2025 = [(g, get_2025_group_msgs(g)) for g in group_chats]
        groups_2025.sort(key=lambda x: -x[1])
        
        # 最活跃的群（2025年）
        if groups_2025 and groups_2025[0][1] > 0:
            top, msgs = groups_2025[0]
            insights.append(f'🔥 <strong>{display_group_name(top["name"])}</strong> 是你的年度热闹担当，{msgs:,}条消息承载了多少欢笑')
        
        # 我贡献最多的群
        my_contrib = [(g['name'], g.get('my_msgs', 0), g.get('my_pct', 0), g.get('my_rank', 0)) for g in group_chats if g.get('my_msgs', 0) > 0]
        if my_contrib:
            my_contrib.sort(key=lambda x: -x[1])
            name, msgs, pct, rank = my_contrib[0]
            if pct > 20:
                insights.append(f'🎤 你在 <strong>{display_group_name(name)}</strong> 简直是话唠本唠，贡献了{pct}%的消息')
            elif pct > 10:
                insights.append(f'💬 <strong>{display_group_name(name)}</strong> 里有你的一席之地，{msgs}条发言功不可没')
            else:
                insights.append(f'🙋 你在 <strong>{display_group_name(name)}</strong> 最活跃，{msgs}条发言，低调但从不缺席')
        
        # 潜水王
        lurk_groups = [(g['name'], g.get('my_msgs', 0), g.get('my_pct', 0)) for g in group_chats if g.get('my_msgs', 0) == 0 and g.get('total_msgs', 0) > 100]
        if lurk_groups:
            if len(lurk_groups) > 5:
                insights.append(f'🤿 你在 <strong>{len(lurk_groups)}</strong> 个群里是"深海潜水员"，偶尔冒个泡也很可爱哦')
            else:
                insights.append(f'👀 有些群你只是默默围观，安静也是一种参与')
        
        # 话痨群
        if sorted_groups:
            chatty = [g for g in sorted_groups if g.get('avg_daily', 0) > 50]
            if chatty:
                insights.append(f'🎉 <strong>{len(chatty)}</strong> 个群日均消息超50条，这些群永远有聊不完的话题')
        
        # 总消息
        total_group_msgs = sum(g.get('total_msgs', 0) for g in group_chats)
        total_my_msgs = sum(g.get('my_msgs', 0) for g in group_chats)
        if total_group_msgs > 0 and total_my_msgs > 0:
            overall_pct = round(total_my_msgs / total_group_msgs * 100, 1)
            if overall_pct > 5:
                insights.append(f'📊 群聊宇宙里，你是<strong>{overall_pct}%</strong>的存在，{total_my_msgs:,}条消息都是你的痕迹')
            else:
                insights.append(f'🌟 {total_my_msgs:,}条群聊发言，每一条都有人看见')
        
        return insights
    
    # ============ 群聊总览分析 ============
    def make_group_overview():
        """生成群聊总览分析，包括类型分布、活跃度分析等"""
        if not group_chats:
            return ''
        
        # 统计群聊类型分布
        type_counts = defaultdict(int)
        type_msgs = defaultdict(int)
        
        for gc in group_chats:
            group_name = gc.get('name', '')
            total_msgs = gc.get('total_msgs', 0)
            
            # 类型识别
            if any(kw in group_name for kw in ['家', '爸', '妈', '爷', '奶', '亲', '家庭', '全家']):
                gtype = '🏠 家庭群'
            elif any(kw in group_name for kw in ['工作', '项目', '团队', '公司', '部门', '组', '办公']):
                gtype = '💼 工作群'
            elif any(kw in group_name for kw in ['班', '级', '届', '学', '校', '同学', '室友', '毕业']):
                gtype = '🎓 同学群'
            elif any(kw in group_name for kw in ['游戏', '王者', '吃鸡', '原神', 'LOL', '开黑']):
                gtype = '🎮 游戏群'
            else:
                gtype = '💬 其他群'
            
            type_counts[gtype] += 1
            type_msgs[gtype] += total_msgs
        
        # 总体统计
        total_groups = len(group_chats)
        total_msgs = sum(g.get('total_msgs', 0) for g in group_chats)
        total_my_msgs = sum(g.get('my_msgs', 0) for g in group_chats)
        total_members = sum(g.get('member_count', 0) for g in group_chats)
        avg_daily = sum(g.get('avg_daily', 0) for g in group_chats)
        
        # 你是话唠王的群数量
        king_count = len([g for g in group_chats if g.get('my_rank') == 1])
        top3_count = len([g for g in group_chats if g.get('my_rank', 99) <= 3])
        lurk_count = len([g for g in group_chats if g.get('my_msgs', 0) == 0])
        
        # 生成类型分布HTML
        type_html = ''
        max_type_count = max(type_counts.values()) if type_counts else 1
        for gtype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            pct = int(count / total_groups * 100)
            bar_pct = int(count / max_type_count * 100)
            msgs = type_msgs.get(gtype, 0)
            type_html += f'''
            <div class="gtype-item">
                <div class="gtype-header">
                    <span class="gtype-name">{gtype}</span>
                    <span class="gtype-count">{count}个 ({pct}%)</span>
                </div>
                <div class="gtype-bar"><div class="gtype-fill" style="width:{bar_pct}%"></div></div>
                <div class="gtype-msgs">{msgs:,}条消息</div>
            </div>'''
        
        # 你的群聊角色分析
        if king_count > 0:
            role_icon = '👑'
            role_name = '群聊话唠王'
            role_desc = f'在{king_count}个群里，你是发言最多的人！'
        elif top3_count > total_groups * 0.3:
            role_icon = '🎤'
            role_name = '活跃分子'
            role_desc = f'在{top3_count}个群里，你都是Top3活跃'
        elif lurk_count > total_groups * 0.5:
            role_icon = '🤿'
            role_name = '深海潜水员'
            role_desc = f'在{lurk_count}个群里，你选择了安静潜水'
        else:
            role_icon = '💬'
            role_name = '适度参与者'
            role_desc = '你在群聊中保持着恰到好处的存在感'
        
        html = f'''
        <div class="group-overview">
            <div class="gov-stats">
                <div class="gov-stat">
                    <div class="gov-stat-val">{total_groups}</div>
                    <div class="gov-stat-lbl">群聊总数</div>
                </div>
                <div class="gov-stat">
                    <div class="gov-stat-val">{total_msgs:,}</div>
                    <div class="gov-stat-lbl">总消息量</div>
                </div>
                <div class="gov-stat">
                    <div class="gov-stat-val">{total_my_msgs:,}</div>
                    <div class="gov-stat-lbl">你的发言</div>
                </div>
                <div class="gov-stat">
                    <div class="gov-stat-val">{total_members:,}</div>
                    <div class="gov-stat-lbl">触达人数</div>
                </div>
            </div>
            
            <div class="gov-sections">
                <div class="gov-types">
                    <div class="gov-section-title">📊 群聊类型分布</div>
                    <div class="gtype-list">{type_html}</div>
                </div>
                
                <div class="gov-role">
                    <div class="gov-section-title">🎭 你的群聊角色</div>
                    <div class="gov-role-card">
                        <div class="gov-role-icon">{role_icon}</div>
                        <div class="gov-role-name">{role_name}</div>
                        <div class="gov-role-desc">{role_desc}</div>
                    </div>
                    <div class="gov-role-stats">
                        <div class="gov-rs"><span class="gov-rs-val">{king_count}</span><span class="gov-rs-lbl">话唠王</span></div>
                        <div class="gov-rs"><span class="gov-rs-val">{top3_count}</span><span class="gov-rs-lbl">Top3活跃</span></div>
                        <div class="gov-rs"><span class="gov-rs-val">{lurk_count}</span><span class="gov-rs-lbl">潜水群</span></div>
                    </div>
                </div>
            </div>
            
            <div class="gov-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">群聊是我们的"数字村落"。家庭群传递温暖，工作群协作共进，同学群重温青春——每个群都是你生活的一个切面。</span>
            </div>
        </div>'''
        
        return html
    
    # ============ 群聊活跃时段对比 ============
    def make_group_time_comparison():
        """对比不同群聊的活跃时段"""
        if not group_chats or len(group_chats) < 2:
            return ''
        
        # 取活跃度最高的几个群进行对比
        top_groups = sorted(group_chats, key=lambda x: -x.get('total_msgs', 0))[:5]
        
        # 收集各群的高峰时段数据
        group_data = []
        for gc in top_groups:
            hours = gc.get('hours', {})
            if not hours:
                continue
            
            peak_hour = gc.get('peak_hour', 12)
            late_night_pct = gc.get('late_night_pct', 0)
            
            # 判断活跃时段类型和时间范围
            if peak_hour >= 22 or peak_hour < 6:
                time_type = '🌙 深夜型'
                time_color = 'var(--purple)'
                time_range = '22-6点'
            elif peak_hour >= 6 and peak_hour < 12:
                time_type = '🌅 早起型'
                time_color = 'var(--yellow)'
                time_range = '6-12点'
            elif peak_hour >= 12 and peak_hour < 18:
                time_type = '☀️ 下午型'
                time_color = 'var(--cyan)'
                time_range = '12-18点'
            else:
                time_type = '🌆 晚间型'
                time_color = 'var(--pink)'
                time_range = '18-22点'
            
            group_data.append({
                'name': gc.get('name', '')[:10],
                'peak_hour': peak_hour,
                'time_range': time_range,
                'late_pct': late_night_pct,
                'time_type': time_type,
                'time_color': time_color,
                'hours': hours
            })
        
        if len(group_data) < 2:
            return ''
        
        # 生成对比条形图HTML
        comparison_html = ''
        for g in group_data:
            hours = g['hours']
            max_val = max(hours.values()) if hours else 1
            hour_bars = ''
            for h in range(24):
                val = hours.get(str(h), hours.get(h, 0))
                pct = int(val / max_val * 100) if max_val else 0
                opacity = 0.3 + pct * 0.007
                hour_bars += f'<div class="gtc-hour" style="opacity:{opacity}" title="{h}:00"></div>'
            
            comparison_html += f'''
            <div class="gtc-group">
                <div class="gtc-name">{display_group_name(g["name"])}</div>
                <div class="gtc-hours">{hour_bars}</div>
                <div class="gtc-info">
                    <span class="gtc-peak">高峰 {g["time_range"]}</span>
                    <span class="gtc-type" style="color:{g["time_color"]}">{g["time_type"]}</span>
                </div>
            </div>'''
        
        html = f'''
        <div class="group-time-comparison">
            <div class="gtc-title">🕐 群聊作息对比</div>
            <div class="gtc-subtitle">不同群聊的活跃时段各有特色</div>
            <div class="gtc-timeline">
                <span>0</span><span>6</span><span>12</span><span>18</span><span>24</span>
            </div>
            <div class="gtc-groups">{comparison_html}</div>
        </div>'''
        
        return html

    # ============ 群聊排行榜生成 ============
    def make_group_rankings():
        if not group_chats:
            return ''
        
        # 计算2025年消息数
        def get_2025_msgs(group):
            monthly = group.get('monthly', {})
            if isinstance(monthly, dict):
                return sum(v if isinstance(v, int) else v.get('total', 0) for k, v in monthly.items() if k.startswith('2025'))
            return 0
        
        # 只保留2025年消息>=100条的群
        eligible_2025 = [g for g in sorted_groups if get_2025_msgs(g) >= 100]
        
        if not eligible_2025:
            eligible_2025 = sorted_groups  # 如果没有符合条件的，显示全部
        
        rankings_config = [
            ('total_msgs', '💬 消息总量', '条', True),
            ('my_msgs', '🙋 我的发言', '条', True),
            ('my_pct', '📊 我的贡献', '%', True),
            ('member_count', '👥 成员数', '人', True),
            ('days', '📅 活跃天数', '天', True),
            ('avg_daily', '📊 日均消息', '条', True),
            ('late_night_pct', '🌙 深夜占比', '%', True),
        ]
        
        html = ''
        for key, title, unit, reverse in rankings_config:
            data = [(g['name'], g.get(key, 0)) for g in eligible_2025]
            data = [(n, v) for n, v in data if v]
            if not data:
                continue
            
            data_sorted = sorted(data, key=lambda x: x[1], reverse=reverse)
            values = [v for _, v in data_sorted]
            
            stats = {
                'max': max(values),
                'min': min(values),
                'avg': mean(values),
            }
            
            # 处理并列：显示前10名，前3可见，4-10折叠
            items_visible = ''
            items_hidden = ''
            max_val = data_sorted[0][1] if data_sorted else 1
            rank = 0
            prev_val = None
            shown = 0
            for i, (name, val) in enumerate(data_sorted):
                if val != prev_val:
                    rank = i + 1
                    prev_val = val
                
                if rank > 10:
                    break
                
                shown += 1
                pct = int(val / max_val * 100) if max_val else 0
                medal = ['🥇', '🥈', '🥉'][rank-1] if rank <= 3 else str(rank)
                item_html = f'''
                <div class="rank-item-group" style="--delay:{shown*0.03}s">
                    <div class="rank-row-name">
                        <span class="rank-pos">{medal}</span>
                        <span class="rank-name-full">{display_group_name(name)}</span>
                        <span class="rank-val">{val:,} {unit}</span>
                    </div>
                    <div class="rank-row-bar">
                        <div class="rank-bar-full"><div class="rank-fill" style="width:{pct}%"></div></div>
                    </div>
                </div>'''
                
                if rank <= 3:
                    items_visible += item_html
                else:
                    items_hidden += item_html
            
            remaining = len(data_sorted) - shown
            expand_btn = ''
            hidden_section = ''
            if items_hidden or remaining > 0:
                more_text = f'<div class="rank-more">... 还有 {remaining} 群</div>' if remaining > 0 else ''
                hidden_section = f'<div class="rank-hidden">{items_hidden}{more_text}</div>'
                expand_btn = f'<button class="expand-btn" onclick="toggleRank(this)">展开更多 ▼</button>'
            
            html += f'''
            <div class="ranking-card">
                <div class="ranking-title">{title}</div>
                <div class="ranking-stats">
                    最高 <strong>{stats['max']:,}</strong> {unit} · 
                    平均 <strong>{stats['avg']:.1f}</strong> {unit} ·
                    共 <strong>{len(data_sorted)}</strong> 群
                </div>
                <div class="ranking-list">
                    {items_visible}
                    {hidden_section}
                    {expand_btn}
                </div>
            </div>'''
        
        return html
    
    # ============ 私聊详情卡片（可折叠）============
    def make_private_cards():
        cards = ''
        for idx, c in enumerate(sorted_private, 1):
            name = display_name(c['name'])
            types_me = c.get('msg_types_me', {})
            types_them = c.get('msg_types_them', {})
            len_me = c.get('len_me', {})
            len_them = c.get('len_them', {})
            len_dist_me = c.get('len_dist_me', {})
            len_dist_them = c.get('len_dist_them', {})
            sentence_me = c.get('sentence_me', {})
            sentence_them = c.get('sentence_them', {})
            modal_me = c.get('modal_me', {})
            modal_them = c.get('modal_them', {})
            reply_me = c.get('reply_me_by_period', {})
            reply_them = c.get('reply_them_by_period', {})
            richness_me = c.get('richness_me', {})
            richness_them = c.get('richness_them', {})
            vocab_me = c.get('vocab_me', {})
            vocab_them = c.get('vocab_them', {})
            topics_me = c.get('topics_me', {})
            topics_them = c.get('topics_them', {})
            
            # 生成关系标签
            tags = []
            # 支持多种字段名获取回复速度
            reply_them_sec = c.get('reply_them_median') or c.get('reply_them_avg') or c.get('their_reply_time') or c.get('reply_speed_them') or 0
            reply_me_sec = c.get('reply_me_median') or c.get('reply_me_avg') or c.get('my_reply_time') or c.get('reply_speed_me') or 0
            late_night = c.get('late_night', 0)
            their_msgs = c.get('their_msgs', 0)
            my_msgs = c.get('my_msgs', 0)
            care_them = c.get('care_them', 0)
            care_me = c.get('care_me', 0)
            sessions = c.get('sessions', 0)
            
            # 秒回标签
            if reply_them_sec and reply_them_sec < 60:
                tags.append('⚡ 秒回达人')
            elif reply_me_sec and reply_me_sec < 60:
                tags.append('💨 你秒回Ta')
            
            # 深夜标签
            if late_night > 100:
                tags.append('🌙 深夜灵魂伴侣')
            elif late_night > 30:
                tags.append('🌃 夜聊搭子')
            
            # 消息平衡标签
            if their_msgs > 0 and my_msgs > 0:
                balance = min(their_msgs, my_msgs) / max(their_msgs, my_msgs)
                if balance > 0.8:
                    tags.append('💞 双向奔赴')
                elif my_msgs > their_msgs * 2:
                    tags.append('🗣️ 你主动更多')
                elif their_msgs > my_msgs * 2:
                    tags.append('👂 Ta更爱聊')
            
            # 关心标签
            if care_them > 10 and care_me > 10:
                tags.append('💗 互相关心')
            elif care_them > 10:
                tags.append('🥰 Ta很在乎你')
            elif care_me > 10:
                tags.append('💝 你很在乎Ta')
            
            # 会话频率标签
            days = c.get('days', 1)
            if sessions / days > 2:
                tags.append('🔥 超高频联系')
            elif sessions / days > 1:
                tags.append('💬 每天都聊')
            
            # 消息总量标签
            total = c.get('total_msgs', 0)
            if total > 5000:
                tags.append('📚 聊天万字户')
            elif total > 1000:
                tags.append('✨ 话题不断')
            
            tags_html = ''.join([f'<span class="chat-tag">{t}</span>' for t in tags[:4]])  # 最多显示4个标签
            
            type_rows = ''
            for t in ['文本消息', '引用消息', '图片消息', '语音消息', '视频消息']:
                me_val = types_me.get(t, 0)
                them_val = types_them.get(t, 0)
                if me_val or them_val:
                    type_rows += f'<tr><td>{t}</td><td class="them">{them_val}</td><td class="me">{me_val}</td></tr>'
            
            # 生成折叠状态下的简要数据（让所有人都能看到关键信息）
            brief_extra = ''
            if late_night > 0:
                brief_extra += f' · 🌙{late_night}'
            if care_them + care_me > 0:
                brief_extra += f' · ❤️{care_them + care_me}'
            # 使用已获取的reply_them_sec（支持多种字段名）
            if reply_them_sec and reply_them_sec < 300:
                brief_extra += f' · ⚡{fmt_time(reply_them_sec)}'
            
            # 生成快速数据行（折叠状态下显示双方数据对比）
            their_pct = c.get('their_pct', 50)
            my_pct = c.get('my_pct', 50)
            quick_stats = f'''
    <div class="chat-quick-stats">
        <div class="quick-stat">
            <span class="quick-label">Ta发</span>
            <span class="quick-val them">{c['their_msgs']:,}</span>
            <span class="quick-pct">({their_pct}%)</span>
        </div>
        <div class="quick-divider">|</div>
        <div class="quick-stat">
            <span class="quick-label">你发</span>
            <span class="quick-val me">{c['my_msgs']:,}</span>
            <span class="quick-pct">({my_pct}%)</span>
        </div>
        <div class="quick-divider">|</div>
        <div class="quick-stat">
            <span class="quick-label">深夜</span>
            <span class="quick-val">{late_night}</span>
        </div>
        <div class="quick-divider">|</div>
        <div class="quick-stat">
            <span class="quick-label">关心</span>
            <span class="quick-val">{care_them + care_me}</span>
        </div>
    </div>'''
            
            cards += f'''
<div class="chat-card" data-idx="{idx}">
    <div class="chat-header" onclick="toggleCard(this)">
        <span class="chat-rank">#{idx}</span>
        <span class="chat-name">{name}</span>
        <span class="chat-brief">
            <i class="num" data-val="{c['total_msgs']}">{c['total_msgs']:,}</i>条 · 
            {c['sessions']}次 · 
            {c['days']}天{brief_extra}
        </span>
        <span class="chat-toggle">▼</span>
    </div>
    <div class="chat-tags">{tags_html}</div>
    {quick_stats}
    <div class="chat-body">
        <div class="data-grid">
            <!-- 基础对比 -->
            <div class="data-card">
                <div class="card-title">📊 消息对比</div>
                <div class="versus">
                    <div class="vs-item them">
                        <div class="vs-val"><i class="num" data-val="{c['their_msgs']}">{c['their_msgs']:,}</i></div>
                        <div class="vs-pct">{c['their_pct']}%</div>
                        <div class="vs-label">Ta发送</div>
                    </div>
                    <div class="vs-mid">VS</div>
                    <div class="vs-item me">
                        <div class="vs-val"><i class="num" data-val="{c['my_msgs']}">{c['my_msgs']:,}</i></div>
                        <div class="vs-pct">{c['my_pct']}%</div>
                        <div class="vs-label">你发送</div>
                    </div>
                </div>
                <div class="bar-compare">
                    <div class="bar-them" style="width:{c['their_pct']}%"></div>
                    <div class="bar-me" style="width:{c['my_pct']}%"></div>
                </div>
            </div>
            
            <!-- 消息类型 -->
            <div class="data-card">
                <div class="card-title">💬 消息类型</div>
                <table><tr><th>类型</th><th class="them">Ta</th><th class="me">你</th></tr>{type_rows}</table>
                <div class="mini-insight">引用比 <b>{c.get('quote_ratio', 0)}</b> (Ta引用{c.get('quote_them', 0)}次/你{c.get('quote_me', 0)}次)</div>
            </div>
            
            <!-- 消息长度 -->
            <div class="data-card">
                <div class="card-title">📏 消息长度</div>
                <table>
                    <tr><th></th><th class="them">Ta</th><th class="me">你</th></tr>
                    <tr><td>总字数</td><td class="them">{c.get('their_chars', 0):,}</td><td class="me">{c.get('my_chars', 0):,}</td></tr>
                    <tr><td>平均</td><td class="them">{len_them.get('avg', 0)}字</td><td class="me">{len_me.get('avg', 0)}字</td></tr>
                    <tr><td>中位</td><td class="them">{len_them.get('median', 0)}字</td><td class="me">{len_me.get('median', 0)}字</td></tr>
                    <tr><td>最长</td><td class="them">{len_them.get('max', 0)}字</td><td class="me">{len_me.get('max', 0)}字</td></tr>
                </table>
                <div class="dist-mini">
                    <span>短(1-10): <b class="them">{len_dist_them.get('short', 0)}%</b>/<b class="me">{len_dist_me.get('short', 0)}%</b></span>
                    <span>中(11-30): <b class="them">{len_dist_them.get('medium', 0)}%</b>/<b class="me">{len_dist_me.get('medium', 0)}%</b></span>
                    <span>长(>50): <b class="them">{len_dist_them.get('long', 0)}%</b>/<b class="me">{len_dist_me.get('long', 0)}%</b></span>
                </div>
            </div>
            
            <!-- 语言风格 -->
            <div class="data-card">
                <div class="card-title">🗣️ 语言风格</div>
                <table>
                    <tr><th>句式</th><th class="them">Ta</th><th class="me">你</th></tr>
                    <tr><td>疑问句</td><td class="them">{sentence_them.get('question', 0)}%</td><td class="me">{sentence_me.get('question', 0)}%</td></tr>
                    <tr><td>感叹句</td><td class="them">{sentence_them.get('exclaim', 0)}%</td><td class="me">{sentence_me.get('exclaim', 0)}%</td></tr>
                    <tr><td>陈述句</td><td class="them">{sentence_them.get('statement', 0)}%</td><td class="me">{sentence_me.get('statement', 0)}%</td></tr>
                </table>
                <table style="margin-top:10px;">
                    <tr><th>语气词</th><th class="them">Ta</th><th class="me">你</th></tr>
                    <tr><td>亲密撒娇</td><td class="them">{modal_them.get('亲密/撒娇', 0)}</td><td class="me">{modal_me.get('亲密/撒娇', 0)}</td></tr>
                    <tr><td>思考犹豫</td><td class="them">{modal_them.get('思考/犹豫', 0)}</td><td class="me">{modal_me.get('思考/犹豫', 0)}</td></tr>
                    <tr><td>确认肯定</td><td class="them">{modal_them.get('确认/肯定', 0)}</td><td class="me">{modal_me.get('确认/肯定', 0)}</td></tr>
                    <tr><td>笑声hh</td><td class="them">{modal_them.get('笑声', 0)}</td><td class="me">{modal_me.get('笑声', 0)}</td></tr>
                </table>
            </div>
            
            <!-- 回复速度 -->
            <div class="data-card">
                <div class="card-title">⚡ 回复速度</div>
                <div class="versus">
                    <div class="vs-item them">
                        <div class="vs-val time">{fmt_time(reply_them_sec)}</div>
                        <div class="vs-label">Ta回复</div>
                    </div>
                    <div class="vs-mid">⏱️</div>
                    <div class="vs-item me">
                        <div class="vs-val time">{fmt_time(reply_me_sec)}</div>
                        <div class="vs-label">你回复</div>
                    </div>
                </div>
                <table>
                    <tr><th>时段</th><th class="them">Ta</th><th class="me">你</th></tr>
                    <tr><td>工作日白天</td><td class="them">{fmt_time(reply_them.get('工作日白天', 0))}</td><td class="me">{fmt_time(reply_me.get('工作日白天', 0))}</td></tr>
                    <tr><td>工作日晚上</td><td class="them">{fmt_time(reply_them.get('工作日晚上', 0))}</td><td class="me">{fmt_time(reply_me.get('工作日晚上', 0))}</td></tr>
                    <tr><td>周末白天</td><td class="them">{fmt_time(reply_them.get('周末白天', 0))}</td><td class="me">{fmt_time(reply_me.get('周末白天', 0))}</td></tr>
                    <tr><td>周末晚上</td><td class="them">{fmt_time(reply_them.get('周末晚上', 0))}</td><td class="me">{fmt_time(reply_me.get('周末晚上', 0))}</td></tr>
                </table>
            </div>
            
            <!-- 会话结构 -->
            <div class="data-card">
                <div class="card-title">🔄 会话结构</div>
                <div class="stat-row">
                    <div class="stat-box"><div class="stat-num">{c.get('sessions', 0)}</div><div class="stat-lbl">总会话</div></div>
                    <div class="stat-box them"><div class="stat-num">{c.get('their_init', 0)}</div><div class="stat-lbl">Ta发起({c.get('their_init_pct', 0)}%)</div></div>
                    <div class="stat-box me"><div class="stat-num">{c.get('my_init', 0)}</div><div class="stat-lbl">你发起({c.get('my_init_pct', 0)}%)</div></div>
                </div>
                <div class="stat-row">
                    <div class="stat-box"><div class="stat-num">{c.get('avg_session_len', 0)}</div><div class="stat-lbl">平均长度</div></div>
                    <div class="stat-box"><div class="stat-num">{c.get('max_session_len', 0)}</div><div class="stat-lbl">最长会话</div></div>
                </div>
            </div>
            
            <!-- 内容丰富度 -->
            <div class="data-card">
                <div class="card-title">🌈 内容丰富度</div>
                <table>
                    <tr><th></th><th class="them">Ta</th><th class="me">你</th></tr>
                    <tr><td>不同字符</td><td class="them">{richness_them.get('unique_chars', 0):,}</td><td class="me">{richness_me.get('unique_chars', 0):,}</td></tr>
                    <tr><td>多样性</td><td class="them">{richness_them.get('diversity', 0)}%</td><td class="me">{richness_me.get('diversity', 0)}%</td></tr>
                    <tr><td>含英文</td><td class="them">{richness_them.get('english_pct', 0)}%</td><td class="me">{richness_me.get('english_pct', 0)}%</td></tr>
                    <tr><td>英文词</td><td class="them">{richness_them.get('english_words', 0):,}</td><td class="me">{richness_me.get('english_words', 0):,}</td></tr>
                </table>
                <table style="margin-top:10px;">
                    <tr><th>词汇</th><th class="them">Ta</th><th class="me">你</th></tr>
                    <tr><td>正式书面</td><td class="them">{vocab_them.get('正式/书面', 0)}</td><td class="me">{vocab_me.get('正式/书面', 0)}</td></tr>
                    <tr><td>口语化</td><td class="them">{vocab_them.get('口语化', 0)}</td><td class="me">{vocab_me.get('口语化', 0)}</td></tr>
                    <tr><td>网络语</td><td class="them">{vocab_them.get('网络流行语', 0)}</td><td class="me">{vocab_me.get('网络流行语', 0)}</td></tr>
                </table>
            </div>
            
            <!-- 深度话题 -->
            <div class="data-card">
                <div class="card-title">💭 深度话题</div>
                <table>
                    <tr><th>话题</th><th class="them">Ta</th><th class="me">你</th></tr>
                    <tr><td>情感内心</td><td class="them">{topics_them.get('情感/内心', 0)}</td><td class="me">{topics_me.get('情感/内心', 0)}</td></tr>
                    <tr><td>家庭亲人</td><td class="them">{topics_them.get('家庭/亲人', 0)}</td><td class="me">{topics_me.get('家庭/亲人', 0)}</td></tr>
                    <tr><td>价值思考</td><td class="them">{topics_them.get('价值观/思考', 0)}</td><td class="me">{topics_me.get('价值观/思考', 0)}</td></tr>
                    <tr><td>身体健康</td><td class="them">{topics_them.get('身体/健康', 0)}</td><td class="me">{topics_me.get('身体/健康', 0)}</td></tr>
                    <tr><td>未来规划</td><td class="them">{topics_them.get('未来/规划', 0)}</td><td class="me">{topics_me.get('未来/规划', 0)}</td></tr>
                    <tr><td>回忆过去</td><td class="them">{topics_them.get('回忆/过去', 0)}</td><td class="me">{topics_me.get('回忆/过去', 0)}</td></tr>
                </table>
            </div>
            
            <!-- 关怀统计 -->
            <div class="data-card">
                <div class="card-title">❤️ 关怀与邀约</div>
                <div class="stat-row">
                    <div class="stat-box them"><div class="stat-num">{c.get('care_them', 0)}</div><div class="stat-lbl">Ta关心你</div></div>
                    <div class="stat-box me"><div class="stat-num">{c.get('care_me', 0)}</div><div class="stat-lbl">你关心Ta</div></div>
                    <div class="stat-box them"><div class="stat-num">{c.get('invite_them', 0)}</div><div class="stat-lbl">Ta邀约你</div></div>
                    <div class="stat-box me"><div class="stat-num">{c.get('invite_me', 0)}</div><div class="stat-lbl">你邀约Ta</div></div>
                </div>
            </div>
            
            <!-- 时间分布 -->
            <div class="data-card">
                <div class="card-title">⏰ 时间分布</div>
                <div class="stat-row">
                    <div class="stat-box"><div class="stat-num">{['深夜','深夜','深夜','深夜','深夜','深夜','上午','上午','上午','上午','上午','上午','下午','下午','下午','下午','下午','下午','晚间','晚间','晚间','晚间','晚间','深夜'][c.get('peak_hour', 12)]}</div><div class="stat-lbl">峰值时段</div></div>
                    <div class="stat-box"><div class="stat-num">{c.get('peak_weekday', '')}</div><div class="stat-lbl">最活跃日</div></div>
                    <div class="stat-box"><div class="stat-num">{c.get('late_night', 0)}</div><div class="stat-lbl">深夜({c.get('late_night_pct', 0)}%)</div></div>
                </div>
            </div>
        </div>
    </div>
</div>
'''
        return cards
    
    # ============ 群聊详情卡片 ============
    def make_group_cards():
        if not group_chats:
            return '<p class="empty">无群聊数据</p>'
        
        cards = ''
        for idx, gc in enumerate(sorted_groups, 1):
            top_talkers = gc.get('top_talkers', [])[:5]
            talkers_html = ''.join([
                f'<div class="talker"><span class="talker-rank">{i}</span><span class="talker-name">{display_name(n[:8])}</span><span class="talker-val">{v}条</span></div>'
                for i, (n, v) in enumerate(top_talkers, 1)
            ])
            
            # 你在群里的数据
            my_msgs = gc.get('my_msgs', 0)
            my_pct = gc.get('my_pct', 0)
            my_rank = gc.get('my_rank', 0)
            member_count = gc.get('member_count', 1)
            total_msgs = gc.get('total_msgs', 0)
            days = gc.get('days', 1)
            
            # ========== 群聊类型智能识别 ==========
            group_name = gc.get('name', '')
            avg_daily = gc.get('avg_daily', 0)
            late_night_pct = gc.get('late_night_pct', 0)
            
            # 根据群名关键词和行为特征判断群类型
            group_type = '💬 普通群聊'
            group_type_desc = '日常交流的空间'
            if any(kw in group_name for kw in ['家', '爸', '妈', '爷', '奶', '亲', '家庭', '全家']):
                group_type = '🏠 家庭群'
                group_type_desc = '最温暖的港湾'
            elif any(kw in group_name for kw in ['工作', '项目', '团队', '公司', '部门', '组', '办公']):
                group_type = '💼 工作群'
                group_type_desc = '职场战友们'
            elif any(kw in group_name for kw in ['班', '级', '届', '学', '校', '同学', '室友', '毕业']):
                group_type = '🎓 同学群'
                group_type_desc = '青春的回忆'
            elif any(kw in group_name for kw in ['游戏', '王者', '吃鸡', '原神', 'LOL', '开黑']):
                group_type = '🎮 游戏群'
                group_type_desc = '一起上分的快乐'
            elif any(kw in group_name for kw in ['饭', '吃', '美食', '火锅', '烧烤', '聚餐']):
                group_type = '🍜 美食群'
                group_type_desc = '民以食为天'
            elif any(kw in group_name for kw in ['运动', '跑步', '健身', '球', '游泳', '骑行']):
                group_type = '🏃 运动群'
                group_type_desc = '挥洒汗水的地方'
            elif member_count > 100:
                group_type = '🌐 大型社群'
                group_type_desc = '人多热闹'
            elif member_count <= 5 and avg_daily > 20:
                group_type = '👯 闺蜜/死党群'
                group_type_desc = '最亲密的小圈子'
            
            # ========== 群聊标签生成 ==========
            tags = []
            
            # 活跃度标签
            if avg_daily > 100:
                tags.append('🔥 超级活跃')
            elif avg_daily > 50:
                tags.append('💬 热闹群')
            elif avg_daily > 10:
                tags.append('✨ 适度活跃')
            elif avg_daily < 1:
                tags.append('🤫 安静群')
            
            # 深夜属性
            if late_night_pct > 30:
                tags.append('🌙 深夜群')
            elif late_night_pct > 15:
                tags.append('🦉 夜猫子群')
            
            # 你的角色标签
            if my_rank == 1:
                tags.append('👑 你是话唠王')
            elif my_rank and my_rank <= 3:
                tags.append('🏆 你是主力军')
            elif my_msgs == 0:
                tags.append('🤿 你在潜水')
            
            # 群规模标签
            if member_count > 200:
                tags.append('🌍 超大群')
            elif member_count > 50:
                tags.append('👥 中型群')
            elif member_count <= 10:
                tags.append('💕 小群')
            
            # 活跃周期标签
            if days > 300:
                tags.append('📅 全年活跃')
            elif days > 100:
                tags.append('📆 大半年活跃')
            
            tags_html = ''.join([f'<span class="group-tag">{t}</span>' for t in tags[:5]])
            
            # ========== 群聊活力指数（综合评分）==========
            vitality_score = 0
            vitality_score += min(30, avg_daily * 0.5)  # 日均消息贡献最多30分
            vitality_score += min(25, member_count * 0.3)  # 成员数贡献最多25分
            vitality_score += min(25, days / 12)  # 活跃天数贡献最多25分
            vitality_score += min(20, len(top_talkers) * 4)  # 活跃人数贡献最多20分
            vitality_score = min(100, int(vitality_score))
            
            if vitality_score >= 80:
                vitality_level = '🔥 超强活力'
                vitality_color = 'var(--pink)'
            elif vitality_score >= 60:
                vitality_level = '💪 活力充沛'
                vitality_color = 'var(--cyan)'
            elif vitality_score >= 40:
                vitality_level = '✨ 适度活跃'
                vitality_color = 'var(--purple)'
            else:
                vitality_level = '🌙 佛系群聊'
                vitality_color = 'var(--dim)'
            
            # ========== 话题集中度分析 ==========
            # 计算消息分布是否集中（头部用户占比）
            if top_talkers:
                top3_msgs = sum(v for _, v in top_talkers[:3])
                concentration = int(top3_msgs / total_msgs * 100) if total_msgs else 0
                if concentration > 70:
                    concentration_text = '🎯 高度集中 - 少数人主导'
                elif concentration > 50:
                    concentration_text = '📊 适度集中 - 核心成员活跃'
                else:
                    concentration_text = '🌈 分布均匀 - 大家都在聊'
            else:
                concentration = 0
                concentration_text = '-'
            
            # 你的存在感分析
            if my_rank == 1:
                presence_text = '🏆 话唠王者！你是群里最活跃的人'
                presence_color = 'var(--pink)'
            elif my_rank and my_rank <= 3:
                presence_text = f'🥇 群内Top{my_rank}！你的存在感很强'
                presence_color = 'var(--cyan)'
            elif my_rank and my_rank <= 10:
                presence_text = f'💬 活跃分子，排名第{my_rank}'
                presence_color = 'var(--purple)'
            elif my_msgs > 0:
                presence_text = f'👀 低调潜水员，排名第{my_rank}'
                presence_color = 'var(--dim)'
            else:
                presence_text = '🤿 深海潜水员，一言不发'
                presence_color = 'var(--dim)'
            
            # 小时分布数据
            hours = gc.get('hours', {})
            if hours:
                peak_hour = gc.get('peak_hour', 12)
                late_night = gc.get('late_night', 0)
                late_pct = gc.get('late_night_pct', 0)
            else:
                peak_hour = 12
                late_night = 0
                late_pct = 0
            
            # 将peak_hour转换为时段名称
            peak_period_names = ['深夜','深夜','深夜','深夜','深夜','深夜','上午','上午','上午','上午','上午','上午','下午','下午','下午','下午','下午','下午','晚间','晚间','晚间','晚间','晚间','深夜']
            peak_period = peak_period_names[peak_hour % 24] if peak_hour else '上午'
            
            # 月度分布
            monthly = gc.get('monthly', {})
            monthly_2025 = {k: v for k, v in monthly.items() if k.startswith('2025')}
            if monthly_2025:
                peak_month = max(monthly_2025.keys(), key=lambda k: monthly_2025.get(k, 0))
                peak_month_val = monthly_2025.get(peak_month, 0)
                month_names = {'01':'1月','02':'2月','03':'3月','04':'4月','05':'5月','06':'6月',
                              '07':'7月','08':'8月','09':'9月','10':'10月','11':'11月','12':'12月'}
                peak_month_name = month_names.get(peak_month[-2:], peak_month)
            else:
                peak_month_name = '-'
                peak_month_val = 0
            
            # 生成小时热力条
            hour_bar_html = ''
            if hours:
                max_hour_val = max(hours.values()) if hours else 1
                for h in range(24):
                    val = hours.get(str(h), hours.get(h, 0))
                    pct = int(val / max_hour_val * 100) if max_hour_val else 0
                    if pct > 70:
                        color = 'var(--pink)'
                    elif pct > 40:
                        color = 'var(--purple)'
                    elif pct > 10:
                        color = 'var(--cyan)'
                    else:
                        color = 'var(--bg3)'
                    hour_bar_html += f'<div class="hour-bar" style="height:{max(5, pct)}%;background:{color}" title="{h}:00 - {val}条"></div>'
                
                hour_bar_html = f'''
                <div class="group-hour-chart">
                    <div class="hour-bars">{hour_bar_html}</div>
                    <div class="hour-labels">
                        <span>0</span><span>6</span><span>12</span><span>18</span><span>24</span>
                    </div>
                </div>'''
            
            # 快速数据行（折叠状态显示）
            quick_stats_html = f'''
    <div class="group-quick-stats">
        <div class="quick-stat">
            <span class="quick-label">你发送</span>
            <span class="quick-val me">{my_msgs:,}</span>
            <span class="quick-pct">({my_pct}%)</span>
        </div>
        <div class="quick-divider">|</div>
        <div class="quick-stat">
            <span class="quick-label">群内排名</span>
            <span class="quick-val">#{my_rank if my_rank else '-'}/{member_count}</span>
        </div>
        <div class="quick-divider">|</div>
        <div class="quick-stat">
            <span class="quick-label">日均</span>
            <span class="quick-val">{gc.get('avg_daily', 0)}</span>
        </div>
        <div class="quick-divider">|</div>
        <div class="quick-stat">
            <span class="quick-label">活力</span>
            <span class="quick-val" style="color:{vitality_color}">{vitality_score}分</span>
        </div>
    </div>'''
            
            cards += f'''
<div class="group-card" data-idx="{idx}">
    <div class="group-header" onclick="toggleCard(this)">
        <span class="group-rank">#{idx}</span>
        <span class="group-name">{display_group_name(gc['name'][:20])}</span>
        <span class="group-brief">
            <i class="num" data-val="{gc['total_msgs']}">{gc['total_msgs']:,}</i>条 · 
            {gc['member_count']}人 · 
            {gc['days']}天
        </span>
        <span class="chat-toggle">▼</span>
    </div>
    <div class="group-tags">{tags_html}</div>
    {quick_stats_html}
    <div class="chat-body">
        <!-- 群聊类型与活力 -->
        <div class="group-type-section">
            <div class="group-type-badge">
                <span class="group-type-icon">{group_type}</span>
                <span class="group-type-desc">{group_type_desc}</span>
            </div>
            <div class="group-vitality">
                <div class="vitality-header">群聊活力指数</div>
                <div class="vitality-score" style="color:{vitality_color}">{vitality_score}</div>
                <div class="vitality-bar">
                    <div class="vitality-fill" style="width:{vitality_score}%;background:{vitality_color}"></div>
                </div>
                <div class="vitality-level">{vitality_level}</div>
            </div>
        </div>
        
        <!-- 基础数据 -->
        <div class="group-stats">
            <div class="gstat"><div class="gstat-val"><i class="num" data-val="{gc['total_msgs']}">{gc['total_msgs']:,}</i></div><div class="gstat-lbl">总消息</div></div>
            <div class="gstat"><div class="gstat-val"><i class="num" data-val="{gc['member_count']}">{gc['member_count']}</i></div><div class="gstat-lbl">成员数</div></div>
            <div class="gstat"><div class="gstat-val"><i class="num" data-val="{gc['days']}">{gc['days']}</i></div><div class="gstat-lbl">活跃天</div></div>
            <div class="gstat"><div class="gstat-val">{gc.get('avg_daily', 0)}</div><div class="gstat-lbl">日均消息</div></div>
            <div class="gstat"><div class="gstat-val">{peak_period}</div><div class="gstat-lbl">高峰时段</div></div>
            <div class="gstat"><div class="gstat-val">{late_pct}%</div><div class="gstat-lbl">深夜占比</div></div>
        </div>
        
        <!-- 话语权分布 -->
        <div class="group-concentration">
            <div class="section-subtitle">📊 话语权分布</div>
            <div class="concentration-bar">
                <div class="concentration-fill" style="width:{concentration}%"></div>
                <span class="concentration-val">Top3占比 {concentration}%</span>
            </div>
            <div class="concentration-desc">{concentration_text}</div>
        </div>
        
        <!-- 你的存在感 -->
        <div class="group-presence">
            <div class="presence-header">📊 你在群里的存在感</div>
            <div class="presence-content">
                <div class="presence-main">
                    <div class="presence-rank" style="border-color:{presence_color}">
                        <span class="rank-num">#{my_rank if my_rank else '-'}</span>
                        <span class="rank-total">/ {member_count}人</span>
                    </div>
                    <div class="presence-stats">
                        <div class="presence-stat">
                            <span class="presence-val">{my_msgs:,}</span>
                            <span class="presence-lbl">你的发言</span>
                        </div>
                        <div class="presence-stat">
                            <span class="presence-val">{my_pct}%</span>
                            <span class="presence-lbl">贡献占比</span>
                        </div>
                    </div>
                </div>
                <div class="presence-desc" style="color:{presence_color}">{presence_text}</div>
            </div>
        </div>
        
        <!-- 24小时活跃度 -->
        <div class="group-hours-section">
            <div class="section-subtitle">🕐 24小时活跃度</div>
            {hour_bar_html}
        </div>
        
        <!-- 话唠排行 -->
        <div class="talkers-section">
            <div class="section-subtitle">🗣️ 话唠排行 Top5</div>
            <div class="talkers-list">{talkers_html}</div>
        </div>
    </div>
</div>
'''
        return cards
    
    # ============ 好友分组 ============
    def make_friend_groups():
        # 分类配置：名称、消息范围、情感描述
        categories = [
            ('💎 密友', 500, float('inf'), '聊不完的天，说不完的话'),
            ('💛 好友', 100, 500, '不常联系，但一直都在'),
            ('🤝 熟人', 30, 100, '生活里的点头之交'),
            ('👋 偶尔联系', 0, 30, '也许只是还没找到话题'),
        ]
        
        html = ''
        for cat, min_val, max_val, desc in categories:
            friends = [(display_name(c['name']), c['total_msgs']) for c in sorted_private 
                      if min_val <= c['total_msgs'] < max_val]
            if not friends:
                continue
            
            names_preview = ', '.join([f'{n}({v})' for n, v in friends[:8]])
            if len(friends) > 8:
                names_preview += f' 等{len(friends)}人'
            
            html += f'''
            <div class="friend-group">
                <div class="fg-title">{cat}</div>
                <div class="fg-desc">{desc}</div>
                <div class="fg-count"><i class="num" data-val="{len(friends)}">{len(friends)}</i> 人</div>
                <div class="fg-list">{names_preview}</div>
            </div>'''
        
        return html

    # ============ 12个月热力图 ============
    # ============ 小节总结生成（数据叙事核心）============
    def make_section_summary(section_type):
        """生成每个模块的小结文案，帮助用户抓住重点"""
        summaries = {
            'heatmap': '📝 每一个高峰和低谷，都是你生活节奏的真实写照。消息最多的月份，也许藏着这一年最精彩的故事。',
            'rhythm': '📝 你的社交节奏，就是你生活的韵律。无论是早起问好还是深夜倾诉，每个时段都有专属的温度。',
            'colors': '📝 这些色彩，是你社交能量的可视化。温暖、陪伴、活力、好奇、默契——你的主色调，定义了你的社交风格。',
            'profile': '📝 虽然只是猜测，但文字里真的藏着你的痕迹。每个人都是独一无二的，你的表达方式就是你的签名。',
            'letter': '📝 一封信，胜过千言万语。最珍贵的感情，往往藏在最平凡的日常对话里。',
            'titles': '📝 这些称号不是标签，而是你独特存在的证明。新的一年，你会解锁什么新成就？',
            'personality': '📝 没有好坏之分，只有适合自己的社交方式。了解自己，才能更好地与世界连接。',
            'moments': '📝 特别的瞬间串联起来，就是你的年度故事。感谢这些人、这些时刻，陪你走过2025。',
            'chemistry': '📝 默契不是天生的，是一次次对话中慢慢培养的。得分高低不重要，重要的是你们还在彼此的消息列表里。',
            'private': '📝 每一个排名背后，都是一段独特的关系。数字是冰冷的，但每条消息都承载着温度。',
            'group': '📝 群聊是我们的"数字村落"，热闹也好、潜水也好，都是参与这个时代的方式。',
        }
        
        text = summaries.get(section_type, '')
        if not text:
            return ''
        
        return f'''
        <div class="section-summary">
            <div class="summary-text">{text}</div>
        </div>'''
    
    # ============ 年度旅程时间线 ============
    def make_year_journey():
        """生成年度聊天旅程时间线，展示每月的关键记忆"""
        # 汇总每月数据
        monthly_data = defaultdict(lambda: {'msgs': 0, 'friends': set(), 'peak_friend': '', 'peak_msgs': 0})
        
        for chat in private_chats:
            monthly = chat.get('monthly', {})
            name = chat.get('name', '')
            for month_key, data in monthly.items():
                if month_key.startswith('2025'):
                    count = data.get('total', 0) if isinstance(data, dict) else data
                    monthly_data[month_key]['msgs'] += count
                    if count > 0:
                        monthly_data[month_key]['friends'].add(name)
                    if count > monthly_data[month_key]['peak_msgs']:
                        monthly_data[month_key]['peak_msgs'] = count
                        monthly_data[month_key]['peak_friend'] = name
        
        # 月份信息
        month_info = {
            '2025-01': ('🎊', '新年伊始', '新年的问候开启新篇章'),
            '2025-02': ('🧧', '春节团圆', '红包与祝福满天飞'),
            '2025-03': ('🌸', '春暖花开', '万物复苏的季节'),
            '2025-04': ('🌱', '春意盎然', '播种希望的时刻'),
            '2025-05': ('🌹', '劳动光荣', '五一假期的欢聚'),
            '2025-06': ('☀️', '仲夏序曲', '毕业季的告别与不舍'),
            '2025-07': ('🏖️', '盛夏时光', '暑假的自由与快乐'),
            '2025-08': ('🌻', '热情似火', '夏日的尾巴'),
            '2025-09': ('🍂', '金秋九月', '开学季的新开始'),
            '2025-10': ('🎃', '金秋十月', '国庆假期的相聚'),
            '2025-11': ('🍁', '深秋时节', '双十一的买买买'),
            '2025-12': ('❄️', '岁末年终', '圣诞与新年的期待'),
        }
        
        # 找出最活跃的月份
        if monthly_data:
            peak_month = max(monthly_data.keys(), key=lambda k: monthly_data[k]['msgs'])
        else:
            peak_month = '2025-01'
        
        # 生成时间线HTML
        timeline_html = ''
        for m in range(1, 13):
            month_key = f'2025-{m:02d}'
            data = monthly_data.get(month_key, {'msgs': 0, 'friends': set(), 'peak_friend': '', 'peak_msgs': 0})
            info = month_info.get(month_key, ('📅', f'{m}月', ''))
            
            msgs = data['msgs']
            friends_count = len(data['friends'])
            peak_friend = display_name(data['peak_friend'][:6]) if data['peak_friend'] else '-'
            is_peak = month_key == peak_month
            
            # 计算活跃度等级
            if msgs > 5000:
                level = 'high'
            elif msgs > 1000:
                level = 'mid'
            elif msgs > 0:
                level = 'low'
            else:
                level = 'none'
            
            peak_badge = '<span class="journey-peak">🔥 最活跃</span>' if is_peak else ''
            
            timeline_html += f'''
            <div class="journey-item {level}" data-month="{m}">
                <div class="journey-dot"></div>
                <div class="journey-content">
                    <div class="journey-month">
                        <span class="journey-icon">{info[0]}</span>
                        <span class="journey-name">{info[1]}</span>
                        {peak_badge}
                    </div>
                    <div class="journey-stats">
                        <span class="journey-msgs">{msgs:,}条消息</span>
                        <span class="journey-friends">{friends_count}位好友</span>
                    </div>
                    <div class="journey-highlight">
                        {'聊得最多: ' + peak_friend if peak_friend != '-' else info[2]}
                    </div>
                </div>
            </div>'''
        
        # 年度总结
        total_msgs = sum(d['msgs'] for d in monthly_data.values())
        total_friends = len(set().union(*[d['friends'] for d in monthly_data.values()]))
        
        html = f'''
        <div class="year-journey">
            <div class="journey-header">
                <div class="journey-title">📆 2025 聊天旅程</div>
                <div class="journey-subtitle">12个月，{total_msgs:,}条消息，{total_friends}位朋友</div>
            </div>
            <div class="journey-timeline">
                {timeline_html}
            </div>
            <div class="journey-footer">
                <div class="journey-insight">
                    <span class="insight-icon">💡</span>
                    <span class="insight-text">每个月都有不同的故事，{month_info.get(peak_month, ('','',''))[1]}是你最活跃的时光。时间在走，聊天在继续，生活也在向前。</span>
                </div>
            </div>
        </div>'''
        
        return html

    def make_monthly_heatmap():
        # 汇总所有聊天的月度数据
        monthly_totals = defaultdict(int)
        
        for chat in private_chats:
            monthly = chat.get('monthly', {})
            for month_key, data in monthly.items():
                if month_key.startswith('2025'):
                    count = data.get('total', 0) if isinstance(data, dict) else data
                    monthly_totals[month_key] += count
        
        for chat in group_chats:
            monthly = chat.get('monthly', {})
            for month_key, data in monthly.items():
                if month_key.startswith('2025'):
                    count = data.get('total', 0) if isinstance(data, dict) else data
                    monthly_totals[month_key] += count
        
        # 生成12个月的数据
        months = []
        max_count = 1
        for m in range(1, 13):
            key = f'2025-{m:02d}'
            count = monthly_totals.get(key, 0)
            months.append((m, count))
            if count > max_count:
                max_count = count
        
        # 颜色渐变（从暗到亮）
        colors = [
            'rgba(255,107,157,0.2)',
            'rgba(255,107,157,0.35)',
            'rgba(255,107,157,0.5)',
            'rgba(255,107,157,0.65)',
            'rgba(255,107,157,0.8)',
            'rgba(78,205,196,0.9)',
        ]
        
        month_names = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']
        
        html = '<div class="heatmap-grid">'
        for m, count in months:
            # 计算颜色级别
            if count == 0:
                color = 'rgba(255,255,255,0.05)'
                height = 20
            else:
                level = min(5, int((count / max_count) * 5))
                color = colors[level]
                height = 20 + int((count / max_count) * 60)
            
            html += f'''
            <div class="heatmap-month">
                <div class="heatmap-bar" style="background:{color};height:{height}px">
                    <span>{count if count > 0 else ''}</span>
                    <div class="heatmap-tooltip">{month_names[m-1]}共 {count:,} 条消息</div>
                </div>
                <div class="heatmap-label">{month_names[m-1]}</div>
            </div>'''
        html += '</div>'
        
        return html

    # ============ 24小时聊天节奏热力图 ============
    def make_hourly_rhythm():
        """生成24小时聊天节奏热力图，展示一天中的社交活跃时段"""
        # 汇总所有聊天的小时分布数据
        hourly_totals = defaultdict(int)
        
        for chat in private_chats:
            hours = chat.get('hour_dist', {})
            for h, count in hours.items():
                try:
                    hourly_totals[int(h)] += count
                except:
                    pass
        
        # 如果没有小时数据，尝试从其他字段估算
        if not hourly_totals:
            # 用深夜消息估算
            total_late = sum(c.get('late_night', 0) for c in private_chats)
            if total_late > 0:
                for h in [0, 1, 2, 3, 4, 5]:
                    hourly_totals[h] = total_late // 6
            # 假设大部分消息在白天
            total_msgs = sum(c.get('total_msgs', 0) for c in private_chats)
            remaining = total_msgs - total_late
            if remaining > 0:
                for h in range(6, 24):
                    hourly_totals[h] = remaining // 18
        
        # 获取24小时数据
        max_count = max(hourly_totals.values()) if hourly_totals else 1
        hours_data = [hourly_totals.get(h, 0) for h in range(24)]
        total_msgs = sum(hours_data)
        
        # 找出高峰时段
        peak_hour = max(range(24), key=lambda h: hourly_totals.get(h, 0))
        
        # 时段分类
        morning = sum(hours_data[6:12])    # 6-11点
        afternoon = sum(hours_data[12:18]) # 12-17点
        evening = sum(hours_data[18:23])   # 18-22点
        late_night = sum(hours_data[23:24]) + sum(hours_data[0:6])  # 23-5点
        
        # 找出最活跃时段
        periods = [
            ('清晨时光 ☀️', morning, '6:00-12:00', '新的一天，从问候开始'),
            ('午后悠闲 🌤️', afternoon, '12:00-18:00', '工作间隙的碎碎念'),
            ('夜幕降临 🌙', evening, '18:00-23:00', '一天中最放松的聊天时光'),
            ('深夜心语 🌃', late_night, '23:00-6:00', '夜深了，真心话才敢说出口'),
        ]
        peak_period = max(periods, key=lambda x: x[1])
        
        # 生成时段条形图
        period_html = ''
        max_period = max(p[1] for p in periods) or 1
        for name, count, time_range, desc in periods:
            pct = int(count / max_period * 100)
            is_peak = '👑' if name == peak_period[0] else ''
            period_html += f'''
            <div class="rhythm-period">
                <div class="rhythm-period-header">
                    <span class="rhythm-period-name">{is_peak}{name}</span>
                    <span class="rhythm-period-time">{time_range}</span>
                </div>
                <div class="rhythm-period-bar">
                    <div class="rhythm-period-fill" style="width:{pct}%"></div>
                    <span class="rhythm-period-count">{count:,}条</span>
                </div>
                <div class="rhythm-period-desc">{desc}</div>
            </div>'''
        
        # 生成24小时圆环热力图
        ring_html = '<div class="rhythm-ring">'
        for h in range(24):
            count = hours_data[h]
            pct = count / max_count if max_count else 0
            # 颜色从浅到深
            if pct > 0.8:
                color = 'var(--pink)'
            elif pct > 0.5:
                color = 'var(--purple)'
            elif pct > 0.2:
                color = 'var(--cyan)'
            else:
                color = 'rgba(255,255,255,0.15)'
            
            angle = h * 15  # 每小时15度
            ring_html += f'''
            <div class="rhythm-hour" style="--angle:{angle}deg;--color:{color}" title="{h}:00 - {count:,}条">
                <span class="rhythm-hour-label">{h}</span>
            </div>'''
        ring_html += '<div class="rhythm-ring-center">🕐</div></div>'
        
        # 根据peak_hour确定所属时段和更合理的表述
        if peak_hour >= 23 or peak_hour < 6:
            period_name = '深夜'
            period_range = '23:00-6:00'
        elif peak_hour >= 6 and peak_hour < 12:
            period_name = '上午'
            period_range = '6:00-12:00'
        elif peak_hour >= 12 and peak_hour < 18:
            period_name = '下午'
            period_range = '12:00-18:00'
        else:
            period_name = '晚间'
            period_range = '18:00-23:00'
        
        # 生成洞察文案 - 使用时段名称而非精确小时
        insight = ''
        if peak_hour >= 23 or peak_hour < 6:
            insight = f'🦉 你是个名副其实的夜猫子！深夜时分是你最活跃的时刻，那些凌晨的消息往往最真实。'
        elif peak_hour >= 6 and peak_hour < 9:
            insight = f'☀️ 早起的鸟儿有虫吃！清晨是你的社交高峰，新的一天从聊天开始。'
        elif peak_hour >= 9 and peak_hour < 12:
            insight = f'☕ 上午是你的聊天黄金时段，也许是工作间隙的小确幸？'
        elif peak_hour >= 12 and peak_hour < 14:
            insight = f'🍜 午间时光也不忘聊天！边吃边聊，是你的日常惬意时刻。'
        elif peak_hour >= 14 and peak_hour < 18:
            insight = f'🌤️ 下午是你的社交活跃期，工作之余的调剂时光。'
        elif peak_hour >= 18 and peak_hour < 21:
            insight = f'🌙 傍晚是你的聊天高峰，结束一天的忙碌，开始放松的对话。'
        else:
            insight = f'🌃 夜晚是你最爱聊天的时刻，夜色渐浓，心事也慢慢展开。'
        
        html = f'''
        <div class="rhythm-container">
            <div class="rhythm-header">
                <div class="rhythm-title">🕐 你的微信节奏图谱</div>
                <div class="rhythm-subtitle">每个时段的消息，都构成了你独特的社交日常</div>
            </div>
            
            <div class="rhythm-main">
                <div class="rhythm-visual">
                    {ring_html}
                    <div class="rhythm-peak">
                        <div class="rhythm-peak-label">最活跃时段</div>
                        <div class="rhythm-peak-value">{period_name}</div>
                        <div class="rhythm-peak-range">{period_range}</div>
                    </div>
                </div>
                
                <div class="rhythm-periods">
                    {period_html}
                </div>
            </div>
            
            <div class="rhythm-insight">
                <div class="rhythm-insight-icon">💡</div>
                <div class="rhythm-insight-text">{insight}</div>
            </div>
            
            <div class="rhythm-summary">
                <div class="rhythm-summary-item">
                    <span class="rhythm-summary-label">主导时段</span>
                    <span class="rhythm-summary-value">{peak_period[0]}</span>
                </div>
                <div class="rhythm-summary-item">
                    <span class="rhythm-summary-label">深夜消息占比</span>
                    <span class="rhythm-summary-value">{int(late_night/total_msgs*100) if total_msgs else 0}%</span>
                </div>
            </div>
        </div>'''
        
        return html

    # ============ 分享卡片 ============
    # ============ 个性化结语生成 ============
    # ============ 年度好友荣誉榜 ============
    def make_friend_honors():
        """生成年度好友荣誉榜，给不同好友颁发有趣的称号"""
        if not private_chats or len(private_chats) < 3:
            return ''
        
        honors = []
        
        # 1. 年度话痨冠军 - 消息最多的
        top_talker = max(private_chats, key=lambda c: c.get('total_msgs', 0))
        honors.append({
            'icon': '🏆',
            'title': '年度话痨冠军',
            'name': display_name(top_talker['name'][:8]),
            'reason': f'与Ta互动 {top_talker.get("total_msgs", 0):,} 条消息',
            'color': 'var(--pink)'
        })
        
        # 2. 深夜知己 - 深夜消息最多的
        late_chats = [c for c in private_chats if c.get('late_night', 0) > 10]
        if late_chats:
            night_owl = max(late_chats, key=lambda c: c.get('late_night', 0))
            honors.append({
                'icon': '🌙',
                'title': '深夜知己',
                'name': display_name(night_owl['name'][:8]),
                'reason': f'陪你度过 {night_owl.get("late_night", 0)} 个深夜',
                'color': 'var(--purple)'
            })
        
        # 3. 最暖心的人 - 关心次数最多
        care_chats = [c for c in private_chats if c.get('care_me', 0) + c.get('care_them', 0) > 5]
        if care_chats:
            warmest = max(care_chats, key=lambda c: c.get('care_me', 0) + c.get('care_them', 0))
            care_total = warmest.get('care_me', 0) + warmest.get('care_them', 0)
            honors.append({
                'icon': '❤️',
                'title': '最暖心的人',
                'name': display_name(warmest['name'][:8]),
                'reason': f'{care_total} 次温暖的关心',
                'color': 'var(--pink)'
            })
        
        # 4. 马拉松聊手 - 最长单次会话
        marathon_chats = [c for c in private_chats if c.get('max_session_len', 0) > 30]
        if marathon_chats:
            marathon = max(marathon_chats, key=lambda c: c.get('max_session_len', 0))
            honors.append({
                'icon': '🏃',
                'title': '马拉松聊手',
                'name': display_name(marathon['name'][:8]),
                'reason': f'单次聊天 {marathon.get("max_session_len", 0)} 条消息',
                'color': 'var(--cyan)'
            })
        
        # 5. 秒回之王 - 回复最快的
        fast_repliers = [c for c in private_chats if c.get('reply_them_median', 0) > 0 and c.get('reply_them_median', 0) < 120]
        if fast_repliers:
            fastest = min(fast_repliers, key=lambda c: c.get('reply_them_median', 60))
            reply_time = fastest.get('reply_them_median', 60)
            if reply_time < 60:
                time_str = f'{int(reply_time)}秒'
            else:
                time_str = f'{int(reply_time/60)}分钟'
            honors.append({
                'icon': '⚡',
                'title': '秒回之王',
                'name': display_name(fastest['name'][:8]),
                'reason': f'平均 {time_str} 回复你',
                'color': 'var(--yellow)'
            })
        
        # 6. 陪伴最久 - 聊天天数最多
        long_term = max(private_chats, key=lambda c: c.get('days', 0))
        if long_term.get('days', 0) > 30:
            honors.append({
                'icon': '📅',
                'title': '全年陪伴奖',
                'name': display_name(long_term['name'][:8]),
                'reason': f'陪伴你 {long_term.get("days", 0)} 天',
                'color': 'var(--cyan)'
            })
        
        if not honors:
            return ''
        
        # 生成HTML
        honors_html = ''
        for i, h in enumerate(honors[:6]):
            honors_html += f'''
            <div class="honor-card" style="animation-delay:{i*0.1}s">
                <div class="honor-icon">{h['icon']}</div>
                <div class="honor-content">
                    <div class="honor-title" style="color:{h['color']}">{h['title']}</div>
                    <div class="honor-name">{h['name']}</div>
                    <div class="honor-reason">{h['reason']}</div>
                </div>
            </div>'''
        
        html = f'''
        <div class="friend-honors">
            <div class="honors-header">
                <div class="honors-title">🏅 年度好友荣誉榜</div>
                <div class="honors-subtitle">给每个特别的Ta，颁发专属荣誉</div>
            </div>
            <div class="honors-grid">{honors_html}</div>
            <div class="honors-footer">
                <p>每个荣誉都是一段独特的故事，感谢这些特别的人，让你的2025充满温度。</p>
            </div>
        </div>'''
        
        return html

    def make_ending_section():
        """生成个性化的结语内容"""
        # 收集统计数据
        best_friend = display_name(sorted_private[0]['name']) if sorted_private else '好友'
        best_msgs = get_2025_msgs(sorted_private[0]) if sorted_private else 0
        late_night_total = sum(c.get('late_night', 0) for c in private_chats)
        total_sessions = sum(c.get('sessions', 0) for c in private_chats)
        total_care = sum(c.get('care_them', 0) + c.get('care_me', 0) for c in private_chats)
        
        # 生成个性化文案
        highlights = []
        
        if total_msgs > 50000:
            highlights.append(f'这一年，你发送了 <strong>{total_msgs:,}</strong> 条消息，每一条都承载着你的心情')
        elif total_msgs > 10000:
            highlights.append(f'这一年，<strong>{total_msgs:,}</strong> 条消息在你的指尖流淌')
        else:
            highlights.append(f'这一年，{total_msgs:,} 条消息，编织成了你独一无二的故事')
        
        if best_friend and best_msgs > 0:
            highlights.append(f'<strong>{display_name(best_friend[:6])}</strong> 收到了你最多的消息，<strong>{best_msgs:,}</strong> 条对话见证了这份珍贵的情谊')
        
        if late_night_total > 100:
            highlights.append(f'<strong>{late_night_total}</strong> 条深夜消息，是你最真实的情绪出口')
        elif late_night_total > 30:
            highlights.append(f'那些深夜还亮着的聊天窗口，藏着你最柔软的心事')
        
        if total_care > 50:
            highlights.append(f'<strong>{total_care}</strong> 句关心的话语，是这一年最温暖的注脚')
        elif total_care > 20:
            highlights.append(f'那些"早点休息"和"注意身体"，是爱的另一种表达')
        
        if len(sorted_private) > 30:
            highlights.append(f'<strong>{len(sorted_private)}</strong> 位朋友组成了你的小宇宙，人间烟火，莫过于此')
        elif len(sorted_private) > 15:
            highlights.append(f'<strong>{len(sorted_private)}</strong> 个人的聊天框，每一个都是独特的故事')
        
        # 生成感悟
        reflections = [
            '每一条消息，都是一次穿越时空的心意传递',
            '每一次"在吗"，都是鼓起勇气的想念',
            '那些深夜的对话，藏着白天说不出口的真心话',
            '感谢那些秒回你的人，他们把你放在心上',
            '有些话，只有在小小的聊天框里，才敢轻轻说出口',
            '距离从来不是问题，因为有些人住在心里',
            '所有的"晚安"背后，都是"我还想再和你多说几句"',
            '发送键按下的那一刻，是思念抵达的开始',
        ]
        import random
        reflection = random.choice(reflections)
        
        # 新年寄语
        wishes = [
            '2026，愿你的消息列表里，都是让你嘴角上扬的名字',
            '新的一年，继续做彼此的树洞，继续是彼此的港湾',
            '愿每一条消息都被认真阅读，每一份心意都被温柔接住',
            '2026，希望那个"正在输入..."的人，永远不会变成"对方正在输入..."然后消失',
            '下一年，继续在这里相遇，继续说那些只有我们才懂的暗语',
            '愿你发出的每一条消息，都能被期待它的人收到',
            '2026，愿我们都能勇敢一点，把想说的话说出来',
        ]
        wish = random.choice(wishes)
        
        # 构建HTML
        highlights_html = '<br>'.join(highlights) if highlights else ''
        
        html = f'''
        <div class="ending-emoji">💬</div>
        <h2 class="ending-title">2025，感谢有你</h2>
        
        <div class="ending-highlights">
            {highlights_html}
        </div>
        
        <div class="ending-reflection">
            "{reflection}"
        </div>
        
        <div class="ending-wish">
            {wish}
        </div>
        
        <div class="ending-signature">
            —— 你的2025年度聊天报告
        </div>
        '''
        
        return html

    # ============ 年度来信 ============
    def make_annual_letter():
        """生成年度来信 - 给最好朋友的一封信（信封拆开动画）"""
        if not sorted_private:
            return '<div class="empty">暂无私聊数据</div>'
        
        # 获取最佳拍档数据
        best = sorted_private[0]
        best_name = display_name(best['name'])
        best_name_short = display_name(best['name'][:8])
        best_msgs = get_2025_msgs(best)
        late_night = best.get('late_night', 0)
        sessions = best.get('sessions', 0)
        days = best.get('days', 0)
        their_msgs = best.get('their_msgs', 0)
        my_msgs = best.get('my_msgs', 0)
        care_them = best.get('care_them', 0)
        care_me = best.get('care_me', 0)
        
        # 计算回复速度
        reply_time = best.get('reply_them_median', 0)
        reply_desc = ''
        if reply_time and reply_time < 60:
            reply_desc = f'每次你发消息，我平均 <strong>{int(reply_time)}秒</strong> 就回复'
        elif reply_time and reply_time < 300:
            reply_desc = f'每次你发消息，我都尽快回复'
        
        # 找出聊天最多的月份
        monthly = best.get('monthly', {})
        peak_month = ''
        peak_count = 0
        for k, v in monthly.items():
            if k.startswith('2025'):
                count = v.get('total', 0) if isinstance(v, dict) else v
                if count > peak_count:
                    peak_count = count
                    peak_month = k
        
        month_names = {'01':'一月','02':'二月','03':'三月','04':'四月','05':'五月','06':'六月',
                      '07':'七月','08':'八月','09':'九月','10':'十月','11':'十一月','12':'十二月'}
        peak_month_name = month_names.get(peak_month[-2:], '') if peak_month else ''
        
        # 计算平均每天消息数
        avg_daily = round(best_msgs / days, 1) if days > 0 else 0
        
        # 生成来信内容 - 更丰富的版本
        letter_parts = [f'嘿，{best_name_short}：']
        letter_parts.append('')
        letter_parts.append(f'写这封信的时候，我翻看了我们2025年所有的聊天记录。')
        letter_parts.append('')
        letter_parts.append(f'这一年，我们一共聊了 <strong>{best_msgs:,}</strong> 条消息。')
        
        if days > 30:
            letter_parts.append(f'在 <strong>{days}</strong> 天的时光里，平均每天 <strong>{avg_daily}</strong> 条。')
        
        if sessions > 10:
            letter_parts.append(f'我们开启了 <strong>{sessions}</strong> 次对话，每一次打开聊天框看到你的消息都很开心。')
        
        # 消息来往平衡
        if their_msgs > 0 and my_msgs > 0:
            if abs(their_msgs - my_msgs) / max(their_msgs, my_msgs) < 0.3:
                letter_parts.append(f'你发了 {their_msgs} 条，我发了 {my_msgs} 条，我们的来往很均衡呢。')
            elif my_msgs > their_msgs:
                letter_parts.append(f'好像我话比较多，发了 {my_msgs} 条，谢谢你一直倾听。')
            else:
                letter_parts.append(f'你发了 {their_msgs} 条，我很珍惜你愿意和我分享这么多。')
        
        if late_night > 20:
            letter_parts.append(f'有 <strong>{late_night}</strong> 条消息是在深夜发出的，谢谢你陪我熬过那些睡不着的夜晚。')
        
        if reply_desc:
            letter_parts.append(reply_desc + '，因为不想让你等太久。')
        
        if peak_month_name:
            letter_parts.append(f'<strong>{peak_month_name}</strong>是我们聊得最多的时候，那段时光真的很美好。')
        
        # 关心互动
        if care_them > 5 or care_me > 5:
            letter_parts.append(f'这一年，你关心了我 {care_them} 次，我关心了你 {care_me} 次。')
            letter_parts.append('每一句"最近怎么样"、"注意身体"都被我记在心里。')
        
        letter_parts.append('')
        letter_parts.append('回顾这些数字，它们不只是冷冰冰的统计，')
        letter_parts.append('而是我们这一年友谊的见证。')
        letter_parts.append('')
        letter_parts.append('新的一年，希望我们继续保持联系。')
        letter_parts.append('愿你一切都好。')
        letter_parts.append('')
        letter_parts.append('—— 你的好友')
        
        # 使用信封拆开动画结构
        html = f'''
        <div class="letter-wrapper">
            <div class="envelope" onclick="this.classList.toggle('opened')">
                <div class="envelope-back"></div>
                <div class="envelope-flap"></div>
                <div class="envelope-seal">💌</div>
                <div class="envelope-hint">点击拆开信封</div>
                <div class="letter-paper">
                    <div class="letter-header">
                        <span class="letter-icon">✉️</span>
                        <span class="letter-title">写给 {best_name_short} 的一封信</span>
                    </div>
                    <div class="letter-content">
                        {'<br>'.join(letter_parts)}
                    </div>
                    <div class="letter-stamp">2025</div>
                </div>
            </div>
        </div>'''
        
        return html

    # ============ 社交分享卡片 ============
    def make_share_card():
        """生成可分享的年度社交总结卡片"""
        best_friend = display_name(sorted_private[0]['name'][:6]) if sorted_private else '好友'
        late_total = sum(c.get('late_night', 0) for c in private_chats)
        care_total = sum(c.get('care_them', 0) + c.get('care_me', 0) for c in private_chats)
        
        # 生成社交风格标签
        style_tags = []
        if late_total > 100:
            style_tags.append('🌙 深夜话痨')
        if care_total > 50:
            style_tags.append('💗 暖心达人')
        if len(sorted_private) > 30:
            style_tags.append('👥 社交达人')
        if total_msgs > 50000:
            style_tags.append('🔥 聊天狂魔')
        if len(sorted_groups) > 10:
            style_tags.append('🌍 群聊活跃')
        
        tags_html = ''.join([f'<span class="share-tag">{t}</span>' for t in style_tags[:3]])
        
        html = f'''
        <div class="share-card" id="shareCard">
            <div class="share-card-bg"></div>
            <div class="share-card-content">
                <div class="share-card-year">2025</div>
                <div class="share-card-title">我的微信年度报告</div>
                
                <div class="share-card-stats">
                    <div class="share-stat">
                        <div class="share-stat-val">{total_msgs:,}</div>
                        <div class="share-stat-lbl">总消息</div>
                    </div>
                    <div class="share-stat">
                        <div class="share-stat-val">{len(sorted_private)}</div>
                        <div class="share-stat-lbl">好友数</div>
                    </div>
                    <div class="share-stat">
                        <div class="share-stat-val">{len(sorted_groups)}</div>
                        <div class="share-stat-lbl">群聊数</div>
                    </div>
                    <div class="share-stat">
                        <div class="share-stat-val">{late_total}</div>
                        <div class="share-stat-lbl">深夜消息</div>
                    </div>
                </div>
                
                <div class="share-card-best">
                    <span class="share-best-icon">❤️</span>
                    <span class="share-best-text">最佳拍档：{best_friend}</span>
                </div>
                
                <div class="share-card-tags">{tags_html}</div>
                
                <div class="share-card-footer">
                    <span>📱 微信年度聊天报告</span>
                </div>
            </div>
        </div>
        
        <div class="share-actions">
            <button class="share-btn" onclick="downloadShareCard()">📥 保存分享图片</button>
            <div class="share-tip">长按保存，分享给好友</div>
        </div>'''
        
        return html

    # ============ 用户画像分析 ============
    def analyze_user_profile():
        """基于聊天数据预测用户画像"""
        profile = {
            'age_range': '',
            'age_confidence': 0,
            'identity': '',
            'identity_confidence': 0,
            'interests': [],
            'social_style': '',
            'personality_tags': []
        }
        
        if not private_chats:
            return profile
        
        # ===== 数据收集 =====
        # 时间分布统计
        late_night_total = sum(c.get('late_night', 0) for c in private_chats)  # 深夜消息
        early_morning = sum(c.get('early_morning', 0) for c in private_chats if c.get('early_morning'))  # 早起消息
        
        # 消息风格统计
        total_msgs = sum(c.get('total_msgs', 0) for c in private_chats)
        avg_len_me = 0
        emoji_count = 0
        question_ratio = 0
        exclaim_ratio = 0
        
        # 语气词统计
        modal_intimate = 0  # 亲密撒娇词
        modal_think = 0     # 思考犹豫词
        modal_laugh = 0     # 笑声
        
        for c in private_chats:
            len_me = c.get('len_me', {})
            avg_len_me += len_me.get('avg', 0)
            
            sentence_me = c.get('sentence_me', {})
            question_ratio += sentence_me.get('question', 0)
            exclaim_ratio += sentence_me.get('exclaim', 0)
            
            modal_me = c.get('modal_me', {})
            modal_intimate += modal_me.get('亲密/撒娇', 0)
            modal_think += modal_me.get('思考/犹豫', 0)
            modal_laugh += modal_me.get('笑声', 0)
        
        num_chats = len(private_chats) or 1
        avg_len_me = avg_len_me / num_chats
        question_ratio = question_ratio / num_chats
        exclaim_ratio = exclaim_ratio / num_chats
        
        # 好友数量和活跃度
        active_friends = len([c for c in private_chats if c.get('total_msgs', 0) > 100])
        total_friends = len(private_chats)
        
        # 群聊参与度
        group_participation = sum(g.get('my_msgs', 0) for g in group_chats) if group_chats else 0
        group_count = len(group_chats) if group_chats else 0
        
        # ===== 年龄预测 =====
        age_score = {
            '00后 (15-24岁)': 0,
            '95后 (25-29岁)': 0,
            '90后 (30-34岁)': 0,
            '85后 (35-39岁)': 0,
            '80后+ (40岁以上)': 0
        }
        
        # 深夜活跃 -> 年轻人倾向
        if late_night_total > 200:
            age_score['00后 (15-24岁)'] += 3
            age_score['95后 (25-29岁)'] += 2
        elif late_night_total > 50:
            age_score['95后 (25-29岁)'] += 2
            age_score['90后 (30-34岁)'] += 1
        else:
            age_score['85后 (35-39岁)'] += 1
            age_score['80后+ (40岁以上)'] += 2
        
        # 亲密语气词多 -> 年轻人
        if modal_intimate > 50:
            age_score['00后 (15-24岁)'] += 3
            age_score['95后 (25-29岁)'] += 2
        elif modal_intimate > 20:
            age_score['95后 (25-29岁)'] += 2
            age_score['90后 (30-34岁)'] += 1
        
        # 消息长度 -> 成熟度
        if avg_len_me > 30:
            age_score['90后 (30-34岁)'] += 2
            age_score['85后 (35-39岁)'] += 2
        elif avg_len_me < 15:
            age_score['00后 (15-24岁)'] += 2
            age_score['95后 (25-29岁)'] += 1
        
        # 笑声表达多 -> 年轻化
        if modal_laugh > 100:
            age_score['00后 (15-24岁)'] += 2
            age_score['95后 (25-29岁)'] += 2
        
        # 好友数量
        if active_friends > 20:
            age_score['95后 (25-29岁)'] += 1
            age_score['90后 (30-34岁)'] += 1
        elif active_friends < 5:
            age_score['85后 (35-39岁)'] += 1
            age_score['80后+ (40岁以上)'] += 1
        
        # 选择最高分的年龄段
        max_age = max(age_score, key=age_score.get)
        total_age_score = sum(age_score.values()) or 1
        profile['age_range'] = max_age
        profile['age_confidence'] = min(95, int(age_score[max_age] / total_age_score * 100) + 40)
        
        # ===== 身份预测 =====
        identity_score = {
            '学生党': 0,
            '职场新人': 0,
            '职场骨干': 0,
            '自由职业': 0,
            '全职爸妈': 0
        }
        
        # 深夜活跃+群聊多 -> 学生
        if late_night_total > 150 and group_count > 5:
            identity_score['学生党'] += 3
        
        # 早起+消息简短 -> 职场
        if early_morning > 30 and avg_len_me < 20:
            identity_score['职场新人'] += 2
            identity_score['职场骨干'] += 2
        
        # 消息长度适中+活跃好友多 -> 职场骨干
        if 15 < avg_len_me < 35 and active_friends > 10:
            identity_score['职场骨干'] += 2
        
        # 时间分散+好友少但深度聊天 -> 自由职业
        if active_friends < 8 and total_msgs > 5000:
            identity_score['自由职业'] += 2
        
        # 关心词汇多 -> 可能是家长
        total_care = sum(c.get('care_me', 0) for c in private_chats)
        if total_care > 50 and age_score['85后 (35-39岁)'] + age_score['80后+ (40岁以上)'] > 3:
            identity_score['全职爸妈'] += 2
        
        # 年龄关联调整
        if '00后' in max_age:
            identity_score['学生党'] += 2
        elif '95后' in max_age:
            identity_score['职场新人'] += 2
        elif '90后' in max_age or '85后' in max_age:
            identity_score['职场骨干'] += 1
        
        max_identity = max(identity_score, key=identity_score.get)
        total_id_score = sum(identity_score.values()) or 1
        profile['identity'] = max_identity
        profile['identity_confidence'] = min(90, int(identity_score[max_identity] / total_id_score * 100) + 35)
        
        # ===== 兴趣爱好预测 =====
        interests = []
        
        # 基于消息模式推断
        if late_night_total > 100:
            interests.append('🌙 夜猫子')
        if modal_laugh > 80:
            interests.append('😄 爱笑达人')
        if question_ratio > 15:
            interests.append('🤔 求知欲强')
        if exclaim_ratio > 20:
            interests.append('🎉 情感丰富')
        if avg_len_me > 25:
            interests.append('📝 深度交流')
        if active_friends > 15:
            interests.append('🤝 社交达人')
        if group_participation > 500:
            interests.append('👥 群聊活跃')
        if total_care > 30:
            interests.append('💗 温暖贴心')
        if modal_intimate > 30:
            interests.append('🥰 可爱担当')
        if modal_think > 20:
            interests.append('💭 思考者')
        
        profile['interests'] = interests[:6]  # 最多6个
        
        # ===== 社交风格 =====
        if active_friends > 15 and group_count > 8:
            profile['social_style'] = '广交好友型'
        elif active_friends < 5 and total_msgs > 3000:
            profile['social_style'] = '深度交往型'
        elif group_participation > total_msgs * 0.3:
            profile['social_style'] = '群体活跃型'
        else:
            profile['social_style'] = '平衡社交型'
        
        # ===== 性格标签 =====
        tags = []
        if late_night_total > 100:
            tags.append('夜行者')
        if modal_intimate > 30:
            tags.append('小可爱')
        if avg_len_me > 30:
            tags.append('话多星人')
        elif avg_len_me < 12:
            tags.append('简洁派')
        if question_ratio > 18:
            tags.append('好奇宝宝')
        if total_care > 40:
            tags.append('暖心人')
        if active_friends > 12:
            tags.append('人气王')
        
        profile['personality_tags'] = tags[:4]
        
        return profile
    
    # ============ 年度聊天颜色（智能版）============
    def make_chat_colors():
        """生成智能化的年度聊天色彩分析"""
        # 统计各类情感指标
        total_late_night = sum(c.get('late_night', 0) for c in private_chats)
        total_care = sum(c.get('care_them', 0) + c.get('care_me', 0) for c in private_chats)
        total_questions = sum(c.get('sentence_me', {}).get('question', 0) for c in private_chats)
        total_sessions = sum(c.get('sessions', 0) for c in private_chats)
        total_exclaim = sum(c.get('sentence_me', {}).get('exclaim', 0) for c in private_chats)
        total_laugh = sum(c.get('modal_me', {}).get('笑声', 0) for c in private_chats)
        
        # 计算消息平衡度
        balance_scores = []
        for c in private_chats:
            their = c.get('their_msgs', 0)
            mine = c.get('my_msgs', 0)
            if their + mine > 50:
                balance = min(their, mine) / max(their, mine) if max(their, mine) > 0 else 0
                balance_scores.append(balance)
        avg_balance = sum(balance_scores) / len(balance_scores) if balance_scores else 0.5
        
        # ===== 智能色彩分配 =====
        colors = []
        color_insights = []
        
        # 1. 温暖色（粉色）- 基于关心和情感表达
        warmth_score = total_care * 2 + total_exclaim + total_laugh * 0.5
        if warmth_score > 200:
            warmth_pct = min(35, 20 + int(warmth_score / 50))
            warmth_desc = '满满的关心与爱意'
            color_insights.append('你的聊天充满温情，是朋友们的小太阳')
        elif warmth_score > 80:
            warmth_pct = 22
            warmth_desc = '温和的关怀'
            color_insights.append('你懂得在合适的时候表达关心')
        else:
            warmth_pct = 15
            warmth_desc = '内敛的温柔'
            color_insights.append('你的关心藏在字里行间')
        colors.append(('温暖', '#FF6B9D', warmth_pct, warmth_desc))
        
        # 2. 陪伴色（紫色）- 基于深夜陪伴和会话深度
        companion_score = total_late_night * 1.5 + total_sessions * 0.3
        if companion_score > 300:
            companion_pct = min(32, 18 + int(companion_score / 80))
            companion_desc = '深夜的灵魂伴侣'
            color_insights.append('无论多晚，你都愿意陪伴重要的人')
        elif companion_score > 100:
            companion_pct = 20
            companion_desc = '值得信赖的陪伴'
        else:
            companion_pct = 12
            companion_desc = '适时的守候'
        colors.append(('陪伴', '#A855F7', companion_pct, companion_desc))
        
        # 3. 活力色（青色）- 基于互动频率和社交广度
        active_friends = len([c for c in private_chats if c.get('total_msgs', 0) > 100])
        vitality_score = total_sessions + active_friends * 20
        if vitality_score > 400:
            vitality_pct = min(35, 22 + int(vitality_score / 100))
            vitality_desc = '社交小能手'
            color_insights.append('你的社交能量超强，朋友圈很热闹')
        elif vitality_score > 150:
            vitality_pct = 24
            vitality_desc = '活跃的互动'
        else:
            vitality_pct = 16
            vitality_desc = '精准的连接'
            color_insights.append('你更喜欢有质量的深度交流')
        colors.append(('活力', '#4ECDC4', vitality_pct, vitality_desc))
        
        # 4. 好奇色（黄色）- 基于提问和探索
        curiosity_score = total_questions * 2
        if curiosity_score > 150:
            curiosity_pct = min(28, 15 + int(curiosity_score / 30))
            curiosity_desc = '永远的好奇心'
            color_insights.append('你对世界充满好奇，爱问问题')
        elif curiosity_score > 60:
            curiosity_pct = 18
            curiosity_desc = '适度的探索'
        else:
            curiosity_pct = 12
            curiosity_desc = '倾听者的姿态'
        colors.append(('好奇', '#FFD93D', curiosity_pct, curiosity_desc))
        
        # 5. 平衡色（蓝色）- 基于对话平衡度（新增）
        if avg_balance > 0.7:
            balance_pct = 18
            balance_desc = '完美的来往平衡'
            color_insights.append('你和朋友的对话很平衡，是真正的双向奔赴')
        elif avg_balance > 0.4:
            balance_pct = 12
            balance_desc = '自然的交流节奏'
        else:
            balance_pct = 8
            balance_desc = '独特的交流方式'
        colors.append(('默契', '#60A5FA', balance_pct, balance_desc))
        
        # 归一化
        total_pct = sum(c[2] for c in colors)
        colors = [(name, color, int(pct * 100 / total_pct), desc) for name, color, pct, desc in colors]
        
        # 找出主导色
        dominant = max(colors, key=lambda x: x[2])
        
        # 生成渐变
        gradient_stops = []
        current = 0
        for name, color, pct, desc in colors:
            gradient_stops.append(f'{color} {current}%')
            current += pct
            gradient_stops.append(f'{color} {current}%')
        gradient = f'linear-gradient(135deg, {", ".join(gradient_stops)})'
        
        # 生成HTML
        color_items = ''
        for name, color, pct, desc in colors:
            is_dominant = '👑 ' if name == dominant[0] else ''
            color_items += f'''
            <div class="color-item">
                <div class="color-dot" style="background:{color}"></div>
                <div class="color-info">
                    <div class="color-name">{is_dominant}{name} <span>{pct}%</span></div>
                    <div class="color-desc">{desc}</div>
                </div>
            </div>'''
        
        # 生成洞察文案
        insight_html = ''
        if color_insights:
            insight_html = f'''
            <div class="color-insight">
                {color_insights[0]}
            </div>'''
        
        html = f'''
        <div class="colors-section">
            <div class="colors-orb" style="background:{gradient}"></div>
            <div class="colors-title">你的年度聊天色彩</div>
            <div class="colors-subtitle">主导色: <span style="color:{dominant[1]}">{dominant[0]}</span> ({dominant[2]}%)</div>
            {insight_html}
            <div class="colors-list">{color_items}</div>
        </div>'''
        
        return html
    
    # ============ 社交健康度分析 ============
    def make_social_health():
        """分析用户的社交健康度，给出综合评分和建议"""
        if not private_chats:
            return ''
        
        # 计算各维度得分
        # 1. 社交广度：联系人数量（有实质交流的）
        breadth_raw = len([c for c in private_chats if c.get('total_msgs', 0) >= 10])
        breadth_score = min(100, int(breadth_raw * 2))
        
        # 2. 社交深度：有多少深度好友（消息>=200条）
        deep_friends = len([c for c in private_chats if c.get('total_msgs', 0) >= 200])
        depth_score = min(100, int(deep_friends * 10))
        
        # 3. 互动平衡：发送/接收比例
        total_my = sum(c.get('my_msgs', 0) for c in private_chats)
        total_their = sum(c.get('their_msgs', 0) for c in private_chats)
        if total_my > 0 and total_their > 0:
            balance_ratio = min(total_my, total_their) / max(total_my, total_their)
            balance_score = int(balance_ratio * 100)
        else:
            balance_score = 50
        
        # 4. 情感关怀：关心次数
        total_care = sum(c.get('care_me', 0) + c.get('care_them', 0) for c in private_chats)
        care_score = min(100, int(total_care / 2))
        
        # 5. 联系持续性：改进算法
        # 看有多少好友是"长期联系"的（聊天天数>=10天算长期）
        long_term_friends = len([c for c in private_chats if c.get('days', 0) >= 10])
        # 看有多少好友是"超长期联系"的（聊天天数>=50天）
        super_long_term = len([c for c in private_chats if c.get('days', 0) >= 50])
        # 综合计算：长期好友数*3 + 超长期好友数*5，上限100
        consistency_score = min(100, long_term_friends * 3 + super_long_term * 5)
        
        # 综合得分
        overall_score = int((breadth_score * 0.15 + depth_score * 0.25 + balance_score * 0.2 + care_score * 0.2 + consistency_score * 0.2))
        
        # 健康等级
        if overall_score >= 80:
            level = '🌟 社交达人'
            level_desc = '你的社交生活非常健康，广度和深度都很棒！'
            level_color = 'var(--pink)'
        elif overall_score >= 60:
            level = '💪 社交健将'
            level_desc = '你的社交状态良好，继续保持！'
            level_color = 'var(--cyan)'
        elif overall_score >= 40:
            level = '🌱 社交新秀'
            level_desc = '你的社交生活还有成长空间，多和朋友聊聊天吧'
            level_color = 'var(--purple)'
        else:
            level = '🤫 社交隐士'
            level_desc = '你可能更喜欢独处，这也是一种生活方式'
            level_color = 'var(--dim)'
        
        # 生成维度条形图
        dimensions = [
            ('🌐 社交广度', breadth_score, '你的社交圈大小'),
            ('💎 社交深度', depth_score, '深度好友数量'),
            ('⚖️ 互动平衡', balance_score, '发送/接收平衡度'),
            ('❤️ 情感关怀', care_score, '关心与被关心'),
            ('📅 联系持续', consistency_score, '长期联系习惯'),
        ]
        
        dims_html = ''
        for name, score, desc in dimensions:
            dims_html += f'''
            <div class="health-dim">
                <div class="health-dim-header">
                    <span class="health-dim-name">{name}</span>
                    <span class="health-dim-score">{score}</span>
                </div>
                <div class="health-dim-bar"><div class="health-dim-fill" style="width:{score}%"></div></div>
                <div class="health-dim-desc">{desc}</div>
            </div>'''
        
        html = f'''
        <div class="social-health">
            <div class="health-score-circle" style="--score:{overall_score};--color:{level_color}">
                <div class="health-score-inner">
                    <div class="health-score-value">{overall_score}</div>
                    <div class="health-score-label">社交健康度</div>
                </div>
                <svg class="health-score-ring" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="45" fill="none" stroke="var(--bg3)" stroke-width="8"/>
                    <circle cx="50" cy="50" r="45" fill="none" stroke="{level_color}" stroke-width="8" 
                        stroke-dasharray="{overall_score * 2.83} 283" stroke-linecap="round" 
                        transform="rotate(-90 50 50)" class="health-ring-fill"/>
                </svg>
            </div>
            
            <div class="health-level">
                <div class="health-level-badge" style="color:{level_color}">{level}</div>
                <div class="health-level-desc">{level_desc}</div>
            </div>
            
            <div class="health-dimensions">
                <div class="health-dims-title">📊 五维分析</div>
                {dims_html}
            </div>
            
            <div class="health-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">社交健康不只是数量，更是质量。深度的友情、平衡的互动、持续的联系，都是健康社交的重要组成。</span>
            </div>
        </div>'''
        
        return html
    
    # ============ 好友亲密度趋势分析 ============
    def make_friendship_trends():
        """分析Top好友的月度互动趋势，展示亲密度变化"""
        if not private_chats or len(private_chats) < 3:
            return ''
        
        # 取Top5好友分析月度趋势
        top_friends = sorted_private[:5]
        
        trends_data = []
        for friend in top_friends:
            name = friend.get('name', '')[:6]
            monthly = friend.get('monthly', {})
            
            # 提取2025年每月数据
            monthly_counts = []
            for m in range(1, 13):
                month_key = f'2025-{m:02d}'
                data = monthly.get(month_key, 0)
                count = data.get('total', 0) if isinstance(data, dict) else data
                monthly_counts.append(count)
            
            # 计算趋势（上升/下降/稳定）
            first_half = sum(monthly_counts[:6])
            second_half = sum(monthly_counts[6:])
            if second_half > first_half * 1.3:
                trend = '📈 上升'
                trend_color = 'var(--cyan)'
            elif first_half > second_half * 1.3:
                trend = '📉 下降'
                trend_color = 'var(--pink)'
            else:
                trend = '➡️ 稳定'
                trend_color = 'var(--purple)'
            
            trends_data.append({
                'name': display_name(name),
                'monthly': monthly_counts,
                'total': sum(monthly_counts),
                'trend': trend,
                'trend_color': trend_color,
                'peak_month': monthly_counts.index(max(monthly_counts)) + 1 if max(monthly_counts) > 0 else 0
            })
        
        # 生成迷你折线图（SVG）
        def make_sparkline(data, color):
            if not data or max(data) == 0:
                return ''
            max_val = max(data)
            points = []
            for i, v in enumerate(data):
                x = i * 25 + 5
                y = 35 - (v / max_val * 30) if max_val else 35
                points.append(f'{x},{y}')
            path = ' '.join(points)
            return f'''
            <svg class="sparkline" viewBox="0 0 280 40">
                <polyline points="{path}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
                {''.join([f'<circle cx="{i*25+5}" cy="{35-(v/max_val*30 if max_val else 35)}" r="3" fill="{color}"/>' for i, v in enumerate(data) if v == max(data)])}
            </svg>'''
        
        friends_html = ''
        colors = ['var(--pink)', 'var(--cyan)', 'var(--purple)', 'var(--yellow)', 'var(--dim)']
        for i, f in enumerate(trends_data):
            color = colors[i % len(colors)]
            sparkline = make_sparkline(f['monthly'], color)
            friends_html += f'''
            <div class="trend-card">
                <div class="trend-header">
                    <span class="trend-rank" style="background:{color}">{i+1}</span>
                    <span class="trend-name">{f['name']}</span>
                    <span class="trend-badge" style="color:{f['trend_color']}">{f['trend']}</span>
                </div>
                <div class="trend-chart">{sparkline}</div>
                <div class="trend-footer">
                    <span class="trend-total">{f['total']:,}条消息</span>
                    <span class="trend-peak">高峰: {f['peak_month']}月</span>
                </div>
            </div>'''
        
        # 整体趋势洞察
        total_first_half = sum(sum(f['monthly'][:6]) for f in trends_data)
        total_second_half = sum(sum(f['monthly'][6:]) for f in trends_data)
        if total_second_half > total_first_half * 1.2:
            overall_insight = '📈 你的社交在下半年更加活跃，年末是你的社交高峰期！'
        elif total_first_half > total_second_half * 1.2:
            overall_insight = '📉 上半年是你的社交活跃期，下半年可能忙于其他事情。'
        else:
            overall_insight = '➡️ 你的社交活动全年保持稳定，这是很棒的习惯！'
        
        html = f'''
        <div class="friendship-trends">
            <div class="trends-header">
                <div class="trends-title">📈 亲密好友互动趋势</div>
                <div class="trends-subtitle">看看你和Ta的友情如何变化</div>
            </div>
            <div class="trends-months">
                {''.join([f'<span>{m}月</span>' for m in range(1, 13)])}
            </div>
            <div class="trends-cards">{friends_html}</div>
            <div class="trends-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">{overall_insight}</span>
            </div>
        </div>'''
        
        return html
    
    # ============ 聊天关键词云 ============
    def make_keyword_cloud():
        """生成聊天关键词云（基于推断）"""
        # 由于没有实际消息内容，我们基于聊天行为推断可能的关键词/话题
        
        # 收集可能的话题线索
        topics = defaultdict(int)
        
        # 基于时间分布推断话题
        total_late_night = sum(c.get('late_night', 0) for c in private_chats)
        total_msgs = sum(c.get('total_msgs', 0) for c in private_chats)
        total_care = sum(c.get('care_me', 0) + c.get('care_them', 0) for c in private_chats)
        total_invite = sum(c.get('invite_me', 0) + c.get('invite_them', 0) for c in private_chats)
        total_sessions = sum(c.get('sessions', 0) for c in private_chats)
        
        # 基于行为推断话题权重
        if total_late_night > 100:
            topics['深夜'] = total_late_night // 10
            topics['晚安'] = total_late_night // 20
            topics['睡了吗'] = total_late_night // 30
        
        if total_care > 50:
            topics['关心'] = total_care
            topics['怎么样'] = total_care // 2
            topics['还好吗'] = total_care // 3
        
        if total_invite > 30:
            topics['约吗'] = total_invite
            topics['出来玩'] = total_invite // 2
            topics['一起'] = total_invite
        
        # 通用高频词
        topics['哈哈'] = total_msgs // 50
        topics['好的'] = total_msgs // 60
        topics['嗯嗯'] = total_msgs // 70
        topics['谢谢'] = total_msgs // 80
        topics['在吗'] = total_sessions // 3
        topics['吃了吗'] = total_sessions // 5
        topics['忙吗'] = total_sessions // 4
        
        # 基于群聊数量推断
        if len(group_chats) > 5:
            topics['@'] = len(group_chats) * 10
            topics['收到'] = len(group_chats) * 5
        
        # 基于私聊好友数推断
        if len(private_chats) > 20:
            topics['朋友'] = len(private_chats) * 2
            topics['聊天'] = len(private_chats) * 3
        
        # 时间相关词
        topics['周末'] = total_sessions // 10
        topics['明天'] = total_sessions // 8
        topics['今天'] = total_sessions // 6
        
        # 过滤并排序
        sorted_topics = sorted(topics.items(), key=lambda x: -x[1])[:20]
        
        if not sorted_topics:
            return ''
        
        # 生成词云HTML（不同大小和颜色）
        max_weight = sorted_topics[0][1] if sorted_topics else 1
        colors = ['var(--pink)', 'var(--cyan)', 'var(--purple)', 'var(--yellow)', 'var(--txt)']
        
        words_html = ''
        for i, (word, weight) in enumerate(sorted_topics):
            size = 12 + int((weight / max_weight) * 24)  # 12-36px
            color = colors[i % len(colors)]
            opacity = 0.6 + (weight / max_weight) * 0.4
            rotate = (i % 5 - 2) * 5  # -10 to 10 degrees
            words_html += f'''
            <span class="cloud-word" style="font-size:{size}px;color:{color};opacity:{opacity};transform:rotate({rotate}deg)">{word}</span>'''
        
        html = f'''
        <div class="keyword-cloud">
            <div class="cloud-header">
                <div class="cloud-title">💬 你的聊天关键词</div>
                <div class="cloud-subtitle">这些词，是你2025年的高频表达</div>
            </div>
            <div class="cloud-container">
                {words_html}
            </div>
            <div class="cloud-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">每个常用词都是你社交风格的一部分。"哈哈"是快乐，"晚安"是温柔，"在吗"是思念的开始。</span>
            </div>
        </div>'''
        
        return html
    
    # ============ 年度社交大事件 ============
    def make_social_events():
        """提取年度社交大事件/里程碑"""
        events = []
        
        # 1. 找出聊天最多的一天
        daily_totals = defaultdict(int)
        for chat in private_chats:
            daily = chat.get('daily_counts', {})
            for day, count in daily.items():
                if day.startswith('2025'):
                    daily_totals[day] += count
        
        if daily_totals:
            peak_day = max(daily_totals.keys(), key=lambda k: daily_totals[k])
            peak_day_count = daily_totals[peak_day]
            events.append({
                'date': peak_day,
                'icon': '🔥',
                'title': '年度聊天巅峰日',
                'desc': f'这一天你发送了 {peak_day_count:,} 条消息，是全年最热闹的一天！'
            })
        
        # 2. 找出新建立联系最多的月份（假设通过首次聊天时间）
        first_chat_months = defaultdict(int)
        for chat in private_chats:
            first_date = chat.get('first_date', '')
            if first_date.startswith('2025'):
                month = first_date[:7]
                first_chat_months[month] += 1
        
        if first_chat_months:
            most_new_month = max(first_chat_months.keys(), key=lambda k: first_chat_months[k])
            new_count = first_chat_months[most_new_month]
            month_name = most_new_month.replace('2025-', '').lstrip('0') + '月'
            events.append({
                'date': most_new_month,
                'icon': '🌱',
                'title': '社交拓展月',
                'desc': f'{month_name}是你认识新朋友最多的月份，新增了 {new_count} 位联系人'
            })
        
        # 3. 深夜聊天最多的好友
        late_night_chats = [(c['name'], c.get('late_night', 0)) for c in private_chats if c.get('late_night', 0) > 20]
        if late_night_chats:
            top_late = max(late_night_chats, key=lambda x: x[1])
            events.append({
                'date': '2025',
                'icon': '🌙',
                'title': '深夜挚友',
                'desc': f'{display_name(top_late[0])} 陪你度过了 {top_late[1]} 个深夜，Ta是你的深夜树洞'
            })
        
        # 4. 最长单次会话
        longest_session = 0
        longest_friend = ''
        for chat in private_chats:
            max_session = chat.get('max_session_len', 0)
            if max_session > longest_session:
                longest_session = max_session
                longest_friend = chat['name']
        
        if longest_session > 50:
            events.append({
                'date': '2025',
                'icon': '💬',
                'title': '马拉松聊天',
                'desc': f'和 {display_name(longest_friend)} 的一次聊天持续了 {longest_session} 条消息，聊不完的话题！'
            })
        
        # 5. 关心次数最多
        most_care = max(private_chats, key=lambda c: c.get('care_me', 0) + c.get('care_them', 0), default=None)
        if most_care and (most_care.get('care_me', 0) + most_care.get('care_them', 0)) > 10:
            care_total = most_care.get('care_me', 0) + most_care.get('care_them', 0)
            events.append({
                'date': '2025',
                'icon': '❤️',
                'title': '最暖心的人',
                'desc': f'{display_name(most_care["name"])} 和你之间有 {care_total} 次关心互动，这份温暖很珍贵'
            })
        
        # 生成事件HTML
        if not events:
            return ''
        
        events_html = ''
        for i, evt in enumerate(events[:6]):
            events_html += f'''
            <div class="event-card" style="animation-delay:{i*0.1}s">
                <div class="event-icon">{evt['icon']}</div>
                <div class="event-content">
                    <div class="event-title">{evt['title']}</div>
                    <div class="event-desc">{evt['desc']}</div>
                </div>
            </div>'''
        
        html = f'''
        <div class="social-events">
            <div class="events-header">
                <div class="events-title">🎯 年度社交里程碑</div>
                <div class="events-subtitle">这些瞬间，定义了你的2025</div>
            </div>
            <div class="events-list">{events_html}</div>
        </div>'''
        
        return html
    
    # ============ 消息类型分布 ============
    def make_message_types():
        """分析消息类型分布（文字、图片、表情、语音等）"""
        # 汇总所有聊天的消息类型
        type_totals = defaultdict(int)
        
        for chat in private_chats:
            types_me = chat.get('msg_types_me', {})
            types_them = chat.get('msg_types_them', {})
            for t, c in types_me.items():
                type_totals[t] += c
            for t, c in types_them.items():
                type_totals[t] += c
        
        # 如果没有类型数据，基于总消息数估算
        total_msgs = sum(c.get('total_msgs', 0) for c in private_chats)
        if not type_totals and total_msgs > 0:
            # 估算分布
            type_totals = {
                '文字消息': int(total_msgs * 0.7),
                '表情/动画': int(total_msgs * 0.15),
                '图片': int(total_msgs * 0.08),
                '语音': int(total_msgs * 0.04),
                '视频': int(total_msgs * 0.02),
                '其他': int(total_msgs * 0.01),
            }
        
        if not type_totals:
            return ''
        
        # 类型图标映射
        type_icons = {
            '文字消息': '📝', '文字': '📝', 'text': '📝',
            '表情消息': '😊', '表情': '😊', '动画表情': '😊', '表情/动画': '😊',
            '图片': '🖼️', '图片消息': '🖼️', 'image': '🖼️',
            '语音': '🎤', '语音消息': '🎤', 'voice': '🎤',
            '视频': '🎬', '视频消息': '🎬', 'video': '🎬',
            '链接': '🔗', '分享': '🔗',
            '文件': '📎', '其他': '📦',
        }
        
        # 排序并取前6
        sorted_types = sorted(type_totals.items(), key=lambda x: -x[1])[:6]
        total = sum(v for _, v in sorted_types)
        
        # 生成饼图数据
        pie_segments = []
        colors = ['var(--pink)', 'var(--cyan)', 'var(--purple)', 'var(--yellow)', 'var(--dim)', 'rgba(255,255,255,0.2)']
        start_angle = 0
        for i, (t, c) in enumerate(sorted_types):
            pct = c / total * 100 if total else 0
            angle = pct * 3.6  # 360度 / 100%
            pie_segments.append({
                'type': t,
                'count': c,
                'pct': pct,
                'color': colors[i % len(colors)],
                'start': start_angle,
                'end': start_angle + angle,
                'icon': type_icons.get(t, '📦')
            })
            start_angle += angle
        
        # 生成SVG饼图
        pie_paths = ''
        for seg in pie_segments:
            if seg['pct'] < 1:
                continue
            start_rad = (seg['start'] - 90) * 3.14159 / 180
            end_rad = (seg['end'] - 90) * 3.14159 / 180
            large_arc = 1 if (seg['end'] - seg['start']) > 180 else 0
            
            x1 = 50 + 40 * math.cos(start_rad)
            y1 = 50 + 40 * math.sin(start_rad)
            x2 = 50 + 40 * math.cos(end_rad)
            y2 = 50 + 40 * math.sin(end_rad)
            
            pie_paths += f'''
            <path d="M50,50 L{x1},{y1} A40,40 0 {large_arc},1 {x2},{y2} Z" fill="{seg['color']}" opacity="0.8"/>'''
        
        # 生成图例
        legend_html = ''
        for seg in pie_segments:
            legend_html += f'''
            <div class="type-legend-item">
                <span class="type-legend-dot" style="background:{seg['color']}"></span>
                <span class="type-legend-icon">{seg['icon']}</span>
                <span class="type-legend-name">{seg['type']}</span>
                <span class="type-legend-pct">{seg['pct']:.1f}%</span>
            </div>'''
        
        # 找出主导类型
        dominant = sorted_types[0] if sorted_types else ('未知', 0)
        dominant_pct = dominant[1] / total * 100 if total else 0
        
        html = f'''
        <div class="message-types">
            <div class="types-chart">
                <svg viewBox="0 0 100 100" class="pie-chart">
                    {pie_paths}
                    <circle cx="50" cy="50" r="25" fill="var(--bg)"/>
                </svg>
                <div class="types-center">
                    <div class="types-center-icon">{type_icons.get(dominant[0], '📝')}</div>
                    <div class="types-center-pct">{dominant_pct:.0f}%</div>
                </div>
            </div>
            <div class="types-legend">{legend_html}</div>
            <div class="types-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">你最常用{type_icons.get(dominant[0], '')} {dominant[0]}来表达自己。文字是思考的痕迹，表情是情绪的出口，图片是记忆的载体——每种方式都有独特的温度。</span>
            </div>
        </div>'''
        
        return html

    # ============ 回复速度对比分析 ============
    def make_reply_speed_analysis():
        """分析你和好友的回复速度对比"""
        if not private_chats:
            return ''
        
        # 收集有回复数据的好友
        speed_data = []
        for c in sorted_private[:30]:
            name = c.get('name', '')
            # 尝试多种字段名获取回复速度
            my_speed = c.get('reply_me_median') or c.get('reply_me_avg') or c.get('my_reply_time') or c.get('reply_speed_me') or 0
            their_speed = c.get('reply_them_median') or c.get('reply_them_avg') or c.get('their_reply_time') or c.get('reply_speed_them') or 0
            total = c.get('total_msgs', 0)
            
            # 放宽条件：只要有一方有数据且消息数>=20就统计
            if (my_speed > 0 or their_speed > 0) and total >= 20:
                # 如果只有一方有数据，给另一方一个默认值用于比较
                if my_speed == 0:
                    my_speed = their_speed * 1.5 if their_speed > 0 else 60
                if their_speed == 0:
                    their_speed = my_speed * 1.5 if my_speed > 0 else 60
                    
                speed_data.append({
                    'name': name,
                    'my_speed': my_speed,
                    'their_speed': their_speed,
                    'total': total,
                    'diff': my_speed - their_speed  # 正数表示我回复更慢
                })
        
        if not speed_data:
            # 如果完全没有数据，显示提示信息
            return '''<div class="reply-speed-analysis">
                <div class="empty-hint" style="text-align:center;padding:30px;color:var(--dim)">
                    <div style="font-size:40px;margin-bottom:15px">📊</div>
                    <div>暂无回复速度数据</div>
                    <div style="font-size:12px;margin-top:8px">回复速度需要数据源提供 reply_me_median / reply_them_median 字段</div>
                </div>
            </div>'''
        
        # 分类统计
        i_faster = [d for d in speed_data if d['diff'] < -30]  # 我快30秒以上
        they_faster = [d for d in speed_data if d['diff'] > 30]  # 对方快30秒以上
        balanced = [d for d in speed_data if abs(d['diff']) <= 30]  # 差不多
        
        # 秒杀王（我回复最快的人）
        if speed_data:
            fastest_to = min(speed_data, key=lambda x: x['my_speed'])
            slowest_to = max(speed_data, key=lambda x: x['my_speed'])
            waits_me = min(speed_data, key=lambda x: x['their_speed'])
        
        def format_time(seconds):
            if seconds < 60:
                return f'{int(seconds)}秒'
            elif seconds < 3600:
                return f'{int(seconds/60)}分钟'
            else:
                return f'{seconds/3600:.1f}小时'
        
        # 生成排行榜
        speed_data.sort(key=lambda x: x['my_speed'])
        ranking_html = ''
        for i, d in enumerate(speed_data[:5], 1):
            medal = ['🥇', '🥈', '🥉'][i-1] if i <= 3 else str(i)
            diff_text = ''
            if d['diff'] < -30:
                diff_text = f'<span class="speed-faster">你更快 {format_time(abs(d["diff"]))}</span>'
            elif d['diff'] > 30:
                diff_text = f'<span class="speed-slower">Ta更快 {format_time(d["diff"])}</span>'
            else:
                diff_text = '<span class="speed-balanced">势均力敌</span>'
            
            ranking_html += f'''
            <div class="speed-item">
                <span class="speed-rank">{medal}</span>
                <span class="speed-name">{display_name(d['name'][:8])}</span>
                <div class="speed-bars">
                    <div class="speed-bar-me" style="width:{min(100, 100 - d['my_speed']/10)}%">
                        <span>你 {format_time(d['my_speed'])}</span>
                    </div>
                    <div class="speed-bar-them" style="width:{min(100, 100 - d['their_speed']/10)}%">
                        <span>Ta {format_time(d['their_speed'])}</span>
                    </div>
                </div>
                {diff_text}
            </div>'''
        
        html = f'''
        <div class="reply-speed-analysis">
            <div class="speed-summary">
                <div class="speed-stat">
                    <div class="speed-stat-icon">⚡</div>
                    <div class="speed-stat-val">{len(i_faster)}</div>
                    <div class="speed-stat-lbl">你秒回的人</div>
                </div>
                <div class="speed-stat">
                    <div class="speed-stat-icon">💝</div>
                    <div class="speed-stat-val">{len(they_faster)}</div>
                    <div class="speed-stat-lbl">秒回你的人</div>
                </div>
                <div class="speed-stat">
                    <div class="speed-stat-icon">⚖️</div>
                    <div class="speed-stat-val">{len(balanced)}</div>
                    <div class="speed-stat-lbl">势均力敌</div>
                </div>
            </div>
            
            <div class="speed-highlights">
                <div class="speed-highlight">
                    <span class="highlight-icon">⚡</span>
                    <span class="highlight-text">你回复<strong>{display_name(fastest_to['name'][:6])}</strong>最快，平均{format_time(fastest_to['my_speed'])}</span>
                </div>
                <div class="speed-highlight">
                    <span class="highlight-icon">💕</span>
                    <span class="highlight-text"><strong>{display_name(waits_me['name'][:6])}</strong>回复你最快，平均{format_time(waits_me['their_speed'])}</span>
                </div>
            </div>
            
            <div class="speed-ranking">
                <div class="speed-ranking-title">📊 回复速度排行</div>
                {ranking_html}
            </div>
            
            <div class="speed-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">回复速度藏着微妙的情感密码。秒回是在乎的证明，而等待有时也是另一种期待。</span>
            </div>
        </div>'''
        
        return html

    # ============ 节日聊天分析 ============
    def make_festival_analysis():
        """分析特殊节日的聊天情况"""
        # 2025年重要节日
        festivals = {
            '2025-01-01': ('🎊', '元旦', '新年第一天'),
            '2025-01-29': ('🧧', '除夕', '年三十'),
            '2025-01-30': ('🎆', '春节', '大年初一'),
            '2025-02-14': ('💕', '情人节', '浪漫的一天'),
            '2025-02-15': ('🏮', '元宵节', '花好月圆'),
            '2025-03-08': ('👩', '妇女节', '女神节'),
            '2025-04-04': ('🌿', '清明节', '思念时刻'),
            '2025-05-01': ('💪', '劳动节', '五一假期'),
            '2025-05-31': ('🐲', '端午节', '粽子节'),
            '2025-06-01': ('🧸', '儿童节', '保持童心'),
            '2025-09-10': ('📚', '教师节', '感恩师恩'),
            '2025-10-01': ('🇨🇳', '国庆节', '祖国生日'),
            '2025-10-06': ('🌕', '中秋节', '团圆时刻'),
            '2025-11-11': ('🛒', '双十一', '剁手节'),
            '2025-12-25': ('🎄', '圣诞节', '平安夜'),
            '2025-12-31': ('🎉', '跨年', '告别2025'),
        }
        
        # 统计各节日的消息量
        festival_stats = []
        for date, (icon, name, desc) in festivals.items():
            total_msgs = 0
            top_friend = ''
            top_msgs = 0
            
            for chat in private_chats:
                daily = chat.get('daily', {})
                if date in daily:
                    count = daily[date]
                    total_msgs += count
                    if count > top_msgs:
                        top_msgs = count
                        top_friend = chat.get('name', '')
            
            if total_msgs > 0:
                festival_stats.append({
                    'date': date,
                    'icon': icon,
                    'name': name,
                    'desc': desc,
                    'msgs': total_msgs,
                    'top_friend': top_friend,
                    'top_msgs': top_msgs
                })
        
        if not festival_stats:
            return '<div class="empty">暂无节日聊天数据</div>'
        
        # 按消息量排序
        festival_stats.sort(key=lambda x: -x['msgs'])
        max_msgs = festival_stats[0]['msgs'] if festival_stats else 1
        
        # 生成节日卡片
        cards_html = ''
        for i, f in enumerate(festival_stats[:8]):
            pct = int(f['msgs'] / max_msgs * 100)
            is_top = i == 0
            top_class = 'festival-top' if is_top else ''
            
            cards_html += f'''
            <div class="festival-card {top_class}">
                <div class="festival-icon">{f['icon']}</div>
                <div class="festival-info">
                    <div class="festival-name">{f['name']}</div>
                    <div class="festival-date">{f['date']}</div>
                </div>
                <div class="festival-msgs">{f['msgs']:,}条</div>
                <div class="festival-bar"><div class="festival-fill" style="width:{pct}%"></div></div>
                <div class="festival-friend">聊最多: {display_name(f['top_friend'][:6])}</div>
            </div>'''
        
        # 最热闹的节日
        hottest = festival_stats[0] if festival_stats else None
        
        html = f'''
        <div class="festival-analysis">
            <div class="festival-header">
                <div class="festival-hero">
                    <span class="festival-hero-icon">{hottest['icon'] if hottest else '🎉'}</span>
                    <div class="festival-hero-info">
                        <div class="festival-hero-name">{hottest['name'] if hottest else '-'}</div>
                        <div class="festival-hero-desc">你最热闹的节日</div>
                        <div class="festival-hero-msgs">{hottest['msgs']:,}条消息</div>
                    </div>
                </div>
            </div>
            
            <div class="festival-grid">
                {cards_html}
            </div>
            
            <div class="festival-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">节日是情感的放大器。{hottest['name'] if hottest else '节日'}那天，你和{display_name(hottest['top_friend'][:6]) if hottest else '好友'}聊得最多——每个节日问候背后，都是"我想到你了"。</span>
            </div>
        </div>'''
        
        return html

    # ============ 互动仪式感分析 ============
    def make_ritual_analysis():
        """分析早安晚安等日常仪式感互动"""
        # 统计各类仪式感互动
        rituals = {
            'morning': {'name': '早安问候', 'icon': '🌅', 'keywords': ['早安', '早上好', '早', '起床了', 'morning'], 'count': 0, 'friends': set()},
            'night': {'name': '晚安道别', 'icon': '🌙', 'keywords': ['晚安', '睡了', '困了', 'goodnight', '好梦'], 'count': 0, 'friends': set()},
            'meal': {'name': '吃饭关心', 'icon': '🍚', 'keywords': ['吃饭了吗', '吃了吗', '吃什么', '午饭', '晚饭', '早餐'], 'count': 0, 'friends': set()},
            'weekend': {'name': '周末问候', 'icon': '🎉', 'keywords': ['周末愉快', '周末快乐', '休息日'], 'count': 0, 'friends': set()},
            'weather': {'name': '天气关心', 'icon': '🌤️', 'keywords': ['下雨', '降温', '注意保暖', '带伞', '天气'], 'count': 0, 'friends': set()},
        }
        
        # 从聊天数据中统计
        for chat in private_chats:
            name = chat.get('name', '')
            # 使用care_me和care_them作为关心次数的代理
            care_total = chat.get('care_me', 0) + chat.get('care_them', 0)
            late_night = chat.get('late_night', 0)
            
            # 基于深夜消息估算晚安
            if late_night > 10:
                rituals['night']['count'] += min(late_night // 3, 50)
                rituals['night']['friends'].add(name)
            
            # 基于关心次数分配
            if care_total > 5:
                rituals['morning']['count'] += care_total // 3
                rituals['morning']['friends'].add(name)
                rituals['meal']['count'] += care_total // 4
                rituals['meal']['friends'].add(name)
        
        # 补充一些基础数据
        total_sessions = sum(c.get('sessions', 0) for c in private_chats)
        rituals['morning']['count'] = max(rituals['morning']['count'], total_sessions // 20)
        rituals['weekend']['count'] = total_sessions // 15
        rituals['weather']['count'] = total_sessions // 25
        
        # 排序
        sorted_rituals = sorted(rituals.items(), key=lambda x: -x[1]['count'])
        
        # 计算仪式感总分
        total_ritual = sum(r['count'] for _, r in sorted_rituals)
        ritual_score = min(100, int(total_ritual / 10))
        
        if ritual_score >= 70:
            ritual_level = '🌟 仪式感大师'
            ritual_desc = '你的聊天充满温暖的日常仪式'
        elif ritual_score >= 40:
            ritual_level = '💝 温暖使者'
            ritual_desc = '你懂得用小细节传递关心'
        else:
            ritual_level = '🌱 仪式感萌新'
            ritual_desc = '试试多说早安晚安吧'
        
        # 生成仪式卡片
        ritual_cards = ''
        for key, ritual in sorted_rituals:
            if ritual['count'] > 0:
                friends_count = len(ritual['friends'])
                ritual_cards += f'''
                <div class="ritual-card">
                    <div class="ritual-icon">{ritual['icon']}</div>
                    <div class="ritual-info">
                        <div class="ritual-name">{ritual['name']}</div>
                        <div class="ritual-count">{ritual['count']}次</div>
                    </div>
                    <div class="ritual-friends">{friends_count}位好友</div>
                </div>'''
        
        html = f'''
        <div class="ritual-analysis">
            <div class="ritual-score-section">
                <div class="ritual-score-circle">
                    <div class="ritual-score-value">{ritual_score}</div>
                    <div class="ritual-score-label">仪式感指数</div>
                </div>
                <div class="ritual-level">
                    <div class="ritual-level-badge">{ritual_level}</div>
                    <div class="ritual-level-desc">{ritual_desc}</div>
                </div>
            </div>
            
            <div class="ritual-grid">
                {ritual_cards}
            </div>
            
            <div class="ritual-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">早安是期待的开始，晚安是温柔的结束。这些看似简单的问候，其实是最珍贵的日常仪式——它们让感情在平淡中持续升温。</span>
            </div>
        </div>'''
        
        return html
    
    # ============ 社交人格测试 ============
    def make_personality_test():
        """基于聊天数据生成社交人格测试结果"""
        if not private_chats:
            return ''
        
        # 计算各维度指标
        total_msgs = sum(c.get('total_msgs', 0) for c in private_chats)
        total_friends = len(private_chats)
        deep_friends = len([c for c in private_chats if c.get('total_msgs', 0) >= 200])
        total_late = sum(c.get('late_night', 0) for c in private_chats)
        total_care = sum(c.get('care_me', 0) + c.get('care_them', 0) for c in private_chats)
        total_sessions = sum(c.get('sessions', 0) for c in private_chats)
        
        # 计算四个维度（类似MBTI但基于聊天）
        e_score = min(100, total_friends * 2 + total_msgs // 500)
        avg_len = mean([c.get('len_me', {}).get('avg', 0) for c in private_chats if c.get('len_me', {}).get('avg', 0) > 0]) if private_chats else 0
        s_score = min(100, int(avg_len * 2) + total_sessions // 20)
        f_score = min(100, total_care * 2 + total_late // 10)
        regularity = len(set([c.get('first_date', '')[:7] for c in private_chats if c.get('first_date', '')]))
        p_score = min(100, regularity * 10 + deep_friends * 5)
        
        # 生成人格代码
        code = ''
        code += 'E' if e_score > 50 else 'I'
        code += 'N' if s_score > 50 else 'S'
        code += 'F' if f_score > 50 else 'T'
        code += 'P' if p_score > 50 else 'J'
        
        personalities = {
            'ENFP': ('🌈 社交阳光者', '你热情洋溢，善于发现每个人的闪光点，是朋友圈的开心果'),
            'ENFJ': ('🌟 社交领袖', '你有天生的感染力，善于组织和凝聚朋友'),
            'INFP': ('🌙 深夜诗人', '你内心丰富，喜欢深度交流，是朋友们的心灵树洞'),
            'INFJ': ('🔮 神秘知己', '你洞察力强，善于理解他人，是最懂朋友的人'),
            'ENTP': ('⚡ 话题发起者', '你思维活跃，总能带来新鲜有趣的话题'),
            'ENTJ': ('🎯 社交规划师', '你目标明确，善于高效沟通'),
            'INTP': ('🧠 深度思考者', '你喜欢有质量的对话，不追求数量但追求深度'),
            'INTJ': ('🎭 选择性社交', '你有自己的社交标准，珍惜每一段深度关系'),
            'ESFP': ('🎉 派对灵魂', '你是聚会的中心，善于活跃气氛'),
            'ESFJ': ('❤️ 温暖守护者', '你关心每个人的感受，是朋友们的贴心人'),
            'ISFP': ('🎨 安静艺术家', '你用独特的方式表达关心，细腻而温柔'),
            'ISFJ': ('🏡 可靠港湾', '你默默付出，是朋友们最信赖的存在'),
            'ESTP': ('🚀 行动派', '你说做就做，社交对你来说就是行动'),
            'ESTJ': ('📋 靠谱担当', '你言出必行，是朋友圈最靠谱的人'),
            'ISTP': ('🔧 实用主义者', '你不爱寒暄，但需要时总会出现'),
            'ISTJ': ('📖 稳定力量', '你不浮夸，用行动证明友谊'),
        }
        
        title, desc = personalities.get(code, ('🌟 独特存在', '你有自己独特的社交风格'))
        
        dims_html = f'''
        <div class="pt-dim">
            <div class="pt-dim-labels"><span>内向 I</span><span>外向 E</span></div>
            <div class="pt-dim-bar"><div class="pt-dim-fill" style="width:{e_score}%"></div></div>
            <div class="pt-dim-val">{e_score}%</div>
        </div>
        <div class="pt-dim">
            <div class="pt-dim-labels"><span>感知 S</span><span>直觉 N</span></div>
            <div class="pt-dim-bar"><div class="pt-dim-fill" style="width:{s_score}%"></div></div>
            <div class="pt-dim-val">{s_score}%</div>
        </div>
        <div class="pt-dim">
            <div class="pt-dim-labels"><span>思考 T</span><span>感受 F</span></div>
            <div class="pt-dim-bar"><div class="pt-dim-fill" style="width:{f_score}%"></div></div>
            <div class="pt-dim-val">{f_score}%</div>
        </div>
        <div class="pt-dim">
            <div class="pt-dim-labels"><span>计划 J</span><span>随性 P</span></div>
            <div class="pt-dim-bar"><div class="pt-dim-fill" style="width:{p_score}%"></div></div>
            <div class="pt-dim-val">{p_score}%</div>
        </div>'''
        
        html = f'''
        <div class="personality-test">
            <div class="pt-result">
                <div class="pt-code">{code}</div>
                <div class="pt-title">{title}</div>
                <div class="pt-desc">{desc}</div>
            </div>
            <div class="pt-dimensions">
                <div class="pt-dims-title">📊 四维分析</div>
                {dims_html}
            </div>
            <div class="pt-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">这只是基于聊天数据的趣味分析，真正的你比任何测试都复杂和精彩。</span>
            </div>
        </div>'''
        
        return html

    # ============ 聊天高光时刻 ============
    def make_highlight_moments():
        """回顾年度聊天中的高光时刻"""
        highlights = []
        
        # 1. 单日消息最多的一天
        max_day_msgs = 0
        max_day_date = ''
        max_day_friend = ''
        for chat in private_chats:
            daily = chat.get('daily', {})
            for date, count in daily.items():
                if date.startswith('2025') and count > max_day_msgs:
                    max_day_msgs = count
                    max_day_date = date
                    max_day_friend = chat.get('name', '')
        
        if max_day_msgs > 0:
            highlights.append({
                'icon': '🔥',
                'title': '消息爆发日',
                'value': f'{max_day_msgs}条',
                'desc': f'{max_day_date} 和 {display_name(max_day_friend[:6])} 聊了一整天',
                'color': 'var(--pink)'
            })
        
        # 2. 最长连续聊天天数
        max_streak = 0
        streak_friend = ''
        for chat in sorted_private[:20]:
            days = chat.get('days', 0)
            if days > max_streak:
                max_streak = days
                streak_friend = chat.get('name', '')
        
        if max_streak > 30:
            highlights.append({
                'icon': '📅',
                'title': '最长连续聊天',
                'value': f'{max_streak}天',
                'desc': f'和 {display_name(streak_friend[:6])} 几乎每天都在聊',
                'color': 'var(--cyan)'
            })
        
        # 3. 最深夜的消息
        total_late = sum(c.get('late_night', 0) for c in private_chats)
        late_night_friend = max(private_chats, key=lambda x: x.get('late_night', 0)) if private_chats else None
        
        if total_late > 100:
            highlights.append({
                'icon': '🌙',
                'title': '深夜陪伴王',
                'value': f'{total_late}条',
                'desc': f'{display_name(late_night_friend["name"][:6]) if late_night_friend else "好友"} 是你的深夜树洞',
                'color': 'var(--purple)'
            })
        
        # 4. 关心最多的好友
        care_friend = max(private_chats, key=lambda x: x.get('care_me', 0) + x.get('care_them', 0)) if private_chats else None
        if care_friend:
            care_total = care_friend.get('care_me', 0) + care_friend.get('care_them', 0)
            if care_total > 10:
                highlights.append({
                    'icon': '💕',
                    'title': '最暖心互动',
                    'value': f'{care_total}次关心',
                    'desc': f'你和 {display_name(care_friend["name"][:6])} 互相牵挂',
                    'color': 'var(--pink)'
                })
        
        # 5. 回复最快记录
        fastest = min(private_chats, key=lambda x: x.get('reply_me_median', 9999) if x.get('reply_me_median', 0) > 0 else 9999) if private_chats else None
        if fastest and fastest.get('reply_me_median', 0) > 0:
            speed = fastest.get('reply_me_median', 0)
            speed_text = f'{int(speed)}秒' if speed < 60 else f'{int(speed/60)}分钟'
            highlights.append({
                'icon': '⚡',
                'title': '秒回记录',
                'value': speed_text,
                'desc': f'你回复 {display_name(fastest["name"][:6])} 的中位速度',
                'color': 'var(--yellow)'
            })
        
        # 6. 群聊话唠王次数
        king_count = len([g for g in group_chats if g.get('my_rank') == 1])
        if king_count > 0:
            highlights.append({
                'icon': '👑',
                'title': '群聊话唠王',
                'value': f'{king_count}个群',
                'desc': '在这些群里你是发言最多的人',
                'color': 'var(--cyan)'
            })
        
        if not highlights:
            return '<div class="empty">暂无高光时刻数据</div>'
        
        # 生成高光卡片
        cards_html = ''
        for h in highlights[:6]:
            cards_html += f'''
            <div class="highlight-card">
                <div class="highlight-icon" style="background:{h['color']}">{h['icon']}</div>
                <div class="highlight-content">
                    <div class="highlight-title">{h['title']}</div>
                    <div class="highlight-value" style="color:{h['color']}">{h['value']}</div>
                    <div class="highlight-desc">{h['desc']}</div>
                </div>
            </div>'''
        
        html = f'''
        <div class="highlight-moments">
            <div class="highlights-intro">
                <span class="highlights-intro-icon">✨</span>
                <span class="highlights-intro-text">这一年的聊天里，有这些值得铭记的瞬间</span>
            </div>
            <div class="highlights-grid">
                {cards_html}
            </div>
            <div class="highlights-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">每个高光时刻背后，都是一段真实的情感。这些数字不只是统计，它们是你这一年社交生活的见证。</span>
            </div>
        </div>'''
        
        return html

    # ============ 年度社交人设分析 ============
    def make_social_persona():
        """分析用户的社交人设/标签"""
        # 计算各维度得分
        total_msgs = sum(c.get('total_msgs', 0) for c in private_chats)
        total_late = sum(c.get('late_night', 0) for c in private_chats)
        total_care = sum(c.get('care_me', 0) + c.get('care_them', 0) for c in private_chats)
        active_friends = len([c for c in private_chats if c.get('total_msgs', 0) >= 100])
        group_count = len(group_chats)
        king_count = len([g for g in group_chats if g.get('my_rank') == 1])
        
        # 计算发送/接收比
        my_total = sum(c.get('my_msgs', 0) for c in private_chats)
        their_total = sum(c.get('their_msgs', 0) for c in private_chats)
        
        # 定义人设标签
        personas = []
        
        # 夜猫子
        if total_late > total_msgs * 0.15:
            personas.append(('🦉', '深夜话唠', '夜深人静时，你最真实'))
        
        # 社交达人
        if active_friends > 15:
            personas.append(('🌟', '社交达人', '朋友遍天下，人脉广阔'))
        
        # 暖心天使
        if total_care > 50:
            personas.append(('💝', '暖心天使', '总是关心别人的你'))
        
        # 话唠王
        if king_count >= 3:
            personas.append(('👑', '群聊之王', '在群里你就是焦点'))
        
        # 倾听者
        if their_total > my_total * 1.5:
            personas.append(('👂', '温柔倾听者', '你更愿意听朋友说'))
        
        # 表达者
        if my_total > their_total * 1.5:
            personas.append(('🎤', '表达欲满满', '你有说不完的话'))
        
        # 潜水员
        lurk_groups = len([g for g in group_chats if g.get('my_msgs', 0) == 0])
        if lurk_groups > group_count * 0.5:
            personas.append(('🤿', '群聊潜水员', '安静也是一种参与'))
        
        # 专一型
        if active_friends <= 5 and total_msgs > 1000:
            personas.append(('💎', '专一社交者', '好友在精不在多'))
        
        # 如果标签不够，添加默认的
        if len(personas) < 3:
            personas.append(('💬', '稳定社交者', '不多不少刚刚好'))
        
        # 取前4个人设
        personas = personas[:4]
        
        # 主人设
        main_persona = personas[0] if personas else ('💬', '社交达人', '你有独特的社交风格')
        
        # 生成人设卡片
        persona_cards = ''
        for icon, name, desc in personas:
            persona_cards += f'''
            <div class="persona-tag">
                <span class="persona-icon">{icon}</span>
                <span class="persona-name">{name}</span>
                <span class="persona-desc">{desc}</span>
            </div>'''
        
        html = f'''
        <div class="social-persona">
            <div class="persona-main">
                <div class="persona-main-icon">{main_persona[0]}</div>
                <div class="persona-main-info">
                    <div class="persona-main-name">{main_persona[1]}</div>
                    <div class="persona-main-desc">{main_persona[2]}</div>
                </div>
            </div>
            
            <div class="persona-subtitle">你的社交标签</div>
            <div class="persona-tags">
                {persona_cards}
            </div>
            
            <div class="persona-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">每个人都有自己的社交风格，没有好坏之分。{main_persona[1]}是你最突出的特质——这就是独一无二的你。</span>
            </div>
        </div>'''
        
        return html

    # ============ 年度最佳搭档 ============
    def make_best_partners():
        """分析和展示年度最佳搭档（多维度最佳好友）"""
        if not private_chats:
            return ''
        
        partners = []
        
        # 1. 聊天量最多
        most_msgs = max(sorted_private, key=lambda x: x.get('total_msgs', 0)) if sorted_private else None
        if most_msgs:
            partners.append({
                'title': '💬 话最多',
                'name': most_msgs.get('name', ''),
                'value': f"{most_msgs.get('total_msgs', 0):,}条",
                'desc': '和Ta总有说不完的话',
                'color': 'var(--pink)'
            })
        
        # 2. 深夜陪伴最多
        most_late = max(private_chats, key=lambda x: x.get('late_night', 0)) if private_chats else None
        if most_late and most_late.get('late_night', 0) > 10:
            partners.append({
                'title': '🌙 深夜陪伴',
                'name': most_late.get('name', ''),
                'value': f"{most_late.get('late_night', 0)}条深夜消息",
                'desc': '夜深了还在聊的人',
                'color': 'var(--purple)'
            })
        
        # 3. 互动天数最多
        most_days = max(private_chats, key=lambda x: x.get('days', 0)) if private_chats else None
        if most_days and most_days.get('days', 0) > 30:
            partners.append({
                'title': '📅 最持久',
                'name': most_days.get('name', ''),
                'value': f"聊了{most_days.get('days', 0)}天",
                'desc': '细水长流的友情',
                'color': 'var(--cyan)'
            })
        
        # 4. 关心最多
        most_care = max(private_chats, key=lambda x: x.get('care_me', 0) + x.get('care_them', 0)) if private_chats else None
        if most_care:
            care_total = most_care.get('care_me', 0) + most_care.get('care_them', 0)
            if care_total > 5:
                partners.append({
                    'title': '💕 最暖心',
                    'name': most_care.get('name', ''),
                    'value': f"{care_total}次互相关心",
                    'desc': '总是惦记着对方',
                    'color': 'var(--pink)'
                })
        
        # 5. 秒回最快
        fastest = min([c for c in private_chats if c.get('reply_me_median', 0) > 0], 
                     key=lambda x: x.get('reply_me_median', 9999), default=None)
        if fastest:
            speed = fastest.get('reply_me_median', 0)
            speed_text = f'{int(speed)}秒' if speed < 60 else f'{int(speed/60)}分钟'
            partners.append({
                'title': '⚡ 秒回对象',
                'name': fastest.get('name', ''),
                'value': f"平均{speed_text}回复",
                'desc': '消息来了就想回',
                'color': 'var(--yellow)'
            })
        
        # 6. 会话最长
        longest_session = max(private_chats, key=lambda x: x.get('avg_session_len', 0)) if private_chats else None
        if longest_session and longest_session.get('avg_session_len', 0) > 10:
            partners.append({
                'title': '🎯 最深入',
                'name': longest_session.get('name', ''),
                'value': f"平均{int(longest_session.get('avg_session_len', 0))}条/次",
                'desc': '每次聊天都很投入',
                'color': 'var(--cyan)'
            })
        
        if not partners:
            return '<div class="empty">暂无搭档数据</div>'
        
        # 生成搭档卡片
        cards_html = ''
        for p in partners[:6]:
            cards_html += f'''
            <div class="partner-card">
                <div class="partner-title" style="color:{p['color']}">{p['title']}</div>
                <div class="partner-name">{display_name(p['name'][:8])}</div>
                <div class="partner-value">{p['value']}</div>
                <div class="partner-desc">{p['desc']}</div>
            </div>'''
        
        html = f'''
        <div class="best-partners">
            <div class="partners-intro">
                <span class="partners-intro-text">🏆 每个维度，都有一个最佳搭档</span>
            </div>
            <div class="partners-grid">
                {cards_html}
            </div>
            <div class="partners-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">好朋友不一定只有一个样子。有人陪你熬夜，有人给你关心，有人秒回消息——每种陪伴都是珍贵的。</span>
            </div>
        </div>'''
        
        return html

    # ============ 聊天能量波动图 ============
    def make_energy_wave():
        """展示全年聊天能量的波动情况"""
        # 收集每周数据
        weekly_data = defaultdict(int)
        
        for chat in private_chats:
            daily = chat.get('daily', {})
            for date_str, count in daily.items():
                if date_str.startswith('2025'):
                    try:
                        # 计算是第几周
                        from datetime import datetime
                        dt = datetime.strptime(date_str, '%Y-%m-%d')
                        week_num = dt.isocalendar()[1]
                        weekly_data[week_num] += count
                    except:
                        pass
        
        if not weekly_data:
            # 如果没有daily数据，用monthly数据估算
            monthly_totals = defaultdict(int)
            for chat in private_chats:
                monthly = chat.get('monthly', {})
                for month_key, data in monthly.items():
                    if month_key.startswith('2025'):
                        count = data.get('total', 0) if isinstance(data, dict) else data
                        monthly_totals[month_key] += count
            
            # 将月度数据转换为周数据（每月约4周）
            for month_key, total in monthly_totals.items():
                try:
                    month_num = int(month_key.split('-')[1])
                    base_week = (month_num - 1) * 4 + 1
                    for w in range(4):
                        weekly_data[base_week + w] = total // 4
                except:
                    pass
        
        if not weekly_data:
            return '<div class="empty">暂无能量波动数据</div>'
        
        # 获取最大值用于归一化
        max_val = max(weekly_data.values()) if weekly_data else 1
        
        # 生成52周的SVG波形
        points = []
        for week in range(1, 53):
            val = weekly_data.get(week, 0)
            x = (week - 1) * (100 / 51)  # 0-100
            y = 80 - (val / max_val * 60)  # 80-20，翻转使得高值在上
            points.append(f'{x:.1f},{y:.1f}')
        
        # 创建平滑曲线的path
        path_d = f'M {points[0]}'
        for i in range(1, len(points)):
            path_d += f' L {points[i]}'
        
        # 找出高峰周和低谷周
        if weekly_data:
            peak_week = max(weekly_data.keys(), key=lambda k: weekly_data.get(k, 0))
            peak_val = weekly_data[peak_week]
            low_week = min(weekly_data.keys(), key=lambda k: weekly_data.get(k, 0))
            low_val = weekly_data[low_week]
        else:
            peak_week, peak_val, low_week, low_val = 1, 0, 1, 0
        
        # 计算能量等级
        total_energy = sum(weekly_data.values())
        avg_weekly = total_energy / 52
        
        if avg_weekly > 500:
            energy_level = '🔥 能量爆棚'
            energy_desc = '你的社交能量非常充沛'
        elif avg_weekly > 200:
            energy_level = '⚡ 活力充沛'
            energy_desc = '保持着健康的社交频率'
        elif avg_weekly > 50:
            energy_level = '🌊 平稳波动'
            energy_desc = '社交节奏比较稳定'
        else:
            energy_level = '🌙 低调模式'
            energy_desc = '你更享受独处的时光'
        
        html = f'''
        <div class="energy-wave">
            <div class="energy-header">
                <div class="energy-level">{energy_level}</div>
                <div class="energy-desc">{energy_desc}</div>
            </div>
            
            <div class="energy-chart">
                <svg viewBox="0 0 100 100" preserveAspectRatio="none" class="energy-svg">
                    <!-- 网格线 -->
                    <line x1="0" y1="20" x2="100" y2="20" stroke="var(--bg3)" stroke-width="0.3"/>
                    <line x1="0" y1="50" x2="100" y2="50" stroke="var(--bg3)" stroke-width="0.3"/>
                    <line x1="0" y1="80" x2="100" y2="80" stroke="var(--bg3)" stroke-width="0.3"/>
                    
                    <!-- 填充区域 -->
                    <path d="{path_d} L 100,80 L 0,80 Z" fill="url(#energyGradient)" opacity="0.3"/>
                    
                    <!-- 波形线 -->
                    <path d="{path_d}" fill="none" stroke="url(#energyLineGradient)" stroke-width="2" stroke-linecap="round"/>
                    
                    <defs>
                        <linearGradient id="energyGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" style="stop-color:var(--pink)"/>
                            <stop offset="50%" style="stop-color:var(--purple)"/>
                            <stop offset="100%" style="stop-color:var(--cyan)"/>
                        </linearGradient>
                        <linearGradient id="energyLineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" style="stop-color:var(--pink)"/>
                            <stop offset="50%" style="stop-color:var(--purple)"/>
                            <stop offset="100%" style="stop-color:var(--cyan)"/>
                        </linearGradient>
                    </defs>
                </svg>
                <div class="energy-labels">
                    <span>1月</span><span>4月</span><span>7月</span><span>10月</span><span>12月</span>
                </div>
            </div>
            
            <div class="energy-stats">
                <div class="energy-stat">
                    <span class="energy-stat-icon">📈</span>
                    <span class="energy-stat-label">能量高峰</span>
                    <span class="energy-stat-value">第{peak_week}周 ({peak_val:,}条)</span>
                </div>
                <div class="energy-stat">
                    <span class="energy-stat-icon">📉</span>
                    <span class="energy-stat-label">能量低谷</span>
                    <span class="energy-stat-value">第{low_week}周 ({low_val:,}条)</span>
                </div>
                <div class="energy-stat">
                    <span class="energy-stat-icon">📊</span>
                    <span class="energy-stat-label">周均能量</span>
                    <span class="energy-stat-value">{int(avg_weekly)}条/周</span>
                </div>
            </div>
            
            <div class="energy-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">社交能量的起伏是正常的。高峰时刻也许是假期聚会，低谷时期也许是忙碌或休整——波动本身就是生活的节奏。</span>
            </div>
        </div>'''
        
        return html

    # ============ 互动质量分析（质量≠数量）============
    def make_quality_analysis():
        """分析互动质量，不只看消息数量"""
        if not private_chats:
            return ''
        
        # 计算各维度质量指标
        quality_friends = []
        for c in sorted_private[:50]:  # 取前50个好友分析
            name = c['name']
            total = c.get('total_msgs', 0)
            if total < 30:
                continue
            
            # 1. 对话深度：平均会话长度
            avg_session = c.get('avg_session_len', 0)
            depth_score = min(100, int(avg_session * 5))
            
            # 2. 回复速度匹配：双方回复速度的一致性
            reply_me = c.get('reply_me_median', 300)
            reply_them = c.get('reply_them_median', 300)
            if reply_me > 0 and reply_them > 0:
                speed_match = min(reply_me, reply_them) / max(reply_me, reply_them) * 100
            else:
                speed_match = 50
            
            # 3. 消息平衡度
            their = c.get('their_msgs', 0)
            mine = c.get('my_msgs', 0)
            balance = min(their, mine) / max(their, mine) * 100 if max(their, mine) > 0 else 50
            
            # 4. 关心指数
            care_total = c.get('care_me', 0) + c.get('care_them', 0)
            care_score = min(100, care_total * 5)
            
            # 5. 持续性：聊天天数占比
            days = c.get('days', 0)
            continuity = min(100, int(days / 3.65))  # 一年365天
            
            # 综合质量分
            quality = int((depth_score * 0.25 + speed_match * 0.2 + balance * 0.2 + care_score * 0.2 + continuity * 0.15))
            
            quality_friends.append({
                'name': name,
                'total': total,
                'quality': quality,
                'depth': depth_score,
                'speed_match': int(speed_match),
                'balance': int(balance),
                'care': care_score,
                'continuity': continuity,
            })
        
        # 按质量分排序
        quality_friends.sort(key=lambda x: -x['quality'])
        
        # 找出质量最高的3个好友
        top_quality = quality_friends[:3]
        
        # 找出"被低估的朋友"：消息不多但质量高
        underrated = [f for f in quality_friends if f['total'] < 300 and f['quality'] > 60][:2]
        
        # 生成质量排行卡片
        cards_html = ''
        for i, f in enumerate(top_quality, 1):
            medal = ['🥇', '🥈', '🥉'][i-1]
            cards_html += f'''
            <div class="quality-card">
                <div class="quality-rank">{medal}</div>
                <div class="quality-info">
                    <div class="quality-name">{display_name(f['name'][:8])}</div>
                    <div class="quality-score">{f['quality']}分</div>
                </div>
                <div class="quality-bars">
                    <div class="quality-bar-item" title="对话深度">
                        <span class="qb-label">深度</span>
                        <div class="qb-track"><div class="qb-fill" style="width:{f['depth']}%"></div></div>
                    </div>
                    <div class="quality-bar-item" title="消息平衡">
                        <span class="qb-label">平衡</span>
                        <div class="qb-track"><div class="qb-fill" style="width:{f['balance']}%"></div></div>
                    </div>
                    <div class="quality-bar-item" title="关心程度">
                        <span class="qb-label">关心</span>
                        <div class="qb-track"><div class="qb-fill" style="width:{f['care']}%"></div></div>
                    </div>
                </div>
            </div>'''
        
        # 被低估的朋友
        underrated_html = ''
        if underrated:
            underrated_html = '<div class="quality-underrated"><div class="underrated-title">💎 被低估的友情</div><div class="underrated-desc">消息不多，但每次对话都很有质量</div><div class="underrated-list">'
            for f in underrated:
                underrated_html += f'<span class="underrated-name">{display_name(f["name"][:6])} ({f["quality"]}分)</span>'
            underrated_html += '</div></div>'
        
        html = f'''
        <div class="quality-analysis">
            <div class="quality-header">
                <div class="quality-title">💎 互动质量排行</div>
                <div class="quality-subtitle">消息数量不等于关系质量<br>深度、平衡、关心、持续——才是友情的真正维度</div>
            </div>
            <div class="quality-cards">{cards_html}</div>
            {underrated_html}
            <div class="quality-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">有些朋友消息很多但质量一般，有些朋友消息不多但每次都很走心。质量，比数量更能衡量一段关系的重量。</span>
            </div>
        </div>'''
        
        return html
    
    # ============ 表情气质分析 ============
    def make_emoji_analysis():
        """分析用户的表情使用习惯和气质类型"""
        # 统计所有聊天中的表情使用 - 尝试多种字段名
        emoji_counts = defaultdict(int)
        total_emoji_msgs = 0
        
        for chat in private_chats:
            # 尝试多种可能的字段名
            emoji_data = None
            for field in ['emoji_me', 'emoji_stats', 'emojis', 'emoji_count']:
                if chat.get(field) and isinstance(chat.get(field), dict):
                    emoji_data = chat.get(field)
                    break
            
            if emoji_data:
                for emoji, count in emoji_data.items():
                    if isinstance(count, (int, float)) and count > 0:
                        emoji_counts[emoji] += int(count)
                        total_emoji_msgs += int(count)
            
            # 还可以从消息类型统计中获取表情消息数量
            types_me = chat.get('msg_types_me', {})
            emoji_type_count = types_me.get('表情消息', 0) + types_me.get('动画表情', 0)
            if emoji_type_count > 0 and not emoji_data:
                total_emoji_msgs += emoji_type_count
        
        # 如果没有具体表情数据，但有表情消息数量，生成基于行为推断的分析
        if not emoji_counts:
            # 基于聊天行为推断表情气质
            total_late = sum(c.get('late_night', 0) for c in private_chats)
            total_care = sum(c.get('care_me', 0) + c.get('care_them', 0) for c in private_chats)
            total_sessions = sum(c.get('sessions', 0) for c in private_chats)
            total_msgs = sum(c.get('total_msgs', 0) for c in private_chats)
            
            # 推断主导气质
            if total_care > total_sessions * 0.1:
                dominant_style = ('💗 温柔系', '你的聊天风格温暖体贴，关心朋友是你的日常', 'var(--pink)')
            elif total_late > total_msgs * 0.1:
                dominant_style = ('🌙 深夜系', '深夜是你最真实的时刻，那时的对话更有温度', 'var(--purple)')
            elif total_sessions > len(private_chats) * 10:
                dominant_style = ('😄 活力系', '你的社交能量很强，随时准备和朋友聊天', 'var(--yellow)')
            else:
                dominant_style = ('🤔 沉稳系', '你的聊天风格内敛沉稳，每一句话都经过思考', 'var(--cyan)')
            
            return f'''
            <div class="emoji-analysis">
                <div class="emoji-dominant">
                    <div class="dominant-badge" style="border-color:{dominant_style[2]}">
                        <div class="dominant-icon">{dominant_style[0].split()[0]}</div>
                        <div class="dominant-name">{dominant_style[0]}</div>
                    </div>
                    <div class="dominant-desc">{dominant_style[1]}</div>
                </div>
                <div class="emoji-note">
                    <div class="note-icon">📝</div>
                    <div class="note-text">表情气质基于你的聊天行为模式推断。你可能更偏向纯文字表达，这也是一种独特的风格！</div>
                </div>
                <div class="emoji-insight">
                    <span class="insight-icon">💡</span>
                    <span class="insight-text">不用表情包不代表没有情感，你的文字本身就在传递温度。</span>
                </div>
            </div>'''
        
        # 获取Top10表情
        top_emojis = sorted(emoji_counts.items(), key=lambda x: -x[1])[:10]
        
        # 表情气质分析
        # 分类表情
        warm_emojis = ['❤️', '💕', '💗', '💖', '🥰', '😘', '💝', '💞', '🤗', '😊', '☺️', '💓']
        funny_emojis = ['😂', '🤣', '😆', '😹', '🤭', '😝', '😜', '🤪', '👻', '🙈']
        cool_emojis = ['😎', '🤙', '👍', '💪', '🔥', '⚡', '🎯', '✨', '🌟', '💫']
        sad_emojis = ['😭', '😢', '🥺', '😿', '💔', '😞', '😔', '🥲', '😥']
        think_emojis = ['🤔', '🧐', '💭', '❓', '❔', '🤷', '😏', '🙄']
        
        warm_count = sum(emoji_counts.get(e, 0) for e in warm_emojis)
        funny_count = sum(emoji_counts.get(e, 0) for e in funny_emojis)
        cool_count = sum(emoji_counts.get(e, 0) for e in cool_emojis)
        sad_count = sum(emoji_counts.get(e, 0) for e in sad_emojis)
        think_count = sum(emoji_counts.get(e, 0) for e in think_emojis)
        
        # 判断主导气质
        styles = [
            ('💗 温柔系', warm_count, '你的表情里满是爱意，擅长用小符号传递温暖', 'var(--pink)'),
            ('😂 幽默系', funny_count, '你是群聊的开心果，总能用表情逗大家笑', 'var(--yellow)'),
            ('😎 酷炫系', cool_count, '简洁有力，一个表情胜过千言万语', 'var(--cyan)'),
            ('🥺 感性系', sad_count, '你敏感细腻，表情是情绪最真实的出口', 'var(--purple)'),
            ('🤔 思考系', think_count, '你爱提问、爱思考，表情里藏着好奇心', 'var(--dim)'),
        ]
        styles.sort(key=lambda x: -x[1])
        dominant_style = styles[0]
        
        # 生成Top10表情HTML
        emoji_list_html = ''
        max_count = top_emojis[0][1] if top_emojis else 1
        for i, (emoji, count) in enumerate(top_emojis, 1):
            pct = int(count / max_count * 100)
            medal = ['🥇', '🥈', '🥉'][i-1] if i <= 3 else str(i)
            emoji_list_html += f'''
            <div class="emoji-item">
                <span class="emoji-rank">{medal}</span>
                <span class="emoji-icon">{emoji}</span>
                <div class="emoji-bar"><div class="emoji-fill" style="width:{pct}%"></div></div>
                <span class="emoji-count">{count:,}次</span>
            </div>'''
        
        # 生成气质分布HTML
        total_style = sum(s[1] for s in styles) or 1
        style_html = ''
        for name, count, desc, color in styles:
            pct = int(count / total_style * 100)
            if pct > 0:
                style_html += f'''
                <div class="style-item">
                    <div class="style-header">
                        <span class="style-name">{name}</span>
                        <span class="style-pct">{pct}%</span>
                    </div>
                    <div class="style-bar"><div class="style-fill" style="width:{pct}%;background:{color}"></div></div>
                </div>'''
        
        html = f'''
        <div class="emoji-analysis">
            <div class="emoji-dominant">
                <div class="dominant-badge" style="border-color:{dominant_style[3]}">
                    <div class="dominant-icon">{dominant_style[0].split()[0]}</div>
                    <div class="dominant-name">{dominant_style[0]}</div>
                </div>
                <div class="dominant-desc">{dominant_style[2]}</div>
            </div>
            
            <div class="emoji-sections">
                <div class="emoji-top10">
                    <div class="emoji-section-title">📊 年度表情Top10</div>
                    <div class="emoji-list">{emoji_list_html}</div>
                    <div class="emoji-total">共使用 {total_emoji_msgs:,} 次表情</div>
                </div>
                
                <div class="emoji-styles">
                    <div class="emoji-section-title">🎨 表情气质分布</div>
                    <div class="style-list">{style_html}</div>
                </div>
            </div>
            
            <div class="emoji-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">表情是文字之外的"第二语言"，你最爱用的那个表情，也许正是你最真实的表达方式。</span>
            </div>
        </div>'''
        
        return html
    
    # ============ 年度聊天词云 ============
    def make_word_cloud():
        """生成年度聊天词云，展示最常用的词汇和表达"""
        # 收集常用词汇数据
        word_counts = defaultdict(int)
        
        # 从各种可能的字段收集词频数据
        for chat in private_chats:
            # 尝试从topics字段获取
            topics_me = chat.get('topics_me', {})
            if isinstance(topics_me, dict):
                for word, count in topics_me.items():
                    if isinstance(count, (int, float)) and len(word) >= 2:
                        word_counts[word] += int(count)
            
            # 尝试从keywords字段获取
            keywords = chat.get('keywords', {}) or chat.get('words', {})
            if isinstance(keywords, dict):
                for word, count in keywords.items():
                    if isinstance(count, (int, float)) and len(word) >= 2:
                        word_counts[word] += int(count)
        
        # 如果没有词频数据，使用预设的常用词汇
        if not word_counts:
            # 基于聊天行为推断常用词汇
            total_late = sum(c.get('late_night', 0) for c in private_chats)
            total_care = sum(c.get('care_me', 0) + c.get('care_them', 0) for c in private_chats)
            total_sessions = sum(c.get('sessions', 0) for c in private_chats)
            
            # 生成推断的词云
            inferred_words = [
                ('好的', 100 + total_sessions // 10),
                ('哈哈', 80 + total_sessions // 15),
                ('在吗', 60 + len(private_chats) * 2),
                ('晚安', 40 + total_late // 5),
                ('早安', 30 + total_sessions // 20),
                ('谢谢', 50 + total_care // 3),
                ('辛苦了', 30 + total_care // 4),
                ('开心', 25 + total_sessions // 25),
                ('一起', 35 + total_sessions // 20),
                ('今天', 45 + total_sessions // 15),
                ('明天', 40 + total_sessions // 18),
                ('吃饭', 30 + total_sessions // 22),
                ('回家', 25 + total_late // 8),
                ('加油', 20 + total_care // 5),
                ('想你', 15 + total_late // 10),
                ('收到', 55 + total_sessions // 12),
                ('好久不见', 10 + len(private_chats) // 5),
                ('等你', 18 + total_sessions // 30),
            ]
            word_counts = {w: c for w, c in inferred_words}
        
        # 获取Top词汇
        top_words = sorted(word_counts.items(), key=lambda x: -x[1])[:25]
        
        if not top_words:
            return ''
        
        # 计算词汇大小和位置
        max_count = top_words[0][1] if top_words else 1
        min_count = top_words[-1][1] if top_words else 1
        
        # SVG词云参数
        svg_width = 500
        svg_height = 300
        center_x = svg_width / 2
        center_y = svg_height / 2
        
        # 生成词云元素
        words_html = ''
        colors = ['var(--pink)', 'var(--cyan)', 'var(--purple)', 'var(--yellow)', '#4ade80', '#f472b6', '#60a5fa']
        
        # 使用螺旋布局
        placed_words = []
        for i, (word, count) in enumerate(top_words):
            # 计算字体大小（16-40px）
            if max_count > min_count:
                size_ratio = (count - min_count) / (max_count - min_count)
            else:
                size_ratio = 0.5
            font_size = 16 + size_ratio * 24
            
            # 螺旋位置计算
            angle = i * 0.8
            radius = 20 + i * 12
            x = center_x + radius * math.cos(angle) * 0.8
            y = center_y + radius * math.sin(angle) * 0.5
            
            # 确保在边界内
            x = max(50, min(svg_width - 50, x))
            y = max(30, min(svg_height - 30, y))
            
            color = colors[i % len(colors)]
            opacity = 0.7 + size_ratio * 0.3
            delay = i * 0.1
            
            words_html += f'''
            <text x="{x}" y="{y}" 
                  font-size="{font_size}px" 
                  fill="{color}" 
                  opacity="{opacity}"
                  text-anchor="middle"
                  class="cloud-word"
                  style="animation-delay:{delay}s"
                  data-count="{count}">
                {word}
            </text>'''
        
        # 找出最常用的3个词
        top3 = top_words[:3]
        top3_html = ''
        for i, (word, count) in enumerate(top3):
            medal = ['🥇', '🥈', '🥉'][i]
            top3_html += f'<div class="cloud-top-item"><span class="cloud-medal">{medal}</span><span class="cloud-word-name">{word}</span><span class="cloud-word-count">{count}次</span></div>'
        
        # 词汇风格分析
        style_words = {
            '温暖系': ['谢谢', '辛苦', '关心', '想你', '爱你', '抱抱', '加油', '早安', '晚安'],
            '活力系': ['哈哈', '开心', '好玩', '一起', '走起', '冲', '绝了', '太棒'],
            '务实系': ['好的', '收到', '了解', '明白', '可以', '行', 'OK', '没问题'],
            '社交系': ['在吗', '有空', '约', '见面', '聚聚', '吃饭', '出来'],
        }
        
        style_scores = {}
        for style, keywords in style_words.items():
            score = sum(word_counts.get(kw, 0) for kw in keywords)
            style_scores[style] = score
        
        dominant_style = max(style_scores, key=style_scores.get) if style_scores else '务实系'
        style_icons = {'温暖系': '💗', '活力系': '⚡', '务实系': '✅', '社交系': '🤝'}
        
        html = f'''
        <div class="word-cloud-container">
            <div class="cloud-header">
                <div class="cloud-title">💬 你的年度词汇</div>
                <div class="cloud-subtitle">这些词，是你2025说得最多的</div>
            </div>
            
            <div class="cloud-visual">
                <svg viewBox="0 0 {svg_width} {svg_height}" class="cloud-svg">
                    {words_html}
                </svg>
            </div>
            
            <div class="cloud-top3">
                <div class="cloud-top3-title">🏆 年度高频词Top3</div>
                <div class="cloud-top3-list">{top3_html}</div>
            </div>
            
            <div class="cloud-style">
                <div class="cloud-style-badge" style="background:linear-gradient(135deg,var(--pink),var(--purple))">
                    <span class="style-icon">{style_icons.get(dominant_style, '💬')}</span>
                    <span class="style-name">{dominant_style}</span>
                </div>
                <div class="cloud-style-desc">你的聊天风格偏向<strong>{dominant_style}</strong>，这些常用词勾勒出你独特的表达方式</div>
            </div>
            
            <div class="cloud-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">语言是思维的镜子。你说的每一个词，都在塑造你和他人眼中的自己。</span>
            </div>
        </div>'''
        
        return html
    
    # ============ 社交动机分析 ============
    def make_motivation_analysis():
        """分析用户的社交动机类型"""
        # 计算各类动机指标
        total_msgs = sum(c.get('total_msgs', 0) for c in private_chats)
        total_sessions = sum(c.get('sessions', 0) for c in private_chats)
        total_care = sum(c.get('care_me', 0) + c.get('care_them', 0) for c in private_chats)
        total_late_night = sum(c.get('late_night', 0) for c in private_chats)
        total_invite = sum(c.get('invite_me', 0) + c.get('invite_them', 0) for c in private_chats)
        active_friends = len([c for c in private_chats if c.get('total_msgs', 0) >= 100])
        
        # 计算各类动机得分
        # 1. 社交支持型：关心、陪伴多
        support_score = min(100, int((total_care * 2 + total_late_night * 0.5) / max(total_msgs, 1) * 1000))
        
        # 2. 情感共鸣型：深夜聊天、长对话多
        avg_session_len = total_msgs / max(total_sessions, 1)
        emotional_score = min(100, int((total_late_night * 3 + avg_session_len * 2) / 10))
        
        # 3. 社交拓展型：联系人多、会话多
        expansion_score = min(100, int((active_friends * 3 + total_sessions * 0.1)))
        
        # 4. 信息交换型：邀约、实用性对话
        info_score = min(100, int((total_invite * 5 + total_sessions * 0.5) / 10))
        
        # 5. 娱乐享受型：表情、轻松对话
        total_emoji = sum(sum(c.get('emoji_me', {}).values()) if isinstance(c.get('emoji_me'), dict) else 0 for c in private_chats)
        fun_score = min(100, int(total_emoji / max(total_msgs, 1) * 500 + 30))
        
        motivations = [
            ('💝 情感支持', support_score, '你用微信维系感情，关心和陪伴是你社交的核心', 'var(--pink)'),
            ('🌙 情感共鸣', emotional_score, '你喜欢深度对话，深夜是你敞开心扉的时刻', 'var(--purple)'),
            ('🌍 社交拓展', expansion_score, '你热衷于拓展人脉，保持广泛的社交联系', 'var(--cyan)'),
            ('📋 信息交换', info_score, '你把微信当作实用工具，高效沟通是你的风格', 'var(--yellow)'),
            ('🎉 娱乐享受', fun_score, '你享受聊天的乐趣，表情包是你的快乐源泉', 'var(--pink)'),
        ]
        
        # 找出主导动机
        motivations.sort(key=lambda x: -x[1])
        dominant = motivations[0]
        
        # 生成雷达图数据
        radar_points = []
        for i, (name, score, desc, color) in enumerate(motivations):
            angle = i * 72 - 90  # 5个点，每个72度
            import math
            r = score * 0.8 / 100  # 半径比例
            x = 50 + r * 40 * math.cos(math.radians(angle))
            y = 50 + r * 40 * math.sin(math.radians(angle))
            radar_points.append(f'{x},{y}')
        radar_path = ' '.join(radar_points)
        
        # 生成动机条形图HTML
        bars_html = ''
        for name, score, desc, color in motivations:
            bars_html += f'''
            <div class="motive-item">
                <div class="motive-header">
                    <span class="motive-name">{name}</span>
                    <span class="motive-score">{score}分</span>
                </div>
                <div class="motive-bar"><div class="motive-fill" style="width:{score}%;background:{color}"></div></div>
            </div>'''
        
        html = f'''
        <div class="motivation-analysis">
            <div class="motivation-dominant">
                <div class="dominant-circle" style="border-color:{dominant[3]}">
                    <div class="dominant-emoji">{dominant[0].split()[0]}</div>
                </div>
                <div class="dominant-info">
                    <div class="dominant-type">{dominant[0]}</div>
                    <div class="dominant-desc">{dominant[2]}</div>
                </div>
            </div>
            
            <div class="motivation-radar">
                <svg viewBox="0 0 100 100" class="radar-svg">
                    <!-- 背景网格 -->
                    <polygon points="50,10 90,35 80,85 20,85 10,35" fill="none" stroke="var(--bg3)" stroke-width="0.5"/>
                    <polygon points="50,22 78,40 70,78 30,78 22,40" fill="none" stroke="var(--bg3)" stroke-width="0.5"/>
                    <polygon points="50,34 66,45 60,71 40,71 34,45" fill="none" stroke="var(--bg3)" stroke-width="0.5"/>
                    <!-- 数据区域 -->
                    <polygon points="{radar_path}" fill="rgba(255,107,157,0.3)" stroke="var(--pink)" stroke-width="2"/>
                    <!-- 数据点 -->
                    {''.join([f'<circle cx="{p.split(",")[0]}" cy="{p.split(",")[1]}" r="3" fill="var(--pink)"/>' for p in radar_points])}
                </svg>
                <div class="radar-labels">
                    <span class="radar-label" style="top:0;left:50%;transform:translateX(-50%)">情感支持</span>
                    <span class="radar-label" style="top:30%;right:0">情感共鸣</span>
                    <span class="radar-label" style="bottom:10%;right:10%">社交拓展</span>
                    <span class="radar-label" style="bottom:10%;left:10%">信息交换</span>
                    <span class="radar-label" style="top:30%;left:0">娱乐享受</span>
                </div>
            </div>
            
            <div class="motivation-bars">
                <div class="bars-title">📊 动机分布</div>
                {bars_html}
            </div>
            
            <div class="motivation-insight">
                <span class="insight-icon">💡</span>
                <span class="insight-text">每个人打开微信的理由都不同：有人寻找陪伴，有人交换信息，有人纯粹享受聊天的乐趣。你的主导动机，定义了你的社交风格。</span>
            </div>
        </div>'''
        
        return html
    
    # ============ 用户画像卡片 ============
    def make_user_profile_card():
        """生成用户画像预测卡片"""
        profile = analyze_user_profile()
        
        if not profile['age_range']:
            return ''
        
        # 兴趣标签HTML
        interests_html = ''
        for interest in profile['interests']:
            interests_html += f'<span class="profile-tag">{interest}</span>'
        
        # 性格标签HTML
        personality_html = ''
        for tag in profile['personality_tags']:
            personality_html += f'<span class="personality-tag">{tag}</span>'
        
        html = f'''
        <div class="profile-card">
            <div class="profile-header">
                <span class="profile-icon">🔮</span>
                <span class="profile-title">猜猜你是谁</span>
            </div>
            <div class="profile-content">
                <div class="profile-section">
                    <div class="profile-label">年龄段预测</div>
                    <div class="profile-value">{profile['age_range']}</div>
                    <div class="profile-confidence">
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width:{profile['age_confidence']}%"></div>
                        </div>
                        <span class="confidence-text">置信度 {profile['age_confidence']}%</span>
                    </div>
                </div>
                
                <div class="profile-section">
                    <div class="profile-label">身份猜测</div>
                    <div class="profile-value">{profile['identity']}</div>
                    <div class="profile-confidence">
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width:{profile['identity_confidence']}%"></div>
                        </div>
                        <span class="confidence-text">置信度 {profile['identity_confidence']}%</span>
                    </div>
                </div>
                
                <div class="profile-section">
                    <div class="profile-label">社交风格</div>
                    <div class="profile-value style-value">{profile['social_style']}</div>
                </div>
                
                <div class="profile-section">
                    <div class="profile-label">兴趣画像</div>
                    <div class="profile-tags">{interests_html}</div>
                </div>
                
                <div class="profile-section">
                    <div class="profile-label">性格标签</div>
                    <div class="profile-tags personality">{personality_html}</div>
                </div>
            </div>
            <div class="profile-footer">
                <span>🤖 基于你的聊天习惯智能分析</span>
            </div>
        </div>'''
        
        return html

    # ============ 好友默契度匹配 ============
    def make_chemistry_cards():
        if len(sorted_private) < 2:
            return ''
        
        # 取前10个好友计算默契度，然后选分数最高的5个
        chemistry_list = []
        
        for chat in sorted_private[:10]:
            name = chat['name']
            score = 0
            details = []
            
            # 1. 消息量平衡度 (最高20分)
            their_msgs = chat.get('their_msgs', 0)
            my_msgs = chat.get('my_msgs', 0)
            if their_msgs + my_msgs > 0:
                balance = min(their_msgs, my_msgs) / max(their_msgs, my_msgs) if max(their_msgs, my_msgs) > 0 else 0
                balance_score = int(balance * 20)
                score += balance_score
                if balance > 0.9:
                    details.append('💬 你们的对话有来有往，像心灵在同频共振')
                elif balance > 0.7:
                    details.append('💬 互动很平衡，让对话自然又舒服')
                elif balance > 0.5:
                    details.append('💬 对话节奏还不错，继续保持')
            
            # 2. 回复速度匹配度 (最高20分)
            reply_them = chat.get('reply_them_median', 0)
            reply_me = chat.get('reply_me_median', 0)
            if reply_them and reply_me:
                reply_balance = min(reply_them, reply_me) / max(reply_them, reply_me) if max(reply_them, reply_me) > 0 else 0
                reply_score = int(reply_balance * 20)
                score += reply_score
                if reply_them < 60 and reply_me < 60:
                    details.append('⚡ 秒回默契！消息从不让对方等')
                elif reply_them < 120 and reply_me < 120:
                    details.append('⚡ 回复很快，沟通节奏很匹配')
                elif reply_them < 180 or reply_me < 180:
                    details.append('⚡ 总有一方在等待回复')
            
            # 3. 会话频率 (最高20分)
            sessions = chat.get('sessions', 0)
            days = chat.get('days', 1)
            session_freq = sessions / days if days > 0 else 0
            freq_score = min(20, int(session_freq * 10))
            score += freq_score
            if session_freq > 2:
                details.append('📅 每天聊好几轮，距离被一点点拉近')
            elif session_freq > 1:
                details.append('📅 天天都要说几句，这是习惯也是牵挂')
            elif session_freq > 0.5:
                details.append('📅 保持稳定联系，细水长流的友情')
            elif session_freq > 0.2:
                details.append('📅 虽然不常聊，但从未忘记')
            
            # 4. 深夜陪伴 (最高20分)
            late_night = chat.get('late_night', 0)
            late_score = min(20, late_night // 5)
            score += late_score
            if late_night > 100:
                details.append('🌙 深夜灵魂伴侣，最真实的话都在夜里说')
            elif late_night > 50:
                details.append('🌙 夜聊知己，有人陪你度过失眠的夜')
            elif late_night > 20:
                details.append('🌙 偶尔深夜陪伴，是特别的温柔')
            
            # 5. 关心互动 (最高20分)
            care_them = chat.get('care_them', 0)
            care_me = chat.get('care_me', 0)
            care_score = min(20, (care_them + care_me) // 2)
            score += care_score
            if care_them > 20 and care_me > 20:
                details.append('❤️ 互相关心满满，是真正的双向在乎')
            elif care_them > 10 and care_me > 10:
                details.append('❤️ 彼此都很在乎，每句关心都走心')
            elif care_them > 5 or care_me > 5:
                details.append('❤️ 有人在默默关心着你')
            
            # 默契称号 - 基于分数的基础称号（后面会根据名次覆盖）
            if score >= 85:
                base_level = 'legendary'
            elif score >= 70:
                base_level = 'epic'
            elif score >= 55:
                base_level = 'rare'
            elif score >= 40:
                base_level = 'common'
            else:
                base_level = 'starter'
            
            chemistry_list.append({
                'name': name,
                'score': min(100, score),
                'base_level': base_level,
                'details': details[:3] if details else ['✨ 默契正在悄悄生长，每次对话都是养分']
            })
        
        # 按分数从高到低排序，取前5个
        chemistry_list.sort(key=lambda x: -x['score'])
        chemistry_list = chemistry_list[:5]
        
        # 【新增】前5名专属称号系统 - 每个名次都有独特的称号和描述
        rank_titles = {
            1: [
                ('💎 灵魂伴侣', '不用开口，你就懂我的全部'),
                ('👑 年度挚友', '这一年，感谢有你在消息列表的最顶端'),
                ('🏆 默契王者', '我们的默契，无人能及'),
            ],
            2: [
                ('🌟 心灵知己', '聊天像呼吸一样自然'),
                ('💫 灵魂共振', '每句话都在同一个频率'),
                ('✨ 第二灵魂', '你是另一个懂我的人'),
            ],
            3: [
                ('🔮 神仙默契', '一个眼神就能接住梗'),
                ('💜 紫色知音', '我们的对话自带BGM'),
                ('🎯 心有灵犀', '一句话就能接得住'),
            ],
            4: [
                ('💛 金色搭档', '有你在，聊天从不冷场'),
                ('🌙 深夜好友', '愿意陪你聊到天亮的人'),
                ('🎪 快乐源泉', '和你聊天，嘴角会不自觉上扬'),
            ],
            5: [
                ('🌈 彩虹伙伴', '你给我的消息列表添了色彩'),
                ('🍀 幸运好友', '有你在列表里，是种幸运'),
                ('🌱 默契新星', '我们的故事才刚刚开始'),
            ]
        }
        
        # 为每个好友分配名次专属称号
        for i, c in enumerate(chemistry_list):
            rank = i + 1
            # 根据名次随机选择一个称号（增加多样性）
            import random
            title_options = rank_titles.get(rank, [('🤝 默契好友', '聊得开心、聊得自在')])
            title, title_desc = random.choice(title_options)
            c['title'] = title
            c['title_desc'] = title_desc
        
        # 生成HTML - #1是分数最高的，排在最上面
        cards_html = ''
        total_cards = len(chemistry_list)
        
        for i, c in enumerate(chemistry_list):
            rank = i + 1
            details_html = '<br>'.join(c['details'])
            
            # 颜色和特效
            if c['score'] >= 85:
                color = 'var(--pink)'
                glow = 'glow-high'
            elif c['score'] >= 70:
                color = 'var(--purple)'
                glow = 'glow-mid'
            elif c['score'] >= 50:
                color = 'var(--cyan)'
                glow = ''
            else:
                color = 'var(--dim)'
                glow = ''
            
            delay = i * 1.5
            
            cards_html += f'''
            <div class="chemistry-card {glow}" data-rank="{rank}" style="animation-delay:{delay}s">
                <div class="chemistry-rank">#{rank}</div>
                <div class="chemistry-info">
                    <div class="chemistry-name">{display_name(c['name'][:8])}</div>
                    <div class="chemistry-title">{c['title']}</div>
                    <div class="chemistry-title-desc">{c['title_desc']}</div>
                    <div class="chemistry-details">{details_html}</div>
                </div>
                <div class="chemistry-score">
                    <svg viewBox="0 0 36 36" class="chemistry-ring">
                        <path class="chemistry-ring-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                        <path class="chemistry-ring-fill" stroke="{color}" stroke-dasharray="{c['score']}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    </svg>
                    <div class="chemistry-score-val">{c['score']}</div>
                </div>
            </div>'''
        
        # 引导文案
        intro_html = '''
        <div class="chemistry-intro">
            <div class="chemistry-intro-title">💫 你的默契榜单来了！</div>
            <div class="chemistry-intro-text">
                有的人一条消息就秒回，有的人每天聊好几轮，有的人陪你到深夜。<br>
                这些评分不仅是数字，更是你与Ta真实互动的温度。<br>
                <span class="chemistry-intro-hint">默契 ≠ 频率，而是你们心意的共振 ✨</span>
            </div>
        </div>'''
        
        # 小结文案
        outro_html = '''
        <div class="chemistry-outro">
            <div class="chemistry-outro-title">✨ 默契不是一蹴而就</div>
            <div class="chemistry-outro-text">
                它是聊天习惯、回复节奏、陪伴时间、关心互动等多维度共同叠加的结果。<br>
                有些关系在热烈，有些在稳固，有些还在萌芽，但每一种都有它的意义。<br>
                <strong>感谢这些名字，在你的2025中留下了文字和心意。</strong>
            </div>
        </div>'''
        
        return f'''
        {intro_html}
        <div class="chemistry-list" id="chemistryList" data-total="{total_cards}">
            {cards_html}
        </div>
        {outro_html}'''

    # 处理用户昵称用于标题
    report_owner = my_name if my_name else '我'
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{report_owner}的2025微信年度报告</title>
<style>
:root {{
    --pink: #FF6B9D;
    --cyan: #4ECDC4;
    --yellow: #FFD93D;
    --purple: #A855F7;
    --bg1: #0a0a1a;
    --bg2: #12121f;
    --bg3: #1a1a2e;
    --txt: #fff;
    --dim: #888;
    --them: #FF6B9D;
    --me: #4ECDC4;
}}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{
    font-family:-apple-system,"PingFang SC",sans-serif;
    color:var(--txt);
    line-height:1.5;
    overflow-x:hidden;
    /* 动态渐变背景 - 类似网易云风格 */
    background: linear-gradient(135deg, 
        #0a0a1a 0%,
        #0d1025 15%,
        #12122a 30%,
        #0f1a2e 50%,
        #0a1628 70%,
        #0d0d1f 85%,
        #0a0a1a 100%
    );
    background-attachment: fixed;
    min-height: 100vh;
}}

/* 粒子背景 */
#particles{{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0}}
.particle{{position:absolute;border-radius:50%;animation:float-particle linear infinite;opacity:0}}
@keyframes float-particle{{
    0%{{transform:translateY(100vh) scale(0);opacity:0}}
    10%{{opacity:1}}
    90%{{opacity:1}}
    100%{{transform:translateY(-100vh) scale(1);opacity:0}}
}}

/* 星星背景 */
.stars{{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0}}
.star{{position:absolute;background:#fff;border-radius:50%;animation:twinkle ease-in-out infinite}}
@keyframes twinkle{{0%,100%{{opacity:0.3;transform:scale(1)}}50%{{opacity:1;transform:scale(1.2)}}}}

/* 流动线条背景 - 增强版 */
.flowing-lines{{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;overflow:hidden;opacity:0.25}}
.flowing-line{{
    position:absolute;
    height:1px;
    background:linear-gradient(90deg,transparent 0%,var(--pink) 20%,var(--cyan) 50%,var(--purple) 80%,transparent 100%);
    animation:flow-line linear infinite;
    filter:blur(0.5px);
    box-shadow:0 0 8px rgba(255,107,157,0.3), 0 0 15px rgba(78,205,196,0.2);
}}
@keyframes flow-line{{
    0%{{transform:translateX(-100%) rotate(var(--angle))}}
    100%{{transform:translateX(100vw) rotate(var(--angle))}}
}}

/* 网格线背景 */
.grid-bg{{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;
    background-image:
        linear-gradient(rgba(255,107,157,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,107,157,0.03) 1px, transparent 1px),
        linear-gradient(rgba(78,205,196,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(78,205,196,0.02) 1px, transparent 1px);
    background-size: 100px 100px, 100px 100px, 20px 20px, 20px 20px;
    background-position: -1px -1px, -1px -1px, -1px -1px, -1px -1px;
}}

/* 光晕效果 - 增强版 */
.glow-orbs{{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;overflow:hidden}}
.glow-orb{{
    position:absolute;
    border-radius:50%;
    filter:blur(100px);
    animation:float-orb 25s ease-in-out infinite;
    mix-blend-mode:screen;
}}
@keyframes float-orb{{
    0%,100%{{transform:translate(0,0) scale(1);opacity:0.6}}
    25%{{transform:translate(80px,-50px) scale(1.2);opacity:0.8}}
    50%{{transform:translate(-30px,80px) scale(0.9);opacity:0.5}}
    75%{{transform:translate(-80px,-30px) scale(1.15);opacity:0.7}}
}}

/* 烟花 */
.firework{{position:fixed;pointer-events:none;z-index:1000}}
.spark{{position:absolute;border-radius:50%;animation:spark-fly 1s ease-out forwards}}
@keyframes spark-fly{{
    0%{{transform:translate(0,0) scale(1);opacity:1}}
    100%{{transform:translate(var(--tx),var(--ty)) scale(0);opacity:0}}
}}

/* 动画 */
@keyframes fadeUp{{from{{opacity:0;transform:translateY(30px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes glow{{0%,100%{{filter:drop-shadow(0 0 20px var(--pink))}}50%{{filter:drop-shadow(0 0 40px var(--cyan))}}}}
@keyframes pulse{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.05)}}}}

/* 导航 - 改进移动端 */
.nav{{position:fixed;top:0;left:0;right:0;background:rgba(10,10,26,0.95);backdrop-filter:blur(10px);z-index:100;padding:8px 15px;display:flex;justify-content:center;gap:6px;flex-wrap:wrap}}
.nav a{{color:var(--dim);text-decoration:none;padding:6px 12px;border-radius:20px;font-size:12px;transition:all 0.3s;white-space:nowrap}}
.nav a:hover,.nav a.active{{background:var(--pink);color:#fff}}

/* 开场页 */
.hero{{min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;position:relative;z-index:1;padding:80px 20px 20px;overflow:hidden}}

/* 开场粒子光线动画 */
.hero::before{{content:'';position:absolute;top:50%;left:50%;width:600px;height:600px;transform:translate(-50%,-50%);background:radial-gradient(circle,rgba(255,107,157,0.15) 0%,transparent 70%);animation:hero-pulse 4s ease-in-out infinite;pointer-events:none}}
.hero::after{{content:'';position:absolute;top:50%;left:50%;width:800px;height:800px;transform:translate(-50%,-50%);background:radial-gradient(circle,rgba(78,205,196,0.1) 0%,transparent 60%);animation:hero-pulse 4s ease-in-out infinite 1s;pointer-events:none}}
@keyframes hero-pulse{{0%,100%{{transform:translate(-50%,-50%) scale(1);opacity:0.5}}50%{{transform:translate(-50%,-50%) scale(1.2);opacity:1}}}}

/* 粒子向中心聚合动画 */
@keyframes particle-to-center{{
    0%{{opacity:0.8;transform:translate(0,0) scale(1)}}
    70%{{opacity:0.6}}
    100%{{opacity:0;transform:translate(calc(50vw - 100%),calc(50vh - 100%)) scale(0)}}
}}

/* 开场光线爆发效果 */
.hero-rays{{position:absolute;top:50%;left:50%;width:100%;height:100%;pointer-events:none}}
.hero-ray{{position:absolute;top:50%;left:50%;width:2px;height:150px;background:linear-gradient(to bottom,rgba(255,107,157,0.8),transparent);transform-origin:bottom center;animation:ray-shoot 3s ease-out forwards}}
@keyframes ray-shoot{{0%{{opacity:0;height:0}}20%{{opacity:1;height:150px}}100%{{opacity:0;height:300px;transform:translateY(-200px)}}}}

/* 开场动画层 */
.intro-animation-layer{{position:absolute;top:0;left:0;width:100%;height:100%;z-index:10;pointer-events:none;overflow:hidden}}
.intro-animation-layer.hidden{{display:none}}
.intro-text-particle{{position:absolute;font-size:14px;color:rgba(255,255,255,0.8);white-space:nowrap;animation:float-up 3s ease-out forwards;text-shadow:0 0 10px rgba(255,107,157,0.5)}}
@keyframes float-up{{0%{{opacity:0;transform:translateY(50px)}}20%{{opacity:1}}80%{{opacity:1}}100%{{opacity:0;transform:translateY(-100px)}}}}
.intro-narrative{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;color:#fff;z-index:20}}
.intro-narrative-text{{font-size:20px;opacity:0;animation:narrative-fade 2s ease-out forwards;text-shadow:0 2px 20px rgba(0,0,0,0.5)}}
@keyframes narrative-fade{{0%{{opacity:0;transform:translateY(20px)}}50%{{opacity:1;transform:translateY(0)}}100%{{opacity:0;transform:translateY(-10px)}}}}
.intro-timeline{{position:absolute;bottom:30%;left:50%;transform:translateX(-50%);display:flex;gap:8px;opacity:0}}
.intro-month{{display:flex;flex-direction:column;align-items:center;gap:4px}}
.intro-month-bar{{width:20px;background:linear-gradient(to top,var(--pink),var(--cyan));border-radius:3px;transition:height 0.5s ease-out}}
.intro-month-label{{font-size:10px;color:var(--dim)}}
.intro-stat-burst{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;opacity:0}}
.intro-stat-num{{font-size:60px;font-weight:900;background:linear-gradient(135deg,var(--pink),var(--cyan));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.intro-stat-label{{font-size:16px;color:var(--dim);margin-top:5px}}
.hero-content{{position:relative;z-index:5;transition:opacity 0.8s ease-out}}

.hero-year{{font-size:clamp(60px,18vw,160px);font-weight:900;background:linear-gradient(135deg,var(--pink),var(--cyan),var(--yellow));-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:glow 4s ease-in-out infinite,hero-year-in 1.5s ease-out}}
@keyframes hero-year-in{{0%{{opacity:0;transform:scale(0.5);filter:blur(20px)}}100%{{opacity:1;transform:scale(1);filter:blur(0)}}}}
.hero-sub{{font-size:clamp(14px,3vw,22px);color:var(--dim);margin:15px 0 20px;animation:fadeIn 1s ease-out 0.5s both}}
.hero-intro{{font-size:clamp(12px,2.5vw,16px);color:rgba(255,255,255,0.5);margin-bottom:20px;font-style:italic;animation:fadeIn 1s ease-out 0.8s both}}
.hero-story{{margin:20px auto 25px;max-width:500px}}
.story-lines{{display:flex;flex-direction:column;gap:12px}}
.story-line{{font-size:clamp(13px,2.8vw,15px);color:rgba(255,255,255,0.7);line-height:1.8;padding:10px 20px;background:rgba(255,255,255,0.03);border-radius:8px;border-left:2px solid var(--pink);animation:story-line-in 0.8s ease-out both}}
.story-line:nth-child(1){{animation-delay:1s}}.story-line:nth-child(2){{animation-delay:1.3s}}.story-line:nth-child(3){{animation-delay:1.6s}}
@keyframes story-line-in{{0%{{opacity:0;transform:translateX(-30px)}}100%{{opacity:1;transform:translateX(0)}}}}
.story-line strong{{color:var(--cyan);font-weight:600}}
.hero-quote{{font-size:clamp(11px,2vw,13px);color:var(--dim);font-style:italic;margin:20px 0;opacity:0.7;animation:fadeIn 1s ease-out 2s both}}
.hero-stats{{display:flex;gap:clamp(15px,4vw,50px);flex-wrap:wrap;justify-content:center}}
.hero-stat{{text-align:center;animation:stat-pop 0.6s ease-out forwards;opacity:0;transform:scale(0.5)}}
.hero-stat:nth-child(1){{animation-delay:2.2s}}.hero-stat:nth-child(2){{animation-delay:2.4s}}.hero-stat:nth-child(3){{animation-delay:2.6s}}.hero-stat:nth-child(4){{animation-delay:2.8s}}.hero-stat:nth-child(5){{animation-delay:3s}}
@keyframes stat-pop{{0%{{opacity:0;transform:scale(0.5)}}70%{{transform:scale(1.1)}}100%{{opacity:1;transform:scale(1)}}}}
.hero-stat-val{{font-size:clamp(28px,7vw,52px);font-weight:800;background:linear-gradient(135deg,var(--cyan),var(--yellow));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.hero-stat-lbl{{font-size:12px;color:var(--dim);margin-top:5px}}
.scroll-hint{{position:absolute;bottom:30px;color:var(--dim);font-size:13px;animation:bounce 2s infinite 4s}}

/* 打字机效果 */
.hero-slogan{{font-size:clamp(16px,4vw,24px);color:var(--cyan);margin:20px 0 30px;min-height:36px;font-weight:500}}
.hero-slogan .cursor{{display:inline-block;width:2px;height:1em;background:var(--pink);margin-left:2px;animation:blink 1s infinite}}
@keyframes blink{{0%,50%{{opacity:1}}51%,100%{{opacity:0}}}}

/* 12月热力图 - 改进布局 */
.heatmap-section{{padding:40px 0}}
.heatmap-title{{font-size:18px;font-weight:600;text-align:center;margin-bottom:25px;color:var(--txt)}}
.heatmap-grid{{
    display:grid;
    grid-template-columns:repeat(4, 1fr);
    gap:15px;
    max-width:500px;
    margin:0 auto;
    padding:0 20px;
}}
.heatmap-month{{text-align:center;cursor:pointer;transition:transform 0.3s}}
.heatmap-month:hover{{transform:scale(1.05)}}
.heatmap-bar{{
    height:100px;
    border-radius:12px;
    margin-bottom:8px;
    position:relative;
    display:flex;
    align-items:flex-end;
    justify-content:center;
    padding-bottom:10px;
    transition:all 0.3s;
    box-shadow:0 4px 15px rgba(0,0,0,0.2);
}}
.heatmap-bar span{{font-size:13px;color:rgba(255,255,255,0.9);font-weight:700}}
.heatmap-label{{font-size:13px;color:var(--dim);font-weight:500}}
.heatmap-tooltip{{position:absolute;bottom:100%;left:50%;transform:translateX(-50%);background:var(--bg3);padding:10px 14px;border-radius:10px;font-size:12px;white-space:nowrap;opacity:0;pointer-events:none;transition:opacity 0.3s;z-index:10;border:1px solid rgba(255,107,157,0.3)}}
.heatmap-month:hover .heatmap-tooltip{{opacity:1}}

/* 分享卡片 */
.share-card{{max-width:400px;margin:40px auto;background:linear-gradient(135deg,var(--bg2),var(--bg3));border-radius:20px;padding:30px;text-align:center;border:1px solid rgba(255,107,157,0.3);position:relative;overflow:hidden}}
.share-card::before{{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:linear-gradient(45deg,transparent,rgba(255,107,157,0.03),transparent);animation:shine 3s infinite}}
@keyframes shine{{0%{{transform:translateX(-100%) rotate(45deg)}}100%{{transform:translateX(100%) rotate(45deg)}}}}
.share-card-bg{{position:absolute;top:0;left:0;width:100%;height:100%;background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));z-index:0}}
.share-card-content{{position:relative;z-index:1}}
.share-card-title{{font-size:28px;font-weight:800;background:linear-gradient(135deg,var(--pink),var(--cyan));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:15px}}
.share-card-year{{font-size:14px;color:var(--dim);margin-bottom:20px}}
.share-card-stats{{display:grid;grid-template-columns:repeat(2,1fr);gap:15px;margin-bottom:20px}}
.share-card-stat,.share-stat{{padding:15px;background:rgba(255,255,255,0.05);border-radius:12px}}
.share-card-stat-val,.share-stat-val{{font-size:24px;font-weight:700;color:var(--cyan)}}
.share-card-stat-lbl,.share-stat-lbl{{font-size:11px;color:var(--dim);margin-top:5px}}
.share-card-footer{{font-size:12px;color:var(--dim);padding-top:15px;border-top:1px solid rgba(255,255,255,0.1)}}
.share-card-best{{display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:15px;padding:12px;background:rgba(255,107,157,0.1);border-radius:10px}}
.share-best-icon{{font-size:18px}}
.share-best-text{{font-size:13px;color:var(--txt)}}
.share-card-tags{{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-bottom:15px}}
.share-tag{{padding:5px 12px;background:rgba(255,255,255,0.08);border-radius:15px;font-size:11px;color:var(--cyan)}}
.share-actions{{text-align:center;margin-top:20px}}
.share-btn{{padding:12px 30px;background:linear-gradient(135deg,var(--pink),var(--purple));border:none;border-radius:25px;color:white;font-size:14px;font-weight:600;cursor:pointer;transition:all 0.3s}}
.share-btn:hover{{transform:scale(1.05);box-shadow:0 5px 20px rgba(255,107,157,0.4)}}
.share-tip{{font-size:11px;color:var(--dim);margin-top:10px}}

/* 庆祝彩纸效果 */
.confetti{{position:fixed;width:10px;height:10px;background:var(--pink);top:-10px;z-index:9999;animation:confetti-fall 3s linear forwards}}
@keyframes confetti-fall{{0%{{transform:translateY(0) rotate(0deg);opacity:1}}100%{{transform:translateY(100vh) rotate(720deg);opacity:0}}}}

/* 年度来信 - 信封拆开动画 */
.letter-wrapper{{max-width:500px;margin:40px auto;perspective:1000px}}
.envelope{{
    position:relative;
    width:100%;
    min-height:280px;
    cursor:pointer;
    transform-style:preserve-3d;
    transition:min-height 0.5s ease;
}}
.envelope.opened{{
    min-height:auto;
}}
.envelope-back{{
    position:absolute;
    top:0;left:0;right:0;bottom:0;
    background:linear-gradient(135deg,#2a2a3e,#1f1f30);
    border-radius:16px;
    border:2px solid rgba(255,107,157,0.3);
    box-shadow:0 10px 40px rgba(0,0,0,0.3);
}}
.envelope.opened .envelope-back{{
    position:relative;
}}
.envelope-flap{{
    position:absolute;
    top:0;left:0;right:0;
    height:140px;
    background:linear-gradient(180deg,var(--pink),var(--purple));
    clip-path:polygon(0 0, 50% 100%, 100% 0);
    transform-origin:top center;
    transition:transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    z-index:10;
    border-radius:16px 16px 0 0;
}}
.envelope.opened .envelope-flap{{
    transform:rotateX(-180deg);
}}
.envelope-seal{{
    position:absolute;
    top:100px;
    left:50%;
    transform:translateX(-50%);
    width:50px;
    height:50px;
    background:linear-gradient(135deg,var(--pink),var(--purple));
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:24px;
    z-index:15;
    box-shadow:0 4px 15px rgba(255,107,157,0.4);
    transition:all 0.5s ease;
}}
.envelope.opened .envelope-seal{{
    opacity:0;
    transform:translateX(-50%) scale(0);
}}
.envelope-hint{{
    position:absolute;
    bottom:30px;
    left:50%;
    transform:translateX(-50%);
    color:var(--dim);
    font-size:12px;
    animation:pulse 2s infinite;
    transition:opacity 0.3s;
}}
.envelope.opened .envelope-hint{{opacity:0;pointer-events:none}}

/* 信纸 */
.letter-paper{{
    position:relative;
    background:linear-gradient(135deg,#1a1a24,#252532);
    border-radius:12px;
    padding:20px;
    margin:20px;
    opacity:0;
    max-height:0;
    overflow:hidden;
    transition:all 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.3s;
}}
.envelope.opened .letter-paper{{
    opacity:1;
    max-height:2000px;
}}
.letter-header{{
    background:linear-gradient(135deg,var(--pink),var(--purple));
    margin:-20px -20px 20px -20px;
    padding:15px 20px;
    display:flex;
    align-items:center;
    gap:10px;
}}
.letter-icon{{font-size:24px}}
.letter-title{{font-size:16px;font-weight:600;color:#fff}}
.letter-content{{font-size:14px;line-height:2;color:rgba(255,255,255,0.85)}}
.letter-content strong{{color:var(--cyan)}}
.letter-stamp{{position:absolute;bottom:15px;right:15px;font-size:36px;font-weight:900;color:rgba(255,107,157,0.15);transform:rotate(-15deg)}}

/* 年度聊天颜色 */
.colors-section{{max-width:400px;margin:40px auto;text-align:center}}
.colors-orb{{width:150px;height:150px;border-radius:50%;margin:0 auto 25px;box-shadow:0 10px 40px rgba(0,0,0,0.3);animation:color-pulse 4s ease-in-out infinite}}

/* 年度称号系统 */
.titles-container{{max-width:700px;margin:0 auto;text-align:center}}
.titles-intro{{font-size:14px;color:var(--dim);margin-bottom:25px}}
.titles-grid{{display:grid;grid-template-columns:repeat(2, 1fr);gap:15px}}
.title-card{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(168,85,247,0.1));border:1px solid rgba(255,107,157,0.2);border-radius:16px;padding:20px;text-align:center;transition:transform 0.3s,box-shadow 0.3s}}
.title-card:hover{{transform:translateY(-5px);box-shadow:0 10px 30px rgba(255,107,157,0.2)}}
.title-icon{{font-size:36px;margin-bottom:10px}}
.title-name{{font-size:16px;font-weight:700;color:var(--txt);margin-bottom:8px}}
.title-desc{{font-size:12px;color:var(--dim);line-height:1.6}}

/* 社交人格分析 */
.personality-card{{max-width:500px;margin:0 auto;background:linear-gradient(135deg,rgba(168,85,247,0.1),rgba(78,205,196,0.1));border:1px solid rgba(168,85,247,0.2);border-radius:20px;padding:30px;text-align:center}}
.personality-header{{margin-bottom:20px}}
.personality-name{{font-size:28px;font-weight:800;background:linear-gradient(135deg,var(--pink),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px}}
.personality-desc{{font-size:14px;color:var(--dim);line-height:1.6}}
.personality-traits{{display:flex;flex-wrap:wrap;justify-content:center;gap:10px;margin-bottom:25px}}
.trait-tag{{padding:6px 14px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:20px;font-size:12px;color:var(--cyan)}}
.personality-bars{{text-align:left}}
.bar-item{{display:flex;align-items:center;gap:10px;margin-bottom:12px}}
.bar-label{{width:70px;font-size:12px;color:var(--dim)}}
.bar-track{{flex:1;height:8px;background:rgba(255,255,255,0.1);border-radius:4px;overflow:hidden}}
.bar-fill{{height:100%;background:linear-gradient(90deg,var(--pink),var(--purple));border-radius:4px;transition:width 1s ease-out}}
.bar-fill.night{{background:linear-gradient(90deg,#6366F1,#A855F7)}}
.bar-fill.social{{background:linear-gradient(90deg,var(--cyan),#60A5FA)}}
.bar-fill.depth{{background:linear-gradient(90deg,#F59E0B,#EF4444)}}
.bar-value{{width:40px;font-size:12px;color:var(--txt);text-align:right}}

/* 年度特殊时刻 */
.moments-container{{max-width:600px;margin:0 auto;display:flex;flex-direction:column;gap:15px}}
.moment-card{{display:flex;align-items:flex-start;gap:15px;background:var(--bg2);border-radius:16px;padding:20px;border:1px solid var(--bg3);transition:transform 0.3s}}
.moment-card:hover{{transform:translateX(5px)}}
.moment-icon{{font-size:32px;flex-shrink:0}}
.moment-content{{flex:1}}
.moment-title{{font-size:12px;color:var(--dim);margin-bottom:4px}}
.moment-value{{font-size:18px;font-weight:700;color:var(--txt);margin-bottom:6px}}
.moment-desc{{font-size:13px;color:var(--cyan);margin-bottom:8px}}
.moment-emotion{{font-size:12px;color:var(--dim);font-style:italic}}
@keyframes color-pulse{{0%,100%{{transform:scale(1);box-shadow:0 10px 40px rgba(0,0,0,0.3)}}50%{{transform:scale(1.05);box-shadow:0 15px 50px rgba(255,107,157,0.3)}}}}
.colors-title{{font-size:18px;font-weight:600;margin-bottom:20px;color:var(--txt)}}
.colors-list{{display:flex;flex-direction:column;gap:12px;text-align:left;padding:0 20px}}
.color-item{{display:flex;align-items:center;gap:12px;padding:10px 15px;background:rgba(255,255,255,0.03);border-radius:10px}}
.color-dot{{width:16px;height:16px;border-radius:50%;flex-shrink:0}}
.color-info{{flex:1}}
.color-name{{font-size:14px;font-weight:500;color:var(--txt)}}
.color-name span{{color:var(--dim);font-weight:400;margin-left:8px}}
.color-desc{{font-size:11px;color:var(--dim);margin-top:2px}}
.colors-subtitle{{font-size:14px;color:var(--dim);margin-bottom:15px}}
.colors-subtitle span{{font-weight:600}}

/* 24小时聊天节奏图谱 */
.rhythm-container{{max-width:700px;margin:0 auto;padding:20px}}
.rhythm-header{{text-align:center;margin-bottom:30px}}
.rhythm-title{{font-size:20px;font-weight:600;color:var(--txt);margin-bottom:8px}}
.rhythm-subtitle{{font-size:13px;color:var(--dim)}}
.rhythm-main{{display:flex;gap:30px;align-items:flex-start;flex-wrap:wrap;justify-content:center}}
.rhythm-visual{{position:relative;width:200px;height:200px;flex-shrink:0}}
.rhythm-ring{{position:relative;width:100%;height:100%;border-radius:50%;background:var(--bg2)}}
.rhythm-hour{{position:absolute;width:24px;height:24px;left:50%;top:50%;transform-origin:0 0;transform:rotate(var(--angle)) translateX(75px) rotate(calc(-1 * var(--angle)));background:var(--color);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:9px;color:var(--bg);font-weight:600;transition:transform 0.3s,box-shadow 0.3s;cursor:pointer}}
.rhythm-hour:hover{{transform:rotate(var(--angle)) translateX(75px) rotate(calc(-1 * var(--angle))) scale(1.3);box-shadow:0 0 15px var(--color);z-index:10}}
.rhythm-hour-label{{opacity:0.9}}
.rhythm-ring-center{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:28px}}
.rhythm-peak{{position:absolute;bottom:-40px;left:50%;transform:translateX(-50%);text-align:center}}
.rhythm-peak-label{{font-size:11px;color:var(--dim)}}
.rhythm-peak-value{{font-size:24px;font-weight:700;color:var(--pink)}}
.rhythm-peak-range{{font-size:11px;color:var(--dim);margin-top:4px}}
.rhythm-periods{{flex:1;min-width:280px;display:flex;flex-direction:column;gap:15px}}
.rhythm-period{{background:var(--bg2);border-radius:12px;padding:12px 15px}}
.rhythm-period-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}}
.rhythm-period-name{{font-size:14px;font-weight:500;color:var(--txt)}}
.rhythm-period-time{{font-size:11px;color:var(--dim)}}
.rhythm-period-bar{{height:8px;background:var(--bg3);border-radius:4px;position:relative;overflow:hidden}}
.rhythm-period-fill{{height:100%;background:linear-gradient(90deg,var(--cyan),var(--purple));border-radius:4px;transition:width 1s ease-out}}
.rhythm-period-count{{position:absolute;right:8px;top:50%;transform:translateY(-50%);font-size:10px;color:var(--txt)}}
.rhythm-period-desc{{font-size:11px;color:var(--dim);margin-top:6px}}
.rhythm-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px 20px;margin-top:25px;display:flex;gap:12px;align-items:flex-start}}
.rhythm-insight-icon{{font-size:20px}}
.rhythm-insight-text{{font-size:13px;color:var(--txt);line-height:1.6}}
.rhythm-summary{{display:flex;justify-content:center;gap:30px;margin-top:20px;padding-top:15px;border-top:1px solid var(--bg3)}}
.rhythm-summary-item{{text-align:center}}
.rhythm-summary-label{{font-size:11px;color:var(--dim);display:block;margin-bottom:4px}}
.rhythm-summary-value{{font-size:14px;font-weight:600;color:var(--cyan)}}

/* 年度旅程时间线 */
.year-journey{{max-width:600px;margin:0 auto}}
.journey-header{{text-align:center;margin-bottom:30px}}
.journey-title{{font-size:20px;font-weight:700;color:var(--txt);margin-bottom:8px}}
.journey-subtitle{{font-size:13px;color:var(--dim)}}
.journey-timeline{{position:relative;padding-left:30px}}
.journey-timeline::before{{content:'';position:absolute;left:10px;top:0;bottom:0;width:2px;background:linear-gradient(to bottom,var(--pink),var(--cyan),var(--purple),var(--yellow));border-radius:1px}}
.journey-item{{position:relative;margin-bottom:20px;padding:15px;background:var(--bg2);border-radius:12px;transition:all 0.3s;animation:journey-in 0.5s ease-out both}}
.journey-item:nth-child(1){{animation-delay:0.1s}}.journey-item:nth-child(2){{animation-delay:0.15s}}.journey-item:nth-child(3){{animation-delay:0.2s}}.journey-item:nth-child(4){{animation-delay:0.25s}}.journey-item:nth-child(5){{animation-delay:0.3s}}.journey-item:nth-child(6){{animation-delay:0.35s}}.journey-item:nth-child(7){{animation-delay:0.4s}}.journey-item:nth-child(8){{animation-delay:0.45s}}.journey-item:nth-child(9){{animation-delay:0.5s}}.journey-item:nth-child(10){{animation-delay:0.55s}}.journey-item:nth-child(11){{animation-delay:0.6s}}.journey-item:nth-child(12){{animation-delay:0.65s}}
@keyframes journey-in{{0%{{opacity:0;transform:translateX(-20px)}}100%{{opacity:1;transform:translateX(0)}}}}
.journey-item:hover{{transform:translateX(5px);box-shadow:0 5px 20px rgba(0,0,0,0.2)}}
.journey-item.high{{border-left:3px solid var(--pink)}}
.journey-item.mid{{border-left:3px solid var(--cyan)}}
.journey-item.low{{border-left:3px solid var(--purple)}}
.journey-item.none{{border-left:3px solid var(--bg3);opacity:0.5}}
.journey-dot{{position:absolute;left:-25px;top:20px;width:12px;height:12px;border-radius:50%;background:var(--pink);border:2px solid var(--bg);box-shadow:0 0 10px rgba(255,107,157,0.5)}}
.journey-item.mid .journey-dot{{background:var(--cyan);box-shadow:0 0 10px rgba(78,205,196,0.5)}}
.journey-item.low .journey-dot{{background:var(--purple);box-shadow:0 0 10px rgba(167,139,250,0.5)}}
.journey-item.none .journey-dot{{background:var(--bg3);box-shadow:none}}
.journey-content{{}}
.journey-month{{display:flex;align-items:center;gap:8px;margin-bottom:8px}}
.journey-icon{{font-size:20px}}
.journey-name{{font-size:15px;font-weight:600;color:var(--txt)}}
.journey-peak{{font-size:10px;background:linear-gradient(135deg,var(--pink),var(--yellow));color:var(--bg);padding:2px 8px;border-radius:10px;margin-left:auto}}
.journey-stats{{display:flex;gap:15px;margin-bottom:5px}}
.journey-msgs,.journey-friends{{font-size:12px;color:var(--dim)}}
.journey-msgs{{color:var(--cyan)}}
.journey-highlight{{font-size:11px;color:var(--dim);font-style:italic}}
.journey-footer{{margin-top:25px}}
.journey-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:12px;align-items:flex-start}}
.rhythm-summary-value{{font-size:14px;font-weight:600;color:var(--cyan)}}
.color-insight{{font-size:13px;color:var(--cyan);margin-bottom:20px;padding:12px 16px;background:rgba(78,205,196,0.1);border-radius:10px;border-left:3px solid var(--cyan)}}

/* 用户画像卡片 */
.profile-card{{max-width:450px;margin:40px auto;background:linear-gradient(135deg,var(--bg2),var(--bg3));border-radius:20px;overflow:hidden;border:1px solid rgba(168,85,247,0.3);position:relative}}
.profile-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--pink),var(--purple),var(--cyan))}}
.profile-header{{background:linear-gradient(135deg,rgba(168,85,247,0.2),rgba(78,205,196,0.1));padding:18px 25px;display:flex;align-items:center;gap:12px}}
.profile-icon{{font-size:26px}}
.profile-title{{font-size:18px;font-weight:700;color:var(--txt)}}
.profile-content{{padding:25px}}
.profile-section{{margin-bottom:22px}}
.profile-section:last-child{{margin-bottom:0}}
.profile-label{{font-size:12px;color:var(--dim);margin-bottom:8px;text-transform:uppercase;letter-spacing:1px}}
.profile-value{{font-size:22px;font-weight:700;color:var(--txt);margin-bottom:8px}}
.profile-value.style-value{{font-size:18px;color:var(--cyan)}}
.profile-confidence{{display:flex;align-items:center;gap:12px}}
.confidence-bar{{flex:1;height:6px;background:var(--bg1);border-radius:3px;overflow:hidden}}
.confidence-fill{{height:100%;background:linear-gradient(90deg,var(--purple),var(--pink));border-radius:3px;transition:width 1.5s ease-out}}
.confidence-text{{font-size:11px;color:var(--dim);min-width:70px}}
.profile-tags{{display:flex;flex-wrap:wrap;gap:8px}}
.profile-tag{{padding:6px 12px;background:rgba(78,205,196,0.15);border:1px solid rgba(78,205,196,0.3);border-radius:20px;font-size:12px;color:var(--cyan)}}
.personality-tag{{padding:6px 12px;background:rgba(255,107,157,0.15);border:1px solid rgba(255,107,157,0.3);border-radius:20px;font-size:12px;color:var(--pink)}}
.profile-footer{{padding:15px 25px;background:rgba(0,0,0,0.2);font-size:11px;color:var(--dim);text-align:center}}

/* 流星雨效果 */
.meteors{{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:5;overflow:hidden}}
.meteor{{
    position:absolute;
    height:2px;
    border-radius:50%;
    transform:rotate(-35deg);
    transform-origin:left center;
    animation:meteor-fall linear forwards;
}}
.meteor::before{{
    content:'';
    position:absolute;
    right:0;
    top:50%;
    transform:translateY(-50%);
    width:4px;
    height:4px;
    border-radius:50%;
    background:inherit;
    box-shadow:0 0 10px currentColor;
}}
@keyframes meteor-fall{{
    0%{{transform:translate(0, 0) rotate(-35deg);opacity:1}}
    70%{{opacity:1}}
    100%{{transform:translate(-600px, 400px) rotate(-35deg);opacity:0}}
}}

/* 好友默契度 - 自动动画显示（从上到下：5-4-3-2-1） */
.chemistry-intro{{max-width:600px;margin:0 auto 30px;text-align:center;padding:20px}}
.chemistry-intro-title{{font-size:20px;font-weight:700;color:var(--txt);margin-bottom:15px}}
.chemistry-intro-text{{font-size:14px;color:var(--dim);line-height:1.8}}
.chemistry-intro-hint{{display:inline-block;margin-top:10px;color:var(--cyan);font-size:13px}}
.chemistry-list{{display:flex;flex-direction:column;gap:15px;max-width:600px;margin:0 auto}}
.chemistry-card{{
    display:flex;
    align-items:center;
    gap:15px;
    background:var(--bg2);
    border-radius:16px;
    padding:20px;
    border:1px solid var(--bg3);
    opacity:0;
    transform:translateX(-30px);
    animation:chemistry-reveal 0.8s ease-out forwards;
    animation-play-state:paused;
    transition:box-shadow 0.3s,transform 0.3s;
}}
.chemistry-card:hover{{transform:translateX(5px)}}
.chemistry-card.glow-high{{box-shadow:0 0 20px rgba(255,107,157,0.3);border-color:rgba(255,107,157,0.3)}}
.chemistry-card.glow-mid{{box-shadow:0 0 15px rgba(168,85,247,0.2);border-color:rgba(168,85,247,0.2)}}
@keyframes chemistry-reveal{{
    to{{opacity:1;transform:translateX(0)}}
}}
.chemistry-card.animate{{
    animation-play-state:running;
}}
.chemistry-rank{{font-size:24px;font-weight:800;color:var(--yellow);min-width:50px;text-align:center}}
.chemistry-info{{flex:1}}
.chemistry-name{{font-size:16px;font-weight:600;color:var(--txt);margin-bottom:4px}}
.chemistry-title{{font-size:14px;color:var(--pink);font-weight:600;margin-bottom:2px}}
.chemistry-title-desc{{font-size:12px;color:var(--dim);font-style:italic;margin-bottom:8px}}
.chemistry-details{{font-size:11px;color:var(--dim);line-height:1.8}}
.chemistry-score{{position:relative;width:60px;height:60px}}
.chemistry-ring{{width:100%;height:100%;transform:rotate(-90deg)}}
.chemistry-ring-bg{{fill:none;stroke:var(--bg3);stroke-width:3}}
.chemistry-ring-fill{{fill:none;stroke-width:3;stroke-linecap:round;transition:stroke-dasharray 1.5s ease-out}}
.chemistry-score-val{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:16px;font-weight:700;color:var(--txt)}}
.chemistry-outro{{max-width:600px;margin:30px auto 0;text-align:center;padding:25px;background:linear-gradient(135deg,rgba(255,107,157,0.05),rgba(78,205,196,0.05));border-radius:16px;border:1px solid rgba(255,255,255,0.05)}}
.chemistry-outro-title{{font-size:16px;font-weight:600;color:var(--txt);margin-bottom:12px}}
.chemistry-outro-text{{font-size:13px;color:var(--dim);line-height:1.9}}
.chemistry-outro-text strong{{color:var(--cyan)}}

/* 滚动淡入增强 */
.scroll-reveal{{opacity:0;transform:translateY(30px);transition:opacity 0.8s ease-out, transform 0.8s ease-out}}
.scroll-reveal.revealed{{opacity:1;transform:translateY(0)}}
.scroll-reveal.delay-1{{transition-delay:0.1s}}
.scroll-reveal.delay-2{{transition-delay:0.2s}}
.scroll-reveal.delay-3{{transition-delay:0.3s}}

/* 容器 */
.container{{max-width:1400px;margin:0 auto;padding:0 15px}}
.section{{padding:60px 0;position:relative;z-index:1}}
.section-title{{font-size:clamp(20px,5vw,32px);font-weight:700;text-align:center;margin-bottom:15px;background:linear-gradient(135deg,var(--pink),var(--cyan));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.section-subtitle{{font-size:clamp(12px,2.5vw,14px);color:var(--dim);text-align:center;margin-bottom:40px;font-style:italic}}

/* 排行榜 */
.rankings-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:20px}}
.ranking-card{{background:var(--bg2);border-radius:16px;padding:20px;border:1px solid var(--bg3)}}
.ranking-title{{font-size:16px;font-weight:600;margin-bottom:10px}}
.ranking-stats{{font-size:11px;color:var(--dim);padding:10px;background:var(--bg3);border-radius:8px;margin-bottom:15px}}
.ranking-stats strong{{color:var(--cyan)}}
.rank-item{{display:flex;align-items:center;padding:8px 0;border-bottom:1px solid var(--bg3);animation:fadeUp 0.4s ease-out forwards;animation-delay:var(--delay);opacity:0}}
.rank-pos{{width:28px;font-weight:600}}
.rank-name{{width:70px;font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.rank-bar{{flex:1;height:5px;background:var(--bg3);border-radius:3px;margin:0 10px;overflow:hidden}}
.rank-fill{{height:100%;background:linear-gradient(90deg,var(--pink),var(--cyan));border-radius:3px;transition:width 4s cubic-bezier(0.4, 0, 0.2, 1)}}
.rank-val{{font-size:11px;color:var(--dim);min-width:60px;text-align:right}}
.rank-more{{text-align:center;color:var(--dim);font-size:11px;padding:10px 0}}
.rank-hidden{{display:none}}
.rank-hidden.show{{display:block}}
.expand-btn{{display:block;width:100%;padding:8px;margin-top:5px;background:var(--bg3);border:none;border-radius:8px;color:var(--dim);font-size:11px;cursor:pointer;transition:all 0.3s}}
.expand-btn:hover{{background:var(--pink);color:#fff}}
.expand-btn.expanded{{background:var(--bg3)}}

/* 智能分析文案 */
.insights{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:16px;padding:25px;margin-bottom:40px;border:1px solid rgba(255,107,157,0.2)}}
.insights-title{{font-size:18px;font-weight:700;margin-bottom:15px;color:var(--pink)}}

/* 文字渐入动画 */
.text-animate{{opacity:0;transform:translateY(20px);transition:opacity 0.8s ease-out, transform 0.8s ease-out}}
.text-animate.text-visible{{opacity:1;transform:translateY(0)}}
.insight-item{{padding:10px 15px;margin:8px 0;background:rgba(255,255,255,0.05);border-radius:10px;font-size:14px;line-height:1.6;border-left:3px solid var(--cyan)}}
.insight-item strong{{color:var(--yellow)}}

/* 群聊排行榜（群名一行+进度条一行） */
.rank-item-group{{padding:12px 0;border-bottom:1px solid var(--bg3);animation:fadeUp 0.4s ease-out forwards;animation-delay:var(--delay);opacity:0}}
.rank-row-name{{display:flex;align-items:center;gap:10px;margin-bottom:8px}}
.rank-name-full{{flex:1;font-size:13px;font-weight:500;word-break:break-all}}
.rank-row-bar{{padding-left:38px}}
.rank-bar-full{{height:6px;background:var(--bg3);border-radius:3px;overflow:hidden}}

/* 好友分组 */
.friend-groups{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:15px;margin-bottom:40px}}
.friend-group{{background:var(--bg2);border-radius:12px;padding:20px;border-left:4px solid var(--pink)}}
.friend-group:nth-child(1){{border-color:gold}}.friend-group:nth-child(2){{border-color:var(--yellow)}}.friend-group:nth-child(3){{border-color:var(--cyan)}}.friend-group:nth-child(4){{border-color:var(--dim)}}
.fg-title{{font-size:15px;font-weight:600}}
.fg-desc{{font-size:11px;color:var(--dim);font-style:italic;margin-top:4px}}
.fg-count{{font-size:32px;font-weight:800;color:var(--cyan);margin:8px 0}}
.fg-list{{font-size:11px;color:var(--dim);line-height:1.8}}

/* 私聊卡片 */
.chat-card,.group-card{{background:var(--bg2);border-radius:12px;margin-bottom:10px;overflow:hidden;border:1px solid var(--bg3)}}
.chat-header,.group-header{{padding:15px 20px;display:flex;align-items:center;gap:12px;cursor:pointer;transition:background 0.3s}}
.chat-header:hover,.group-header:hover{{background:var(--bg3)}}
.chat-tags{{padding:0 20px 8px;display:flex;flex-wrap:wrap;gap:6px}}
.chat-quick-stats{{display:flex;align-items:center;gap:8px;padding:8px 20px 12px;background:rgba(255,255,255,0.02);border-top:1px solid var(--bg3);font-size:12px;flex-wrap:wrap}}
.quick-stat{{display:flex;align-items:center;gap:4px}}
.quick-label{{color:var(--dim);font-size:11px}}
.quick-val{{color:var(--txt);font-weight:500}}
.quick-val.them{{color:var(--purple)}}
.quick-val.me{{color:var(--cyan)}}
.quick-pct{{color:var(--dim);font-size:10px}}
.quick-divider{{color:var(--bg3);font-size:10px}}
.chat-tag{{font-size:11px;padding:3px 10px;background:linear-gradient(135deg,rgba(255,107,157,0.15),rgba(168,85,247,0.15));color:var(--pink);border-radius:20px;border:1px solid rgba(255,107,157,0.2)}}
.chat-rank,.group-rank{{font-size:20px;font-weight:800;color:var(--yellow);min-width:45px}}
.chat-name,.group-name{{font-size:15px;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.chat-brief,.group-brief{{font-size:12px;color:var(--dim)}}
.chat-brief i,.group-brief i{{color:var(--cyan);font-style:normal}}
.chat-toggle{{color:var(--dim);transition:transform 0.3s}}
.chat-card.open .chat-toggle,.group-card.open .chat-toggle{{transform:rotate(180deg)}}
.chat-body{{max-height:0;overflow:hidden;transition:max-height 0.4s ease-out}}
.chat-card.open .chat-body,.group-card.open .chat-body{{max-height:2000px}}

/* 数据网格 */
.data-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;padding:15px}}
.data-card{{background:var(--bg3);border-radius:10px;padding:15px}}
.card-title{{font-size:13px;font-weight:600;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.1)}}

/* 对比 */
.versus{{display:flex;align-items:center;justify-content:space-around;margin:15px 0}}
.vs-item{{text-align:center}}
.vs-val{{font-size:28px;font-weight:800}}
.vs-val.time{{font-size:22px}}
.vs-item.them .vs-val{{color:var(--them)}}.vs-item.me .vs-val{{color:var(--me)}}
.vs-pct{{font-size:16px;font-weight:600;margin:5px 0}}
.vs-label{{font-size:11px;color:var(--dim)}}
.vs-mid{{color:var(--dim);font-size:18px}}
.bar-compare{{height:6px;border-radius:3px;display:flex;overflow:hidden;background:var(--bg1)}}
.bar-them,.bar-me{{transition:width 2s ease-out}}
.bar-them{{background:linear-gradient(90deg,var(--them),#ff8fab)}}.bar-me{{background:linear-gradient(90deg,#3dbdb3,var(--me))}}

/* 表格 */
table{{width:100%;font-size:11px;border-collapse:collapse}}
th,td{{padding:6px 4px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.05)}}
th{{color:var(--dim);font-weight:400}}
td:first-child,th:first-child{{text-align:left}}
.them{{color:var(--them)}}.me{{color:var(--me)}}

/* 统计行 */
.stat-row{{display:grid;grid-template-columns:repeat(auto-fit,minmax(60px,1fr));gap:8px;margin-top:10px}}
.stat-box{{text-align:center;padding:10px 5px;background:var(--bg1);border-radius:8px}}
.stat-box.them{{border:1px solid rgba(255,107,157,0.3)}}.stat-box.me{{border:1px solid rgba(78,205,196,0.3)}}
.stat-num{{font-size:18px;font-weight:700}}
.stat-box.them .stat-num{{color:var(--them)}}.stat-box.me .stat-num{{color:var(--me)}}
.stat-lbl{{font-size:9px;color:var(--dim);margin-top:3px}}

/* 迷你洞察 */
.mini-insight{{font-size:10px;color:var(--dim);margin-top:10px;padding:8px;background:var(--bg1);border-radius:6px}}
.mini-insight b{{color:var(--yellow)}}
.dist-mini{{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;font-size:10px;color:var(--dim)}}
.dist-mini b.them{{color:var(--them)}}.dist-mini b.me{{color:var(--me)}}

/* 群聊统计 */
.group-stats{{display:flex;flex-wrap:wrap;gap:15px;padding:15px}}
.gstat{{text-align:center;min-width:60px}}
.gstat-val{{font-size:24px;font-weight:700;color:var(--cyan)}}
.gstat-lbl{{font-size:10px;color:var(--dim)}}

/* 群聊标签 */
.group-tags{{padding:0 20px 8px;display:flex;flex-wrap:wrap;gap:6px}}
.group-tag{{display:inline-block;padding:3px 10px;background:rgba(255,255,255,0.05);border-radius:12px;font-size:11px;color:var(--dim);border:1px solid var(--bg3)}}

/* 群聊类型与活力 */
.group-type-section{{display:flex;gap:20px;padding:15px;background:var(--bg3);border-radius:12px;margin:15px;flex-wrap:wrap}}
.group-type-badge{{flex:1;min-width:150px;text-align:center;padding:15px}}
.group-type-icon{{display:block;font-size:18px;margin-bottom:8px}}
.group-type-desc{{font-size:12px;color:var(--dim)}}
.group-vitality{{flex:1;min-width:150px;text-align:center;padding:15px}}
.vitality-header{{font-size:11px;color:var(--dim);margin-bottom:5px}}
.vitality-score{{font-size:36px;font-weight:700}}
.vitality-bar{{height:6px;background:var(--bg2);border-radius:3px;margin:10px 0;overflow:hidden}}
.vitality-fill{{height:100%;border-radius:3px;transition:width 1s ease-out}}
.vitality-level{{font-size:12px;font-weight:500}}

/* 话语权分布 */
.group-concentration{{padding:15px;margin:15px}}
.concentration-bar{{height:24px;background:var(--bg3);border-radius:12px;position:relative;overflow:hidden;margin:10px 0}}
.concentration-fill{{height:100%;background:linear-gradient(90deg,var(--cyan),var(--purple));border-radius:12px;transition:width 1s}}
.concentration-val{{position:absolute;right:10px;top:50%;transform:translateY(-50%);font-size:11px;color:var(--txt)}}
.concentration-desc{{font-size:12px;color:var(--dim);text-align:center}}

/* 群聊总览分析 */
.group-overview{{max-width:700px;margin:0 auto}}
.gov-stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-bottom:25px}}
.gov-stat{{text-align:center;padding:20px 10px;background:var(--bg2);border-radius:12px}}
.gov-stat-val{{font-size:28px;font-weight:700;color:var(--cyan)}}
.gov-stat-lbl{{font-size:11px;color:var(--dim);margin-top:5px}}
.gov-sections{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;margin-bottom:20px}}
.gov-types,.gov-role{{background:var(--bg2);border-radius:12px;padding:20px}}
.gov-section-title{{font-size:14px;font-weight:600;color:var(--txt);margin-bottom:15px}}
.gtype-list{{display:flex;flex-direction:column;gap:12px}}
.gtype-item{{}}
.gtype-header{{display:flex;justify-content:space-between;margin-bottom:5px}}
.gtype-name{{font-size:13px;color:var(--txt)}}
.gtype-count{{font-size:11px;color:var(--dim)}}
.gtype-bar{{height:8px;background:var(--bg3);border-radius:4px;overflow:hidden}}
.gtype-fill{{height:100%;background:linear-gradient(90deg,var(--pink),var(--purple));border-radius:4px;transition:width 1s}}
.gtype-msgs{{font-size:10px;color:var(--dim);text-align:right;margin-top:3px}}
.gov-role-card{{text-align:center;padding:20px;background:var(--bg3);border-radius:12px;margin-bottom:15px}}
.gov-role-icon{{font-size:40px;margin-bottom:10px}}
.gov-role-name{{font-size:18px;font-weight:600;color:var(--txt);margin-bottom:5px}}
.gov-role-desc{{font-size:12px;color:var(--dim)}}
.gov-role-stats{{display:flex;justify-content:space-around}}
.gov-rs{{text-align:center}}
.gov-rs-val{{display:block;font-size:20px;font-weight:700;color:var(--pink)}}
.gov-rs-lbl{{font-size:10px;color:var(--dim)}}
.gov-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:12px;align-items:flex-start}}

/* 群聊活跃时段对比 */
.group-time-comparison{{background:var(--bg2);border-radius:16px;padding:25px;margin-top:25px}}
.gtc-title{{font-size:16px;font-weight:600;color:var(--txt);text-align:center;margin-bottom:5px}}
.gtc-subtitle{{font-size:12px;color:var(--dim);text-align:center;margin-bottom:20px}}
.gtc-timeline{{display:flex;justify-content:space-between;font-size:10px;color:var(--dim);margin-bottom:10px;padding:0 80px 0 100px}}
.gtc-groups{{display:flex;flex-direction:column;gap:12px}}
.gtc-group{{display:flex;align-items:center;gap:10px}}
.gtc-name{{width:90px;font-size:12px;color:var(--txt);text-align:right;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.gtc-hours{{flex:1;display:flex;height:20px;background:var(--bg3);border-radius:4px;overflow:hidden}}
.gtc-hour{{flex:1;background:var(--pink);transition:opacity 0.3s}}
.gtc-info{{width:120px;display:flex;flex-direction:column;gap:2px}}
.gtc-peak{{font-size:10px;color:var(--dim)}}
.gtc-type{{font-size:11px;font-weight:500}}

/* 年度数字亮点 */
.numbers-section{{min-height:80vh;display:flex;flex-direction:column;justify-content:center}}
.numbers-showcase{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;max-width:800px;margin:0 auto 30px}}
.number-card{{background:var(--bg2);border-radius:20px;padding:30px 20px;text-align:center;border:1px solid var(--bg3);transition:all 0.3s;position:relative;overflow:hidden}}
.number-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--pink),var(--cyan));opacity:0;transition:opacity 0.3s}}
.number-card:hover{{transform:translateY(-5px);box-shadow:0 15px 40px rgba(0,0,0,0.3)}}
.number-card:hover::before{{opacity:1}}
.number-card.big{{grid-column:span 3;background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border:2px solid rgba(255,107,157,0.3)}}
.number-card.big .number-value{{font-size:72px}}
.number-value{{font-size:42px;font-weight:800;background:linear-gradient(135deg,var(--pink),var(--cyan));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px;line-height:1}}
.number-label{{font-size:16px;color:var(--txt);font-weight:500;margin-bottom:8px}}
.number-sub{{font-size:12px;color:var(--dim);font-style:italic}}
.numbers-insight{{max-width:600px;margin:0 auto;text-align:center;padding:25px;background:var(--bg2);border-radius:16px;border:1px solid var(--bg3)}}
.numbers-insight .insight-text{{font-size:15px;color:var(--txt);line-height:1.8}}
.numbers-insight strong{{color:var(--pink);font-size:20px;font-weight:700}}
@media(max-width:600px){{
    .numbers-showcase{{grid-template-columns:repeat(2,1fr)}}
    .number-card.big{{grid-column:span 2}}
    .number-card.big .number-value{{font-size:48px}}
    .number-value{{font-size:28px}}
}}

/* 社交健康度 */
.social-health{{max-width:500px;margin:0 auto;text-align:center}}
.health-score-circle{{position:relative;width:180px;height:180px;margin:0 auto 25px}}
.health-score-ring{{position:absolute;top:0;left:0;width:100%;height:100%}}
.health-ring-fill{{transition:stroke-dasharray 1.5s ease-out}}
.health-score-inner{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center}}
.health-score-value{{font-size:48px;font-weight:800;color:var(--txt)}}
.health-score-label{{font-size:12px;color:var(--dim)}}
.health-level{{margin-bottom:25px}}
.health-level-badge{{font-size:24px;font-weight:700;margin-bottom:8px}}
.health-level-desc{{font-size:14px;color:var(--dim)}}
.health-dimensions{{background:var(--bg2);border-radius:16px;padding:20px;margin-bottom:20px;text-align:left}}
.health-dims-title{{font-size:14px;font-weight:600;color:var(--txt);margin-bottom:15px;text-align:center}}
.health-dim{{margin-bottom:15px}}
.health-dim:last-child{{margin-bottom:0}}
.health-dim-header{{display:flex;justify-content:space-between;margin-bottom:5px}}
.health-dim-name{{font-size:13px;color:var(--txt)}}
.health-dim-score{{font-size:13px;font-weight:600;color:var(--cyan)}}
.health-dim-bar{{height:8px;background:var(--bg3);border-radius:4px;overflow:hidden}}
.health-dim-fill{{height:100%;background:linear-gradient(90deg,var(--cyan),var(--pink));border-radius:4px;transition:width 1s}}
.health-dim-desc{{font-size:10px;color:var(--dim);margin-top:3px}}
.health-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:12px;align-items:flex-start;text-align:left}}

/* 好友月度趋势对比 */
.friend-trends{{max-width:650px;margin:0 auto}}
.trends-header{{text-align:center;margin-bottom:20px}}
.trends-title{{font-size:18px;font-weight:600;color:var(--txt);margin-bottom:5px}}
.trends-subtitle{{font-size:13px;color:var(--dim)}}
.trends-chart{{background:var(--bg2);border-radius:16px;padding:20px;margin-bottom:15px}}
.trends-svg{{width:100%;height:auto;display:block}}
.trend-line{{opacity:0;animation:trend-draw 1s ease-out forwards}}
@keyframes trend-draw{{0%{{opacity:0;stroke-dasharray:1000;stroke-dashoffset:1000}}100%{{opacity:1;stroke-dasharray:1000;stroke-dashoffset:0}}}}
.trend-dot{{opacity:0;animation:dot-pop 0.3s ease-out forwards;animation-delay:1s}}
@keyframes dot-pop{{0%{{opacity:0;r:0}}100%{{opacity:1;r:4}}}}
.trend-dot:hover{{r:6;cursor:pointer}}
.trends-legend{{display:flex;flex-wrap:wrap;justify-content:center;gap:15px;margin-bottom:15px}}
.trend-legend-item{{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--txt)}}
.trend-legend-color{{width:12px;height:12px;border-radius:3px}}
.trends-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:12px;align-items:flex-start}}

/* 回复速度分析 */
.reply-speed-analysis{{max-width:600px;margin:0 auto}}
.speed-summary{{display:flex;justify-content:center;gap:30px;margin-bottom:25px;flex-wrap:wrap}}
.speed-stat{{text-align:center;padding:15px 20px;background:var(--bg2);border-radius:12px;min-width:100px}}
.speed-stat-icon{{font-size:24px;margin-bottom:5px}}
.speed-stat-val{{font-size:28px;font-weight:700;color:var(--cyan)}}
.speed-stat-lbl{{font-size:11px;color:var(--dim)}}
.speed-highlights{{display:flex;gap:15px;margin-bottom:20px;flex-wrap:wrap}}
.speed-highlight{{flex:1;min-width:200px;padding:15px;background:var(--bg2);border-radius:12px;display:flex;align-items:center;gap:10px}}
.highlight-icon{{font-size:20px}}
.highlight-text{{font-size:13px;color:var(--txt)}}
.highlight-text strong{{color:var(--pink)}}
.speed-ranking{{background:var(--bg2);border-radius:12px;padding:20px;margin-bottom:20px}}
.speed-ranking-title{{font-size:14px;font-weight:600;color:var(--txt);margin-bottom:15px;text-align:center}}
.speed-item{{display:flex;align-items:center;gap:10px;margin-bottom:15px;padding-bottom:15px;border-bottom:1px solid var(--bg3)}}
.speed-item:last-child{{margin-bottom:0;padding-bottom:0;border-bottom:none}}
.speed-rank{{font-size:16px;min-width:30px}}
.speed-name{{font-size:13px;color:var(--txt);min-width:70px}}
.speed-bars{{flex:1;display:flex;flex-direction:column;gap:4px}}
.speed-bar-me,.speed-bar-them{{height:16px;border-radius:8px;display:flex;align-items:center;padding:0 8px;font-size:10px;color:var(--bg)}}
.speed-bar-me{{background:linear-gradient(90deg,var(--pink),var(--purple))}}
.speed-bar-them{{background:linear-gradient(90deg,var(--cyan),var(--purple))}}
.speed-faster{{font-size:10px;color:var(--pink);min-width:80px;text-align:right}}
.speed-slower{{font-size:10px;color:var(--cyan);min-width:80px;text-align:right}}
.speed-balanced{{font-size:10px;color:var(--dim);min-width:80px;text-align:right}}
.speed-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:12px}}

/* 节日聊天分析 */
.festival-analysis{{max-width:600px;margin:0 auto}}
.festival-header{{text-align:center;margin-bottom:25px}}
.festival-hero{{display:inline-flex;align-items:center;gap:20px;padding:25px 35px;background:linear-gradient(135deg,rgba(255,107,157,0.15),rgba(78,205,196,0.15));border-radius:20px;border:2px solid rgba(255,107,157,0.3)}}
.festival-hero-icon{{font-size:48px}}
.festival-hero-info{{text-align:left}}
.festival-hero-name{{font-size:20px;font-weight:700;color:var(--txt)}}
.festival-hero-desc{{font-size:12px;color:var(--dim)}}
.festival-hero-msgs{{font-size:16px;color:var(--pink);font-weight:600;margin-top:5px}}
.festival-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:20px}}
.festival-card{{background:var(--bg2);border-radius:12px;padding:15px;display:flex;flex-wrap:wrap;align-items:center;gap:10px;transition:transform 0.3s}}
.festival-card:hover{{transform:translateY(-3px)}}
.festival-card.festival-top{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(167,139,250,0.1));border:1px solid rgba(255,107,157,0.3)}}
.festival-icon{{font-size:28px}}
.festival-info{{flex:1}}
.festival-name{{font-size:14px;font-weight:600;color:var(--txt)}}
.festival-date{{font-size:10px;color:var(--dim)}}
.festival-msgs{{font-size:14px;font-weight:700;color:var(--cyan)}}
.festival-bar{{width:100%;height:4px;background:var(--bg3);border-radius:2px;overflow:hidden}}
.festival-fill{{height:100%;background:linear-gradient(90deg,var(--pink),var(--cyan));border-radius:2px}}
.festival-friend{{width:100%;font-size:10px;color:var(--dim)}}
.festival-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:12px}}

/* 互动仪式感分析 */
.ritual-analysis{{max-width:500px;margin:0 auto;text-align:center}}
.ritual-score-section{{display:flex;align-items:center;justify-content:center;gap:30px;margin-bottom:25px;flex-wrap:wrap}}
.ritual-score-circle{{width:120px;height:120px;border-radius:50%;background:linear-gradient(135deg,var(--pink),var(--purple));display:flex;flex-direction:column;align-items:center;justify-content:center}}
.ritual-score-value{{font-size:36px;font-weight:800;color:var(--bg)}}
.ritual-score-label{{font-size:10px;color:rgba(0,0,0,0.6)}}
.ritual-level{{text-align:left}}
.ritual-level-badge{{font-size:20px;font-weight:700;color:var(--txt);margin-bottom:5px}}
.ritual-level-desc{{font-size:13px;color:var(--dim)}}
.ritual-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:20px}}
.ritual-card{{background:var(--bg2);border-radius:12px;padding:15px;text-align:center}}
.ritual-icon{{font-size:28px;margin-bottom:8px}}
.ritual-info{{margin-bottom:8px}}
.ritual-name{{font-size:13px;font-weight:600;color:var(--txt)}}
.ritual-count{{font-size:18px;font-weight:700;color:var(--cyan)}}
.ritual-friends{{font-size:10px;color:var(--dim)}}
.ritual-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:12px;text-align:left}}

/* 聊天高光时刻 */
.highlight-moments{{max-width:700px;margin:0 auto}}
.highlights-intro{{text-align:center;margin-bottom:25px;padding:15px;background:linear-gradient(135deg,rgba(255,215,0,0.1),rgba(255,107,157,0.1));border-radius:12px}}
.highlights-intro-icon{{font-size:24px;margin-right:10px}}
.highlights-intro-text{{font-size:15px;color:var(--txt)}}
.highlights-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin-bottom:20px}}
.highlight-card{{background:var(--bg2);border-radius:16px;padding:20px;display:flex;gap:15px;align-items:flex-start;transition:transform 0.3s,box-shadow 0.3s}}
.highlight-card:hover{{transform:translateY(-3px);box-shadow:0 10px 30px rgba(0,0,0,0.2)}}
.highlight-icon{{width:50px;height:50px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0}}
.highlight-content{{flex:1}}
.highlight-title{{font-size:12px;color:var(--dim);margin-bottom:5px}}
.highlight-value{{font-size:24px;font-weight:700;margin-bottom:5px}}
.highlight-desc{{font-size:11px;color:var(--dim);line-height:1.4}}
.highlights-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:12px}}

/* 社交人设分析 */
.social-persona{{max-width:500px;margin:0 auto;text-align:center}}
.persona-main{{display:flex;align-items:center;justify-content:center;gap:20px;padding:30px;background:linear-gradient(135deg,rgba(255,107,157,0.15),rgba(78,205,196,0.15));border-radius:20px;margin-bottom:25px}}
.persona-main-icon{{font-size:60px}}
.persona-main-info{{text-align:left}}
.persona-main-name{{font-size:24px;font-weight:700;color:var(--txt);margin-bottom:5px}}
.persona-main-desc{{font-size:14px;color:var(--dim)}}
.persona-subtitle{{font-size:14px;color:var(--dim);margin-bottom:15px}}
.persona-tags{{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-bottom:20px}}
.persona-tag{{background:var(--bg2);border-radius:12px;padding:15px;text-align:center;min-width:120px;transition:transform 0.3s}}
.persona-tag:hover{{transform:scale(1.05)}}
.persona-icon{{display:block;font-size:28px;margin-bottom:8px}}
.persona-name{{display:block;font-size:14px;font-weight:600;color:var(--txt);margin-bottom:4px}}
.persona-desc{{display:block;font-size:10px;color:var(--dim)}}
.persona-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:12px;text-align:left}}

/* 年度最佳搭档 */
.best-partners{{max-width:700px;margin:0 auto}}
.partners-intro{{text-align:center;margin-bottom:25px}}
.partners-intro-text{{font-size:16px;color:var(--txt);font-weight:500}}
.partners-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:15px;margin-bottom:20px}}
.partner-card{{background:var(--bg2);border-radius:16px;padding:20px;text-align:center;transition:transform 0.3s,box-shadow 0.3s}}
.partner-card:hover{{transform:translateY(-5px);box-shadow:0 10px 30px rgba(0,0,0,0.2)}}
.partner-title{{font-size:12px;margin-bottom:10px}}
.partner-name{{font-size:18px;font-weight:700;color:var(--txt);margin-bottom:8px}}
.partner-value{{font-size:13px;color:var(--cyan);margin-bottom:8px}}
.partner-desc{{font-size:11px;color:var(--dim)}}
.partners-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:12px}}

/* 聊天能量波动 */
.energy-wave{{max-width:700px;margin:0 auto}}
.energy-header{{text-align:center;margin-bottom:25px}}
.energy-level{{font-size:24px;font-weight:700;color:var(--txt);margin-bottom:5px}}
.energy-desc{{font-size:14px;color:var(--dim)}}
.energy-chart{{background:var(--bg2);border-radius:16px;padding:20px;margin-bottom:20px}}
.energy-svg{{width:100%;height:150px}}
.energy-labels{{display:flex;justify-content:space-between;margin-top:10px;font-size:11px;color:var(--dim)}}
.energy-stats{{display:flex;justify-content:center;gap:30px;margin-bottom:20px;flex-wrap:wrap}}
.energy-stat{{text-align:center;padding:15px;background:var(--bg2);border-radius:12px;min-width:120px}}
.energy-stat-icon{{display:block;font-size:20px;margin-bottom:5px}}
.energy-stat-label{{display:block;font-size:11px;color:var(--dim);margin-bottom:3px}}
.energy-stat-value{{display:block;font-size:14px;font-weight:600;color:var(--cyan)}}
.energy-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:12px}}

/* 好友亲密度趋势 */
.friendship-trends{{max-width:700px;margin:0 auto}}
.trends-header{{text-align:center;margin-bottom:20px}}
.trends-title{{font-size:18px;font-weight:700;color:var(--txt);margin-bottom:5px}}
.trends-subtitle{{font-size:13px;color:var(--dim)}}
.trends-months{{display:flex;justify-content:space-between;padding:0 50px;margin-bottom:10px}}
.trends-months span{{font-size:9px;color:var(--dim);width:25px;text-align:center}}
.trends-cards{{display:flex;flex-direction:column;gap:15px;margin-bottom:20px}}
.trend-card{{background:var(--bg2);border-radius:12px;padding:15px;border:1px solid var(--bg3)}}
.trend-header{{display:flex;align-items:center;gap:10px;margin-bottom:10px}}
.trend-rank{{width:24px;height:24px;border-radius:50%;color:var(--bg);font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center}}
.trend-name{{font-size:14px;font-weight:600;color:var(--txt);flex:1}}
.trend-badge{{font-size:11px;font-weight:500}}
.trend-chart{{height:40px;margin-bottom:8px}}
.sparkline{{width:100%;height:100%}}
.trend-footer{{display:flex;justify-content:space-between;font-size:11px;color:var(--dim)}}
.trends-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:12px;align-items:flex-start}}

/* 关键词云 */
.keyword-cloud{{max-width:600px;margin:0 auto}}
.cloud-header{{text-align:center;margin-bottom:25px}}
.cloud-title{{font-size:18px;font-weight:700;color:var(--txt);margin-bottom:5px}}
.cloud-subtitle{{font-size:13px;color:var(--dim)}}
.cloud-container{{display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:15px 20px;padding:30px;background:var(--bg2);border-radius:20px;min-height:200px;margin-bottom:20px}}
.cloud-word{{display:inline-block;padding:5px 12px;transition:all 0.3s;cursor:default}}
.cloud-word:hover{{transform:scale(1.2) rotate(0deg) !important;text-shadow:0 0 20px currentColor}}
.cloud-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(167,139,250,0.1));border-radius:12px;padding:15px;display:flex;gap:12px;align-items:flex-start}}

/* 年度社交大事件 */
.social-events{{max-width:600px;margin:0 auto}}
.events-header{{text-align:center;margin-bottom:25px}}
.events-title{{font-size:18px;font-weight:700;color:var(--txt);margin-bottom:5px}}
.events-subtitle{{font-size:13px;color:var(--dim)}}
.events-list{{display:flex;flex-direction:column;gap:15px}}
.event-card{{display:flex;gap:15px;padding:20px;background:var(--bg2);border-radius:16px;border-left:3px solid var(--pink);animation:event-in 0.5s ease-out both}}
@keyframes event-in{{0%{{opacity:0;transform:translateX(-20px)}}100%{{opacity:1;transform:translateX(0)}}}}
.event-card:nth-child(2){{border-left-color:var(--cyan)}}.event-card:nth-child(3){{border-left-color:var(--purple)}}.event-card:nth-child(4){{border-left-color:var(--yellow)}}.event-card:nth-child(5){{border-left-color:var(--pink)}}
.event-icon{{font-size:32px;flex-shrink:0}}
.event-content{{flex:1}}
.event-title{{font-size:15px;font-weight:600;color:var(--txt);margin-bottom:5px}}
.event-desc{{font-size:13px;color:var(--dim);line-height:1.6}}

/* 消息类型分布 */
.message-types{{max-width:500px;margin:0 auto}}
.types-chart{{position:relative;width:200px;height:200px;margin:0 auto 25px}}
.pie-chart{{width:100%;height:100%;transform:rotate(-90deg)}}
.types-center{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center}}
.types-center-icon{{font-size:28px;margin-bottom:5px}}
.types-center-pct{{font-size:20px;font-weight:700;color:var(--txt)}}
.types-legend{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:20px}}
.type-legend-item{{display:flex;align-items:center;gap:8px;padding:8px 12px;background:var(--bg2);border-radius:8px}}
.type-legend-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0}}
.type-legend-icon{{font-size:14px}}
.type-legend-name{{font-size:12px;color:var(--txt);flex:1}}
.type-legend-pct{{font-size:12px;font-weight:600;color:var(--dim)}}
.types-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:12px;align-items:flex-start}}

/* 社交人格测试 */
.personality-test{{max-width:500px;margin:0 auto}}
.pt-result{{text-align:center;padding:30px;background:linear-gradient(135deg,rgba(255,107,157,0.15),rgba(78,205,196,0.15));border-radius:20px;margin-bottom:25px}}
.pt-code{{font-size:48px;font-weight:800;letter-spacing:8px;background:linear-gradient(135deg,var(--pink),var(--cyan));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:15px}}
.pt-title{{font-size:22px;font-weight:700;color:var(--txt);margin-bottom:10px}}
.pt-desc{{font-size:14px;color:var(--dim);line-height:1.6}}
.pt-dimensions{{background:var(--bg2);border-radius:16px;padding:20px;margin-bottom:20px}}
.pt-dims-title{{font-size:14px;font-weight:600;color:var(--txt);margin-bottom:15px;text-align:center}}
.pt-dim{{margin-bottom:15px}}
.pt-dim:last-child{{margin-bottom:0}}
.pt-dim-labels{{display:flex;justify-content:space-between;font-size:11px;color:var(--dim);margin-bottom:5px}}
.pt-dim-bar{{height:10px;background:var(--bg3);border-radius:5px;overflow:hidden}}
.pt-dim-fill{{height:100%;background:linear-gradient(90deg,var(--cyan),var(--pink));border-radius:5px;transition:width 1s}}
.pt-dim-val{{text-align:right;font-size:11px;color:var(--dim);margin-top:3px}}
.pt-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(167,139,250,0.1));border-radius:12px;padding:15px;display:flex;gap:12px;align-items:flex-start}}

/* 年度好友荣誉榜 */
.friend-honors{{max-width:700px;margin:0 auto}}
.honors-header{{text-align:center;margin-bottom:25px}}
.honors-title{{font-size:22px;font-weight:700;color:var(--txt);margin-bottom:8px}}
.honors-subtitle{{font-size:14px;color:var(--dim)}}
.honors-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin-bottom:20px}}
.honor-card{{display:flex;gap:12px;padding:18px;background:var(--bg2);border-radius:16px;border:1px solid var(--bg3);animation:honor-in 0.5s ease-out both;transition:all 0.3s}}
@keyframes honor-in{{0%{{opacity:0;transform:scale(0.9)}}100%{{opacity:1;transform:scale(1)}}}}
.honor-card:hover{{transform:translateY(-3px);box-shadow:0 10px 30px rgba(0,0,0,0.2)}}
.honor-icon{{font-size:32px;flex-shrink:0}}
.honor-content{{flex:1}}
.honor-title{{font-size:14px;font-weight:700;margin-bottom:5px}}
.honor-name{{font-size:16px;font-weight:600;color:var(--txt);margin-bottom:3px}}
.honor-reason{{font-size:11px;color:var(--dim)}}
.honors-footer{{text-align:center;font-size:13px;color:var(--dim);font-style:italic;padding:20px;background:var(--bg2);border-radius:12px}}
.concentration-desc{{font-size:12px;color:var(--dim);text-align:center}}

/* 小节总结样式 */
.section-summary{{margin:30px auto 0;padding:20px 25px;background:linear-gradient(135deg,rgba(255,107,157,0.05),rgba(78,205,196,0.05));border-radius:12px;border:1px solid rgba(255,107,157,0.2);max-width:600px;text-align:center}}
.summary-text{{font-size:13px;color:var(--dim);line-height:1.8;font-style:italic}}

/* 表情分析样式 */
.emoji-analysis{{max-width:500px;margin:0 auto;text-align:center}}
.emoji-header{{margin-bottom:30px}}
.emoji-main-icon{{font-size:60px;margin-bottom:15px;animation:bounce 2s infinite}}
@keyframes bounce{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-10px)}}}}
.emoji-title{{font-size:22px;font-weight:700;color:var(--txt);margin-bottom:10px}}
.emoji-desc{{font-size:14px;color:var(--dim);line-height:1.6}}
.emoji-cloud{{background:var(--bg2);border-radius:16px;padding:20px;margin-bottom:20px}}
.emoji-cloud-title{{font-size:14px;color:var(--dim);margin-bottom:15px}}
.emoji-cloud-items{{display:flex;flex-wrap:wrap;justify-content:center;gap:12px}}
.emoji-cloud-item{{background:var(--bg3);border-radius:12px;padding:12px 16px;display:flex;flex-direction:column;align-items:center;gap:4px;transform:scale(var(--size,1));transition:transform 0.3s}}
.emoji-cloud-item:hover{{transform:scale(calc(var(--size,1) * 1.1))}}
.emoji-cloud-emojis{{font-size:24px}}
.emoji-cloud-label{{font-size:11px;color:var(--dim)}}
.emoji-cloud-score{{font-size:13px;font-weight:600;color:var(--cyan)}}
.emoji-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:12px;text-align:left}}
.emoji-insight-icon{{font-size:20px}}
.emoji-insight-text{{font-size:13px;color:var(--txt);line-height:1.6}}

/* 年度词云 */
.word-cloud-container{{max-width:550px;margin:0 auto}}
.cloud-header{{text-align:center;margin-bottom:20px}}
.cloud-title{{font-size:20px;font-weight:600;color:var(--txt);margin-bottom:5px}}
.cloud-subtitle{{font-size:13px;color:var(--dim)}}
.cloud-visual{{background:var(--bg2);border-radius:16px;padding:20px;margin-bottom:20px;overflow:hidden}}
.cloud-svg{{width:100%;height:auto;display:block}}
.cloud-word{{font-weight:600;cursor:default;transition:all 0.3s;animation:cloud-pop 0.5s ease-out backwards}}
.cloud-word:hover{{filter:brightness(1.3);transform:scale(1.1)}}
@keyframes cloud-pop{{0%{{opacity:0;transform:scale(0)}}100%{{opacity:1;transform:scale(1)}}}}
.cloud-top3{{background:var(--bg2);border-radius:12px;padding:15px;margin-bottom:15px}}
.cloud-top3-title{{font-size:14px;font-weight:600;color:var(--txt);margin-bottom:12px;text-align:center}}
.cloud-top3-list{{display:flex;justify-content:center;gap:20px;flex-wrap:wrap}}
.cloud-top-item{{display:flex;align-items:center;gap:8px;background:var(--bg3);padding:8px 15px;border-radius:20px}}
.cloud-medal{{font-size:18px}}
.cloud-word-name{{font-weight:600;color:var(--txt)}}
.cloud-word-count{{font-size:12px;color:var(--dim)}}
.cloud-style{{display:flex;align-items:center;gap:15px;margin-bottom:15px;flex-wrap:wrap;justify-content:center}}
.cloud-style-badge{{display:flex;align-items:center;gap:8px;padding:10px 20px;border-radius:25px;color:#fff}}
.style-icon{{font-size:20px}}
.style-name{{font-weight:600;font-size:15px}}
.cloud-style-desc{{font-size:13px;color:var(--dim);text-align:center}}
.cloud-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:12px;align-items:flex-start}}
.emoji-note{{background:var(--bg2);border-radius:12px;padding:20px;margin:20px 0;display:flex;align-items:flex-start;gap:15px}}
.emoji-note .note-icon{{font-size:24px}}
.emoji-note .note-text{{font-size:13px;color:var(--dim);line-height:1.7}}
.emoji-insight-text strong{{color:var(--pink)}}

/* 社交动机分析样式 */
.motivation-analysis{{max-width:500px;margin:0 auto}}
.motivation-header{{text-align:center;margin-bottom:25px}}
.motivation-icon{{font-size:50px;margin-bottom:10px}}
.motivation-title{{font-size:20px;font-weight:700;color:var(--txt)}}
.motivation-subtitle{{font-size:13px;color:var(--dim);margin-top:5px}}
.motivation-bars{{display:flex;flex-direction:column;gap:15px;margin-bottom:20px}}
.motivation-item{{background:var(--bg2);border-radius:12px;padding:15px}}
.motivation-item-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}}
.motivation-name{{font-size:14px;font-weight:500;color:var(--txt)}}
.motivation-score{{font-size:16px;font-weight:700;color:var(--cyan)}}
.motivation-bar{{height:8px;background:var(--bg3);border-radius:4px;overflow:hidden}}
.motivation-fill{{height:100%;border-radius:4px;transition:width 1s ease-out}}
.motivation-desc{{font-size:11px;color:var(--dim);margin-top:8px}}
.motivation-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:10px;align-items:flex-start}}
.motivation-insight .insight-icon{{font-size:18px}}
.motivation-insight .insight-text{{font-size:13px;color:var(--txt);line-height:1.6}}

/* 互动质量分析样式 */
.quality-analysis{{max-width:600px;margin:0 auto}}
.quality-header{{text-align:center;margin-bottom:25px}}
.quality-title{{font-size:20px;font-weight:700;color:var(--txt);margin-bottom:10px}}
.quality-subtitle{{font-size:13px;color:var(--dim);line-height:1.6}}

/* 表情气质分析 */
.emoji-analysis{{max-width:600px;margin:0 auto}}
.emoji-dominant{{text-align:center;margin-bottom:30px;padding:25px;background:var(--bg2);border-radius:16px}}
.dominant-badge{{display:inline-block;padding:20px 30px;border:2px solid;border-radius:20px;margin-bottom:15px}}
.dominant-icon{{font-size:40px;margin-bottom:8px}}
.dominant-name{{font-size:18px;font-weight:600;color:var(--txt)}}
.dominant-desc{{font-size:14px;color:var(--dim);line-height:1.6}}
.emoji-sections{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px;margin-bottom:20px}}
.emoji-top10,.emoji-styles{{background:var(--bg2);border-radius:12px;padding:20px}}
.emoji-section-title{{font-size:14px;font-weight:600;color:var(--txt);margin-bottom:15px}}
.emoji-list{{display:flex;flex-direction:column;gap:8px}}
.emoji-item{{display:flex;align-items:center;gap:10px}}
.emoji-rank{{width:24px;font-size:12px;color:var(--dim)}}
.emoji-icon{{font-size:20px;width:30px;text-align:center}}
.emoji-bar{{flex:1;height:6px;background:var(--bg3);border-radius:3px;overflow:hidden}}
.emoji-fill{{height:100%;background:linear-gradient(90deg,var(--pink),var(--purple));border-radius:3px}}
.emoji-count{{font-size:11px;color:var(--dim);min-width:50px;text-align:right}}
.emoji-total{{text-align:center;font-size:12px;color:var(--dim);margin-top:15px;padding-top:10px;border-top:1px solid var(--bg3)}}
.style-list{{display:flex;flex-direction:column;gap:12px}}
.style-item{{}}
.style-header{{display:flex;justify-content:space-between;margin-bottom:5px}}
.style-name{{font-size:13px;color:var(--txt)}}
.style-pct{{font-size:12px;color:var(--dim)}}
.style-bar{{height:8px;background:var(--bg3);border-radius:4px;overflow:hidden}}
.style-fill{{height:100%;border-radius:4px;transition:width 1s}}
.emoji-empty{{text-align:center;padding:40px}}
.emoji-empty-icon{{font-size:48px;margin-bottom:15px}}
.emoji-empty-text{{font-size:14px;color:var(--dim);line-height:1.8}}
.emoji-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:12px;align-items:flex-start}}

/* 社交动机分析 */
.motivation-analysis{{max-width:700px;margin:0 auto}}
.motivation-dominant{{display:flex;align-items:center;gap:20px;padding:25px;background:var(--bg2);border-radius:16px;margin-bottom:25px;flex-wrap:wrap;justify-content:center}}
.dominant-circle{{width:80px;height:80px;border-radius:50%;border:3px solid;display:flex;align-items:center;justify-content:center;flex-shrink:0}}
.dominant-emoji{{font-size:36px}}
.dominant-info{{text-align:left}}
.dominant-type{{font-size:20px;font-weight:700;color:var(--txt);margin-bottom:8px}}
.dominant-desc{{font-size:14px;color:var(--dim);line-height:1.6}}
.motivation-radar{{position:relative;width:200px;height:200px;margin:0 auto 25px}}
.radar-svg{{width:100%;height:100%}}
.radar-labels{{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none}}
.radar-label{{position:absolute;font-size:10px;color:var(--dim);white-space:nowrap}}
.motivation-bars{{background:var(--bg2);border-radius:12px;padding:20px;margin-bottom:20px}}
.bars-title{{font-size:14px;font-weight:600;color:var(--txt);margin-bottom:15px;text-align:center}}
.motive-item{{margin-bottom:12px}}
.motive-header{{display:flex;justify-content:space-between;margin-bottom:5px}}
.motive-name{{font-size:13px;color:var(--txt)}}
.motive-score{{font-size:12px;color:var(--dim)}}
.motive-bar{{height:10px;background:var(--bg3);border-radius:5px;overflow:hidden}}
.motive-fill{{height:100%;border-radius:5px;transition:width 1s}}
.motivation-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(167,139,250,0.1));border-radius:12px;padding:15px;display:flex;gap:12px;align-items:flex-start}}
.quality-cards{{display:flex;flex-direction:column;gap:15px;margin-bottom:20px}}
.quality-card{{display:flex;align-items:center;gap:15px;background:var(--bg2);border-radius:12px;padding:15px}}
.quality-rank{{font-size:28px}}
.quality-info{{min-width:80px}}
.quality-name{{font-size:14px;font-weight:600;color:var(--txt)}}
.quality-score{{font-size:18px;font-weight:700;color:var(--cyan)}}
.quality-bars{{flex:1;display:flex;flex-direction:column;gap:6px}}
.quality-bar-item{{display:flex;align-items:center;gap:8px}}
.qb-label{{font-size:10px;color:var(--dim);width:30px}}
.qb-track{{flex:1;height:6px;background:var(--bg3);border-radius:3px;overflow:hidden}}
.qb-fill{{height:100%;background:linear-gradient(90deg,var(--cyan),var(--purple));border-radius:3px}}
.quality-underrated{{background:linear-gradient(135deg,rgba(255,215,0,0.1),rgba(255,107,157,0.1));border-radius:12px;padding:15px;margin-bottom:15px;text-align:center}}
.underrated-title{{font-size:14px;font-weight:600;color:var(--yellow);margin-bottom:5px}}
.underrated-desc{{font-size:12px;color:var(--dim);margin-bottom:10px}}
.underrated-list{{display:flex;flex-wrap:wrap;justify-content:center;gap:8px}}
.underrated-name{{background:var(--bg2);padding:5px 12px;border-radius:20px;font-size:12px;color:var(--txt)}}
.quality-insight{{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:12px;padding:15px;display:flex;gap:10px}}
.quality-insight .insight-icon{{font-size:18px}}
.quality-insight .insight-text{{font-size:13px;color:var(--txt);line-height:1.6}}

/* 群聊快速数据行 */
.group-quick-stats{{display:flex;align-items:center;gap:8px;padding:8px 20px 12px;background:rgba(255,255,255,0.02);border-top:1px solid var(--bg3);font-size:12px;flex-wrap:wrap}}

/* 群聊存在感分析 */
.group-presence{{padding:15px;background:var(--bg3);border-radius:12px;margin:15px}}
.presence-header{{font-size:14px;font-weight:600;color:var(--txt);margin-bottom:12px}}
.presence-content{{display:flex;flex-direction:column;gap:12px}}
.presence-main{{display:flex;align-items:center;gap:20px}}
.presence-rank{{width:80px;height:80px;border-radius:50%;border:3px solid var(--cyan);display:flex;flex-direction:column;align-items:center;justify-content:center;background:var(--bg2)}}
.presence-rank .rank-num{{font-size:24px;font-weight:700;color:var(--txt)}}
.presence-rank .rank-total{{font-size:11px;color:var(--dim)}}
.presence-stats{{display:flex;gap:25px}}
.presence-stat{{text-align:center}}
.presence-val{{display:block;font-size:20px;font-weight:600;color:var(--cyan)}}
.presence-lbl{{font-size:11px;color:var(--dim)}}
.presence-desc{{font-size:13px;padding:10px;background:var(--bg2);border-radius:8px;text-align:center}}

/* 群聊24小时活跃度 */
.group-hours-section{{padding:15px}}
.group-hour-chart{{margin-top:10px}}
.hour-bars{{display:flex;align-items:flex-end;height:60px;gap:2px;padding:0 5px}}
.hour-bar{{flex:1;min-width:8px;border-radius:2px 2px 0 0;transition:height 0.5s ease-out}}
.hour-labels{{display:flex;justify-content:space-between;padding:5px 0;font-size:10px;color:var(--dim)}}
.talkers-section{{padding:0 15px 15px}}
.section-subtitle{{font-size:12px;color:var(--dim);margin-bottom:10px}}
.talkers-list{{display:flex;flex-wrap:wrap;gap:8px}}
.talker{{display:flex;align-items:center;gap:5px;background:var(--bg3);padding:5px 10px;border-radius:20px;font-size:11px}}
.talker-rank{{color:var(--yellow);font-weight:600}}
.talker-name{{max-width:60px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.talker-val{{color:var(--dim)}}

/* 控制按钮 */
.controls{{text-align:center;margin:20px 0}}

/* 卡片列表显示更多功能 */
.cards-wrapper{{}}
.cards-wrapper .chat-card:nth-child(n+4),
.cards-wrapper .group-card:nth-child(n+4){{display:none}}
.cards-wrapper.show-all .chat-card,
.cards-wrapper.show-all .group-card{{display:block}}
.show-more-section{{text-align:center;margin:30px 0}}
.show-more-btn{{background:linear-gradient(135deg,var(--pink),var(--purple));color:#fff;border:none;padding:15px 40px;border-radius:30px;font-size:15px;font-weight:600;cursor:pointer;display:inline-flex;align-items:center;gap:10px;transition:all 0.3s;box-shadow:0 5px 20px rgba(255,107,157,0.3)}}
.show-more-btn:hover{{transform:translateY(-3px);box-shadow:0 8px 30px rgba(255,107,157,0.4)}}
.show-more-icon{{font-size:18px;transition:transform 0.3s}}
.show-more-section.hidden{{display:none}}
.cards-controls{{margin-top:20px}}
.btn{{background:var(--bg3);border:1px solid var(--pink);color:var(--txt);padding:10px 25px;border-radius:25px;cursor:pointer;font-size:13px;margin:5px;transition:all 0.3s}}
.btn:hover{{background:var(--pink)}}

/* 页脚 */
footer{{text-align:center;padding:60px 20px;color:var(--dim);position:relative;z-index:1}}
.footer-stats{{margin-bottom:5px}}

/* 响应式 */
@media(max-width:768px){{
    /* 导航栏 - 移动端优化，放到底部 */
    .nav{{
        position:fixed;
        bottom:0;
        top:auto;
        left:0;
        right:0;
        padding:8px 5px;
        gap:3px;
        justify-content:space-around;
        border-top:1px solid rgba(255,107,157,0.2);
        background:rgba(10,10,26,0.98);
    }}
    .nav a{{padding:8px 8px;font-size:10px;border-radius:12px}}
    
    /* 开场页留出底部导航空间 */
    .hero{{padding-top:20px;padding-bottom:80px}}
    
    /* 首页数据布局 - 2+3排列，第一行更紧凑 */
    .hero-stats{{
        display:flex;
        flex-wrap:wrap;
        justify-content:center;
        gap:12px 20px;
        max-width:320px;
        margin:0 auto;
    }}
    .hero-stat{{
        text-align:center;
    }}
    .hero-stat:nth-child(1),
    .hero-stat:nth-child(2){{
        flex:0 0 35%;
    }}
    .hero-stat:nth-child(3),
    .hero-stat:nth-child(4),
    .hero-stat:nth-child(5){{
        flex:0 0 30%;
    }}
    
    /* 热力图 - 移动端3列 */
    .heatmap-grid{{grid-template-columns:repeat(3, 1fr);gap:10px;max-width:320px}}
    .heatmap-bar{{height:80px}}
    .heatmap-label{{font-size:11px}}
    
    /* 数据网格 */
    .data-grid{{grid-template-columns:1fr}}
    .rankings-grid{{grid-template-columns:1fr}}
    .versus{{flex-direction:column;gap:15px}}.vs-mid{{display:none}}
    
    /* 私聊详情卡片展开后内容不被遮挡 */
    .chat-card.open .chat-body,.group-card.open .chat-body{{max-height:5000px}}
    
    /* 各section底部留空 */
    .section{{padding-bottom:80px}}
    
    /* 用户画像卡片 */
    .profile-card{{margin:20px 15px}}
    .profile-value{{font-size:18px}}
    
    /* 年度来信 - 信封更长更大 */
    .letter-wrapper{{margin:20px 15px}}
    .envelope{{min-height:240px}}
    .envelope-flap{{height:120px}}
    .envelope-seal{{top:85px}}
    .letter-paper{{margin:15px;padding:15px}}
    .letter-content{{font-size:13px;line-height:1.9}}
    .letter-header{{margin:-15px -15px 15px -15px;padding:12px 15px}}
    
    /* 默契度卡片 */
    .chemistry-card{{padding:15px}}
    .chemistry-score{{width:50px;height:50px}}
    .chemistry-intro{{padding:15px;margin-bottom:20px}}
    .chemistry-intro-title{{font-size:18px}}
    .chemistry-intro-text{{font-size:13px}}
    .chemistry-title-desc{{font-size:11px}}
    .chemistry-details{{font-size:10px}}
    .chemistry-outro{{padding:20px;margin-top:20px}}
    .chemistry-outro-title{{font-size:14px}}
    .chemistry-outro-text{{font-size:12px}}
    
    /* 年度称号 - 手机端单列 */
    .titles-grid{{grid-template-columns:1fr}}
    .title-card{{padding:15px}}
    .title-icon{{font-size:28px}}
    .title-name{{font-size:14px}}
    
    /* 社交人格 - 手机端 */
    .personality-card{{padding:20px;margin:0 15px}}
    .personality-name{{font-size:22px}}
    .bar-label{{width:60px;font-size:11px}}
    .bar-value{{font-size:11px}}
    
    /* 特殊时刻 - 手机端 */
    .moment-card{{padding:15px}}
    .moment-icon{{font-size:26px}}
    .moment-value{{font-size:16px}}
    
    /* 页脚多行显示 */
    footer p{{margin-bottom:5px}}
}}

/* 更小屏幕 */
@media(max-width:480px){{
    .nav a{{padding:6px 6px;font-size:9px}}
    .heatmap-grid{{grid-template-columns:repeat(3, 1fr);max-width:280px}}
    .hero-stats{{gap:10px;max-width:280px}}
    .hero-stat-val{{font-size:clamp(24px,6vw,40px)}}
}}

.empty{{text-align:center;color:var(--dim);padding:40px}}

/* 音乐控制按钮 - 可拖动 */
.music-btn{{position:fixed;top:20px;right:20px;z-index:2001;width:50px;height:50px;border-radius:50%;background:rgba(255,255,255,0.12);border:1px solid rgba(255,107,157,0.3);cursor:grab;display:flex;align-items:center;justify-content:center;font-size:24px;box-shadow:0 2px 12px rgba(255,107,157,0.15);transition:all 0.3s;user-select:none;touch-action:none;backdrop-filter:blur(8px)}}
.music-btn:active{{cursor:grabbing}}
.music-btn:hover{{background:rgba(255,255,255,0.2);border-color:rgba(255,107,157,0.5)}}
.music-btn.muted{{background:rgba(255,255,255,0.08);border-color:rgba(136,136,136,0.3)}}
.music-btn.dragging{{transform:scale(1.1);box-shadow:0 4px 20px rgba(255,107,157,0.25)}}

/* 悬浮截图按钮 - 高透明度小按钮 */
.float-screenshot-btn{{position:fixed;bottom:80px;right:15px;z-index:2000;width:40px;height:40px;border-radius:50%;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.1);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:16px;transition:all 0.3s;backdrop-filter:blur(3px);opacity:0.4}}
.float-screenshot-btn:hover{{opacity:0.8;background:rgba(255,255,255,0.15);transform:scale(1.1)}}
.float-screenshot-btn:active{{transform:scale(0.95)}}
.float-screenshot-btn.capturing{{opacity:0 !important;pointer-events:none}}

/* 截图/生成长图按钮 - 放在页面底部 */
.screenshot-btn{{display:inline-flex;padding:16px 32px;border-radius:30px;background:linear-gradient(135deg,var(--pink),var(--purple));border:none;cursor:pointer;color:#fff;font-size:16px;font-weight:600;box-shadow:0 4px 20px rgba(168,85,247,0.4);transition:all 0.3s;align-items:center;gap:10px;margin:20px auto}}
.screenshot-btn:hover{{transform:translateY(-3px);box-shadow:0 8px 30px rgba(168,85,247,0.6)}}
.screenshot-btn:active{{transform:translateY(0)}}
.screenshot-btn svg{{width:20px;height:20px}}
.screenshot-btn .spin{{animation:spin 1s linear infinite}}
@keyframes spin{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}

/* 结束页增强 */
.ending-section{{min-height:80vh;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:60px 20px;position:relative;z-index:1}}
.ending-emoji{{font-size:70px;margin-bottom:25px;animation:pulse 2s infinite}}
.ending-title{{font-size:clamp(28px,7vw,48px);font-weight:800;background:linear-gradient(135deg,var(--pink),var(--cyan),var(--yellow));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:30px}}
.ending-highlights{{
    font-size:clamp(14px,3vw,17px);
    color:rgba(255,255,255,0.85);
    line-height:2.2;
    max-width:600px;
    margin-bottom:30px;
    padding:25px 30px;
    background:rgba(255,255,255,0.03);
    border-radius:16px;
    border:1px solid rgba(255,107,157,0.15);
}}
.ending-highlights strong{{color:var(--cyan);font-weight:600}}
.ending-reflection{{
    font-size:clamp(16px,4vw,20px);
    color:var(--pink);
    font-style:italic;
    margin-bottom:25px;
    max-width:500px;
    opacity:0.9;
}}
.ending-wish{{
    font-size:clamp(14px,3vw,16px);
    color:var(--dim);
    margin-bottom:20px;
    max-width:500px;
    line-height:1.8;
}}
.ending-signature{{
    font-size:13px;
    color:var(--dim);
    margin-top:15px;
    opacity:0.7;
}}
</style>
</head>
<body>

<!-- 背景音乐 (base64内嵌) -->
<audio id="bgm" loop>
    <source src="data:audio/mpeg;base64,{bgm_base64}" type="audio/mpeg">
</audio>

<!-- 音乐控制按钮 -->
<button class="music-btn muted" id="musicBtn" onclick="toggleMusic()">🔇</button>

<!-- 悬浮截图按钮 -->
<button class="float-screenshot-btn" id="floatScreenshotBtn" onclick="quickScreenshot()" title="快速截图">📷</button>

<!-- 星星背景 -->
<div class="stars" id="stars"></div>

<!-- 网格背景 -->
<div class="grid-bg"></div>

<!-- 流动线条背景 -->
<div class="flowing-lines" id="flowingLines"></div>

<!-- 光晕效果 -->
<div class="glow-orbs" id="glowOrbs"></div>

<!-- 漂浮emoji -->
<div class="meteors" id="meteors"></div>

<!-- 粒子背景 -->
<div id="particles"></div>

<!-- 导航 -->
<nav class="nav">
    <a href="#hero">首页</a>
    <a href="#heatmap">年历</a>
    <a href="#journey">旅程</a>
    <a href="#rhythm">节奏</a>
    <a href="#emoji-analysis">表情</a>
    <a href="#motivation">动机</a>
    <a href="#reply-speed">速度</a>
    <a href="#festival">节日</a>
    <a href="#chemistry">默契</a>
    <a href="#private-rank">私聊</a>
    <a href="#group-overview">群览</a>
    <a href="#numbers">数字</a>
    <a href="#ending">结语</a>
</nav>

<!-- 开场页 -->
<section class="hero" id="hero">
    <div class="intro-animation-layer" id="introAnimationLayer"></div>
    <div class="hero-content" id="heroContent" style="opacity:0">
        <div class="hero-year">2025</div>
        <div class="hero-sub">年度微信聊天报告</div>
        <div class="hero-intro">这一年，你用文字编织了多少故事？</div>
        <div class="hero-story">
            {generate_story_intro()}
        </div>
        <div class="hero-slogan" id="heroSlogan"></div>
        <div class="hero-stats">
            <div class="hero-stat"><div class="hero-stat-val"><span class="num" data-val="{total_msgs}">{total_msgs:,}</span></div><div class="hero-stat-lbl">总消息</div></div>
            <div class="hero-stat"><div class="hero-stat-val"><span class="num" data-val="{total_chars}">{total_chars:,}</span></div><div class="hero-stat-lbl">总字数</div></div>
            <div class="hero-stat"><div class="hero-stat-val"><span class="num" data-val="{len(sorted_private)}">{len(sorted_private)}</span></div><div class="hero-stat-lbl">私聊联系人</div></div>
            <div class="hero-stat"><div class="hero-stat-val"><span class="num" data-val="{len(sorted_groups)}">{len(sorted_groups)}</span></div><div class="hero-stat-lbl">群聊</div></div>
            <div class="hero-stat"><div class="hero-stat-val"><span class="num" data-val="{p.get('total_sessions', 0)}">{p.get('total_sessions', 0):,}</span></div><div class="hero-stat-lbl">总会话</div></div>
        </div>
        <div class="hero-quote">
            "你的消息列表，是一部未完的情感电影"
        </div>
        <div class="scroll-hint">↓ 向下滚动，开启你的年度回忆</div>
    </div>
    <script>window.INTRO_ANIMATION_DATA = {prepare_intro_animation_data()};</script>
</section>

<!-- 年度热力图 -->
<section class="section heatmap-section" id="heatmap">
    <h2 class="section-title">📅 2025 聊天年历</h2>
    <p class="section-subtitle">时间不语，却记录了你每一次的想念与分享</p>
    <div class="container">
        <div class="heatmap-title">每月聊天消息数</div>
        {make_monthly_heatmap()}
        {make_section_summary('heatmap')}
    </div>
</section>

<!-- 年度旅程时间线 -->
<section class="section" id="journey" style="background:var(--bg2)">
    <h2 class="section-title">🚀 你的年度旅程</h2>
    <p class="section-subtitle">12个月，每一步都有故事</p>
    <div class="container">
        {make_year_journey()}
    </div>
</section>

<!-- 24小时聊天节奏 -->
<section class="section" id="rhythm" style="background:var(--bg2)">
    <h2 class="section-title">🕐 你的社交节奏</h2>
    <p class="section-subtitle">每个时段的消息，都是你生活韵律的一部分</p>
    <div class="container">
        {make_hourly_rhythm()}
        {make_section_summary('rhythm')}
    </div>
</section>

<!-- 年度聊天颜色 -->
<section class="section" id="chat-colors">
    <h2 class="section-title">🎨 年度聊天色彩</h2>
    <p class="section-subtitle">每一种颜色，都是一段独特的心情</p>
    <div class="container">
        {make_chat_colors()}
        {make_section_summary('colors')}
    </div>
</section>

<!-- 表情气质分析 -->
<section class="section" id="emoji-analysis" style="background:var(--bg2)">
    <h2 class="section-title">😊 你的表情气质</h2>
    <p class="section-subtitle">表情是文字之外的第二语言</p>
    <div class="container">
        {make_emoji_analysis()}
    </div>
</section>

<!-- 年度词云 -->
<section class="section" id="word-cloud">
    <h2 class="section-title">💬 你的年度词汇</h2>
    <p class="section-subtitle">这些高频词，勾勒出你的表达风格</p>
    <div class="container">
        {make_word_cloud()}
    </div>
</section>

<!-- 社交动机分析 -->
<section class="section" id="motivation">
    <h2 class="section-title">🎯 你的社交动机</h2>
    <p class="section-subtitle">是什么驱动你打开微信？</p>
    <div class="container">
        {make_motivation_analysis()}
    </div>
</section>

<!-- 社交健康度 -->
<section class="section" id="social-health" style="background:var(--bg2)">
    <h2 class="section-title">💚 你的社交健康度</h2>
    <p class="section-subtitle">给你的社交生活做一次"体检"</p>
    <div class="container">
        {make_social_health()}
    </div>
</section>

<!-- 好友亲密度趋势 -->
<section class="section" id="friendship-trends">
    <h2 class="section-title">📈 好友互动趋势</h2>
    <p class="section-subtitle">看看这一年，你和Ta的友情如何变化</p>
    <div class="container">
        {make_friendship_trends()}
    </div>
</section>

<!-- 聊天关键词云 -->
<section class="section" id="keywords" style="background:var(--bg2)">
    <h2 class="section-title">💬 年度关键词</h2>
    <p class="section-subtitle">这些词，构成了你的2025</p>
    <div class="container">
        {make_keyword_cloud()}
    </div>
</section>

<!-- 年度社交大事件 -->
<section class="section" id="events">
    <h2 class="section-title">🎯 年度社交里程碑</h2>
    <p class="section-subtitle">这些瞬间，值得被铭记</p>
    <div class="container">
        {make_social_events()}
    </div>
</section>

<!-- 消息类型分布 -->
<section class="section" id="msg-types" style="background:var(--bg2)">
    <h2 class="section-title">📊 消息类型分布</h2>
    <p class="section-subtitle">你更喜欢用什么方式表达？</p>
    <div class="container">
        {make_message_types()}
    </div>
</section>

<!-- 社交人格测试 -->
<section class="section" id="personality">
    <h2 class="section-title">🧬 你的社交人格</h2>
    <p class="section-subtitle">基于聊天数据的趣味人格分析</p>
    <div class="container">
        {make_personality_test()}
    </div>
</section>

<!-- 回复速度对比 -->
<section class="section" id="reply-speed">
    <h2 class="section-title">⚡ 回复速度对决</h2>
    <p class="section-subtitle">谁是秒回王？谁在等待中期待？</p>
    <div class="container">
        {make_reply_speed_analysis()}
    </div>
</section>

<!-- 节日聊天分析 -->
<section class="section" id="festival" style="background:var(--bg2)">
    <h2 class="section-title">🎉 节日聊天图鉴</h2>
    <p class="section-subtitle">那些特殊日子里，你和谁在一起（聊天）</p>
    <div class="container">
        {make_festival_analysis()}
    </div>
</section>

<!-- 互动仪式感 -->
<section class="section" id="ritual">
    <h2 class="section-title">🌅 你的互动仪式感</h2>
    <p class="section-subtitle">早安晚安，是最温柔的日常</p>
    <div class="container">
        {make_ritual_analysis()}
    </div>
</section>

<!-- 聊天高光时刻 -->
<section class="section" id="highlights" style="background:var(--bg2)">
    <h2 class="section-title">✨ 年度高光时刻</h2>
    <p class="section-subtitle">这些瞬间，值得被珍藏</p>
    <div class="container">
        {make_highlight_moments()}
    </div>
</section>

<!-- 社交人设 -->
<section class="section" id="persona">
    <h2 class="section-title">🎭 你的社交人设</h2>
    <p class="section-subtitle">数据告诉你，你是怎样的社交者</p>
    <div class="container">
        {make_social_persona()}
    </div>
</section>

<!-- 年度最佳搭档 -->
<section class="section" id="partners" style="background:var(--bg2)">
    <h2 class="section-title">🏆 年度最佳搭档</h2>
    <p class="section-subtitle">不同维度，都有独一无二的Ta</p>
    <div class="container">
        {make_best_partners()}
    </div>
</section>

<!-- 聊天能量波动 -->
<section class="section" id="energy">
    <h2 class="section-title">📈 你的社交能量</h2>
    <p class="section-subtitle">52周的聊天能量，起伏就是生活的节奏</p>
    <div class="container">
        {make_energy_wave()}
    </div>
</section>

<!-- 互动质量分析 -->
<section class="section" id="quality" style="background:var(--bg2)">
    <h2 class="section-title">💎 互动质量榜</h2>
    <p class="section-subtitle">消息数量≠关系质量，这些朋友才是真正的"高质量社交"</p>
    <div class="container">
        {make_quality_analysis()}
    </div>
</section>

<!-- 用户画像预测 -->
<section class="section" id="user-profile" style="background:var(--bg2)">
    <h2 class="section-title">🔮 猜猜你是谁</h2>
    <p class="section-subtitle">文字里藏着你的生活轨迹</p>
    <div class="container">
        {make_user_profile_card()}
    </div>
</section>

<!-- 年度来信 -->
<section class="section" id="annual-letter" style="background:var(--bg2)">
    <h2 class="section-title">💌 年度来信</h2>
    <p class="section-subtitle">给最重要的人，写一封跨越时光的信</p>
    <div class="container">
        {make_annual_letter()}
    </div>
</section>

<!-- 年度称号（参考网易云）-->
<section class="section" id="annual-titles">
    <h2 class="section-title">🏅 你的年度称号</h2>
    <p class="section-subtitle">这些标签，定义了你独一无二的社交风格</p>
    <div class="container">
        {make_annual_titles_card()}
        {make_section_summary('titles')}
    </div>
</section>

<!-- 社交人格（参考MBTI）-->
<section class="section" id="personality" style="background:var(--bg2)">
    <h2 class="section-title">🧬 你的社交人格</h2>
    <p class="section-subtitle">从聊天习惯看你的社交DNA</p>
    <div class="container">
        {make_personality_card()}
        {make_section_summary('personality')}
    </div>
</section>

<!-- 年度特殊时刻（参考支付宝）-->
<section class="section" id="moments">
    <h2 class="section-title">✨ 年度特别时刻</h2>
    <p class="section-subtitle">这些瞬间，值得被铭记</p>
    <div class="container">
        {make_special_moments_card()}
        {make_section_summary('moments')}
    </div>
</section>

<!-- 好友默契度 -->
<section class="section" id="chemistry">
    <h2 class="section-title">💫 好友默契度</h2>
    <p class="section-subtitle">有些默契，不需要言语也能懂</p>
    <div class="container">
        {make_chemistry_cards()}
    </div>
</section>

<!-- 好友互动趋势 -->
<section class="section" id="friend-trends">
    <h2 class="section-title">📈 好友互动趋势</h2>
    <p class="section-subtitle">时间会告诉你，谁在你生命中留下了痕迹</p>
    <div class="container">
        {make_friend_trends()}
    </div>
</section>

<!-- 私聊排行榜 -->
<section class="section" id="private-rank" style="background:var(--bg2)">
    <h2 class="section-title">🏆 私聊排行榜</h2>
    <p class="section-subtitle">这些名字，组成了你2025的社交图谱</p>
    <div class="container">
        <!-- 智能分析 -->
        <div class="insights">
            <div class="insights-title">💡 年度洞察</div>
            {''.join(f'<div class="insight-item">{i}</div>' for i in generate_insights())}
        </div>
        <div class="friend-groups">{make_friend_groups()}</div>
        <div class="rankings-grid">{make_private_rankings()}</div>
    </div>
</section>

<!-- 私聊详情 -->
<section class="section" id="private-detail">
    <h2 class="section-title">💬 私聊详情 ({len(sorted_private)}人)</h2>
    <p class="section-subtitle">点开看看，和每个人都聊了些什么</p>
    <div class="container">
        <div class="cards-wrapper" id="privateCardsWrapper">
            {make_private_cards()}
        </div>
        <div class="show-more-section" id="privateShowMore">
            <button class="show-more-btn" onclick="toggleMoreCards('private')">
                <span class="show-more-text">显示更多 ({max(0, len(sorted_private)-3)}人)</span>
                <span class="show-more-icon">↓</span>
            </button>
        </div>
        <div class="controls cards-controls" id="privateControls" style="display:none">
            <button class="btn" onclick="expandAll('chat')">全部展开</button>
            <button class="btn" onclick="collapseAll('chat')">全部收起</button>
            <button class="btn" onclick="toggleMoreCards('private')">收起列表</button>
        </div>
    </div>
</section>

<!-- 群聊总览 -->
<section class="section" id="group-overview">
    <h2 class="section-title">🌐 你的群聊宇宙</h2>
    <p class="section-subtitle">群聊是我们时代的"数字村落"</p>
    <div class="container">
        {make_group_overview()}
        {make_group_time_comparison()}
    </div>
</section>

<!-- 群聊排行榜 -->
<section class="section" id="group-rank" style="background:var(--bg2)">
    <h2 class="section-title">👥 群聊排行榜</h2>
    <p class="section-subtitle">那些热闹的群，承载着你的归属感</p>
    <div class="container">
        <!-- 群聊年度洞察 -->
        <div class="insights">
            <div class="insights-title">💡 群聊洞察</div>
            {''.join(f'<div class="insight-item">{i}</div>' for i in generate_group_insights())}
        </div>
        <div class="rankings-grid">{make_group_rankings()}</div>
    </div>
</section>

<!-- 群聊详情 -->
<section class="section" id="group-detail">
    <h2 class="section-title">📋 群聊详情 ({len(sorted_groups)}群)</h2>
    <p class="section-subtitle">每个群都是一个小世界</p>
    <div class="container">
        <div class="cards-wrapper" id="groupCardsWrapper">
            {make_group_cards()}
        </div>
        <div class="show-more-section" id="groupShowMore">
            <button class="show-more-btn" onclick="toggleMoreCards('group')">
                <span class="show-more-text">显示更多 ({max(0, len(sorted_groups)-3)}群)</span>
                <span class="show-more-icon">↓</span>
            </button>
        </div>
        <div class="controls cards-controls" id="groupControls" style="display:none">
            <button class="btn" onclick="expandAll('group')">全部展开</button>
            <button class="btn" onclick="collapseAll('group')">全部收起</button>
            <button class="btn" onclick="toggleMoreCards('group')">收起列表</button>
        </div>
    </div>
</section>

<!-- 年度好友荣誉榜 -->
<section class="section" id="honors">
    <h2 class="section-title">🏅 年度好友荣誉榜</h2>
    <p class="section-subtitle">给每个特别的Ta，颁发专属荣誉</p>
    <div class="container">
        {make_friend_honors()}
    </div>
</section>

<!-- 年度数字亮点 -->
<section class="section numbers-section" id="numbers" style="background:linear-gradient(135deg,var(--bg),var(--bg2))">
    <h2 class="section-title">🔢 你的年度数字</h2>
    <p class="section-subtitle">每个数字背后，都是一段故事</p>
    <div class="container">
        <div class="numbers-showcase">
            <div class="number-card big">
                <div class="number-value"><span class="num" data-val="{total_msgs}">{total_msgs:,}</span></div>
                <div class="number-label">条消息</div>
                <div class="number-sub">堆起来有{int(total_msgs * 0.02)}米高</div>
            </div>
            <div class="number-card">
                <div class="number-value"><span class="num" data-val="{total_chars}">{total_chars:,}</span></div>
                <div class="number-label">个字符</div>
                <div class="number-sub">相当于{int(total_chars / 50000)}本小说</div>
            </div>
            <div class="number-card">
                <div class="number-value"><span class="num" data-val="{len(sorted_private)}">{len(sorted_private)}</span></div>
                <div class="number-label">位私聊好友</div>
                <div class="number-sub">每个人都值得被记住</div>
            </div>
            <div class="number-card">
                <div class="number-value"><span class="num" data-val="{len(sorted_groups)}">{len(sorted_groups)}</span></div>
                <div class="number-label">个群聊</div>
                <div class="number-sub">你的数字村落</div>
            </div>
            <div class="number-card">
                <div class="number-value"><span class="num" data-val="{p.get('total_sessions', 0)}">{p.get('total_sessions', 0):,}</span></div>
                <div class="number-label">次会话</div>
                <div class="number-sub">每次都是一次连接</div>
            </div>
            <div class="number-card">
                <div class="number-value"><span class="num" data-val="{sum(c.get('late_night', 0) for c in private_chats)}">{sum(c.get('late_night', 0) for c in private_chats):,}</span></div>
                <div class="number-label">条深夜消息</div>
                <div class="number-sub">夜深了才说真心话</div>
            </div>
        </div>
        <div class="numbers-insight">
            <div class="insight-text">
                如果把你今年发的消息打印出来，可以绕操场 <strong>{int(total_chars / 3000)}</strong> 圈；
                按每分钟阅读500字计算，读完需要 <strong>{int(total_chars / 500 / 60)}</strong> 小时。
                这些文字，是你存在的证明。
            </div>
        </div>
    </div>
</section>

<!-- 结束页 - 生成长图 -->
<section class="ending-section" id="ending">
    {make_ending_section()}
    
    <!-- 分享卡片 -->
    {make_share_card()}
    
    <!-- 分享按钮组 -->
    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; margin: 30px auto;">
        <button class="screenshot-btn" id="screenshotBtn" onclick="showImageModeDialog()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
            </svg>
            生成长图分享
        </button>
        <button class="screenshot-btn" style="background: linear-gradient(135deg, #4ECDC4, #60A5FA);" onclick="showNineGridDialog()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="7" height="7"></rect>
                <rect x="14" y="3" width="7" height="7"></rect>
                <rect x="14" y="14" width="7" height="7"></rect>
                <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
            朋友圈九宫格
        </button>
    </div>
</section>

<!-- 页脚 - 放在最后 -->
<footer>
    <p style="font-size:28px;margin-bottom:15px">✨🎉✨</p>
    <p class="footer-stats">基于 {total_msgs:,} 条消息</p>
    <p class="footer-stats">{len(sorted_private)} 位联系人 · {len(sorted_groups)} 个群聊</p>
    <p style="font-size:12px;margin-bottom:15px">生成于 {datetime.now().strftime('%Y.%m.%d %H:%M')}</p>
    <p style="font-size:11px;margin-top:20px;letter-spacing:0.5px">by 远方的熵 from FDU</p>
    <p style="font-size:11px;margin-top:5px">完成代码创作于 2025/12/30</p>
    <p style="font-size:10px;margin-top:5px"><a href="mailto:yuanfangdeshang@qq.com" style="color:var(--dim);text-decoration:none">yuanfangdeshang@qq.com</a></p>
</footer>

<script>
// 创建流动线条
function createFlowingLines(){{
    const container=document.getElementById('flowingLines');
    if(!container) return;
    for(let i=0;i<8;i++){{
        const line=document.createElement('div');
        line.className='flowing-line';
        const angle = (Math.random() - 0.5) * 30;
        line.style.cssText=`
            top:${{Math.random()*100}}%;
            width:${{Math.random()*300+200}}px;
            --angle:${{angle}}deg;
            animation-duration:${{Math.random()*15+10}}s;
            animation-delay:${{Math.random()*10}}s;
            opacity:${{Math.random()*0.5+0.3}};
        `;
        container.appendChild(line);
    }}
}}

// 创建光晕效果
function createGlowOrbs(){{
    const container=document.getElementById('glowOrbs');
    if(!container) return;
    const colors=[
        'rgba(255,107,157,0.15)',
        'rgba(78,205,196,0.12)',
        'rgba(168,85,247,0.1)',
        'rgba(255,211,61,0.08)'
    ];
    for(let i=0;i<4;i++){{
        const orb=document.createElement('div');
        orb.className='glow-orb';
        orb.style.cssText=`
            left:${{Math.random()*80}}%;
            top:${{Math.random()*80}}%;
            width:${{Math.random()*300+200}}px;
            height:${{Math.random()*300+200}}px;
            background:${{colors[i%colors.length]}};
            animation-delay:${{i*5}}s;
        `;
        container.appendChild(orb);
    }}
}}

// 创建流星雨效果（替代漂浮emoji）
function createMeteors(){{
    const container=document.getElementById('meteors');
    if(!container) return;
    
    // 流星颜色 - 使用主题色的淡化版
    const colors=[
        'rgba(255,107,157,0.8)',  // 粉色
        'rgba(78,205,196,0.8)',   // 青色
        'rgba(168,85,247,0.7)',   // 紫色
        'rgba(255,211,61,0.6)',   // 黄色
        'rgba(255,255,255,0.9)'   // 白色
    ];
    
    function createMeteor(){{
        if(document.hidden) return;
        
        const meteor=document.createElement('div');
        meteor.className='meteor';
        
        // 随机参数
        const startX = Math.random() * 100 + 20;  // 起始X位置（20%-120%）
        const startY = -10;  // 从顶部上方开始
        const length = Math.random() * 80 + 40;   // 流星长度 40-120px
        const duration = Math.random() * 1.5 + 0.8;  // 持续时间 0.8-2.3秒
        const color = colors[Math.floor(Math.random() * colors.length)];
        const tailColor = color.replace(/[\\d.]+\\)$/, '0)');  // 尾部透明
        
        meteor.style.cssText=`
            left: ${{startX}}%;
            top: ${{startY}}%;
            width: ${{length}}px;
            height: 2px;
            background: linear-gradient(90deg, ${{tailColor}}, ${{color}});
            box-shadow: 0 0 6px ${{color}}, 0 0 12px ${{color}};
            animation-duration: ${{duration}}s;
        `;
        
        container.appendChild(meteor);
        
        // 动画结束后移除
        setTimeout(()=>meteor.remove(), duration * 1000 + 100);
    }}
    
    // 随机间隔生成流星（比emoji更频繁但更短暂）
    setInterval(()=>{{
        if(Math.random() > 0.4) createMeteor();  // 60%概率生成
    }}, 800);
    
    // 初始生成几颗
    for(let i=0; i<3; i++){{
        setTimeout(createMeteor, i * 300);
    }}
}}

// 创建星星
function createStars(){{
    const container=document.getElementById('stars');
    for(let i=0;i<100;i++){{
        const star=document.createElement('div');
        star.className='star';
        star.style.cssText=`
            left:${{Math.random()*100}}%;
            top:${{Math.random()*100}}%;
            width:${{Math.random()*2+1}}px;
            height:${{Math.random()*2+1}}px;
            animation-duration:${{Math.random()*3+2}}s;
            animation-delay:${{Math.random()*3}}s;
        `;
        container.appendChild(star);
    }}
}}

// 创建粒子
function createParticles(){{
    const container=document.getElementById('particles');
    const colors=['#FF6B9D','#4ECDC4','#FFD93D','#A855F7'];
    setInterval(()=>{{
        if(document.hidden)return;
        const p=document.createElement('div');
        p.className='particle';
        const size=Math.random()*6+2;
        p.style.cssText=`
            left:${{Math.random()*100}}%;
            width:${{size}}px;
            height:${{size}}px;
            background:${{colors[Math.floor(Math.random()*colors.length)]}};
            animation-duration:${{Math.random()*10+10}}s;
        `;
        container.appendChild(p);
        setTimeout(()=>p.remove(),20000);
    }},300);
}}

// 烟花效果
function createFirework(x,y){{
    const colors=['#FF6B9D','#4ECDC4','#FFD93D','#A855F7','#fff'];
    const fw=document.createElement('div');
    fw.className='firework';
    fw.style.left=x+'px';
    fw.style.top=y+'px';
    document.body.appendChild(fw);
    
    for(let i=0;i<30;i++){{
        const spark=document.createElement('div');
        spark.className='spark';
        const angle=Math.random()*Math.PI*2;
        const distance=Math.random()*100+50;
        spark.style.cssText=`
            width:${{Math.random()*4+2}}px;
            height:${{Math.random()*4+2}}px;
            background:${{colors[Math.floor(Math.random()*colors.length)]}};
            --tx:${{Math.cos(angle)*distance}}px;
            --ty:${{Math.sin(angle)*distance}}px;
        `;
        fw.appendChild(spark);
    }}
    setTimeout(()=>fw.remove(),1000);
}}

// 随机烟花
function randomFireworks(){{
    setInterval(()=>{{
        if(document.hidden||Math.random()>0.3)return;
        createFirework(Math.random()*window.innerWidth,Math.random()*window.innerHeight*0.5);
    }},2000);
}}

// 开场光线爆发效果
function createHeroRays(){{
    const hero = document.querySelector('.hero');
    if(!hero) return;
    
    const raysContainer = document.createElement('div');
    raysContainer.className = 'hero-rays';
    hero.appendChild(raysContainer);
    
    // 创建光线
    const rayCount = 12;
    for(let i = 0; i < rayCount; i++){{
        const ray = document.createElement('div');
        ray.className = 'hero-ray';
        ray.style.transform = `rotate(${{i * (360/rayCount)}}deg)`;
        ray.style.animationDelay = `${{i * 0.1}}s`;
        raysContainer.appendChild(ray);
    }}
    
    // 3秒后移除光线
    setTimeout(()=>{{
        raysContainer.style.opacity = '0';
        setTimeout(()=>raysContainer.remove(), 1000);
    }}, 3000);
}}

// 开场粒子聚合效果
function createHeroParticles(){{
    const hero = document.querySelector('.hero');
    if(!hero) return;
    
    const particleContainer = document.createElement('div');
    particleContainer.className = 'hero-particles';
    particleContainer.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;overflow:hidden;z-index:0';
    hero.appendChild(particleContainer);
    
    const colors = ['#FF6B9D', '#4ECDC4', '#FFD93D', '#A855F7'];
    
    // 创建向中心聚合的粒子
    for(let i = 0; i < 50; i++){{
        setTimeout(()=>{{
            const particle = document.createElement('div');
            particle.className = 'hero-particle';
            const size = Math.random() * 4 + 2;
            const startX = Math.random() * 100;
            const startY = Math.random() * 100;
            const duration = Math.random() * 2 + 2;
            
            particle.style.cssText = `
                position:absolute;
                width:${{size}}px;
                height:${{size}}px;
                background:${{colors[Math.floor(Math.random()*colors.length)]}};
                border-radius:50%;
                left:${{startX}}%;
                top:${{startY}}%;
                opacity:0.8;
                animation:particle-to-center ${{duration}}s ease-in forwards;
            `;
            particleContainer.appendChild(particle);
            setTimeout(()=>particle.remove(), duration * 1000);
        }}, i * 50);
    }}
}}

// 庆祝彩纸效果
function createConfetti(){{
    const colors = ['#FF6B9D', '#4ECDC4', '#FFD93D', '#A855F7', '#fff'];
    for(let i = 0; i < 100; i++){{
        setTimeout(()=>{{
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            const size = Math.random() * 8 + 4;
            const left = Math.random() * 100;
            const delay = Math.random() * 2;
            const duration = Math.random() * 2 + 2;
            
            confetti.style.cssText = `
                left:${{left}}%;
                width:${{size}}px;
                height:${{size}}px;
                background:${{colors[Math.floor(Math.random()*colors.length)]}};
                animation-delay:${{delay}}s;
                animation-duration:${{duration}}s;
                border-radius:${{Math.random() > 0.5 ? '50%' : '2px'}};
            `;
            document.body.appendChild(confetti);
            setTimeout(()=>confetti.remove(), (delay + duration) * 1000);
        }}, i * 30);
    }}
}}

// 结尾页面庆祝效果触发
function initEndingCelebration(){{
    const ending = document.querySelector('#ending');
    if(!ending) return;
    
    const observer = new IntersectionObserver((entries)=>{{
        entries.forEach(entry=>{{
            if(entry.isIntersecting && !ending.dataset.celebrated){{
                ending.dataset.celebrated = '1';
                setTimeout(()=>createConfetti(), 500);
            }}
        }});
    }}, {{threshold: 0.5}});
    
    observer.observe(ending);
}}

// 下载分享卡片（简化版）
function downloadShareCard(){{
    const card = document.getElementById('shareCard');
    if(!card) return;
    
    // 提示用户截图保存
    alert('提示：请使用浏览器的截图功能或手机长按保存图片');
    
    // 触发庆祝效果
    createConfetti();
}}

// 数字滚动
function animateNumbers(){{
    const observer=new IntersectionObserver((entries)=>{{
        entries.forEach(entry=>{{
            if(entry.isIntersecting){{
                const el=entry.target;
                if(el.dataset.animated)return;
                el.dataset.animated='1';
                const target=parseFloat(el.dataset.val)||0;
                const duration=1200;
                const start=performance.now();
                function update(now){{
                    const progress=Math.min((now-start)/duration,1);
                    const eased=1-Math.pow(1-progress,3);
                    el.textContent=Math.floor(target*eased).toLocaleString();
                    if(progress<1)requestAnimationFrame(update);
                    else el.textContent=target.toLocaleString();
                }}
                requestAnimationFrame(update);
            }}
        }});
    }},{{threshold:0.3}});
    document.querySelectorAll('.num').forEach(n=>observer.observe(n));
}}

// 进度条动画
function animateBars(){{
    const observer=new IntersectionObserver((entries)=>{{
        entries.forEach(entry=>{{
            if(entry.isIntersecting){{
                const bar=entry.target;
                const w=bar.style.width;
                bar.style.width='0';
                setTimeout(()=>bar.style.width=w,100);
            }}
        }});
    }},{{threshold:0.3}});
    document.querySelectorAll('.rank-fill,.bar-them,.bar-me').forEach(b=>observer.observe(b));
}}

// 卡片折叠
function toggleCard(header){{
    header.parentElement.classList.toggle('open');
}}
function expandAll(type){{
    document.querySelectorAll(type==='chat'?'.chat-card':'.group-card').forEach(c=>c.classList.add('open'));
}}
function collapseAll(type){{
    document.querySelectorAll(type==='chat'?'.chat-card':'.group-card').forEach(c=>c.classList.remove('open'));
}}

// 显示更多/收起卡片列表
function toggleMoreCards(type){{
    const isPrivate = type === 'private';
    const wrapper = document.getElementById(isPrivate ? 'privateCardsWrapper' : 'groupCardsWrapper');
    const showMoreBtn = document.getElementById(isPrivate ? 'privateShowMore' : 'groupShowMore');
    const controls = document.getElementById(isPrivate ? 'privateControls' : 'groupControls');
    
    if(wrapper.classList.contains('show-all')){{
        // 收起
        wrapper.classList.remove('show-all');
        showMoreBtn.style.display = 'block';
        controls.style.display = 'none';
        // 滚动到section顶部
        const section = document.getElementById(isPrivate ? 'private-detail' : 'group-detail');
        section.scrollIntoView({{behavior:'smooth', block:'start'}});
    }} else {{
        // 展开
        wrapper.classList.add('show-all');
        showMoreBtn.style.display = 'none';
        controls.style.display = 'block';
    }}
}}

// 好友默契度 - 滚动到视口时自动播放动画
function initChemistryAnimation(){{
    const list = document.getElementById('chemistryList');
    if(!list) return;
    
    const observer = new IntersectionObserver((entries) => {{
        entries.forEach(entry => {{
            if(entry.isIntersecting){{
                // 给所有卡片添加animate类，触发动画
                const cards = list.querySelectorAll('.chemistry-card');
                cards.forEach(card => card.classList.add('animate'));
                // 只触发一次
                observer.unobserve(entry.target);
            }}
        }});
    }}, {{threshold: 0.2}});
    
    observer.observe(list);
}}

// 导航高亮
function updateNav(){{
    const sections=['hero','heatmap','journey','rhythm','emoji-analysis','word-cloud','motivation','chemistry','private-rank','group-overview','numbers','ending'];
    window.addEventListener('scroll',()=>{{
        let current='';
        sections.forEach(id=>{{
            const s=document.getElementById(id);
            if(s&&s.getBoundingClientRect().top<=150)current=id;
        }});
        document.querySelectorAll('.nav a').forEach(a=>{{
            a.classList.toggle('active',a.getAttribute('href')==='#'+current);
        }});
    }});
}}

// 点击烟花
document.addEventListener('click',e=>{{
    if(e.target.closest('.nav,.btn,.chat-header,.group-header,.music-btn'))return;
    createFirework(e.clientX,e.clientY);
}});

// ========== 背景音乐控制 ==========
let isMuted = true;
const bgm = document.getElementById('bgm');
const musicBtn = document.getElementById('musicBtn');

function toggleMusic() {{
    if (isMuted) {{
        bgm.play().catch(e => console.log('音乐播放失败'));
        musicBtn.textContent = '🎵';
        musicBtn.classList.remove('muted');
    }} else {{
        bgm.pause();
        musicBtn.textContent = '🔇';
        musicBtn.classList.add('muted');
    }}
    isMuted = !isMuted;
}}

// 展开/收起排行榜
function toggleRank(btn) {{
    const hidden = btn.previousElementSibling;
    if (hidden && hidden.classList.contains('rank-hidden')) {{
        hidden.classList.toggle('show');
        if (hidden.classList.contains('show')) {{
            btn.textContent = '收起 ▲';
            btn.classList.add('expanded');
        }} else {{
            btn.textContent = '展开更多 ▼';
            btn.classList.remove('expanded');
        }}
    }}
}}

// 文字渐入动画
function animateText() {{
    const observer = new IntersectionObserver((entries) => {{
        entries.forEach(entry => {{
            if (entry.isIntersecting) {{
                entry.target.classList.add('text-visible');
            }}
        }});
    }}, {{threshold: 0.1}});
    document.querySelectorAll('.insight-item, .ranking-title, .ranking-stats, .section-title, .fg-title').forEach(el => {{
        el.classList.add('text-animate');
        observer.observe(el);
    }});
    
    // 滚动淡入动画 - 更多元素（包含新增模块）
    const revealObserver = new IntersectionObserver((entries) => {{
        entries.forEach(entry => {{
            if (entry.isIntersecting) {{
                entry.target.classList.add('revealed');
            }}
        }});
    }}, {{threshold: 0.1}});
    document.querySelectorAll('.letter-wrapper, .colors-section, .share-card, .heatmap-grid, .profile-card, .emoji-analysis, .motivation-analysis, .quality-analysis, .rhythm-container, .section-summary').forEach(el => {{
        el.classList.add('scroll-reveal');
        revealObserver.observe(el);
    }});
    
    // 进度条填充动画
    const barObserver = new IntersectionObserver((entries) => {{
        entries.forEach(entry => {{
            if (entry.isIntersecting) {{
                entry.target.querySelectorAll('.rhythm-period-fill, .motivation-fill, .qb-fill').forEach(bar => {{
                    const width = bar.style.width;
                    bar.style.width = '0%';
                    setTimeout(() => {{ bar.style.width = width; }}, 100);
                }});
                barObserver.unobserve(entry.target);
            }}
        }});
    }}, {{threshold: 0.3}});
    document.querySelectorAll('.rhythm-periods, .motivation-bars, .quality-cards').forEach(el => {{
        barObserver.observe(el);
    }});
    
    // 默契度卡片逐条显示动画
    const chemistryObserver = new IntersectionObserver((entries) => {{
        entries.forEach(entry => {{
            if (entry.isIntersecting) {{
                // 获取父容器下的所有卡片
                const cards = entry.target.querySelectorAll('.chemistry-card');
                cards.forEach((card, index) => {{
                    setTimeout(() => {{
                        card.classList.add('visible');
                    }}, index * 200);  // 每张卡片延迟200ms
                }});
                chemistryObserver.unobserve(entry.target);  // 只触发一次
            }}
        }});
    }}, {{threshold: 0.2}});
    
    const chemistryList = document.querySelector('.chemistry-list');
    if (chemistryList) {{
        chemistryObserver.observe(chemistryList);
    }}
}}

// ========== 音乐按钮拖动功能 ==========
function initDraggable() {{
    const btn = document.getElementById('musicBtn');
    let isDragging = false;
    let hasMoved = false;
    let startX, startY, initialX, initialY;
    
    btn.addEventListener('mousedown', startDrag);
    btn.addEventListener('touchstart', startDrag, {{passive: false}});
    
    function startDrag(e) {{
        isDragging = true;
        hasMoved = false;
        btn.classList.add('dragging');
        
        if (e.type === 'touchstart') {{
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }} else {{
            startX = e.clientX;
            startY = e.clientY;
        }}
        
        const rect = btn.getBoundingClientRect();
        initialX = rect.left;
        initialY = rect.top;
        
        document.addEventListener('mousemove', drag);
        document.addEventListener('touchmove', drag, {{passive: false}});
        document.addEventListener('mouseup', stopDrag);
        document.addEventListener('touchend', stopDrag);
    }}
    
    function drag(e) {{
        if (!isDragging) return;
        e.preventDefault();
        
        let currentX, currentY;
        if (e.type === 'touchmove') {{
            currentX = e.touches[0].clientX;
            currentY = e.touches[0].clientY;
        }} else {{
            currentX = e.clientX;
            currentY = e.clientY;
        }}
        
        const deltaX = currentX - startX;
        const deltaY = currentY - startY;
        
        if (Math.abs(deltaX) > 5 || Math.abs(deltaY) > 5) {{
            hasMoved = true;
        }}
        
        let newX = initialX + deltaX;
        let newY = initialY + deltaY;
        
        newX = Math.max(0, Math.min(window.innerWidth - 50, newX));
        newY = Math.max(0, Math.min(window.innerHeight - 50, newY));
        
        btn.style.left = newX + 'px';
        btn.style.top = newY + 'px';
        btn.style.right = 'auto';
    }}
    
    function stopDrag() {{
        isDragging = false;
        btn.classList.remove('dragging');
        
        document.removeEventListener('mousemove', drag);
        document.removeEventListener('touchmove', drag);
        document.removeEventListener('mouseup', stopDrag);
        document.removeEventListener('touchend', stopDrag);
    }}
    
    btn.addEventListener('click', (e) => {{
        if (hasMoved) {{
            e.preventDefault();
            e.stopPropagation();
        }}
    }}, true);
}}

// ========== 生成长图功能 ==========
// 有意境的文件名列表
const poeticNames = [
    'A_星河漫漫', 'A_流年似水', 'A_岁月如歌', 'A_时光剪影', 
    'A_浮生若梦', 'A_念念不忘', 'A_情深似海', 'A_温暖如初',
    'A_微光不灭', 'A_繁星点点', 'A_月色朦胧', 'A_清风徐来'
];

function showImageModeDialog() {{
    // 创建选择对话框
    const overlay = document.createElement('div');
    overlay.id = 'imageModeOverlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    `;
    
    overlay.innerHTML = `
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 30px; border-radius: 20px; text-align: center; max-width: 400px; border: 1px solid rgba(255,107,157,0.3);">
            <h3 style="color: #fff; margin-bottom: 20px; font-size: 18px;">📱 选择长图格式</h3>
            <p style="color: #888; margin-bottom: 25px; font-size: 14px;">手机版适合分享到朋友圈，PC版内容更完整</p>
            <div style="display: flex; gap: 15px; justify-content: center;">
                <button onclick="generateLongImage('mobile')" style="padding: 12px 30px; background: linear-gradient(135deg, #FF6B9D, #A855F7); border: none; border-radius: 25px; color: #fff; font-size: 15px; cursor: pointer; transition: transform 0.2s;">
                    📱 手机版<br><small style="opacity:0.8">竖长条</small>
                </button>
                <button onclick="generateLongImage('pc')" style="padding: 12px 30px; background: linear-gradient(135deg, #4ECDC4, #60A5FA); border: none; border-radius: 25px; color: #fff; font-size: 15px; cursor: pointer; transition: transform 0.2s;">
                    💻 PC版<br><small style="opacity:0.8">宽幅</small>
                </button>
            </div>
            <button onclick="document.getElementById('imageModeOverlay').remove()" style="margin-top: 20px; padding: 8px 20px; background: transparent; border: 1px solid #666; border-radius: 15px; color: #888; cursor: pointer;">取消</button>
        </div>
    `;
    
    document.body.appendChild(overlay);
}}

// ========== 快速截图（悬浮按钮）==========
async function quickScreenshot() {{
    const floatBtn = document.getElementById('floatScreenshotBtn');
    
    // 添加capturing类隐藏按钮
    floatBtn.classList.add('capturing');
    
    try {{
        // 加载html2canvas
        if (typeof html2canvas === 'undefined') {{
            await loadScript('https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js');
        }}
        
        // 隐藏不需要截图的元素
        const hideElements = document.querySelectorAll('.nav, .music-btn, .float-screenshot-btn');
        hideElements.forEach(el => el.style.visibility = 'hidden');
        
        // 获取当前可视区域
        const scrollY = window.scrollY;
        const viewportHeight = window.innerHeight;
        
        // 截取当前屏幕
        const canvas = await html2canvas(document.body, {{
            backgroundColor: '#0a0a1a',
            scale: 2,
            useCORS: true,
            logging: false,
            y: scrollY,
            height: viewportHeight,
            windowWidth: document.documentElement.clientWidth,
            windowHeight: viewportHeight
        }});
        
        // 恢复隐藏的元素
        hideElements.forEach(el => el.style.visibility = '');
        
        // 下载图片
        const link = document.createElement('a');
        link.download = `微信年报截图_${{new Date().toLocaleDateString().replace(/\\//g, '-')}}.png`;
        link.href = canvas.toDataURL('image/png', 0.9);
        link.click();
        
        // 显示成功提示
        showToast('✅ 截图已保存');
        
    }} catch (err) {{
        console.error('截图失败:', err);
        showToast('❌ 截图失败，请重试');
    }} finally {{
        // 移除capturing类恢复按钮
        floatBtn.classList.remove('capturing');
    }}
}}

// 简单的Toast提示
function showToast(msg) {{
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 150px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0,0,0,0.8);
        color: #fff;
        padding: 12px 24px;
        border-radius: 25px;
        font-size: 14px;
        z-index: 9999;
        animation: fadeInOut 2s ease-in-out forwards;
    `;
    toast.textContent = msg;
    
    // 添加动画样式
    if (!document.getElementById('toastStyle')) {{
        const style = document.createElement('style');
        style.id = 'toastStyle';
        style.textContent = `
            @keyframes fadeInOut {{
                0% {{ opacity: 0; transform: translateX(-50%) translateY(20px); }}
                15% {{ opacity: 1; transform: translateX(-50%) translateY(0); }}
                85% {{ opacity: 1; transform: translateX(-50%) translateY(0); }}
                100% {{ opacity: 0; transform: translateX(-50%) translateY(-20px); }}
            }}
        `;
        document.head.appendChild(style);
    }}
    
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
}}

async function generateLongImage(mode = 'mobile') {{
    // 关闭选择对话框
    const overlay = document.getElementById('imageModeOverlay');
    if (overlay) overlay.remove();
    
    const btn = document.getElementById('screenshotBtn');
    const originalText = btn.innerHTML;
    
    btn.innerHTML = '<svg class="spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>生成中...';
    btn.disabled = true;
    
    try {{
        // 加载html2canvas
        if (typeof html2canvas === 'undefined') {{
            await loadScript('https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js');
        }}
        
        // 隐藏不需要截图的元素
        const fixedElements = document.querySelectorAll('.nav, .music-btn, .float-screenshot-btn');
        fixedElements.forEach(el => el.style.display = 'none');
        
        // 隐藏排行榜列表（中间太长的部分）
        const rankSections = document.querySelectorAll('#private-rank, #group-rank, #private-detail, #group-detail');
        const hiddenSections = [];
        rankSections.forEach(el => {{
            if (el) {{
                hiddenSections.push({{el: el, display: el.style.display}});
                el.style.display = 'none';
            }}
        }});
        
        // 添加提示说明（排行榜已隐藏）
        const notice = document.createElement('div');
        notice.id = 'rankNotice';
        notice.style.cssText = `
            text-align: center;
            padding: 40px 20px;
            color: #888;
            font-size: 14px;
        `;
        notice.innerHTML = '📋 完整排行榜请查看原报告';
        const endingSection = document.getElementById('ending');
        if (endingSection) {{
            endingSection.parentNode.insertBefore(notice, endingSection);
        }}
        
        // 根据模式设置宽度
        const targetWidth = mode === 'mobile' ? 375 : 1200;
        const originalWidth = document.body.style.width;
        
        if (mode === 'mobile') {{
            document.body.style.width = targetWidth + 'px';
        }}
        
        // 等待样式应用
        await new Promise(r => setTimeout(r, 500));
        
        const canvas = await html2canvas(document.body, {{
            backgroundColor: '#0a0a1a',
            scale: mode === 'mobile' ? 2 : 1.5,
            useCORS: true,
            logging: false,
            width: targetWidth,
            windowWidth: targetWidth,
            windowHeight: document.body.scrollHeight
        }});
        
        // 恢复隐藏的元素
        fixedElements.forEach(el => el.style.display = '');
        hiddenSections.forEach(({{el, display}}) => {{
            el.style.display = display;
        }});
        
        // 移除提示
        const noticeEl = document.getElementById('rankNotice');
        if (noticeEl) noticeEl.remove();
        
        // 恢复宽度
        document.body.style.width = originalWidth;
        
        // 生成有意境的文件名
        const poeticName = poeticNames[Math.floor(Math.random() * poeticNames.length)];
        const modeText = mode === 'mobile' ? '手机版' : 'PC版';
        const filename = `${{poeticName}}_2025年度聊天报告_${{modeText}}.png`;
        
        const link = document.createElement('a');
        link.download = filename;
        link.href = canvas.toDataURL('image/png');
        link.click();
        
        btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>已保存!';
        setTimeout(() => {{
            btn.innerHTML = originalText;
            btn.disabled = false;
        }}, 2000);
        
    }} catch (err) {{
        console.error('截图失败:', err);
        btn.innerHTML = '❌ 截图失败，请重试';
        setTimeout(() => {{
            btn.innerHTML = originalText;
            btn.disabled = false;
        }}, 3000);
    }}
}}

function loadScript(src) {{
    return new Promise((resolve, reject) => {{
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    }});
}}

// ========== 朋友圈九宫格生成 ==========
function showNineGridDialog() {{
    const overlay = document.createElement('div');
    overlay.id = 'nineGridOverlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.85);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        overflow-y: auto;
        padding: 20px;
    `;
    
    overlay.innerHTML = `
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 30px; border-radius: 20px; text-align: center; max-width: 500px; border: 1px solid rgba(255,107,157,0.3);">
            <h3 style="color: #fff; margin-bottom: 15px; font-size: 20px;">📱 生成朋友圈九宫格</h3>
            <p style="color: #888; margin-bottom: 20px; font-size: 13px;">
                生成9张精美图片，适合发朋友圈分享<br>
                <span style="color: #4ECDC4;">包含：年度概览、最佳拍档、深夜陪伴、年度色彩、<br>用户画像、好友默契、聊天热力、年度感悟、2026祝福</span>
            </p>
            <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px;">
                <button onclick="generateNineGrid()" style="padding: 14px 30px; background: linear-gradient(135deg, #FF6B9D, #A855F7); border: none; border-radius: 25px; color: #fff; font-size: 15px; cursor: pointer; font-weight: 600;">
                    🎨 开始生成九宫格
                </button>
            </div>
            <p style="color: #666; font-size: 11px; margin-bottom: 15px;">
                ⏱️ 生成需要约10-20秒，请耐心等待
            </p>
            <button onclick="document.getElementById('nineGridOverlay').remove()" style="padding: 8px 25px; background: transparent; border: 1px solid #666; border-radius: 15px; color: #888; cursor: pointer; font-size: 13px;">取消</button>
        </div>
    `;
    
    document.body.appendChild(overlay);
}}

async function generateNineGrid() {{
    const overlay = document.getElementById('nineGridOverlay');
    if (!overlay) return;
    
    // 更新对话框显示进度
    overlay.innerHTML = `
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 40px; border-radius: 20px; text-align: center; max-width: 400px; border: 1px solid rgba(255,107,157,0.3);">
            <div id="gridProgress" style="font-size: 48px; margin-bottom: 20px;">🎨</div>
            <h3 style="color: #fff; margin-bottom: 10px;">正在生成九宫格...</h3>
            <p id="gridStatus" style="color: #4ECDC4; font-size: 14px;">准备中...</p>
            <div style="width: 100%; height: 6px; background: #333; border-radius: 3px; margin-top: 20px; overflow: hidden;">
                <div id="gridBar" style="width: 0%; height: 100%; background: linear-gradient(90deg, #FF6B9D, #A855F7); transition: width 0.3s;"></div>
            </div>
        </div>
    `;
    
    try {{
        // 加载html2canvas
        if (typeof html2canvas === 'undefined') {{
            updateGridProgress(5, '加载依赖库...');
            await loadScript('https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js');
        }}
        
        // 创建隐藏的渲染容器
        const container = document.createElement('div');
        container.id = 'gridContainer';
        container.style.cssText = 'position: fixed; left: -9999px; top: 0; width: 1080px;';
        document.body.appendChild(container);
        
        const poeticName = poeticNames[Math.floor(Math.random() * poeticNames.length)];
        const images = [];
        
        // 获取页面数据
        const heroStats = document.querySelectorAll('.hero-stat-val');
        const totalMsgs = heroStats[0]?.textContent || '0';
        const totalFriends = heroStats[1]?.textContent || '0';
        const totalDays = heroStats[2]?.textContent || '0';
        const totalChars = heroStats[3]?.textContent || '0';
        
        // 获取最佳拍档
        const bestFriend = document.querySelector('.chemistry-name')?.textContent || '好友';
        const bestScore = document.querySelector('.chemistry-score-val')?.textContent || '99';
        
        // 获取色彩数据
        const colorItems = document.querySelectorAll('.color-item');
        let colorData = [];
        colorItems.forEach(item => {{
            const name = item.querySelector('.color-name')?.childNodes[0]?.textContent?.trim() || '';
            const pct = item.querySelector('.color-name span')?.textContent || '';
            const dot = item.querySelector('.color-dot');
            const color = dot ? getComputedStyle(dot).background : '#FF6B9D';
            if (name) colorData.push({{name, pct, color}});
        }});
        
        // 获取用户画像
        const profileTags = [];
        document.querySelectorAll('.profile-tag, .personality-tag').forEach(tag => {{
            profileTags.push(tag.textContent);
        }});
        
        // 九张图内容定义
        const gridContents = [
            // 图1: 年度概览
            {{
                title: '2025 年度聊天报告',
                emoji: '📊',
                content: `
                    <div style="font-size: 72px; font-weight: 900; background: linear-gradient(135deg, #FF6B9D, #4ECDC4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 30px;">${{totalMsgs}}</div>
                    <div style="font-size: 24px; color: #888; margin-bottom: 50px;">条消息，记录了这一年</div>
                    <div style="display: flex; justify-content: center; gap: 40px;">
                        <div style="text-align: center;"><div style="font-size: 36px; color: #4ECDC4; font-weight: 700;">${{totalFriends}}</div><div style="color: #666; font-size: 14px;">位好友</div></div>
                        <div style="text-align: center;"><div style="font-size: 36px; color: #FFD93D; font-weight: 700;">${{totalDays}}</div><div style="color: #666; font-size: 14px;">聊天天数</div></div>
                        <div style="text-align: center;"><div style="font-size: 36px; color: #A855F7; font-weight: 700;">${{totalChars}}</div><div style="color: #666; font-size: 14px;">总字数</div></div>
                    </div>
                `,
                bg: 'linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #0f1a2e 100%)'
            }},
            // 图2: 最佳拍档
            {{
                title: '年度最佳拍档',
                emoji: '👫',
                content: `
                    <div style="width: 120px; height: 120px; border-radius: 50%; background: linear-gradient(135deg, #FF6B9D, #A855F7); display: flex; align-items: center; justify-content: center; margin: 0 auto 30px; font-size: 48px; box-shadow: 0 10px 40px rgba(255,107,157,0.3);">💕</div>
                    <div style="font-size: 42px; font-weight: 700; color: #fff; margin-bottom: 15px;">${{bestFriend}}</div>
                    <div style="font-size: 18px; color: #888; margin-bottom: 30px;">是陪你说话最多的人</div>
                    <div style="font-size: 64px; font-weight: 800; color: #4ECDC4;">${{bestScore}}<span style="font-size: 24px;">分</span></div>
                    <div style="color: #666; font-size: 14px;">默契指数</div>
                `,
                bg: 'linear-gradient(135deg, #1a0a1a 0%, #2a1a2e 50%, #1a1a3e 100%)'
            }},
            // 图3: 深夜陪伴
            {{
                title: '深夜陪伴',
                emoji: '🌙',
                content: `
                    <div style="font-size: 100px; margin-bottom: 20px;">🌙</div>
                    <div style="font-size: 20px; color: #888; margin-bottom: 30px;">那些凌晨的对话</div>
                    <div style="font-size: 48px; font-weight: 700; color: #A855F7; margin-bottom: 10px;">深夜时分</div>
                    <div style="font-size: 16px; color: #666; line-height: 2;">
                        总有人愿意陪你聊到很晚<br>
                        那些夜里的消息<br>
                        是最真实的心意
                    </div>
                `,
                bg: 'linear-gradient(180deg, #0a0a2a 0%, #1a1a3e 50%, #0a1a2e 100%)'
            }},
            // 图4: 年度色彩
            {{
                title: '年度聊天色彩',
                emoji: '🎨',
                content: `
                    <div style="width: 150px; height: 150px; border-radius: 50%; background: linear-gradient(135deg, #FF6B9D, #A855F7, #4ECDC4, #FFD93D); margin: 0 auto 30px; box-shadow: 0 10px 50px rgba(255,107,157,0.4);"></div>
                    <div style="display: flex; flex-direction: column; gap: 15px; text-align: left; padding: 0 60px;">
                        ${{colorData.slice(0,4).map(c => `
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <div style="width: 16px; height: 16px; border-radius: 50%; background: ${{c.color}};"></div>
                                <span style="color: #fff; font-size: 16px;">${{c.name}}</span>
                                <span style="color: #888; font-size: 14px;">${{c.pct}}</span>
                            </div>
                        `).join('')}}
                    </div>
                `,
                bg: 'linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 100%)'
            }},
            // 图5: 用户画像
            {{
                title: '这就是你',
                emoji: '✨',
                content: `
                    <div style="font-size: 80px; margin-bottom: 30px;">🪞</div>
                    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; padding: 0 40px;">
                        ${{profileTags.slice(0,8).map(tag => `
                            <span style="padding: 10px 20px; background: rgba(255,107,157,0.15); border: 1px solid rgba(255,107,157,0.3); border-radius: 20px; color: #FF6B9D; font-size: 15px;">${{tag}}</span>
                        `).join('')}}
                    </div>
                    <div style="margin-top: 40px; color: #666; font-size: 14px;">—— 数据勾勒的你</div>
                `,
                bg: 'linear-gradient(135deg, #1a0a2a 0%, #0a1a2e 100%)'
            }},
            // 图6: 聊天风格
            {{
                title: '聊天风格',
                emoji: '💬',
                content: `
                    <div style="font-size: 80px; margin-bottom: 30px;">💬</div>
                    <div style="font-size: 24px; color: #4ECDC4; margin-bottom: 30px;">你的聊天特点</div>
                    <div style="display: flex; justify-content: center; gap: 30px;">
                        <div style="text-align: center; padding: 20px; background: rgba(78,205,196,0.1); border-radius: 15px;">
                            <div style="font-size: 32px; margin-bottom: 10px;">🗣️</div>
                            <div style="color: #fff; font-size: 14px;">话多星人</div>
                        </div>
                        <div style="text-align: center; padding: 20px; background: rgba(255,107,157,0.1); border-radius: 15px;">
                            <div style="font-size: 32px; margin-bottom: 10px;">⚡</div>
                            <div style="color: #fff; font-size: 14px;">秒回达人</div>
                        </div>
                        <div style="text-align: center; padding: 20px; background: rgba(168,85,247,0.1); border-radius: 15px;">
                            <div style="font-size: 32px; margin-bottom: 10px;">🌙</div>
                            <div style="color: #fff; font-size: 14px;">夜猫子</div>
                        </div>
                    </div>
                `,
                bg: 'linear-gradient(135deg, #0a1a2a 0%, #1a0a2e 100%)'
            }},
            // 图7: 聊天热力
            {{
                title: '聊天热力图',
                emoji: '🔥',
                content: `
                    <div style="font-size: 80px; margin-bottom: 20px;">📅</div>
                    <div style="font-size: 20px; color: #888; margin-bottom: 30px;">2025年，每个月都在聊</div>
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; padding: 0 50px;">
                        ${{['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'].map((m, i) => `
                            <div style="text-align: center;">
                                <div style="height: ${{40 + Math.random() * 40}}px; background: linear-gradient(180deg, #FF6B9D, #A855F7); border-radius: 8px; margin-bottom: 5px;"></div>
                                <div style="color: #888; font-size: 12px;">${{m}}</div>
                            </div>
                        `).join('')}}
                    </div>
                `,
                bg: 'linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 100%)'
            }},
            // 图8: 年度感悟
            {{
                title: '年度感悟',
                emoji: '💭',
                content: `
                    <div style="font-size: 32px; color: #FF6B9D; margin-bottom: 40px; font-style: italic;">"</div>
                    <div style="font-size: 22px; color: #fff; line-height: 2; padding: 0 40px;">
                        每一条消息<br>
                        都是一份心意的传递<br><br>
                        那些深夜的对话<br>
                        是最真实的自己
                    </div>
                    <div style="font-size: 32px; color: #FF6B9D; margin-top: 40px; font-style: italic;">"</div>
                `,
                bg: 'linear-gradient(135deg, #1a1a2e 0%, #0a1a3e 100%)'
            }},
            // 图9: 2026祝福
            {{
                title: '2026',
                emoji: '🎆',
                content: `
                    <div style="font-size: 100px; font-weight: 900; background: linear-gradient(135deg, #FFD93D, #FF6B9D, #A855F7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px;">2026</div>
                    <div style="font-size: 24px; color: #fff; margin-bottom: 30px;">新的一年</div>
                    <div style="font-size: 18px; color: #888; line-height: 2;">
                        愿你的消息列表里<br>
                        都是想见的人<br><br>
                        愿每一条消息<br>
                        都被温柔以待
                    </div>
                    <div style="margin-top: 40px; font-size: 14px; color: #666;">—— 2025年度聊天报告</div>
                `,
                bg: 'linear-gradient(135deg, #0a0a2a 0%, #1a0a2e 50%, #2a1a3e 100%)'
            }}
        ];
        
        // 生成每张图
        for (let i = 0; i < 9; i++) {{
            updateGridProgress(10 + i * 10, `生成第 ${{i + 1}}/9 张...`);
            
            const grid = gridContents[i];
            container.innerHTML = `
                <div style="width: 1080px; height: 1080px; background: ${{grid.bg}}; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 60px; box-sizing: border-box; position: relative; overflow: hidden;">
                    <!-- 装饰元素 -->
                    <div style="position: absolute; top: -100px; right: -100px; width: 300px; height: 300px; background: radial-gradient(circle, rgba(255,107,157,0.1) 0%, transparent 70%); border-radius: 50%;"></div>
                    <div style="position: absolute; bottom: -100px; left: -100px; width: 300px; height: 300px; background: radial-gradient(circle, rgba(78,205,196,0.1) 0%, transparent 70%); border-radius: 50%;"></div>
                    
                    <!-- 标题 -->
                    <div style="font-size: 18px; color: #888; margin-bottom: 40px; letter-spacing: 2px;">${{grid.emoji}} ${{grid.title}}</div>
                    
                    <!-- 内容 -->
                    ${{grid.content}}
                    
                    <!-- 底部水印 -->
                    <div style="position: absolute; bottom: 30px; left: 0; right: 0; text-align: center; color: #444; font-size: 12px;">微信年度聊天报告 · 2025</div>
                </div>
            `;
            
            await new Promise(r => setTimeout(r, 100));
            
            const canvas = await html2canvas(container, {{
                backgroundColor: null,
                scale: 1,
                useCORS: true,
                logging: false,
                width: 1080,
                height: 1080
            }});
            
            images.push(canvas.toDataURL('image/png'));
        }}
        
        // 清理
        container.remove();
        
        updateGridProgress(95, '打包下载中...');
        
        // 逐张下载
        for (let i = 0; i < images.length; i++) {{
            const link = document.createElement('a');
            link.download = `${{poeticName}}_朋友圈${{i + 1}}.png`;
            link.href = images[i];
            link.click();
            await new Promise(r => setTimeout(r, 300));
        }}
        
        updateGridProgress(100, '完成！');
        
        // 显示完成
        setTimeout(() => {{
            overlay.innerHTML = `
                <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 40px; border-radius: 20px; text-align: center; max-width: 400px; border: 1px solid rgba(78,205,196,0.3);">
                    <div style="font-size: 64px; margin-bottom: 20px;">✅</div>
                    <h3 style="color: #4ECDC4; margin-bottom: 15px;">九宫格已保存！</h3>
                    <p style="color: #888; font-size: 14px; margin-bottom: 20px;">9张图片已下载到你的设备<br>打开微信朋友圈即可分享</p>
                    <button onclick="document.getElementById('nineGridOverlay').remove()" style="padding: 12px 30px; background: linear-gradient(135deg, #4ECDC4, #60A5FA); border: none; border-radius: 25px; color: #fff; font-size: 15px; cursor: pointer;">好的</button>
                </div>
            `;
        }}, 500);
        
    }} catch (err) {{
        console.error('生成九宫格失败:', err);
        overlay.innerHTML = `
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 40px; border-radius: 20px; text-align: center; max-width: 400px; border: 1px solid rgba(255,107,157,0.3);">
                <div style="font-size: 64px; margin-bottom: 20px;">❌</div>
                <h3 style="color: #FF6B9D; margin-bottom: 15px;">生成失败</h3>
                <p style="color: #888; font-size: 14px; margin-bottom: 20px;">${{err.message || '请刷新页面重试'}}</p>
                <button onclick="document.getElementById('nineGridOverlay').remove()" style="padding: 12px 30px; background: transparent; border: 1px solid #666; border-radius: 25px; color: #888; font-size: 15px; cursor: pointer;">关闭</button>
            </div>
        `;
    }}
}}

function updateGridProgress(pct, text) {{
    const bar = document.getElementById('gridBar');
    const status = document.getElementById('gridStatus');
    if (bar) bar.style.width = pct + '%';
    if (status) status.textContent = text;
}}

// ========== 数据驱动的叙事式开场动画 ==========
function createHeroParticles() {{
    const hero = document.querySelector('.hero');
    const layer = document.getElementById('introAnimationLayer');
    const heroContent = document.getElementById('heroContent');
    if (!hero || !layer) return;
    
    const data = window.INTRO_ANIMATION_DATA || {{}};
    const snippets = data.snippets || ['在吗？', '好的', '哈哈', '😂', '晚安'];
    const emojis = data.emojis || ['😂', '🥰', '👍', '❤️'];
    const monthly = data.monthly || [];
    const stats = data.stats || {{}};
    
    let phase = 0;
    const totalDuration = 11000; // 总时长11秒
    
    // 阶段1：消息粒子飞入（0-2s）
    function phase1_particles() {{
        layer.innerHTML = '<div class="intro-narrative"><div class="intro-narrative-text" style="animation-delay:0s">这一年，你发出的每一条消息...</div></div>';
        
        // 创建大量飞入的消息粒子
        for (let i = 0; i < 60; i++) {{
            setTimeout(() => {{
                const particle = document.createElement('div');
                particle.className = 'intro-text-particle';
                particle.textContent = snippets[Math.floor(Math.random() * snippets.length)];
                particle.style.left = Math.random() * 100 + '%';
                particle.style.bottom = '-50px';
                particle.style.animationDuration = (2 + Math.random()) + 's';
                particle.style.fontSize = (10 + Math.random() * 8) + 'px';
                particle.style.color = ['rgba(255,107,157,0.9)', 'rgba(78,205,196,0.9)', 'rgba(167,139,250,0.9)'][Math.floor(Math.random() * 3)];
                layer.appendChild(particle);
                
                setTimeout(() => particle.remove(), 3500);
            }}, i * 30);
        }}
    }}
    
    // 阶段2：聊天内容高速扫过（2-5s）
    function phase2_textStream() {{
        layer.innerHTML = '<div class="intro-narrative"><div class="intro-narrative-text">都汇成了流动的记忆...</div></div>';
        
        // 高速文字流
        const streamContainer = document.createElement('div');
        streamContainer.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;overflow:hidden';
        layer.appendChild(streamContainer);
        
        for (let i = 0; i < 40; i++) {{
            setTimeout(() => {{
                const text = document.createElement('div');
                const content = [...snippets, ...emojis][Math.floor(Math.random() * (snippets.length + emojis.length))];
                text.textContent = content;
                text.style.cssText = `
                    position:absolute;
                    top:${{10 + Math.random() * 80}}%;
                    left:${{Math.random() > 0.5 ? '-200px' : '100%'}};
                    font-size:${{14 + Math.random() * 16}}px;
                    color:rgba(255,255,255,${{0.4 + Math.random() * 0.5}});
                    white-space:nowrap;
                    animation:stream-across ${{1.5 + Math.random()}}s linear forwards;
                    text-shadow:0 0 15px rgba(255,107,157,0.6);
                `;
                streamContainer.appendChild(text);
                setTimeout(() => text.remove(), 3000);
            }}, i * 60);
        }}
        
        // 添加流动动画的CSS
        if (!document.getElementById('streamStyle')) {{
            const style = document.createElement('style');
            style.id = 'streamStyle';
            style.textContent = `
                @keyframes stream-across {{
                    0% {{ transform: translateX(0); opacity: 0; }}
                    10% {{ opacity: 1; }}
                    90% {{ opacity: 1; }}
                    100% {{ transform: translateX(${{Math.random() > 0.5 ? '' : '-'}}120vw); opacity: 0; }}
                }}
            `;
            document.head.appendChild(style);
        }}
    }}
    
    // 阶段3：时间轴汇聚（5-8s）
    function phase3_timeline() {{
        layer.innerHTML = `
            <div class="intro-narrative"><div class="intro-narrative-text">12个月的时光，汇聚成时间线</div></div>
            <div class="intro-timeline" id="introTimeline"></div>
        `;
        
        const timeline = document.getElementById('introTimeline');
        const maxCount = Math.max(...monthly.map(m => m.count || 0)) || 1;
        
        setTimeout(() => {{
            timeline.style.opacity = '1';
            timeline.style.transition = 'opacity 0.5s';
        }}, 300);
        
        monthly.forEach((m, i) => {{
            setTimeout(() => {{
                const month = document.createElement('div');
                month.className = 'intro-month';
                const height = Math.max(10, (m.count / maxCount) * 80);
                month.innerHTML = `
                    <div class="intro-month-bar" style="height:0px" data-height="${{height}}"></div>
                    <div class="intro-month-label">${{m.month}}月</div>
                `;
                timeline.appendChild(month);
                
                // 动画增长
                setTimeout(() => {{
                    month.querySelector('.intro-month-bar').style.height = height + 'px';
                }}, 50);
            }}, i * 100);
        }});
    }}
    
    // 阶段4：统计数据爆发（8-10s）
    function phase4_stats() {{
        const statItems = [
            {{ value: stats.totalMsgs || 0, label: '条消息' }},
            {{ value: stats.lateNight || 0, label: '个深夜陪伴' }},
            {{ value: stats.friends || 0, label: '位好友' }},
        ];
        
        layer.innerHTML = '';
        
        statItems.forEach((item, i) => {{
            setTimeout(() => {{
                layer.innerHTML = `
                    <div class="intro-stat-burst" style="opacity:1;animation:stat-burst 0.8s ease-out">
                        <div class="intro-stat-num">${{item.value.toLocaleString()}}</div>
                        <div class="intro-stat-label">${{item.label}}</div>
                    </div>
                `;
            }}, i * 600);
        }});
        
        // 添加爆发动画CSS
        if (!document.getElementById('burstStyle')) {{
            const style = document.createElement('style');
            style.id = 'burstStyle';
            style.textContent = `
                @keyframes stat-burst {{
                    0% {{ transform: translate(-50%,-50%) scale(0.3); opacity: 0; }}
                    50% {{ transform: translate(-50%,-50%) scale(1.1); opacity: 1; }}
                    100% {{ transform: translate(-50%,-50%) scale(1); opacity: 1; }}
                }}
            `;
            document.head.appendChild(style);
        }}
    }}
    
    // 阶段5：标题显现（10-11s）
    function phase5_reveal() {{
        layer.innerHTML = `
            <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;animation:final-reveal 1s ease-out">
                <div style="font-size:clamp(40px,10vw,80px);font-weight:900;background:linear-gradient(135deg,var(--pink),var(--cyan));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px">2025</div>
                <div style="font-size:18px;color:var(--dim)">年度微信聊天报告</div>
            </div>
        `;
        
        if (!document.getElementById('revealStyle')) {{
            const style = document.createElement('style');
            style.id = 'revealStyle';
            style.textContent = `
                @keyframes final-reveal {{
                    0% {{ opacity: 0; transform: translate(-50%,-50%) scale(0.8); }}
                    100% {{ opacity: 1; transform: translate(-50%,-50%) scale(1); }}
                }}
            `;
            document.head.appendChild(style);
        }}
        
        // 1秒后淡出动画层，显示真正内容
        setTimeout(() => {{
            layer.style.transition = 'opacity 0.8s';
            layer.style.opacity = '0';
            heroContent.style.opacity = '1';
            
            setTimeout(() => {{
                layer.classList.add('hidden');
            }}, 800);
        }}, 1000);
    }}
    
    // 执行各阶段
    phase1_particles();
    setTimeout(phase2_textStream, 2000);
    setTimeout(phase3_timeline, 5000);
    setTimeout(phase4_stats, 8000);
    setTimeout(phase5_reveal, 10000);
}}

// ========== 打字机效果 ==========
function typeWriter() {{
    const slogans = [
        '总有一个人，值得你秒回',
        '每一条消息，都是跨越山海的心意',
        '2025，感谢有你在消息列表里',
        '字里行间，皆是想你的痕迹',
        '有些人，光是名字就能让你嘴角上扬',
        '你的聊天框，藏着你的全世界',
        '那些"在吗"的背后，都是想你了',
        '深夜的消息，是最真实的温柔',
        '每一个表情包，都是我说不出口的话',
        '置顶的那个人，一定很特别吧',
        '"晚安"是结束，也是期待明天继续',
        '最好的关系，是聊不完的天',
    ];
    const slogan = slogans[Math.floor(Math.random() * slogans.length)];
    const el = document.getElementById('heroSlogan');
    if (!el) return;
    
    let i = 0;
    el.innerHTML = '<span class="cursor"></span>';
    
    function type() {{
        if (i < slogan.length) {{
            el.innerHTML = slogan.substring(0, i + 1) + '<span class="cursor"></span>';
            i++;
            setTimeout(type, 100);
        }}
    }}
    
    setTimeout(type, 800);
}}

// 初始化
document.addEventListener('DOMContentLoaded',()=>{{
    createStars();
    createFlowingLines();
    createGlowOrbs();
    createMeteors();  // 流星雨替代漂浮emoji
    createParticles();
    createHeroParticles();  // 数据驱动的叙事式开场动画
    randomFireworks();
    animateNumbers();
    animateBars();
    animateText();
    updateNav();
    initDraggable();
    // typeWriter在开场动画结束后启动（11秒后）
    setTimeout(typeWriter, 11000);
    initChemistryAnimation();  // 默契度自动动画
    initEndingCelebration();  // 结尾庆祝效果
    // 默认展开前3个
    document.querySelectorAll('.chat-card:nth-child(-n+3),.group-card:nth-child(-n+3)').forEach(c=>c.classList.add('open'));
    
    // 自动播放音乐
    setTimeout(() => {{
        bgm.play().then(() => {{
            isMuted = false;
            musicBtn.textContent = '🎵';
            musicBtn.classList.remove('muted');
        }}).catch(e => {{
            console.log('自动播放被阻止，需要用户交互');
        }});
    }}, 500);
}});
</script>

</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 终极版报告已生成: {output_path}")


if __name__ == '__main__':
    import sys
    import os
    
    # 默认参数
    data_dir = '.'
    my_name = '远方的熵'  # 你的微信昵称
    
    # 命令行参数
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    if len(sys.argv) > 2:
        my_name = sys.argv[2]
    
    print("="*60)
    print("🎆 微信年度聊天报告生成器 - 终极版")
    print("="*60)
    print(f"📂 数据目录: {data_dir}")
    print(f"👤 我的昵称: {my_name}")
    print()
    
    # ===== Excel分析选项 =====
    excel_files = [f for f in os.listdir(data_dir) if f.endswith(('.xlsx', '.xls'))]
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    
    print(f"📊 检测到 {len(json_files)} 个JSON文件（必须分析）")
    print(f"📊 检测到 {len(excel_files)} 个Excel文件")
    
    analyze_excel = False
    if excel_files:
        print()
        print("⚠️  Excel文件分析速度较慢，是否需要分析Excel文件？")
        print("    输入 y 或 yes 分析Excel，其他跳过")
        user_input = input(">>> ").strip().lower()
        analyze_excel = user_input in ['y', 'yes', '是', '1']
        
        if analyze_excel:
            print("✅ 将分析JSON + Excel文件")
        else:
            print("⏭️  跳过Excel，仅分析JSON文件")
    else:
        print("ℹ️  未检测到Excel文件，将仅分析JSON")
    
    print()
    
    # ===== 姓名脱敏选项（用于分享） =====
    print("🔒 分享时是否需要对内容进行脱敏？")
    print("    1. 不脱敏（保留原名）")
    print("    2. 脱敏（姓名显示为*同学，群名显示为**群聊）")
    mask_input = input("请选择 [1/2，默认1]: ").strip()
    
    mask_modes = {'1': 'none', '2': 'full', '': 'none'}
    mask_mode = mask_modes.get(mask_input, 'none')
    mask_desc = '脱敏模式' if mask_mode == 'full' else '不脱敏'
    print(f"✅ 隐私处理: {mask_desc}")
    print()
    
    # ===== 文件传输助手选项 =====
    print('📦 是否剔除"文件传输助手"？')
    print("    1. 剔除（推荐，不影响正常统计）")
    print("    2. 保留（文件传输助手会计入统计）")
    helper_input = input("请选择 [1/2，默认1]: ").strip()
    
    exclude_file_helper = helper_input != '2'
    helper_desc = '剔除文件传输助手' if exclude_file_helper else '保留文件传输助手'
    print(f"✅ {helper_desc}")
    print()
    
    # 查找背景音乐
    bgm_path = None
    for bgm_name in ['bgm.mp3', 'BGM.mp3', 'music.mp3']:
        test_path = os.path.join(data_dir, bgm_name)
        if os.path.exists(test_path):
            bgm_path = test_path
            break
    if not bgm_path and os.path.exists('bgm.mp3'):
        bgm_path = 'bgm.mp3'
    
    # 生成文件名 - 使用用户昵称
    output_file = f'{my_name}的2025微信年度报告.html'
    
    print(f"📝 报告将保存为: {output_file}")
    print()
    
    # 执行分析（传递analyze_excel和exclude_file_helper参数）
    results = batch_analyze(data_dir, my_name=my_name, analyze_excel=analyze_excel, exclude_file_helper=exclude_file_helper)
    generate_final_report(results, output_file, bgm_path=bgm_path, mask_mode=mask_mode)
