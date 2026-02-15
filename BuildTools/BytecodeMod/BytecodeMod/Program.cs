using System;
using System.IO;
using System.Linq;
using UAssetAPI;
using UAssetAPI.UnrealTypes;

string assetPath = @"C:\TVModBuilder\PakContent\Icarus\Content\Mods\TV\Blueprints\BP_TV.uasset";

var asset = new UAsset(assetPath, EngineVersion.VER_UE4_27);

Console.WriteLine("=== BP_TV Super Fix Tool ===\n");

// Functions that need their outer redirected from PowerToggleableBase to DeployableBase
string[] functionsToFix = { "Deployable_Interact", "GetWidgetClass" };

Console.WriteLine("=== Imports Before Fix ===");
for (int i = 0; i < asset.Imports.Count; i++)
{
    var imp = asset.Imports[i];
    Console.WriteLine($"  Import[{i}] = {imp.ObjectName} (Class: {imp.ClassName}, Outer: {imp.OuterIndex})");
}

// Find key imports
int powerToggleableClassIdx = -1;
int deployableBaseClassIdx = -1;

for (int i = 0; i < asset.Imports.Count; i++)
{
    string name = asset.Imports[i].ObjectName.ToString();
    if (name == "BP_Deployable_PowerToggleableBase_C") powerToggleableClassIdx = i;
    if (name == "BP_DeployableBase_C") deployableBaseClassIdx = i;
}

Console.WriteLine($"\nPowerToggleable_C idx: {powerToggleableClassIdx}");
Console.WriteLine($"DeployableBase_C idx: {deployableBaseClassIdx}");

// If BP_DeployableBase_C not in imports, add it
if (deployableBaseClassIdx == -1)
{
    Console.WriteLine("\nAdding BP_DeployableBase imports...");
    
    var pkgImport = new Import(
        "/Script/CoreUObject",
        "Package",
        new FPackageIndex(0),
        "/Game/BP/Objects/World/Items/Deployables/BP_DeployableBase",
        false, asset
    );
    asset.Imports.Add(pkgImport);
    int pkgIdx = asset.Imports.Count;

    var classImport = new Import(
        "/Script/Engine",
        "BlueprintGeneratedClass",
        new FPackageIndex(-pkgIdx),
        "BP_DeployableBase_C",
        false, asset
    );
    asset.Imports.Add(classImport);
    deployableBaseClassIdx = asset.Imports.Count - 1;
    Console.WriteLine($"  Added BP_DeployableBase_C at import index {deployableBaseClassIdx}");
}

// Fix each function's outer
int fixCount = 0;
foreach (string funcName in functionsToFix)
{
    int funcIdx = -1;
    for (int i = 0; i < asset.Imports.Count; i++)
    {
        if (asset.Imports[i].ObjectName.ToString() == funcName) { funcIdx = i; break; }
    }
    
    if (funcIdx == -1)
    {
        Console.WriteLine($"\n  {funcName}: not found in imports - skipping");
        continue;
    }

    var funcImport = asset.Imports[funcIdx];
    int currentOuter = funcImport.OuterIndex.Index;
    int targetOuter = -(deployableBaseClassIdx + 1);
    
    if (currentOuter == targetOuter)
    {
        Console.WriteLine($"\n  {funcName}: already points to DeployableBase - no fix needed");
        continue;
    }
    
    Console.WriteLine($"\n  {funcName}: fixing outer {currentOuter} -> {targetOuter}");
    funcImport.OuterIndex = new FPackageIndex(targetOuter);
    fixCount++;
}

if (fixCount > 0)
{
    asset.Write(assetPath);
    Console.WriteLine($"\n=== {fixCount} fix(es) applied and saved ===");
    
    // Verify
    var verify = new UAsset(assetPath, EngineVersion.VER_UE4_27);
    Console.WriteLine("\n=== Imports After Fix ===");
    for (int i = 0; i < verify.Imports.Count; i++)
    {
        var imp = verify.Imports[i];
        Console.WriteLine($"  Import[{i}] = {imp.ObjectName} (Class: {imp.ClassName}, Outer: {imp.OuterIndex})");
    }
}
else
{
    Console.WriteLine("\n=== No fixes needed ===");
}
