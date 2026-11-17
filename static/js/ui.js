/* 渲染小工具：与业务状态无关，可复用到以后的新模块。 */

export const $ = (id) => document.getElementById(id);

let toastTimer;
export function toast(message) {
  const el = $('toast');
  el.textContent = message;
  el.classList.add('on');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('on'), 2400);
}

/* 六种戏份的线性图标，颜色统一用 currentColor */
const SCENE_PATHS = {
  '叙事戏': '<path d="M4 7h16M4 12h11M4 17h14"/><circle cx="18" cy="17" r="1.4"/>',
  '动作戏': '<path d="M13 3 5 13h6l-1 8 9-11h-6z"/>',
  '对话戏': '<path d="M4 5h11a2 2 0 0 1 2 2v5H8l-4 3z"/><path d="M9 16h8l3 3v-3h1a2 2 0 0 0 2-2V9"/>',
  '悬疑戏': '<circle cx="10.5" cy="10.5" r="6"/><path d="m15 15 5 5"/><path d="M10.5 8v3M10.5 13.2v.2"/>',
  '环境戏': '<path d="M3 18h18M5 18l5-8 4 5 2-3 3 6"/><circle cx="17" cy="7" r="2"/>',
  '恐怖戏': '<path d="M12 3a8 8 0 1 0 8 8 6 6 0 0 1-8-8z"/><path d="M6 18h12"/>',
};

export function sceneIcon(name) {
  const body = SCENE_PATHS[name] || SCENE_PATHS['叙事戏'];
  return `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`;
}

/* 轻量语法高亮：全部用 textContent 生成，不会把模型输出当 HTML 执行 */
const TOKEN_RE = /(【[^】]*】|\[[^\]\n]*\d[^\]\n]*\]|@[^\s=,，。；;]+|<[^>\n]+>|\([^)\n]+\)|\{[^}\n]+\})/g;

function tokenSpan(token) {
  let cls = 'audio';
  if (token.startsWith('【')) cls = 'sec';
  else if (token.startsWith('[')) cls = 'time';
  else if (token.startsWith('@')) cls = 'ref';
  const span = document.createElement('span');
  span.className = cls;
  span.textContent = token;
  return span;
}

export function highlight(text) {
  const frag = document.createDocumentFragment();
  const lines = (text || '').split('\n');
  lines.forEach((line, index) => {
    if (index) frag.appendChild(document.createTextNode('\n'));
    let last = 0;
    for (const match of line.matchAll(TOKEN_RE)) {
      if (match.index > last) {
        frag.appendChild(document.createTextNode(line.slice(last, match.index)));
      }
      frag.appendChild(tokenSpan(match[0]));
      last = match.index + match[0].length;
    }
    if (last < line.length) frag.appendChild(document.createTextNode(line.slice(last)));
  });
  return frag;
}

export async function copyText(text) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch { /* 落到下面的降级方案 */ }

  const helper = document.createElement('textarea');
  helper.value = text;
  helper.setAttribute('readonly', '');
  helper.style.cssText = 'position:fixed;top:-2000px;opacity:0';
  document.body.appendChild(helper);
  helper.select();
  let ok = false;
  try { ok = document.execCommand('copy'); } catch { /* 浏览器拒绝 */ }
  helper.remove();
  return ok;
}

export function downloadText(filename, text) {
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function formatTime(ts) {
  const d = new Date(ts * 1000);
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getMonth() + 1}月${d.getDate()}日 ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function fullText(result) {
  const lines = [];
  if (result.scene) lines.push(`戏份：${result.scene}`);
  if (result.reason) lines.push(`判断依据：${result.reason}`);
  lines.push('', result.prompt || '');
  if (result.changes && result.changes.length) {
    lines.push('', '改了什么', ...result.changes.map((c, i) => `${i + 1}. ${c}`));
  }
  return lines.join('\n');
}
