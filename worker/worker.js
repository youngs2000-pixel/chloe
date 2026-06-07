/**
 * 아기고양이 임시 집사 v2.0 — Cloudflare Worker (Gemini Flash 프록시)
 * ────────────────────────────────────────────────────────────────
 * 브라우저(index.html)는 이 Worker 로만 요청을 보내고,
 * Gemini API Key 는 Worker 의 환경변수(시크릿) GEMINI_API_KEY 에만 저장됩니다.
 * → 브라우저는 절대 키를 알 수 없습니다. (가이드라인 1장 준수)
 *
 * 배포 전 준비:
 *   1) npm i -g wrangler
 *   2) wrangler login
 *   3) wrangler secret put GEMINI_API_KEY   (Google AI Studio 에서 발급한 키 입력)
 *   4) wrangler deploy
 * 배포 후 나오는 https://....workers.dev 주소를 index.html 의 AI_ENDPOINT 에 넣으세요.
 */

// 이 Worker 를 호출할 수 있는 출처(origin) 허용 목록.
// 본인 GitHub Pages 주소로 바꾸거나 추가하세요.
const ALLOWED_ORIGIN_PREFIXES = [
  "https://youngs2000-pixel.github.io",
  "http://localhost",
  "http://127.0.0.1",
  "null", // 로컬에서 index.html 을 더블클릭(file://)으로 열 때
];

const GEMINI_MODEL = "gemini-2.0-flash";

function corsHeaders(origin) {
  const allow = (origin && ALLOWED_ORIGIN_PREFIXES.some(p => origin.startsWith(p))) ? origin : ALLOWED_ORIGIN_PREFIXES[0];
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}

function json(body, status, origin) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders(origin) },
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin");

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }
    if (request.method !== "POST") {
      return json({ error: "POST only" }, 405, origin);
    }
    if (!env.GEMINI_API_KEY) {
      return json({ error: "GEMINI_API_KEY not configured" }, 500, origin);
    }

    let payload;
    try {
      payload = await request.json();
    } catch (e) {
      return json({ error: "invalid json" }, 400, origin);
    }

    const userPrompt = buildUserPrompt(payload);
    if (!userPrompt) {
      return json({ error: "unknown type" }, 400, origin);
    }

    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;
      const gemRes = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-goog-api-key": env.GEMINI_API_KEY,
        },
        body: JSON.stringify({
          systemInstruction: { parts: [{ text: COMMON_INSTRUCTION }] },
          contents: [{ role: "user", parts: [{ text: userPrompt }] }],
          generationConfig: {
            temperature: 1.0,
            topP: 0.95,
            maxOutputTokens: 512,
            responseMimeType: "application/json",
            responseSchema: {
              type: "object",
              properties: { text: { type: "string" } },
              required: ["text"],
            },
          },
        }),
      });

      if (!gemRes.ok) {
        const detail = await gemRes.text();
        console.warn("Gemini error", gemRes.status, detail);
        return json({ error: "gemini failed", status: gemRes.status }, 502, origin);
      }

      const data = await gemRes.json();
      const raw = data?.candidates?.[0]?.content?.parts?.[0]?.text || "";
      let text = "";
      try {
        text = (JSON.parse(raw).text || "").trim();
      } catch (e) {
        text = raw.trim(); // JSON 파싱 실패 시 원문이라도 사용
      }
      if (!text) return json({ error: "empty" }, 502, origin);
      return json({ text }, 200, origin);
    } catch (e) {
      console.warn("worker exception", e);
      return json({ error: "exception" }, 502, origin);
    }
  },
};

// ──────────────────────────────────────────────
// 프롬프트 (가이드라인 5장: 짧고 안정적으로)
// ──────────────────────────────────────────────
const COMMON_INSTRUCTION = `너는 초등학생이 플레이하는 따뜻한 아기고양이 돌보기 게임의 문장 작가야.
규칙:
- 한국어로, 초등학교 5학년도 이해할 수 있게 쉽게 쓴다.
- 귀엽고 따뜻하고 살짝 재미있게 쓴다.
- 무섭거나 슬프거나 잔인한 표현은 쓰지 않는다. 고양이가 아프더라도 심각하거나 충격적으로 묘사하지 않는다.
- 게임의 수치나 별점은 절대 바꾸지 않고, 언급하지도 않는다. 오직 화면에 보여줄 이야기 문장만 만든다.
- 반드시 {"text": "..."} 형식의 JSON 으로만 답한다.`;

function statLine(s) {
  if (!s) return "";
  return `현재 상태(0~100): 배고픔 ${s.hunger}, 기분 ${s.mood}, 건강 ${s.health}, 졸림 ${s.sleep}, 친밀도 ${s.affection}.`;
}
function changeLine(c) {
  if (!c) return "";
  const parts = [];
  const map = { hunger: "배고픔", mood: "기분", health: "건강", sleep: "졸림", affection: "친밀도" };
  for (const k in c) {
    if (c[k] === 0 || c[k] == null) continue;
    const v = c[k];
    parts.push(`${map[k] || k} ${v > 0 ? "+" + v : v}`);
  }
  return parts.length ? `방금 수치 변화: ${parts.join(", ")}.` : "";
}
function persLine(p) {
  return `고양이 이름은 ${p.catName}, 성격은 ${p.catPersonality}(${p.catPersonalityDesc || ""}).`;
}
function dayEventLine(p) {
  return `오늘은 ${p.currentDay}일차${p.currentEvent ? ", 오늘의 이벤트는 '" + p.currentEvent + "'" : ""}.`;
}

function buildUserPrompt(p) {
  switch (p && p.type) {
    case "food_reaction":
      return [
        persLine(p), dayEventLine(p),
        `플레이어 ${p.playerName}가 방금 '${p.selectedFood}'를 줬어.`,
        statLine(p.stats), changeLine(p.resultChanges),
        p.tummyUpset ? "이 음식은 오늘 고양이 배에 살짝 안 맞았어(아주 심하지는 않게)." : "",
        "이 상황에 맞는 고양이 반응을 2~3문장으로 만들어줘. 성격, 이벤트, 현재 상태(특히 배고픔/졸림/기분)를 자연스럽게 반영해.",
      ].filter(Boolean).join(" ");

    case "item_reaction":
      return [
        persLine(p), dayEventLine(p),
        `플레이어 ${p.playerName}가 방금 '${p.selectedItem}'(${p.itemType === "play" ? "놀이 아이템" : "돌봄 아이템"})을 사용했어.`,
        statLine(p.stats), changeLine(p.resultChanges),
        p.situation ? `특별 상황: ${p.situation}.` : "",
        "고양이 반응을 2~3문장으로 만들어줘. 놀이 아이템은 귀엽고 장난스럽게, 돌봄 아이템은 편안하고 회복되는 느낌으로. 졸림이 높으면 너무 활발하게 표현하지 마.",
      ].filter(Boolean).join(" ");

    case "owner_review":
      return [
        `고양이 이름은 ${p.catName}, 돌본 어린이는 ${p.playerName}.`,
        dayEventLine(p),
        `오늘 별점은 ${p.earnedStars}점(5점 만점).`,
        statLine(p.stats),
        p.todayActionsSummary && p.todayActionsSummary.length ? `오늘 한 일: ${p.todayActionsSummary.join(", ")}.` : "",
        "고양이 주인이 어린이에게 하는 따뜻한 평가 멘트를 2~3문장으로 만들어줘. 5점이면 크게 칭찬, 3점이면 부드러운 조언, 1~2점이면 걱정은 하되 혼내지 말고 격려해줘. 무엇을 잘했고 무엇을 개선하면 좋을지 살짝 알려줘.",
      ].filter(Boolean).join(" ");

    case "cat_diary":
      return [
        persLine(p), dayEventLine(p),
        p.todayActionsSummary && p.todayActionsSummary.length ? `오늘 ${p.playerName}가 해준 일: ${p.todayActionsSummary.join(", ")}.` : "",
        statLine(p.stats || p.endingStats),
        "고양이가 직접 쓰는 일기를 1인칭으로 3문장 이내로 만들어줘. 귀엽고 따뜻하게, 너무 논리적으로 길게 말하지 말고, 마지막은 '냐아', '야옹', '골골골' 같은 고양이 느낌으로 끝내줘. 오늘의 사건과 플레이어가 해준 일을 반영해.",
      ].filter(Boolean).join(" ");

    case "ending_letter":
      return [
        `고양이 이름은 ${p.catName}, 성격은 ${p.catPersonality}. 7일 동안 ${p.playerName}가 돌봤어.`,
        `엔딩 종류: ${p.endingType}. 총 별점 ${p.totalStars}, 하루 평균 ${p.averageStars}점.`,
        statLine(p.finalStats),
        "고양이 또는 고양이 주인이 어린이에게 보내는 짧은 편지를 4~6문장으로 만들어줘. '최고의 집사 엔딩'이면 감동적이고 뿌듯하게, '괜찮은 집사 엔딩'이면 따뜻하고 격려하듯, '아쉬운 집사 엔딩'이면 절대 비난하지 말고 '다음엔 더 잘할 수 있어' 같은 희망적인 느낌으로. 어린이가 기분 좋게 마무리하도록 써줘.",
      ].filter(Boolean).join(" ");

    default:
      return null;
  }
}
