# -*- coding: utf-8 -*-
# ./site に index.html / mycalinks.html を生成（白背景・黒文字／重複CSS排除）
# - ヘッダーの店名テキスト削除（ロゴのみ表示）
# - ナビ左寄せ／タブ構成: HOME | 大会・イベント | 店頭買取 | 郵送買取 | デュエルスペース | アクセス | 通販 | X
# - 「買取」タブ→「郵送買取」に改名／「店頭買取」タブ新設
# - 大会イベントページはスケジュールのみ
# - 店頭買取2枚＆イベントスケジュール画像：白背景で黒枠
# - HOMEカルーセル改良：
#   * PC：左右の広い透明ヒットエリア（どこでも前後移動）、矢印ボタンも継続表示
#   * SP：横スワイプで前後、しきい値を軽め（25px）
#   * オート再生は触ったら一時停止→操作後に再開

from pathlib import Path
from string import Template
import shutil

# ===== 基本設定 =====
STORE_NAME   = "カードショップCLIMAX"
ADDRESS      = "〒101-0021 東京都千代田区外神田3-15-5 MNビル 3F"
SHOP_URL     = "https://www.climax-card.jp/"
BUYLIST_URL  = "https://climaxcard.github.io/climax/default/"
X_URL        = "https://x.com/climaxcard"
PRODUCTS_URL = "https://www.climax-card.jp/product-list/345"

MAP_EMBED_SRC = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d12959.948330384788!2d139.7712742631493!3d35.70193548613032!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x60188c1dd8a0a351%3A0x521f149db8f31043!2z44CSMTAxLTAwMjEg5p2x5Lqs6YO95Y2D5Luj55Sw5Yy65aSW56We55Sw77yT5LiB55uu77yR77yV4oiS77yV!5e0!3m2!1sja!2sjp!4v1758198516772!5m2!1sja!2sjp"

# 画像
LOGO_IMG               = "logo.png"
SCHEDULE_IMG           = "schedule.png"
POP_TOREKA_IMG         = "pop_toreka.png"
POP_MYCALINKS_IMG      = "pop_mycalinks.png"
DUEL_IMG               = "01.png"
POP_KAITORI_FLOW_IMG   = "kaitori_flow.png"
POP_MYCA_REGISTER_IMG  = "myca_register_pop.png"
POP_STORE_DRAGON_IMG   = "pop_store_dragon.png"
EVENTS_PHOTO           = "events_photo.jpg"
MAIL_POP_IMG           = "mail_buy.png"
BUY_CTA_IMG            = "yusoudragon.png"
X_ICON_CANDIDATES = ["unnamed.png","unnamaed.png"]  # ←候補
LINE_ICON_CANDIDATES = ["LINE.png","line.png","LINE.webp","line.webp","LINE.jpg","line.jpg","LINE.jpeg","line.jpeg","LINE.svg","line.svg"]

HOME_MAX_SLIDES = 7

TITLES_DEF = [
    {"name":"デュエル・マスターズ","key":"duel","url":"https://dm.takaratomy.co.jp/","imgs":["DUELMASTERS.webp","DUELMASTERS.png","duelmasters.webp","duelmasters.png","duelmasters.jpg"]},
    {"name":"ポケモンカードゲーム","key":"poke","url":"https://www.pokemon-card.com/","imgs":["pokemon.png","pokemon.webp","pokemon.jpg","POKEMON.png"]},
    {"name":"Disney Lorcana","key":"lorc","url":"https://www.takaratomy.co.jp/products/disneylorcana/","imgs":["LORCANA.png","LORCANA.webp","lorcana.png","lorcana.jpg"]},
    {"name":"ヴァイスシュヴァルツ","key":"weiss","url":"https://ws-tcg.com/","imgs":["WEISSCHWARZ.png","WEISSSCHWARZ.png","weissschwarz.png","weiss.png"]},
]

# ===== 出力先（スクリプトの場所基準に統一）=====
ROOT = Path(__file__).resolve().parent
# スクリプトが site フォルダ内にある場合はそのまま出力、それ以外は site/ を作る
OUT  = ROOT if ROOT.name.lower() == "site" else (ROOT / "site")
OUT.mkdir(parents=True, exist_ok=True)

# ===== ユーティリティ（先に定義してから使う） =====
def safe_copy(src: Path):
    if not src or not src.exists() or not src.is_file():
        return
    try:
        rel = src.relative_to(ROOT)
    except ValueError:
        rel = Path(src.name)
    dst = OUT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        # 自分自身をコピーしようとしている場合はスキップ
        if dst.exists() and dst.resolve() == src.resolve():
            return
    except Exception:
        pass
    if not dst.exists():
        shutil.copy(src, dst)

def find_asset(name: str):
    """ROOT または OUT にあるアセットを探す"""
    for d in (ROOT, OUT):
        p = d / name
        if p.exists():
            return p
    return None
# --- yusoudragon の拡張子ゆらぎを自動検出 ---
if not find_asset(BUY_CTA_IMG):
    base = "yusoudragon"
    for ext in (".png",".PNG",".webp",".WEBP",".jpg",".JPG",".jpeg",".JPEG",".gif",".GIF"):
        p = find_asset(base + ext)
        if p:
            BUY_CTA_IMG = p.name  # 見つかった実名で上書き
            break


# ===== スライド検出 =====
ALLOWED_EXT = {".png",".jpg",".jpeg",".webp",".gif",".PNG",".JPG",".JPEG",".WEBP",".GIF"}
def find_one(base: str):
    for d in (ROOT, OUT):
        for ext in ALLOWED_EXT:
            p = d / f"{base}{ext}"
            if p.exists(): return p
    return None

slides_paths = []
for base in ("slide1","slide2","slide3"):
    p = find_one(base)
    if p: slides_paths.append(p)
if len(slides_paths) < HOME_MAX_SLIDES:
    seen = {p.name.lower() for p in slides_paths}
    for d in (ROOT, OUT):
        for p in sorted(d.glob("slide*")):
            if p.is_file() and p.suffix in ALLOWED_EXT:
                k = p.name.lower()
                if k not in seen:
                    slides_paths.append(p); seen.add(k)
                    if len(slides_paths) >= HOME_MAX_SLIDES: break

# ===== 画像コピー =====
for name in (LOGO_IMG, SCHEDULE_IMG, POP_TOREKA_IMG, POP_MYCALINKS_IMG, DUEL_IMG,
             POP_KAITORI_FLOW_IMG, POP_MYCA_REGISTER_IMG, POP_STORE_DRAGON_IMG,
             EVENTS_PHOTO, MAIL_POP_IMG, BUY_CTA_IMG):
    p = ROOT / name
    if p.exists(): safe_copy(p)
for sp in slides_paths: safe_copy(sp)

# ===== X / LINE アイコン検出 =====
X_ICON_IMG = ""
for cand in X_ICON_CANDIDATES:
    p = find_asset(cand)
    if p:
        safe_copy(p)
        X_ICON_IMG = (OUT / p.name).name
        break

LINE_ICON_IMG = ""
for cand in LINE_ICON_CANDIDATES:
    p = find_asset(cand)
    if p:
        safe_copy(p)
        LINE_ICON_IMG = (OUT / p.name).name
        break

# HTML片（見つからない場合はテキストリンク）
X_ICON_HTML = f'<img src="{X_ICON_IMG}" alt="X" class="x-icon-img" onerror="this.style.display=\'none\'">' if X_ICON_IMG else ""
LINE_ICON_HTML = (f'<img src="{LINE_ICON_IMG}" alt="LINE" class="line-icon-img" onerror="this.style.display=\'none\'">'
                  if LINE_ICON_IMG else "LINE")

def find_asset(name: str):
    for d in (ROOT, OUT):
        p = d / name
        if p.exists(): return p
    return None

TITLE_ITEMS = []
for t in TITLES_DEF:
    chosen = None
    for cand in t["imgs"]:
        p = find_asset(cand)
        if p:
            safe_copy(p)
            chosen = (OUT / p.name).name
            break
    if chosen:
        TITLE_ITEMS.append({"name":t["name"],"url":t["url"],"img":chosen,"key":t["key"]})

# ===== 部品HTML =====
def site_name(p: Path) -> str:
    return (OUT / p.name).name

if slides_paths:
    SLIDES_HTML = "".join(
        f'<div class="slide fit">'
        f'  <a class="slide-link" href="{PRODUCTS_URL}" target="_blank" rel="noopener" aria-label="商品一覧へ">'
        f'    <img src="{site_name(p)}" alt="HOMEスライド">'
        f'  </a>'
        f'</div>'
        for p in slides_paths
    )
    DOTS_HTML   = "".join('<div class="dot"></div>' for _ in slides_paths)
else:
    SLIDES_HTML = (
        f'<div class="slide fit">'
        f'  <a class="slide-link" href="{PRODUCTS_URL}" target="_blank" rel="noopener" aria-label="商品一覧へ">'
        f'    <img src="{LOGO_IMG}" alt="HOMEスライド">'
        f'  </a>'
        f'</div>'
    )
    DOTS_HTML   = '<div class="dot active"></div>'


X_ICON_HTML = f'<img src="{X_ICON_IMG}" alt="X" class="x-icon-img" onerror="this.style.display=\'none\'">' if X_ICON_IMG else ""

def title_class(key: str) -> str:
    return "title-card--duel" if key=="duel" else ""

TITLES_HTML = "".join(
    f'<a class="title-card {title_class(item["key"])}" href="{item["url"]}" target="_blank" rel="noopener" aria-label="{item["name"]}">'
    f'  <img src="{item["img"]}" alt="{item["name"]} ロゴ">'
    f'</a>'
    for item in TITLE_ITEMS
) or '<div style="color:#888;">（タイトル画像をこの .py または site/ に置くと表示されます）</div>'
# --- 郵送買取POP (あるときだけ差し込む) ---
MAIL_POP_HTML = ""
if find_asset(MAIL_POP_IMG):
    p = find_asset(MAIL_POP_IMG)
    if p: safe_copy(p)
    MAIL_POP_HTML = f'<img class="buy-pop" src="{MAIL_POP_IMG}" alt="郵送買取案内POP">'
# --- 左側のバナー（ボタンの代わりに表示） ---
BUY_CTA_HTML = ""
p = find_asset(BUY_CTA_IMG)
if p:
    safe_copy(p)
    BUY_CTA_HTML = (
        f'<a class="buy-cta-link" href="{BUYLIST_URL}" target="_blank" aria-label="買取表を見る">'
        f'  <img class="buy-cta-img" src="{p.name}" alt="買取金額">'
        f'</a>'
    )
else:
    # 画像が無いときでもリンクは出す（デバッグにもなる）
    BUY_CTA_HTML = (
        f'<a class="buy-cta-link" href="{BUYLIST_URL}" target="_blank" '
        f'style="display:inline-block;padding:.6em 1em;border:1px solid #222;border-radius:8px;'
        f'text-decoration:none;font-weight:900;color:#111;">買取表を見る</a>'
    )
# ===== HTMLテンプレ（1本化・白基調＋カルーセル強化） =====
INDEX_HTML = Template(r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>${STORE_NAME} - 公式サイト</title>
<meta name="theme-color" content="#ffffff" />
<style>
  :root{
  --home-slide-max:720px;
  --soft: 0 8px 24px rgba(0,0,0,.08);
  --cta-ar: 16/9;      /* 枠の比率（16:9） */
  --cta-zoom: 1;       /* 画像の拡大率（1=等倍） */
  --cta-pos-x: 50%;    /* 画像の表示位置X */
  --cta-pos-y: 50%;    /* 画像の表示位置Y */
  --cta-shift: 0px;    /* 追加の横シフト */
}
  /* === Carousel: PCは矢印＋広いヒットエリア／SPはスワイプ === */
  .carousel { position: relative; }
  .carousel .ctrl{
    z-index: 3; /* 画像より前面 */
    opacity: .9;
  }
  .prev-hit{ left:0; } .next-hit{ right:0; }
  @media (max-width:900px){
    .carousel .ctrl{ display:none; }  /* スマホは矢印隠す */
    .edge-hit{ display:none; }        /* スマホはヒットエリアも隠す（スワイプに専念） */
    .carousel .track{
      touch-action: pan-y;            /* 縦スクロールは通しつつ横スワイプ可 */
      cursor: grab;
    }
  }
/* --- 強制表示＆edge-hit無効化 --- */
.carousel .ctrl{ display:block !important; z-index:5; }
@media (max-width:900px){
  .carousel .ctrl{ display:none !important; } /* SPは矢印非表示（スワイプ優先） */
}
/* 透明ヒットエリアは一旦無効化（クリックを奪うので） */
.edge-hit{ display:none !important; }


  /* ===== 基本（白地・黒文字） ===== */
  body{
    margin:0;
    font-family:system-ui,-apple-system,Segoe UI,Roboto,'Noto Sans JP',sans-serif;
    color:#111;
    background:#fff;
  }

  /* ===== Header（白） ===== */
  header{
    position:sticky; top:0; z-index:50;
    background:#fff;
    color:#111;
    border-bottom:1px solid #e5e7eb;
    box-shadow:0 2px 6px rgba(0,0,0,.08);
  }
  .h-inner{ max-width:1200px; margin:auto; padding:10px 16px; display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
  .brand{ display:flex; align-items:center; gap:10px; text-decoration:none; white-space:nowrap; }
  .brand img{ height:78px; width:auto; }
  nav{ display:flex; align-items:center; gap:6px; white-space:nowrap; flex:1 1 auto; justify-content:flex-start; flex-wrap:wrap; }
  nav a{ padding:8px 10px; border-radius:10px; color:#111; font-weight:800; text-decoration:none; }
  .nav-active{ background:rgba(0,0,0,.06); }
  nav a:hover{ background:rgba(0,0,0,.05); }
  .cta{ background:#111; color:#fff !important; border-radius:999px; padding:8px 14px; }
  .x-icon-img{ width:28px; height:28px; display:inline-block; vertical-align:middle; border-radius:6px; object-fit:cover; }
  .line-icon-img{
  width:28px; height:28px; display:inline-block; vertical-align:middle;
  border-radius:6px; object-fit:cover;
}
@media (min-width:900px){
  header .x-icon-img, header .line-icon-img{ width:34px !important; height:34px !important; }
}
  .container{ max-width:1200px; margin:auto; padding:24px 16px; }
  .section{ display:none; } .section.active{ display:block; }

  /* ===== HOME：左スライド / 右POP ===== */
  .home-grid{ display:grid; grid-template-columns:minmax(360px,var(--home-slide-max)) 1fr; gap:16px; align-items:start; }
  .carousel{ position:relative; overflow:hidden; border-radius:18px; border:1px solid #e5e7eb; background:#fff; box-shadow:var(--soft); }
  .track{ position:relative; z-index:1; display:flex; transition:transform .5s ease; align-items:stretch; }
  .slide{ position:relative; min-width:100%; }
  .slide.fit a{ display:block; }
.slide.fit img{
 width:100%; height:auto; display:block; object-fit:contain; object-position:center center; background:transparent; -webkit-user-drag:none; user-select:none; }
  .ctrl{ position:absolute; top:50%; transform:translateY(-50%); background:rgba(17,17,17,.6); color:#fff; border:none; width:44px; height:44px; border-radius:50%; cursor:pointer; }
  .prev{ left:10px; } .next{ right:10px; }
  .dots{ position:absolute; left:0; right:0; bottom:8px; display:flex; gap:6px; justify-content:center; z-index:2; }
  .dot{ width:8px; height:8px; border-radius:999px; background:#fff; border:1px solid rgba(0,0,0,.2); opacity:.85; }
  .dot.active{ opacity:1; }

  .home-side{ display:flex; flex-direction:column; gap:16px; }
  .home-card{ border-radius:18px; border:1px solid #e5e7eb; overflow:hidden; background:#fff; box-shadow:var(--soft); }
  /* === HOME POP画像（横幅優先・ガビガビ防止）=== */
.home-card img{
  width:100%;
  height:auto;                  /* 拡大せず等倍維持 */
  object-fit:cover;             /* 横幅いっぱいに合わせる（上下トリミングあり） */
  object-position:center center;/* 中央基準でトリム */
}

  /* ===== 取扱タイトル ===== */
  .titles{ position:relative; background:#fff; border:1px solid #e5e7eb; border-radius:22px; padding:18px; margin-top:20px; box-shadow:var(--soft); }
  .titles h2{ position:relative; z-index:1; margin:0 0 8px; font-size:1.25rem; }
  .title-grid{ position:relative; z-index:1; display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; }
  .title-card{
    position:relative; display:grid; place-items:center; height:190px;
    background:#fff; color:#111;
    border:1px solid #e5e7eb; border-radius:18px; overflow:hidden; box-shadow:0 8px 18px rgba(0,0,0,.06);
  }
  .title-card::after{ content:""; position:absolute; left:10px; right:10px; bottom:10px; height:4px; border-radius:8px;
    background:linear-gradient(90deg, #ff8bd1, #ffd18b, #8bdfff, #b88bff); opacity:.55; }
  .title-card img{ max-width:96%; max-height:150px; height:auto; display:block; }
  .title-card--duel img{ max-height:175px; transform:scale(1.05); }

  /* ===== 大会・イベント ===== */
  .event-intro{
    white-space:pre-line;
    margin:10px 0 14px;
    color:#111;
  }
  .event-row{ display:flex; align-items:flex-start; gap:16px; }
  .event-row .left, .event-row .right{ flex:1 1 0; display:flex; }
  .event-row .right{ justify-content:flex-end; }
  .event-row .left img{
    width:100%; height:auto; display:block;
    border-radius:12px; border:1px solid #000; background:#fff;
    box-shadow:0 2px 6px rgba(0,0,0,.12);
  }

  :root{ --schedule-lift: 96px; --schedule-crop: 4%; }
  #events .event-row{ align-items:flex-start; }
  #events .event-row .right{ margin-top: calc(-1 * var(--schedule-lift)); justify-content:flex-end; }
  #events .event-row .right > img{
    width:80% !important; height:auto !important; display:block;
    border-radius:12px; border:1px solid #000; background:#fff;
    clip-path: inset(var(--schedule-crop) 0 var(--schedule-crop) 0 round 12px);
    box-shadow:0 2px 6px rgba(0,0,0,.12);
  }
  #events .event-row .right .event-schedule{ width:80% !important; margin-top: calc(-1 * var(--schedule-lift)); }
  /* ラッパーに枠線を付けて画像の上下を clip しても線が消えないように */
#events .event-row .right .event-schedule{
  width:80% !important;
  margin-top: calc(-1 * var(--schedule-lift));
  border:1px solid #000;            /* ← 枠線はこちらに移動 */
  border-radius:12px;
  background:#fff;
  overflow:hidden;                   /* ← 角丸＋clip整合 */
  box-shadow:0 2px 6px rgba(0,0,0,.12);
}

#events .event-row .right .event-schedule img{
  width:100% !important;
  height:auto !important;
  display:block;
  border:none;                       /* ← ボーダー外す */
  border-radius:0;                   /* ← 角丸はラッパーに任せる */
  background:#fff;
  clip-path: inset(var(--schedule-crop) 0 var(--schedule-crop) 0 round 12px);
  box-shadow:none;                   /* ← 影もラッパーに任せる */
}
/* EVENTS も STOREBUY/BUY と同じ位置に揃える */
@media (min-width:900px){
  #events{
    width:80%;
    margin-left:16%;
    margin-right:0;
  }
  /* 以前の右寄せは打ち消す */
  #events .event-intro,
  #events .event-row .left{
    margin-left:0 !important;
  }
}
  /* ===== 店舗情報＆決済（白基調の表） ===== */
  .info-wrap{ display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:20px; }
  .panel{ background:#fff; border:1px solid #e5e7eb; border-radius:16px; padding:16px; box-shadow:0 8px 24px rgba(0,0,0,.04); }
  .panel h3{ margin:0 0 10px; font-size:1.1rem; color:#111; }
  .info-table{ width:100%; border-collapse:separate; border-spacing:0 8px; }
  .info-table th{ text-align:left; white-space:nowrap; padding:6px 10px; width:10em; color:#111; background:#f5f6f8; border-radius:8px; border:1px solid #e5e7eb; }
  .info-table td{ padding:6px 10px; border-radius:8px; border:1px solid #e5e7eb; background:#fff; color:#111; }

  .pay-group{ margin-top:10px; }
  .chips{ display:flex; flex-wrap:wrap; gap:8px; margin-top:6px; }
  .chip{ display:inline-flex; align-items:center; padding:6px 10px; border-radius:999px;
         background:#fff; color:#111; border:1px solid rgba(0,0,0,.12); box-shadow:0 2px 6px rgba(0,0,0,.06); font-weight:700; font-size:.95rem; }

  /* ===== デュエルスペース ===== */
  .duel-grid{ display:grid; grid-template-columns:1.1fr .9fr; gap:18px; align-items:start; color:#111; }
  .duel-image{ border-radius:16px; overflow:hidden; border:1px solid #000; background:#fff; box-shadow:0 2px 6px rgba(0,0,0,.12); }
  .duel-image img{ width:100%; height:auto; display:block; }
  .duel-stack{ display:flex; flex-direction:column; gap:14px; align-items:flex-end; }
  .duel-panel{ width:100%; max-width:620px; border:1px solid rgba(0,0,0,.12); border-radius:16px; padding:14px; background:rgba(0,0,0,.04); }
  .links{ display:flex; gap:10px; flex-wrap:wrap; margin-top:10px; }
  .btn{ display:inline-block; padding:10px 14px; border-radius:12px; font-weight:900; text-decoration:none; }
  .btn-outline{ border:2px solid rgba(0,0,0,.22); color:#111; }
  .btn-outline:hover{ background:rgba(0,0,0,.05); }

  /* ===== 店頭買取画像（黒枠） ===== */
  .storebuy-wrap{ width:80%; margin-left:0; margin-right:auto; }
  .storebuy-left img, .storebuy-right img{
    border:1px solid #000; border-radius:12px; background:#fff; box-shadow:0 2px 6px rgba(0,0,0,.12);
  }

  /* Mycalinks リンク強調（白基調） */
.storebuy-note .myca-link, .storebuy-note .myca-link:visited,
.buy-note .myca-link, .buy-note .myca-link:visited{
  color:#dc2626; font-weight:900; text-decoration:underline; text-decoration-color:rgba(220,38,38,.95);
  text-decoration-thickness:2px; text-underline-offset:3px;
}
.storebuy-note .myca-link:hover,
.buy-note .myca-link:hover{
  background:rgba(220,38,38,.10); border-radius:6px; padding:0 4px;
}
.storebuy-note .myca-link:focus-visible,
.buy-note .myca-link:focus-visible{
  outline:2px solid #dc2626; outline-offset:2px;
}

  /* ===== アクセスの地図枠 ===== */
  .map-wrap{ margin-top:16px; border:1px solid #e5e7eb; border-radius:16px; overflow:hidden; box-shadow:var(--soft); background:#fff; }

  /* ===== レスポンシブ ===== */
  @media (max-width:900px){
    header .h-inner{ padding:8px 12px; flex-direction:column; align-items:center; gap:6px; }
    .brand{ order:0; width:100%; justify-content:center; }
    .brand img{ height:44px; }
    nav{ order:1; width:100%; display:flex; justify-content:center; gap:6px; flex-wrap:nowrap; overflow-x:auto; -webkit-overflow-scrolling:touch; padding-bottom:4px; }
    nav a{ padding:6px 8px; font-size:.9rem; white-space:nowrap; }
    nav::-webkit-scrollbar{ display:none; } nav{ scrollbar-width:none; }

    .titles{ padding:12px; }
    .title-grid{ grid-template-columns:repeat(2, 1fr); gap:10px; }
    .title-card{ height:120px; border-radius:14px; }
    .title-card img{ max-height:80px; }

    .event-row{ flex-direction:column; gap:12px; }
    #events{ --schedule-lift:0px; }
    #events .event-row .right{ margin-top:24px; justify-content:center; align-items:center; width:100%; }
    #events .event-row .right .event-schedule,
    #events .event-row .right > img{
      margin-top:0; width:92%; max-width:520px; margin-left:auto; margin-right:auto; clip-path:none; position:static; z-index:auto;
    }
    #events .event-row .right .event-schedule img{ width:100%; height:auto; clip-path:none; }

    .storebuy-wrap{ width:100%; margin:0 auto; }
    .storebuy-right{ display:flex; flex-direction:column; gap:10px; }
    .storebuy-right img, .storebuy-left img{ width:100%; height:auto; object-fit:contain; display:block; margin:0 auto; }

    .info-wrap{ grid-template-columns:1fr; }
    .home-grid{ grid-template-columns:1fr; }
    .duel-grid{ grid-template-columns:1fr; }
    .duel-stack{ align-items:stretch; }
  }

  @media (min-width:900px){
    .storebuy-wrap{ display:flex; flex-direction:row; align-items:stretch; gap:20px; }
    .storebuy-left, .storebuy-right{ flex:1 1 0; display:flex; flex-direction:column; }
    .storebuy-left img{ width:100%; height:100%; object-fit:cover; }
    .storebuy-right{ display:grid; grid-template-rows:1fr 1fr; gap:20px; }
    .storebuy-right img{ width:100%; height:100%; object-fit:cover; }
  }

  /* ===== Duel Space（安全版スタイル） ===== */
  #duel .duel-panel { box-sizing:border-box; overflow:visible !important; }
  .duel-badges, .badge { display:none !important; }
  .duel-headline{ font-weight:900; font-size:1.1em; letter-spacing:.02em; white-space:nowrap; }
  @media (min-width: 900px){
    .duel-grid{ display:flex !important; align-items:stretch !important; gap:16px; }
    .duel-image{
      flex:1.3 1 0; display:flex; align-items:flex-start; justify-content:center;
      border:2px solid #000; border-radius:18px; background:#fff; box-shadow:0 2px 6px rgba(0,0,0,.12);
    }
    .duel-image img{ width:100%; height:100%; object-fit:contain; object-position:top center; }
    .duel-stack{ flex:0.7 1 0; display:flex; flex-direction:column; gap:14px; }
    .duel-panel{
      flex:1 1 0; display:flex; flex-direction:column; justify-content:center;
      padding:12px; font-size:1.02em; line-height:1.5; background:rgba(0,0,0,.04);
      border:1px solid rgba(0,0,0,.12); border-radius:16px;
    }
    #duel .duel-panel--compact{ padding:8px 10px; line-height:1.35; }
  }
/* ===== Duel 右パネルの余白をタイトに ===== */
#duel .duel-panel{
  padding:10px 12px;          /* 14px → 10px に圧縮 */
  line-height:1.32;           /* 1.5 → 1.32 で詰める */
  border-radius:12px;         /* 16px → 12px（締まって見える） */
}
#duel .duel-panel--compact{
  padding:6px 10px;           /* 8px → 6px */
  line-height:1.22;           /* 1.35 → 1.22 */
}
#duel .duel-panel h3{ 
  margin:0 0 4px;             /* タイトル下の余白を減らす */
  font-size:1.02rem;
}
#duel .duel-panel p{ 
  margin:6px 0 0;             /* 段落の上下余白を減らす */
}
#duel .duel-panel ul{ 
  margin:6px 0 0; 
  padding-left:1.1em; 
}
#duel .duel-panel li{ 
  margin:3px 0;               /* 箇条書きの行間も詰める */
}

/* 右カラムどうしのスキマも少しだけ縮める */
@media (min-width:900px){
  .duel-stack{ gap:10px; }    /* 14px → 10px */
}
/* --- Duel: 画像枠をもう少し上へ（余白カット） --- */
#duel .duel-image{ margin:0 !important; }      /* figure 既定マージン除去 */
#duel h2{ margin:0 0 8px !important; }         /* 見出し下を少し詰める */
#duel .container{ padding-top:12px !important; }/* セクション上パディング控えめ */
/* === BUY（郵送買取）: テーブルと画像を2カラム、左は短め幅 === */
#buy .buy-layout{
  display:grid;
  grid-template-columns:minmax(320px,560px) minmax(220px,1fr);
  gap:16px; align-items:start;
}

/* 左：表とバナーを同じ幅で束ねる */
#buy .buy-card{
  width:100%;
  max-width:560px;          /* ここを 520/480 に下げるとさらに短くできます */
}

/* 表はラッパー幅いっぱい＝「短い枠」 */
#buy .buy-table{
  width:100% !important;    /* ラッパーに合わせる */
  table-layout:fixed;
}

/* 右：郵送POPは小さめ */
#buy .buy-pop{
  width:100%; max-width:480px; height:auto;
  border:1px solid #e5e7eb; border-radius:12px;
  box-shadow:0 4px 12px rgba(0,0,0,.08);
}
/* 注意事項：ベース */
#buy .buy-notes.panel{
  margin:16px 0 0;
  padding:16px;
  border:1px solid #e5e7eb;
  border-radius:12px;
  background:#fff;
  box-shadow:0 4px 12px rgba(0,0,0,.05);
}

/* PCだけ：右から10%削る＋少し上げる */
@media (min-width:900px){
  #buy .buy-notes.panel{
    width:85.3%;            /* 全体の90%幅＝右を10%削った見え方 */
    margin:-8px 10% 0 0;  /* 上-8px / 右10% / 下0 / 左0 */
  }
}

/* SP は全幅 */
@media (max-width:899px){
  #buy .buy-notes.panel{
    width:100%;
    margin:12px 0 0;
  }
}
/* === PCだけ：店頭買取／郵送買取セクションを右にずらす === */
@media (min-width: 900px){
  #storebuy,
  #buy {
    width: 80%;          /* 横幅を少し狭くする */
    margin-left: 16%;    /* 左に20%の余白を取って右寄せ */
    margin-right: 0;     /* 念のため右余白は0に */
  }
}
/* === PCだけ：ヘッダー中身（ロゴ＋ナビ）を20%右へ === */
@media (min-width: 900px){
  header .h-inner{
    max-width: none !important; /* 中央寄せのauto制御を解除 */
    width: 80% !important;      /* 中身の横幅を80%に */
    margin-left: 19.5% !important;/* 左に20%の余白を作って全体を右へ */
    margin-right: 0 !important;
  }
}
/* === PCだけ：ナビの文字とXアイコンを1.2倍 === */
@media (min-width: 900px){
  /* 各タブ（HOME〜通販サイト） */
  header nav { gap: 8px !important; }                /* 6 → 8px（少し広げる） */
  header nav a{
    font-size: 1.2em !important;                     /* 文字を1.2倍 */
    padding: 10px 12px !important;                   /* 8x10 → 10x12 に微増 */
    border-radius: 12px !important;                  /* 少しだけ丸みも増やす（任意） */
  }
  /* 通販ボタンは横幅も少し余裕 */
  header nav a.cta{
    padding: 10px 16px !important;                   /* 見栄え用に横だけさらに+4px */
  }
  /* Xアイコン画像（28px → 約34px） */
  header .x-icon-img{
    width: 34px !important;
    height: 34px !important;
  }
}

/* 余白や枠はナシのまま */
#buy .buy-cta{
  margin-top: 0;
  border: none !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  background: transparent !important;
}

/* PC時、左カラム幅に自然に収まるように */
@media (min-width: 900px){
  #buy .addr-cta { max-width: 560px; }
}
/* === BUY（郵送買取） === */
#buy .buy-cta-link{
  position: relative;
  display: block;
  width: 100%;
  aspect-ratio: var(--cta-ar);
  overflow: hidden; /* 切り抜きが枠からはみ出さないように */
}

#buy .buy-cta-img{
  position: absolute; inset: 0;
  width: 100%; height: 100%; display: block;
  object-fit: cover;
  clip-path: inset(10% 0 10% 0);

  /* 右へ寄せ + 上へ寄せ */
  transform: translate(1.5%, -8%) scale(1.2);
  transform-origin: center center;
}
/* === SPだけ：BUYを縦並び & 余白圧縮 & yusoudragon右寄せ＋上下トリム === */
@media (max-width: 900px){

  /* BUYは縦積み（表 → mail_buy → yusoudragon → 注意事項） */
  #buy .buy-layout{
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;                 /* ← グリッドの隙間を小さく */
    align-items: start;
  }
  #buy .buy-card{ order: 1; }
  #buy .buy-right{ order: 2; }

  /* 表の上マージン＆行間の隙間を圧縮（発送先住所〜ボタン間の“空白”対策） */
  #buy .buy-table{
    margin-top: 8px !important;          /* 16px → 8px */
    border-collapse: separate !important;
    border-spacing: 0 4px !important;    /* 0 8px → 0 4px（行間を半分） */
  }

  /* mail_buy 画像は横幅いっぱい・等倍描画（ガビ防止） */
  #buy .buy-right img,
  #buy .buy-pop{
    width: 100% !important;
    max-width: none !important;
    height: auto !important;
    display: block !important;
    image-rendering: auto !important;
    object-fit: contain !important;
  }

  /* yusoudragon（SP専用）：高さを低めに、右寄せ、上下トリムで“余白感”を削る */
  #buy .buy-cta{ margin-top: 6px !important; }

  #buy .buy-cta-link{
    position: relative !important;
    display: block !important;
    width: 100% !important;
    aspect-ratio: 16/7 !important;   /* ← 16/9より“低い”比率。縦の余白を減らすキモ */
    overflow: hidden !important;
  }

  #buy .buy-cta-img{
    position: absolute !important;
    inset: 0 !important;
    width: 100% !important;
    height: 100% !important;
    display: block !important;

    /* 右寄せ＋上下トリム＋軽い拡大 */
    object-fit: cover !important;
    object-position: 48% center !important;   
    transform: translateX(1.5%) scale(1.2) !important; /* ← さらに少し右へ寄せつつ1.2倍 */
    transform-origin: center center !important;
    clip-path: inset(12% 0 12% 0) !important; /* ← 上下をカット（15～25%で微調整可） */

    image-rendering: auto !important;
  }

  /* 注意事項：右から削る指定はそのまま活かす */
  #buy .buy-notes.panel{
    width: 90% !important;
    margin: 12px 12% 0 0 !important; /* 上12 / 右12% / 下0 / 左0 */
  }
}
/* SP（～900px）で buy-table の列幅を 30:70 にする */
@media (max-width: 900px){
  #buy .buy-table{
    table-layout: fixed;         /* 列幅を固定的に解釈させる */
    width: 100%;
  }
  #buy .buy-table th{
    width: 28% !important;       /* 左カラム（ラベル）を狭く */
    white-space: nowrap;          /* 「発送」などは1行で */
    padding-right: 8px;           /* 右詰め気味で余白を軽く */
  }
  #buy .buy-table td{
    width: 72% !important;       /* 右カラムを広く */
    word-break: break-word;       /* 長文でもはみ出さない */
  }
}

/* === SP（～900px）: HOMEの「営業時間」「買取受付時間」を2行に収める === */
@media (max-width: 900px){
  /* 見出し列を少しだけ細くして本文側の横幅を確保 */
  #home .info-table th{ width: 7.5em; }

  /* 5行目=営業時間, 6行目=買取受付時間 の右セルのみ2行でクランプ */
  #home .info-table tr:nth-child(5) td,
  #home .info-table tr:nth-child(6) td{
    display: -webkit-box;          /* iOS/Safari対応の行数制限 */
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;         /* 最大2行 */
    overflow: hidden;              /* 3行目以降は隠す（必要なら…で省略可） */
    line-height: 1.35;             /* ちょい詰めで収まりやすく */
    /* 省略記号を出したい場合は次行ON */
    /* text-overflow: ellipsis; */
  }
}
/* === SP（～900px）: HOME 情報テーブルのクランプ調整 === */
@media (max-width: 900px){
  /* 右セルに少しでも横幅を渡す（見出し側を少し細く） */
  #home .info-table th{
    width: 6.6em;           /* 7.5em → 少し細く */
    padding-right: 8px;
  }

  /* 共通：2行クランプ用 */
  #home .info-table .clamp-2{
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;   /* 最大2行 */
    overflow: hidden;
    line-height: 1.35;
    word-break: break-word;
  }

  /* 共通：3行クランプ用 */
  #home .info-table .clamp-3{
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;   /* 最大3行 */
    overflow: hidden;
    line-height: 1.35;
    word-break: break-word;
  }
}
/* === SP（～900px）: HOME 情報テーブルの収まり最適化（省略なし狙い） === */
@media (max-width: 900px){
  /* 横幅の稼ぎ：左右パディングを少しだけ削る */
  #home .container{ padding-left: 12px; padding-right: 12px; }

  /* テーブル全体をタイトに */
  #home .info-table{
    border-collapse: separate !important;
    border-spacing: 0 3px !important;     /* 行間 8px → 3px */
    font-size: .96em;                      /* 全体をほんの少し縮小 */
  }

  /* 見出し列をやや細く、本文側の幅を確保 */
  #home .info-table th{
    width: 6.2em !important;               /* 右セルへ面積を回す */
    padding: 5px 8px !important;           /* 6x10 → 5x8 */
    white-space: nowrap;
  }
  #home .info-table td{
    padding: 5px 8px !important;           /* 6x10 → 5x8 */
  }

  /* アクセス文（3行以内）を収めやすく */
  #home .info-table .clamp-3{
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;                 /* 最大3行 */
    overflow: hidden;
    line-height: 1.28;                      /* 行間を少し詰める */
    font-size: .95em;                       /* さらに微縮小 */
    word-break: break-word;
  }

  /* 営業時間/買取受付時間（2行以内）を収めやすく */
  #home .info-table .clamp-2{
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;                 /* 最大2行 */
    overflow: hidden;
    line-height: 1.28;
    font-size: .95em;                       /* さらに微縮小 */
    word-break: break-word;
  }
}
/* === FINAL OVERRIDE: SP yusoudragon 強制トリム === */
@media (max-width: 900px){
  /* 箱は低め比率で上下を切る前提 */
  #buy .buy-cta-link{
    aspect-ratio: 16/7 !important;
    height: auto !important;
    overflow: hidden !important;
    position: relative !important;
  }
  /* 画像は全面に敷いて上下カット */
  #buy .buy-cta-img{
    position: absolute !important;
    inset: 0 !important;
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;            /* ← これで上下トリムの土台 */
    object-position: 50% 50% !important;     /* 右に寄せたければ 52–55% に */
    clip-path: inset(14% 0 14% 0) !important;/* ← ここで上下カット量を微調整(10–20%) */
    transform: none !important;              /* 余計な拡大/平行移動は無効化 */
  }
}

</style>
</head>
<body>
<header>
  <div class="h-inner">
    <a class="brand" href="#home">
      <img src="${LOGO_IMG}" alt="${STORE_NAME} ロゴ" />
    </a>
    <nav>
      <a href="#home"     class="navlink" data-section="home">HOME</a>
      <a href="#events"   class="navlink" data-section="events">大会・イベント</a>
      <a href="#storebuy" class="navlink" data-section="storebuy">店頭買取</a>
      <a href="#buy"      class="navlink" data-section="buy">郵送買取</a>
      <a href="#duel"     class="navlink" data-section="duel">デュエルスペース</a>
      <a href="#access"   class="navlink" data-section="access">アクセス</a>
      <a href="${SHOP_URL}" target="_blank" class="cta">通販サイト</a>
      <a href="${X_URL}" target="_blank" aria-label="X アカウント" title="@climaxcard">${X_ICON_HTML}</a>
<a href="https://line.me/R/ti/p/@512nwjvn" target="_blank" rel="noopener"
   aria-label="LINE" title="LINE">${LINE_ICON_HTML}</a>

    </nav>
  </div>
</header>

<main>
  <!-- HOME -->
  <section id="home" class="section active">
    <div class="container">
      <div class="home-grid">
        <div class="carousel" id="carousel" aria-roledescription="carousel">
          <div class="track" id="track">${SLIDES_HTML}</div>
          <button class="ctrl prev" id="prev" aria-label="前へ">&#9664;</button>
          <button class="ctrl next" id="next" aria-label="次へ">&#9654;</button>
          <div class="dots" id="dots">${DOTS_HTML}</div>
        </div>
        <div class="home-side" id="homeSide">
          <a class="home-card navlink" data-section="buy" href="#buy">
  <img src="${POP_MYCALINKS_IMG}" alt="郵送買取案内">
</a>
          <a class="home-card" href="${SHOP_URL}" target="_blank"><img src="${POP_TOREKA_IMG}" alt="通販POP"></a>
        </div>
      </div>

      <div class="titles">
        <h2>取扱タイトル</h2>
        <div class="title-grid">${TITLES_HTML}</div>
      </div>

      <div class="info-wrap">
        <div class="panel">
          <h3>店舗基本情報</h3>
          <table class="info-table">
            <tr><th>所在地</th><td>〒101-0021<br>東京都千代田区外神田3-15-5 MNビル 3F</td></tr>
            <tr>
    <th>アクセス</th>
    <td><span class="clamp-3">
      秋葉原駅より秋葉原電気街口を御徒町方面に出て徒歩5分　毎日営業中
    </span></td>
  </tr>
            <tr><th>デュエルスペース</th><td>64席　無料で利用可能！！</td></tr>
            <tr><th>TEL</th><td>070-9160-3270</td></tr>
            <tr>
  <th>営業時間</th>
  <td>
    <div class="info-time">
      <div class="row"><span class="label">月～土</span><span class="time">11:00～20:00</span></div>
      <div class="row"><span class="label">日・祝</span><span class="time">11:00～19:00</span></div>
    </div>
  </td>
</tr>
<tr>
  <th>買取受付時間</th>
  <td>
    <div class="info-time">
      <div class="row"><span class="label">月～土</span><span class="time">11:00～19:00</span></div>
      <div class="row"><span class="label">日・祝</span><span class="time">11:00～18:00</span></div>
    </div>
  </td>
</tr>
</table>
        </div>
        <div class="panel">
          <h3>ご利用可能な決済</h3>
          <div class="pay-group">
            <b>クレジットカード</b>
            <div class="chips"><span class="chip">VISA</span><span class="chip">Master</span><span class="chip">JCB</span><span class="chip">AMEX</span><span class="chip">Diners</span><span class="chip">Discover</span></div>
          </div>
          <div class="pay-group">
            <b>電子マネー・スマホ決済</b>
            <div class="chips"><span class="chip">iD</span><span class="chip">QUICPay+</span><span class="chip">Kitaca</span><span class="chip">Suica</span><span class="chip">PASMO</span><span class="chip">TOICA</span><span class="chip">manaca</span><span class="chip">ICOCA</span><span class="chip">SUGOCA</span><span class="chip">nimoca</span><span class="chip">はやかけん</span></div>
          </div>
          <div class="pay-group">
            <b>コード決済</b>
            <div class="chips"><span class="chip">d払い</span><span class="chip">au PAY</span><span class="chip">メルペイ</span><span class="chip">楽天PAY</span></div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- EVENTS（スケジュールのみ） -->
  <section id="events" class="section">
    <div class="container">
      <h2>大会・イベント</h2>

      <p class="event-intro">
週のどの日でも、CLIMAXのデュエルスペースは大会が繰り広げられる舞台。
ここはただの対戦会場ではなく、“本気のデュエリスト”が集まる特別な場所です。
ひとりでも、仲間とでも、あなたの挑戦を待っています！
      </p>

      <div class="event-row">
        <div class="left">
          <img src="${EVENTS_PHOTO}" alt="デュエルスペースの様子">
        </div>
        <div class="right">
          <div class="event-schedule">
            <img src="${SCHEDULE_IMG}" alt="イベントスケジュール" loading="lazy">
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- STORE BUY（店頭買取） -->
  <section id="storebuy" class="section">
    <div class="container">
      <h2>店頭買取</h2>
      <p class="storebuy-note">
        店頭買取には
        <a class="myca-link" href="https://myca.cards/" target="_blank" rel="noopener">
          <strong>Mycalinks アプリのインストール</strong>
        </a>
        が必要です。以下のPOPを確認してください。
      </p>

      <div class="storebuy-wrap">
        <div class="storebuy-left">
          <img src="${POP_KAITORI_FLOW_IMG}" alt="店頭買取の流れ">
        </div>
        <div class="storebuy-right">
          <img src="${POP_MYCA_REGISTER_IMG}" alt="Mycalinks登録方法">
          <img src="${POP_STORE_DRAGON_IMG}" alt="店頭買取POP">
        </div>
      </div>
    </div>
  </section>

     <!-- BUY（郵送買取） -->
<section id="buy" class="section">
  <div class="container">
    <h2>郵送買取</h2>

    <p class="buy-note">
      郵送買取には
      <a class="myca-link" href="https://myca.cards/" target="_blank" rel="noopener">
        <strong>Mycalinks アプリのインストール</strong>
      </a>
      が必要です。手順や最新の買取価格は下記をご確認ください。
    </p>

    <!-- ★ この div を忘れずに！左右2カラムの親ラッパー -->
    <div class="buy-layout">
      <!-- 左：表（発送先住所の下に yusoudragon を1回だけ表示） -->
      <div class="buy-card" id="buyCard">
        <table class="info-table buy-table" style="margin-top:16px; border-collapse:separate; border-spacing:0 8px;">
          <tr><th>送料</th><td>基本お客様負担（最終買取金額 ¥10,000 以上で送料無料）</td></tr>
          <tr><th>対象</th><td>18歳以上（高校生可）</td></tr>
          <tr><th>お支払い</th><td>振込（手数料当社負担）</td></tr>
          <tr><th>申し込み</th><td>LINE（会員登録なし）</td></tr>
          <tr><th>発送</th><td>お近くのコンビニや郵便局から（追跡番号付き発送推奨）</td></tr>
          <tr><th>身分証明書</th><td>免許証・保険証・学生証・マイナンバーカードなど ※必ず現住所記載</td></tr>
          <tr>
            <th>発送先住所</th>
            <td>
              <div class="addr-grid">
                <span class="lead">〒101-0021&nbsp;</span>
                <span>東京都千代田区外神田3-15-5MNビル3階</span>
                <span class="shop">カードショップCLIMAX</span>
              </div>
            </td>
          </tr>
        </table>

        <!-- 発送先住所の“下”に yusoudragon（クリックで買取表） -->
        <div class="buy-cta addr-cta">
          ${BUY_CTA_HTML}  <!-- BUYLIST_URL(https://climaxcard.github.io/climax/default/)へ遷移 -->
        </div>
      </div>

      <!-- 右：郵送POP -->
        <div class="buy-right">
          ${MAIL_POP_HTML}
        </div>
      </div> <!-- /.buy-layout -->

      <!-- 注意事項（★グリッドの外★） -->
      <div class="buy-notes panel">
        <h3>注意事項</h3>
        <ul style="margin:0; padding-left:1.2em; line-height:1.6; color:#111;">
          <li>送料について：最終査定金額が1万円を超えた場合、当社で送料負担します（レターパックライト）。</li>
          <li>レアとノーマルが混在する場合は、あらかじめレアとノーマルを分けてから梱包・発送してください。<br>
              （※ノーマルに混在しているレアカードなどは一括でノーマルカード査定となる可能性があります。）</li>
          <li>一律のレアリティのカードは分けて送っていただけると査定完了まで早いです。</li>
          <li>デュエルマスターズのVR以上のカードは１枚10円。</li>
          <li>同タイトルの大量査定は減額対象となります。</li>
          <li>カード両面のキズ・スレなどは減額対象となります。</li>
          <li>破れ・書き込み・水濡れ・日焼け・大きな折れ・反り・縁のめくれ・ひどいキズがあるカードは個別にお値段をつけられない場合があります。</li>
          <li>海賊版やコピー品など正規品でないものは引き取りのみとなります。</li>
          <li>査定金額は状態や在庫状況により予告なく変更される場合があります。</li>
          <li>買取査定金額から発送費や発送手数料を差し引くことはありません。</li>
          <li>査定時にキズ確認のためファイルからカードを抜いたりスリーブを外します。返送時は元の状態に戻せません。</li>
          <li>タバコや香水などの匂いが染みついたカードは査定対象外となります。</li>
        </ul>
        <p style="margin-top:12px; font-size:.9rem; color:#666;">※2025年9月20日更新※</p>
      </div>
    </div>
  </section>
  <!-- DUEL -->
  <section id="duel" class="section">
    <div class="container">
      <h2>デュエルスペース</h2>
      <div class="duel-grid">
        <figure class="duel-image">
          <img src="${DUEL_IMG}" alt="デュエルスペース">
        </figure>

        <div class="duel-stack">
          <div class="duel-panel duel-panel--compact">
            <div class="duel-headline">FREE毎日開放</div>
            <p style="margin-top:10px;white-space:pre-line">
デュエルスペースはいつでも無料で使えて、毎週各種大会も開催しています！
腕試しや仲間増やしの場にもピッタリ！
            </p>
          </div>

          <div class="duel-panel duel-guide" id="duel-guide">
            <h3>ご利用案内</h3>
            <ul>
              <li>営業時間内いつでもご利用OK（混雑時は譲り合いをお願いします）</li>
              <li>飲食はフタ付きのみ可・ゴミは各自お持ち帰り</li>
              <li>大会開催日はスタッフの指示に従ってください</li>
            </ul>
          </div>
        </div>

      </div>
    </div>
  </section>

  <!-- ACCESS -->
  <section id="access" class="section">
    <div class="container">
      <h2>アクセス</h2>
      <p>${ADDRESS}</p>
      <div class="map-wrap">
        <iframe src="${MAP_EMBED_SRC}" width="100%" height="380" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
      </div>
    </div>
  </section>
</main>
<script>
  // ==== SPAタブ ====
  const sections = Array.from(document.querySelectorAll('.section'));
  const navlinks = Array.from(document.querySelectorAll('.navlink'));
  function show(id, push=true){
    sections.forEach(s=>s.classList.toggle('active', s.id===id));
    document.querySelectorAll('header .navlink').forEach(a => a.classList.toggle('nav-active', a.dataset.section===id));
    if(push) history.pushState({id}, '', '#'+id);
  }
  function hook(a){ a.addEventListener('click', e=>{ if(a.getAttribute('href')?.startsWith('#')) e.preventDefault(); const id=a.dataset.section; if(id) show(id); }); }
  navlinks.forEach(hook);
  window.addEventListener('popstate', e=> show((e.state&&e.state.id)||location.hash.replace('#','')||'home', false));
  show(location.hash.replace('#','')||'home', false);

  // ==== HOMEカルーセル（PC:矢印＆左右どこでもクリック / SP:スワイプ） + 右POP高さ同期 ====
(function(){
  const carousel = document.getElementById('carousel'); if(!carousel) return;
  const track = document.getElementById('track');
  const dotsWrap = document.getElementById('dots');
  const slides = Array.from(track.children);
  const dots = Array.from(dotsWrap.children);
  const side = document.getElementById('homeSide');
  const prev = document.getElementById('prev');
  const next = document.getElementById('next');
  const mqPC = window.matchMedia('(min-width:900px)');

  slides.forEach(s=> s.classList.add('fit'));
  // 画像のドラッグでブラウザ既定動作が出ないように
  slides.forEach(s=>{
    const img=s.querySelector('img');
    if(img){ img.setAttribute('draggable','false'); img.style.userSelect='none'; }
  });

  function slideHeight(idx){
    const s = slides[idx], img = s.querySelector('img'); if(!img) return 0;
    const w = carousel.clientWidth;
    if(img.naturalWidth===0) return 0;
    return Math.round(w * img.naturalHeight / img.naturalWidth);
  }
  function syncSide(h){
    if(!side) return;
    const cards = Array.from(side.querySelectorAll('.home-card'));
    const gap = parseFloat(getComputedStyle(side).gap)||16;
    if(window.matchMedia("(max-width:900px)").matches){
      cards.forEach(c=>c.style.height="auto"); return;
    }
    const each = Math.max(120, Math.floor((h - gap)/2));
    cards.forEach(c=>c.style.height = each+"px");
  }

  let i=0, timer=null;
  const DURATION = 500;
  function setActiveDot(){ dots.forEach((d,idx)=>d.classList.toggle('active',idx===i)); }
  function snap(noAnim=false){
    track.style.transition = noAnim ? 'none' : 'transform ' + DURATION + 'ms ease';
    track.style.transform = `translate3d(${(-100*i)}%,0,0)`;
    setActiveDot();
    const h = slideHeight(i);
    if(h>0){ slides[i].style.height=h+"px"; syncSide(h); }
  }
  function go(n, noAnim=false){ i = (n+slides.length)%slides.length; snap(noAnim); }

  function autoStart(){ stopAuto(); timer=setInterval(()=>go(i+1),7000); }
  function stopAuto(){ if(timer){ clearInterval(timer); timer=null; } }

  const goPrev = ()=>{ stopAuto(); go(i-1); autoStart(); };
  const goNext = ()=>{ stopAuto(); go(i+1); autoStart(); };

  // 矢印
  prev && prev.addEventListener('click', goPrev);
  next && next.addEventListener('click', goNext);
  // ドット
  dots.forEach((d,idx)=> d.addEventListener('click', ()=>{ stopAuto(); go(idx); autoStart(); }));

  // PC：カルーセルの左右どこをクリックしても前後
  carousel.addEventListener('click', (e)=>{
    // 矢印/ドット/リンクをクリックした時は無視
    if(e.target.closest('.ctrl,.dots,.dot,a,button')) return;
    const r = carousel.getBoundingClientRect();
    (e.clientX - r.left < r.width/2) ? goPrev() : goNext();
  });

  // スワイプ（iOS/Android/Safariも拾える実装）
  let startX=0, startY=0, isDown=false, deltaX=0, width=0, axis=null;
  const THRESHOLD_PX = 25;  // これ超えたらページ送り
  const LOCK_PX = 8;        // 軸判定の閾値

  const onDown = (x,y)=>{
    isDown = true; axis=null; deltaX=0;
    width = carousel.clientWidth||1;
    startX = x; startY = y;
    stopAuto();
    track.style.transition = 'none';
  };
  const onMove = (x,y,ev)=>{
    if(!isDown) return;
    const dx = x - startX, dy = y - startY;
    if(axis===null && (Math.abs(dx) > LOCK_PX || Math.abs(dy) > LOCK_PX)){
      axis = Math.abs(dx) > Math.abs(dy) ? 'x' : 'y';
    }
    if(axis==='x'){
      // 横スクロールを優先するためSPでは既定動作を止める
      if(ev && ev.cancelable) ev.preventDefault();
      deltaX = dx;
      const pct = (deltaX/width)*100;
      track.style.transform = `translate3d(${(-100*i + pct)}%,0,0)`;
    }
  };
  const onUp = ()=>{
    if(!isDown) return;
    isDown = false;
    if(axis==='x' && Math.abs(deltaX) > THRESHOLD_PX){
      (deltaX < 0) ? go(i+1) : go(i-1);
    }else{
      snap(); // 元に戻す
    }
    autoStart();
  };

  // マウス
  track.addEventListener('mousedown', (e)=>onDown(e.clientX, e.clientY));
  window.addEventListener('mousemove', (e)=>onMove(e.clientX, e.clientY, e));
  window.addEventListener('mouseup', onUp);

  // タッチ
  track.addEventListener('touchstart', (e)=>{
    const t=e.touches[0]; onDown(t.clientX, t.clientY);
  }, {passive:true});
  window.addEventListener('touchmove', (e)=>{
    const t=e.touches[0]; if(t) onMove(t.clientX, t.clientY, e);
  }, {passive:false}); // ← preventDefaultできるように
  window.addEventListener('touchend', onUp, {passive:true});
  window.addEventListener('touchcancel', onUp, {passive:true});

  // キーボード（PC）
  document.addEventListener('keydown', (e)=>{
    if(!mqPC.matches) return;
    if(e.key === 'ArrowLeft')  goPrev();
    if(e.key === 'ArrowRight') goNext();
  });

  function adjustAll(){ const h=slideHeight(i); if(h>0){ slides[i].style.height=h+"px"; syncSide(h); } }
  slides.forEach((s,idx)=>{
    const img=s.querySelector('img'); if(!img) return;
    if(img.complete){ if(idx===0) adjustAll(); }
    else img.addEventListener('load', ()=>{ if(idx===0) adjustAll(); }, {once:true});
  });
  window.addEventListener('resize', adjustAll);

  go(0, true);
  autoStart();
})();  

/* ===== Duel 高さ同期（左画像の高さ＝右2パネル合計） ===== */
(function(){
  const mq = window.matchMedia('(min-width:900px)');
  const root = document.getElementById('duel');
  if(!root) return;

  const frame = root.querySelector('.duel-image');
  const img   = frame && frame.querySelector('img');
  const stack = root.querySelector('.duel-stack');
  const topP  = root.querySelector('.duel-panel.duel-panel--compact');
  const panels= root.querySelectorAll('.duel-stack .duel-panel');
  const botP  = panels.length >= 2 ? panels[1] : null;

  function stackGap(){
    if(!stack) return 10;
    const g = parseFloat(getComputedStyle(stack).gap || '10');
    return isNaN(g) ? 10 : g;
  }
  function clamp(n, min){ return n < min ? min : n; }

  function sync(){
    if(!(mq.matches && frame && img && stack && topP && botP)){
      if(topP) topP.style.height = '';
      if(botP) botP.style.height = '';
      if(stack) stack.style.height = '';
      return;
    }
    // 左の画像の「想定高さ」をアスペクト比から算出（表示幅 × 画像比）
    const w  = frame.getBoundingClientRect().width;
    const nw = img.naturalWidth, nh = img.naturalHeight;
    if(!nw || !nh || w < 10) return;

    const leftH = Math.round(w * nh / nw);   // 左の枠と画像がcontainなのでこれが見た目高さ
    const total = leftH;                     // 右2パネル合計をこれに合わせる
    const gap   = stackGap();

    // 上下の配分比（お好みで 0.40〜0.50 を微調整）
    const split = 0.45;
    let topH = Math.round(total * split);
    let botH = total - gap - topH;

    // 最低高でつぶれ防止
    topH = clamp(topH, 84);
    botH = clamp(botH, 84);

    // 誤差吸収（合計＝total に厳密一致）
    const diff = topH + gap + botH - total;
    if(diff > 0) botH -= diff;
    else if(diff < 0) botH -= diff;

    stack.style.height = total + 'px';
    topP.style.height  = topH  + 'px';
    botP.style.height  = botH  + 'px';
  }

  function ready(fn){
    if(img && img.complete && img.naturalWidth) fn();
    else img && img.addEventListener('load', fn, {once:true});
  }

  ready(sync);
  window.addEventListener('resize', sync);
  document.addEventListener('visibilitychange', ()=>{ if(!document.hidden) sync(); });
  window.addEventListener('hashchange', sync);
  // 初期のレイアウト揺れ対策で数回だけ再同期
  setTimeout(sync, 50);
  setTimeout(sync, 250);
  setTimeout(sync, 800);
})();
/* === SP時だけ yusoudragon を mail_buy と 注意事項の間に移動、PCに戻ったら元へ === */
(function(){
  const mq = window.matchMedia('(max-width: 900px)');
  const buy = document.getElementById('buy');
  if(!buy) return;

  const card  = buy.querySelector('.buy-card');
  const cta   = card && card.querySelector('.buy-cta');
  const right = buy.querySelector('.buy-right');
  const notes = buy.querySelector('.buy-notes');
  if(!(card && cta && right && notes)) return;

  const originalParent = cta.parentNode;

  function apply(){
    if(mq.matches){
      if(cta.parentNode !== buy){
        buy.insertBefore(cta, notes);
      }
    }else{
      if(cta.parentNode !== originalParent){
        originalParent.appendChild(cta);
      }
    }
  }

  apply();
  mq.addEventListener ? mq.addEventListener('change', apply) : window.addEventListener('resize', apply);
})();
</script>
</body>
</html>

""")

MYCA_HTML = Template(r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>買取受付｜Mycalinks アプリのご案内 - ${STORE_NAME}</title>
<meta name="theme-color" content="#ffffff" />
<style>
  :root{ --brand:#dc2626; --ink:#111; }
  body{ margin:0; font-family:system-ui,-apple-system,Segoe UI,Roboto,'Noto Sans JP',sans-serif; color:#111; background:#fff; }
  .container{ max-width:960px; margin:auto; padding:24px 16px; }
  a.btn{ display:inline-block; padding:10px 14px; border-radius:12px; background:#111; color:#fff; text-decoration:none; font-weight:900; }
  .pop{ width:100%; height:auto; border:1px solid #eee; border-radius:12px; box-shadow:0 6px 16px rgba(0,0,0,.08); }
  header{ border-bottom:1px solid #eee; padding:12px 16px; }
/* BUYページの注意書き（文言） */
.buy-note .myca-link, .buy-note .myca-link:visited{
  color:#dc2626; font-weight:900; text-decoration:underline; text-decoration-color:rgba(220,38,38,.95);
  text-decoration-thickness:2px; text-underline-offset:3px;
}
.buy-note .myca-link:hover{ background:rgba(220,38,38,.10); border-radius:6px; padding:0 4px; }
.buy-note .myca-link:focus-visible{ outline:2px solid #dc2626; outline-offset:2px; }
</style>
</head>
<body>
<header>
  <div class="container"><a href="index.html">← トップへ戻る</a></div>
</header>
<div class="container">
  <h1>買取受付には <span style="color:#111">Mycalinks</span> アプリのインストールが必要です</h1>
  <p>かんたん登録！以下のPOPをご確認ください。</p>
  <img class="pop" src="${POP_MYCALINKS_IMG}" alt="Mycalinks案内POP">
  <p style="margin-top:16px"><a class="btn" href="${BUYLIST_URL}" target="_blank">買取表を見る</a></p>
</div>
</body>
</html>
""")

# ===== 書き込み =====
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "index.html").write_text(
    INDEX_HTML.safe_substitute(
        STORE_NAME=STORE_NAME, ADDRESS=ADDRESS,
        SHOP_URL=SHOP_URL, BUYLIST_URL=BUYLIST_URL, X_URL=X_URL,
        LOGO_IMG=LOGO_IMG, X_ICON_HTML=X_ICON_HTML,
        SCHEDULE_IMG=SCHEDULE_IMG, POP_TOREKA_IMG=POP_TOREKA_IMG,
        POP_MYCALINKS_IMG=POP_MYCALINKS_IMG, DUEL_IMG=DUEL_IMG,
        SLIDES_HTML=SLIDES_HTML, DOTS_HTML=DOTS_HTML,
        TITLES_HTML=TITLES_HTML, MAP_EMBED_SRC=MAP_EMBED_SRC,
        POP_KAITORI_FLOW_IMG=POP_KAITORI_FLOW_IMG, POP_MYCA_REGISTER_IMG=POP_MYCA_REGISTER_IMG,
        POP_STORE_DRAGON_IMG=POP_STORE_DRAGON_IMG, MAIL_POP_IMG=MAIL_POP_IMG,
        EVENTS_PHOTO=EVENTS_PHOTO,MAIL_POP_HTML=MAIL_POP_HTML,BUY_CTA_HTML=BUY_CTA_HTML,LINE_ICON_HTML=LINE_ICON_HTML,
    ),
    encoding="utf-8"
)

(OUT / "mycalinks.html").write_text(
    MYCA_HTML.substitute(
        STORE_NAME=STORE_NAME,
        BUYLIST_URL=BUYLIST_URL,
        POP_MYCALINKS_IMG=POP_MYCALINKS_IMG
    ),
    encoding="utf-8"
)

print("[OK] 出力:", (OUT / "index.html").resolve())
print("必要画像: ", ", ".join([
    LOGO_IMG, DUEL_IMG, SCHEDULE_IMG, POP_TOREKA_IMG, POP_MYCALINKS_IMG,
    POP_KAITORI_FLOW_IMG, POP_MYCA_REGISTER_IMG, POP_STORE_DRAGON_IMG, EVENTS_PHOTO
]), "+ slide1/slide2/slide3.*（任意）")
print("※ タイトル画像は同フォルダに置けば自動検出。デュエマは少し大きめで表示します。")
