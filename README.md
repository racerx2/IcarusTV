# Icarus TV Mod

A deployable flat-screen TV for the survival game [Icarus](https://store.steampowered.com/app/1149460/ICARUS/) that streams live IPTV, local media files, or any HTTP video source directly onto an in-game wall-mounted screen. Built for Unreal Engine 4.27.2.

## What It Does

- Wall-mounted 55-inch flat-screen TV, craftable at the Fabricator and deployable on walls
- Live IPTV streaming via a local relay server that transcodes any source to UE4-compatible MP4
- Local media file playback (MP4, MKV, AVI, MOV, and more)
- Multiplayer support through Cloudflare tunneling so friends on your server can watch the same stream
- Full power system integration with the Icarus electrical grid
- Custom UI widget accessible through the native F-interact system

## Architecture

```
[IPTV Provider / Local Files]
          |
  [Icarus Relay Server]
    FFmpeg transcodes -> fragmented MP4
    HTTP server on port 8080
          |
  http://localhost:8080/stream.mp4
          |
  [UE4 MediaPlayer -> MediaTexture -> TV Screen Material]
          |
  [In-game TV screen]
```

The relay server runs alongside the game on your PC. It transcodes any video source into UE4-compatible fragmented MP4 and serves it over HTTP. The TV blueprint opens this URL through UE4's Media Framework.

## Repository Structure

```
IcarusTV/
|-- README.md                            This file
|-- MODDING_RULES.md                     Hard-learned UE4 modding lessons
|-- TV_Mod_P.pak                         Pre-built pak (drop into mods folder)
|-- IcarusRelayServer/
|   |-- icarus_relay.py                  Streaming relay server (Python/Tkinter)
|   |-- .gitignore                       Excludes credentials and ffmpeg binary
|   +-- ffmpeg/                          Place ffmpeg.exe here (not included)
|-- TVMod/                               Raw UE4 mod editor project
|   |-- IcarusTVMod.uproject
|   |-- Source/
|   |   |-- IcarusTVMod.Target.cs
|   |   |-- IcarusTVModEditor.Target.cs
|   |   +-- IcarusTVMod/
|   |       |-- IcarusTVMod.Build.cs
|   |       |-- Public/
|   |       |   |-- DeployableBaseStub.h     Deployable_Interact + GetWidgetClass
|   |       |   |-- PowerToggleableStub.h    Power event overrides
|   |       |   +-- IcarusTVMod.h            Module header
|   |       +-- Private/
|   |           +-- IcarusTVMod.cpp          Module implementation
|   +-- Content/
|       |-- Mods/TV/
|       |   |-- Blueprints/BP_TV             Main TV blueprint
|       |   |-- Materials/                   Body, screen, off-state materials
|       |   |-- Meshes/                      Frame and screen static meshes
|       |   |-- Textures/                    Crafting icon (T_ITEM_TV)
|       |   |-- MP_TVStream                  MediaPlayer asset
|       |   |-- MP_TVStream_Video            MediaTexture asset
|       |   +-- UMG_TVControls               UI widget
|       +-- UI/Popups/
|           +-- BP_SecondaryWidgetInterface   Blueprint Interface stub
|-- BuildTools/
|   |-- build_deploy.ps1                 Automated cook -> fix -> pak -> deploy
|   +-- BytecodeMod/
|       |-- Program.cs                   Super reference fix tool (C#)
|       +-- BytecodeMod.csproj           .NET 8 project file
+-- DataTables/
    +-- TV_DataTables.md                 All server-side JSON entries documented
```

---

## The Journey: How We Built This

This section documents every major problem we hit and how we solved it. If you are modding Icarus or any UE4 game with a custom mod editor, these lessons will save you weeks.

### Phase 1: Concept and 3D Model

The idea was simple: bring a working TV into Icarus that could stream live IPTV content. We already had a relay server built for another project that transcodes IPTV streams into fragmented MP4 over HTTP. All we needed was a 3D model, a deployable blueprint, and a way to pipe the stream onto a screen.

We started with a 3DS model of an LG flat-screen TV imported into Blender. The import came in at 33 meters wide due to unit differences in the 3DS format, with messy negative scales and wrong rotations from the conversion.

Key steps in Blender:
- Joined all mesh pieces into one object, applied all transforms (Ctrl+A)
- Scaled to real-world dimensions: 1.12m wide x 0.69m tall x 0.10m deep (55 inch TV)
- Separated the screen faces into their own mesh object (TV_Screen) with its own material slot
- Reset screen UVs to fill the full 0-1 space so video textures map correctly
- Pushed the screen plane slightly forward (about 1mm) to prevent z-fighting with the frame
- Exported as FBX with Y-Forward, Z-Up, Apply Transform checked

The screen must be a separate mesh object because UE4's MediaTexture needs to be applied to a specific material on a specific mesh component. Having the screen as its own StaticMeshComponent lets us swap just that material to show video without touching the TV body.

### Phase 2: UE4 Project and Blueprint Setup

The Icarus mod editor (IcarusModEditorVer4_1) is a custom UE4 4.27.2 build. It lacks the real game's C++ classes entirely. You work with stub parent classes that approximate the game's hierarchy but expose none of the real functions.

BP_TV blueprint structure:
- Parent class: BP_Deployable_PowerToggleableBase (via our stub)
- Components: TV_Frame (StaticMesh), TV_Screen (StaticMesh), TV_Audio (MediaSoundComponent)
- Variables: StreamURL (String, default http://localhost:8080/stream.mp4), MediaPlayerRef, bisPlaying, TV_OffMaterial, TVControlsWidget
- MediaPlayer asset: MP_TVStream configured for HTTP streaming
- MediaTexture: MP_TVStream_Video linked to MP_TVStream

Material setup:
- M_TV_Body: standard PBR material for the frame
- M_TV_Screen: material instance that samples from MP_TVStream_Video (MediaTexture linked to the MediaPlayer)
- M_TV_Off: dark material shown when the TV is unpowered

Power event logic (OnDeviceTurnedOn/Off, OnDeviceStartRunning/StopRunning):
- Power on: MediaPlayer opens StreamURL, screen mesh gets M_TV_Screen applied
- Power off: MediaPlayer closes, screen mesh reverts to M_TV_Off

### Phase 3: Data Tables (Server-Side)

Icarus uses JSON data tables for all item definitions. These run server-side and get merged via Icarus Mod Manager (IMM) or manual JSON editing. The TV required entries in 8 separate data tables to exist in the crafting system:

- D_ItemsStatic: core item definition that links all other traits together
- D_ItemTemplate: runtime item template
- D_Itemable: display name ("Flat Screen TV"), icon path, description text
- D_Deployable: links the item to D_DeployableSetup
- D_DeployableSetup: the critical entry — sets the blueprint path (/Game/Mods/TV/Blueprints/BP_TV.BP_TV_C), preview mesh, wall placement mode, and snap angles
- D_Resource: power grid connection (reuses Electric_Light_Single)
- D_Energy: energy flow configuration
- D_ProcessorRecipes: crafting recipe (4 Electronics + 1 Glass + 1 Aluminium at the Fabricator)
- D_BlueprintUnlocks: tech tree unlock point

The DeployableBlueprint path in D_DeployableSetup must exactly match where the cooked asset ends up in the pak. Getting this wrong means the item crafts and appears in inventory but spawns nothing when placed.

All data table entries are documented in DataTables/TV_DataTables.md.

### Phase 4: The PascalCase FName Disaster

This was the first wall we hit. Everything looked correct in the editor — the TV placed on walls, connected to power cables, but the power events never fired. OnDeviceTurnedOn, OnDeviceTurnedOff, OnDeviceStartRunning, OnDeviceStopRunning — all silent.

We spent hours checking wiring, verifying power connections, testing different generator setups. Everything was hooked up correctly. The problem was invisible because it was in the cooked binary.

When we exported the cooked BP_TV.uasset to JSON using UAssetGUI, we found it. The UE4 Blueprint editor automatically inserts spaces into PascalCase function names when cooking assets. In the FName table of the cooked binary:

- OnDeviceTurnedOff became "On Device Turned Off"
- OnDeviceTurnedOn became "On Device Turned On"
- OnDeviceStartRunning became "On Device Start Running"
- OnDeviceStopRunning became "On Device Stop Running"

The real game's C++ code dispatches virtual calls using the exact PascalCase names with no spaces. The Blueprint editor's cooked names simply did not match, so the engine could never find our override implementations.

The solution: C++ header stubs. Instead of creating override functions through the Blueprint editor's GUI (which mangles the names on cook), we declare them in C++ header files that compile with the mod editor. The C++ compiler preserves exact FNames because it is working with actual symbol names, not display strings.

```cpp
// PowerToggleableStub.h
UCLASS(Blueprintable)
class APowerToggleableStub : public ADeployableBaseStub
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, BlueprintImplementableEvent)
    void OnDeviceTurnedOn();
    UFUNCTION(BlueprintCallable, BlueprintImplementableEvent)
    void OnDeviceTurnedOff();
    UFUNCTION(BlueprintCallable, BlueprintImplementableEvent)
    void OnDeviceStartRunning();
    UFUNCTION(BlueprintCallable, BlueprintImplementableEvent)
    void OnDeviceStopRunning();
};
```

With these stubs compiled, the functions appear in the Override dropdown in the Blueprint editor and cook with the correct FNames. Power events started firing immediately.

This became Rule 2: never create override functions as Blueprint functions. Always use C++ stubs.

### Phase 5: The Super Reference Problem

With power events working, we moved to the interaction system. The game shows "F - Press to Inspect" on deployables, and we needed to intercept that press to do something useful. The function for this is Deployable_Interact, defined on BP_DeployableBase in the real game.

We added Deployable_Interact to our DeployableBaseStub.h and overrode it in BP_TV. It cooked with the correct FName (no spaces, thanks to the C++ stub). But it crashed or silently failed at runtime.

The root cause was in the cooked binary's import table. Our stub class hierarchy is:

```
APowerToggleableStub -> ADeployableBaseStub -> AActor
```

When BP_TV overrides Deployable_Interact (defined on DeployableBaseStub), the UE4 cooker writes the Super reference as:

```
BP_Deployable_PowerToggleableBase_C:Deployable_Interact
```

It points to the immediate parent class. But in the real game, Deployable_Interact lives on BP_DeployableBase, which is one level higher in the hierarchy. The import outer reference was pointing to the wrong class, so the Super call resolved to nothing.

We built BytecodeMod, a C# tool using UAssetAPI, to fix this post-cook. It opens the cooked BP_TV.uasset, finds function imports that need fixing, and redirects their OuterIndex from PowerToggleableBase_C to BP_DeployableBase_C:

```csharp
string[] functionsToFix = { "Deployable_Interact", "GetWidgetClass" };
foreach (string funcName in functionsToFix)
{
    // Redirect outer from PowerToggleableBase to DeployableBase
    funcImport.OuterIndex = new FPackageIndex(-(deployableBaseClassIdx + 1));
}
```

If BP_DeployableBase_C does not already exist in the import table, the tool adds it along with its package import. The fix runs automatically as part of the build pipeline.

### Phase 6: The Interaction UI

With Deployable_Interact firing correctly, we needed to show a custom widget when the player presses F. This went through several failed approaches before we found the right one.

Attempt 1 — TriggerBox overlap: We added a CapsuleComponent with ActorBeginOverlap to detect nearby players and auto-open the UI. It worked technically but was the wrong UX — players should explicitly press F, not just walk near the TV.

Attempt 2 — Manual widget creation via RPC: We created a Client_OpenTVMenu custom event that manually creates the widget, adds it to viewport, shows the mouse cursor, and sets input mode to UI Only. This created the widget correctly but we had no reliable trigger to call it from.

Attempt 3 — Deployable_Interact calling Client_OpenTVMenu directly: This was closer but the widget was not being created by the game's expected system, leading to lifecycle issues.

The breakthrough came from analyzing the game's base classes with FModel. BP_DeployableBase has a function called GetWidgetClass that returns a TSubclassOf<UUserWidget>. When the player presses F to interact with any deployable, the game calls GetWidgetClass on that actor. If it returns a valid widget class, the game creates and displays the widget automatically using its own UI management system, handling focus, input modes, and cleanup.

But GetWidgetClass is not a regular virtual function. It is a Blueprint Interface method from BP_SecondaryWidgetInterface. This meant we had to:

1. Create a stub for BP_SecondaryWidgetInterface at Content/UI/Popups/ in the mod project (matching the game's internal path — this is Rule 1)
2. Add the interface to BP_TV via Class Settings, then Interfaces
3. Override GetWidgetClass to return UMG_TVControls (our custom widget class)
4. Add GetWidgetClass to DeployableBaseStub.h so the FName cooks correctly (Rule 2)
5. Apply the same Super reference fix via BytecodeMod (Rule 3)

The widget itself (UMG_TVControls) receives a reference to BP_TV through an Init Vars pattern, allowing it to call functions on the TV actor like changing channels or toggling power.

### Phase 7: The Streaming Server

The relay server was originally built for a VR application that had the same problem: IPTV providers serve MKV containers with codecs (HEVC, AC3) that most game engines cannot decode natively. UE4's Media Foundation backend on Windows only reliably handles H.264 in MP4 containers.

The relay server solves this by sitting between the IPTV source and the game:

1. User browses channels/shows/movies through a Tkinter GUI
2. When content is selected, the server resolves the IPTV API URL and starts FFmpeg
3. FFmpeg transcodes the source to H.264 Main profile + AAC audio in a fragmented MP4 container
4. An HTTP server on port 8080 serves the stream at /stream.mp4
5. UE4's MediaPlayer opens this URL and feeds frames to the MediaTexture on the TV screen

Key FFmpeg settings for UE4 compatibility:
- The -re flag for real-time pacing is critical. Without it, FFmpeg transcodes faster than realtime, flooding UE4 with a burst of data that overwhelms Media Foundation's decoder and causes the stream to never display.
- Fragmented MP4 flags (frag_keyframe+empty_moov+default_base_moof) enable streaming playback without needing the full file.
- Forced keyframes every 2 seconds so clients can join mid-stream.
- H.264 Main profile level 4.1 for maximum Media Foundation compatibility.

The SharedStream architecture serves all connected clients from one FFmpeg process. It parses MP4 box boundaries in real-time, caches the init segment (ftyp+moov), and maintains a rolling buffer of fragments. New clients receive the init segment plus the last couple fragments for a clean join point.

For multiplayer, Cloudflare tunneling exposes the local HTTP server so friends on the same Icarus server can point their TV at the tunnel URL instead of localhost.

Security hardening for the GitHub release replaced all hardcoded IPTV credentials with a config file system. On first run, a login dialog asks for provider URL, username, and password. These are saved locally to icarus_relay_config.json (gitignored). The app works without IPTV credentials for local file playback only.

### Phase 8: The Build Pipeline

After discovering all the above issues through painful trial and error, we automated the entire post-cook workflow into a single PowerShell script (build_deploy.ps1):

Step 1: Copy cooked assets from UE4's Saved/Cooked output to a PakContent staging directory
Step 2: Run BytecodeMod to fix Super references in the cooked BP_TV.uasset
Step 3: Generate a file list and build the pak using UnrealPak
Step 4: Deploy the pak to both server and client mods folders

The workflow after making any change is: open the editor, make changes, Compile, Save All, File then Cook Content for Windows, then run build_deploy.ps1. One command handles everything after cooking.

---

## Setup Guide

### Prerequisites

- Icarus Mod Editor v4.1 (UE4 4.27.2 custom build from RocketWerkz)
- .NET 8 SDK (for the BytecodeMod build tool)
- UAssetAPI (clone from https://github.com/atenfyr/UAssetAPI and build with dotnet build -c Release)
- Python 3.8 or later (for the relay server)
- FFmpeg (place ffmpeg.exe in IcarusRelayServer/ffmpeg/)
- UnrealPak (included with Icarus Mod Manager or from Epic's engine tools)
- Cloudflared (optional, only needed for multiplayer tunneling)

### Quick Start: Just Use the Pre-Built Pak

If you only want to play with the TV mod and not modify it:

1. Copy TV_Mod_P.pak to your Icarus mods folder:
   - Server: (server path)/Icarus/Content/Paks/mods/
   - Client: Steam/steamapps/common/Icarus/Icarus/Content/Paks/mods/
2. The server also needs the data table entries merged (see DataTables/TV_DataTables.md)
3. Run the relay server: python IcarusRelayServer/icarus_relay.py
4. In-game: craft the TV at the Fabricator, place it on a wall, connect power, press F to interact

### Building from Source

1. Clone UAssetAPI and build it
2. Open TVMod/IcarusTVMod.uproject in the Icarus Mod Editor
3. C++ stubs compile automatically on editor launch
4. Make your changes to blueprints or content
5. Compile, Save All, Cook Content for Windows
6. Edit the paths in BuildTools/build_deploy.ps1 to match your system
7. Run: powershell -ExecutionPolicy Bypass -File BuildTools/build_deploy.ps1

### Relay Server Setup

```
cd IcarusRelayServer
python icarus_relay.py
```

On first run, enter your IPTV credentials if you have a provider, or click Skip to use local files only.

### Phase 1: Concept and 3D Model

**Goal:** Get a TV model into Icarus as a placeable, powered deployable.

We started with a 3DS model of an LG flat-screen TV, imported into Blender. The import came in at 33 meters wide (about 30x too big), with messy transforms from the format conversion.

**Key steps in Blender:**
- Joined all mesh pieces into one object, applied all transforms
- Scaled to real-world dimensions: 1.12m x 0.69m x 0.10m (55" TV)
- Separated the screen into its own mesh object (TV_Screen) with its own material slot
- Reset screen UVs to fill 0-1 space so video textures map correctly
- Pushed screen plane slightly forward (~1mm) to prevent z-fighting with the frame
- Exported as FBX with Y-Forward, Z-Up

**Why the screen must be separate:** UE4's MediaTexture needs to be applied to a specific material on a specific mesh component. Having the screen as its own StaticMeshComponent lets us swap just that material to show video without affecting the TV body.

### Phase 2: UE4 Project and Blueprint Setup

**Goal:** Import the model, create a deployable blueprint with media playback.

The Icarus mod editor is a custom UE4 4.27.2 build that lacks the real game's C++ classes. You work with stub parent classes that approximate the game's hierarchy.

**BP_TV blueprint structure:**
- Parent class: BP_Deployable_PowerToggleableBase (stub)
- Components: TV_Frame (StaticMesh), TV_Screen (StaticMesh), TV_Audio (MediaSoundComponent)
- Variables: StreamURL (String, default http://localhost:8080/stream.mp4), MediaPlayerRef, bisPlaying, TV_OffMaterial, TVControlsWidget
- MediaPlayer asset: MP_TVStream configured for HTTP streaming

**Material setup:**
- M_TV_Body: standard material for the frame
- M_TV_Screen: material instance that samples from MP_TVStream_Video (MediaTexture linked to MediaPlayer)
- M_TV_Off: dark material shown when TV is unpowered

**Power events (OnDeviceTurnedOn/Off, OnDeviceStartRunning/OnDeviceStopRunning):**
- On power: MediaPlayer->OpenUrl(StreamURL), apply M_TV_Screen to screen mesh
- On power off: MediaPlayer->Close(), apply M_TV_Off material

### Phase 3: Data Tables (Server-Side)

**Goal:** Make the TV appear in the crafting system and tech tree.

Icarus uses JSON data tables for item definitions. These go into the server-side pak via Icarus Mod Manager (IMM). The TV required entries in 8 separate data tables:

| Data Table | Entry | Purpose |
|-----------|-------|---------|
| D_ItemsStatic | TV | Core item definition, links all traits |
| D_ItemTemplate | TV | Runtime item template |
| D_Itemable | Item_TV | Display name "Flat Screen TV", icon, description |
| D_Deployable | TV | Links to D_DeployableSetup |
| D_DeployableSetup | TV | Blueprint path, wall placement, preview mesh |
| D_Resource | Electric_Light_Single | Power grid connection (reuses existing) |
| D_ProcessorRecipes | TV | Crafting: 4 Electronics + 1 Glass + 1 Aluminium at Fabricator |
| D_BlueprintUnlocks | TV | Tech tree unlock point |

**Key detail in D_DeployableSetup:** The DeployableBlueprint path must be `/Game/Mods/TV/Blueprints/BP_TV.BP_TV_C` — this must exactly match where the cooked asset ends up in the pak. This is one of our core modding rules.

### Phase 4: The PascalCase FName Disaster

**Problem:** Power events never fired in-game. The TV placed fine, connected to power, but OnDeviceTurnedOn/Off/OnDeviceStartRunning/OnDeviceStopRunning did nothing.

**Root cause:** When the UE4 Blueprint editor cooks assets, it inserts spaces into PascalCase function names in the FName table. `OnDeviceTurnedOff` becomes `On Device Turned Off` in the cooked binary. The real game expects the exact C++ FName with no spaces, so the virtual dispatch never matches.

**Discovery process:** We exported the cooked uasset to JSON using UAssetGUI and found the mangled names in the name map. Every PascalCase function created through the Blueprint editor had spaces inserted.

**Solution: C++ Header Stubs**

Instead of creating override functions through the Blueprint editor (which mangles names), we declare them in C++ header files. The C++ compiler preserves exact FNames.

```cpp
// PowerToggleableStub.h
UCLASS(Blueprintable)
class APowerToggleableStub : public ADeployableBaseStub
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, BlueprintImplementableEvent)
    void OnDeviceTurnedOn();
    UFUNCTION(BlueprintCallable, BlueprintImplementableEvent)
    void OnDeviceTurnedOff();
    UFUNCTION(BlueprintCallable, BlueprintImplementableEvent)
    void OnDeviceStartRunning();
    UFUNCTION(BlueprintCallable, BlueprintImplementableEvent)
    void OnDeviceStopRunning();
};
```

With these stubs compiled into the mod editor, the functions appear in the Override dropdown and cook with correct FNames. **This is Rule #2: Never create override functions as Blueprint functions — always use C++ stubs.**

### Phase 5: The Super Reference Problem

**Problem:** After fixing FNames with C++ stubs, Deployable_Interact crashed or did not fire. The cooked blueprint's Super call pointed to the wrong parent class.

**Root cause:** The stub hierarchy is APowerToggleableStub -> ADeployableBaseStub -> AActor. When BP_TV overrides Deployable_Interact (defined on DeployableBaseStub), the cooked asset writes the Super reference as `BP_Deployable_PowerToggleableBase_C:Deployable_Interact` — pointing to the immediate parent. But in the real game, Deployable_Interact lives on BP_DeployableBase, one level higher. The import outer reference points to the wrong class.

**Solution: BytecodeMod post-cook fixer**

We built a C# tool using UAssetAPI that runs after cooking. It scans the import table for function references and redirects their OuterIndex from PowerToggleableBase to DeployableBase:

```csharp
string[] functionsToFix = { "Deployable_Interact", "GetWidgetClass" };
foreach (string funcName in functionsToFix)
{
    // Change outer from PowerToggleableBase_C to DeployableBase_C
    funcImport.OuterIndex = new FPackageIndex(-(deployableBaseClassIdx + 1));
}
```

If BP_DeployableBase_C is not already in the import table, the tool adds it automatically. This fix is applied by build_deploy.ps1 after every cook.

### Phase 6: The Interaction UI

**Problem:** How does the player open the TV controls widget? The game shows "F - Press to Inspect" on deployables, but our mod needs to intercept that to show custom UI.

**Approaches tried and failed:**

1. **TriggerBox overlap** — added a CapsuleComponent with ActorBeginOverlap to detect nearby players. It fired, but was the wrong approach — players should explicitly press F, not just walk near the TV.

2. **Manual widget creation via RPC** — created a Client_OpenTVMenu custom event that builds the widget directly. This worked for creating the widget but had no trigger mechanism.

**The breakthrough: GetWidgetClass**

Analyzing the game's base classes with FModel, we found that BP_DeployableBase has a function called GetWidgetClass that returns a TSubclassOf<UUserWidget>. When the player presses F to interact, the game calls GetWidgetClass on the deployable — if it returns a valid class, the game creates and displays that widget automatically.

**But GetWidgetClass is a Blueprint Interface method**, not a regular virtual function. It comes from BP_SecondaryWidgetInterface. We had to:

1. Create a stub for BP_SecondaryWidgetInterface at Content/UI/Popups/ (matching the game's path — Rule #1)
2. Add the interface to BP_TV via Class Settings -> Interfaces
3. Implement GetWidgetClass to return UMG_TVControls (our widget class)
4. Add GetWidgetClass to DeployableBaseStub.h so the FName cooks correctly (Rule #2)

**The widget architecture:**
- UMG_TVControls: UserWidget with TV control UI
- Client_OpenTVMenu: custom event that creates the widget, adds to viewport, enables mouse cursor, sets input mode to UI Only
- Init Vars: passes BP_TV reference (Self) to the widget so it can call functions on the TV actor
- Closing: SetInputMode_GameOnly restores normal gameplay controls

### Phase 7: The Build Pipeline

After all the above discoveries, we automated the workflow into a single script:

```
[UE4 Editor] -> Compile + Save -> Cook Content for Windows
                                        |
[build_deploy.ps1] Step 1: Copy cooked assets to staging
                   Step 2: Run BytecodeMod (fix Super references)
                   Step 3: Build pak with UnrealPak
                   Step 4: Deploy to server + client mods folder
```

A single PowerShell command handles everything after cooking. The script paths need to be edited to match your local directory structure.

### Phase 8: The Streaming Server

The relay server was originally built for a VR application and adapted for Icarus. It solves fundamental incompatibilities between IPTV streams and UE4's Media Framework.

**Why not just point UE4 at the IPTV stream directly?**
- IPTV providers serve MKV containers, which UE4's Media Foundation backend cannot decode
- Streams use API redirects that UE4's HTTP client cannot follow
- Codec combinations (HEVC, AC3) are not supported by Media Foundation

**FFmpeg transcoding pipeline:**
```
Input (any format) -> libx264 ultrafast + AAC -> fragmented MP4 -> stdout pipe
```

Key settings for UE4 compatibility:
- `-re` flag for real-time pacing (prevents burst that overwhelms Media Foundation)
- `-movflags frag_keyframe+empty_moov+default_base_moof` for streaming playback
- Forced keyframes every 2 seconds so clients can join mid-stream
- H.264 Main profile, level 4.1 (maximum Media Foundation compatibility)
- 3500kbps video, 128kbps AAC audio, 30fps

**SharedStream architecture:** One FFmpeg process serves all connected clients. The server parses MP4 box boundaries in real-time, caching the init segment (ftyp+moov) and maintaining a rolling buffer of fragments. New clients receive the init segment plus the last 2 fragments for a clean join point.

**Security:** Credentials are saved locally to `icarus_relay_config.json` (gitignored). On first run, a login dialog prompts for your IPTV provider URL, username, and password. You can skip IPTV setup entirely and use local files only.

---

## Setup Guide

### Prerequisites

- [Icarus Mod Editor v4.1](https://github.com/RocketWerkz/IcarusModdingDocumentation) (UE4 4.27.2)
- [.NET 8 SDK](https://dotnet.microsoft.com/download) (for BytecodeMod build tool)
- [UAssetAPI](https://github.com/atenfyr/UAssetAPI) (build from source, reference the DLL)
- [Python 3.8+](https://python.org) (for relay server)
- [FFmpeg](https://ffmpeg.org/download.html) (place in IcarusRelayServer/ffmpeg/)
- UnrealPak (from Epic Games or Icarus Mod Manager)
- [Cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/) (optional, for multiplayer tunneling)

### 1. Relay Server Setup

```bash
cd IcarusRelayServer
# Place ffmpeg.exe in ./ffmpeg/
python icarus_relay.py
```

On first run, a login dialog asks for your IPTV credentials (saved locally, gitignored). You can skip this and use Local Files only.

### 2. Mod Editor Setup

1. Clone UAssetAPI and build it: `dotnet build -c Release`
2. Open TVMod/IcarusTVMod.uproject in the Icarus Mod Editor
3. The C++ stubs compile automatically on editor launch
4. All Blueprint and content assets are in Content/Mods/TV/

### 3. Building the Pak

After making changes in the editor:

1. **Compile** the blueprint (button in toolbar)
2. **Save All**
3. **File -> Cook Content for Windows**
4. Edit paths in `BuildTools/build_deploy.ps1` to match your system
5. Update the UAssetAPI DLL path in `BuildTools/BytecodeMod/BytecodeMod.csproj`
6. Run: `powershell -ExecutionPolicy Bypass -File BuildTools\build_deploy.ps1`

### 4. Data Tables

The JSON entries in DataTables/ need to be merged into your server's data tables using Icarus Mod Manager or manual JSON editing. See DataTables/README.md for the exact entries. These define the item, crafting recipe, tech tree unlock, and deployment configuration.

### 5. Installation (End Users)

- **Server:** Place TV_Mod_P.pak in `<server>/Icarus/Content/Paks/mods/`
- **Client:** Place TV_Mod_P.pak in `<Steam>/steamapps/common/Icarus/Icarus/Content/Paks/mods/`
- Both server and client need the pak file
- Run the Icarus Relay Server on your PC for streaming

---

## Three Core Modding Rules

These apply to any Icarus mod (and likely other UE4 games with custom mod editors):

**Rule 1: Directory Structure Must Match the Game.**
Asset paths in your mod project must mirror the game's content paths exactly. At runtime, UE4 resolves references by path. If yours don't match, assets fail to load silently.

**Rule 2: PascalCase FNames Must Be Exact — Use C++ Stubs.**
The UE4 Blueprint editor inserts spaces into PascalCase function names when cooking. `OnDeviceTurnedOff` becomes `On Device Turned Off`. The game expects exact C++ names. Never create override functions as Blueprint functions. Always use C++ header stubs.

**Rule 3: Stubs Are Required for Parent Class Overrides.**
The mod editor uses stub parent classes. Without C++ stubs, override functions don't appear in the dropdown, aren't registered as proper overrides, and cooked Super references point to wrong class levels. The BytecodeMod tool fixes the Super references post-cook.

---

## Credits

Built by RacerX with assistance from Claude (Anthropic).

## License

MIT
