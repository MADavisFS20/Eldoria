-- AnalyticsManager.lua
-- Tracks player statistics and game analytics

local AnalyticsManager = {}
local DataStoreService = game:GetService("DataStoreService")

local analyticsStore = DataStoreService:GetDataStore("GameAnalytics")

function AnalyticsManager:TrackEvent(eventName, eventData)
	local timestamp = os.time()
	local key = eventName .. "_" .. timestamp
	
	local success, err = pcall(function()
		analyticsStore:SetAsync(key, {
			event = eventName,
			data = eventData,
			timestamp = timestamp
		})
	end)
	
	if not success then
		print("Analytics error: " .. err)
	end
end

function AnalyticsManager:TrackPlayerJoin(userId)
	self:TrackEvent("PlayerJoin", {userId = userId, joinTime = os.time()})
end

function AnalyticsManager:TrackPurchase(userId, productId, price)
	self:TrackEvent("Purchase", {userId = userId, productId = productId, price = price})
end

function AnalyticsManager:TrackCombatEncounter(userId, enemyType, victory)
	self:TrackEvent("CombatEncounter", {userId = userId, enemy = enemyType, victory = victory})
end

function AnalyticsManager:TrackQuestComplete(userId, questId)
	self:TrackEvent("QuestComplete", {userId = userId, questId = questId})
end

function AnalyticsManager:TrackPlaySession(userId, duration)
	self:TrackEvent("PlaySession", {userId = userId, duration = duration})
end

return AnalyticsManager
