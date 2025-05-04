import json
import re

def sanitize(id_str: str) -> str:
    # Заменяем любые не-алфавитно-цифровые символы на '_'
    return re.sub(r'[^0-9A-Za-z_]', '_', id_str)

# Загружаем JSON
with open("diagram.json", encoding="utf-8") as f:
    data = json.load(f)

# Начинаем диаграмму
print("graph LR\n")

# Контейнеры (модули)
for c in data["containers"]:
    nid = sanitize(c["id"])
    label = c["name"]
    print(f'{nid}["{label}"]')

# Компоненты (функции/классы)
for comp in data["components"]:
    cid = sanitize(comp["id"])
    clabel = comp["name"]
    pid = sanitize(comp["containerId"])
    print(f'{cid}["{clabel}"]')
    # связь «содержит»
    print(f'{pid} --> {cid}')

# Связи (import и call)
for rel in data["relationships"]:
    if rel["description"] == "содержит":
        continue
    src = sanitize(rel["source"])
    dst = sanitize(rel["destination"])
    desc = rel["description"].replace('"', '')  # убираем лишние кавычки
    # Вот правильный синтаксис стрелки с подписью:
    print(f'{src} -->|{desc}| {dst}')
