-- AchievementSystem.lua
-- Manages player achievements and badges

local AchievementSystem = {}

local ACHIEVEMENTS = {
	FirstBlood = {
		id = "first_blood",
		name = "First Blood",
		description = "Defeat your first enemy",
		rarity = "common",
		reward_xp = 50
	},
	GoblinSlayer = {
		id = "goblin_slayer",
		name = "Goblin Slayer",
		description = "Defeat 10 goblins",
		rarity = "rare",
		reward_xp = 200
	},
	DragonSlayer = {
		id = "dragon_slayer",
		name = "Dragon Slayer",
		description = "Defeat a dragon",
		rarity = "legendary",
		reward_xp = 500
	},
	QuestMaster = {
		id = "quest_master",
		name = "Quest Master",
		description = "Complete 10 quests",
		rarity = "epic",
		reward_xp = 300
	},
	LevelUp = {
		id = "level_up",
		name = "Rising Star",
		description = "Reach level 10",
		rarity = "common",
		reward_xp = 100
	},
	RichPerson = {
		id = "rich_person",
		name = "Wealthy Adventurer",
		description = "Accumulate 1000 gold",
		rarity = "rare",
		reward_xp = 150
	},
	Equipmaster = {
		id = "equipment_master",
		name = "Equipment Master",
		description = "Equip a full legendary set",
		rarity = "epic",
		reward_xp = 250
	},
	CosmeticCollector = {
		id = "cosmetic_collector",
		name = "Cosmetic Collector",
		description = "Unlock 5 cosmetic items",
		rarity = "rare",
		reward_xp = 200
	}
}

local PlayerAchievementClass = {}
PlayerAchievementClass.__index = PlayerAchievementClass

function PlayerAchievementClass:new()
	local self = setmetatable({}, PlayerAchievementClass)
	self.unlockedAchievements = {}
	self.achievementProgress = {}
	return self
end

function PlayerAchievementClass:UnlockAchievement(achievementId)
	if self.unlockedAchievements[achievementId] then
		return false, "Already unlocked"
	end
	
	local achievement = ACHIEVEMENTS[achievementId]
	if not achievement then return false, "Achievement not found" end
	
	self.unlockedAchievements[achievementId] = {
		id = achievementId,
		unlockedAt = os.time()
	}
	
	return true, "Achievement unlocked: " .. achievement.name
end

function PlayerAchievementClass:UpdateProgress(achievementId, currentProgress, maxProgress)
	self.achievementProgress[achievementId] = {
		current = currentProgress,
		max = maxProgress,
		percentage = (currentProgress / maxProgress) * 100
	}
	
	if currentProgress >= maxProgress then
		return self:UnlockAchievement(achievementId)
	end
end

function PlayerAchievementClass:GetUnlockedAchievements()
	return self.unlockedAchievements
end

function PlayerAchievementClass:GetUnlockedCount()
	local count = 0
	for _ in pairs(self.unlockedAchievements) do
		count = count + 1
	end
	return count
end

function AchievementSystem:GetAllAchievements()
	return ACHIEVEMENTS
end

function AchievementSystem:GetAchievement(achievementId)
	return ACHIEVEMENTS[achievementId]
end

function AchievementSystem:CreateAchievementTracker()
	return PlayerAchievementClass:new()
end

return AchievementSystem
