import re
import sys

with open('images/er_diagram.svg', 'r', encoding='utf-8') as f:
    svg = f.read()

paths = re.findall(r'd="([^"]+)"', svg)
lines = re.findall(r'<line x1="([^"]+)" y1="([^"]+)" x2="([^"]+)" y2="([^"]+)"', svg)
texts = re.findall(r'<text x="([^"]+)" y="([^"]+)"[^>]*class="card-lbl">([^<]+)</text>', svg)

print(f"Total paths: {len(paths)}, lines: {len(lines)}, labels: {len(texts)}")

segments = []
for x1, y1, x2, y2 in lines:
    segments.append(((float(x1), float(y1)), (float(x2), float(y2))))

for p in paths:
    pts = []
    tokens = p.split()
    i = 0
    while i < len(tokens):
        if tokens[i] in ['M', 'L']:
            pts.append((float(tokens[i+1]), float(tokens[i+2])))
            i += 3
        else:
            i += 1
    for k in range(len(pts)-1):
        segments.append((pts[k], pts[k+1]))

conflicts = []
for tx, ty, txt in texts:
    tx, ty = float(tx), float(ty)
    # text is text-anchor: middle, width ~ 20, height ~ 10, y is baseline (so y-10 to y+2)
    bx1, bx2 = tx - 12, tx + 12
    by1, by2 = ty - 10, ty + 2
    for (x1, y1), (x2, y2) in segments:
        # vertical segment:
        if abs(x1 - x2) < 0.1:
            vx = x1
            vy_min, vy_max = min(y1, y2), max(y1, y2)
            if bx1 <= vx <= bx2 and not (vy_max < by1 or vy_min > by2):
                conflicts.append((txt, (tx, ty), 'vertical segment at x=' + str(vx), (vy_min, vy_max)))
        # horizontal segment:
        elif abs(y1 - y2) < 0.1:
            hy = y1
            hx_min, hx_max = min(x1, x2), max(x1, x2)
            if by1 <= hy <= by2 and not (hx_max < bx1 or hx_min > bx2):
                conflicts.append((txt, (tx, ty), 'horizontal segment at y=' + str(hy), (hx_min, hx_max)))

print(f"Detected conflicts: {len(conflicts)}")
for c in conflicts:
    print("  CONFLICT:", c)
