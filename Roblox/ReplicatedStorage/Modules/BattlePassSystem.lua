-- BattlePassSystem.lua
-- Manages seasonal battle pass progression and rewards

local BattlePassSystem = {}
local BattlePassSystem_mt = {__index = BattlePassSystem}

local SEASONS = {
	Season1 = {
		name = "Season 1: Rise of Heroes",
		number = 1,
		description = "The first season of Eldoria",
		startDate = 1719100800, -- July 23, 2026
		endDate = 1726876800, -- September 21, 2026
		maxLevel = 100,
		passes = {
			Free = {
				name = "Free Pass",
				price = 0,
				rewards = {
					{level = 10, reward = "300 Gold"},
					{level = 25, reward = "Iron Sword"},
					{level = 50, reward = "500 Gold"},
					{level = 75, reward = "Steel Plate Armor"}
				}
			},
			Premium = {
				name = "Premium Pass",
				price = 500,
				currency = "Robux",
				rewards = {
					{level = 5, reward = "Dracon Knight Skin"},
					{level = 15, reward = "1000 Gold"},
					{level = 30, reward = "Dragon Fang Blade (1 week)"},
					{level = 50, reward = "Ring of Power"},
					{level = 75, reward = "Dragonscale Armor (1 week)"},
					{level = 100, reward = "Legendary Dragon Helmet"}
				}
			}
		}
	},
	Season2 = {
		name = "Season 2: Shadows Rise",
		number = 2,
		description = "The second season brings new challenges",
		startDate = 1726876800, -- September 21, 2026
		endDate = 1734652800, -- December 20, 2026
		maxLevel = 100,
		passes = {
			Free = {
				name = "Free Pass",
				price = 0,
				rewards = {
					{level = 10, reward = "300 Gold"},
					{level = 30, reward = "Fire Mage Skin"},
					{level = 60, reward = "1000 Gold"}
				}
			},
			Premium = {
				name = "Premium Pass",
				price = 500,
				currency = "Robux",
				rewards = {
					{level = 1, reward = "Ice Wizard Skin"},
					{level = 20, reward = "Runic Warhammer (1 week)"},
					{level = 100, reward = "Eternal Crown"}
				}
			}
		}
	}
}

local PlayerBattlePassClass = {}
PlayerBattlePassClass.__index = PlayerBattlePassClass

function PlayerBattlePassClass:new()
	local self = setmetatable({}, PlayerBattlePassClass)
	self.currentSeason = 1
	self.level = 1
	self.experience = 0
	self.experienceToNextLevel = 1000
	self.activePasses = {} -- {freePass = bool, premiumPass = bool}
	self.claimedRewards = {}
	return self
end

function PlayerBattlePassClass:PurchasePremiumPass(seasonNumber)
	local season = SEASONS["Season" .. seasonNumber]
	if not season then return false, "Season not found" end
	
	if self.activePasses[seasonNumber] and self.activePasses[seasonNumber].premium then
		return false, "Already own premium pass for this season"
	end
	
	self.activePasses[seasonNumber] = self.activePasses[seasonNumber] or {}
	self.activePasses[seasonNumber].premium = true
	self.activePasses[seasonNumber].purchasedAt = os.time()
	
	return true, "Premium pass purchased!"
end

function PlayerBattlePassClass:AddExperience(amount)
	self.experience = self.experience + amount
	
	while self.experience >= self.experienceToNextLevel do
		self:LevelUp()
	end
end

function PlayerBattlePassClass:LevelUp()
	self.level = self.level + 1
	self.experience = self.experience - self.experienceToNextLevel
	self.experienceToNextLevel = math.floor(self.experienceToNextLevel * 1.1)
end

function PlayerBattlePassClass:ClaimReward(seasonNumber, level)
	local season = SEASONS["Season" .. seasonNumber]
	if not season then return false, "Season not found" end
	
	if level > self.level then return false, "Level requirement not met" end
	
	local rewardKey = seasonNumber .. "_" .. level
	if self.claimedRewards[rewardKey] then
		return false, "Reward already claimed"
	end
	
	self.claimedRewards[rewardKey] = true
	
	return true, "Reward claimed!"
end

function PlayerBattlePassClass:GetCurrentLevel()
	return self.level
end

function PlayerBattlePassClass:GetExperienceProgress()
	return {
		current = self.experience,
		required = self.experienceToNextLevel,
		percentage = (self.experience / self.experienceToNextLevel) * 100
	}
end

function PlayerBattlePassClass:HasPremiumPass(seasonNumber)
	if not self.activePasses[seasonNumber] then return false end
	return self.activePasses[seasonNumber].premium or false
end

function BattlePassSystem:CreateBattlePass()
	return PlayerBattlePassClass:new()
end

function BattlePassSystem:GetSeasons()
	return SEASONS
end

function BattlePassSystem:GetSeason(seasonNumber)
	return SEASONS["Season" .. seasonNumber]
end

function BattlePassSystem:GetCurrentSeason()
	local currentTime = os.time()
	for seasonKey, season in pairs(SEASONS) do
		if currentTime >= season.startDate and currentTime <= season.endDate then
			return season, season.number
		end
	end
	
	-- Return latest season if current time doesn't match any
	return SEASONS.Season2, 2
end

return BattlePassSystem
