-- UIManager.lua
-- Manages all UI elements for the game

local UIManager = {}
local UIManager_mt = {__index = UIManager}

local MarketplaceService = game:GetService("MarketplaceService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ShopSystem = require(ReplicatedStorage:WaitForChild("Modules"):WaitForChild("ShopSystem"))

function UIManager:new(playerGui)
	local self = setmetatable({}, UIManager_mt)
	self.playerGui = playerGui
	self.screens = {}
	return self
end

function UIManager:ShowMainMenu()
	local screenFrame = self:CreateScreen("MainMenu")
	screenFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
	screenFrame.Size = UDim2.new(1, 0, 1, 0)
	
	-- Title
	local title = Instance.new("TextLabel")
	title.Parent = screenFrame
	title.Text = "ELDORIA: ROBLOX EDITION"
	title.Size = UDim2.new(1, 0, 0.15, 0)
	title.Position = UDim2.new(0, 0, 0.1, 0)
	title.BackgroundTransparency = 1
	title.TextScaled = true
	title.TextColor3 = Color3.fromRGB(255, 215, 0)
	title.Font = Enum.Font.GothamBold
	
	-- New Game Button
	local newGameBtn = self:CreateButton("NEW GAME", 0.25)
	newGameBtn.Position = UDim2.new(0.25, 0, 0.35, 0)
	newGameBtn.Parent = screenFrame
	newGameBtn.MouseButton1Click:Connect(function()
		self:ShowCharacterCreation()
	end)
	
	-- Premium Shop Button
	local shopBtn = self:CreateButton("PREMIUM SHOP", 0.25)
	shopBtn.Position = UDim2.new(0.25, 0, 0.5, 0)
	shopBtn.Parent = screenFrame
	shopBtn.MouseButton1Click:Connect(function()
		self:ShowPremiumShop()
	end)
	
	-- Settings Button
	local settingsBtn = self:CreateButton("SETTINGS", 0.25)
	settingsBtn.Position = UDim2.new(0.25, 0, 0.65, 0)
	settingsBtn.Parent = screenFrame
	
	return screenFrame
end

function UIManager:ShowCharacterCreation()
	local screenFrame = self:CreateScreen("CharacterCreation")
	screenFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
	screenFrame.Size = UDim2.new(1, 0, 1, 0)
	
	-- Title
	local title = Instance.new("TextLabel")
	title.Parent = screenFrame
	title.Text = "CREATE YOUR HERO"
	title.Size = UDim2.new(1, 0, 0.1, 0)
	title.Position = UDim2.new(0, 0, 0.05, 0)
	title.BackgroundTransparency = 1
	title.TextScaled = true
	title.TextColor3 = Color3.fromRGB(255, 215, 0)
	title.Font = Enum.Font.GothamBold
	
	-- Class selection
	local classFrame = Instance.new("Frame")
	classFrame.Parent = screenFrame
	classFrame.Size = UDim2.new(0.8, 0, 0.7, 0)
	classFrame.Position = UDim2.new(0.1, 0, 0.2, 0)
	classFrame.BackgroundColor3 = Color3.fromRGB(30, 30, 40)
	classFrame.BorderSizePixel = 0
	
	local classes = {"Warrior", "Rogue", "Mage", "Paladin", "Ranger"}
	for i, className in ipairs(classes) do
		local btn = self:CreateButton(className, 0.25)
		btn.Parent = classFrame
		btn.Position = UDim2.new(0.05 + (i - 1) * 0.18, 0, 0.1, 0)
		btn.Size = UDim2.new(0.15, 0, 0.2, 0)
	end
	
	return screenFrame
end

function UIManager:ShowPremiumShop()
	local screenFrame = self:CreateScreen("PremiumShop")
	screenFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
	screenFrame.Size = UDim2.new(1, 0, 1, 0)
	
	-- Title
	local title = Instance.new("TextLabel")
	title.Parent = screenFrame
	title.Text = "⭐ PREMIUM SHOP - ROBUX ⭐"
	title.Size = UDim2.new(1, 0, 0.1, 0)
	title.Position = UDim2.new(0, 0, 0.05, 0)
	title.BackgroundTransparency = 1
	title.TextScaled = true
	title.TextColor3 = Color3.fromRGB(255, 100, 100)
	title.Font = Enum.Font.GothamBold
	
	-- Scroll frame for items
	local scrollFrame = Instance.new("ScrollingFrame")
	scrollFrame.Parent = screenFrame
	scrollFrame.Size = UDim2.new(1, 0, 0.8, 0)
	scrollFrame.Position = UDim2.new(0, 0, 0.15, 0)
	scrollFrame.BackgroundColor3 = Color3.fromRGB(30, 30, 40)
	scrollFrame.BorderSizePixel = 0
	scrollFrame.CanvasSize = UDim2.new(0, 0, 2, 0)
	
	local premiumShop = ShopSystem:GetPremiumShop()
	
	for i, item in ipairs(premiumShop) do
		local itemFrame = Instance.new("Frame")
		itemFrame.Parent = scrollFrame
		itemFrame.Size = UDim2.new(0.9, 0, 0.12, 0)
		itemFrame.Position = UDim2.new(0.05, 0, (i - 1) * 0.13, 0)
		itemFrame.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
		itemFrame.BorderColor3 = Color3.fromRGB(255, 215, 0)
		itemFrame.BorderSizePixel = 2
		
		-- Item name
		local nameLabel = Instance.new("TextLabel")
		nameLabel.Parent = itemFrame
		nameLabel.Text = item.name
		nameLabel.Size = UDim2.new(0.5, 0, 0.5, 0)
		nameLabel.Position = UDim2.new(0.05, 0, 0.1, 0)
		nameLabel.BackgroundTransparency = 1
		nameLabel.TextScaled = true
		nameLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
		
		-- Price button
		local buyBtn = self:CreateButton(item.robuxtPrice .. " R$", 0.15)
		buyBtn.Parent = itemFrame
		buyBtn.Position = UDim2.new(0.75, 0, 0.2, 0)
		buyBtn.Size = UDim2.new(0.2, 0, 0.6, 0)
		buyBtn.MouseButton1Click:Connect(function()
			self:PromptPurchase(item.productId, item.robuxtPrice)
		end)
	end
	
	return screenFrame
end

function UIManager:PromptPurchase(productId, price)
	local success, err = pcall(function()
		MarketplaceService:PromptBuyProductAsync(game.Players.LocalPlayer, productId)
	end)
	
	if not success then
		self:ShowNotification("Error initiating purchase: " .. tostring(err))
	end
end

function UIManager:ShowNotification(text)
	local notification = Instance.new("TextLabel")
	notification.Parent = self.playerGui
	notification.Text = text
	notification.Size = UDim2.new(0.3, 0, 0.1, 0)
	notification.Position = UDim2.new(0.35, 0, 0.05, 0)
	notification.BackgroundColor3 = Color3.fromRGB(50, 50, 60)
	notification.TextColor3 = Color3.fromRGB(255, 255, 255)
	notification.BorderSizePixel = 0
	notification.TextScaled = true
	
	game:GetService("Debris"):AddItem(notification, 3)
end

function UIManager:CreateScreen(screenName)
	local screen = Instance.new("ScreenGui")
	screen.Name = screenName
	screen.Parent = self.playerGui
	self.screens[screenName] = screen
	return screen
end

function UIManager:CreateButton(text, width)
	local button = Instance.new("TextButton")
	button.Text = text
	button.Size = UDim2.new(width, 0, 0.08, 0)
	button.BackgroundColor3 = Color3.fromRGB(255, 140, 0)
	button.TextColor3 = Color3.fromRGB(0, 0, 0)
	button.Font = Enum.Font.GothamBold
	button.BorderSizePixel = 0
	button.TextScaled = true
	
	button.MouseEnter:Connect(function()
		button.BackgroundColor3 = Color3.fromRGB(255, 165, 0)
	end)
	
	button.MouseLeave:Connect(function()
		button.BackgroundColor3 = Color3.fromRGB(255, 140, 0)
	end)
	
	return button
end

return UIManager
