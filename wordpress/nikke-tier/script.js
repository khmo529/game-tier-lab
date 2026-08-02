/* =========================================================================
 * NIKKE Tier — main script (Vanilla JS + SEO Optimization + AdSense Fix)
 * =======================================================================*/

(function () {
  'use strict';

  const ROOT = document.getElementById('nikke-tier-app');
  if (!ROOT) return;

  const CFG = window.NIKKE_TIER_CFG || {};
  const BASE = (CFG.base || ROOT.dataset.base || '').replace(/\/$/, '');

  const TIERS = ['SSS', 'SS', 'S', 'A', 'B', 'C'];
  const TIER_LABEL = {
    SSS: '메타 최정점 · 전 컨텐츠 필수',
    SS: '엔드컨텐츠 핵심',
    S: '안정적 상위 성능',
    A: '특정 컨텐츠에서 유용',
    B: '대체재 있음 · 육성 후순위',
    C: '초반용 · 장기 육성 비추',
  };

  const ADS_CONFIG = {
    client: 'ca-pub-5335907721603724',
    slots: {
      top: '2613199390',    // NoPickle_본문상단
      mid: '4117852756',    // NoPickle_본문
      bottom: '8163967020', // NoPickle_본문하단
    }
  };

  function loadAdsenseScript() {
    if (document.querySelector('script[src*="adsbygoogle.js"]')) return;
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${ADS_CONFIG.client}`;
    script.crossOrigin = 'anonymous';
    document.head.appendChild(script);
  }

  // ------------------------------------------------------------------------
  // Services
  // ------------------------------------------------------------------------
  const DataService = {
    async load() {
      const [chars, week] = await Promise.all([
        fetch(`${BASE}/data/characters.json`, { cache: 'no-cache' }).then(r => r.json()),
        fetch(`${BASE}/data/weekly-update.json`, { cache: 'no-cache' }).then(r => r.json()),
      ]);
      return { chars, week };
    },
  };

  const FavService = {
    KEY: 'nikke:fav',
    get set() {
      try { return new Set(JSON.parse(localStorage.getItem(this.KEY) || '[]')); }
      catch { return new Set(); }
    },
    save(set) { localStorage.setItem(this.KEY, JSON.stringify([...set])); },
    toggle(id) {
      const s = this.set; s.has(id) ? s.delete(id) : s.add(id); this.save(s); return s.has(id);
    },
    has(id) { return this.set.has(id); },
  };

  const ThemeService = {
    KEY: 'nikke:theme',
    apply(theme) { ROOT.dataset.theme = theme; localStorage.setItem(this.KEY, theme); },
    init() {
      const saved = localStorage.getItem(this.KEY);
      const preferDark = matchMedia('(prefers-color-scheme: dark)').matches;
      this.apply(saved || (preferDark ? 'dark' : 'light'));
    },
    toggle() { this.apply(ROOT.dataset.theme === 'dark' ? 'light' : 'dark'); },
  };

  // ------------------------------------------------------------------------
  // SEO Helpers (JSON-LD & Meta Tags)
  // ------------------------------------------------------------------------
  function injectSEOData(chars, week) {
    // 1. 구글 검색엔진용 JSON-LD 구조화 데이터 삽입
    const jsonLd = {
      "@context": "https://schema.org",
      "@type": "ItemList",
      "name": `승리의 여신: 니케 최신 티어표 (${week.metaVersion})`,
      "description": `승리의 여신 니케 최신 캐릭터 티어표 및 등급표 정보. ${week.note || ''}`,
      "numberOfItems": chars.length,
      "itemListElement": chars.slice(0, 30).map((c, index) => ({
        "@type": "ListItem",
        "position": index + 1,
        "item": {
          "@type": "IndividualProduct",
          "name": `${c.name} (${c.tier}티어)`,
          "image": c.image,
          "description": `${c.company} / ${c.element} / ${c.weapon} - ${c.pros ? c.pros.join(', ') : ''}`
        }
      }))
    };

    let script = document.getElementById('nikke-json-ld');
    if (!script) {
      script = document.createElement('script');
      script.id = 'nikke-json-ld';
      script.type = 'application/ld+json';
      document.head.appendChild(script);
    }
    script.textContent = JSON.stringify(jsonLd);
  }

  const defaultTitle = document.title;
  function updatePageMeta(titleText, descText) {
    if (titleText) document.title = titleText;
    else document.title = defaultTitle;

    let metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc && descText) metaDesc.setAttribute('content', descText);
  }

  // ------------------------------------------------------------------------
  // UI Helpers
  // ------------------------------------------------------------------------
  function el(tag, attrs = {}, children = []) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v == null || v === false) continue;
      if (k === 'class') node.className = v;
      else if (k === 'html') node.innerHTML = v;
      else if (k.startsWith('on') && typeof v === 'function') node.addEventListener(k.slice(2), v);
      else if (k === 'dataset') Object.assign(node.dataset, v);
      else node.setAttribute(k, v === true ? '' : v);
    }
    const list = Array.isArray(children) ? children : [children];
    for (const c of list) {
      if (c == null || c === false) continue;
      node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    }
    return node;
  }

  const esc = (s) => String(s ?? '').replace(/[&<>"']/g,
    c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  function placeholderAvatar(name) {
    const initial = (name || '?').charAt(0);
    const hue = [...name].reduce((a, c) => a + c.charCodeAt(0), 0) % 360;
    return `data:image/svg+xml;utf8,` + encodeURIComponent(
      `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>
        <defs><linearGradient id='g' x1='0' x2='1' y1='0' y2='1'>
          <stop offset='0' stop-color='hsl(${hue},80%,68%)'/>
          <stop offset='1' stop-color='hsl(${(hue + 40) % 360},70%,55%)'/>
        </linearGradient></defs>
        <rect width='100' height='100' fill='url(#g)'/>
        <text x='50' y='58' text-anchor='middle' font-family='Pretendard,sans-serif'
              font-size='42' font-weight='800' fill='white'>${initial}</text>
      </svg>`
    );
  }

  // ------------------------------------------------------------------------
  // Components
  // ------------------------------------------------------------------------
  function Hero(week) {
    return el('header', { class: 'nk-hero' }, [
      el('span', { class: 'nk-hero__eyebrow' }, ['⚡ ' + week.metaVersion + ' · 최신 메타 기준']),
      el('h1', { class: 'nk-hero__title', html: '승리의 여신: 니케<br><strong>최신 캐릭터 티어표</strong>' }),
      el('p', { class: 'nk-hero__sub' }, [week.week + ' · ' + (week.note || '')]),
      el('div', { class: 'nk-hero__cta' }, [
        el('button', { class: 'nk-btn nk-btn--primary', onclick: () => scrollToId('nk-tiers') }, ['▼ 티어표 보기']),
        el('button', { class: 'nk-btn', onclick: () => scrollToId('nk-new') }, ['✨ 신규 캐릭터']),
        el('button', { class: 'nk-btn', onclick: () => scrollToId('nk-changes') }, ['📅 업데이트 내역']),
      ]),
    ]);
  }

  function scrollToId(id) {
    const t = document.getElementById(id);
    if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function UpdateCard(week) {
    const stat = (label, value, mod = '') =>
      el('div', { class: 'nk-stat ' + mod }, [
        el('div', { class: 'nk-stat__label' }, [label]),
        el('div', { class: 'nk-stat__value', html: value }),
      ]);
    return el('section', { class: 'nk-update', id: 'nk-changes', 'aria-label': '주간 업데이트' }, [
      el('h2', { class: 'nk-sr' }, ['업데이트 요약']),
      el('div', { class: 'nk-update__grid' }, [
        stat('📅 업데이트', `<span class="em">${esc(week.date)}</span>`),
        stat('🧭 메타 버전', esc(week.metaVersion)),
        stat('✨ 신규', String(week.counts.new), 'nk-stat--new'),
        stat('▲ 상향', String(week.counts.up), 'nk-stat--up'),
      ]),
      el('div', { class: 'nk-update__grid', style: 'margin-top:10px' }, [
        stat('▼ 하향', String(week.counts.down), 'nk-stat--down'),
        stat('💪 버프', String(week.counts.buff)),
        stat('🩹 너프', String(week.counts.nerf)),
        stat('📝 노트', esc(week.note || '-')),
      ]),
    ]);
  }

  function WeeklyChanges(week) {
    const items = week.changes.map(c =>
      el('span', { class: `nk-change nk-change--${c.type}` }, [
        el('span', { class: 'nk-change__badge' }, [
          c.type === 'new' ? 'NEW' : c.type === 'up' ? '▲' : '▼'
        ]),
        c.name + (c.type === 'new' ? '' : `  ${c.from}→${c.to}`),
      ])
    );
    return el('section', { class: 'nk-changes', id: 'nk-new', 'aria-label': '이번주 변경 캐릭터' }, [
      el('h2', { class: 'nk-sr' }, ['이번주 변동 캐릭터']),
      ...items
    ]);
  }

  function Filter(state, onChange, characters) {
    const uniq = (arr) => [...new Set(arr)];
    const companies = uniq(characters.map(c => c.company));
    const elements = uniq(characters.map(c => c.element));
    const weapons = uniq(characters.map(c => c.weapon));
    const bursts = uniq(characters.map(c => c.burst));
    const positions = uniq(characters.map(c => c.position));

    const chip = (label, group, value) => {
      const active = state[group] === value;
      return el('button', {
        class: 'nk-chip', 'aria-pressed': active ? 'true' : 'false',
        onclick: () => { state[group] = active ? null : value; onChange(); }
      }, [label]);
    };

    const searchInput = el('input', {
      type: 'search',
      placeholder: '캐릭터 이름 검색…',
      'aria-label': '캐릭터 검색',
      value: state.query || '',
      oninput: (e) => { state.query = e.target.value; onChange(); },
    });

    const chipRow = (label, group, values) =>
      el('div', { class: 'nk-chipbar', role: 'group', 'aria-label': label }, [
        el('button', { class: 'nk-chip', 'aria-pressed': state[group] == null ? 'true' : 'false',
          onclick: () => { state[group] = null; onChange(); } }, [label]),
        ...values.map(v => chip(v, group, v)),
      ]);

    const sortSelect = el('select', {
      'aria-label': '정렬 기준',
      onchange: (e) => { state.sort = e.target.value; onChange(); },
    }, [
      ['tier', '티어순'],
      ['name', '이름순'],
      ['release', '출시순'],
      ['company', '기업순'],
      ['element', '속성순'],
      ['burst', '버스트순'],
    ].map(([v, l]) => {
      const o = el('option', { value: v }, [l]);
      if (state.sort === v) o.selected = true;
      return o;
    }));

    const onlySSR = el('label', { class: 'nk-chip', style: 'display:inline-flex;gap:6px;align-items:center;cursor:pointer' }, [
      (() => {
        const cb = el('input', { type: 'checkbox',
          onchange: (e) => { state.onlySSR = e.target.checked; onChange(); }
        });
        if (state.onlySSR) cb.checked = true;
        return cb;
      })(),
      'SSR만'
    ]);

    const onlyFav = el('label', { class: 'nk-chip', style: 'display:inline-flex;gap:6px;align-items:center;cursor:pointer' }, [
      (() => {
        const cb = el('input', { type: 'checkbox',
          onchange: (e) => { state.onlyFav = e.target.checked; onChange(); }
        });
        if (state.onlyFav) cb.checked = true;
        return cb;
      })(),
      '⭐ 즐겨찾기'
    ]);

    const toggleBtn = el('button', {
      class: 'nk-filter__toggle',
      'aria-expanded': state.collapsed ? 'false' : 'true',
      onclick: () => { state.collapsed = !state.collapsed; onChange(); }
    }, [state.collapsed ? '🎛️ 필터 열기 ▼' : '🎛️ 필터 닫기 ▲']);

    const filterBody = el('div', { class: `nk-filter__body ${state.collapsed ? 'is-collapsed' : ''}` }, [
      chipRow('기업', 'company', companies),
      chipRow('속성', 'element', elements),
      chipRow('무기', 'weapon', weapons),
      chipRow('버스트', 'burst', bursts),
      chipRow('포지션', 'position', positions),
      el('div', { class: 'nk-toolbar' }, [
        el('div', { style: 'display:flex;gap:8px;flex-wrap:wrap' }, [onlySSR, onlyFav]),
        el('div', {}, [
          el('span', { class: 'nk-sr' }, ['정렬']),
          sortSelect,
        ]),
      ]),
    ]);

    return el('div', { class: 'nk-filter', role: 'search' }, [
      el('div', { class: 'nk-filter__header' }, [
        el('div', { class: 'nk-search' }, [
          el('span', { 'aria-hidden': 'true' }, ['🔍']),
          searchInput,
        ]),
        toggleBtn,
      ]),
      filterBody,
    ]);
  }

  // SEO 최적화: 시맨틱 h3 태그 적용
  function CharacterCard(c, weekMap, onOpen) {
    const change = weekMap.get(c.id);
    const isFav = FavService.has(c.id);
    const img = el('img', {
      alt: `${c.name} (${c.tier}티어)`, loading: 'lazy', decoding: 'async',
      'data-src': c.image || placeholderAvatar(c.name),
    });

    const card = el('article', {
      class: 'nk-card', tabindex: '0', role: 'button',
      'aria-label': `${c.name} 상세 보기`,
      onclick: () => onOpen(c),
      onkeydown: (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onOpen(c); } },
    }, [
      el('div', { class: 'nk-card__img' }, [
        img,
        el('div', { class: 'nk-card__badges' }, [
          change ? el('span', {
            class: 'nk-badge nk-badge--' + change.type
          }, [change.type === 'new' ? 'NEW' : change.type === 'up' ? '▲' : '▼']) : el('span'),
        ]),
        el('button', {
          class: 'nk-fav', 'aria-pressed': isFav ? 'true' : 'false',
          'aria-label': '즐겨찾기',
          onclick: (e) => {
            e.stopPropagation();
            const now = FavService.toggle(c.id);
            e.currentTarget.setAttribute('aria-pressed', now ? 'true' : 'false');
          }
        }, ['★']),
      ]),
      el('h3', { class: 'nk-card__name' }, [c.name]), // h3 시맨틱 태그로 변경
      el('div', { class: 'nk-card__meta' }, [
        el('span', {}, [c.element]),
        el('span', {}, [c.weapon]),
      ]),
    ]);

    return card;
  }

  // SEO 최적화: 시맨틱 h2 태그 적용
  function TierGrid(chars, weekMap, onOpen) {
    const wrap = el('section', { id: 'nk-tiers' });

    TIERS.forEach((tier) => {
      const list = chars.filter(c => c.tier === tier);
      if (list.length === 0) return;

      const row = el('section', { class: 'nk-tier', 'aria-label': tier + ' 티어' }, [
        el('div', { class: 'nk-tier__head' }, [
          el('div', { class: 'nk-tier__badge', dataset: { t: tier } }, [tier]),
          el('div', {}, [
            el('h2', { class: 'nk-tier__title' }, [tier + ' 티어']), // h2 시맨틱 태그로 변경
            el('p', { class: 'nk-tier__desc' }, [TIER_LABEL[tier] || '']),
          ]),
        ]),
        el('div', { class: 'nk-tier__grid' },
          list.map(c => CharacterCard(c, weekMap, onOpen))),
      ]);
      wrap.appendChild(row);
    });

    return wrap;
  }

  // 애드센스 슬롯 컴포넌트
  function AdSlot(type) {
    const slotId = ADS_CONFIG.slots[type] || ADS_CONFIG.slots.mid;
    
    const ins = el('ins', {
      class: 'adsbygoogle',
      style: 'display:block; min-height:90px;',
      'data-ad-client': ADS_CONFIG.client,
      'data-ad-slot': slotId,
      'data-ad-format': 'auto',
      'data-full-width-responsive': 'true'
    });

    const wrap = el('aside', { class: 'nk-ad', 'aria-label': '광고' }, [ins]);

    setTimeout(() => {
      try {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      } catch (err) {}
    }, 100);

    return wrap;
  }

  function MetaStats(chars) {
    const total = chars.length;
    const bar = (cur, max) => el('div', { class: 'nk-meta__bar' }, [
      (() => { const i = el('i'); i.style.width = (max ? (cur / max * 100) : 0) + '%'; return i; })()
    ]);
    const groupCount = (key) => {
      const m = new Map();
      chars.forEach(c => m.set(c[key], (m.get(c[key]) || 0) + 1));
      return [...m.entries()].sort((a, b) => b[1] - a[1]);
    };
    const card = (label, value, extra) =>
      el('div', { class: 'nk-meta__card' }, [
        el('div', { class: 'nk-meta__label' }, [label]),
        el('div', { class: 'nk-meta__value' }, [value]),
        extra,
      ]);

    const [topCompany, topCompanyCount] = groupCount('company')[0] || ['-', 0];
    const [topElement, topElementCount] = groupCount('element')[0] || ['-', 0];
    const recommended = chars.filter(c => c.reroll).length;

    return el('section', { class: 'nk-meta', 'aria-label': '메타 통계' }, [
      el('h2', { class: 'nk-sr' }, ['티어표 메타 통계']),
      card('전체 SSR 수', total + '명', bar(total, total)),
      card('최다 기업', topCompany, bar(topCompanyCount, total)),
      card('최다 속성', topElement, bar(topElementCount, total)),
      card('추천 리세율', Math.round(recommended / total * 100) + '%', bar(recommended, total)),
    ]);
  }

  // ------------------------------------------------------------------------
  // BottomSheet (동적 Meta/Title 변경 반영)
  // ------------------------------------------------------------------------
  const Sheet = (() => {
    let root, panel;
    function ensure() {
      if (root) return;
      root = el('div', { class: 'nk-sheet', role: 'dialog', 'aria-modal': 'true' }, [
        el('div', { class: 'nk-sheet__scrim', onclick: close }),
        el('div', { class: 'nk-sheet__panel', id: 'nk-sheet-panel' }, []),
      ]);
      panel = root.querySelector('#nk-sheet-panel');
      ROOT.appendChild(root);
      document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
    }
    function open(c) {
      ensure();
      panel.innerHTML = '';
      panel.appendChild(SheetContent(c));
      root.classList.add('open');
      document.body.style.overflow = 'hidden';
      panel.scrollTop = 0;

      // SEO: 캐릭터 창이 열리면 Title과 Meta Description을 동적으로 변경
      const prosText = (c.pros || []).join(', ');
      updatePageMeta(
        `${c.name} 티어 및 공략 - 승리의 여신 니케`,
        `${c.name} (${c.tier}티어) 추천 오버로드, 큐브, 조합, 장단점 정보: ${prosText}`
      );
    }
    function close() {
      if (!root) return;
      root.classList.remove('open');
      document.body.style.overflow = '';
      updatePageMeta(); // 원래 타이틀로 원복
    }
    return { open, close };
  })();

  function SheetContent(c) {
    const stars = '★'.repeat(c.rating) + '☆'.repeat(5 - c.rating);
    const contentNames = { story: '스토리', boss: '보스', pvp: 'PVP', raid: '레이드', union: '유니온' };
    const scoreBoxes = Object.entries(c.scores || {}).map(([k, v]) =>
      el('div', { class: 'nk-score' }, [
        el('div', { class: 'nk-score__label' }, [contentNames[k] || k]),
        el('div', { class: 'nk-score__value' }, [String(v)]),
      ])
    );

    const timeline = (c.history || []).map((t, i) =>
      el('div', { class: 'nk-tl-item' }, [
        el('div', { class: 'nk-tl-item__wk' }, ['W-' + (8 - i)]),
        el('div', { class: 'nk-tl-item__tier' }, [t]),
      ])
    );

    const share = async () => {
      const url = location.origin + location.pathname + '#char=' + c.id;
      try {
        if (navigator.share) await navigator.share({ title: c.name + ' 티어 정보', url });
        else { await navigator.clipboard.writeText(url); alert('URL이 복사되었습니다.'); }
      } catch { /* noop */ }
    };

    return el('div', {}, [
      el('div', { class: 'nk-sheet__grab' }),
      el('div', { class: 'nk-sheet__hero' }, [
        el('div', { class: 'nk-sheet__thumb' }, [
          el('img', { src: c.image || placeholderAvatar(c.name), alt: c.name, loading: 'lazy' })
        ]),
        el('div', {}, [
          el('h2', { class: 'nk-sheet__name' }, [c.name]),
          el('div', { class: 'nk-sheet__tags' }, [
            el('span', { class: 'nk-tag' }, [c.tier + ' 티어']),
            el('span', { class: 'nk-tag nk-tag--muted' }, [c.rarity]),
            el('span', { class: 'nk-tag nk-tag--muted' }, [c.company]),
            el('span', { class: 'nk-tag nk-tag--muted' }, [c.element]),
            el('span', { class: 'nk-tag nk-tag--muted' }, [c.weapon]),
            el('span', { class: 'nk-tag nk-tag--muted' }, ['버스트 ' + c.burst]),
            el('span', { class: 'nk-tag nk-tag--muted' }, [c.position]),
          ]),
          el('div', { class: 'nk-stars', 'aria-label': `평점 ${c.rating}/5` }, [stars]),
        ]),
      ]),

      el('div', { class: 'nk-section' }, [
        el('h3', { class: 'nk-section__title' }, ['컨텐츠별 점수']),
        el('div', { class: 'nk-scores' }, scoreBoxes),
      ]),

      el('div', { class: 'nk-section' }, [
        el('h3', { class: 'nk-section__title' }, ['장점 · 단점']),
        el('div', { class: 'nk-pros' }, [
          el('strong', {}, ['👍 장점 · ']),
          (c.pros || []).join(' · '),
        ]),
        el('div', { class: 'nk-cons' }, [
          el('strong', {}, ['⚠️ 단점 · ']),
          (c.cons || []).join(' · '),
        ]),
      ]),

      el('div', { class: 'nk-section' }, [
        el('h3', { class: 'nk-section__title' }, ['추천 오버로드 · 큐브']),
        el('ul', { class: 'nk-list' }, [
          el('li', {}, ['오버로드 · ' + (c.overload || []).join(' / ')]),
          el('li', {}, ['큐브 · ' + (c.cube || '-')]),
        ]),
      ]),

      el('div', { class: 'nk-section' }, [
        el('h3', { class: 'nk-section__title' }, ['추천 조합']),
        el('ul', { class: 'nk-list' }, (c.team || []).map(t => el('li', {}, [t]))),
      ]),

      el('div', { class: 'nk-section' }, [
        el('h3', { class: 'nk-section__title' }, ['스킬 우선순위']),
        el('ul', { class: 'nk-list' }, (c.priority || []).map(p => el('li', {}, [p]))),
      ]),

      el('div', { class: 'nk-section' }, [
        el('h3', { class: 'nk-section__title' }, ['추천 리세마라 · ' + (c.reroll ? '✅ 추천' : '❌ 비추천')]),
      ]),

      el('div', { class: 'nk-section' }, [
        el('h3', { class: 'nk-section__title' }, ['최근 8주 티어 변화']),
        el('div', { class: 'nk-timeline' }, timeline),
      ]),

      el('div', { class: 'nk-sheet__actions' }, [
        el('button', { class: 'nk-btn nk-btn--primary', onclick: share }, ['🔗 공유하기']),
        el('button', { class: 'nk-btn', onclick: () => {
          navigator.clipboard.writeText(location.origin + location.pathname + '#char=' + c.id);
          alert('URL이 복사되었습니다.');
        }}, ['URL 복사']),
        el('button', { class: 'nk-btn nk-btn--ghost', onclick: () => Sheet.close() }, ['닫기']),
      ]),
    ]);
  }

  function Fab() {
    const btn = el('button', {
      class: 'nk-fab', 'aria-label': '위로 이동',
      onclick: () => window.scrollTo({ top: 0, behavior: 'smooth' })
    }, ['↑']);
    const theme = el('button', {
      class: 'nk-fab', style: 'right: 78px; background:#191F28',
      'aria-label': '다크모드 전환',
      onclick: () => ThemeService.toggle()
    }, ['🌓']);
    return el('div', {}, [theme, btn]);
  }

  function applyFilters(chars, state) {
    const q = (state.query || '').trim().toLowerCase();
    const fav = FavService.set;
    const tierRank = Object.fromEntries(TIERS.map((t, i) => [t, i]));
    const list = chars.filter(c => {
      if (q && !c.name.toLowerCase().includes(q)) return false;
      if (state.company  && c.company  !== state.company)  return false;
      if (state.element  && c.element  !== state.element)  return false;
      if (state.weapon   && c.weapon   !== state.weapon)   return false;
      if (state.burst    && c.burst    !== state.burst)    return false;
      if (state.position && c.position !== state.position) return false;
      if (state.onlySSR  && c.rarity !== 'SSR') return false;
      if (state.onlyFav  && !fav.has(c.id))     return false;
      return true;
    });
    const cmp = {
      tier:    (a, b) => (tierRank[a.tier] - tierRank[b.tier]) || a.name.localeCompare(b.name, 'ko'),
      name:    (a, b) => a.name.localeCompare(b.name, 'ko'),
      release: (a, b) => a.id - b.id,
      company: (a, b) => a.company.localeCompare(b.company, 'ko'),
      element: (a, b) => a.element.localeCompare(b.element, 'ko'),
      burst:   (a, b) => String(a.burst).localeCompare(String(b.burst), 'ko'),
    };
    list.sort(cmp[state.sort] || cmp.tier);
    return list;
  }

  function observeLazyImages(container) {
    const imgs = container.querySelectorAll('img[data-src]');
    if (!('IntersectionObserver' in window)) {
      imgs.forEach(i => { i.src = i.dataset.src; i.removeAttribute('data-src'); });
      return;
    }
    const io = new IntersectionObserver((entries, obs) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        const img = e.target;
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
        obs.unobserve(img);
      }
    }, { rootMargin: '200px 0px' });
    imgs.forEach(i => io.observe(i));
  }

  // ------------------------------------------------------------------------
  // App Bootstrap (AdSense Safe Structure)
  // ------------------------------------------------------------------------
  async function main() {
    ThemeService.init();
    loadAdsenseScript();

    ROOT.classList.add('nikke-app-ready');
    const shell = el('div', { class: 'nikke-shell' });
    ROOT.appendChild(shell);

    shell.appendChild(el('div', { class: 'nk-update' }, ['불러오는 중…']));

    let data;
    try {
      data = await DataService.load();
    } catch (err) {
      shell.innerHTML = '';
      shell.appendChild(el('div', { class: 'nk-update' }, [
        '데이터를 불러오지 못했습니다. ',
        el('code', {}, [String(err && err.message || err)]),
      ]));
      return;
    }
    shell.innerHTML = '';

    const { chars, week } = data;
    const weekMap = new Map(week.changes.map(c => [c.id, c]));

    // SEO 최적화: 데이터 로드 직후 JSON-LD 주입
    injectSEOData(chars, week);

    const state = {
      query: '', company: null, element: null, weapon: null,
      burst: null, position: null, tier: null,
      onlySSR: false, onlyFav: false, sort: 'tier',
      collapsed: true,
    };

    // 상단 정적 영역
    shell.appendChild(Hero(week));
    shell.appendChild(UpdateCard(week));
    shell.appendChild(WeeklyChanges(week));
    
    // ★ 상단 광고: 필터링 시 파괴되지 않도록 상단에 정적으로 고정
    shell.appendChild(AdSlot('top'));

    // 동적 영역 (필터 + 티어표 그리드)
    const filterContainer = el('div');
    const gridContainer = el('div');
    
    shell.appendChild(filterContainer);
    shell.appendChild(gridContainer);
    
    // ★ 중간 및 하단 광고 고정 배치
    shell.appendChild(AdSlot('mid'));
    shell.appendChild(MetaStats(chars));
    shell.appendChild(AdSlot('bottom'));

    // 필터링 동작 시 'gridContainer'만 파괴하고 재구성 (광고 파괴 방지)
    function renderGridOnly() {
      gridContainer.innerHTML = '';
      const filtered = applyFilters(chars, state);
      const gridMount = TierGrid(filtered, weekMap, (c) => Sheet.open(c));
      gridContainer.appendChild(gridMount);
      observeLazyImages(gridMount);
    }

    function renderAll() {
      filterContainer.innerHTML = '';
      filterContainer.appendChild(Filter(state, renderAll, chars));
      renderGridOnly();
    }

    renderAll();

    ROOT.appendChild(Fab());

    const m = /#char=(\d+)/.exec(location.hash);
    if (m) {
      const c = chars.find(x => String(x.id) === m[1]);
      if (c) setTimeout(() => Sheet.open(c), 200);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', main);
  } else {
    main();
  }
})();