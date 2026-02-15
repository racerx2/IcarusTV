import json

path = r'D:\Program Files (x86)\Icarus_Mod_Manager_2_2_6\data\Traits\D_Interactable.json'
with open(path, 'r') as f:
    data = json.load(f)

rows = data.get('Rows', data)
if isinstance(rows, list):
    row_dict = {r.get('Name',''): r for r in rows}
else:
    row_dict = rows

targets = ['Deployable', 'Deployable_Power_Toggle_Only', 'Deployable_No_Power_Toggle', 
           'Slotable_Deployable', 'Slotable_Deployable_Electric', 'Lights_Fire_Base',
           'Deployable_NoInteract', 'Deployable_Generator']

for name in targets:
    if name in row_dict:
        print(f"\n{'='*60}")
        print(f"  {name}")
        print(f"{'='*60}")
        print(json.dumps(row_dict[name], indent=2))
    else:
        print(f"\n  {name}: NOT FOUND")

print(f"\n\n=== ALL ROW NAMES ({len(row_dict)}) ===")
for k in sorted(row_dict.keys()):
    print(f"  {k}")
