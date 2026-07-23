-- WorldSystem.lua
-- Manages game world, locations, NPCs, and encounters

local WorldSystem = {}

local LOCATIONS = {
	Oakhaven = {
		name = "Oakhaven Village",
		description = "A peaceful village at the edge of Eldoria",
		type = "village",
		npcs = {"Blacksmith", "Innkeeper", "Merchant"},
		encounters = {
			{enemyType = "Goblin", chance = 0.3},
			{enemyType = "Orc", chance = 0.1}
		},
		connections = {north = "ForestPath", east = "MountainBase"}
	},
	ForestPath = {
		name = "Dark Forest",
		description = "A dense forest filled with danger and mystery",
		type = "dungeon",
		npcs = {"WoodElfScout"},
		encounters = {
			{enemyType = "Goblin", chance = 0.5},
			{enemyType = "Orc", chance = 0.3},
			{enemyType = "Dragon", chance = 0.05}
		},
		connections = {south = "Oakhaven", east = "AncientRuins"}
	},
	MountainBase = {
		name = "Mountain Base",
		description = "The foot of a towering mountain",
		type = "wilderness",
		npcs = {"MountainClimber"},
		encounters = {
			{enemyType = "Orc", chance = 0.4},
			{enemyType = "Dragon", chance = 0.1}
		},
		connections = {west = "Oakhaven", north = "MountainPeak"}
	},
	MountainPeak = {
		name = "Mountain Peak",
		description = "The summit of the great mountain. A dragon's lair?",
		type = "boss_arena",
		npcs = {},
		encounters = {
			{enemyType = "Dragon", chance = 1.0}
		},
		connections = {south = "MountainBase"}
	},
	AncientRuins = {
		name = "Ancient Ruins",
		description = "Crumbling structures from a forgotten civilization",
		type = "dungeon",
		npcs = {"RuneArchivist"},
		encounters = {
			{enemyType = "Orc", chance = 0.4},
			{enemyType = "Dragon", chance = 0.15}
		},
		connections = {west = "ForestPath", south = "CrystalCavern"}
	},
	CrystalCavern = {
		name = "Crystal Cavern",
		description = "A glowing cavern filled with magical crystals",
		type = "dungeon",
		npcs = {"CrystalMage"},
		encounters = {
			{enemyType = "Goblin", chance = 0.2},
			{enemyType = "Orc", chance = 0.5},
			{enemyType = "Dragon", chance = 0.2}
		},
		connections = {north = "AncientRuins"}
	}
}

local NPCs = {
	Blacksmith = {
		name = "Gorwin the Blacksmith",
		description = "A skilled weaponsmith",
		dialogue = "Need a weapon? I've got the finest blades in Eldoria!",
		shopType = "WeaponSmith",
		location = "Oakhaven"
	},
	Innkeeper = {
		name = "Elara the Innkeeper",
		description = "Runs the local tavern",
		dialogue = "Welcome, traveler! Let me heal your wounds.",
		shopType = "GeneralStore",
		location = "Oakhaven"
	},
	Merchant = {
		name = "Zax the Merchant",
		description = "A traveling merchant",
		dialogue = "I've got rare goods from across the realm!",
		shopType = "GeneralStore",
		location = "Oakhaven"
	},
	WoodElfScout = {
		name = "Aelith the Scout",
		description = "A wood elf ranger",
		dialogue = "Beware of goblins in these woods. Stay sharp!",
		shopType = nil,
		location = "ForestPath",
		quests = {"GoblinInfestation"}
	},
	MountainClimber = {
		name = "Thorne the Climber",
		description = "An experienced mountain guide",
		dialogue = "The peak calls to only the strongest adventurers.",
		shopType = nil,
		location = "MountainBase",
		quests = {"ConquerThePeak"}
	},
	RuneArchivist = {
		name = "Lysander the Archivist",
		description = "An ancient scholar",
		dialogue = "These ruins hold secrets of forgotten magic.",
		shopType = nil,
		location = "AncientRuins",
		quests = {"LostKnowledge"}
	},
	CrystalMage = {
		name = "Sylla the Crystal Mage",
		description = "A master of crystal magic",
		dialogue = "The crystals here pulse with ancient power.",
		shopType = "ArmorSmith",
		location = "CrystalCavern"
	}
}

local QUESTS = {
	GoblinInfestation = {
		id = "goblin_infestation",
		name = "The Goblin Infestation",
		description = "Clear out the goblin nest in the forest",
		quester = "Aelith",
		target = "Defeat 5 Goblins",
		targetCount = 5,
		reward_xp = 100,
		reward_gold = 50
	},
	ConquerThePeak = {
		id = "conquer_peak",
		name = "Conquer the Peak",
		description = "Defeat the dragon atop the mountain",
		quester = "Thorne",
		target = "Defeat the Mountain Dragon",
		targetCount = 1,
		reward_xp = 500,
		reward_gold = 250,
		reward_item = "DragonScale"
	},
	LostKnowledge = {
		id = "lost_knowledge",
		name = "Lost Knowledge",
		description = "Recover the ancient tome from the ruins",
		quester = "Lysander",
		target = "Find the Ancient Tome",
		targetCount = 1,
		reward_xp = 150,
		reward_gold = 75
	}
}

function WorldSystem:GetLocations()
	return LOCATIONS
end

function WorldSystem:GetLocation(locationName)
	return LOCATIONS[locationName]
end

function WorldSystem:GetNPCs()
	return NPCs
end

function WorldSystem:GetNPC(npcName)
	return NPCs[npcName]
end

function WorldSystem:GetQuests()
	return QUESTS
end

function WorldSystem:GetQuest(questId)
	for _, quest in pairs(QUESTS) do
		if quest.id == questId then
			return quest
		end
	end
	return nil
end

function WorldSystem:GetNPCsInLocation(locationName)
	local location = LOCATIONS[locationName]
	if not location then return {} end
	
	local npcsInLocation = {}
	for _, npcName in ipairs(location.npcs) do
		table.insert(npcsInLocation, NPCs[npcName])
	end
	
	return npcsInLocation
end

function WorldSystem:GetEncounterInLocation(locationName)
	local location = LOCATIONS[locationName]
	if not location or #location.encounters == 0 then return nil end
	
	local roll = math.random()
	local cumulativeChance = 0
	
	for _, encounter in ipairs(location.encounters) do
		cumulativeChance = cumulativeChance + encounter.chance
		if roll <= cumulativeChance then
			return encounter.enemyType
		end
	end
	
	return nil
end

return WorldSystem
