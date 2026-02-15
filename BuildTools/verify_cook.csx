using UAssetAPI;
using UAssetAPI.ExportTypes;
using UAssetAPI.Kismet.Bytecode;
using UAssetAPI.Kismet.Bytecode.Expressions;

var asset = new UAsset(@"C:\IcarusTVMod\IcarusTVMod\Saved\Cooked\WindowsNoEditor\IcarusTVMod\Content\Mods\TV\Blueprints\BP_TV.uasset", EngineVersion.VER_UE4_27);
foreach (var exp in asset.Exports)
{
    if (exp is FunctionExport fe)
    {
        Console.WriteLine($"{fe.ObjectName}: size={fe.ScriptBytecodeSize}");
        if (fe.ScriptBytecode != null)
            foreach (var inst in fe.ScriptBytecode)
            {
                Console.Write($"  {inst.Token}");
                if (inst is EX_FinalFunction ff) Console.Write($" -> {ff.StackNode.Index}");
                if (inst is EX_CallMath cm) Console.Write($" -> {cm.StackNode.Index}");
                if (inst is EX_LocalFinalFunction lf) 
                {
                    Console.Write($" -> export {lf.StackNode.Index}");
                    if (lf.Parameters?.Length > 0 && lf.Parameters[0] is EX_IntConst ic)
                        Console.Write($" entry={ic.Value}");
                }
                if (inst is EX_StringConst sc) Console.Write($" \"{sc.Value}\"");
                Console.WriteLine();
            }
    }
}
