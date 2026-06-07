/**
 * 아기고양이 임시 집사 v2.0 — Vercel Serverless Function (Gemini Flash 프록시)
 * ────────────────────────────────────────────────────────────────────────
 * 왜 Vercel 인가:
 *   Cloudflare Workers 에서 Gemini 를 부르면 "User location is not supported"(지역 차단)가
 *   자주 발생한다. Vercel 의 Node 서버리스 함수는 미국(US, iad1) 리전에서 실행되므로
 *   Gemini 가 허용된다. (Edge 런타임이 아니라 Node 서버리스여야 리전이 고정됨)
 *
 * 보안(가이드라인 1장):
 *   - Gemini API Key 는 Vercel 환경변수 GEMINI_API_KEY 에만 저장한다.
 *   - 브라우저(index.html)는 이 함수 주소(/api/generate-cat-text)만 호출한다. 키는 절대 노출 안 됨.
 *
 * 호출: POST /api/generate-cat-text   body = 게임이 보내는 payload(JSON)
 * 응답: { "text": "..." }  (실패 시 text:null → 게임은 기존 내장 fallback 문장으로 진행)
 */

const GEMINI_MODEL = "gemini-2.5-flash";

// 이 API 를 호출할 수 있는 출처(origin) 허용 목록. 본인 GitHub Pages 주소.
const ALLOWED_ORIGIN_PREFIXES = [
  "https://youngs2000-pixel.github.io",
  "http://localhost",
  "http://127.0.0.1",
];

function setCors(req, res) {
  const origin = req.headers.origin || "";
  const allow = ALLOWED_ORIGIN_PREFIXES.some((p) => origin.startsWith(p))
    ? origin
    : ALLOWED_ORIGIN_PREFIXES[0];
  res.setHeader("Access-Control-Allow-Origin", allow);
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Vary", "Origin");
}

module.exports = async function handler(req, res) {
  setCors(req, res);

  if (req.method === "OPTIONS") {
    res.status(204).end();
    return;
  }
  if (req.method !== "POST") {
    res.status(405).json({ text: null, error: "Only POST allowed." });
    return;
  }
  if (!process.env.GEMINI_API_KEY) {
    res.status(500).json({ text: null, error: "GEMINI_API_KEY not set." });
    return;
  }

  try {
    let payload = req.body;
    if (typeof payload === "string") {
      try { payload = JSON.parse(payload); } catch (e) { payload = {}; }
    }
    payload = payload || {};

    const prompt = buildPrompt(payload);

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-goog-api-key": process.env.GEMINI_API_KEY,
        },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: {
            temperature: 1.0,
            topP: 0.95,
            maxOutputTokens: 512,
            // 2.5-flash 는 thinking 에 토큰을 먼저 쓰므로 끄지 않으면 빈 응답이 날 수 있음
            thinkingConfig: { thinkingBudget: 0 },
          },
        }),
      }
    );

    if (!response.ok) {
      const detail = await response.text();
      console.warn("Gemini error", response.status, detail);
      res.status(502).json({ text: null, error: "Gemini request failed.", status: response.status, detail: detail.slice(0, 600) });
      return;
    }

    const data = await response.json();
    let text = (data && data.candidates && data.candidates[0] &&
      data.candidates[0].content && data.candidates[0].content.parts &&
      data.candidates[0].content.parts[0] && data.candidates[0].content.parts[0].text) || "";
    text = String(text).trim();
    // 모델이 {"text":"..."} 로 답하면 안쪽 텍스트만 사용
    if (text.startsWith("{")) {
      try { const o = JSON.parse(text); if (o && o.text) text = String(o.text).trim(); } catch (e) {}
    }
    if (!text) {
      res.status(502).json({ text: null, error: "Empty response." });
      return;
    }
    res.status(200).json({ text });
  } catch (error) {
    console.warn("function exception", error);
    res.status(500).json({ text: null, error: "AI generation failed." });
  }
};

// ──────────────────────────────────────────────
// 프롬프트 빌더 (가이드라인 5장: 짧고 안정적으로 / 타입별 맞춤)
// ──────────────────────────────────────────────
const COMMON = `너는 초등학생이 플레이하는 따뜻한 아기고양이 돌보기 게임의 문장 작가야.
- 한국어로, 초등학교 5학년도 이해할 수 있게 쉽게 쓴다.
- 귀엽고 따뜻하고 살짝 재미있게 쓴다.
- 무섭거나 슬프거나 잔인한 표현은 쓰지 않는다. 고양이가 아프더라도 심각하게 묘사하지 않는다.
- 게임의 수치나 별점은 절대 바꾸지 않고, 숫자를 직접 언급하지도 않는다.
- 오직 화면에 보여줄 이야기 문장만 쓴다. 따옴표나 JSON 없이 문장만 출력한다.`;

function statLine(s) {
  if (!s) return "";
  return `현재 상태(0~100): 배고픔 ${s.hunger}, 기분 ${s.mood}, 건강 ${s.health}, 졸림 ${s.sleep}, 친밀도 ${s.affection}.`;
}
function changeLine(c) {
  if (!c) return "";
  const map = { hunger: "배고픔", mood: "기분", health: "건강", sleep: "졸림", affection: "친밀도" };
  const parts = [];
  for (const k in c) { if (!c[k]) continue; parts.push(`${map[k] || k} ${c[k] > 0 ? "+" + c[k] : c[k]}`); }
  return parts.length ? `방금 수치 변화: ${parts.join(", ")}.` : "";
}
function persLine(p) { return `고양이 이름은 ${p.catName}, 성격은 ${p.catPersonality}(${p.catPersonalityDesc || ""}).`; }
function dayEventLine(p) { return `오늘은 ${p.currentDay}일차${p.currentEvent ? ", 오늘의 이벤트는 '" + p.currentEvent + "'" : ""}.`; }

function buildPrompt(p) {
  const t = p && p.type;
  let body;

  if (t === "food_reaction") {
    body = [
      persLine(p), dayEventLine(p),
      `플레이어 ${p.playerName}가 방금 '${p.selectedFood}'를 줬어.`,
      statLine(p.stats), changeLine(p.resultChanges),
      p.tummyUpset ? "이 음식은 오늘 고양이 배에 살짝 안 맞았어(아주 심하지 않게)." : "",
      "이 상황에 맞는 고양이 반응을 2~3문장으로 써줘. 성격, 이벤트, 배고픔/졸림/기분을 자연스럽게 반영해.",
    ];
  } else if (t === "item_reaction") {
    body = [
      persLine(p), dayEventLine(p),
      `플레이어 ${p.playerName}가 방금 '${p.selectedItem}'(${p.itemType === "play" ? "놀이 아이템" : "돌봄 아이템"})을 사용했어.`,
      statLine(p.stats), changeLine(p.resultChanges),
      p.situation ? `특별 상황: ${p.situation}.` : "",
      "고양이 반응을 2~3문장으로 써줘. 놀이 아이템은 귀엽고 장난스럽게, 돌봄 아이템은 편안하고 회복되는 느낌으로. 졸림이 높으면 너무 활발하게 표현하지 마.",
    ];
  } else if (t === "owner_review") {
    body = [
      `고양이 이름은 ${p.catName}, 돌본 어린이는 ${p.playerName}.`, dayEventLine(p),
      `오늘 별점은 ${p.earnedStars}점(5점 만점).`, statLine(p.stats),
      p.todayActionsSummary && p.todayActionsSummary.length ? `오늘 한 일: ${p.todayActionsSummary.join(", ")}.` : "",
      "고양이 주인이 어린이에게 하는 따뜻한 평가 멘트를 2~3문장으로 써줘. 5점이면 크게 칭찬, 3점이면 부드러운 조언, 1~2점이면 걱정은 하되 혼내지 말고 격려해줘. 무엇을 잘했고 무엇을 개선하면 좋을지 살짝 알려줘.",
    ];
  } else if (t === "cat_diary") {
    body = [
      persLine(p), dayEventLine(p),
      p.todayActionsSummary && p.todayActionsSummary.length ? `오늘 ${p.playerName}가 해준 일: ${p.todayActionsSummary.join(", ")}.` : "",
      statLine(p.stats || p.endingStats),
      "고양이가 직접 쓰는 일기를 1인칭으로 3문장 이내로 써줘. 귀엽고 따뜻하게, 너무 길게 말하지 말고, 마지막은 '냐아', '야옹', '골골골' 같은 고양이 느낌으로 끝내줘. 오늘의 사건과 플레이어가 해준 일을 반영해.",
    ];
  } else if (t === "ending_letter") {
    body = [
      `고양이 이름은 ${p.catName}, 성격은 ${p.catPersonality}. 7일 동안 ${p.playerName}가 돌봤어.`,
      `엔딩 종류: ${p.endingType}. 총 별점 ${p.totalStars}, 하루 평균 ${p.averageStars}점.`,
      statLine(p.finalStats),
      "고양이 또는 고양이 주인이 어린이에게 보내는 짧은 편지를 4~6문장으로 써줘. '최고의 집사 엔딩'이면 감동적이고 뿌듯하게, '괜찮은 집사 엔딩'이면 따뜻하고 격려하듯, '아쉬운 집사 엔딩'이면 절대 비난하지 말고 '다음엔 더 잘할 수 있어' 같은 희망적인 느낌으로. 어린이가 기분 좋게 마무리하도록 써줘.",
    ];
  } else {
    body = [`게임 상황: ${JSON.stringify(p)}`, "이 상황에 어울리는 귀여운 아기고양이 문장을 2~3문장으로 써줘."];
  }

  return COMMON + "\n\n" + body.filter(Boolean).join(" ");
}
