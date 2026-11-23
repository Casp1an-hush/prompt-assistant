/* Prompt Assistant · 主逻辑
   视图切换、流式渲染、结果操作、历史、氛围。
   新增功能时：加一个 .view + 一条导航 + 一个模块，不用改这里的结构。 */

import {
  getOptions, getHealth, getHistory, getHistoryItem,
  deleteHistoryItem, clearHistory, streamRewrite,
} from './api.js';
import {
  $, toast, sceneIcon, highlight, copyText,
  downloadText, formatTime, fullText,
} from './ui.js';
import { initBreakdown, refreshBreakdown } from './breakdown.js';
import { initI18n, t, tr, onLangChange, setLang, getLang, LANGS } from './i18n.js';

const EXAMPLES = [
  { label: 'example.chase.label', text: 'example.chase.text' },
  { label: 'example.cat.label', text: 'example.cat.text' },
  { label: 'example.product.label', text: 'example.product.text' },
];

const AMBIENT_LABELS = {
  'planet-ship.jpeg': '星际',
  'ocean.jpeg': '海面',
  'space-1.jpeg': '深空',
  'space-window.jpeg': '舷窗',
  'starship.jpeg': '星舰',
};

const STAGES = [
  [0, '正在读你的描述…'],
  [1200, '正在判断这是什么戏份…'],
  [2800, '正在组织镜头与细节…'],
  [5600, '正在整理改动说明…'],
];

const state = {
  options: null,
  running: false,
  controller: null,
  result: null,
  streamText: '',
  sceneOverride: '',
  stageOverride: '',
  startedAt: 0,
  stageTimer: null,
  ambient: 'off',
  epoch: 0,            // 每次清空 +1，用于让在途的流式事件作废
  streamError: '',     // 本次流收到的真实错误，别被笼统提示盖掉
};

/* ---------------------------------------------------------------- 基础 */

function fillSelect(id, pairs) {
  const el = $(id);
  el.replaceChildren();
  for (const [value, label] of pairs) {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = label;
    el.appendChild(option);
  }
}

function setStatus(kind, text) {
  $('statusLed').className = `status-led ${kind}`;
  $('statusText').textContent = text;
}

function showNotice(message) {
  $('notice').textContent = message;
  $('notice').classList.add('on');
}

function hideNotice() {
  $('notice').classList.remove('on');
  $('notice').textContent = '';
}

function onModelChange() {
  const model = state.options?.models.find((m) => m.value === $('model').value);
  $('modelHint').textContent = model?.hint || '';
  $('durationField').hidden = !model?.video;
}

function updateChar() {
  const count = $('prompt').value.trim().length;
  $('charCount').textContent = t('count.chars', { n: count });
  if (count > 0 && count < 18) {
    $('editorHint').innerHTML = `<span class="soft-hint">${tr('再补点主体、动作或环境，会更准')}</span>`;
  } else {
    $('editorHint').textContent = tr('支持 ⌘ + Enter 快速开始');
  }
}

function renderExamples() {
  const wrap = $('examples');
  wrap.replaceChildren();
  for (const example of EXAMPLES) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'chip';
    button.textContent = t(example.label);
    button.title = t(example.text);
    button.addEventListener('click', () => {
      $('prompt').value = t(example.text);
      updateChar();
      $('prompt').focus();
    });
    wrap.appendChild(button);
  }
}

/* ---------------------------------------------------------------- 动态粒子层
   在 .atmosphere 内注入四类粒子。位置、尺寸、时长、相位随机，
   用负 animation-delay 让首帧就有粒子在动。
   动画定义在 motion.css；prefers-reduced-motion 时由 CSS 隐藏。 */

function buildParticles() {
  const layer = $('atmoLive');
  if (!layer) return;
  const rand = (min, max) => min + Math.random() * (max - min);
  const frag = document.createDocumentFragment();

  // 上浮气泡：18 个
  for (let i = 0; i < 18; i++) {
    const el = document.createElement('span');
    const size = rand(6, 20);
    el.className = 'p-bubble';
    el.style.left = `${rand(4, 96)}%`;
    el.style.width = `${size}px`;
    el.style.height = `${size}px`;
    el.style.animationDuration = `${rand(16, 30)}s`;
    el.style.animationDelay = `${rand(-30, 0)}s`;
    el.style.setProperty('--sway', `${rand(-30, 30)}px`);
    frag.appendChild(el);
  }

  // 漂浮陨尘：26 个
  for (let i = 0; i < 26; i++) {
    const el = document.createElement('span');
    const size = rand(2, 5);
    el.className = 'p-drift';
    el.style.left = `${rand(3, 97)}%`;
    el.style.top = `${rand(3, 97)}%`;
    el.style.width = `${size}px`;
    el.style.height = `${size}px`;
    el.style.animationDuration = `${rand(16, 34)}s`;
    el.style.animationDelay = `${rand(-34, 0)}s`;
    el.style.setProperty('--dx', `${rand(-90, 90)}px`);
    el.style.setProperty('--dy', `${rand(-70, 70)}px`);
    frag.appendChild(el);
  }

  // 斜划流星：9 个
  for (let i = 0; i < 9; i++) {
    const el = document.createElement('span');
    el.className = 'p-meteor';
    el.style.left = `${rand(18, 88)}%`;
    el.style.top = `${rand(-6, 62)}%`;
    el.style.width = `${rand(80, 170)}px`;
    el.style.animationDuration = `${rand(9, 16)}s`;
    el.style.animationDelay = `${rand(-16, 0)}s`;
    frag.appendChild(el);
  }

  // 扩散水波：9 个
  for (let i = 0; i < 9; i++) {
    const el = document.createElement('span');
    const size = rand(46, 110);
    el.className = 'p-ripple';
    el.style.left = `${rand(10, 90)}%`;
    el.style.top = `${rand(12, 90)}%`;
    el.style.width = `${size}px`;
    el.style.height = `${size}px`;
    el.style.animationDuration = `${rand(9, 15)}s`;
    el.style.animationDelay = `${rand(-15, 0)}s`;
    frag.appendChild(el);
  }

  layer.appendChild(frag);
}

/* ---------------------------------------------------------------- 氛围 */

function applyAmbient(key) {
  state.ambient = key;
  const layer = $('ambient');
  if (key === 'off') {
    layer.classList.remove('on');
    $('ambientLabel').textContent = '关';
  } else {
    layer.style.backgroundImage = `url(/static/backgrounds/${encodeURIComponent(key)})`;
    layer.classList.add('on');
    $('ambientLabel').textContent = AMBIENT_LABELS[key] || '开';
  }
  document.querySelectorAll('.ambient-item').forEach((item) => {
    item.classList.toggle('active', item.dataset.key === key);
  });
  try { localStorage.setItem('ps-ambient', key); } catch { /* 隐私模式 */ }
}

function renderAmbient(backgrounds) {
  const list = $('ambientList');
  list.replaceChildren();
  const addItem = (key, label, image) => {
    const item = document.createElement('button');
    item.type = 'button';
    item.className = 'ambient-item' + (image ? '' : ' off');
    item.dataset.key = key;
    item.textContent = label;
    item.title = image ? AMBIENT_LABELS[key] || key : '关闭背景';
    if (image) item.style.backgroundImage = `url(/static/backgrounds/${encodeURIComponent(key)})`;
    item.addEventListener('click', () => {
      applyAmbient(key);
      closeAmbientPanel();
      toast(image ? `${t('ambient.label')}：${tr(AMBIENT_LABELS[key] || key)}` : t('toast.ambientOff'));
    });
    list.appendChild(item);
  };
  addItem('off', '关', null);
  backgrounds.forEach((name) => addItem(name, (AMBIENT_LABELS[name] || name).slice(0, 2), name));
  try {
    const saved = localStorage.getItem('ps-ambient');
    if (saved === 'off' || backgrounds.includes(saved)) applyAmbient(saved);
  } catch { /* 隐私模式 */ }
}

function closeAmbientPanel() {
  $('ambientPanel').hidden = true;
  $('ambientToggle').setAttribute('aria-expanded', 'false');
}

/* ---------------------------------------------------------------- 戏份覆盖（可选出口） */

function renderOverrideMenu(types) {
  const menu = $('overrideMenu');
  menu.replaceChildren();
  const entries = [['', '自动判断（默认）'], ...types.map((t) => [t, t])];
  for (const [value, label] of entries) {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = label;
    button.dataset.scene = value;
    button.addEventListener('click', () => {
      state.sceneOverride = value;
      updateOverrideHint();
      closeOverride();
      toast(value ? t('toast.override', { v: value }) : t('toast.autoScene'));
    });
    menu.appendChild(button);
  }
}

function updateOverrideHint() {
  const hint = $('overrideHint');
  if (state.sceneOverride) {
    hint.hidden = false;
    hint.textContent = `下次按「${state.sceneOverride}」改写`;
  } else {
    hint.hidden = true;
  }
  document.querySelectorAll('#overrideMenu button').forEach((button) => {
    button.classList.toggle('active', button.dataset.scene === state.sceneOverride);
  });
}

function closeOverride() {
  $('overrideMenu').hidden = true;
  $('overrideToggle').setAttribute('aria-expanded', 'false');
}

/* ---------------------------------------------------------------- 视图 */

function switchView(name) {
  document.querySelectorAll('.view').forEach((view) => {
    view.classList.toggle('active', view.id === `view-${name}`);
  });
  document.querySelectorAll('.nav-item').forEach((button) => {
    if (!button.dataset.soon) button.classList.toggle('active', button.dataset.view === name);
  });
  const titles = { rewrite: '改写', breakdown: '剧本拆解', history: '历史记录' };
  $('crumbCurrent').textContent = titles[name] || '改写';
  if (name === 'history') loadHistory();
  if (name === 'breakdown' && state.options) initBreakdown(state.options);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* ---------------------------------------------------------------- 结果渲染 */

function showResultShell(show) {
  $('resultEmpty').hidden = show;
  $('resultContent').hidden = !show;
}

function setScene(scene, reason) {
  $('sceneIcon').innerHTML = sceneIcon(scene || '叙事戏');
  $('sceneName').textContent = scene ? tr(scene) : t('scene.judging');
  $('sceneReason').textContent = reason || '';
}

function renderPrompt(text, streaming) {
  const el = $('promptBody');
  el.replaceChildren(highlight(text));
  if (streaming) {
    const caret = document.createElement('span');
    caret.className = 'caret';
    el.appendChild(caret);
  }
}

let renderFrame = 0;
function scheduleRender() {
  if (renderFrame) return;
  renderFrame = requestAnimationFrame(() => {
    renderFrame = 0;
    renderPrompt(state.streamText, true);
  });
}

function renderChanges(changes) {
  const box = $('changes');
  if (!changes || !changes.length) {
    box.hidden = true;
    $('changesList').replaceChildren();
    $('changesCount').textContent = '';
    return;
  }
  box.hidden = false;
  box.classList.remove('collapsed');
  $('changesHead').setAttribute('aria-expanded', 'true');
  $('changesCount').textContent = `${changes.length} 处`;
  const list = $('changesList');
  list.replaceChildren();
  for (const text of changes) {
    const li = document.createElement('li');
    li.textContent = text;
    list.appendChild(li);
  }
}

function showResult(result, meta) {
  state.result = result;
  showResultShell(true);
  setScene(result.scene, result.reason);
  renderPrompt(result.prompt || '', false);
  renderChanges(result.changes || []);
  $('resultMeta').textContent = meta || '';
  $('resultPanel').classList.remove('stale');
}

/* ---------------------------------------------------------------- 清空 / 重置 */

/** 把右侧结果区恢复到空态，并丢弃所有与结果相关的状态。 */
function resetResult() {
  state.result = null;
  state.streamText = '';
  // 取消还没执行的渲染帧，否则它会在清空后又把正文画回去
  if (renderFrame) {
    cancelAnimationFrame(renderFrame);
    renderFrame = 0;
  }
  showResultShell(false);
  $('sceneIcon').replaceChildren();
  $('sceneName').textContent = '—';
  $('sceneReason').textContent = '';
  renderPrompt('', false);
  $('changes').classList.remove('collapsed');
  renderChanges([]);
  $('resultMeta').textContent = '';
  $('resultPanel').classList.remove('stale');
}

/** 清空输入框时，右边的改写结果同步消失；在途的改写也一并收掉。 */
function clearWorkspace({ focus = true } = {}) {
  $('prompt').value = '';
  updateChar();
  hideNotice();
  state.epoch += 1;
  state.stageOverride = '';
  state.streamError = '';
  if (state.running) {
    state.controller?.abort();
    state.controller = null;
    stopRunning();               // 不等旧请求的 finally，立刻恢复按钮
  }
  resetResult();
  if (focus) $('prompt').focus();
}

/* ---------------------------------------------------------------- 改写流程 */

function tickStage() {
  const elapsed = Date.now() - state.startedAt;
  let label = STAGES[0][1];
  for (const [ms, text] of STAGES) if (elapsed >= ms) label = text;
  $('progressText').textContent = state.stageOverride || tr(label);
  $('progressTime').textContent = `${(elapsed / 1000).toFixed(1)}s`;
}

function startRunning() {
  state.running = true;
  state.stageOverride = '';
  $('goBtn').disabled = true;
  $('goBtn').setAttribute('aria-busy', 'true');
  $('goBtn').textContent = '改写中…';
  $('cancelBtn').hidden = false;
  $('progress').classList.add('on');
  state.startedAt = Date.now();
  state.stageTimer = setInterval(tickStage, 120);
  tickStage();
}

function stopRunning() {
  state.running = false;
  clearInterval(state.stageTimer);
  state.stageTimer = null;
  $('goBtn').disabled = false;
  $('goBtn').removeAttribute('aria-busy');
  $('goBtn').textContent = '开始改写';
  $('cancelBtn').hidden = true;
  $('progress').classList.remove('on');
}

function handleEvent(type, data) {
  if (type === 'start') {
    if (data.cached) state.stageOverride = tr('命中本地缓存…');
    return;
  }
  if (type === 'meta') {
    setScene(data.scene, data.reason);
    state.stageOverride = `判定为「${data.scene}」，正在写…`;
    $('resultPanel').classList.remove('stale');
    return;
  }
  if (type === 'delta') {
    state.streamText += data.text;
    $('resultPanel').classList.remove('stale');
    scheduleRender();
    return;
  }
  if (type === 'done') {
    state.streamText = data.prompt || state.streamText;
    const meta = data.cached
      ? `本地缓存 · ${(data.prompt || '').length} 字`
      : `${((data.latency_ms || 0) / 1000).toFixed(1)}s · ${(data.prompt || '').length} 字`;
    showResult(data, meta);
    state.stageOverride = '';
    if (window.innerWidth <= 1180) {
      $('resultPanel').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    $('promptBody').focus({ preventScroll: true });
    return;
  }
  if (type === 'error') {
    state.streamError = data.message || '改写没能完成，再试一次。';
    showNotice(state.streamError);
  }
}

async function submit() {
  if (state.running) return;
  if (!state.options) {
    showNotice('配置还没加载好，刷新一下页面再试。');
    return;
  }
  const prompt = $('prompt').value.trim();
  if (!prompt) {
    showNotice('先写点什么，再交给它改写。');
    $('prompt').focus();
    return;
  }

  const hadResult = !!state.result;
  const epoch = state.epoch;
  const payload = {
    prompt,
    model: $('model').value,
    scene_type: state.sceneOverride || '',
    style: $('style').value,
    ratio: $('ratio').value,
    duration: $('duration').value,
  };

  hideNotice();
  state.result = null;
  state.streamText = '';
  state.streamError = '';
  state.controller = new AbortController();
  startRunning();

  if (hadResult) {
    $('resultPanel').classList.add('stale');
  } else {
    showResultShell(true);
    setScene('', '正在读你的描述…');
    renderPrompt('', true);
    $('resultPanel').classList.add('stale');
    $('changes').hidden = true;
    $('resultMeta').textContent = '';
  }

  try {
    // epoch 不匹配说明期间清空过，丢弃这次流的事件
    await streamRewrite(payload, (type, data) => {
      if (state.epoch === epoch) handleEvent(type, data);
    }, state.controller.signal);
    if (state.epoch === epoch && !state.result && !state.streamError) {
      showNotice('这次没拿到完整结果，再试一次。');
    }
  } catch (error) {
    if (state.epoch !== epoch) return;   // 已被清空，静默收尾，不再弹提示
    if (error.name === 'AbortError') toast(t('toast.cancelled'));
    else showNotice(error.message || '改写没能完成，再试一次。');
  } finally {
    // 若期间清空过并又开了新请求，旧请求不能碰新请求的状态和按钮
    if (state.epoch === epoch) {
      stopRunning();
      state.controller = null;
      state.stageOverride = '';
      $('resultPanel').classList.remove('stale');
      if (!state.result && !hadResult) showResultShell(false);
    }
  }
}

/* ---------------------------------------------------------------- 历史 */

async function loadHistory() {
  const list = $('historyList');
  try {
    const { items } = await getHistory(30);
    $('historyCount').textContent = items.length ? t('count.records', { n: items.length }) : '';
    list.replaceChildren();
    if (!items.length) {
      const empty = document.createElement('div');
      empty.className = 'history-empty';
      empty.textContent = t('history.empty');
      list.appendChild(empty);
      return;
    }
    for (const item of items) {
      const row = document.createElement('div');
      row.className = 'history-item';

      const main = document.createElement('div');
      main.className = 'history-main';
      const title = document.createElement('div');
      title.className = 'history-title';
      title.textContent = item.input || '(空)';
      const sub = document.createElement('div');
      sub.className = 'history-sub';
      const tag = document.createElement('span');
      tag.className = 'history-tag';
      tag.textContent = item.scene || t('count.unfinished');
      const detail = `${formatTime(item.created_at)} · ${item.model} · ${item.cached ? t('count.cached') : ((item.latency_ms || 0) / 1000).toFixed(1) + 's'}`;
      sub.append(tag, document.createTextNode(detail));
      main.append(title, sub);

      const remove = document.createElement('button');
      remove.type = 'button';
      remove.className = 'history-del';
      remove.textContent = tr('删除');
      remove.addEventListener('click', async (event) => {
        event.stopPropagation();
        try {
          await deleteHistoryItem(item.id);
          toast(t('toast.deleted'));
          loadHistory();
        } catch (error) { toast(error.message); }
      });

      row.append(main, remove);
      row.addEventListener('click', () => openHistoryItem(item.id));
      list.appendChild(row);
    }
  } catch (error) {
    list.replaceChildren();
    const empty = document.createElement('div');
    empty.className = 'history-empty';
    empty.textContent = `读取历史失败：${error.message}`;
    list.appendChild(empty);
  }
}

async function openHistoryItem(id) {
  try {
    const detail = await getHistoryItem(id);
    $('prompt').value = detail.input || '';
    if (detail.model) $('model').value = detail.model;
    if (detail.style) $('style').value = detail.style;
    if (detail.ratio) $('ratio').value = detail.ratio;
    if (detail.duration) $('duration').value = detail.duration;
    onModelChange();
    updateChar();
    state.sceneOverride = '';
    updateOverrideHint();
    switchView('rewrite');
    showResult({
      scene: detail.scene || '',
      reason: detail.reason || '',
      prompt: detail.result_prompt || '',
      changes: detail.changes || [],
    }, `${formatTime(detail.created_at)} · 历史记录`);
    toast(t('toast.revisited'));
  } catch (error) {
    toast(error.message);
  }
}

/* ---------------------------------------------------------------- 事件绑定 */

function bindEvents() {
  $('goBtn').addEventListener('click', submit);
  $('cancelBtn').addEventListener('click', () => state.controller?.abort());
  $('clearBtn').addEventListener('click', () => clearWorkspace());
  $('prompt').addEventListener('input', () => {
    updateChar();
    // 手动把文字删光时，也同步收掉右边的旧结果，避免左右不一致
    if ($('prompt').value.trim() === '' && !$('resultContent').hidden) {
      clearWorkspace({ focus: false });
    }
  });
  $('model').addEventListener('change', onModelChange);

  document.querySelectorAll('.nav-item').forEach((button) => {
    button.addEventListener('click', () => {
      if (button.dataset.soon) {
        toast(`「${button.dataset.soon}」还在路上，位置先留着`);
        return;
      }
      switchView(button.dataset.view);
    });
  });

  $('ambientToggle').addEventListener('click', (event) => {
    event.stopPropagation();
    const panel = $('ambientPanel');
    panel.hidden = !panel.hidden;
    $('ambientToggle').setAttribute('aria-expanded', String(!panel.hidden));
  });

  $('overrideToggle').addEventListener('click', (event) => {
    event.stopPropagation();
    const menu = $('overrideMenu');
    menu.hidden = !menu.hidden;
    $('overrideToggle').setAttribute('aria-expanded', String(!menu.hidden));
  });

  document.addEventListener('click', (event) => {
    if (!event.target.closest('.scene-override')) closeOverride();
    if (!event.target.closest('.ambient-wrap')) closeAmbientPanel();
  });

  document.querySelector('.result-tools').addEventListener('click', async (event) => {
    const button = event.target.closest('[data-action]');
    if (!button || !state.result) return;
    const result = state.result;
    const action = button.dataset.action;

    if (action === 'copy-all' || action === 'copy-prompt') {
      const text = action === 'copy-all' ? fullText(result) : (result.prompt || '');
      const ok = await copyText(text);
      toast(ok ? (action === 'copy-all' ? t('toast.copied') : t('toast.copiedPrompt')) : t('toast.copyFailed'));
      return;
    }
    if (action === 'export') {
      const now = new Date();
      const stamp = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}`;
      downloadText(`prompt-studio-${stamp}.txt`, fullText(result));
      toast(t('toast.exported'));
      return;
    }
    if (action === 'reuse') {
      $('prompt').value = result.prompt || '';
      updateChar();
      switchView('rewrite');
      $('prompt').focus();
      $('prompt').scrollIntoView({ behavior: 'smooth', block: 'center' });
      toast(t('toast.reuse'));
    }
  });

  $('changesHead').addEventListener('click', () => {
    const collapsed = $('changes').classList.toggle('collapsed');
    $('changesHead').setAttribute('aria-expanded', String(!collapsed));
  });

  $('clearHistoryBtn').addEventListener('click', async () => {
    if (!window.confirm(t('history.confirm'))) return;
    try {
      await clearHistory();
      toast(t('toast.historyCleared'));
      loadHistory();
    } catch (error) { toast(error.message); }
  });

  document.addEventListener('keydown', (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
      event.preventDefault();
      submit();
    }
    if (event.key === 'Escape') {
      closeOverride();
      closeAmbientPanel();
    }
  });
}

async function init() {
  initI18n();
  buildLangSwitch();
  onLangChange(refreshAfterLangChange);
  buildParticles();
  bindEvents();
  updateChar();
  try {
    const [options, health] = await Promise.all([getOptions(), getHealth()]);
    state.options = options;
    state.health = health;
    fillSelect('model', options.models.map((m) => [m.value, m.label]));
    fillSelect('style', options.styles.map((s) => [s, s]));
    fillSelect('ratio', options.ratios.map((r) => [r, r]));
    fillSelect('duration', options.durations.map((d) => [d, d]));
    fillSelect('bdStyle', options.styles.map((s) => [s, s]));
    onModelChange();
    renderExamples();
    renderAmbient(options.backgrounds || []);
    renderOverrideMenu(options.scene_types || []);
    initBreakdown(options);
    applyStatus(health);
    if (health.version) $('versionTag').textContent = `v${health.version}`;
  } catch (error) {
    setStatus('bad', t('status.offline'));
    showNotice(`读取配置失败：${error.message}`);
  }
}

/** 顶部语言切换按钮。 */
function buildLangSwitch() {
  const box = $('langSwitch');
  if (!box) return;
  box.replaceChildren();
  LANGS.forEach(([code, label]) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'lang-btn' + (getLang() === code ? ' active' : '');
    button.textContent = label;
    button.dataset.lang = code;
    button.addEventListener('click', () => setLang(code));
    box.appendChild(button);
  });
}

/** 服务状态与演示提示。 */
function applyStatus(health) {
  const banner = $('demoBanner');
  if (banner) banner.hidden = !health.demo_mode;
  setStatus(
    health.demo_mode ? 'warn' : (health.key_configured ? 'ok' : 'bad'),
    health.demo_mode
      ? t('status.demo')
      : (health.key_configured ? t('status.ready') : t('status.noKey')),
  );
}

/** 切换语言后重建所有由 JS 生成的文案。 */
function refreshAfterLangChange() {
  buildLangSwitch();
  updateChar();
  renderExamples();
  if (state.health) applyStatus(state.health);
  if (state.options) {
    renderAmbient(state.options.backgrounds || []);
    renderOverrideMenu(state.options.scene_types || []);
  }
  if (state.result) showResultMetaOnly();
  if ($('view-history').classList.contains('active')) loadHistory();
  if ($('view-breakdown').classList.contains('active')) refreshBreakdown();
}

/** 只刷新结果区里由语言决定的文字（正文本身是模型输出，不翻译）。 */
function showResultMetaOnly() {
  const scene = $('sceneName').textContent;
  if (scene && scene !== '—') setScene(state.result?.scene, state.result?.reason);
}

init();
