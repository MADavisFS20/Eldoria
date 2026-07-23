-- LeaderboardSystem.lua
-- Manages player rankings and leaderboards

local LeaderboardSystem = {}
local DataStoreService = game:GetService("DataStoreService")

local leaderboardStore = DataStoreService:GetOrderedDataStore("Leaderboard_Level")

local LEADERBOARD_TYPES = {
	Level = "Leaderboard_Level",
	Gold = "Leaderboard_Gold",
	Experience = "Leaderboard_Experience",
	QuestsCompleted = "Leaderboard_Quests"
}

function LeaderboardSystem:UpdateLeaderboard(leaderboardType, userId, value)
	local success, err = pcall(function()
		local store = DataStoreService:GetOrderedDataStore(leaderboardType)
		store:SetAsync(userId, value)
	end)
	
	if not success then
		print("Leaderboard error: " .. err)
	end
end

function LeaderboardSystem:GetTopPlayers(leaderboardType, count)
	count = count or 10
	local success, results = pcall(function()
		local store = DataStoreService:GetOrderedDataStore(leaderboardType)
		return store:GetSortedAsync(false, count)
	end)
	
	if not success then
		print("Leaderboard error: " .. results)
		return {}
	end
	
	local topPlayers = {}
	for rank, page in pairs(results:GetPages(1, 1)) do
		for rank, data in ipairs(page) do
			table.insert(topPlayers, {
				rank = rank,
				userId = data.key,
				value = data.value
			})
		end
	end
	
	return topPlayers
end

function LeaderboardSystem:GetPlayerRank(leaderboardType, userId)
	local success, results = pcall(function()
		local store = DataStoreService:GetOrderedDataStore(leaderboardType)
		return store:GetSortedAsync(false, 100000)
	end)
	
	if not success then
		return nil
	end
	
	for rank, page in pairs(results:GetPages(1, -1)) do
		for position, data in ipairs(page) do
			if data.key == tostring(userId) then
				return position
			end
		end
	end
	
	return nil
end

return LeaderboardSystem
