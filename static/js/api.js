/* 请求层：所有后端调用集中在这里。
   流式用 fetch + ReadableStream 读 SSE（EventSource 不支持 POST），
   因此取消、超时、错误处理都能统一走 AbortController。 */

import { t } from './i18n.js';

async function parseJSON(res) {
  try { return await res.json(); } catch { return {}; }
}

async function request(path, options = {}) {
  const res = await fetch(path, options);
  const data = await parseJSON(res);
  if (!res.ok) {
    const error = new Error(localized(data, res.status));
    error.code = data.code || 'http';
    error.status = res.status;
    throw error;
  }
  return data;
}

/** 优先用错误码本地化，服务端文案只作兜底。 */
function localized(data, status) {
  const key = data.code ? `error.${data.code}` : '';
  if (key) {
    const text = t(key);
    if (text !== key) return text;
  }
  return data.message || data.error || t('error.unknown');
}

export const getOptions = () => request('/api/options');
export const getHealth = () => request('/api/health');
export const getHistory = (limit = 30) => request(`/api/history?limit=${limit}`);
export const getHistoryItem = (id) => request(`/api/history/${encodeURIComponent(id)}`);
export const deleteHistoryItem = (id) => request(`/api/history/${encodeURIComponent(id)}`, { method: 'DELETE' });
export const clearHistory = () => request('/api/history', { method: 'DELETE' });

export const rewriteSync = (payload, signal) => request('/api/rewrite', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload),
  signal,
});

/** 逐事件回调：onEvent(type, data)，type ∈ start/meta/delta/done/error。 */
export async function streamRewrite(payload, onEvent, signal) {
  const res = await fetch('/api/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal,
  });

  if (!res.ok) {
    const data = await parseJSON(res);
    const error = new Error(localized(data, res.status));
    error.code = data.code || 'http';
    error.status = res.status;
    throw error;
  }
  if (!res.body) {
    throw new Error('当前浏览器不支持流式读取，请换用新版 Chrome 或 Safari。');
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true }).replace(/\r/g, '');

      let boundary;
      while ((boundary = buffer.indexOf('\n\n')) !== -1) {
        const block = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);

        let event = 'message';
        let raw = '';
        for (const line of block.split('\n')) {
          if (line.startsWith('event:')) event = line.slice(6).trim();
          else if (line.startsWith('data:')) raw += line.slice(5).trim();
        }
        if (!raw) continue;
        let data;
        try { data = JSON.parse(raw); } catch { continue; }
        onEvent(event, data);
      }
    }
  } finally {
    try { reader.releaseLock(); } catch { /* 已释放 */ }
  }
}
