with open(r"C:\Users\shankar mishra\openhinglish\src\openhinglish\data\gazetteers\brands.tsv", encoding="utf-8") as f:
    lines = f.readlines()

before = len(lines)
lines = [l for l in lines if not l.startswith("hero\t")]
after = len(lines)
print(f"Removed {before - after} line(s)")

with open(r"C:\Users\shankar mishra\openhinglish\src\openhinglish\data\gazetteers\brands.tsv", "w", encoding="utf-8", newline="") as f:
    f.writelines(lines)
