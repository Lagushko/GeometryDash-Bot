from database import userDB

# правильные ID
id1 = 1374624035693920318
id2 = 739123605538996285

# --- 1 ---
userDB.update_field(id1, "last_reward_time", [0, 0])

# --- 2 ---
data = userDB.get(id2)
creations = data.get("creations", [])
creations = [int(x) for x in creations]

userDB.update_field(id2, "creations", creations)

print("✅ Done")