-- PersistenceManager.lua
-- Handles player data storage and retrieval

local PersistenceManager = {}
local DataStoreService = game:GetService("DataStoreService")

local playerDataStore = DataStoreService:GetDataStore("PlayerData")
local playerProgressStore = DataStoreService:GetDataStore("PlayerProgress")

local DEFAULT_PLAYER_DATA = {
	charactersCreated = 0,
	levelsMilestones = {},
	totalPlayTime = 0,
	premiumOwned = {}
}

function PersistenceManager:SavePlayerData(userId, characterData)
	local success, err = pcall(function()
		playerDataStore:SetAsync("Player_" .. userId, characterData)
		print("Saved data for player " .. userId)
	end)
	
	if not success then
		print("Error saving player data: " .. err)
	end
	
	return success
end

function PersistenceManager:LoadPlayerData(userId)
	local success, data = pcall(function()
		return playerDataStore:GetAsync("Player_" .. userId)
	end)
	
	if success then
		if data then
			print("Loaded data for player " .. userId)
			return data
		else
			print("No data found for player " .. userId .. ", creating new")
			return nil
		end
	else
		print("Error loading player data: " .. data)
		return nil
	end
end

function PersistenceManager:SavePlayerProgress(userId, progressData)
	local success, err = pcall(function()
		playerProgressStore:SetAsync("Progress_" .. userId, progressData)
	end)
	
	return success
end

function PersistenceManager:LoadPlayerProgress(userId)
	local success, data = pcall(function()
		return playerProgressStore:GetAsync("Progress_" .. userId)
	end)
	
	if success then
		return data or DEFAULT_PLAYER_DATA
	else
		return DEFAULT_PLAYER_DATA
	end
end

return PersistenceManager
