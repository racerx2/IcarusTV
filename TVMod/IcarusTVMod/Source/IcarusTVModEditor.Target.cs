using UnrealBuildTool;

public class IcarusTVModEditorTarget : TargetRules
{
    public IcarusTVModEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V2;
        ExtraModuleNames.Add("IcarusTVMod");
    }
}