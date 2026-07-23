-- CosmeticSystem.lua
-- Manages player cosmetics and appearance customization

local CosmeticSystem = {}
local CosmeticSystem_mt = {__index = CosmeticSystem}

local COSMETICS = {
	Skins = {
		DraconKnight = {
			id = "dracon_knight",
			name = "Dracon Knight Skin",
			description = "An armored warrior blessed by dragons",
			rarity = "legendary",
			price = 400,
			currency = "Robux",
			colorPrimary = Color3.fromRGB(139, 0, 139),
			colorSecondary = Color3.fromRGB(255, 215, 0)
		},
		FireMage = {
			id = "fire_mage",
			name = "Fire Mage Skin",
			description = "A master of flame magic",
			rarity = "epic",
			price = 350,
			currency = "Robux",
			colorPrimary = Color3.fromRGB(255, 69, 0),
			colorSecondary = Color3.fromRGB(255, 140, 0)
		},
		IceWizard = {
			id = "ice_wizard",
			name = "Ice Wizard Skin",
			description = "A wielder of arctic magic",
			rarity = "epic",
			price = 350,
			currency = "Robux",
			colorPrimary = Color3.fromRGB(30, 144, 255),
			colorSecondary = Color3.fromRGB(173, 216, 230)
		},
		ShadowAssassin = {
			id = "shadow_assassin",
			name = "Shadow Assassin Skin",
			description = "A master of darkness",
			rarity = "rare",
			price = 300,
			currency = "Robux",
			colorPrimary = Color3.fromRGB(25, 25, 112),
			colorSecondary = Color3.fromRGB(128, 128, 128)
		}
	},
	WeaponSkins = {
		FlameTongue = {
			id = "flame_tongue",
			name = "Flame Tongue Weapon Skin",
			description = "Weapon trails with fire",
			rarity = "epic",
			price = 250,
			currency = "Robux"
		},
		Frostbite = {
			id = "frostbite",
			name = "Frostbite Weapon Skin",
			description = "Weapon trails with ice",
			rarity = "epic",
			price = 250,
			currency = "Robux"
		}
	},
	Emotes = {
		VictoryDance = {
			id = "victory_dance",
			name = "Victory Dance",
			description = "Celebrate your wins!",
			rarity = "rare",
			price = 150,
			currency = "Robux"
		},
		PowerPose = {
			id = "power_pose",
			name = "Power Pose",
			description = "Show your strength",
			rarity = "rare",
			price = 150,
			currency = "Robux"
		}
	}
}

local PlayerCosmeticClass = {}
PlayerCosmeticClass.__index = PlayerCosmeticClass

function PlayerCosmeticClass:new()
	local self = setmetatable({}, PlayerCosmeticClass)
	self.ownedCosmetics = {}
	self.equippedSkin = nil
	self.equippedWeaponSkin = nil
	self.equippedEmotes = {}
	return self
end

function PlayerCosmeticClass:UnlockCosmetic(cosmeticId, category)
	local cosmetic = COSMETICS[category] and COSMETICS[category][cosmeticId]
	if not cosmetic then return false, "Cosmetic not found" end
	
	if self.ownedCosmetics[cosmeticId] then
		return false, "Already own this cosmetic"
	end
	
	self.ownedCosmetics[cosmeticId] = {
		id = cosmeticId,
		category = category,
		unlockedAt = os.time()
	}
	
	return true, "Unlocked " .. cosmetic.name
end

function PlayerCosmeticClass:EquipSkin(skinId)
	if not COSMETICS.Skins[skinId] then return false, "Skin not found" end
	if not self.ownedCosmetics[skinId] then return false, "Don't own this skin" end
	
	self.equippedSkin = skinId
	return true, "Equipped " .. COSMETICS.Skins[skinId].name
end

function PlayerCosmeticClass:EquipWeaponSkin(skinId)
	if not COSMETICS.WeaponSkins[skinId] then return false, "Weapon skin not found" end
	if not self.ownedCosmetics[skinId] then return false, "Don't own this skin" end
	
	self.equippedWeaponSkin = skinId
	return true, "Equipped " .. COSMETICS.WeaponSkins[skinId].name
end

function PlayerCosmeticClass:GetOwnedCosmetics()
	return self.ownedCosmetics
end

function PlayerCosmeticClass:GetEquippedCosmetics()
	return {
		skin = self.equippedSkin,
		weaponSkin = self.equippedWeaponSkin,
		emotes = self.equippedEmotes
	}
end

function CosmeticSystem:GetAllCosmetics()
	return COSMETICS
end

function CosmeticSystem:GetCosmeticsByCategory(category)
	return COSMETICS[category] or {}
end

function CosmeticSystem:CreateCosmeticManager()
	return PlayerCosmeticClass:new()
end

function CosmeticSystem:GetCosmetic(cosmeticId, category)
	if category then
		return COSMETICS[category] and COSMETICS[category][cosmeticId]
	else
		for cat, cosmetics in pairs(COSMETICS) do
			if cosmetics[cosmeticId] then
				return cosmetics[cosmeticId]
			end
		end
	end
	return nil
end

return CosmeticSystem
