# TV Mod Build & Deploy Script
# Run after cooking in UE4: File > Cook Content for Windows

Write-Host "=== TV MOD BUILD & DEPLOY ===" -ForegroundColor Cyan

# Step 1: Copy cooked assets to PakContent staging
Write-Host "`n[1/4] Copying cooked assets..." -ForegroundColor Yellow
$cookDir = "C:\IcarusTVMod\IcarusTVMod\Saved\Cooked\WindowsNoEditor\IcarusTVMod\Content\Mods\TV"
$pakDir = "C:\TVModBuilder\PakContent\Icarus\Content\Mods\TV"

Copy-Item "$cookDir\Blueprints\BP_TV.uasset" "$pakDir\Blueprints\BP_TV.uasset" -Force
Copy-Item "$cookDir\Blueprints\BP_TV.uexp" "$pakDir\Blueprints\BP_TV.uexp" -Force
Copy-Item "$cookDir\UMG_TVControls.uasset" "$pakDir\UMG_TVControls.uasset" -Force
Copy-Item "$cookDir\UMG_TVControls.uexp" "$pakDir\UMG_TVControls.uexp" -Force
Copy-Item "$cookDir\Materials\*" "$pakDir\Materials\" -Force
Copy-Item "$cookDir\MP_TVStream.uasset" "$pakDir\MP_TVStream.uasset" -Force
Copy-Item "$cookDir\MP_TVStream.uexp" "$pakDir\MP_TVStream.uexp" -Force
Copy-Item "$cookDir\MP_TVStream_Video.uasset" "$pakDir\MP_TVStream_Video.uasset" -Force
Copy-Item "$cookDir\MP_TVStream_Video.uexp" "$pakDir\MP_TVStream_Video.uexp" -Force
Write-Host "  Done." -ForegroundColor Green

# Step 2: Apply GetWidgetClass override fix
Write-Host "`n[2/4] Applying GetWidgetClass SuperStruct fix..." -ForegroundColor Yellow
cd C:\TVModBuilder\BytecodeMod\BytecodeMod
dotnet run 2>&1 | ForEach-Object { Write-Host "  $_" }
Write-Host "  Done." -ForegroundColor Green

# Step 3: Build pak
Write-Host "`n[3/4] Building pak..." -ForegroundColor Yellow
Remove-Item "C:\TVModBuilder\TV_Mod_P.pak" -ErrorAction SilentlyContinue
$files = Get-ChildItem "C:\TVModBuilder\PakContent" -Recurse -File
$lines = $files | ForEach-Object { "`"$($_.FullName)`" `"../../../$($_.FullName.Replace('C:\TVModBuilder\PakContent\','').Replace('\','/'))`"" }
$lines | Set-Content "C:\TVModBuilder\filelist.txt" -Encoding ASCII
& "C:\Icarus_Mod_Manager_2_2_6\UnrealPak\Engine\Binaries\Win64\UnrealPak.exe" "C:\TVModBuilder\TV_Mod_P.pak" -Create="C:\TVModBuilder\filelist.txt" -compress 2>&1 | Select-Object -Last 3
$pakSize = (Get-Item "C:\TVModBuilder\TV_Mod_P.pak").Length
Write-Host "  Pak: $pakSize bytes" -ForegroundColor Green

# Step 4: Deploy to server and client
Write-Host "`n[4/4] Deploying..." -ForegroundColor Yellow
Copy-Item "C:\TVModBuilder\TV_Mod_P.pak" "C:\icarusserver\server\Icarus\Content\Paks\mods\TV_Mod_P.pak" -Force
Copy-Item "C:\TVModBuilder\TV_Mod_P.pak" "C:\Program Files (x86)\Steam\steamapps\common\Icarus\Icarus\Content\Paks\mods\TV_Mod_P.pak" -Force
Write-Host "  Server: C:\icarusserver\server\Icarus\Content\Paks\mods\TV_Mod_P.pak" -ForegroundColor Green
Write-Host "  Client: Steam\...\mods\TV_Mod_P.pak" -ForegroundColor Green

Write-Host "`n=== BUILD COMPLETE - Restart server and test ===" -ForegroundColor Cyan