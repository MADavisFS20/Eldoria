-- PlayerManager.lua
-- Manages player creation, stats, progression, and equipment

local PlayerManager = {}

local CLASS_DEFINITIONS = {
	Warrior = {
		name = "Warrior",
		description = "Strong melee fighter",
		str_base = 15,
		dex_base = 10,
		int_base = 8,
		con_base = 14,
		wis_base = 9,
		startingWeapon = "IronSword",
		startingArmor = "LeatherArmor"
	},
	Rogue = {
		name = "Rogue",
		description = "Swift and deadly striker",
		str_base = 11,
		dex_base = 16,
		int_base = 10,
		con_base = 11,
		wis_base = 10,
		startingWeapon = "RustyDagger",
		startingArmor = "LeatherArmor"
	},
	Mage = {
		name = "Mage",
		description = "Master of arcane magic",
		str_base = 8,
		dex_base = 11,
		int_base = 16,
		con_base = 9,
		wis_base = 13,
		startingWeapon = "ApprenticeStaff",
		startingArmor = "ClothRobe"
	},
	Paladin = {
		name = "Paladin",
		description = "Holy defender",
		str_base = 13,
		dex_base = 10,
		int_base = 10,
		con_base = 15,
		wis_base = 14,
		startingWeapon = "IronSword",
		startingArmor = "LeatherArmor"
	},
	Ranger = {
		name = "Ranger",
		description = "Skilled archer and tracker",
		str_base = 12,
		dex_base = 15,
		int_base = 11,
		con_base = 12,
		wis_base = 12,
		startingWeapon = "RustyDagger",
		startingArmor = "LeatherArmor"
	}
}

local ITEMS_DATABASE = {
	Weapons = {
		IronSword = { name = "Iron Sword", damage = 12, rarity = "common", value = 45 },
		RustyDagger = { name = "Rusty Dagger", damage = 6, rarity = "common", value = 10 },
		ApprenticeStaff = { name = "Apprentice Staff", damage = 8, rarity = "common", value = 60 },
		DragonFangBlade = { name = "Dragon Fang Blade", damage = 45, rarity = "legendary", value = 750, premium = true },
		RunicWarhammer = { name = "Runic Warhammer", damage = 34, rarity = "rare", value = 300 }
	},
	Armor = {
		LeatherArmor = { name = "Leather Armor", defense = 8, rarity = "common", value = 50 },
		ClothRobe = { name = "Cloth Robe", defense = 2, rarity = "common", value = 15 },
		SteelPlate = { name = "Steel Plate Armor", defense = 22, rarity = "rare", value = 250 },
		DragonscaleArmor = { name = "Dragonscale Armor", defense = 35, rarity = "legendary", value = 850, premium = true }
	},
	Accessories = {
		RingOfPower = { name = "Ring of Power", atk_bonus = 6, rarity = "rare", value = 150 },
		RingOfVitality = { name = "Ring of Vitality", hp_bonus = 30, rarity = "rare", value = 100 },
		AmuletOfArcana = { name = "Amulet of Arcana", mp_bonus = 40, rarity = "rare", value = 120 }
	}
}

local PlayerClass = {}
PlayerClass.__index = PlayerClass

function PlayerClass:new(player, playerData)
	local self = setmetatable({}, PlayerClass)
	
	self.userId = player.UserId
	self.playerName = player.Name
	self.account = player
	
	-- Load or create character data
	if playerData then
		self:LoadData(playerData)
	else
		self:InitializeNewCharacter()
	end
	
	return self
end

function PlayerClass:InitializeNewCharacter(className, characterName)
	local classData = CLASS_DEFINITIONS[className or "Warrior"]
	
	self.character = {
		name = characterName or (self.playerName .. "'s Hero"),
		class = className or "Warrior",
		level = 1,
		experience = 0,
		experienceToNext = 100,
		gold = 100,
		
		-- Attributes
		strength = classData.str_base,
		dexterity = classData.dex_base,
		intelligence = classData.int_base,
		constitution = classData.con_base,
		wisdom = classData.wis_base,
		
		-- Pools
		maxHealth = 80 + (classData.con_base * 12),
		currentHealth = 0,
		maxMagicka = 40 + (classData.int_base * 10) + (classData.wis_base * 5),
		currentMagicka = 0,
		maxStamina = 50 + (classData.dex_base * 8) + (classData.con_base * 4),
		currentStamina = 0,
		
		-- Points
		attributePoints = 0,
		perkPoints = 0,
		
		-- Equipment
		equipment = {
			weapon = "IronSword",
			armor = "LeatherArmor",
			ring = nil,
			amulet = nil
		},
		
		-- Inventory
		inventory = {},
		
		-- Perks
		perks = {
			critical_strike = 0,
			spell_power = 0,
			iron_skin = 0,
			mana_efficiency = 0
		}
	}
	
	-- Initialize current pools
	self.character.currentHealth = self.character.maxHealth
	self.character.currentMagicka = self.character.maxMagicka
	self.character.currentStamina = self.character.maxStamina
end

function PlayerClass:LoadData(playerData)
	self.character = playerData
end

function PlayerClass:AddExperience(amount)
	self.character.experience = self.character.experience + amount
	
	if self.character.experience >= self.character.experienceToNext then
		self:LevelUp()
	end
end

function PlayerClass:LevelUp()
	self.character.level = self.character.level + 1
	self.character.experience = self.character.experience - self.character.experienceToNext
	self.character.experienceToNext = math.floor(self.character.experienceToNext * 1.4)
	self.character.attributePoints = self.character.attributePoints + 3
	self.character.perkPoints = self.character.perkPoints + 1
	
	-- Recalculate stats
	self:RecalculateStats()
	
	-- Restore pools
	self.character.currentHealth = self.character.maxHealth
	self.character.currentMagicka = self.character.maxMagicka
	self.character.currentStamina = self.character.maxStamina
end

function PlayerClass:RecalculateStats()
	local con = self.character.constitution
	local int = self.character.intelligence
	local wis = self.character.wisdom
	local dex = self.character.dexterity
	
	self.character.maxHealth = 80 + (con * 12)
	self.character.maxMagicka = 40 + (int * 10) + (wis * 5)
	self.character.maxStamina = 50 + (dex * 8) + (con * 4)
end

function PlayerClass:GetTotalAttack()
	local str = self.character.strength
	local dex = self.character.dexterity
	local baseAtk = str * 1.5 + (dex * 0.8)
	
	local weapon = ITEMS_DATABASE.Weapons[self.character.equipment.weapon]
	local weaponDmg = weapon and weapon.damage or 0
	
	local ringBonus = 0
	if self.character.equipment.ring then
		local ring = ITEMS_DATABASE.Accessories[self.character.equipment.ring]
		ringBonus = ring and ring.atk_bonus or 0
	end
	
	local perkBonus = self.character.perks.critical_strike * 3
	
	return math.floor(baseAtk + weaponDmg + ringBonus + perkBonus)
end

function PlayerClass:GetTotalDefense()
	local con = self.character.constitution
	local baseDef = con * 0.5
	
	local armor = ITEMS_DATABASE.Armor[self.character.equipment.armor]
	local armorDef = armor and armor.defense or 0
	
	local ringBonus = 0
	if self.character.equipment.ring then
		local ring = ITEMS_DATABASE.Accessories[self.character.equipment.ring]
		ringBonus = ring and (ring.atk_bonus and 0 or 0) or 0 -- Add def_bonus if available
	end
	
	local perkBonus = self.character.perks.iron_skin * 4
	
	return math.floor(baseDef + armorDef + ringBonus + perkBonus)
end

function PlayerClass:TakeDamage(damage)
	local actualDamage = math.max(1, damage - self:GetTotalDefense())
	self.character.currentHealth = math.max(0, self.character.currentHealth - actualDamage)
	return actualDamage
end

function PlayerClass:IsAlive()
	return self.character.currentHealth > 0
end

function PlayerClass:Serialize()
	return self.character
end

function PlayerManager:CreatePlayer(player, playerData)
	return PlayerClass:new(player, playerData)
end

function PlayerManager:GetClassDefinitions()
	return CLASS_DEFINITIONS
end

function PlayerManager:GetItemsDatabase()
	return ITEMS_DATABASE
end

return PlayerManager
