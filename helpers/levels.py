from database import *

result = []

loads = "0"
likes = "0"
author = "736932516891590666"

def smart_input(prompt, fields):
    while True:
        val = input(f"{prompt}: ").strip()
        if val.startswith("/"):
            parts = val[1:].split(maxsplit=1)
            if len(parts) == 1:
                key = parts[0].capitalize()
                if key in fields:
                    fields[key] = input(f"{key} (edit): ")
                else:
                    print("❌ Unknown field.")
            elif len(parts) == 2:
                key = parts[0].capitalize()
                if key in fields:
                    fields[key] = parts[1]
                else:
                    print("❌ Unknown field.")
            continue
        return val

answer = None
while answer != "0":
    fields = {
        "ID": "",
        "Name": "",
        "Difficulty": "",
        "Length": "",
        "Coins": ""
    }

    fields["ID"] = smart_input("ID", fields)
    fields["Name"] = smart_input("Name", fields).replace(" ", "-")
    fields["Difficulty"] = smart_input("Difficulty", fields)
    fields["Length"] = smart_input("Length", fields)
    fields["Coins"] = smart_input("Coins", fields)

    args = [
        fields["ID"],
        fields["Name"],
        fields["Difficulty"],
        loads,
        likes,
        fields["Length"],
        fields["Coins"],
        author
    ]
    result.append(args)

    answer = input("- ")

print("\nGenerated commands:")
for cmd in result:
    print("!add-level", *cmd)

confirm = input("\nAdd these levels to the database? (y/n): ").lower()
if confirm == "y":
    for level in result:
        level_id, name, difficulty, downloads, likes, time, coins, sender = level
        name = name.replace("-", " ")

        levelDB.add(level_id, name, difficulty, downloads, likes, time, coins, sender)

        data = userDB.get(sender)
        if data:
            current_cp = data["creatorpoints"]
            creations = data["creations"]
            creations.append(int(level_id))
            userDB.update_field(sender, "creatorpoints", current_cp + 1)
            userDB.update_field(sender, "creations", creations)

    print(f"\n✅ {len(result)} levels added to the database.")
else:
    print("\n❌ Operation cancelled.")
