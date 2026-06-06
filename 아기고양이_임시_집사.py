# -*- coding: utf-8 -*-
"""
아기고양이 임시 집사 게임
7일 동안 아기고양이를 돌보는 텍스트 육성 게임
"""
import random, os, sys, time

# ───────────────────────────────────────────────
# 텍스트 고양이 표정 (ASCII)
# ───────────────────────────────────────────────
CAT_FACES = {
    "happy":   " /\\_/\\ \n( ^w^ )\n > v < ",
    "excited": " /\\_/\\ \n(*^w^*)\n > * < ",
    "normal":  " /\\_/\\ \n( -.- )\n > . < ",
    "sad":     " /\\_/\\ \n( T-T )\n > _ < ",
    "sick":    " /\\_/\\ \n( x_x )\n > ~ < ",
    "sleepy":  " /\\_/\\ \n( -_-)\n > z < ",
    "scared":  " /\\_/\\ \n( o_o )\n > ! < ",
    "hungry":  " /\\_/\\ \n( @.@)\n > o < ",
}

# ───────────────────────────────────────────────
# 고양이 성격
# ───────────────────────────────────────────────
PERSONALITIES = {
    "활발이": {
        "desc": "호기심 많고 장난꾸러기예요. 장난감을 아주 좋아해요.",
        "play_bonus": 12, "food_bonus": 0, "sleep_rate": 1.1, "mood_start": 60,
    },
    "얌전이": {
        "desc": "조용하고 얌전해요. 따뜻한 곳에서 쉬는 걸 좋아해요.",
        "play_bonus": 0, "food_bonus": 5, "sleep_rate": 0.8, "mood_start": 55,
    },
    "겁쟁이": {
        "desc": "겁이 조금 많아요. 익숙해지면 아주 다정해져요.",
        "play_bonus": 0, "food_bonus": 0, "sleep_rate": 1.2, "mood_start": 45,
    },
    "먹보": {
        "desc": "먹는 것을 정말 좋아해요. 맛있는 밥을 주면 엄청 기뻐해요.",
        "play_bonus": 0, "food_bonus": 12, "sleep_rate": 1.0, "mood_start": 60,
    },
    "애교쟁이": {
        "desc": "애교가 넘쳐요. 쓰다듬어 주면 기분이 팍팍 올라가요.",
        "play_bonus": 6, "food_bonus": 6, "sleep_rate": 0.9, "mood_start": 65,
    },
}

# ───────────────────────────────────────────────
# 음식 데이터
# ───────────────────────────────────────────────
FOODS = {
    "아기고양이용 우유": {
        "hunger": -25, "mood": 5, "health": 2, "sleep": 0,
        "tummy_risk": 0,
        "desc": "부드럽고 안전해요. 아기 고양이에게 딱 맞아요.",
    },
    "부드러운 고양이 사료": {
        "hunger": -35, "mood": 5, "health": 3, "sleep": 5,
        "tummy_risk": 0,
        "desc": "든든한 밥이에요. 배고픔을 크게 줄여줘요.",
    },
    "참치캔": {
        "hunger": -28, "mood": 20, "health": -5, "sleep": 0,
        "tummy_risk": 25,
        "desc": "고양이가 아주 좋아해요. 너무 자주 주면 배탈 날 수 있어요!",
    },
}

# ───────────────────────────────────────────────
# 음식 반응 문장
# ───────────────────────────────────────────────
FOOD_REACTIONS = {
    "아기고양이용 우유": {
        "hungry": [
            "{c}이(가) 우유 그릇에 코를 박고 꿀꺽꿀꺽 마셨어요. 배가 많이 고팠나봐요!",
            "{c}이(가) 우유를 단숨에 다 마셔버렸어요.",
        ],
        "sleepy": [
            "{c}이(가) 우유를 두 모금 마시더니 눈을 깜빡였어요. 졸음이 더 강한가봐요.",
            "먹다가 꾸벅꾸벅 조는 {c}이(가) 너무 귀여워요.",
        ],
        "happy": [
            "우유를 다 마신 {c}이(가) 다가와 머리를 살짝 비볐어요!",
            "{c}이(가) 우유를 마시고 꼬리를 살랑살랑 흔들었어요.",
        ],
        "sick": [
            "{c}이(가) 우유를 조금 마시고 조용히 담요 위에 웅크렸어요.",
            "몸이 안 좋은지 {c}이(가) 우유를 조금씩 천천히 마셨어요.",
        ],
        "moody": [
            "{c}이(가) 우유 냄새를 맡고는 고개를 살짝 돌렸어요. 오늘은 기분이 안 좋은가봐요.",
        ],
        "normal": [
            "{c}이(가) 우유 그릇에 코를 가까이 대더니 조심스럽게 핥기 시작했어요. 꼬리를 살랑살랑 흔들었어요.",
            "{c}이(가) 얌전히 우유를 마셨어요. 작은 소리로 '냐아' 했어요.",
        ],
    },
    "부드러운 고양이 사료": {
        "hungry": [
            "{c}이(가) 기다렸다는 듯 사료 그릇으로 달려왔어요! 작은 입으로 열심히 먹는 모습이 귀여워요.",
            "배가 많이 고팠는지 {c}이(가) 사료를 순식간에 다 먹었어요.",
        ],
        "sleepy": [
            "{c}이(가) 사료를 먹다가 꾸벅꾸벅 졸기 시작했어요. 밥보다 잠이 더 필요한 것 같아요.",
            "먹으면서 눈이 자꾸 감기는 {c}이(가) 사료 그릇 앞에서 졸고 있어요.",
        ],
        "sick": [
            "{c}이(가) 사료를 조금 먹고는 멈췄어요. 아직 밥맛이 없는 것 같아요.",
        ],
        "normal": [
            "{c}이(가) 사료를 오물오물 씹어 먹었어요. 배가 든든해졌는지 조용히 몸을 웅크렸어요.",
            "{c}이(가) 얌전하게 사료를 다 먹었어요. 만족스러운 표정이에요.",
        ],
    },
    "참치캔": {
        "normal": [
            "{c}이(가) 참치 냄새를 맡자마자 눈을 반짝였어요! 신나게 먹고 나서 앞발을 핥았어요.",
            "참치를 본 {c}이(가) 작은 발로 그릇을 건드렸어요. 아주 맛있게 먹었어요!",
        ],
        "tummy_bad": [
            "{c}이(가) 참치를 조금 먹더니 배를 웅크렸어요. 오늘은 자극적인 음식이 맞지 않았나봐요.",
            "참치를 먹던 {c}이(가) 갑자기 웅크렸어요. 배탈이 난 것 같아요. 앞으로 조심해요!",
        ],
        "moody": [
            "평소라면 좋아했을 참치인데, 오늘은 냄새만 맡고 뒤로 물러났어요.",
        ],
        "hungry": [
            "{c}이(가) 참치를 보자마자 달려왔어요! 신나게 먹으면서 꼬리를 세웠어요.",
        ],
    },
}

# ───────────────────────────────────────────────
# 아이템 데이터
# ───────────────────────────────────────────────
ITEMS = {
    "고양이 치료제":  {"type": "heal", "cost": 3, "hunger": 0,  "mood": 5,  "health": 30, "sleep": -5,  "desc": "건강을 크게 회복해요.", "max": 3},
    "따뜻한 담요":   {"type": "heal", "cost": 2, "hunger": 0,  "mood": 15, "health": 10, "sleep": -20, "desc": "졸리거나 기분이 안 좋을 때 안정시켜줘요.", "max": 3},
    "영양 간식":     {"type": "heal", "cost": 2, "hunger": -10,"mood": 10, "health": 15, "sleep": 0,   "desc": "건강과 기분을 조금 회복해줘요.", "max": 3},
    "깃털 장난감":   {"type": "play", "cost": 2, "hunger": 5,  "mood": 25, "health": 0,  "sleep": 12,  "desc": "기분을 크게 올려줘요. 졸릴 때 쓰면 오히려 피곤해요.", "max": 3},
    "작은 공":       {"type": "play", "cost": 2, "hunger": 5,  "mood": 20, "health": 0,  "sleep": 8,   "desc": "기분을 올려줘요. 활발한 날에 효과 좋아요.", "max": 3},
    "털실뭉치":      {"type": "play", "cost": 1, "hunger": 3,  "mood": 15, "health": 0,  "sleep": 15,  "desc": "귀엽게 놀아요. 너무 많이 놀면 졸려질 수 있어요.", "max": 3},
    "종이상자":      {"type": "play", "cost": 1, "hunger": 0,  "mood": 20, "health": 5,  "sleep": -5,  "desc": "불안하거나 놀란 날 안정감을 줘요.", "max": 3},
}

ITEM_REACTIONS = {
    "고양이 치료제":  ["{c}이(가) 치료제를 먹고 조금 편안해진 표정을 지었어요. 한결 나아진 것 같아요.",
                       "치료제를 먹은 {c}이(가) 깊게 숨을 쉬었어요. 기운을 차리는 것 같아요."],
    "따뜻한 담요":   ["{c}이(가) 따뜻한 담요 속으로 쏙 들어갔어요. 꼬리가 담요 밖으로 삐죽 나와 있어요.",
                       "담요를 킁킁 맡던 {c}이(가) 폭 파고들었어요. 곧 조용히 잠들었어요."],
    "영양 간식":     ["{c}이(가) 영양 간식을 조심스럽게 먹었어요. 맛이 마음에 들었는지 입가를 핥았어요.",
                       "간식을 받은 {c}이(가) 앞발로 살짝 건드려보더니 맛있게 먹었어요."],
    "깃털 장난감":   ["깃털이 흔들리자 {c}이(가) 눈이 동그래졌어요! 작은 앞발로 톡톡 건드리며 신나게 놀았어요.",
                       "{c}이(가) 깃털을 잡으려고 펄쩍펄쩍 뛰었어요! 아주 신이 났어요."],
    "작은 공":       ["작은 공이 데굴데굴 굴러가자 {c}이(가) 뒤뚱뒤뚱 쫓아갔어요. 공을 잡고 뿌듯한 표정이에요.",
                       "{c}이(가) 공을 앞발로 탁 쳤어요. 공이 굴러가자 눈을 반짝이며 쫓아갔어요."],
    "털실뭉치":      ["{c}이(가) 털실뭉치를 앞발로 건드리다가 살짝 엉켜버렸어요. 멍한 표정으로 앉아 있어요.",
                       "털실에 신나게 놀던 {c}이(가) 털실에 엉켜서 '냐?' 하는 표정을 지었어요."],
    "종이상자":      ["{c}이(가) 종이상자 안으로 쏙 들어갔어요. 귀만 빼꼼 보이는 모습이 너무 귀여워요!",
                       "상자를 발견한 {c}이(가) 냄새를 맡더니 조심스럽게 들어갔어요. 아주 편안해 보여요."],
}

# ───────────────────────────────────────────────
# 랜덤 이벤트
# ───────────────────────────────────────────────
EVENTS = [
    {
        "name": "까칠한 날",
        "chance": 0.15,
        "desc": "오늘 {c}이(가) 왠지 기분이 좋지 않아 보여요. 평소 좋아하던 것도 시큰둥할 수 있어요.",
        "hint": "놀이 아이템이나 따뜻한 담요로 달래줄 수 있어요.",
        "mood": -20, "health": 0, "sleep": 0,
        "toy_bored": False, "tummy": False, "positive": False,
    },
    {
        "name": "낯선 소리에 놀란 날",
        "chance": 0.12,
        "desc": "창밖에서 큰 소리가 났어요! {c}이(가) 깜짝 놀라 소파 밑으로 숨어버렸어요.",
        "hint": "종이상자나 따뜻한 담요로 안정시켜 주세요.",
        "mood": -25, "health": 0, "sleep": 15,
        "toy_bored": False, "tummy": False, "positive": False,
    },
    {
        "name": "장난감 싫증",
        "chance": 0.10,
        "desc": "{c}이(가) 평소 좋아하던 장난감을 보고도 시큰둥해요. 다른 놀이가 필요한 것 같아요.",
        "hint": "다른 종류의 놀이 아이템을 써보세요.",
        "mood": -10, "health": 0, "sleep": 0,
        "toy_bored": True, "tummy": False, "positive": False,
    },
    {
        "name": "꾸벅꾸벅 피곤한 날",
        "chance": 0.15,
        "desc": "{c}이(가) 계속 하품을 해요. 놀고 싶어 보이지만 눈꺼풀이 자꾸 감겨요.",
        "hint": "억지로 놀아주지 말고 쉬게 해주세요.",
        "mood": 0, "health": 0, "sleep": 25,
        "toy_bored": False, "tummy": False, "positive": False,
    },
    {
        "name": "배가 예민한 날",
        "chance": 0.12,
        "desc": "오늘 {c}이(가) 배가 조금 예민해 보여요. 아무 음식이나 주면 배탈이 날 수 있어요.",
        "hint": "우유나 부드러운 사료를 주세요. 참치캔은 위험해요!",
        "mood": 0, "health": -5, "sleep": 0,
        "toy_bored": False, "tummy": True, "positive": False,
    },
    {
        "name": "재채기 연발",
        "chance": 0.10,
        "desc": "{c}이(가) '에취! 에취!' 재채기를 연달아 했어요. 감기 기운이 있나봐요.",
        "hint": "따뜻한 담요로 보온하고 치료제를 써보세요.",
        "mood": -5, "health": -10, "sleep": 0,
        "toy_bored": False, "tummy": False, "positive": False,
    },
    {
        "name": "벌레 발견!",
        "chance": 0.10,
        "desc": "{c}이(가) 바닥에서 작은 벌레를 발견했어요! 눈을 반짝이며 사냥 자세를 취했어요.",
        "hint": "오늘은 기분이 아주 좋은 날이에요!",
        "mood": 15, "health": 0, "sleep": -10,
        "toy_bored": False, "tummy": False, "positive": True,
    },
    {
        "name": "창가 햇살",
        "chance": 0.12,
        "desc": "창가에 따뜻한 햇살이 들어와요. {c}이(가) 햇살을 받으며 기지개를 켰어요.",
        "hint": "오늘은 기분 좋은 날이에요!",
        "mood": 10, "health": 5, "sleep": 0,
        "toy_bored": False, "tummy": False, "positive": True,
    },
    {
        "name": "배탈 조짐",
        "chance": 0.08,
        "desc": "{c}이(가) 배를 핥으며 조금 웅크리고 있어요. 배가 살짝 안 좋은 것 같아요.",
        "hint": "영양 간식이나 치료제로 돌봐주세요.",
        "mood": -10, "health": -8, "sleep": 0,
        "toy_bored": False, "tummy": False, "positive": False,
    },
    {
        "name": "아무 일도 없는 평화로운 날",
        "chance": 0.0,  # fallback only
        "desc": "오늘은 {c}이(가) 아주 평온해 보여요.",
        "hint": "",
        "mood": 0, "health": 0, "sleep": 0,
        "toy_bored": False, "tummy": False, "positive": True,
    },
]

# ───────────────────────────────────────────────
# 주인 평가 멘트
# ───────────────────────────────────────────────
OWNER_LINES = {
    5: [
        "주인이 환하게 웃었어요. \"와, {c}이(가) 아주 편안하고 건강해 보여요! 정말 잘 돌봐주셨어요!\"",
        "주인이 {c}을(를) 안아들고 기뻐했어요. \"{c}이(가) 이렇게 행복해 보이다니! 최고예요!\"",
    ],
    4: [
        "주인이 고개를 끄덕였어요. \"아주 잘 돌봐주셨네요. 내일도 이렇게 해주시면 좋겠어요.\"",
        "주인이 흐뭇하게 웃었어요. \"{c}이(가) 잘 지낸 것 같아요. 정말 수고하셨어요.\"",
    ],
    3: [
        "주인이 {c}을(를) 살펴보았어요. \"나쁘지 않아요. 다만 내일은 조금 더 신경 써주면 좋겠어요.\"",
        "주인이 고개를 갸웃했어요. \"음... 괜찮긴 한데, 조금 더 잘 돌볼 수 있을 것 같아요.\"",
    ],
    2: [
        "주인이 걱정스러운 표정으로 살펴보았어요. \"오늘 {c}이(가) 조금 힘들어 보이네요. 내일은 더 잘 살펴주세요.\"",
        "주인이 한숨을 쉬었어요. \"{c}의 상태가 조금 걱정돼요. 내일은 더 신경 써주세요.\"",
    ],
    1: [
        "주인이 걱정스러운 얼굴로 {c}을(를) 꼭 안았어요. \"오늘은 많이 힘들었겠구나... 내일은 꼭 더 잘 부탁드려요.\"",
        "주인이 미간을 찌푸렸어요. \"상태가 좋지 않네요. 아기고양이를 돌보는 건 세심한 일이에요.\"",
    ],
}

# ───────────────────────────────────────────────
# 유틸리티
# ───────────────────────────────────────────────
def clr():
    os.system("cls" if os.name == "nt" else "clear")

def slow(text, d=0.025):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(d)
    print()

def sep(c="─", n=52):
    print(c * n)

def hdr(title):
    sep("═")
    print(f"  {title}")
    sep("═")

def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))

def bar(v, n=18):
    f = int(n * v / 100)
    return "[" + "█" * f + "░" * (n - f) + f"] {v:3d}"

def stat_label(name, v):
    if name == "배고픔":
        if v >= 70: return "배고픔: 많이 배고파요!"
        if v >= 40: return "배고픔: 조금 배고파요"
        return           "배고픔: 배가 불러요"
    if name == "기분":
        if v >= 70: return "기분: 아주 좋아요 :D"
        if v >= 50: return "기분: 보통이에요"
        if v >= 30: return "기분: 조금 안 좋아요"
        return           "기분: 많이 안 좋아요 :("
    if name == "건강":
        if v >= 80: return "건강: 아주 건강해요!"
        if v >= 60: return "건강: 건강해요"
        if v >= 40: return "건강: 조금 안 좋아요"
        return           "건강: 아파요..."
    if name == "졸림":
        if v >= 70: return "졸림: 많이 졸려요 zzz"
        if v >= 40: return "졸림: 조금 졸려요"
        return           "졸림: 말짱해요"
    return f"{name}: {v}"

def face(mood, health, sleep):
    if health < 30:    return CAT_FACES["sick"]
    if sleep > 70:     return CAT_FACES["sleepy"]
    if mood >= 75:     return CAT_FACES["excited"]
    if mood >= 55:     return CAT_FACES["happy"]
    if mood >= 35:     return CAT_FACES["normal"]
    return                    CAT_FACES["sad"]

def ask(prompt, choices):
    while True:
        print(f"\n  {prompt}")
        for i, c in enumerate(choices, 1):
            print(f"    {i}. {c}")
        try:
            n = int(input("\n  번호 입력 >> ").strip()) - 1
            if 0 <= n < len(choices):
                return n
        except (ValueError, KeyboardInterrupt):
            pass
        print("  올바른 번호를 입력해주세요.")

def pause():
    input("\n  [ 엔터를 눌러 계속 ]")

# ───────────────────────────────────────────────
# 게임 상태 클래스
# ───────────────────────────────────────────────
class GS:
    def __init__(self, pname, cname, pkey):
        self.pname = pname          # 플레이어 이름
        self.cname = cname          # 고양이 이름
        self.pkey  = pkey           # 성격 키
        self.pers  = PERSONALITIES[pkey]

        self.day        = 1
        self.total_stars= 0
        self.day_stars  = []

        # 스탯
        self.hunger  = 40
        self.mood    = self.pers["mood_start"]
        self.health  = 80
        self.sleep   = 20
        self.affection = 30

        # 인벤토리
        self.inv = {k: 0 for k in ITEMS}

        # 하루 상태
        self.event       = None
        self.fed         = False
        self.actions     = 0
        self.max_actions = 3
        self.tuna_streak = 0

    def mod(self, **kw):
        if "hunger"    in kw: self.hunger    = clamp(self.hunger    + kw["hunger"])
        if "mood"      in kw: self.mood      = clamp(self.mood      + kw["mood"])
        if "health"    in kw: self.health    = clamp(self.health    + kw["health"])
        if "sleep"     in kw: self.sleep     = clamp(self.sleep     + kw["sleep"])
        if "affection" in kw: self.affection = clamp(self.affection + kw["affection"])

    def show_stats(self):
        print(f"\n  고양이: {self.cname}  (성격: {self.pkey})")
        print(f"  {self.day}일차 / 7일   모은 별점: {'★' * self.total_stars} ({self.total_stars}개)")
        print()
        for line in face(self.mood, self.health, self.sleep).split("\n"):
            print("  " + line)
        print()
        print(f"  배고픔 {bar(self.hunger)}  {stat_label('배고픔', self.hunger)}")
        print(f"  기  분 {bar(self.mood)}  {stat_label('기분',   self.mood)}")
        print(f"  건  강 {bar(self.health)}  {stat_label('건강',  self.health)}")
        print(f"  졸  림 {bar(self.sleep)}  {stat_label('졸림',   self.sleep)}")
        print(f"  친밀도 {bar(self.affection)}  (집사와 얼마나 친해졌나요)")
        print()

# ───────────────────────────────────────────────
# 음식 주기
# ───────────────────────────────────────────────
def do_feed(gs):
    clr()
    hdr(f"  {gs.cname}에게 음식 주기")
    gs.show_stats()

    food_keys = list(FOODS.keys())
    choice = ask(f"어떤 음식을 {gs.cname}에게 줄까요?", food_keys)
    fname = food_keys[choice]
    fd = FOODS[fname]

    # 기본 효과
    dh = fd["hunger"]
    dm = fd["mood"]
    dH = fd["health"]
    ds = fd["sleep"]

    # 성격 보너스
    dm += gs.pers["food_bonus"] // 2

    # 졸림 패널티
    sleepy = gs.sleep > 65
    if sleepy:
        dm -= 5; dH -= 3; ds += 5

    # 배 예민 이벤트 + 참치
    tummy_bad = False
    ev = gs.event
    if ev and ev["tummy"] and fname == "참치캔":
        dH -= 20; tummy_bad = True
    elif fname == "참치캔":
        gs.tuna_streak += 1
        if gs.tuna_streak >= 3:
            dH -= 10
        if not tummy_bad and random.randint(1, 100) <= fd["tummy_risk"]:
            dH -= 15; tummy_bad = True
    else:
        gs.tuna_streak = 0

    # 반응 문장 선택
    pool = FOOD_REACTIONS.get(fname, {})
    moody = gs.mood < 30
    if tummy_bad:
        lines = pool.get("tummy_bad", [f"{gs.cname}이(가) 음식을 먹었어요."])
    elif sleepy:
        lines = pool.get("sleepy", pool.get("normal", [f"{gs.cname}이(가) 먹었어요."]))
    elif gs.hunger > 60:
        lines = pool.get("hungry", pool.get("normal", [f"{gs.cname}이(가) 먹었어요."]))
    elif moody:
        lines = pool.get("moody", pool.get("normal", [f"{gs.cname}이(가) 먹었어요."]))
    elif gs.health < 40:
        lines = pool.get("sick", pool.get("normal", [f"{gs.cname}이(가) 먹었어요."]))
    elif gs.mood > 65:
        lines = pool.get("happy", pool.get("normal", [f"{gs.cname}이(가) 먹었어요."]))
    else:
        lines = pool.get("normal", [f"{gs.cname}이(가) 먹었어요."])

    reaction = random.choice(lines).replace("{c}", gs.cname)
    print()
    slow(f"  {reaction}")

    gs.mod(hunger=dh, mood=dm, health=dH, sleep=ds, affection=3)
    gs.fed = True
    gs.actions += 1

    changes = []
    if dh < 0: changes.append(f"배고픔 -{abs(dh)}")
    if dm > 0: changes.append(f"기분 +{dm}")
    elif dm < 0: changes.append(f"기분 -{abs(dm)}")
    if dH > 0: changes.append(f"건강 +{dH}")
    elif dH < 0: changes.append(f"건강 -{abs(dH)}")
    if ds > 0: changes.append(f"졸림 +{ds}")
    if changes:
        print(f"\n  [ {' / '.join(changes)} ]")

    pause()

# ───────────────────────────────────────────────
# 아이템 사용
# ───────────────────────────────────────────────
def do_item(gs):
    avail = {k: v for k, v in gs.inv.items() if v > 0}
    if not avail:
        print("\n  아이템이 없어요! 상점에서 구매하세요.")
        pause()
        return

    clr()
    hdr("  아이템 사용")
    gs.show_stats()

    names  = list(avail.keys())
    labels = [f"{n}  (남은 수량: {avail[n]}개)  ─  {ITEMS[n]['desc']}" for n in names]
    labels.append("사용하지 않는다")
    idx = ask("어떤 아이템을 사용할까요?", labels)
    if idx == len(names):
        return

    iname = names[idx]
    idata = ITEMS[iname]

    # 졸릴 때 놀이 아이템 패널티
    if idata["type"] == "play" and gs.sleep > 65:
        slow(f"\n  {gs.cname}이(가) 너무 졸려서 제대로 놀지 못했어요.")
        gs.mod(sleep=10, mood=-5)
        gs.inv[iname] -= 1
        gs.actions += 1
        pause()
        return

    # 장난감 싫증 이벤트
    ev = gs.event
    if ev and ev.get("toy_bored") and idata["type"] == "play" and iname in ["깃털 장난감", "작은 공"]:
        slow(f"\n  오늘은 {gs.cname}이(가) 이 장난감에 별 관심이 없어 보여요.")
        gs.mod(mood=5)
        gs.inv[iname] -= 1
        gs.actions += 1
        pause()
        return

    reaction = random.choice(ITEM_REACTIONS.get(iname, [f"{gs.cname}이(가) 아이템을 사용했어요."])).replace("{c}", gs.cname)
    print()
    slow(f"  {reaction}")

    gs.mod(hunger=idata["hunger"], mood=idata["mood"], health=idata["health"],
           sleep=idata["sleep"], affection=5)
    gs.inv[iname] -= 1
    gs.actions += 1

    changes = []
    if idata["mood"]   > 0: changes.append(f"기분 +{idata['mood']}")
    if idata["health"] > 0: changes.append(f"건강 +{idata['health']}")
    if idata["sleep"]  < 0: changes.append(f"졸림 -{abs(idata['sleep'])}")
    if idata["sleep"]  > 0: changes.append(f"졸림 +{idata['sleep']}")
    if changes:
        print(f"\n  [ {' / '.join(changes)} ]")

    pause()

# ───────────────────────────────────────────────
# 쓰다듬기
# ───────────────────────────────────────────────
def do_pet(gs):
    if gs.mood >= 30:
        lines = [
            f"{gs.cname}이(가) 쓰다듬는 손에 얼굴을 비볐어요!",
            f"{gs.cname}이(가) '그르릉...' 소리를 내며 눈을 가늘게 떴어요.",
            f"등을 쓰다듬자 {gs.cname}이(가) 꼬리를 세웠어요.",
            f"{gs.cname}이(가) 쓰다듬는 손을 핥았어요! 간질간질해요.",
        ]
        dm = 10
    else:
        lines = [
            f"오늘은 기분이 안 좋은지 {gs.cname}이(가) 슬쩍 피했어요.",
            f"{gs.cname}이(가) 손을 가만히 바라보다가 고개를 돌렸어요.",
        ]
        dm = 3

    slow(f"\n  {random.choice(lines)}")
    gs.mod(mood=dm, affection=8)
    gs.actions += 1
    print(f"\n  [ 기분 +{dm} / 친밀도 +8 ]")
    pause()

# ───────────────────────────────────────────────
# 상점
# ───────────────────────────────────────────────
def do_shop(gs):
    while True:
        clr()
        hdr("  ★ 별점 상점 ★")
        print(f"\n  현재 별점: {'★' * gs.total_stars} ({gs.total_stars}개)\n")
        sep()

        item_list = list(ITEMS.items())
        for i, (n, d) in enumerate(item_list, 1):
            owned = gs.inv.get(n, 0)
            print(f"  {i}. {n}  ─  별 {d['cost']}개  (보유: {owned}개)")
            print(f"     {d['desc']}")
        print(f"  {len(item_list)+1}. 상점을 나간다")

        try:
            idx = int(input("\n  번호 입력 >> ").strip()) - 1
            if idx == len(item_list):
                break
            if 0 <= idx < len(item_list):
                iname, idata = item_list[idx]
                if gs.total_stars < idata["cost"]:
                    print(f"\n  별점이 부족해요! (필요: {idata['cost']}개, 보유: {gs.total_stars}개)")
                elif gs.inv[iname] >= idata["max"]:
                    print(f"\n  최대 {idata['max']}개까지만 가질 수 있어요.")
                else:
                    gs.total_stars -= idata["cost"]
                    gs.inv[iname] += 1
                    print(f"\n  {iname}을(를) 구입했어요!")
                input("  [ 엔터 ]")
        except (ValueError, KeyboardInterrupt):
            pass

# ───────────────────────────────────────────────
# 하루 평가
# ───────────────────────────────────────────────
def calc_stars(gs):
    s = 0
    # 배고픔
    if gs.hunger < 30:   s += 2
    elif gs.hunger < 50: s += 1
    elif gs.hunger > 70: s -= 2
    # 기분
    if gs.mood >= 65:    s += 2
    elif gs.mood >= 45:  s += 1
    elif gs.mood < 25:   s -= 2
    else:                s -= 1
    # 건강
    if gs.health >= 70:  s += 2
    elif gs.health >= 50:s += 1
    elif gs.health < 30: s -= 3
    else:                s -= 1
    # 졸림
    if gs.sleep < 40:    s += 1
    elif gs.sleep > 75:  s -= 1
    # 친밀도
    if gs.affection >= 60: s += 1
    # 밥 안 줌
    if not gs.fed:       s -= 3

    if s >= 7: return 5
    if s >= 5: return 4
    if s >= 3: return 3
    if s >= 1: return 2
    return 1

def day_end(gs):
    earned = calc_stars(gs)
    gs.total_stars += earned
    gs.day_stars.append(earned)

    clr()
    hdr(f"  {gs.day}일차 마무리 - 주인 방문")
    gs.show_stats()

    slow(f"\n  밤이 되었어요. {gs.cname}의 주인이 찾아왔어요...")
    pause()

    comment = random.choice(OWNER_LINES.get(earned, OWNER_LINES[3])).replace("{c}", gs.cname)
    print()
    slow(f"  {comment}")
    print()
    print(f"  오늘의 평가: {'★' * earned}{'☆' * (5 - earned)}  ({earned}점)")
    print(f"  누적 별점: {gs.total_stars}개")
    pause()

# ───────────────────────────────────────────────
# 하루 진행
# ───────────────────────────────────────────────
def roll_event():
    for ev in random.sample(EVENTS[:-1], len(EVENTS) - 1):
        if random.random() < ev["chance"]:
            return ev
    return None

def run_day(gs):
    clr()

    # 이벤트 결정
    ev = roll_event()
    gs.event = ev

    hdr(f"  {gs.day}일차 아침")
    gs.show_stats()

    if ev:
        edesc = ev["desc"].replace("{c}", gs.cname)
        print(f"  [오늘의 이벤트: {ev['name']}]")
        slow(f"  {edesc}")
        if ev["hint"]:
            print(f"  ★ 힌트: {ev['hint']}")
        gs.mod(mood=ev["mood"], health=ev["health"], sleep=ev["sleep"])
        print()
        print(f"  현재 기분: {stat_label('기분', gs.mood)}")
        print(f"  현재 건강: {stat_label('건강', gs.health)}")
        print(f"  현재 졸림: {stat_label('졸림', gs.sleep)}")
        pause()

    # 메인 루프
    while True:
        clr()
        hdr(f"  {gs.day}일차 - {gs.pname}의 집사 생활")
        gs.show_stats()

        left = gs.max_actions - gs.actions
        fed_mark = "완료!" if gs.fed else "아직 안 줬어요"
        print(f"  남은 행동: {left}번  |  오늘 밥주기: {fed_mark}")
        print()

        if left <= 0:
            print("  오늘 할 수 있는 행동을 모두 했어요. 하루를 마무리할게요!")
            pause()
            break

        options = []
        if not gs.fed:
            options.append("밥을 준다")
        else:
            options.append("간식을 한 번 더 준다")
        options += ["아이템을 사용한다", "쓰다듬어준다 (기분 & 친밀도 상승)", "오늘은 여기까지 (하루 마무리)"]

        idx = ask("무엇을 할까요?", options)
        sel = options[idx]

        if "밥" in sel or "간식" in sel:
            do_feed(gs)
        elif "아이템" in sel:
            do_item(gs)
        elif "쓰다듬" in sel:
            do_pet(gs)
        elif "마무리" in sel:
            if not gs.fed:
                c2 = ask(f"아직 {gs.cname}에게 밥을 주지 않았어요. 그래도 마무리할까요?",
                         ["네, 마무리할게요", "아니요, 돌아갈게요"])
                if c2 == 1:
                    continue
            break

    # 하루 평가
    day_end(gs)

    # 상점
    clr()
    hdr("  별점 상점")
    print(f"\n  하루가 끝났어요! 현재 별점: {gs.total_stars}개")
    if get_input("\n  상점에 갈까요?", ["상점에 간다", "다음 날로 넘어간다"]) == 0:
        do_shop(gs)

def get_input(prompt, choices):
    return ask(prompt, choices)

# ───────────────────────────────────────────────
# 하룻밤 지나기 (스탯 자연 변화)
# ───────────────────────────────────────────────
def overnight(gs):
    gs.mod(
        hunger=20,
        sleep=-30,
        mood=5 if gs.sleep < 60 else -5,
        health=5 if gs.health < 90 else 0,
        affection=2,
    )
    gs.fed     = False
    gs.actions = 0
    gs.event   = None

# ───────────────────────────────────────────────
# 엔딩
# ───────────────────────────────────────────────
def show_ending(gs):
    clr()
    hdr("  ★★★ 7일간의 임시 집사 생활 종료 ★★★")

    total = sum(gs.day_stars)
    avg   = total / len(gs.day_stars)

    print(f"\n  7일 동안의 별점 기록:")
    for i, s in enumerate(gs.day_stars, 1):
        print(f"  {i}일차: {'★' * s}{'☆' * (5-s)}")
    print(f"\n  총 별점: {gs.total_stars}개  |  하루 평균: {avg:.1f}점")
    print(f"  {gs.cname}의 최종 상태: 건강 {gs.health} / 기분 {gs.mood}")
    pause()

    clr()
    slow(f"\n  7일째 밤, {gs.cname}의 주인이 데리러 왔어요...")
    time.sleep(0.8)

    if avg >= 4.0 and gs.health >= 60 and gs.mood >= 55:
        hdr("  [최고의 집사 엔딩] ★★★")
        slow(f"\n  {gs.cname}은(는) 주인을 보자 반갑게 울었지만,")
        slow(f"  곧 {gs.pname}의 다리에도 얼굴을 비볐어요.")
        slow(f"\n  주인이 환하게 웃으며 말했어요.")
        slow(f"  \"정말 고마워요. {gs.cname}이(가) 전보다 더 건강하고 행복해 보여요.")
        slow(f"  {gs.pname}, 당신은 최고의 임시 집사예요!\"")
        slow(f"\n  {gs.cname}이(가) 마지막으로 '냐아~' 하고 울었어요.")
        slow(f"  행복한 작별이에요.")
        print("\n  >>>  최고의 집사 엔딩 달성!  <<<")

    elif avg >= 2.5 or gs.health >= 45:
        hdr("  [괜찮은 집사 엔딩] ★★")
        slow(f"\n  주인이 {gs.cname}의 상태를 살펴보고 고개를 끄덕였어요.")
        slow(f"  \"조금 서툰 날도 있었지만, 정성껏 돌봐준 게 느껴져요.")
        slow(f"  {gs.pname}, 수고했어요.\"")
        slow(f"\n  {gs.cname}은(는) 작은 소리로 울며 {gs.pname}을(를) 바라보았어요.")
        slow(f"  다음엔 더 잘할 수 있을 것 같아요!")
        print("\n  >>>  괜찮은 집사 엔딩 달성!  <<<")

    else:
        hdr("  [아쉬운 집사 엔딩]")
        slow(f"\n  주인이 걱정스러운 얼굴로 {gs.cname}을(를) 꼭 안았어요.")
        slow(f"  \"아기고양이를 돌보는 건 생각보다 세심한 일이에요.")
        slow(f"  다음에는 {gs.cname}의 상태를 더 잘 살펴주세요.\"")
        slow(f"\n  {gs.cname}은(는) 피곤한 듯 주인의 품에 가만히 안겨 있었어요.")
        slow(f"  다음엔 더 잘할 수 있어요. 힘내요, {gs.pname}!")
        print("\n  >>>  아쉬운 집사 엔딩  <<<")

# ───────────────────────────────────────────────
# 메인
# ───────────────────────────────────────────────
def intro():
    clr()
    sep("═")
    print("  아기고양이 임시 집사 게임")
    print("   /\\_/\\    Baby Cat Caretaker   /\\_/\\ ")
    print("  ( ^w^ )                       ( ^w^ )")
    sep("═")
    slow("\n  7일 동안 아기고양이를 돌봐주세요!")
    slow("  매일 밥을 주고, 아이템을 사용하며")
    slow("  배고픔 / 기분 / 건강 / 졸림을 관리해요.")
    slow("  밤마다 주인이 찾아와 별점을 줄 거예요!")
    print()
    input("  [ 엔터를 눌러 시작 ]")

def main():
    while True:
        intro()

        clr()
        hdr("  게임 시작")

        pname = ""
        while not pname.strip():
            pname = input("\n  아기고양이를 돌볼 어린이의 이름을 입력하세요: ").strip()

        cname = ""
        while not cname.strip():
            cname = input(f"\n  안녕하세요 {pname}! 아기고양이의 이름을 지어주세요: ").strip()

        print(f"\n  {cname}의 성격을 골라주세요!")
        pkeys = list(PERSONALITIES.keys())
        for i, (k, v) in enumerate(PERSONALITIES.items(), 1):
            print(f"  {i}. {k}  ─  {v['desc']}")

        while True:
            try:
                pi = int(input("\n  번호 입력 >> ").strip()) - 1
                if 0 <= pi < len(pkeys):
                    break
            except ValueError:
                pass
            print("  올바른 번호를 입력해주세요.")

        pkey = pkeys[pi]

        clr()
        hdr("  게임 시작!")
        slow(f"\n  {pname}은(는) 오늘부터 7일 동안")
        slow(f"  아기고양이 {cname}을(를) 대신 돌보게 되었어요.")
        slow(f"\n  {cname}의 성격: {pkey}")
        slow(f"  {PERSONALITIES[pkey]['desc']}")
        slow(f"\n  {cname}의 주인은 매일 밤 찾아와")
        slow(f"  {cname}의 상태를 확인하고 별점을 줄 거예요.")
        slow(f"\n  7일 뒤, 주인은 {cname}을(를) 데리러 와요.")
        slow(f"  {pname}은(는) {cname}을(를) 건강하고 행복하게 돌볼 수 있을까요?")
        pause()

        gs = GS(pname, cname, pkey)

        for d in range(1, 8):
            gs.day = d
            run_day(gs)
            if d < 7:
                overnight(gs)

        show_ending(gs)

        again = ask("\n  다시 아기고양이를 돌보시겠어요?",
                    ["다시 시작한다!", "게임을 끝낸다"])
        if again == 1:
            break

    print("\n  게임을 해주셔서 감사해요! 안녕히 가세요~ /^w^\\\n")

if __name__ == "__main__":
    main()
