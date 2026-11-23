/* 剧本拆解：把长文本拆成人物模卡 / 场景图 / 道具图。
   与改写视图相互独立，只复用 api 层的错误归一化与 ui 层的复制工具。 */

import { $, toast, copyText, downloadText } from './ui.js';
import { t, tr } from './i18n.js';

const TEMPLATE = `第一集
1-1
雨夜，老城区天台，积水映着霓虹。
林晚推门冲上天台，雨水顺着湿透的短发往下淌。她穿一件黑色皮夹克，手里攥着一枚旧怀表。
栏杆边站着个穿深灰风衣的男人，兜帽遮住半张脸。

1-2
陈默回过头，露出左眉一道旧疤。
陈默：你终于来了。
林晚没有回答，指节攥得发白。

第二集
2-1
白天，废弃仓库。
林晚换了身米白色毛衣和牛仔裤，头发扎起来，脸色很差。她把怀表放在木箱上。`;

const state = {
  result: null,
  style: '',
  tab: 'characters',
  running: false,
};

let ready = false;

/* ---------------------------------------------------------------- 初始化 */

export function initBreakdown(options) {
  if (!ready) {
    bind();
    ready = true;
  }
  const select = $('bdStyle');
  if (!select.options.length && options.styles) {
    options.styles.forEach((style) => {
      const option = document.createElement('option');
      option.value = style;
      option.textContent = style;
      select.appendChild(option);
    });
  }
  updateCount();
}

function bind() {
  $('bdGo').addEventListener('click', run);
  $('bdText').addEventListener('input', updateCount);
  $('bdTemplate').addEventListener('click', () => {
    const box = $('bdText');
    if (box.value.trim()) return;
    box.value = TEMPLATE;
    updateCount();
    box.focus();
  });
  $('bdExport').addEventListener('click', exportMarkdown);
  document.querySelectorAll('.bd-tab').forEach((tab) => {
    tab.addEventListener('click', () => switchTab(tab.dataset.tab));
  });
}

function updateCount() {
  const text = $('bdText').value;
  const segments = (text.match(/^\s*\d+\s*[-－—]\s*\d+\s*$/gm) || []).length;
  $('bdCount').textContent = `${t('count.chars', { n: text.trim().length })} · ${t('count.segments', { n: segments })}`;
}

/* ---------------------------------------------------------------- 执行 */

async function run() {
  if (state.running) return;
  const text = $('bdText').value.trim();
  if (!text) {
    notice(t('bd.pasteFirst'));
    return;
  }
  hideNotice();
  setRunning(true);

  try {
    const res = await fetch('/api/breakdown', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, style: $('bdStyle').value }),
    });
    const data = await res.json();
    if (!res.ok || data.error) {
      notice(localizeProblem(data));
      return;
    }
    state.result = data;
    state.style = data.style || '';
    render();
    toast(data.demo ? t('toast.doneDemo') : t('toast.done'));
  } catch (error) {
    notice(t('error.fetch', { msg: error.message }));
  } finally {
    setRunning(false);
  }
}

function setRunning(running) {
  state.running = running;
  const button = $('bdGo');
  button.disabled = running;
  button.textContent = running ? t('bd.running') : t('bd.start');
  $('bdHint').textContent = running ? t('bd.runningHint') : '';
}

/* ---------------------------------------------------------------- 渲染 */

const TAB_FIELDS = {
  characters: [
    ['gender', 'f.gender'], ['age', 'f.age'], ['personality', 'f.personality'],
    ['appearance', 'f.appearance'], ['costume', 'f.costume'], ['note', 'f.note'],
  ],
  scenes: [
    ['time', 'f.time'], ['era', 'f.era'], ['architecture', 'f.architecture'],
    ['lighting', 'f.lighting'], ['note', 'f.note'],
  ],
  props: [
    ['material', 'f.material'], ['size', 'f.size'], ['color', 'f.color'],
    ['detail', 'f.detail'], ['note', 'f.note'],
  ],
};

function render() {
  const data = state.result;
  if (!data) return;

  $('bdEmpty').hidden = true;
  $('bdContent').hidden = false;
  $('bdCountChars').textContent = data.characters.length;
  $('bdCountScenes').textContent = data.scenes.length;
  $('bdCountProps').textContent = data.props.length;

  if (!data[state.tab] || !data[state.tab].length) {
    const first = ['characters', 'scenes', 'props'].find((key) => (data[key] || []).length);
    if (first) switchTab(first);
  } else {
    renderCards();
  }
}

function switchTab(tab) {
  state.tab = tab;
  document.querySelectorAll('.bd-tab').forEach((button) => {
    button.classList.toggle('active', button.dataset.tab === tab);
  });
  renderCards();
}

function renderCards() {
  const data = state.result;
  const list = $('bdCards');
  list.replaceChildren();
  const cards = (data && data[state.tab]) || [];

  cards.forEach((card) => {
    const wrap = document.createElement('article');
    wrap.className = 'bd-card';

    const head = document.createElement('div');
    head.className = 'bd-card-head';
    const title = document.createElement('div');
    title.className = 'bd-card-title';
    title.textContent = card.name || '未命名';
    head.appendChild(title);
    if (card.label) {
      const label = document.createElement('span');
      label.className = 'bd-card-label';
      label.textContent = card.label;
      head.appendChild(label);
    }
    wrap.appendChild(head);

    const dl = document.createElement('dl');
    TAB_FIELDS[state.tab].forEach(([key, labelKey]) => {
      const value = card[key];
      if (!value) return;
      const dt = document.createElement('dt');
      dt.textContent = t(labelKey);
      const dd = document.createElement('dd');
      dd.textContent = value;
      dl.append(dt, dd);
    });
    if (card.anchors && card.anchors.length) {
      const dt = document.createElement('dt');
      dt.textContent = t('f.anchors');
      const dd = document.createElement('dd');
      dd.textContent = card.anchors.join('；');
      dl.append(dt, dd);
    }
    wrap.appendChild(dl);

    if (card.prompt) {
      const prompt = document.createElement('div');
      prompt.className = 'bd-prompt';

      const bar = document.createElement('div');
      bar.className = 'bd-prompt-bar';
      const caption = document.createElement('span');
      caption.textContent = t('bd.promptLabel');
      const copy = document.createElement('button');
      copy.className = 'link-btn';
      copy.type = 'button';
      copy.textContent = t('bd.copy');
      copy.addEventListener('click', async () => {
        const ok = await copyText(card.prompt);
        toast(ok ? t('toast.copiedPrompt') : t('toast.copyFailed'));
      });
      bar.append(caption, copy);

      const pre = document.createElement('pre');
      pre.textContent = card.prompt;

      prompt.append(bar, pre);
      wrap.appendChild(prompt);
    }

    list.appendChild(wrap);
  });
}

/* ---------------------------------------------------------------- 导出 */

function exportMarkdown() {
  if (!state.result || !state.result.markdown) {
    notice(t('bd.nothingToExport'));
    return;
  }
  downloadText(t('bd.filename'), state.result.markdown);
  toast(t('toast.mdExported'));
}

/* ---------------------------------------------------------------- 提示 */

const PROBLEM_KEYS = {
  too_short: 'error.tooShort',
  too_long: 'error.tooLong',
  no_episode: 'error.no_episode',
  no_scenes: 'error.no_scenes',
};

function localizeProblem(data) {
  const key = PROBLEM_KEYS[data.code];
  if (!key) return data.error || t('bd.failed');
  const first = (data.problems && data.problems[0]) || {};
  return t(key, { n: first.chars || 0, m: first.limit || 0 });
}

function notice(message) {
  const el = $('bdNotice');
  el.textContent = message;
  el.classList.add('on');
}

function hideNotice() {
  const el = $('bdNotice');
  el.classList.remove('on');
  el.textContent = '';
}


/** 切换语言后重绘已生成的结果（正文是模型输出的中文，不翻译）。 */
export function refreshBreakdown() {
  if (!state.result) return;
  const data = state.result;
  $('bdCountChars').textContent = data.characters.length;
  $('bdCountScenes').textContent = data.scenes.length;
  $('bdCountProps').textContent = data.props.length;
  renderCards();
  updateCount();
}
