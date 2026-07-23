-- ShopSystem.lua
-- Manages NPC shops and the premium Robux shop

local ShopSystem = {}

local SHOPS = {
	GeneralStore = {
		name = "General Store",
		npc = "ShopkeeperTown",
		inventory = {
			{ itemId = "HealthPotionSmall", name = "Small Health Potion", price = 20, restores = "health", amount = 30 },
			{ itemId = "HealthPotionMed", name = "Medium Health Potion", price = 50, restores = "health", amount = 75 },
			{ itemId = "ManaPotionSmall", name = "Small Mana Potion", price = 20, restores = "mana", amount = 30 },
		}
	},
	WeaponSmith = {
		name = "Weapon Smith",
		npc = "WeaponsmithNpc",
		inventory = {
			{ itemId = "IronSword", name = "Iron Sword", price = 45, damage = 12 },
			{ itemId = "SteelGreatsword", name = "Steel Greatsword", price = 150, damage = 26 },
		}
	},
	ArmorSmith = {
		name = "Armor Smith",
		npc = "ArmorsmithNpc",
		inventory = {
			{ itemId = "LeatherArmor", name = "Leather Armor", price = 50, defense = 8 },
			{ itemId = "SteelPlate", name = "Steel Plate Armor", price = 250, defense = 22 },
		}
	}
}

local PREMIUM_SHOP = {
	{
		productId = 1,
		name = "Dracon Knight Skin",
		description = "Exclusive character skin",
		robuxtPrice = 400,
		type = "cosmetic",
		category = "skins"
	},
	{
		productId = 2,
		name = "Dragon Fang Blade",
		description = "Legendary weapon (1 week)",
		robuxtPrice = 800,
		type = "weapon",
		duration = 604800 -- 1 week in seconds
	},
	{
		productId = 3,
		name = "XP Booster (1 Hour)",
		description = "2x experience for 1 hour",
		robuxtPrice = 100,
		type = "booster",
		duration = 3600
	},
	{
		productId = 4,
		name = "XP Booster (24 Hours)",
		description = "2x experience for 24 hours",
		robuxtPrice = 300,
		type = "booster",
		duration = 86400
	},
	{
		productId = 5,
		name = "Battle Pass - Season 1",
		description = "Exclusive seasonal rewards",
		robuxtPrice = 500,
		type = "battle_pass",
		season = 1
	},
	{
		productId = 6,
		name = "Inventory Expansion",
		description = "Increase inventory slots by 10",
		robuxtPrice = 200,
		type = "expansion",
		slots = 10
	},
	{
		productId = 7,
		name = "Fire Mage Skin",
		description = "Exclusive character skin",
		robuxtPrice = 350,
		type = "cosmetic",
		category = "skins"
	},
	{
		productId = 8,
		name = "Ice Wizard Skin",
		description = "Exclusive character skin",
		robuxtPrice = 350,
		type = "cosmetic",
		category = "skins"
	}
}

local ShopClass = {}
ShopClass.__index = ShopClass

function ShopClass:new(shopName)
	local self = setmetatable({}, ShopClass)
	self.shop = SHOPS[shopName]
	self.name = self.shop.name
	self.inventory = self.shop.inventory
	return self
end

function ShopClass:GetInventory()
	return self.inventory
end

function ShopClass:BuyItem(player, itemIndex)
	if itemIndex < 1 or itemIndex > #self.inventory then
		return false, "Invalid item"
	end
	
	local item = self.inventory[itemIndex]
	
	if player.character.gold < item.price then
		return false, "Not enough gold"
	end
	
	-- Deduct gold and add item to inventory
	player.character.gold = player.character.gold - item.price
	table.insert(player.character.inventory, item)
	
	return true, "Purchase successful"
end

function ShopClass:SellItem(player, inventoryIndex)
	if inventoryIndex < 1 or inventoryIndex > #player.character.inventory then
		return false, "Invalid item"
	end
	
	local item = player.character.inventory[inventoryIndex]
	local sellPrice = math.floor(item.price / 2)
	
	player.character.gold = player.character.gold + sellPrice
	table.remove(player.character.inventory, inventoryIndex)
	
	return true, "Sold for " .. sellPrice .. " gold"
end

function ShopSystem:CreateShop(shopName)
	return ShopClass:new(shopName)
end

function ShopSystem:GetShops()
	return SHOPS
end

function ShopSystem:GetPremiumShop()
	return PREMIUM_SHOP
end

function ShopSystem:GetPremiumItem(productId)
	for _, item in ipairs(PREMIUM_SHOP) do
		if item.productId == productId then
			return item
		end
	end
	return nil
end

return ShopSystem
