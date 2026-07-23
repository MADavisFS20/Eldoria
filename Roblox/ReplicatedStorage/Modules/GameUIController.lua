-- GameUIController.lua
-- Central controller for all UI interactions during gameplay

local GameUIController = {}
local GameUIController_mt = {__index = GameUIController}

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local Modules = ReplicatedStorage:WaitForChild("Modules")
local WorldSystem = require(Modules:WaitForChild("WorldSystem"))
local CosmeticSystem = require(Modules:WaitForChild("CosmeticSystem"))
local BattlePassSystem = require(Modules:WaitForChild("BattlePassSystem"))

function GameUIController:new(playerGui)
	local self = setmetatable({}, GameUIController_mt)
	self.playerGui = playerGui
	self.activeScreens = {}
	return self
end

function GameUIController:ShowGameHUD(playerData)
	local hudGui = Instance.new("ScreenGui")
	hudGui.Name = "GameHUD"
	hudGui.Parent = self.playerGui
	
	-- Health bar
	local healthFrame = Instance.new("Frame")
	healthFrame.Parent = hudGui
	healthFrame.Size = UDim2.new(0.25, 0, 0.08, 0)
	healthFrame.Position = UDim2.new(0.02, 0, 0.02, 0)
	healthFrame.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
	healthFrame.BorderColor3 = Color3.fromRGB(255, 50, 50)
	healthFrame.BorderSizePixel = 2
	
	local healthLabel = Instance.new("TextLabel")
	healthLabel.Parent = healthFrame
	healthLabel.Text = "❤ Health"
	healthLabel.Size = UDim2.new(1, 0, 0.3, 0)
	healthLabel.BackgroundTransparency = 1
	healthLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
	healthLabel.Font = Enum.Font.GothamBold
	
	local healthBar = Instance.new("Frame")
	healthBar.Parent = healthFrame
	healthBar.Size = UDim2.new(1, 0, 0.6, 0)
	healthBar.Position = UDim2.new(0, 0, 0.35, 0)
	healthBar.BackgroundColor3 = Color3.fromRGB(100, 200, 100)
	healthBar.BorderSizePixel = 0
	
	-- Mana bar
	local manaFrame = Instance.new("Frame")
	manaFrame.Parent = hudGui
	manaFrame.Size = UDim2.new(0.25, 0, 0.08, 0)
	manaFrame.Position = UDim2.new(0.02, 0, 0.12, 0)
	manaFrame.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
	manaFrame.BorderColor3 = Color3.fromRGB(100, 150, 255)
	manaFrame.BorderSizePixel = 2
	
	local manaLabel = Instance.new("TextLabel")
	manaLabel.Parent = manaFrame
	manaLabel.Text = "✦ Mana"
	manaLabel.Size = UDim2.new(1, 0, 0.3, 0)
	manaLabel.BackgroundTransparency = 1
	manaLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
	manaLabel.Font = Enum.Font.GothamBold
	
	local manaBar = Instance.new("Frame")
	manaBar.Parent = manaFrame
	manaBar.Size = UDim2.new(1, 0, 0.6, 0)
	manaBar.Position = UDim2.new(0, 0, 0.35, 0)
	manaBar.BackgroundColor3 = Color3.fromRGB(100, 150, 255)
	manaBar.BorderSizePixel = 0
	
	-- Level and XP info
	local levelFrame = Instance.new("Frame")
	levelFrame.Parent = hudGui
	levelFrame.Size = UDim2.new(0.15, 0, 0.08, 0)
	levelFrame.Position = UDim2.new(0.02, 0, 0.22, 0)
	levelFrame.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
	levelFrame.BorderColor3 = Color3.fromRGB(255, 215, 0)
	levelFrame.BorderSizePixel = 2
	
	local levelLabel = Instance.new("TextLabel")
	levelLabel.Parent = levelFrame
	levelLabel.Text = "Level " .. (playerData.level or 1)
	levelLabel.Size = UDim2.new(1, 0, 1, 0)
	levelLabel.BackgroundTransparency = 1
	levelLabel.TextColor3 = Color3.fromRGB(255, 215, 0)
	levelLabel.Font = Enum.Font.GothamBold
	levelLabel.TextScaled = true
	
	-- Action buttons
	local inventoryBtn = self:CreateActionButton("📦 Inventory", 0.02, 0.85)
	inventoryBtn.Parent = hudGui
	inventoryBtn.MouseButton1Click:Connect(function()
		self:ShowInventory(playerData)
	end)
	
	local questsBtn = self:CreateActionButton("📋 Quests", 0.12, 0.85)
	questsBtn.Parent = hudGui
	questsBtn.MouseButton1Click:Connect(function()
		self:ShowQuests(playerData)
	end)
	
	local shopBtn = self:CreateActionButton("🛍️ Shop", 0.22, 0.85)
	shopBtn.Parent = hudGui
	shopBtn.MouseButton1Click:Connect(function()
		self:ShowShopMenu(playerData)
	end)
	
	local cosmeticsBtn = self:CreateActionButton("✨ Cosmetics", 0.32, 0.85)
	cosmeticsBtn.Parent = hudGui
	cosmeticsBtn.MouseButton1Click:Connect(function()
		self:ShowCosmeticsMenu(playerData)
	end)
	
	local settingsBtn = self:CreateActionButton("⚙️ Settings", 0.42, 0.85)
	settingsBtn.Parent = hudGui
	
	return hudGui
end

function GameUIController:ShowInventory(playerData)
	local invGui = Instance.new("ScreenGui")
	invGui.Name = "InventoryUI"
	invGui.Parent = self.playerGui
	
	local mainFrame = Instance.new("Frame")
	mainFrame.Parent = invGui
	mainFrame.Size = UDim2.new(0.6, 0, 0.7, 0)
	mainFrame.Position = UDim2.new(0.2, 0, 0.15, 0)
	mainFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
	mainFrame.BorderColor3 = Color3.fromRGB(255, 215, 0)
	mainFrame.BorderSizePixel = 3
	
	local title = Instance.new("TextLabel")
	title.Parent = mainFrame
	title.Text = "📦 INVENTORY"
	title.Size = UDim2.new(1, 0, 0.08, 0)
	title.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
	title.TextColor3 = Color3.fromRGB(255, 215, 0)
	title.Font = Enum.Font.GothamBold
	title.TextScaled = true
	
	local scrollFrame = Instance.new("ScrollingFrame")
	scrollFrame.Parent = mainFrame
	scrollFrame.Size = UDim2.new(1, 0, 0.85, 0)
	scrollFrame.Position = UDim2.new(0, 0, 0.08, 0)
	scrollFrame.BackgroundColor3 = Color3.fromRGB(30, 30, 40)
	scrollFrame.BorderSizePixel = 0
	scrollFrame.CanvasSize = UDim2.new(0, 0, #(playerData.inventory or {}) * 0.1 + 0.5, 0)
	
	for i, item in ipairs(playerData.inventory or {}) do
		local itemFrame = Instance.new("Frame")
		itemFrame.Parent = scrollFrame
		itemFrame.Size = UDim2.new(0.95, 0, 0.08, 0)
		itemFrame.Position = UDim2.new(0.025, 0, (i - 1) * 0.09, 0)
		itemFrame.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
		itemFrame.BorderColor3 = Color3.fromRGB(150, 150, 150)
		itemFrame.BorderSizePixel = 1
		
		local itemName = Instance.new("TextLabel")
		itemName.Parent = itemFrame
		itemName.Text = item.name or "Unknown Item"
		itemName.Size = UDim2.new(0.5, 0, 1, 0)
		itemName.BackgroundTransparency = 1
		itemName.TextColor3 = Color3.fromRGB(255, 255, 255)
		itemName.Font = Enum.Font.Gotham
		itemName.TextScaled = true
		
		local useBtn = Instance.new("TextButton")
		useBtn.Parent = itemFrame
		useBtn.Text = "USE"
		useBtn.Size = UDim2.new(0.2, 0, 1, 0)
		useBtn.Position = UDim2.new(0.75, 0, 0, 0)
		useBtn.BackgroundColor3 = Color3.fromRGB(100, 150, 100)
		useBtn.TextColor3 = Color3.fromRGB(0, 0, 0)
		useBtn.Font = Enum.Font.GothamBold
		useBtn.BorderSizePixel = 0
	end
	
	-- Close button
	local closeBtn = Instance.new("TextButton")
	closeBtn.Parent = mainFrame
	closeBtn.Text = "X"
	closeBtn.Size = UDim2.new(0.05, 0, 0.08, 0)
	closeBtn.Position = UDim2.new(0.93, 0, 0, 0)
	closeBtn.BackgroundColor3 = Color3.fromRGB(255, 50, 50)
	closeBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
	closeBtn.Font = Enum.Font.GothamBold
	closeBtn.BorderSizePixel = 0
	closeBtn.MouseButton1Click:Connect(function()
		invGui:Destroy()
	end)
end

function GameUIController:ShowQuests(playerData)
	local questGui = Instance.new("ScreenGui")
	questGui.Name = "QuestUI"
	questGui.Parent = self.playerGui
	
	local mainFrame = Instance.new("Frame")
	mainFrame.Parent = questGui
	mainFrame.Size = UDim2.new(0.4, 0, 0.6, 0)
	mainFrame.Position = UDim2.new(0.3, 0, 0.2, 0)
	mainFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
	mainFrame.BorderColor3 = Color3.fromRGB(100, 200, 100)
	mainFrame.BorderSizePixel = 3
	
	local title = Instance.new("TextLabel")
	title.Parent = mainFrame
	title.Text = "📋 ACTIVE QUESTS"
	title.Size = UDim2.new(1, 0, 0.1, 0)
	title.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
	title.TextColor3 = Color3.fromRGB(100, 200, 100)
	title.Font = Enum.Font.GothamBold
	title.TextScaled = true
	
	local questsLabel = Instance.new("TextLabel")
	questsLabel.Parent = mainFrame
	questsLabel.Text = "No active quests.\nVisit NPCs to accept quests!"
	questsLabel.Size = UDim2.new(1, 0, 0.8, 0)
	questsLabel.Position = UDim2.new(0, 0, 0.1, 0)
	questsLabel.BackgroundTransparency = 1
	questsLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
	questsLabel.Font = Enum.Font.Gotham
	questsLabel.TextScaled = true
	
	-- Close button
	local closeBtn = Instance.new("TextButton")
	closeBtn.Parent = mainFrame
	closeBtn.Text = "X"
	closeBtn.Size = UDim2.new(0.1, 0, 0.1, 0)
	closeBtn.Position = UDim2.new(0.88, 0, 0, 0)
	closeBtn.BackgroundColor3 = Color3.fromRGB(255, 50, 50)
	closeBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
	closeBtn.Font = Enum.Font.GothamBold
	closeBtn.BorderSizePixel = 0
	closeBtn.MouseButton1Click:Connect(function()
		questGui:Destroy()
	end)
end

function GameUIController:ShowShopMenu(playerData)
	local shopGui = Instance.new("ScreenGui")
	shopGui.Name = "ShopMenuUI"
	shopGui.Parent = self.playerGui
	
	local mainFrame = Instance.new("Frame")
	mainFrame.Parent = shopGui
	mainFrame.Size = UDim2.new(0.8, 0, 0.6, 0)
	mainFrame.Position = UDim2.new(0.1, 0, 0.2, 0)
	mainFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
	mainFrame.BorderColor3 = Color3.fromRGB(255, 140, 0)
	mainFrame.BorderSizePixel = 3
	
	local title = Instance.new("TextLabel")
	title.Parent = mainFrame
	title.Text = "🏪 SHOP MENU"
	title.Size = UDim2.new(1, 0, 0.1, 0)
	title.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
	title.TextColor3 = Color3.fromRGB(255, 140, 0)
	title.Font = Enum.Font.GothamBold
	title.TextScaled = true
	
	local locations = WorldSystem:GetLocations()
	local shopCount = 0
	for location, data in pairs(locations) do
		if data.shop then shopCount = shopCount + 1 end
	end
	
	local shopLabel = Instance.new("TextLabel")
	shopLabel.Parent = mainFrame
	shopLabel.Text = "Available Shops: " .. shopCount
	shopLabel.Size = UDim2.new(1, 0, 0.8, 0)
	shopLabel.Position = UDim2.new(0, 0, 0.1, 0)
	shopLabel.BackgroundTransparency = 1
	shopLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
	shopLabel.Font = Enum.Font.Gotham
	shopLabel.TextScaled = true
	
	-- Close button
	local closeBtn = Instance.new("TextButton")
	closeBtn.Parent = mainFrame
	closeBtn.Text = "X"
	closeBtn.Size = UDim2.new(0.1, 0, 0.1, 0)
	closeBtn.Position = UDim2.new(0.88, 0, 0, 0)
	closeBtn.BackgroundColor3 = Color3.fromRGB(255, 50, 50)
	closeBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
	closeBtn.Font = Enum.Font.GothamBold
	closeBtn.BorderSizePixel = 0
	closeBtn.MouseButton1Click:Connect(function()
		shopGui:Destroy()
	end)
end

function GameUIController:ShowCosmeticsMenu(playerData)
	local cosmeticGui = Instance.new("ScreenGui")
	cosmeticGui.Name = "CosmeticsUI"
	cosmeticGui.Parent = self.playerGui
	
	local mainFrame = Instance.new("Frame")
	mainFrame.Parent = cosmeticGui
	mainFrame.Size = UDim2.new(0.7, 0, 0.7, 0)
	mainFrame.Position = UDim2.new(0.15, 0, 0.15, 0)
	mainFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
	mainFrame.BorderColor3 = Color3.fromRGB(255, 100, 200)
	mainFrame.BorderSizePixel = 3
	
	local title = Instance.new("TextLabel")
	title.Parent = mainFrame
	title.Text = "✨ COSMETICS"
	title.Size = UDim2.new(1, 0, 0.08, 0)
	title.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
	title.TextColor3 = Color3.fromRGB(255, 100, 200)
	title.Font = Enum.Font.GothamBold
	title.TextScaled = true
	
	local cosmetics = CosmeticSystem:GetAllCosmetics()
	local scrollFrame = Instance.new("ScrollingFrame")
	scrollFrame.Parent = mainFrame
	scrollFrame.Size = UDim2.new(1, 0, 0.84, 0)
	scrollFrame.Position = UDim2.new(0, 0, 0.08, 0)
	scrollFrame.BackgroundColor3 = Color3.fromRGB(30, 30, 40)
	scrollFrame.BorderSizePixel = 0
	scrollFrame.CanvasSize = UDim2.new(0, 0, 3, 0)
	
	local itemIndex = 1
	for category, items in pairs(cosmetics) do
		for itemKey, item in pairs(items) do
			local itemBtn = Instance.new("TextButton")
			itemBtn.Parent = scrollFrame
			itemBtn.Size = UDim2.new(0.9, 0, 0.08, 0)
			itemBtn.Position = UDim2.new(0.05, 0, (itemIndex - 1) * 0.09, 0)
			itemBtn.BackgroundColor3 = Color3.fromRGB(50, 50, 60)
			itemBtn.BorderColor3 = Color3.fromRGB(255, 100, 200)
			itemBtn.BorderSizePixel = 1
			itemBtn.Text = item.name .. " (" .. item.price .. " R$)"
			itemBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
			itemBtn.Font = Enum.Font.Gotham
			itemBtn.TextScaled = true
			
			itemIndex = itemIndex + 1
		end
	end
	
	-- Close button
	local closeBtn = Instance.new("TextButton")
	closeBtn.Parent = mainFrame
	closeBtn.Text = "X"
	closeBtn.Size = UDim2.new(0.08, 0, 0.08, 0)
	closeBtn.Position = UDim2.new(0.91, 0, 0, 0)
	closeBtn.BackgroundColor3 = Color3.fromRGB(255, 50, 50)
	closeBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
	closeBtn.Font = Enum.Font.GothamBold
	closeBtn.BorderSizePixel = 0
	closeBtn.MouseButton1Click:Connect(function()
		cosmeticGui:Destroy()
	end)
end

function GameUIController:CreateActionButton(text, posX, posY)
	local button = Instance.new("TextButton")
	button.Text = text
	button.Size = UDim2.new(0.09, 0, 0.06, 0)
	button.Position = UDim2.new(posX, 0, posY, 0)
	button.BackgroundColor3 = Color3.fromRGB(100, 100, 150)
	button.TextColor3 = Color3.fromRGB(255, 255, 255)
	button.Font = Enum.Font.GothamBold
	button.BorderSizePixel = 0
	button.TextScaled = true
	
	button.MouseEnter:Connect(function()
		button.BackgroundColor3 = Color3.fromRGB(150, 150, 200)
	end)
	
	button.MouseLeave:Connect(function()
		button.BackgroundColor3 = Color3.fromRGB(100, 100, 150)
	end)
	
	return button
end

return GameUIController
