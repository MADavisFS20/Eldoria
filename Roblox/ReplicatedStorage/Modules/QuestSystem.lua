-- QuestSystem.lua
-- Manages player quests, progression, and rewards

local QuestSystem = {}
local QuestSystem_mt = {__index = QuestSystem}

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Modules = ReplicatedStorage:WaitForChild("Modules")
local WorldSystem = require(Modules:WaitForChild("WorldSystem"))

local PlayerQuestClass = {}
PlayerQuestClass.__index = PlayerQuestClass

function PlayerQuestClass:new()
	local self = setmetatable({}, PlayerQuestClass)
	self.activeQuests = {}
	self.completedQuests = {}
	self.questProgress = {}
	return self
end

function PlayerQuestClass:AcceptQuest(questId)
	local quest = WorldSystem:GetQuest(questId)
	if not quest then return false, "Quest not found" end
	
	-- Check if already accepted
	if self.activeQuests[questId] then
		return false, "Quest already accepted"
	end
	
	-- Check if already completed
	if self.completedQuests[questId] then
		return false, "Quest already completed"
	end
	
	-- Accept quest
	self.activeQuests[questId] = {
		id = questId,
		name = quest.name,
		description = quest.description,
		target = quest.target,
		targetCount = quest.targetCount,
		progress = 0,
		acceptedAt = os.time()
	}
	
	self.questProgress[questId] = 0
	
	return true, "Quest accepted: " .. quest.name
end

function PlayerQuestClass:UpdateQuestProgress(questId, amount)
	if not self.activeQuests[questId] then return false end
	
	local quest = self.activeQuests[questId]
	quest.progress = quest.progress + amount
	self.questProgress[questId] = quest.progress
	
	if quest.progress >= quest.targetCount then
		return self:CompleteQuest(questId)
	end
	
	return true
end

function PlayerQuestClass:CompleteQuest(questId)
	if not self.activeQuests[questId] then return false, "Quest not active" end
	
	local quest = WorldSystem:GetQuest(questId)
	if not quest then return false end
	
	local questData = self.activeQuests[questId]
	
	-- Mark as completed
	self.completedQuests[questId] = {
		id = questId,
		name = quest.name,
		completedAt = os.time(),
		reward_xp = quest.reward_xp,
		reward_gold = quest.reward_gold
	}
	
	-- Remove from active
	self.activeQuests[questId] = nil
	self.questProgress[questId] = nil
	
	return true, "Quest completed! Gained " .. quest.reward_xp .. " XP and " .. quest.reward_gold .. " gold"
end

function PlayerQuestClass:AbandonQuest(questId)
	if not self.activeQuests[questId] then return false end
	
	self.activeQuests[questId] = nil
	self.questProgress[questId] = nil
	
	return true, "Quest abandoned"
end

function PlayerQuestClass:GetActiveQuests()
	return self.activeQuests
end

function PlayerQuestClass:GetCompletedQuests()
	return self.completedQuests
end

function PlayerQuestClass:IsQuestActive(questId)
	return self.activeQuests[questId] ~= nil
end

function PlayerQuestClass:IsQuestCompleted(questId)
	return self.completedQuests[questId] ~= nil
end

function PlayerQuestClass:GetQuestProgress(questId)
	if not self.activeQuests[questId] then return nil end
	return {
		progress = self.activeQuests[questId].progress,
		target = self.activeQuests[questId].targetCount
	}
end

function QuestSystem:CreateQuestTracker()
	return PlayerQuestClass:new()
end

function QuestSystem:GetAllQuests()
	return WorldSystem:GetQuests()
end

return QuestSystem
