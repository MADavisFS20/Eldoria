-- Create.lua
-- Script to create all necessary RemoteEvents in ReplicatedStorage

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Events = Instance.new("Folder")
Events.Name = "Events"
Events.Parent = ReplicatedStorage

local eventNames = {
	"PlayerInitialized",
	"PurchaseComplete",
	"CombatEncounter",
	"CombatAction",
	"LevelUp",
	"EquipmentChange",
	"ShopInteraction",
	"SaveGame",
	"LoadGame"
}

for _, eventName in ipairs(eventNames) do
	local event = Instance.new("RemoteEvent")
	event.Name = eventName
	event.Parent = Events
end

print("Events created in ReplicatedStorage")
