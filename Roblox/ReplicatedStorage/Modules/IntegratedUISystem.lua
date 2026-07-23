-- IntegratedUISystem.lua
-- Unified system that brings together all UI, dialogue, combat effects, and audio

local IntegratedUISystem = {}
local IntegratedUISystem_mt = {__index = IntegratedUISystem}

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Modules = ReplicatedStorage:WaitForChild("Modules")

local DialogueSystem = require(Modules:WaitForChild("DialogueSystem"))
local CombatEffectsSystem = require(Modules:WaitForChild("CombatEffectsSystem"))
local SoundManager = require(Modules:WaitForChild("SoundManager"))
local MobileUIAdapter = require(Modules:WaitForChild("MobileUIAdapter"))
local GameUIController = require(Modules:WaitForChild("GameUIController"))

function IntegratedUISystem:new(playerGui, soundParent)
	local self = setmetatable({}, IntegratedUISystem_mt)
	self.playerGui = playerGui
	self.soundManager = SoundManager:new()
	self.mobileAdapter = MobileUIAdapter:new()
	self.dialogueActive = nil
	self.inCombat = false
	self.combatUI = nil
	return self
end

function IntegratedUISystem:InitializeGame(playerData)
	-- Start background music
	self.soundManager:PlayMusic("MainMenu", self.playerGui)
	
	-- Create appropriate HUD based on device
	if self.mobileAdapter:IsMobile() then
		return self.mobileAdapter:CreateMobileHUD(self.playerGui, playerData)
	else
		local uiController = GameUIController:new(self.playerGui)
		return uiController:ShowGameHUD(playerData)
	end
end

function IntegratedUISystem:StartDialogueWithNPC(npcId, npcData)
	local dialogue = DialogueSystem:CreateDialogue(npcId)
	local greeting = dialogue:Start()
	
	self:DisplayDialogueUI(dialogue, npcData.name, greeting)
	self.dialogueActive = dialogue
end

function IntegratedUISystem:DisplayDialogueUI(dialogue, npcName, text)
	local dialogueGui = Instance.new("ScreenGui")
	dialogueGui.Name = "DialogueUI"
	dialogueGui.Parent = self.playerGui
	
	-- Background panel
	local panel = Instance.new("Frame")
	panel.Parent = dialogueGui
	panel.Size = UDim2.new(1, 0, 0.3, 0)
	panel.Position = UDim2.new(0, 0, 0.7, 0)
	panel.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
	panel.BorderColor3 = Color3.fromRGB(100, 150, 255)
	panel.BorderSizePixel = 3
	
	-- NPC name
	local nameLabel = Instance.new("TextLabel")
	nameLabel.Parent = panel
	nameLabel.Text = npcName
	nameLabel.Size = UDim2.new(1, 0, 0.15, 0)
	nameLabel.BackgroundColor3 = Color3.fromRGB(30, 30, 40)
	nameLabel.TextColor3 = Color3.fromRGB(100, 200, 255)
	nameLabel.Font = Enum.Font.GothamBold
	nameLabel.TextScaled = true
	
	-- Dialogue text
	local textLabel = Instance.new("TextLabel")
	textLabel.Parent = panel
	textLabel.Text = text
	textLabel.Size = UDim2.new(0.95, 0, 0.4, 0)
	textLabel.Position = UDim2.new(0.025, 0, 0.15, 0)
	textLabel.BackgroundTransparency = 1
	textLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
	textLabel.Font = Enum.Font.Gotham
	textLabel.TextWrapped = true
	textLabel.TextSize = 16
	
	-- Options frame
	local optionsFrame = Instance.new("Frame")
	optionsFrame.Parent = panel
	optionsFrame.Size = UDim2.new(1, 0, 0.4, 0)
	optionsFrame.Position = UDim2.new(0, 0, 0.55, 0)
	optionsFrame.BackgroundTransparency = 1
	
	-- Create buttons for each option
	local options = dialogue:GetOptions()
	for i, option in ipairs(options) do
		local btn = Instance.new("TextButton")
		btn.Parent = optionsFrame
		btn.Text = tostring(i) .. ". " .. option.text
		btn.Size = UDim2.new(0.95, 0, 0.22, 0)
		btn.Position = UDim2.new(0.025, 0, (i - 1) * 0.24, 0)
		btn.BackgroundColor3 = Color3.fromRGB(50, 50, 100)
		btn.TextColor3 = Color3.fromRGB(255, 255, 255)
		btn.Font = Enum.Font.Gotham
		btn.TextScaled = true
		btn.BorderColor3 = Color3.fromRGB(100, 100, 150)
		btn.BorderSizePixel = 2
		
		btn.MouseButton1Click:Connect(function()
			self.soundManager:PlaySFX("ButtonClick", self.playerGui)
			dialogue:SelectOption(i)
			dialogueGui:Destroy()
			
			if dialogue:IsDialogueEnd() then
				self.dialogueActive = nil
			else
				self:DisplayDialogueUI(dialogue, npcName, dialogue:GetNodeText())
			end
			
			-- Handle actions
			local action = dialogue:GetAction()
			if action == "open_shop" then
				self:ShowShopUI()
			elseif action == "accept_quest" then
			self.soundManager:PlaySFX("LevelUp", self.playerGui)
			end
		end)
	end
	
	return dialogueGui
end

function IntegratedUISystem:StartCombat(encounter)
	self.inCombat = true
	self.soundManager:PlaySFX("CombatStart", self.playerGui)
	
	local combatGui = Instance.new("ScreenGui")
	combatGui.Name = "CombatUI"
	combatGui.Parent = self.playerGui
	
	-- Enemy info
	local enemyFrame = Instance.new("Frame")
	enemyFrame.Parent = combatGui
	enemyFrame.Size = UDim2.new(0.3, 0, 0.15, 0)
	enemyFrame.Position = UDim2.new(0.35, 0, 0.1, 0)
	enemyFrame.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
	enemyFrame.BorderColor3 = Color3.fromRGB(255, 50, 50)
	enemyFrame.BorderSizePixel = 2
	
	local enemyLabel = Instance.new("TextLabel")
	enemyLabel.Parent = enemyFrame
	enemyLabel.Text = encounter.enemy.name
	enemyLabel.Size = UDim2.new(1, 0, 0.3, 0)
	enemyLabel.BackgroundTransparency = 1
	enemyLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
	enemyLabel.Font = Enum.Font.GothamBold
	enemyLabel.TextScaled = true
	
	local enemyHealthLabel = Instance.new("TextLabel")
	enemyHealthLabel.Parent = enemyFrame
	enemyHealthLabel.Text = "Health: " .. encounter.enemy.health .. "/" .. encounter.enemy.healthMax
	enemyHealthLabel.Size = UDim2.new(1, 0, 0.3, 0)
	enemyHealthLabel.Position = UDim2.new(0, 0, 0.35, 0)
	enemyHealthLabel.BackgroundTransparency = 1
	enemyHealthLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
	enemyHealthLabel.Font = Enum.Font.Gotham
	enemyHealthLabel.TextScaled = true
	
	-- Action buttons
	local attackBtn = Instance.new("TextButton")
	attackBtn.Parent = combatGui
	attackBtn.Text = "⚔️ ATTACK"
	attackBtn.Size = UDim2.new(0.2, 0, 0.08, 0)
	attackBtn.Position = UDim2.new(0.15, 0, 0.8, 0)
	attackBtn.BackgroundColor3 = Color3.fromRGB(255, 50, 50)
	attackBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
	attackBtn.Font = Enum.Font.GothamBold
	attackBtn.BorderSizePixel = 0
	
	attackBtn.MouseButton1Click:Connect(function()
		self.soundManager:PlaySFX("MeleeAttack", self.playerGui)
		CombatEffectsSystem:PlayAttackAnimation(enemyFrame, "MeleeAttack")
	end)
	
	self.combatUI = combatGui
	return combatGui
end

function IntegratedUISystem:ShowShopUI()
	self.soundManager:PlaySFX("ButtonClick", self.playerGui)
	-- Implementation handled by ShopSystem
end

function IntegratedUISystem:PlayCombatEffect(effectType, parent, damage)
	self.soundManager:PlaySFX(effectType, parent)
	CombatEffectsSystem:CreateDamagePopup(parent, damage, effectType)
end

function IntegratedUISystem:EndCombat(victory)
	if victory then
		self.soundManager:PlaySFX("Victory", self.playerGui)
	else
		self.soundManager:PlaySFX("Defeat", self.playerGui)
	end
	
	self.inCombat = false
	if self.combatUI then
		self.combatUI:Destroy()
		self.combatUI = nil
	end
end

function IntegratedUISystem:ShowNotification(message, duration)
	duration = duration or 3
	
	local notification = Instance.new("TextLabel")
	notification.Name = "Notification"
	notification.Parent = self.playerGui
	notification.Text = message
	notification.Size = UDim2.new(0.4, 0, 0.1, 0)
	notification.Position = UDim2.new(0.3, 0, 0.05, 0)
	notification.BackgroundColor3 = Color3.fromRGB(50, 50, 60)
	notification.TextColor3 = Color3.fromRGB(255, 255, 255)
	notification.BorderColor3 = Color3.fromRGB(100, 200, 100)
	notification.BorderSizePixel = 2
	notification.Font = Enum.Font.GothamBold
	notification.TextScaled = true
	
	game:GetService("Debris"):AddItem(notification, duration)
end

return IntegratedUISystem
