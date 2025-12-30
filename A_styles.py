# -*- coding: utf-8 -*-
"""
report_styles.py - CSS样式模块
所有报告的CSS样式定义
"""

def get_css_styles():
    """返回所有CSS样式"""
    return '''
:root {
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
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{
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
}

/* 粒子背景 */
#particles{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0}
.particle{position:absolute;border-radius:50%;animation:float-particle linear infinite;opacity:0}
@keyframes float-particle{
    0%{transform:translateY(100vh) scale(0);opacity:0}
    10%{opacity:1}
    90%{opacity:1}
    100%{transform:translateY(-100vh) scale(1);opacity:0}
}

/* 星星背景 */
.stars{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0}
.star{position:absolute;background:#fff;border-radius:50%;animation:twinkle ease-in-out infinite}
@keyframes twinkle{0%,100%{opacity:0.3;transform:scale(1)}50%{opacity:1;transform:scale(1.2)}}

/* 流动线条背景 - 增强版 */
.flowing-lines{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;overflow:hidden;opacity:0.25}
.flowing-line{
    position:absolute;
    height:1px;
    background:linear-gradient(90deg,transparent 0%,var(--pink) 20%,var(--cyan) 50%,var(--purple) 80%,transparent 100%);
    animation:flow-line linear infinite;
    filter:blur(0.5px);
    box-shadow:0 0 8px rgba(255,107,157,0.3), 0 0 15px rgba(78,205,196,0.2);
}
@keyframes flow-line{
    0%{transform:translateX(-100%) rotate(var(--angle))}
    100%{transform:translateX(100vw) rotate(var(--angle))}
}

/* 网格线背景 */
.grid-bg{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;
    background-image:
        linear-gradient(rgba(255,107,157,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,107,157,0.03) 1px, transparent 1px),
        linear-gradient(rgba(78,205,196,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(78,205,196,0.02) 1px, transparent 1px);
    background-size: 100px 100px, 100px 100px, 20px 20px, 20px 20px;
    background-position: -1px -1px, -1px -1px, -1px -1px, -1px -1px;
}

/* 光晕效果 - 增强版 */
.glow-orbs{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;overflow:hidden}
.glow-orb{
    position:absolute;
    border-radius:50%;
    filter:blur(100px);
    animation:float-orb 25s ease-in-out infinite;
    mix-blend-mode:screen;
}
@keyframes float-orb{
    0%,100%{transform:translate(0,0) scale(1);opacity:0.6}
    25%{transform:translate(80px,-50px) scale(1.2);opacity:0.8}
    50%{transform:translate(-30px,80px) scale(0.9);opacity:0.5}
    75%{transform:translate(-80px,-30px) scale(1.15);opacity:0.7}
}

/* 烟花 */
.firework{position:fixed;pointer-events:none;z-index:1000}
.spark{position:absolute;border-radius:50%;animation:spark-fly 1s ease-out forwards}
@keyframes spark-fly{
    0%{transform:translate(0,0) scale(1);opacity:1}
    100%{transform:translate(var(--tx),var(--ty)) scale(0);opacity:0}
}

/* 动画 */
@keyframes fadeUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
@keyframes glow{0%,100%{filter:drop-shadow(0 0 20px var(--pink))}50%{filter:drop-shadow(0 0 40px var(--cyan))}}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}

/* 导航 - 改进移动端 */
.nav{position:fixed;top:0;left:0;right:0;background:rgba(10,10,26,0.95);backdrop-filter:blur(10px);z-index:100;padding:8px 15px;display:flex;justify-content:center;gap:6px;flex-wrap:wrap}
.nav a{color:var(--dim);text-decoration:none;padding:6px 12px;border-radius:20px;font-size:12px;transition:all 0.3s;white-space:nowrap}
.nav a:hover,.nav a.active{background:var(--pink);color:#fff}

/* 开场页 */
.hero{min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;position:relative;z-index:1;padding:80px 20px 20px}
.hero-year{font-size:clamp(60px,18vw,160px);font-weight:900;background:linear-gradient(135deg,var(--pink),var(--cyan),var(--yellow));-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:glow 4s ease-in-out infinite}
.hero-sub{font-size:clamp(14px,3vw,22px);color:var(--dim);margin:15px 0 40px}
.hero-stats{display:flex;gap:clamp(15px,4vw,50px);flex-wrap:wrap;justify-content:center}
.hero-stat{text-align:center;animation:fadeUp 0.8s ease-out forwards;opacity:0}
.hero-stat:nth-child(1){animation-delay:0.2s}.hero-stat:nth-child(2){animation-delay:0.3s}.hero-stat:nth-child(3){animation-delay:0.4s}.hero-stat:nth-child(4){animation-delay:0.5s}.hero-stat:nth-child(5){animation-delay:0.6s}
.hero-stat-val{font-size:clamp(28px,7vw,52px);font-weight:800;background:linear-gradient(135deg,var(--cyan),var(--yellow));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero-stat-lbl{font-size:12px;color:var(--dim);margin-top:5px}
.scroll-hint{position:absolute;bottom:30px;color:var(--dim);font-size:13px;animation:pulse 2s infinite}

/* 打字机效果 */
.hero-slogan{font-size:clamp(16px,4vw,24px);color:var(--cyan);margin:20px 0 30px;min-height:36px;font-weight:500}
.hero-slogan .cursor{display:inline-block;width:2px;height:1em;background:var(--pink);margin-left:2px;animation:blink 1s infinite}
@keyframes blink{0%,50%{opacity:1}51%,100%{opacity:0}}

/* 12月热力图 - 改进布局 */
.heatmap-section{padding:40px 0}
.heatmap-title{font-size:18px;font-weight:600;text-align:center;margin-bottom:25px;color:var(--txt)}
.heatmap-grid{
    display:grid;
    grid-template-columns:repeat(4, 1fr);
    gap:15px;
    max-width:500px;
    margin:0 auto;
    padding:0 20px;
}
.heatmap-month{text-align:center;cursor:pointer;transition:transform 0.3s}
.heatmap-month:hover{transform:scale(1.05)}
.heatmap-bar{
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
}
.heatmap-bar span{font-size:13px;color:rgba(255,255,255,0.9);font-weight:700}
.heatmap-label{font-size:13px;color:var(--dim);font-weight:500}
.heatmap-tooltip{position:absolute;bottom:100%;left:50%;transform:translateX(-50%);background:var(--bg3);padding:10px 14px;border-radius:10px;font-size:12px;white-space:nowrap;opacity:0;pointer-events:none;transition:opacity 0.3s;z-index:10;border:1px solid rgba(255,107,157,0.3)}
.heatmap-month:hover .heatmap-tooltip{opacity:1}

/* 分享卡片 */
.share-card{max-width:400px;margin:40px auto;background:linear-gradient(135deg,var(--bg2),var(--bg3));border-radius:20px;padding:30px;text-align:center;border:1px solid rgba(255,107,157,0.3);position:relative;overflow:hidden}
.share-card::before{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:linear-gradient(45deg,transparent,rgba(255,107,157,0.03),transparent);animation:shine 3s infinite}
@keyframes shine{0%{transform:translateX(-100%) rotate(45deg)}100%{transform:translateX(100%) rotate(45deg)}}
.share-card-title{font-size:28px;font-weight:800;background:linear-gradient(135deg,var(--pink),var(--cyan));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:15px}
.share-card-year{font-size:14px;color:var(--dim);margin-bottom:20px}
.share-card-stats{display:grid;grid-template-columns:repeat(2,1fr);gap:15px;margin-bottom:20px}
.share-card-stat{padding:15px;background:rgba(255,255,255,0.05);border-radius:12px}
.share-card-stat-val{font-size:24px;font-weight:700;color:var(--cyan)}
.share-card-stat-lbl{font-size:11px;color:var(--dim);margin-top:5px}
.share-card-footer{font-size:12px;color:var(--dim);padding-top:15px;border-top:1px solid rgba(255,255,255,0.1)}

/* 年度来信 - 信封拆开动画 */
.letter-wrapper{max-width:500px;margin:40px auto;perspective:1000px}
.envelope{
    position:relative;
    width:100%;
    padding-top:70%;
    cursor:pointer;
    transform-style:preserve-3d;
}
.envelope-back{
    position:absolute;
    top:0;left:0;right:0;bottom:0;
    background:linear-gradient(135deg,#2a2a3e,#1f1f30);
    border-radius:16px;
    border:2px solid rgba(255,107,157,0.3);
    box-shadow:0 10px 40px rgba(0,0,0,0.3);
}
.envelope-flap{
    position:absolute;
    top:0;left:0;right:0;
    height:50%;
    background:linear-gradient(180deg,var(--pink),var(--purple));
    clip-path:polygon(0 0, 50% 100%, 100% 0);
    transform-origin:top center;
    transition:transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    z-index:10;
    border-radius:16px 16px 0 0;
}
.envelope.opened .envelope-flap{
    transform:rotateX(-180deg);
}
.envelope-seal{
    position:absolute;
    top:calc(50% - 25px);
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
}
.envelope.opened .envelope-seal{
    opacity:0;
    transform:translateX(-50%) scale(0);
}
.envelope-hint{
    position:absolute;
    bottom:15%;
    left:50%;
    transform:translateX(-50%);
    color:var(--dim);
    font-size:12px;
    animation:pulse 2s infinite;
    transition:opacity 0.3s;
}
.envelope.opened .envelope-hint{opacity:0}

/* 信纸 */
.letter-paper{
    position:absolute;
    top:10%;left:5%;right:5%;bottom:5%;
    background:linear-gradient(135deg,#1a1a24,#252532);
    border-radius:12px;
    padding:20px;
    transform:translateY(100%);
    transition:transform 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.3s;
    overflow:hidden;
}
.envelope.opened .letter-paper{
    transform:translateY(0);
}
.letter-header{
    background:linear-gradient(135deg,var(--pink),var(--purple));
    margin:-20px -20px 20px -20px;
    padding:15px 20px;
    display:flex;
    align-items:center;
    gap:10px;
}
.letter-icon{font-size:24px}
.letter-title{font-size:16px;font-weight:600;color:#fff}
.letter-content{font-size:14px;line-height:2;color:rgba(255,255,255,0.85);max-height:200px;overflow-y:auto}
.letter-content strong{color:var(--cyan)}
.letter-stamp{position:absolute;bottom:15px;right:15px;font-size:36px;font-weight:900;color:rgba(255,107,157,0.15);transform:rotate(-15deg)}

/* 年度聊天颜色 */
.colors-section{max-width:400px;margin:40px auto;text-align:center}
.colors-orb{width:150px;height:150px;border-radius:50%;margin:0 auto 25px;box-shadow:0 10px 40px rgba(0,0,0,0.3);animation:color-pulse 4s ease-in-out infinite}
@keyframes color-pulse{0%,100%{transform:scale(1);box-shadow:0 10px 40px rgba(0,0,0,0.3)}50%{transform:scale(1.05);box-shadow:0 15px 50px rgba(255,107,157,0.3)}}
.colors-title{font-size:18px;font-weight:600;margin-bottom:20px;color:var(--txt)}
.colors-list{display:flex;flex-direction:column;gap:12px;text-align:left;padding:0 20px}
.color-item{display:flex;align-items:center;gap:12px;padding:10px 15px;background:rgba(255,255,255,0.03);border-radius:10px}
.color-dot{width:16px;height:16px;border-radius:50%;flex-shrink:0}
.color-info{flex:1}
.color-name{font-size:14px;font-weight:500;color:var(--txt)}
.color-name span{color:var(--dim);font-weight:400;margin-left:8px}
.color-desc{font-size:11px;color:var(--dim);margin-top:2px}
.colors-subtitle{font-size:14px;color:var(--dim);margin-bottom:15px}
.colors-subtitle span{font-weight:600}
.color-insight{font-size:13px;color:var(--cyan);margin-bottom:20px;padding:12px 16px;background:rgba(78,205,196,0.1);border-radius:10px;border-left:3px solid var(--cyan)}

/* 用户画像卡片 */
.profile-card{max-width:450px;margin:40px auto;background:linear-gradient(135deg,var(--bg2),var(--bg3));border-radius:20px;overflow:hidden;border:1px solid rgba(168,85,247,0.3);position:relative}
.profile-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--pink),var(--purple),var(--cyan))}
.profile-header{background:linear-gradient(135deg,rgba(168,85,247,0.2),rgba(78,205,196,0.1));padding:18px 25px;display:flex;align-items:center;gap:12px}
.profile-icon{font-size:26px}
.profile-title{font-size:18px;font-weight:700;color:var(--txt)}
.profile-content{padding:25px}
.profile-section{margin-bottom:22px}
.profile-section:last-child{margin-bottom:0}
.profile-label{font-size:12px;color:var(--dim);margin-bottom:8px;text-transform:uppercase;letter-spacing:1px}
.profile-value{font-size:22px;font-weight:700;color:var(--txt);margin-bottom:8px}
.profile-value.style-value{font-size:18px;color:var(--cyan)}
.profile-confidence{display:flex;align-items:center;gap:12px}
.confidence-bar{flex:1;height:6px;background:var(--bg1);border-radius:3px;overflow:hidden}
.confidence-fill{height:100%;background:linear-gradient(90deg,var(--purple),var(--pink));border-radius:3px;transition:width 1.5s ease-out}
.confidence-text{font-size:11px;color:var(--dim);min-width:70px}
.profile-tags{display:flex;flex-wrap:wrap;gap:8px}
.profile-tag{padding:6px 12px;background:rgba(78,205,196,0.15);border:1px solid rgba(78,205,196,0.3);border-radius:20px;font-size:12px;color:var(--cyan)}
.personality-tag{padding:6px 12px;background:rgba(255,107,157,0.15);border:1px solid rgba(255,107,157,0.3);border-radius:20px;font-size:12px;color:var(--pink)}
.profile-footer{padding:15px 25px;background:rgba(0,0,0,0.2);font-size:11px;color:var(--dim);text-align:center}

/* 流星雨效果 */
.meteors{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:5;overflow:hidden}
.meteor{
    position:absolute;
    height:2px;
    border-radius:50%;
    transform:rotate(-35deg);
    transform-origin:left center;
    animation:meteor-fall linear forwards;
}
.meteor::before{
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
}
@keyframes meteor-fall{
    0%{transform:translate(0, 0) rotate(-35deg);opacity:1}
    70%{opacity:1}
    100%{transform:translate(-600px, 400px) rotate(-35deg);opacity:0}
}

/* 好友默契度 - 逐条动画显示 */
.chemistry-list{display:flex;flex-direction:column;gap:15px;max-width:600px;margin:0 auto}
.chemistry-card{
    display:flex;
    align-items:center;
    gap:15px;
    background:var(--bg2);
    border-radius:16px;
    padding:20px;
    border:1px solid var(--bg3);
    opacity:0;
    transform:translateX(-30px);
    transition:all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.chemistry-card.visible{
    opacity:1;
    transform:translateX(0);
}
/* 逐条延迟动画 */
.chemistry-card:nth-child(1){transition-delay:0.1s}
.chemistry-card:nth-child(2){transition-delay:0.3s}
.chemistry-card:nth-child(3){transition-delay:0.5s}
.chemistry-card:nth-child(4){transition-delay:0.7s}
.chemistry-card:nth-child(5){transition-delay:0.9s}
.chemistry-rank{font-size:24px;font-weight:800;color:var(--yellow);min-width:50px;text-align:center}
.chemistry-info{flex:1}
.chemistry-name{font-size:16px;font-weight:600;color:var(--txt);margin-bottom:4px}
.chemistry-title{font-size:13px;color:var(--pink);margin-bottom:6px}
.chemistry-details{font-size:11px;color:var(--dim)}
.chemistry-score{position:relative;width:60px;height:60px}
.chemistry-ring{width:100%;height:100%;transform:rotate(-90deg)}
.chemistry-ring-bg{fill:none;stroke:var(--bg3);stroke-width:3}
.chemistry-ring-fill{fill:none;stroke-width:3;stroke-linecap:round;transition:stroke-dasharray 1.5s ease-out}
.chemistry-score-val{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:16px;font-weight:700;color:var(--txt)}

/* 滚动淡入增强 */
.scroll-reveal{opacity:0;transform:translateY(30px);transition:opacity 0.8s ease-out, transform 0.8s ease-out}
.scroll-reveal.revealed{opacity:1;transform:translateY(0)}
.scroll-reveal.delay-1{transition-delay:0.1s}
.scroll-reveal.delay-2{transition-delay:0.2s}
.scroll-reveal.delay-3{transition-delay:0.3s}

/* 容器 */
.container{max-width:1400px;margin:0 auto;padding:0 15px}
.section{padding:60px 0;position:relative;z-index:1}
.section-title{font-size:clamp(20px,5vw,32px);font-weight:700;text-align:center;margin-bottom:40px;background:linear-gradient(135deg,var(--pink),var(--cyan));-webkit-background-clip:text;-webkit-text-fill-color:transparent}

/* 排行榜 */
.rankings-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:20px}
.ranking-card{background:var(--bg2);border-radius:16px;padding:20px;border:1px solid var(--bg3)}
.ranking-title{font-size:16px;font-weight:600;margin-bottom:10px}
.ranking-stats{font-size:11px;color:var(--dim);padding:10px;background:var(--bg3);border-radius:8px;margin-bottom:15px}
.ranking-stats strong{color:var(--cyan)}
.rank-item{display:flex;align-items:center;padding:8px 0;border-bottom:1px solid var(--bg3);animation:fadeUp 0.4s ease-out forwards;animation-delay:var(--delay);opacity:0}
.rank-pos{width:28px;font-weight:600}
.rank-name{width:70px;font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rank-bar{flex:1;height:5px;background:var(--bg3);border-radius:3px;margin:0 10px;overflow:hidden}
.rank-fill{height:100%;background:linear-gradient(90deg,var(--pink),var(--cyan));border-radius:3px;transition:width 4s cubic-bezier(0.4, 0, 0.2, 1)}
.rank-val{font-size:11px;color:var(--dim);min-width:60px;text-align:right}
.rank-more{text-align:center;color:var(--dim);font-size:11px;padding:10px 0}
.rank-hidden{display:none}
.rank-hidden.show{display:block}
.expand-btn{display:block;width:100%;padding:8px;margin-top:5px;background:var(--bg3);border:none;border-radius:8px;color:var(--dim);font-size:11px;cursor:pointer;transition:all 0.3s}
.expand-btn:hover{background:var(--pink);color:#fff}
.expand-btn.expanded{background:var(--bg3)}

/* 智能分析文案 */
.insights{background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(78,205,196,0.1));border-radius:16px;padding:25px;margin-bottom:40px;border:1px solid rgba(255,107,157,0.2)}
.insights-title{font-size:18px;font-weight:700;margin-bottom:15px;color:var(--pink)}

/* 文字渐入动画 */
.text-animate{opacity:0;transform:translateY(20px);transition:opacity 0.8s ease-out, transform 0.8s ease-out}
.text-animate.text-visible{opacity:1;transform:translateY(0)}
.insight-item{padding:10px 15px;margin:8px 0;background:rgba(255,255,255,0.05);border-radius:10px;font-size:14px;line-height:1.6;border-left:3px solid var(--cyan)}
.insight-item strong{color:var(--yellow)}

/* 群聊排行榜（群名一行+进度条一行） */
.rank-item-group{padding:12px 0;border-bottom:1px solid var(--bg3);animation:fadeUp 0.4s ease-out forwards;animation-delay:var(--delay);opacity:0}
.rank-row-name{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.rank-name-full{flex:1;font-size:13px;font-weight:500;word-break:break-all}
.rank-row-bar{padding-left:38px}
.rank-bar-full{height:6px;background:var(--bg3);border-radius:3px;overflow:hidden}

/* 好友分组 */
.friend-groups{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:15px;margin-bottom:40px}
.friend-group{background:var(--bg2);border-radius:12px;padding:20px;border-left:4px solid var(--pink)}
.friend-group:nth-child(1){border-color:gold}.friend-group:nth-child(2){border-color:var(--yellow)}.friend-group:nth-child(3){border-color:var(--cyan)}.friend-group:nth-child(4){border-color:var(--dim)}
.fg-title{font-size:15px;font-weight:600}
.fg-count{font-size:32px;font-weight:800;color:var(--cyan);margin:8px 0}
.fg-list{font-size:11px;color:var(--dim);line-height:1.8}

/* 私聊卡片 */
.chat-card,.group-card{background:var(--bg2);border-radius:12px;margin-bottom:10px;overflow:hidden;border:1px solid var(--bg3)}
.chat-header,.group-header{padding:15px 20px;display:flex;align-items:center;gap:12px;cursor:pointer;transition:background 0.3s}
.chat-header:hover,.group-header:hover{background:var(--bg3)}
.chat-rank,.group-rank{font-size:20px;font-weight:800;color:var(--yellow);min-width:45px}
.chat-name,.group-name{font-size:15px;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.chat-brief,.group-brief{font-size:12px;color:var(--dim)}
.chat-brief i,.group-brief i{color:var(--cyan);font-style:normal}
.chat-toggle{color:var(--dim);transition:transform 0.3s}
.chat-card.open .chat-toggle,.group-card.open .chat-toggle{transform:rotate(180deg)}
.chat-body{max-height:0;overflow:hidden;transition:max-height 0.4s ease-out}
.chat-card.open .chat-body,.group-card.open .chat-body{max-height:2000px}

/* 数据网格 */
.data-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;padding:15px}
.data-card{background:var(--bg3);border-radius:10px;padding:15px}
.card-title{font-size:13px;font-weight:600;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.1)}

/* 对比 */
.versus{display:flex;align-items:center;justify-content:space-around;margin:15px 0}
.vs-item{text-align:center}
.vs-val{font-size:28px;font-weight:800}
.vs-val.time{font-size:22px}
.vs-item.them .vs-val{color:var(--them)}.vs-item.me .vs-val{color:var(--me)}
.vs-pct{font-size:16px;font-weight:600;margin:5px 0}
.vs-label{font-size:11px;color:var(--dim)}
.vs-mid{color:var(--dim);font-size:18px}
.bar-compare{height:6px;border-radius:3px;display:flex;overflow:hidden;background:var(--bg1)}
.bar-them,.bar-me{transition:width 4s cubic-bezier(0.4, 0, 0.2, 1)}
.bar-them{background:linear-gradient(90deg,var(--them),#ff8fab)}.bar-me{background:linear-gradient(90deg,#3dbdb3,var(--me))}

/* 表格 */
table{width:100%;font-size:11px;border-collapse:collapse}
th,td{padding:6px 4px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.05)}
th{color:var(--dim);font-weight:400}
td:first-child,th:first-child{text-align:left}
.them{color:var(--them)}.me{color:var(--me)}

/* 统计行 */
.stat-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(60px,1fr));gap:8px;margin-top:10px}
.stat-box{text-align:center;padding:10px 5px;background:var(--bg1);border-radius:8px}
.stat-box.them{border:1px solid rgba(255,107,157,0.3)}.stat-box.me{border:1px solid rgba(78,205,196,0.3)}
.stat-num{font-size:18px;font-weight:700}
.stat-box.them .stat-num{color:var(--them)}.stat-box.me .stat-num{color:var(--me)}
.stat-lbl{font-size:9px;color:var(--dim);margin-top:3px}

/* 迷你洞察 */
.mini-insight{font-size:10px;color:var(--dim);margin-top:10px;padding:8px;background:var(--bg1);border-radius:6px}
.mini-insight b{color:var(--yellow)}
.dist-mini{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;font-size:10px;color:var(--dim)}
.dist-mini b.them{color:var(--them)}.dist-mini b.me{color:var(--me)}

/* 群聊统计 */
.group-stats{display:flex;flex-wrap:wrap;gap:15px;padding:15px}
.gstat{text-align:center;min-width:60px}
.gstat-val{font-size:24px;font-weight:700;color:var(--cyan)}
.gstat-lbl{font-size:10px;color:var(--dim);margin-top:4px}
.talkers-section{padding:15px}
.section-subtitle{font-size:13px;font-weight:600;margin-bottom:10px;color:var(--txt)}
.talkers-list{display:flex;flex-wrap:wrap;gap:8px}
.talker{background:var(--bg3);padding:6px 12px;border-radius:15px;font-size:11px;display:flex;align-items:center;gap:6px}
.talker-rank{color:var(--yellow);font-weight:600}
.talker-name{color:var(--txt)}
.talker-count{color:var(--dim)}
.controls{text-align:center;margin:20px 0}
.btn{background:var(--bg3);border:1px solid var(--pink);color:var(--txt);padding:10px 25px;border-radius:25px;cursor:pointer;font-size:13px;margin:5px;transition:all 0.3s}
.btn:hover{background:var(--pink)}

/* 页脚 */
footer{text-align:center;padding:60px 20px;color:var(--dim);position:relative;z-index:1}

/* 结语页面增强 */
.ending-section{min-height:80vh;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:60px 20px;position:relative;z-index:1}
.ending-emoji{font-size:70px;margin-bottom:25px;animation:pulse 2s infinite}
.ending-title{font-size:clamp(28px,7vw,48px);font-weight:800;background:linear-gradient(135deg,var(--pink),var(--cyan),var(--yellow));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:30px}
.ending-highlights{
    font-size:clamp(14px,3vw,17px);
    color:rgba(255,255,255,0.85);
    line-height:2.2;
    max-width:600px;
    margin-bottom:30px;
    padding:25px 30px;
    background:rgba(255,255,255,0.03);
    border-radius:16px;
    border:1px solid rgba(255,107,157,0.15);
}
.ending-highlights strong{color:var(--cyan);font-weight:600}
.ending-reflection{
    font-size:clamp(16px,4vw,20px);
    color:var(--pink);
    font-style:italic;
    margin-bottom:25px;
    max-width:500px;
    opacity:0.9;
}
.ending-wish{
    font-size:clamp(14px,3vw,16px);
    color:var(--dim);
    margin-bottom:20px;
    max-width:500px;
    line-height:1.8;
}
.ending-signature{
    font-size:13px;
    color:var(--dim);
    margin-top:15px;
    opacity:0.7;
}

/* 响应式 */
@media(max-width:768px){
    /* 导航栏 - 移动端优化 */
    .nav{
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
    }
    .nav a{padding:8px 8px;font-size:10px;border-radius:12px}
    
    /* 开场页留出底部导航空间 */
    .hero{padding-top:20px;padding-bottom:80px}
    
    /* 热力图 - 移动端2行6列 */
    .heatmap-grid{grid-template-columns:repeat(3, 1fr);gap:10px;max-width:320px}
    .heatmap-bar{height:80px}
    .heatmap-label{font-size:11px}
    
    /* 数据网格 */
    .data-grid{grid-template-columns:1fr}
    .rankings-grid{grid-template-columns:1fr}
    .versus{flex-direction:column;gap:15px}.vs-mid{display:none}
    
    /* 各section底部留空 */
    .section{padding-bottom:80px}
    
    /* 用户画像卡片 */
    .profile-card{margin:20px 15px}
    .profile-value{font-size:18px}
    
    /* 年度来信 */
    .letter-card{margin:20px 15px}
    
    /* 默契度卡片 */
    .chemistry-card{padding:15px}
    .chemistry-score{width:50px;height:50px}
}

/* 更小屏幕 */
@media(max-width:480px){
    .nav a{padding:6px 6px;font-size:9px}
    .heatmap-grid{grid-template-columns:repeat(2, 1fr);max-width:240px}
    .hero-stats{gap:10px}
    .hero-stat-val{font-size:clamp(24px,6vw,40px)}
}

.empty{text-align:center;color:var(--dim);padding:40px}

/* 音乐控制按钮 - 可拖动 */
.music-btn{position:fixed;top:20px;right:20px;z-index:2001;width:50px;height:50px;border-radius:50%;background:rgba(255,107,157,0.4);border:none;cursor:grab;display:flex;align-items:center;justify-content:center;font-size:24px;box-shadow:0 4px 15px rgba(255,107,157,0.2);transition:background 0.3s;user-select:none;touch-action:none;backdrop-filter:blur(5px)}
.music-btn:active{cursor:grabbing}
.music-btn:hover{background:rgba(255,107,157,0.7)}
.music-btn.muted{background:rgba(102,102,102,0.4)}
.music-btn.dragging{transform:scale(1.1);box-shadow:0 8px 25px rgba(255,107,157,0.4)}

/* 截图/生成长图按钮 - 放在页面底部 */
.screenshot-btn{display:inline-flex;padding:16px 32px;border-radius:30px;background:linear-gradient(135deg,var(--pink),var(--purple));border:none;cursor:pointer;color:#fff;font-size:16px;font-weight:600;box-shadow:0 4px 20px rgba(168,85,247,0.4);transition:all 0.3s;align-items:center;gap:10px;margin:20px auto}
.screenshot-btn:hover{transform:translateY(-3px);box-shadow:0 8px 30px rgba(168,85,247,0.6)}
.screenshot-btn:active{transform:translateY(0)}
.screenshot-btn svg{width:20px;height:20px}
.screenshot-btn .spin{animation:spin 1s linear infinite}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}

/* 结束页 */
.ending-section{min-height:60vh;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:60px 20px;position:relative;z-index:1}
.ending-title{font-size:clamp(24px,6vw,42px);font-weight:800;background:linear-gradient(135deg,var(--pink),var(--cyan),var(--yellow));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:15px}
.ending-subtitle{font-size:clamp(14px,3vw,18px);color:var(--dim);margin-bottom:40px;max-width:500px;line-height:1.8}
.ending-emoji{font-size:60px;margin-bottom:30px;animation:pulse 2s infinite}
'''
