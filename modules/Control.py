from modules import *
from bot import bot

async def update_db(ctx, table: str, field: str, default: str, type: str):
    if ctx.author.id not in Config.OWNER:
        return
    
    if table not in ["users", "levels"]:
        await ctx.send("❌ Invalid table name. Use `users` or `levels`.")
        return

    db_path = "data/users.db" if table == "users" else "data/levels.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    existing_columns = [col[1] for col in cursor.fetchall()]

    if field in existing_columns:
        await ctx.send(f"⚠️ Field `{field}` already exists in the `{table}` table.")
    else:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {field} {type} DEFAULT {default}")
        conn.commit()
        await ctx.send(
            f"✅ Field `{field}` has been successfully added to the `{table}` table!\n"
            f"📦 Type: `{type}` | 🧩 Default: `{default}`"
        )

    conn.close()

async def set_db(ctx, table: str, field: str, *, value: str):
    if ctx.author.id not in Config.OWNER:
        return

    if table not in ["users", "levels"]:
        await ctx.send("❌ Invalid table name. Use `users` or `levels`.")
        return

    db_path = "data/users.db" if table == "users" else "data/levels.db"

    try:
        parsed_value = ast.literal_eval(value)
    except:
        parsed_value = value

    if isinstance(parsed_value, (list, dict)):
        stored_value = json.dumps(parsed_value)
    else:
        stored_value = parsed_value

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(f"PRAGMA table_info({table})")
        existing_columns = [col[1] for col in cursor.fetchall()]
        if field not in existing_columns:
            await ctx.send(f"❌ Field `{field}` does not exist in `{table}`.")
            return

        cursor.execute(f"UPDATE {table} SET {field} = ?", (stored_value,))
        conn.commit()

        await ctx.send(
            f"✅ Field `{field}` in `{table}` has been updated for all rows.\n"
            f"📦 New value: `{value}` (type: `{type(parsed_value).__name__}`)"
        )
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")
    finally:
        conn.close()

async def role(ctx, role_name: str, action: str, user_id: int):
    if ctx.author.id not in (Config.OWNER):
        return

    valid_roles = ["admin", "moderator", "helper"]
    valid_actions = ["add", "remove"]

    if role_name not in valid_roles:
        await ctx.send(f"❌ Invalid role. Available roles are: {', '.join(valid_roles)}")
        return

    if action not in valid_actions:
        await ctx.send(f"❌ Invalid action. Available actions are: {', '.join(valid_actions)}")
        return

    if not isinstance(user_id, int):
        await ctx.send("❌ Invalid User ID. Please provide a numeric User ID.")
        return

    settings_key = f"{role_name}s"

    current_ids = botDB.get(settings_key) or []

    if action == "add":
        if user_id not in current_ids:
            current_ids.append(user_id)
            botDB.update_field(settings_key, current_ids)
            await ctx.send(f"✅ User with ID {user_id} has been added to {role_name}s.")
        else:
            await ctx.send(f"ℹ️ User with ID {user_id} is already in {role_name}s.")
    elif action == "remove":
        if user_id in current_ids:
            current_ids.remove(user_id)
            botDB.update_field(settings_key, current_ids)
            await ctx.send(f"✅ User with ID {user_id} has been removed from {role_name}s.")
        else:
            await ctx.send(f"ℹ️ User with ID {user_id} is not in {role_name}s.")

async def data(ctx, name: str, default: str, data_type: str):
    if ctx.author.id not in Config.OWNER:
        return

    valid_types = ["str", "int", "float", "list", "dict"]

    if data_type not in valid_types:
        await ctx.send(f"❌ Invalid data type. Available types are: {', '.join(valid_types)}")
        return

    try:
        if data_type == "int":
            processed_default = int(default)
        elif data_type == "float":
            processed_default = float(default)
        elif data_type == "list":
            processed_default = json.loads(default)
            if not isinstance(processed_default, list):
                raise ValueError("Must be a list")
        elif data_type == "dict":
            processed_default = json.loads(default)
            if not isinstance(processed_default, dict):
                raise ValueError("Must be a dict")
        else:
            processed_default = default
    except Exception as e:
        await ctx.send(f"❌ Error parsing default value: {e}")
        return

    if botDB.get(name) is None:
        botDB.add(name, processed_default)
        await ctx.send(f"✅ Field `{name}` with value `{processed_default}` (type: {data_type}) added.")
    else:
        await ctx.send(f"ℹ️ Field `{name}` already exists.")
