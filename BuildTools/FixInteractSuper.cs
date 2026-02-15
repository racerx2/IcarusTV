using System;
using System.IO;
using System.Linq;
using UAssetAPI;
using UAssetAPI.UnrealTypes;

class Program
{
    static void Main(string[] args)
    {
        string assetPath = @"C:\TVModBuilder\PakContent\Icarus\Content\Mods\TV\Blueprints\BP_TV.uasset";
        
        var asset = new UAsset(assetPath, UE4Version.VER_UE4_27);
        
        Console.WriteLine("=== Imports ===");
        for (int i = 0; i < asset.Imports.Count; i++)
        {
            var imp = asset.Imports[i];
            Console.WriteLine($"Import[{i}] = {imp.ObjectName} (ClassPackage: {imp.ClassPackage}, ClassName: {imp.ClassName}, OuterIndex: {imp.OuterIndex})");
        }
        
        // Find the import that references BP_Deployable_PowerToggleableBase_C:Deployable_Interact
        // and change its outer to point to BP_DeployableBase_C instead
        
        int deployableInteractIdx = -1;
        int powerToggleableClassIdx = -1;
        int deployableBaseClassIdx = -1;
        
        for (int i = 0; i < asset.Imports.Count; i++)
        {
            var imp = asset.Imports[i];
            string name = imp.ObjectName.ToString();
            
            if (name == "Deployable_Interact")
            {
                deployableInteractIdx = i;
                Console.WriteLine($"\nFound Deployable_Interact at import index {i}, OuterIndex: {imp.OuterIndex}");
            }
            if (name == "BP_Deployable_PowerToggleableBase_C")
            {
                powerToggleableClassIdx = i;
                Console.WriteLine($"Found BP_Deployable_PowerToggleableBase_C at import index {i}");
            }
            if (name == "BP_DeployableBase_C")
            {
                deployableBaseClassIdx = i;
                Console.WriteLine($"Found BP_DeployableBase_C at import index {i}");
            }
        }
        
        if (deployableInteractIdx == -1)
        {
            Console.WriteLine("ERROR: Could not find Deployable_Interact import!");
            return;
        }
        
        // Check if BP_DeployableBase_C already exists as an import
        if (deployableBaseClassIdx == -1)
        {
            Console.WriteLine("\nBP_DeployableBase_C not found in imports, need to add it...");
            
            // We need to add imports for:
            // 1. The package: /Game/BP/Objects/World/Items/Deployables/BP_DeployableBase
            // 2. The class: BP_DeployableBase_C (outer = package)
            
            // First add the package import
            var pkgImport = new Import(
                new FName(asset, "/Script/CoreUObject"),  // ClassPackage
                new FName(asset, "Package"),               // ClassName
                new FPackageIndex(0),                      // OuterIndex (0 = no outer)
                new FName(asset, "/Game/BP/Objects/World/Items/Deployables/BP_DeployableBase"),
                false, asset
            );
            asset.Imports.Add(pkgImport);
            int pkgIdx = asset.Imports.Count; // 1-based negative index
            
            // Now add the class import
            var classImport = new Import(
                new FName(asset, "/Script/Engine"),        // ClassPackage  
                new FName(asset, "BlueprintGeneratedClass"), // ClassName
                new FPackageIndex(-pkgIdx),                 // OuterIndex points to package
                new FName(asset, "BP_DeployableBase_C"),
                false, asset
            );
            asset.Imports.Add(classImport);
            deployableBaseClassIdx = asset.Imports.Count - 1;
            Console.WriteLine($"Added BP_DeployableBase_C as import index {deployableBaseClassIdx}");
        }
        
        // Now fix the Deployable_Interact import's OuterIndex to point to BP_DeployableBase_C
        var diImport = asset.Imports[deployableInteractIdx];
        int oldOuterRaw = diImport.OuterIndex.Index;
        
        // OuterIndex uses FPackageIndex: negative values = imports (1-based), positive = exports
        // Import index N is referenced as -(N+1)
        int newOuterRaw = -(deployableBaseClassIdx + 1);
        
        Console.WriteLine($"\nChanging Deployable_Interact OuterIndex from {oldOuterRaw} to {newOuterRaw}");
        diImport.OuterIndex = new FPackageIndex(newOuterRaw);
        
        // Also check exports for SuperStruct references
        Console.WriteLine("\n=== Exports ===");
        foreach (var exp in asset.Exports)
        {
            Console.WriteLine($"Export: {exp.ObjectName} (ClassIndex: {exp.ClassIndex}, SuperIndex: {exp.SuperIndex})");
        }
        
        // Save
        asset.Write(assetPath);
        Console.WriteLine("\nSaved successfully!");
    }
}