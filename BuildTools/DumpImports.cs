using System;
using System.IO;
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
            Console.WriteLine($"[{i}] {imp.ObjectName}  (Class: {imp.ClassName}, Outer: {imp.OuterIndex.Index})");
        }
        
        Console.WriteLine("\n=== Exports ===");
        for (int i = 0; i < asset.Exports.Count; i++)
        {
            var exp = asset.Exports[i];
            Console.WriteLine($"[{i}] {exp.ObjectName}  (Super: {exp.SuperIndex.Index})");
        }
    }
}