# Eldoria Roblox - Monetization Guide

## Premium Shop Items

The game includes a premium shop with cosmetics, weapons, boosts, and battle pass items purchasable with Robux.

### Setting Up Products

1. **Go to Roblox Creator Hub** - https://create.roblox.com
2. **Select Your Game** - Choose the Eldoria game
3. **Navigate to Monetization > Products**
4. **Create New Products** with the following details:

#### Cosmetics (Skins)
- **Dracon Knight Skin** - 400 Robux
- **Fire Mage Skin** - 350 Robux
- **Ice Wizard Skin** - 350 Robux

#### Weapons
- **Dragon Fang Blade (1 Week)** - 800 Robux
- **Runic Warhammer** - 600 Robux

#### Boosts
- **XP Booster (1 Hour)** - 100 Robux
- **XP Booster (24 Hours)** - 300 Robux

#### Battle Pass
- **Battle Pass - Season 1** - 500 Robux
- **Battle Pass - Season 2** - 500 Robux

#### Other
- **Inventory Expansion** - 200 Robux
- **Extra Character Slot** - 250 Robux

### Updating Product IDs

After creating products in Creator Hub:

1. Copy the Product ID from Creator Hub
2. Open `Roblox/ServerScriptService/MarketplaceManager.lua`
3. Replace the `PRODUCT_IDS` table values with your actual IDs

**Example:**
```lua
local PRODUCT_IDS = {
    DRACON_KNIGHT_SKIN = 12345678,
    FIREPAGE_SKIN = 12345679,
    -- ... etc
}
```

### Revenue Sharing

- Roblox takes 30% of Robux sales
- You receive 70% of the revenue
- Payments distributed monthly to your bank account

## Game Pass (Optional)

For recurring revenue, create a Game Pass:

1. In Creator Hub, go to Monetization > Game Passes
2. Create a VIP Pass (e.g., "VIP Premium" - 199 Robux/month)
3. Benefits could include:
   - 1.5x XP gain
   - Weekly Robux stipend (optional)
   - Exclusive cosmetics
   - Access to premium events

## Ad Revenue

Enable in-game ads:

1. Creator Hub > Monetization > Ads
2. Enable ad platforms (YouTube, TikTok, etc.)
3. Players earn small Robux rewards for watching ads

## Analytics

Track monetization performance:

1. Creator Hub > Analytics > Revenue
2. Monitor:
   - Daily/Monthly revenue
   - Top-selling items
   - Player conversion rates
   - Average revenue per user (ARPU)

## Best Practices

1. **Balance** - Don't make premium items too powerful (P2W)
2. **Regular Updates** - Add new cosmetics/items regularly
3. **Fair Pricing** - Price similar to other Roblox games
4. **Transparency** - Clearly display what players get
5. **Battle Pass** - Offer both free and paid tiers
6. **Limited-Time Items** - Create urgency with seasonal items

## Anti-Exploit Measures

- Validate all purchases on server-side
- Use DataStore with proper security
- Implement rate limiting on transactions
- Log all purchases for audit trails
- Regular backups of player data
