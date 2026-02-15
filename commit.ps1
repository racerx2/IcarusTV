cd C:\IcarusTV
git config user.email "racerx708@gmail.com"
git config user.name "RacerX"

# Remove temp scripts
Remove-Item 'C:\IcarusTV\do_commit.ps1' -Force -ErrorAction SilentlyContinue
Remove-Item 'C:\IcarusTV\gitinit.ps1' -Force -ErrorAction SilentlyContinue
git add -A

git commit -m "Icarus TV Mod - deployable flat-screen TV with IPTV streaming

Full UE4 4.27.2 mod project with:
- Wall-mounted 55in TV blueprint with MediaPlayer streaming
- C++ stubs for proper FName preservation and parent class overrides
- BytecodeMod post-cook Super reference fixer (UAssetAPI)
- Icarus Relay Server (Python/FFmpeg) for IPTV and local media
- Complete data table entries for crafting, tech tree, and deployment
- Automated build pipeline (cook -> fix -> pak -> deploy)

Built by RacerX"
