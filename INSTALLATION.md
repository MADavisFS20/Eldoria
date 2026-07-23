# Eldoria Roblox - Installation Guide

## Prerequisites

- Roblox Studio installed
- Creator account on Roblox
- Basic Lua knowledge (optional)

## Step 1: Setup Roblox Place

1. Open Roblox Studio
2. Create a new **Baseplate** template
3. Save the place as "Eldoria RPG"

## Step 2: Install Files

1. Copy the contents of the `Roblox/` folder into your game:
   - **ServerScriptService** → Scripts
   - **StarterPlayer** → Character/GUI
   - **ReplicatedStorage** → Shared modules

2. In **ReplicatedStorage**, create a folder named `Modules` and copy all Lua files there

## Step 3: Create Folder Structure

### In ServerScriptService:
- [ ] GameManager.server.lua
- [ ] MarketplaceManager.lua

### In ReplicatedStorage:
- [ ] Create folder: `Modules`
  - [ ] PlayerManager.lua
  - [ ] CombatSystem.lua
  - [ ] ShopSystem.lua
  - [ ] PersistenceManager.lua
  - [ ] UIManager.lua
  - [ ] PremiumShopUI.lua
- [ ] Create folder: `Events`
  - Run the Events/Create.lua script to auto-generate RemoteEvents

### In StarterPlayer > StarterCharacterScripts:
- [ ] CharacterSetup.lua

### In StarterPlayer > StarterGui:
- [ ] MainUIHandler.lua

## Step 4: Configure Settings

### Game Settings
1. File > Game Settings
2. Set **Allow HttpGet** to ON (for future features)
3. Enable **Load Model Asynchronously**

### Physics
1. Home > Physics > Set gravity to 196.2

## Step 5: Test the Game

1. Click **Play** button
2. You should see the main menu
3. Test:
   - [ ] New Game button
   - [ ] Character creation
   - [ ] Premium shop access

## Step 6: Configure Monetization

See `MONETIZATION.md` for:
- Creating products in Creator Hub
- Setting up Robux prices
- Configuring MarketplaceManager product IDs

## Step 7: Publish

1. File > Publish As...
2. Set name and description
3. Click **Create**
4. Share the link with players!

## Troubleshooting

### Scripts not running?
- Check Output window (View > Output) for errors
- Ensure scripts are in correct locations
- Verify all modules are in ReplicatedStorage/Modules

### UI not appearing?
- Check StarterGui scripts
- Verify Events are created
- Check player.PlayerGui access

### Purchases not working?
- Verify product IDs in MarketplaceManager.lua
- Check Creator Hub for product setup
- Review MarketplaceService documentation

## Next Steps

1. Add NPC characters
2. Create world map with locations
3. Add combat encounters
4. Balance game difficulty
5. Test with friends
6. Gather feedback and iterate
