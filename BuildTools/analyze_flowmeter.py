import json

with open(r'C:\IcarusGameDump\Exports\Icarus\Content\BP\Objects\World\Items\Deployables\Networks\BP_FlowMeter.json', 'r', encoding='utf-8', errors='replace') as f:
    data = json.loads(f.read(), strict=False)

def find_stack_nodes(obj, path=""):
    """Find all StackNode references in the JSON"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'StackNode':
                print(f'{path}.{k}: {json.dumps(v)[:200]}')
            elif k in ('FunctionName', 'PropertyName') and v:
                print(f'{path}.{k}: {v}')
            else:
                find_stack_nodes(v, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            find_stack_nodes(item, f'{path}[{i}]')

# Look at the UberGraph bytecode raw 
for item in data:
    name = item.get('Name', '')
    if name == 'ExecuteUbergraph_BP_FlowMeter':
        print("=== UberGraph StackNodes & FunctionNames ===")
        bytecode = item.get('ScriptBytecode', [])
        find_stack_nodes(bytecode, 'UG')
        break
