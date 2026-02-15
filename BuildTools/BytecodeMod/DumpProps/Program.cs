using UAssetAPI;
using UAssetAPI.ExportTypes;
using UAssetAPI.UnrealTypes;
using UAssetAPI.Kismet.Bytecode;
using UAssetAPI.Kismet.Bytecode.Expressions;

var asset = new UAsset(@"C:\IcarusTVMod\PakStaging\Icarus\Content\Mods\TV\Blueprints\BP_TV.uasset", EngineVersion.VER_UE4_27);

// Dump raw bytecode hex for the thin wrapper functions
foreach (int idx in new[] { 1, 2, 3 }) // OnDeviceTurnedOff, OnDeviceTurnedOn, ReceiveBeginPlay
{
    var fn = (FunctionExport)asset.Exports[idx];
    Console.WriteLine($"=== [{idx+1}] {fn.ObjectName} ===");
    
    // Get the EX_LocalFinalFunction call and its parameters
    if (fn.ScriptBytecode != null)
    {
        foreach (var expr in fn.ScriptBytecode)
        {
            if (expr is EX_LocalFinalFunction lff)
            {
                Console.WriteLine($"  Calls: PI({lff.StackNode})");
                Console.WriteLine($"  Params: {lff.Parameters?.Length ?? 0}");
                if (lff.Parameters != null)
                {
                    foreach (var p in lff.Parameters)
                    {
                        Console.WriteLine($"    {p.GetType().Name}: {p}");
                        if (p is EX_IntConst ic) Console.WriteLine($"    EntryPoint = {ic.Value}");
                    }
                }
            }
        }
    }
    Console.WriteLine();
}

// Now dump full Ubergraph with nested expressions
Console.WriteLine("=== [1] ExecuteUbergraph_BP_TV (FULL) ===");
var uber = (FunctionExport)asset.Exports[0];
if (uber.ScriptBytecode != null)
{
    foreach (var expr in uber.ScriptBytecode)
        DumpRecursive(expr, 0, asset);
}

void DumpRecursive(KismetExpression expr, int depth, UAsset a)
{
    string pad = new string(' ', depth * 2);
    string info = expr.GetType().Name;
    
    if (expr is EX_LocalFinalFunction lff) info += $" PI({lff.StackNode})";
    if (expr is EX_FinalFunction ff) info += $" PI({ff.StackNode})";
    if (expr is EX_VirtualFunction vf) info += $" '{vf.VirtualFunctionName}'";
    if (expr is EX_LocalVirtualFunction lvf) info += $" '{lvf.VirtualFunctionName}'";
    if (expr is EX_Jump j) info += $" →{j.CodeOffset}";
    if (expr is EX_JumpIfNot jin) info += $" →{jin.CodeOffset}";
    if (expr is EX_ComputedJump) info += " (computed)";
    if (expr is EX_IntConst ic) info += $" ={ic.Value}";
    if (expr is EX_InstanceVariable iv) info += $" '{iv.Variable}'";
    if (expr is EX_LocalVariable lv) info += $" '{lv.Variable}'";
    if (expr is EX_Context ctx) 
    {
        info += " {";
        Console.WriteLine($"{pad}{info}");
        DumpRecursive(ctx.ObjectExpression, depth+1, a);
        Console.Write($"{pad}  ."); 
        DumpRecursive(ctx.ContextExpression, depth+1, a);
        Console.WriteLine($"{pad}}}");
        return;
    }
    if (expr is EX_LetBool lb)
    {
        info += " (LetBool)";
    }
    
    Console.WriteLine($"{pad}{info}");
}
