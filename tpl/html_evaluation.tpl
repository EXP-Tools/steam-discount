<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <title>口碑殿堂 · Steam Discount</title>
%(head)s
</head>
<body data-board="evaluation">
  <a class="skip-link" href="#leaderboard">跳到榜单</a>
  <header class="site-header wrap">
    <a class="brand" href="discount.html" aria-label="Steam Discount 首页"><span class="brand-mark" aria-hidden="true">S<span>D</span></span><span>STEAM<span class="brand-sub">DISCOUNT / 游戏情报站</span></span></a>
    <div class="header-right"><span class="edition">THE PLAYER'S RADAR</span><a class="repo-link" href="https://github.com/EXP-Tools/steam-discount" target="_blank" rel="noopener noreferrer">GitHub <span aria-hidden="true">↗</span></a></div>
  </header>
  <main class="wrap">
    <section class="hero" aria-labelledby="page-title">
      <div class="hero-copy"><p class="eyebrow"><span></span> PLAYER APPROVED <i>/ 03</i></p><h1 id="page-title">玩家认证，<br><em>值得一玩。</em></h1><p class="hero-description">从海量游戏中，找到被玩家认真推荐的作品。让下一次选择，多一点确定。</p><a class="jump-link" href="#leaderboard">探索口碑佳作 <span aria-hidden="true">↓</span></a></div>
      <div class="hero-radar" aria-label="本榜精选"><div class="radar-label"><span>ON YOUR RADAR</span><span class="signal-bars" aria-hidden="true">▂▄▆█</span></div>%(featured)s<div class="radar-footer"><span>DISCOVER. PLAY. REPEAT.</span><span aria-hidden="true">✦</span></div></div>
    </section>
    <section class="intel-strip" aria-label="榜单信息"><div><span class="intel-label">本榜游戏</span><strong>%(count)i <small>GAMES</small></strong></div><div><span class="intel-label">最高折扣</span><strong class="lime">%(max_discount)s <small>OFF</small></strong></div><div class="update-intel"><span class="intel-label">数据更新 · UTC+8</span><time>%(datetime)s</time></div><p><span class="status-dot"></span> STEAM STORE DATA<br><small>价格与活动以商店页面为准</small></p></section>
    <nav class="board-nav" aria-label="选择榜单"><a data-board="discount" href="discount.html"><span>01</span> 特惠雷达 <b>DISCOUNTS</b></a><a data-board="zero" href="zero.html"><span>02</span> 零元补给 <b>FREE DROPS</b></a><a data-board="evaluation" href="evaluation.html"><span>03</span> 口碑殿堂 <b>TOP RATED</b></a><a data-board="hot" href="hot.html"><span>04</span> 在线战场 <b>MOST PLAYED</b></a></nav>
    <section id="leaderboard" class="leaderboard" aria-labelledby="board-title">
      <div class="board-toolbar"><div><p class="eyebrow">THE LEADERBOARD</p><h2 id="board-title">口碑殿堂 <span id="result-count">%(count)i</span></h2></div><div class="table-controls"><label class="search-box"><span aria-hidden="true">⌕</span><input id="game-search" type="search" placeholder="搜索游戏名称 / ID" aria-label="搜索游戏名称或 ID"></label><label class="sr-only" for="discount-filter">筛选折扣</label><select id="discount-filter"><option value="0">全部折扣</option><option value="50">50%% 以上</option><option value="75">75%% 以上</option><option value="90">90%% 以上</option></select></div></div>
%(table)s
      <p id="empty-state" class="empty-state" hidden>没有找到匹配的游戏，试试其他关键词或折扣。</p>
      <div class="table-footnote"><span id="visible-count" role="status" aria-live="polite">显示 %(count)i 款游戏</span><span>史低为本站已记录最低价 · 不同地区售价可能不同</span></div>
    </section>
  </main>
%(tail)s
</body>
</html>
