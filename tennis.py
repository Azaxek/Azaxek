"""Turn-based tennis for a GitHub profile README: the internet vs a bot. Run by the workflow on each move."""
import json, os, random, re
from pathlib import Path

W, H, WIN = 11, 7, 5          # court size, points to win a game
BOT_SKILL = 0.6                # chance the bot steps toward the ball each turn; lower = easier
ROOT = Path(__file__).parent
STATE, README = ROOT / "state.json", ROOT / "README.md"
REPO = os.environ.get("GITHUB_REPOSITORY", "Azaxek/Azaxek")
MOVES = {"up": -1, "hold": 0, "down": 1}
clamp = lambda r: max(1, min(H - 2, r))  # a racket is 3 rows tall, centred on r

def serve(s, server):
    if server == "me":
        s.update(x=1, y=s["me"], dx=1, dy=0)
    else:
        s.update(x=W - 2, y=s["bot"], dx=-1, dy=0)
    s["rally"] = 0

def new_game(prev=None, msg="New game. Make a move!"):
    s = {"me": 3, "bot": 3, "score": [0, 0], "rally": 0, "msg": msg,
         "best": 0, "best_by": "nobody yet", "wins": [0, 0]}
    for k in ("best", "best_by", "wins"):
        if prev:
            s[k] = prev[k]
    serve(s, "me")
    return s

def step(s, cmd, actor):
    if cmd == "new":
        return new_game(s)
    s["me"] = clamp(s["me"] + MOVES[cmd])
    x, y, dy = s["x"] + s["dx"], s["y"] + s["dy"], s["dy"]
    if not 0 <= y < H:  # bounce off the side walls
        dy = -dy
        y += 2 * dy
    s.update(x=x, y=y, dy=dy, msg=f"{actor} moved {cmd}.")
    side = "me" if x == 0 else "bot" if x == W - 1 else None
    if side:
        if abs(y - s[side]) <= 1:  # return: the hit angle depends on where the ball meets the racket
            s["dx"] = -s["dx"]
            s["dy"] = (y - s[side]) or (random.choice((-1, 1)) if side == "bot" else 0)
            s["rally"] += 1
            if s["rally"] > s["best"]:
                s["best"], s["best_by"] = s["rally"], actor
        else:  # missed: the other side scores
            w = 1 if side == "me" else 0
            s["score"][w] += 1
            who = "The bot" if w else "The internet"
            if s["score"][w] == WIN:
                s["wins"][w] += 1
                return new_game(s, f"🏆 {who} won the game! New game.")
            serve(s, "bot" if w else "me")
            s["msg"] = f"{who} won the point. {actor} made the last move."
            return s
    if random.random() < BOT_SKILL:
        s["bot"] = clamp(s["bot"] + (y > s["bot"]) - (y < s["bot"]))
    return s

def render(s):
    owner, name = REPO.split("/")
    link = lambda label, c: (f"[{label}](https://github.com/{REPO}/issues/new?title=tennis:+{c}"
                             "&body=Just+press+%22Submit+new+issue%22.+The+board+updates+in+about+a+minute.)")
    rows = ["".join("🎾" if (x, y) == (s["x"], s["y"]) else "🟦" if x == 0 and abs(y - s["me"]) <= 1
                    else "🟥" if x == W - 1 and abs(y - s["bot"]) <= 1 else "⬛" for x in range(W)) for y in range(H)]
    return "\n".join([
        "<pre>" + "\n".join(rows) + "</pre>", "",
        f"**🟦 The Internet {s['score'][0]} – {s['score'][1]} The Bot 🟥** (first to {WIN})", "",
        f"Rally: {s['rally']} · Best rally: {s['best']} by {s['best_by']} · All-time wins: Internet {s['wins'][0]}, Bot {s['wins'][1]}", "",
        f"_{s['msg']}_", "",
        "|  | " + link("⬆️ Move up", "up") + " |  |", "|---|---|---|",
        "|  | " + link("⏺ Stay", "hold") + " |  |",
        "|  | " + link("⬇️ Move down", "down") + " |  |", "",
        f"**[▶ Or play instantly on your own](https://{owner.lower()}.github.io/{name}/play.html)** · [🔄 New match]" +
        f"(https://github.com/{REPO}/issues/new?title=tennis:+new&body=Just+press+%22Submit+new+issue%22.)",
    ])

def main():
    s = json.loads(STATE.read_text()) if STATE.exists() else new_game()
    m = re.fullmatch(r"tennis:\s*(up|hold|down|new)", os.environ.get("TITLE", "").strip().lower())
    if m:
        actor = os.environ.get("ACTOR", "")
        actor = actor if re.fullmatch(r"[A-Za-z0-9-]{1,39}", actor) else "someone"
        s = step(s, m.group(1), actor)
    STATE.write_text(json.dumps(s))
    text = README.read_text(encoding="utf-8")
    README.write_text(re.sub(r"(<!--GAME-->).*?(<!--/GAME-->)", lambda k: f"{k[1]}\n{render(s)}\n{k[2]}", text, flags=re.S), encoding="utf-8")

if __name__ == "__main__":
    main()
