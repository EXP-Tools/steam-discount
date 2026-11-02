(() => {
  'use strict';
  document.querySelectorAll('.board-nav a').forEach(link => {
    if (link.dataset.board === document.body.dataset.board) link.setAttribute('aria-current', 'page');
  });
  const search = document.querySelector('#game-search');
  const filter = document.querySelector('#discount-filter');
  const rows = [...document.querySelectorAll('#steam tbody tr')];
  if (!search || !filter) return;
  const update = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    rows.forEach(row => {
      row.hidden = !row.dataset.search.toLocaleLowerCase().includes(query)
        || Number(row.dataset.discount) < Number(filter.value);
      if (!row.hidden) count++;
    });
    document.querySelector('#result-count').textContent = String(count);
    document.querySelector('#visible-count').textContent = `显示 ${count} / ${rows.length} 款游戏`;
    document.querySelector('#empty-state').hidden = count !== 0;
  };
  search.addEventListener('input', update);
  filter.addEventListener('change', update);
  if (!rows.length) {
    document.querySelector('#empty-state').textContent = document.body.dataset.board === 'zero'
      ? '本次抓取暂未发现付费游戏的免费领取活动，下次更新再来看看。'
      : '本次暂时没有可展示的游戏。';
  }
  update();
})();
