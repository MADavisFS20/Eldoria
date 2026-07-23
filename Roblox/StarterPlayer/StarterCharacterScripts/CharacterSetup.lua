-- CharacterSetup.lua
-- Sets up character model with humanoid

local character = script.Parent
local humanoid = character:WaitForChild("Humanoid")

humanoid.MaxHealth = 100
humanoid.Health = 100

-- Replicate to player info
local player = game.Players:GetPlayerFromCharacter(character)

if player then
	local ReplicatedStorage = game:GetService("ReplicatedStorage")
	local Events = ReplicatedStorage:WaitForChild("Events")
	
	print("Character spawned for " .. player.Name)
end
