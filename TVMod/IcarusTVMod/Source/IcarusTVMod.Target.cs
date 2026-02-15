using UnrealBuildTool;

public class IcarusTVModTarget : TargetRules
{
    public IcarusTVModTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V2;
        ExtraModuleNames.Add("IcarusTVMod");
    }
}