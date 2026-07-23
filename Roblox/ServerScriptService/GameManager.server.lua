-- GameManager.server.lua
-- Main server-side game manager handling game state, progression, and persistence

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")

local Modules = ReplicatedStorage:WaitForChild("Modules")
local PlayerManager = require(Modules:WaitForChild("PlayerManager"))
local CombatSystem = require(Modules:WaitForChild("CombatSystem"))
local ShopSystem = require(Modules:WaitForChild("ShopSystem"))
local PersistenceManager = require(Modules:WaitForChild("PersistenceManager"))

local gameState = {
	activePlayers = {},
	goblinsDefeated = 0,
	activeEncounters = {}
}

local function onPlayerAdded(player)
	print("Player joined: " .. player.Name)
	
	-- Load player data
	local playerData = PersistenceManager:LoadPlayerData(player.UserId)
	
	-- Create player game object
	local playerObject = PlayerManager:CreatePlayer(player, playerData)
	gameState.activePlayers[player.UserId] = playerObject
	
	-- Replicate to client
	local events = ReplicatedStorage:WaitForChild("Events")
	events:WaitForChild("PlayerInitialized"):FireClient(player, playerObject:Serialize())
end

local function onPlayerRemoving(player)
	print("Player leaving: " .. player.Name)
	
	if gameState.activePlayers[player.UserId] then
		-- Save player data
		local playerObject = gameState.activePlayers[player.UserId]
		PersistenceManager:SavePlayerData(player.UserId, playerObject:Serialize())
		gameState.activePlayers[player.UserId] = nil
	end
end

-- Connect player events
Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)

-- Handle existing players
for _, player in pairs(Players:GetPlayers()) do
	onPlayerAdded(player)
end

print("GameManager initialized")
