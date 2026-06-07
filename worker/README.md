# Cloudflare Worker — 아기고양이 AI 프록시 🐱✨

`index.html`(GitHub Pages) 이 직접 Gemini 를 부르지 않고, 이 Worker 를 거쳐 호출합니다.
**Gemini API Key 는 Worker 환경변수에만 저장되어 브라우저에 절대 노출되지 않습니다.**

## 준비물
- Cloudflare 계정 (무료)
- Google AI Studio 에서 발급한 **Gemini API Key** → https://aistudio.google.com/apikey

## 배포 순서

```bash
# 1) wrangler(클라우드플레어 CLI) 설치
npm install -g wrangler

# 2) Cloudflare 로그인 (브라우저 창이 열려요)
wrangler login

# 3) 이 worker 폴더로 이동
cd worker

# 4) Gemini API Key 를 시크릿으로 등록 (입력창에 키 붙여넣기)
wrangler secret put GEMINI_API_KEY

# 5) 배포!
wrangler deploy
```

배포가 끝나면 이런 주소가 나옵니다:

```
https://chloe-cat-ai.<your-subdomain>.workers.dev
```

## 마지막 연결
이 주소를 복사해서 프로젝트 루트의 `index.html` 맨 위 `AI_ENDPOINT` 에 붙여넣으세요:

```js
const AI_ENDPOINT = "https://chloe-cat-ai.<your-subdomain>.workers.dev";
```

그리고 커밋·push 하면 GitHub Pages 게임에서 AI 이야기가 작동합니다.

## 허용 출처(CORS)
`worker.js` 상단 `ALLOWED_ORIGIN_PREFIXES` 에 본인 GitHub Pages 주소가 들어 있어야 합니다.
기본값은 `https://youngs2000-pixel.github.io` 입니다. 다른 주소를 쓰면 수정 후 다시 `wrangler deploy` 하세요.

## 테스트
```bash
curl -X POST https://chloe-cat-ai.<your-subdomain>.workers.dev \
  -H "Content-Type: application/json" \
  -d '{"type":"food_reaction","playerName":"민준","catName":"솜이","catPersonality":"겁쟁이","catPersonalityDesc":"겁이 많아요","currentDay":2,"currentEvent":"낯선 소리에 놀란 날","selectedFood":"아기고양이용 우유","stats":{"hunger":70,"mood":25,"health":80,"sleep":30,"affection":35},"resultChanges":{"hunger":-25,"mood":5,"health":2,"sleep":0}}'
```
`{"text":"..."}` 가 돌아오면 성공입니다.
