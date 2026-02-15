# TV Mod - Power Toggle Investigation Session
# Date: 2025-02-11
# Status: ACTIVE INVESTIGATION

## CRITICAL DISCOVERY: Flow Meter Power Control

The Flow Meter (`BP_FlowMeter`) at `/Game/BP/Objects/World/Items/Deployables/Networks/BP_FlowMeter`
has a UI that lists ALL connected power devices and can toggle them on/off individually.

### Flow Meter Data:
- D_DeployableSetup: line 7049, blueprint path `/Game/BP/Objects/World/Items/Deployables/Networks/BP_FlowMeter.BP_FlowMeter_C`
- D_Resource: `Flow_Meter` row - has `bHasEnergyConnection: true`, `bHasWaterConnection: true`
- D_Interactable: `Flow_Meter` row (line 2036) with TWO interactions:
  1. `Switch_Flow_Meter` → `BP_Interactable_Interact_FlowMeter` ("Switch Network Type")
  2. `Interact_Flow_Meter` → `BP_Interactable_Interact_Deployable` ("View Detailed Information")
- WorldHoldInteracts references a toggle interaction (line 2060-2067)

### Key Insight:
The Flow Meter can SEE and CONTROL power state of connected devices through the resource network.
This means there's an API/interface in the ResourceComponent or network system that:
1. Enumerates connected devices on a network
2. Reads their power on/off state
3. Can toggle individual devices on/off

### What This Means For TV Mod:
If the Flow Meter can toggle devices, the toggle mechanism works through the RESOURCE NETWORK,
not through blueprint parent class events. The `Interact_Toggle_Device_On` interaction 
(used by `Deployable_Power_Toggle_Only` interactable) likely calls into ResourceComponent
to flip a "device enabled" flag. The BP_Deployable_PowerToggleableBase then REACTS to that
flag change by firing OnDeviceTurnedOn/OnDeviceTurnedOff events.

### Investigation Needed:
1. Export BP_FlowMeter from FModel to see how it queries the network
2. Export BP_Deployable_PowerToggleableBase to see OnDeviceTurnedOn/Off implementation
3. Export BP_Interactable_Interact_Toggle_Device_On to see what it actually calls
4. Look at ResourceComponent C++ class for toggle-related BlueprintCallable functions

## PARENT CLASS REPARENTING PLAN (Still the primary approach)

### The Core Problem:
- BP_TV extends BP_DeployableBase (plain base, no power events)
- Wall lights extend BP_Deployable_PowerToggleableBase (has OnDeviceTurnedOn/Off events)
- D_ItemsStatic has correct config: Electric_Light_Single resource + Deployable_Power_Toggle_Only interactable
- F-key toggle UI appears and works at game level
- But BP_TV blueprint can't RESPOND to power state because wrong parent class

### The Solution:
Use UAssetAPI to change the parent class import in the cooked BP_TV.uasset:
- Change import reference from BP_DeployableBase → BP_Deployable_PowerToggleableBase
- Game engine loads real PowerToggleable class at runtime
- BP inherits OnDeviceTurnedOn/OnDeviceTurnedOff events
- Override OnDeviceTurnedOn → MediaPlayer.OpenUrl(StreamURL)
- Override OnDeviceTurnedOff → MediaPlayer.Close()

### Files:
- Fresh cooked BP_TV: C:\IcarusTVMod\IcarusTVMod\Saved\Cooked\WindowsNoEditor\IcarusTVMod\Content\Mods\TV\Blueprints\BP_TV.uasset (5,773 bytes)
- Fresh cooked BP_TV: C:\IcarusTVMod\IcarusTVMod\Saved\Cooked\WindowsNoEditor\IcarusTVMod\Content\Mods\TV\Blueprints\BP_TV.uexp (2,656 bytes)
- UAssetAPI source: C:\TVModBuilder\UAssetAPI\
- BytecodeMod tool: C:\TVModBuilder\BytecodeMod\BytecodeMod\Program.cs
- Current pak: C:\TVModBuilder\TV_Mod_P.pak (345,007 bytes)

## INTERACTABLE SYSTEM REFERENCE

### D_Interactable location: 
`D:\Program Files (x86)\Icarus_Mod_Manager_2_2_6\data\Traits\D_Interactable.json`

### Key Interactable Rows:
- `Deployable_Power_Toggle_Only` (line 2117): WorldPress=[Pickup_Item, Inspect_Deployable], WorldHold=[Interact_Toggle_Device_On], WorldAltHold=[Pickup_Deployable]
- `Flow_Meter` (line 2036): WorldPress=[Switch_Flow_Meter, Interact_Flow_Meter+more], WorldHold=[toggle]
- `Deployable` (line ~62): WorldPress=[Interact_Deployable, Pickup_Item], WorldHold=[Interact_Toggle_Device_On], WorldAltHold=[Pickup_Deployable]

### D_Interactions location:
`D:\Program Files (x86)\Icarus_Mod_Manager_2_2_6\data\Interactions\D_Interactions.json`

### Key Interaction Behaviours:
- `Interact_Toggle_Device_On` → `BP_Interactable_Interact_Toggle_Device_On` (line 537) - "Toggle Device On/Off"
- `Interact_Deployable` → `BP_Interactable_Interact_Deployable` (line 31) - "Interact" (opens inventory/UI)
- `Switch_Flow_Meter` → `BP_Interactable_Interact_FlowMeter` (line 507) - "Switch Network Type"

### 70 Unique Interactable RowNames found in D_ItemsStatic (full list in find_interactables.py output)

## PREVIOUS SESSION BYTECODE KNOWLEDGE

### BP_TV Bytecode Structure (fresh cook, no timer):
- ExecuteUbergraph_BP_TV: 64 bytes - ComputedJump → OpenUrl(StreamURL)
- ReceiveBeginPlay: 18 bytes - calls ExecuteUbergraph
- Name map: ~97 entries, Import table: ~43 entries, Export table: ~15 entries

### Critical UE4.27 Bytecode Facts:
- ScriptBytecodeSize = iCode size (8-byte pointers in memory)
- scriptStorageSize = disk bytes (4-byte FPackageIndex as int32)
- Jump offsets use iCode sizes, NOT disk byte positions
- UAssetAPI's Visit() method correctly computes iCode offsets
- EX_Context: ObjectExpr + uint32 Offset(iCode) + 16-byte RValuePointer + ContextExpr (NO PropertyType in UE4.27)
- FFieldPath serialization: 16 bytes (4 PathLength + 8 FName + 4 ResolvedOwner)

## NEXT STEPS
1. Use FModel to export BP_FlowMeter, BP_Deployable_PowerToggleableBase, BP_Interactable_Interact_Toggle_Device_On
2. Analyze how power toggle mechanism works through ResourceComponent
3. Implement parent class reparenting via UAssetAPI
4. Add OnDeviceTurnedOn/Off overrides with OpenUrl/Close calls
5. Test power toggle → video on/off

## CONFIRMED ARCHITECTURE (from JSON export analysis)

### BP_Deployable_PowerToggleableBase Function Map:
```
IcarusBeginPlay
  └─ For each ResourceNetworkComponent:
       ├─ Bind OnDeviceOnStateChanged delegate
       └─ Bind OnBrownOutStrengthChanged delegate

OnDeviceOnStateChanged(bIsOn)     ← delegate callback from ResourceComponent
  ├─ if bIsOn → OnDeviceTurnedOn()    [EX_LocalVirtualFunction - OVERRIDABLE]
  └─ if !bIsOn → OnDeviceTurnedOff()  [EX_LocalVirtualFunction - OVERRIDABLE]
  └─ then → CheckDeviceRunning()

CheckDeviceRunning()
  └─ CalculateIsDeviceRunning()
       ├─ if running → OnDeviceStartRunning()  [virtual]
       └─ if stopped → OnDeviceStopRunning()   [virtual]

OnRep_IsDeviceRunning()           ← multiplayer replication callback
  └─ CheckDeviceRunning()
```

### Key C++ Delegates (from /Script/Icarus):
- `OnDeviceOnStateChanged__DelegateSignature` - fires when toggle state changes
- `OnBrownOutStrengthChanged__DelegateSignature` - fires on brownout

### JSON Export Location:
`C:\IcarusGameDump\Exports\Icarus\Content\BP\Objects\World\Items\Deployables\BP_Deployable_PowerToggleableBase.json`
(6468 lines)

### IMPLEMENTATION PLAN:
1. Use UAssetAPI to change BP_TV parent class import from BP_DeployableBase → BP_Deployable_PowerToggleableBase
2. Add OnDeviceTurnedOn override → MediaPlayer.OpenUrl(StreamURL) 
3. Add OnDeviceTurnedOff override → MediaPlayer.Close()
4. All delegate binding, network enumeration, replication comes FREE from parent
5. Flow Meter integration comes FREE (it queries ResourceNetworkComponent)
