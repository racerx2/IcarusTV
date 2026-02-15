# Icarus UE4 Modding Rules — Hard-Learned Lessons

## Rule 1: Directory Structure Must Match the Game
Asset paths in your mod project must mirror the game's content paths exactly.
At runtime, UE4 resolves references by path — if yours don't match, assets fail to load.

Example: BP_SecondaryWidgetInterface lives at `Content/UI/Popups/` in the game,
so the stub must be created at `Content/UI/Popups/` in the mod project.

## Rule 2: PascalCase FNames Must Be Exact — Use C++ Stubs
The UE4 Blueprint editor automatically inserts spaces into PascalCase function names
when cooking. `OnDeviceTurnedOff` becomes `On Device Turned Off` in the cooked FName table.
The game expects the exact C++ name with no spaces.

**The ONLY reliable fix:** Declare functions in C++ header stubs.
The C++ compiler preserves exact FNames. Never create override functions as
Blueprint-defined functions — they will always get spaces inserted.

## Rule 3: Stubs Are Required for Parent Class Overrides
The mod editor uses stub parent classes that don't expose the real game's functions.
Without stubs:
- Functions don't appear in the Override dropdown
- Manually created functions aren't registered as proper overrides
- Cooked Super references point to wrong class levels → crash

C++ stubs solve Rules 2 AND 3 simultaneously.

## Current C++ Stubs

### DeployableBaseStub.h (maps to BP_DeployableBase)
- `Deployable_Interact(AActor* Interactor)` — player F-interact hook
- `GetWidgetClass()` → `TSubclassOf<UUserWidget>` — returns custom widget class for inspect UI

### PowerToggleableStub.h (maps to BP_Deployable_PowerToggleableBase)
- `OnDeviceTurnedOn()` — power connected
- `OnDeviceTurnedOff()` — power disconnected
- `OnDeviceStartRunning()` — device starts operating
- `OnDeviceStopRunning()` — device stops operating

## Build Script: Super Fix
After cooking, the build script (build_deploy.ps1) runs a UAssetAPI patch to redirect
import outer references from the stub parent to the correct real game parent class.
Example: `Deployable_Interact` outer redirected from PowerToggleableBase → BP_DeployableBase.

## Blueprint Interface Stubs
`BP_SecondaryWidgetInterface` — stub at `Content/UI/Popups/` defines `GetWidgetClass`.
BP_TV implements this interface so the engine dispatches through the interface vtable.
