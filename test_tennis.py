"""Run: python test_tennis.py"""
import random
from tennis import H, W, new_game, step

s = new_game(); s.update(x=1, y=3, dx=-1, dy=0, me=3)
s = step(s, "hold", "a"); assert (s["x"], s["dx"], s["rally"]) == (0, 1, 1), "player returns the ball"
s = new_game(); s.update(x=1, y=6, dx=-1, dy=0, me=1)
s = step(s, "hold", "a"); assert s["score"] == [0, 1] and s["x"] == 9 and s["dx"] == -1, "miss gives the bot a point and the serve"
s = new_game(); s.update(x=5, y=0, dx=1, dy=-1)
s = step(s, "hold", "a"); assert (s["y"], s["dy"]) == (1, 1), "wall bounce"
s = new_game(); s["score"] = [0, 4]; s.update(x=1, y=6, dx=-1, dy=0, me=1)
s = step(s, "hold", "a"); assert s["wins"] == [0, 1] and s["score"] == [0, 0], "game over resets, tallies kept"
random.seed(1); s = new_game()
for _ in range(20000):
    s = step(s, random.choice(["up", "hold", "down"]), "r")
    assert 1 <= s["me"] <= H - 2 and 1 <= s["bot"] <= H - 2 and 0 <= s["x"] < W and 0 <= s["y"] < H, s
assert sum(s["wins"]) > 0, "games finish"
print("ok", s["wins"])
