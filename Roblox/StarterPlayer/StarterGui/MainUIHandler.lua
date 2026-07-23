-- MainUIHandler.lua
-- Main UI handler for client-side interface

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

local Modules = ReplicatedStorage:WaitForChild("Modules")
local UIManager = require(Modules:WaitForChild("UIManager"))
local PremiumShopUI = require(Modules:WaitForChild("PremiumShopUI"))

-- Initialize UI
local uiManager = UIManager:new(playerGui)

-- Wait for player initialization
local Events = ReplicatedStorage:WaitForChild("Events")
local playerInitEvent = Events:WaitForChild("PlayerInitialized")

local playerData
playerInitEvent.OnClientEvent:Connect(function(data)
	print("Player initialized on client")
	playerData = data
	uiManager:ShowMainMenu()
end)

-- Handle purchase complete
local purchaseEvent = Events:WaitForChild("PurchaseComplete")
purchaseEvent.OnClientEvent:Connect(function(productId)
	uiManager:ShowNotification("Purchase successful! Check your inventory.")
end)

print("MainUIHandler initialized")
