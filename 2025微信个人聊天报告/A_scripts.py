# -*- coding: utf-8 -*-
"""
report_scripts.py - JavaScript代码模块
所有报告的JS交互代码
"""

def get_js_scripts():
    """返回所有JavaScript代码"""
    return '''
// 创建流动线条
function createFlowingLines(){
    const container=document.getElementById('flowingLines');
    if(!container) return;
    for(let i=0;i<8;i++){
        const line=document.createElement('div');
        line.className='flowing-line';
        const angle = (Math.random() - 0.5) * 30;
        line.style.cssText=`
            top:${Math.random()*100}%;
            width:${Math.random()*300+200}px;
            --angle:${angle}deg;
            animation-duration:${Math.random()*15+10}s;
            animation-delay:${Math.random()*10}s;
            opacity:${Math.random()*0.5+0.3};
        `;
        container.appendChild(line);
    }
}

// 创建光晕效果
function createGlowOrbs(){
    const container=document.getElementById('glowOrbs');
    if(!container) return;
    const colors=[
        'rgba(255,107,157,0.15)',
        'rgba(78,205,196,0.12)',
        'rgba(168,85,247,0.1)',
        'rgba(255,211,61,0.08)'
    ];
    for(let i=0;i<4;i++){
        const orb=document.createElement('div');
        orb.className='glow-orb';
        orb.style.cssText=`
            left:${Math.random()*80}%;
            top:${Math.random()*80}%;
            width:${Math.random()*300+200}px;
            height:${Math.random()*300+200}px;
            background:${colors[i%colors.length]};
            animation-delay:${i*5}s;
        `;
        container.appendChild(orb);
    }
}

// 创建流星雨效果（替代漂浮emoji）
function createMeteors(){
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
    
    function createMeteor(){
        if(document.hidden) return;
        
        const meteor=document.createElement('div');
        meteor.className='meteor';
        
        // 随机参数
        const startX = Math.random() * 100 + 20;  // 起始X位置（20%-120%）
        const startY = -10;  // 从顶部上方开始
        const length = Math.random() * 80 + 40;   // 流星长度 40-120px
        const duration = Math.random() * 1.5 + 0.8;  // 持续时间 0.8-2.3秒
        const color = colors[Math.floor(Math.random() * colors.length)];
        const tailColor = color.replace(/[\d.]+\)$/, '0)');  // 尾部透明
        
        meteor.style.cssText=`
            left: ${startX}%;
            top: ${startY}%;
            width: ${length}px;
            height: 2px;
            background: linear-gradient(90deg, ${tailColor}, ${color});
            box-shadow: 0 0 6px ${color}, 0 0 12px ${color};
            animation-duration: ${duration}s;
        `;
        
        container.appendChild(meteor);
        
        // 动画结束后移除
        setTimeout(()=>meteor.remove(), duration * 1000 + 100);
    }
    
    // 随机间隔生成流星（比emoji更频繁但更短暂）
    setInterval(()=>{
        if(Math.random() > 0.4) createMeteor();  // 60%概率生成
    }, 800);
    
    // 初始生成几颗
    for(let i=0; i<3; i++){
        setTimeout(createMeteor, i * 300);
    }
}

// 创建星星
function createStars(){
    const container=document.getElementById('stars');
    for(let i=0;i<100;i++){
        const star=document.createElement('div');
        star.className='star';
        star.style.cssText=`
            left:${Math.random()*100}%;
            top:${Math.random()*100}%;
            width:${Math.random()*2+1}px;
            height:${Math.random()*2+1}px;
            animation-duration:${Math.random()*3+2}s;
            animation-delay:${Math.random()*3}s;
        `;
        container.appendChild(star);
    }
}

// 创建粒子
function createParticles(){
    const container=document.getElementById('particles');
    const colors=['#FF6B9D','#4ECDC4','#FFD93D','#A855F7'];
    setInterval(()=>{
        if(document.hidden)return;
        const p=document.createElement('div');
        p.className='particle';
        const size=Math.random()*6+2;
        p.style.cssText=`
            left:${Math.random()*100}%;
            width:${size}px;
            height:${size}px;
            background:${colors[Math.floor(Math.random()*colors.length)]};
            animation-duration:${Math.random()*10+10}s;
        `;
        container.appendChild(p);
        setTimeout(()=>p.remove(),20000);
    },300);
}

// 烟花效果
function createFirework(x,y){
    const colors=['#FF6B9D','#4ECDC4','#FFD93D','#A855F7','#fff'];
    const fw=document.createElement('div');
    fw.className='firework';
    fw.style.left=x+'px';
    fw.style.top=y+'px';
    document.body.appendChild(fw);
    
    for(let i=0;i<30;i++){
        const spark=document.createElement('div');
        spark.className='spark';
        const angle=Math.random()*Math.PI*2;
        const distance=Math.random()*100+50;
        spark.style.cssText=`
            width:${Math.random()*4+2}px;
            height:${Math.random()*4+2}px;
            background:${colors[Math.floor(Math.random()*colors.length)]};
            --tx:${Math.cos(angle)*distance}px;
            --ty:${Math.sin(angle)*distance}px;
        `;
        fw.appendChild(spark);
    }
    setTimeout(()=>fw.remove(),1000);
}

// 随机烟花
function randomFireworks(){
    setInterval(()=>{
        if(document.hidden||Math.random()>0.3)return;
        createFirework(Math.random()*window.innerWidth,Math.random()*window.innerHeight*0.5);
    },2000);
}

// 数字滚动
function animateNumbers(){
    const observer=new IntersectionObserver((entries)=>{
        entries.forEach(entry=>{
            if(entry.isIntersecting){
                const el=entry.target;
                if(el.dataset.animated)return;
                el.dataset.animated='1';
                const target=parseFloat(el.dataset.val)||0;
                const duration=1200;
                const start=performance.now();
                function update(now){
                    const progress=Math.min((now-start)/duration,1);
                    const eased=1-Math.pow(1-progress,3);
                    el.textContent=Math.floor(target*eased).toLocaleString();
                    if(progress<1)requestAnimationFrame(update);
                    else el.textContent=target.toLocaleString();
                }
                requestAnimationFrame(update);
            }
        });
    },{threshold:0.3});
    document.querySelectorAll('.num').forEach(n=>observer.observe(n));
}

// 进度条动画
function animateBars(){
    const observer=new IntersectionObserver((entries)=>{
        entries.forEach(entry=>{
            if(entry.isIntersecting){
                const bar=entry.target;
                const w=bar.style.width;
                bar.style.width='0';
                setTimeout(()=>bar.style.width=w,100);
            }
        });
    },{threshold:0.3});
    document.querySelectorAll('.rank-fill,.bar-them,.bar-me').forEach(b=>observer.observe(b));
}

// 卡片折叠
function toggleCard(header){
    header.parentElement.classList.toggle('open');
}
function expandAll(type){
    document.querySelectorAll(type==='chat'?'.chat-card':'.group-card').forEach(c=>c.classList.add('open'));
}
function collapseAll(type){
    document.querySelectorAll(type==='chat'?'.chat-card':'.group-card').forEach(c=>c.classList.remove('open'));
}

// 导航高亮
function updateNav(){
    const sections=['hero','heatmap','chat-colors','user-profile','chemistry','private-rank','group-rank','ending'];
    window.addEventListener('scroll',()=>{
        let current='';
        sections.forEach(id=>{
            const s=document.getElementById(id);
            if(s&&s.getBoundingClientRect().top<=150)current=id;
        });
        document.querySelectorAll('.nav a').forEach(a=>{
            a.classList.toggle('active',a.getAttribute('href')==='#'+current);
        });
    });
}

// 点击烟花
document.addEventListener('click',e=>{
    if(e.target.closest('.nav,.btn,.chat-header,.group-header,.music-btn'))return;
    createFirework(e.clientX,e.clientY);
});

// ========== 背景音乐控制 ==========
let isMuted = true;
const bgm = document.getElementById('bgm');
const musicBtn = document.getElementById('musicBtn');

function toggleMusic() {
    if (isMuted) {
        bgm.play().catch(e => console.log('音乐播放失败'));
        musicBtn.textContent = '🎵';
        musicBtn.classList.remove('muted');
    } else {
        bgm.pause();
        musicBtn.textContent = '🔇';
        musicBtn.classList.add('muted');
    }
    isMuted = !isMuted;
}

// 展开/收起排行榜
function toggleRank(btn) {
    const hidden = btn.previousElementSibling;
    if (hidden && hidden.classList.contains('rank-hidden')) {
        hidden.classList.toggle('show');
        if (hidden.classList.contains('show')) {
            btn.textContent = '收起 ▲';
            btn.classList.add('expanded');
        } else {
            btn.textContent = '展开更多 ▼';
            btn.classList.remove('expanded');
        }
    }
}

// 文字渐入动画
function animateText() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('text-visible');
            }
        });
    }, {threshold: 0.1});
    document.querySelectorAll('.insight-item, .ranking-title, .ranking-stats, .section-title, .fg-title').forEach(el => {
        el.classList.add('text-animate');
        observer.observe(el);
    });
    
    // 滚动淡入动画 - 更多元素
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
            }
        });
    }, {threshold: 0.1});
    document.querySelectorAll('.letter-wrapper, .colors-section, .share-card, .heatmap-grid, .profile-card').forEach(el => {
        el.classList.add('scroll-reveal');
        revealObserver.observe(el);
    });
    
    // 默契度卡片逐条显示动画
    const chemistryObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // 获取父容器下的所有卡片
                const cards = entry.target.querySelectorAll('.chemistry-card');
                cards.forEach((card, index) => {
                    setTimeout(() => {
                        card.classList.add('visible');
                    }, index * 200);  // 每张卡片延迟200ms
                });
                chemistryObserver.unobserve(entry.target);  // 只触发一次
            }
        });
    }, {threshold: 0.2});
    
    const chemistryList = document.querySelector('.chemistry-list');
    if (chemistryList) {
        chemistryObserver.observe(chemistryList);
    }
}

// ========== 音乐按钮拖动功能 ==========
function initDraggable() {
    const btn = document.getElementById('musicBtn');
    let isDragging = false;
    let hasMoved = false;
    let startX, startY, initialX, initialY;
    
    btn.addEventListener('mousedown', startDrag);
    btn.addEventListener('touchstart', startDrag, {passive: false});
    
    function startDrag(e) {
        isDragging = true;
        hasMoved = false;
        btn.classList.add('dragging');
        
        if (e.type === 'touchstart') {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        } else {
            startX = e.clientX;
            startY = e.clientY;
        }
        
        const rect = btn.getBoundingClientRect();
        initialX = rect.left;
        initialY = rect.top;
        
        document.addEventListener('mousemove', drag);
        document.addEventListener('touchmove', drag, {passive: false});
        document.addEventListener('mouseup', stopDrag);
        document.addEventListener('touchend', stopDrag);
    }
    
    function drag(e) {
        if (!isDragging) return;
        e.preventDefault();
        
        let currentX, currentY;
        if (e.type === 'touchmove') {
            currentX = e.touches[0].clientX;
            currentY = e.touches[0].clientY;
        } else {
            currentX = e.clientX;
            currentY = e.clientY;
        }
        
        const deltaX = currentX - startX;
        const deltaY = currentY - startY;
        
        if (Math.abs(deltaX) > 5 || Math.abs(deltaY) > 5) {
            hasMoved = true;
        }
        
        let newX = initialX + deltaX;
        let newY = initialY + deltaY;
        
        newX = Math.max(0, Math.min(window.innerWidth - 50, newX));
        newY = Math.max(0, Math.min(window.innerHeight - 50, newY));
        
        btn.style.left = newX + 'px';
        btn.style.top = newY + 'px';
        btn.style.right = 'auto';
    }
    
    function stopDrag() {
        isDragging = false;
        btn.classList.remove('dragging');
        
        document.removeEventListener('mousemove', drag);
        document.removeEventListener('touchmove', drag);
        document.removeEventListener('mouseup', stopDrag);
        document.removeEventListener('touchend', stopDrag);
    }
    
    btn.addEventListener('click', (e) => {
        if (hasMoved) {
            e.preventDefault();
            e.stopPropagation();
        }
    }, true);
}

// ========== 生成长图功能 ==========
async function generateLongImage() {
    const btn = document.getElementById('screenshotBtn');
    const originalText = btn.innerHTML;
    
    btn.innerHTML = '<svg class="spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>生成中...';
    btn.disabled = true;
    
    try {
        if (typeof html2canvas === 'undefined') {
            await loadScript('https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js');
        }
        
        const fixedElements = document.querySelectorAll('.nav, .music-btn');
        fixedElements.forEach(el => el.style.display = 'none');
        
        const canvas = await html2canvas(document.body, {
            backgroundColor: '#0a0a0f',
            scale: 2,
            useCORS: true,
            logging: false,
            windowWidth: document.body.scrollWidth,
            windowHeight: document.body.scrollHeight
        });
        
        fixedElements.forEach(el => el.style.display = '');
        
        const link = document.createElement('a');
        link.download = '2025年度聊天报告.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
        
        btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>已保存!';
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }, 2000);
        
    } catch (err) {
        console.error('截图失败:', err);
        btn.innerHTML = '截图失败';
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }, 2000);
    }
}

function loadScript(src) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

// ========== 打字机效果 ==========
function typeWriter() {
    const slogans = [
        '总有一个人，值得你深夜回复',
        '每一条消息，都是一份心意',
        '2025，感谢有你的陪伴',
        '字里行间，皆是温暖'
    ];
    const slogan = slogans[Math.floor(Math.random() * slogans.length)];
    const el = document.getElementById('heroSlogan');
    if (!el) return;
    
    let i = 0;
    el.innerHTML = '<span class="cursor"></span>';
    
    function type() {
        if (i < slogan.length) {
            el.innerHTML = slogan.substring(0, i + 1) + '<span class="cursor"></span>';
            i++;
            setTimeout(type, 100);
        }
    }
    
    setTimeout(type, 800);
}

// 初始化
document.addEventListener('DOMContentLoaded',()=>{
    createStars();
    createFlowingLines();
    createGlowOrbs();
    createMeteors();  // 流星雨替代漂浮emoji
    createParticles();
    randomFireworks();
    animateNumbers();
    animateBars();
    animateText();
    updateNav();
    initDraggable();
    typeWriter();
    // 默认展开前3个
    document.querySelectorAll('.chat-card:nth-child(-n+3),.group-card:nth-child(-n+3)').forEach(c=>c.classList.add('open'));
    
    // 自动播放音乐
    setTimeout(() => {
        bgm.play().then(() => {
            isMuted = false;
            musicBtn.textContent = '🎵';
            musicBtn.classList.remove('muted');
        }).catch(e => {
            console.log('自动播放被阻止，需要用户交互');
        });
    }, 500);
});
'''
