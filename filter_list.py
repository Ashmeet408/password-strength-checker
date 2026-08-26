with open("xato-100k.txt") as src, open("filtered.txt", "w") as dst:
    for line in src:
        cleaned = line.strip()
        if len(cleaned) >= 15:
            dst.write(cleaned + "\n")
