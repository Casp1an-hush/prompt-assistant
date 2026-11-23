/* 三语支持：简体中文 / 繁體中文 / English。
   字典按 [简, 繁, 英] 三元组存；静态文案用 data-i18n 标注，
   动态文案用 tr('中文原句') 查表，保证界面切换语言后整体一致。 */

export const LANGS = [
  ['zh-Hans', '简'],
  ['zh-Hant', '繁'],
  ['en', 'EN'],
];

const ENTRIES = {
  /* 品牌与导航 */
  'brand.sub': ['before the image', 'before the image', 'before the image'],
  'nav.workspace': ['工作区', '工作區', 'Workspace'],
  'nav.rewrite': ['改写', '改寫', 'Rewrite'],
  'nav.breakdown': ['剧本拆解', '劇本拆解', 'Breakdown'],
  'nav.history': ['历史记录', '歷史記錄', 'History'],
  'nav.templates': ['模板库', '模板庫', 'Templates'],
  'nav.favorites': ['收藏', '收藏', 'Favorites'],
  'nav.compare': ['多模型对比', '多模型對比', 'Compare'],
  'nav.settings': ['设置', '設定', 'Settings'],
  'nav.rules': ['规则与偏好', '規則與偏好', 'Rules'],

  /* 侧栏状态 */
  'status.connecting': ['正在连接…', '正在連線…', 'Connecting…'],
  'status.ready': ['Ready · 本地服务已就绪', 'Ready · 本機服務已就緒', 'Ready · local service is up'],
  'status.demo': ['Demo mode · 演示模式（离线样例）', 'Demo mode · 演示模式（離線範例）', 'Demo mode · offline sample'],
  'status.noKey': ['No API key · 还没配置 API key', 'No API key · 尚未設定 API key', 'No API key · not configured yet'],
  'status.offline': ['连不上本地服务', '連不上本機服務', 'Cannot reach the local service'],
  'foot.local': ['内容留在本地，不上传。', '內容留在本機，不上傳。', 'Everything stays on your machine.'],

  /* 氛围 */
  'ambient.label': ['氛围', '氛圍', 'Ambience'],
  'ambient.off': ['关', '關', 'Off'],
  'ambient.on': ['开', '開', 'On'],
  'ambient.title': ['背景氛围', '背景氛圍', 'Background ambience'],
  'ambient.note': ['默认关闭，让页面保持安静。', '預設關閉，讓頁面保持安靜。', 'Off by default, to keep the page quiet.'],
  'ambient.closeBg': ['关闭背景', '關閉背景', 'Turn off background'],
  'ambient.name.planet-ship.jpeg': ['星际', '星際', 'Interstellar'],
  'ambient.name.ocean.jpeg': ['海面', '海面', 'Sea'],
  'ambient.name.space-1.jpeg': ['深空', '深空', 'Deep space'],
  'ambient.name.space-window.jpeg': ['舷窗', '舷窗', 'Porthole'],
  'ambient.name.starship.jpeg': ['星舰', '星艦', 'Starship'],

  /* 演示提示 */
  'demo.title': ['Demo mode', 'Demo mode', 'Demo mode'],
  'demo.text': [
    '演示模式 · 当前为离线样例输出，无需 API key；配置 DeepSeek key 即可获得模型实时改写。',
    '演示模式 · 目前為離線範例輸出，無需 API key；設定 DeepSeek key 即可取得模型即時改寫。',
    'Offline sample output — no API key needed. Add a DeepSeek key for live rewriting.',
  ],

  /* 改写页 */
  'rewrite.eyebrow': ['01 — Rewrite', '01 — Rewrite', '01 — Rewrite'],
  'rewrite.desc': ['写下所想，其余由它铺陈', '寫下所想，其餘由它鋪陳', 'Write what you mean — the rest is composed.'],
  'input.title': ['你的想法', '你的想法', 'Your idea'],
  'input.clear': ['清空', '清空', 'Clear'],
  'input.hint': ['支持 ⌘ + Enter 快速开始', '支援 ⌘ + Enter 快速開始', '⌘ + Enter to start'],
  'input.hintShort': ['再补点主体、动作或环境，会更准', '再補點主體、動作或環境，會更準', 'Add a subject, an action or a setting'],
  'input.placeholder': [
    '例如：一个少年在雨夜的天台上追一个黑衣人，镜头越来越快',
    '例如：一個少年在雨夜的天台上追一個黑衣人，鏡頭越來越快',
    'e.g. a boy chases a figure in black across a rooftop in the rain, the cuts getting faster',
  ],
  'field.model': ['目标模型', '目標模型', 'Target model'],
  'field.style': ['画风', '畫風', 'Style'],
  'field.ratio': ['画面比例', '畫面比例', 'Aspect ratio'],
  'field.duration': ['时长（秒）', '時長（秒）', 'Duration (s)'],
  'action.start': ['开始改写', '開始改寫', 'Rewrite'],
  'action.running': ['改写中…', '改寫中…', 'Rewriting…'],
  'action.cancel': ['取消', '取消', 'Cancel'],
  'action.preparing': ['正在准备…', '正在準備…', 'Preparing…'],

  /* 结果区 */
  'result.empty': ['改写好的内容，会安静地出现在这里。', '改寫好的內容，會安靜地出現在這裡。', 'What you shape will appear here, quietly.'],
  'result.sceneLabel': ['自动判定的戏份', '自動判定的戲份', 'Inferred scene'],
  'result.changeScene': ['换个戏份', '換個戲份', 'Change scene'],
  'result.info': [
    '戏份由模型根据你写的内容自动判断，一般不需要自己选；想微调时才用「换个戏份」。',
    '戲份由模型根據你寫的內容自動判斷，一般不需要自己選；想微調時才用「換個戲份」。',
    'The scene is inferred from what you write; use "Change scene" only to fine-tune.',
  ],
  'tools.copyAll': ['复制全文', '複製全文', 'Copy all'],
  'tools.copyPrompt': ['只复制提示词', '只複製提示詞', 'Copy prompt'],
  'tools.export': ['导出 .txt', '匯出 .txt', 'Export .txt'],
  'tools.reuse': ['接着改', '接著改', 'Continue editing'],
  'changes.title': ['改了什么', '改了什么', 'What changed'],
  'scene.auto': ['自动判断（默认）', '自動判斷（預設）', 'Auto (default)'],

  /* 历史页 */
  'history.eyebrow': ['02 — History', '02 — History', '02 — History'],
  'history.title': [
    '写过的，<em>都还在这里</em>', '寫過的，<em>都還在這裡</em>', 'What you wrote, <em>still here</em>',
  ],
  'history.desc': [
    '每次改写都留在本地。点开一条可以回看完整结果，也能直接接着改。',
    '每次改寫都留在本機。點開一則可回看完整結果，也能直接接著改。',
    'Every rewrite stays local. Open one to revisit it, or pick up where you left off.',
  ],
  'history.clear': ['清空全部', '清空全部', 'Clear all'],
  'history.confirm': ['清空全部历史？这个动作不能撤销。', '清空全部歷史？這個動作不能撤銷。', 'Clear all history? This cannot be undone.'],
  'history.empty': ['还没有改写记录。写过一次，这里就会留住它。', '還沒有改寫記錄。寫過一次，這裡就會留住它。', 'Nothing yet. Write once and it stays here.'],

  /* 拆解页 */
  'bd.eyebrow': ['03 — Breakdown', '03 — Breakdown', '03 — Breakdown'],
  'bd.title': [
    '把剧本，<em>拆成可以直接开工的资产</em>', '把劇本，<em>拆成可以直接開工的資產</em>',
    'Turn a script <em>into assets you can start on</em>',
  ],
  'bd.desc': [
    '粘贴按「第一集 / 1-1 / 正文」分好段的剧本，自动列出人物模卡、场景图与道具图，并给出可直接出图的提示词。',
    '貼上按「第一集 / 1-1 / 正文」分好段的劇本，自動列出人物模卡、場景圖與道具圖，並給出可直接出圖的提示詞。',
    'Paste a script split into episode-scene segments; get character cards, scene plates and prop plates with ready-to-use image prompts.',
  ],
  'bd.inputTitle': ['剧本原文', '劇本原文', 'Script'],
  'bd.formatHint': [
    '集名一行、场次号一行、正文；单次上限 3 万字',
    '集名一行、場次號一行、正文；單次上限 3 萬字',
    'Episode on its own line, then 1-1, then the text · up to 30,000 characters',
  ],
  'bd.template': ['插入格式示例', '插入格式範例', 'Insert format example'],
  'bd.styleLabel': ['全片画风', '全片畫風', 'Style for the whole film'],
  'bd.styleHint': [
    '所有资产的提示词都会带上同一个风格锚定句',
    '所有資產的提示詞都會帶上同一個風格錨定句',
    'Every asset prompt carries the same style anchor',
  ],
  'bd.start': ['开始拆解', '開始拆解', 'Break down'],
  'bd.running': ['正在拆解…', '正在拆解…', 'Breaking down…'],
  'bd.runningHint': [
    '长剧本可能需要一两分钟，请不要关闭页面',
    '長劇本可能需要一兩分鐘，請不要關閉頁面',
    'A long script can take a minute or two — please keep this page open',
  ],
  'bd.empty': ['拆解结果会出现在这里。', '拆解結果會出現在這裡。', 'Results will appear here.'],
  'bd.tab.characters': ['人物模卡', '人物模卡', 'Characters'],
  'bd.tab.scenes': ['场景图', '場景圖', 'Scenes'],
  'bd.tab.props': ['道具图', '道具圖', 'Props'],
  'bd.export': ['导出 Markdown', '匯出 Markdown', 'Export Markdown'],
  'bd.promptLabel': ['出图提示词', '出圖提示詞', 'Image prompt'],
  'bd.copy': ['复制', '複製', 'Copy'],
  'bd.placeholder': [
    '第一集\n1-1\n【场景】雨夜天台\n【人物】林晚、陈默\n正文……\n1-2\n正文……',
    '第一集\n1-1\n【場景】雨夜天台\n【人物】林晚、陳默\n正文……\n1-2\n正文……',
    'Episode 1\n1-1\n[Scene] rooftop, rainy night\n[Cast] Lin Wan, Chen Mo\nbody text…\n1-2\nbody text…',
  ],

  /* 戏份名（模型输出的是中文类型名，界面按语言显示） */
  'scene.叙事戏': ['叙事戏', '敘事戲', 'Narrative'],
  'scene.动作戏': ['动作戏', '動作戲', 'Action'],
  'scene.对话戏': ['对话戏', '對話戲', 'Dialogue'],
  'scene.悬疑戏': ['悬疑戏', '懸疑戲', 'Suspense'],
  'scene.环境戏': ['环境戏', '環境戲', 'Establishing'],
  'scene.恐怖戏': ['恐怖戏', '恐怖戲', 'Horror'],

  'scene.judging': ['正在判断…', '正在判斷…', 'Inferring…'],
  'toast.override': ['下次按「{v}」改写，点开始改写生效', '下次按「{v}」改寫，點開始改寫生效', 'Next time as "{v}" — press Rewrite to apply'],

  /* 计数与单位 */
  'count.chars': ['{n} 字', '{n} 字', '{n} chars'],
  'count.segments': ['{n} 个分场', '{n} 個分場', '{n} segments'],
  'count.records': ['共 {n} 条', '共 {n} 條', '{n} entries'],
  'count.cached': ['缓存', '快取', 'cached'],
  'count.unfinished': ['未完成', '未完成', 'incomplete'],
  'unit.chars': ['字', '字', 'chars'],

  /* 示例 */
  'example.chase.label': ['动作 · 追逐', '動作 · 追逐', 'Action · Chase'],
  'example.chase.text': [
    '一个少年在雨夜的天台上追一个黑衣人，镜头越来越快',
    '一個少年在雨夜的天台上追一個黑衣人，鏡頭越來越快',
    'a boy chases a figure in black across a rooftop in the rain, the cuts getting faster',
  ],
  'example.cat.label': ['环境 · 窗台', '環境 · 窗台', 'Setting · Window'],
  'example.cat.text': [
    '一只橘猫趴在窗台上看雪，午后，屋里很暖',
    '一隻橘貓趴在窗台上看雪，午後，屋裡很暖',
    'an orange cat on a windowsill watching the snow, warm afternoon light indoors',
  ],
  'example.product.label': ['静物 · 香水', '靜物 · 香水', 'Still life · Perfume'],
  'example.product.text': [
    '一瓶香水放在大理石台面上，旁边有一束干花，柔和的自然光',
    '一瓶香水放在大理石檯面上，旁邊有一束乾花，柔和的自然光',
    'a perfume bottle on a marble counter, a bunch of dried flowers beside it, soft daylight',
  ],

  /* 拆解卡片字段 */
  'f.gender': ['性别', '性別', 'Gender'],
  'f.age': ['年龄', '年齡', 'Age'],
  'f.personality': ['性格', '性格', 'Personality'],
  'f.appearance': ['外貌', '外貌', 'Appearance'],
  'f.costume': ['服饰', '服飾', 'Costume'],
  'f.note': ['出现场次', '出現場次', 'Appears in'],
  'f.time': ['时间', '時間', 'Time'],
  'f.era': ['时代与地点', '時代與地點', 'Era and place'],
  'f.architecture': ['建筑与材质', '建築與材質', 'Architecture'],
  'f.lighting': ['光线氛围', '光線氛圍', 'Lighting'],
  'f.material': ['材质', '材質', 'Material'],
  'f.size': ['尺寸', '尺寸', 'Size'],
  'f.color': ['颜色', '顏色', 'Colour'],
  'f.detail': ['关键细节', '關鍵細節', 'Key detail'],
  'f.anchors': ['一致性锚点', '一致性錨點', 'Consistency anchors'],
  'bd.filename': ['剧本拆解.md', '劇本拆解.md', 'script-breakdown.md'],
  'bd.pasteFirst': ['先把剧本粘进来。', '先把劇本貼進來。', 'Paste the script first.'],
  'bd.failed': ['拆解失败，请重试。', '拆解失敗，請重試。', 'Breakdown failed — try again.'],
  'bd.nothingToExport': ['还没有可导出的结果。', '還沒有可匯出的結果。', 'Nothing to export yet.'],

  /* 动态提示 */
  'toast.copied': ['已复制全文', '已複製全文', 'Copied'],
  'toast.copiedPrompt': ['已复制提示词', '已複製提示詞', 'Prompt copied'],
  'toast.copyFailed': ['复制没成功，可以选中正文手动复制', '複製沒成功，可以選取正文手動複製', 'Copy failed — select the text manually'],
  'toast.exported': ['已导出 .txt', '已匯出 .txt', 'Exported .txt'],
  'toast.reuse': ['已放回输入框，改几个字再试', '已放回輸入框，改幾個字再試', 'Back in the input box — adjust and retry'],
  'toast.cancelled': ['已取消这次改写', '已取消這次改寫', 'Rewrite cancelled'],
  'toast.deleted': ['已删除这条记录', '已刪除這筆記錄', 'Entry deleted'],
  'toast.historyCleared': ['历史已清空', '歷史已清空', 'History cleared'],
  'toast.revisited': ['已回看这条记录', '已回看這筆記錄', 'Loaded from history'],
  'toast.autoScene': ['已恢复自动判断', '已恢復自動判斷', 'Back to automatic scene'],
  'toast.ambientOff': ['已关闭背景氛围', '已關閉背景氛圍', 'Background ambience off'],
  'toast.mdExported': ['已导出 Markdown', '已匯出 Markdown', 'Markdown exported'],
  'toast.done': ['拆解完成', '拆解完成', 'Breakdown finished'],
  'toast.doneDemo': ['拆解完成（演示模式）', '拆解完成（演示模式）', 'Breakdown finished (demo)'],
  'notice.emptyPrompt': ['先写点什么，再交给它改写。', '先寫點什麼，再交給它改寫。', 'Write something first.'],
  'notice.noResult': ['这次没拿到完整结果，再试一次。', '這次沒拿到完整結果，再試一次。', 'Incomplete result — try again.'],
  'notice.failed': ['改写没能完成，再试一次。', '改寫沒能完成，再試一次。', 'Rewrite failed — try again.'],
  'notice.configLoading': ['配置还没加载好，刷新一下页面再试。', '設定還沒載入完成，重新整理頁面再試。', 'Configuration is not loaded yet — reload the page.'],
  'notice.cached': ['命中本地缓存…', '命中本機快取…', 'Served from local cache…'],
  'notice.judging': ['正在判断这是什么戏份…', '正在判斷這是什麼戲份…', 'Inferring the scene…'],
  'notice.reading': ['正在读你的描述…', '正在讀你的描述…', 'Reading your description…'],
  'notice.organizing': ['正在组织镜头与细节…', '正在組織鏡頭與細節…', 'Composing shots and details…'],
  'notice.changes': ['正在整理改动说明…', '正在整理改動說明…', 'Summarising the changes…'],

  /* 错误码：优先用 code 本地化，服务端文案只作兜底 */
  'error.config': ['还没配置 DeepSeek key。请在项目目录的 .env 里填入 DEEPSEEK_API_KEY，然后重启服务。',
    '尚未設定 DeepSeek key。請在專案目錄的 .env 填入 DEEPSEEK_API_KEY，然後重新啟動服務。',
    'No DeepSeek key configured. Put DEEPSEEK_API_KEY in .env and restart.'],
  'error.busy': ['同时最多处理 {n} 个请求，等前一个完成再试。', '同時最多處理 {n} 個請求，等前一個完成再試。',
    'At most {n} requests at once — wait for the previous one.'],
  'error.auth': ['API key 无效或已失效，请重新填一次 key 再试。', 'API key 無效或已失效，請重新填一次 key 再試。',
    'The API key is invalid or expired. Re-enter it and try again.'],
  'error.balance': ['DeepSeek 账户余额不足，去 platform.deepseek.com 充值后再试。',
    'DeepSeek 帳戶餘額不足，到 platform.deepseek.com 儲值後再試。',
    'Out of credit on DeepSeek — top up and try again.'],
  'error.rate_limit': ['请求有点频繁，稍等几秒再试一次。', '請求有點頻繁，稍等幾秒再試一次。', 'Too many requests — wait a few seconds.'],
  'error.upstream': ['DeepSeek 服务暂时不可用，稍后再试。', 'DeepSeek 服務暫時無法使用，稍後再試。', 'DeepSeek is unavailable right now.'],
  'error.timeout': ['请求超时了，检查网络后再试一次。', '請求逾時，檢查網路後再試一次。', 'Request timed out — check the network.'],
  'error.network': ['连不上 DeepSeek，检查网络或代理设置。', '連不上 DeepSeek，檢查網路或代理設定。', 'Cannot reach DeepSeek — check network or proxy.'],
  'error.unknown': ['发生了未预期的错误，再试一次。', '發生了未預期的錯誤，再試一次。', 'Something unexpected happened — try again.'],
  'error.empty': ['请先写点什么。', '請先寫點什麼。', 'Please write something first.'],
  'error.unknown_model': ['未知模型。', '未知模型。', 'Unknown model.'],
  'error.tooShort': ['内容太短，至少要有一段完整的剧情。', '內容太短，至少要有一段完整的劇情。', 'Too short — include at least one full scene.'],
  'error.tooLong': ['文本 {n} 字，超过 {m} 字上限，请先分成几批再提交。', '文字 {n} 字，超過 {m} 字上限，請先分成幾批再提交。',
    'The text is {n} characters, over the {m} limit — split it into batches.'],
  'error.no_episode': [
    '没有检测到「第一集」这样的集名行。剧本需要：集名一行、场次号一行、正文。例如：\n第一集\n1-1\n（正文）',
    '沒有偵測到「第一集」這樣的集名行。劇本需要：集名一行、場次號一行、正文。例如：\n第一集\n1-1\n（正文）',
    'No episode line found. Format: episode line, then 1-1, then the text. e.g.\nEpisode 1\n1-1\n(body)',
  ],
  'error.no_scenes': [
    '没有检测到场次号。每场需要单独一行写「1-1」「1-2」。例如：\n第一集\n1-1\n（正文）',
    '沒有偵測到場次號。每場需要單獨一行寫「1-1」「1-2」。例如：\n第一集\n1-1\n（正文）',
    'No scene numbers found. Put 1-1, 1-2 … on their own lines, e.g.\nEpisode 1\n1-1\n(body)',
  ],
  'error.breakdownJson': ['模型返回的内容不是有效 JSON，请重试一次。', '模型回傳的內容不是有效 JSON，請重試一次。',
    'The model did not return valid JSON — try again.'],
  'error.fetch': ['请求失败：{msg}', '請求失敗：{msg}', 'Request failed: {msg}'],
};

/* 中文原文 → key 的反查表，用于 tr('已复制全文') 这种写法 */
const BY_ZH = new Map();
for (const [key, values] of Object.entries(ENTRIES)) {
  BY_ZH.set(values[0], key);
}

let current = 'zh-Hans';
const listeners = new Set();

function readSaved() {
  try {
    const saved = localStorage.getItem('ps-lang');
    if (LANGS.some(([code]) => code === saved)) return saved;
  } catch { /* 隐私模式 */ }
  const nav = (navigator.language || 'zh-Hans').toLowerCase();
  if (nav.startsWith('zh')) return /hant|tw|hk|mo/.test(nav) ? 'zh-Hant' : 'zh-Hans';
  return 'en';
}

export function getLang() {
  return current;
}

export function setLang(code) {
  if (!LANGS.some(([value]) => value === code)) return;
  current = code;
  try { localStorage.setItem('ps-lang', code); } catch { /* 隐私模式 */ }
  document.documentElement.lang = code === 'en' ? 'en' : code === 'zh-Hant' ? 'zh-Hant' : 'zh-CN';
  applyStatic();
  listeners.forEach((fn) => fn(code));
}

export function onLangChange(fn) {
  listeners.add(fn);
}

/** 取词条；缺失时返回 key 本身，便于发现漏翻。 */
export function t(key, vars) {
  const values = ENTRIES[key];
  if (!values) return key;
  const index = current === 'zh-Hans' ? 0 : current === 'zh-Hant' ? 1 : 2;
  let text = values[index] || values[0];
  if (vars) {
    Object.entries(vars).forEach(([name, value]) => {
      text = text.split('{' + name + '}').join(String(value));
    });
  }
  return text;
}

/** 用中文原句查表；查不到就原样返回（例如模型生成的正文）。 */
export function tr(text) {
  const key = BY_ZH.get(text);
  return key ? t(key) : text;
}

/** 应用所有 data-i18n 标注的静态文案。 */
export function applyStatic(root = document) {
  root.querySelectorAll('[data-i18n]').forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  root.querySelectorAll('[data-i18n-html]').forEach((el) => {
    el.innerHTML = t(el.dataset.i18nHtml);
  });
  root.querySelectorAll('[data-i18n-ph]').forEach((el) => {
    el.setAttribute('placeholder', t(el.dataset.i18nPh));
  });
  root.querySelectorAll('[data-i18n-title]').forEach((el) => {
    const value = t(el.dataset.i18nTitle);
    el.setAttribute('title', value);
    el.setAttribute('aria-label', value);
  });
}

export function initI18n() {
  current = readSaved();
  document.documentElement.lang = current === 'en' ? 'en' : current === 'zh-Hant' ? 'zh-Hant' : 'zh-CN';
  applyStatic();
}
