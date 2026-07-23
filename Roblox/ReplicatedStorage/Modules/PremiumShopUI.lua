-- PremiumShopUI.lua
-- Dedicated premium shop UI with Robux integration

local PremiumShopUI = {}
local PremiumShopUI_mt = {__index = PremiumShopUI}

local MarketplaceService = game:GetService("MarketplaceService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ShopSystem = require(ReplicatedStorage:WaitForChild("Modules"):WaitForChild("ShopSystem"))

local PRODUCT_CATEGORIES = {
	"cosmetic",
	"weapon",
	"booster",
	"battle_pass",
	"expansion"
}

function PremiumShopUI:new(playerGui)
	local self = setmetatable({}, PremiumShopUI_mt)
	self.playerGui = playerGui
	self.premiumShop = ShopSystem:GetPremiumShop()
	return self
end

function PremiumShopUI:Display()
	local screenGui = Instance.new("ScreenGui")
	screenGui.Name = "PremiumShopUI"
	screenGui.Parent = self.playerGui
	
	-- Main container
	local mainFrame = Instance.new("Frame")
	mainFrame.Name = "MainFrame"
	mainFrame.Parent = screenGui
	mainFrame.Size = UDim2.new(1, 0, 1, 0)
	mainFrame.BackgroundColor3 = Color3.fromRGB(15, 15, 25)
	mainFrame.BackgroundTransparency = 0.1
	
	-- Header
	local header = Instance.new("TextLabel")
	header.Parent = mainFrame
	header.Text = "🏆 PREMIUM SHOP - ROBUX 🏆"
	header.Size = UDim2.new(1, 0, 0.12, 0)
	header.Position = UDim2.new(0, 0, 0, 0)
	header.BackgroundColor3 = Color3.fromRGB(255, 100, 100)
	header.TextColor3 = Color3.fromRGB(255, 255, 255)
	header.Font = Enum.Font.GothamBold
	header.TextScaled = true
	
	-- Category buttons
	local categoryFrame = Instance.new("Frame")
	categoryFrame.Parent = mainFrame
	categoryFrame.Size = UDim2.new(1, 0, 0.08, 0)
	categoryFrame.Position = UDim2.new(0, 0, 0.12, 0)
	categoryFrame.BackgroundColor3 = Color3.fromRGB(25, 25, 35)
	
	for i, category in ipairs(PRODUCT_CATEGORIES) do
		local catBtn = Instance.new("TextButton")
		catBtn.Parent = categoryFrame
		catBtn.Text = category:gsub("_", " "):upper()
		catBtn.Size = UDim2.new(0.18, 0, 1, 0)
		catBtn.Position = UDim2.new((i - 1) * 0.2, 0, 0, 0)
		catBtn.BackgroundColor3 = Color3.fromRGB(100, 100, 150)
		catBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
		catBtn.Font = Enum.Font.Gotham
		catBtn.BorderSizePixel = 0
	end
	
	-- Items scroll frame
	local itemsScroll = Instance.new("ScrollingFrame")
	itemsScroll.Parent = mainFrame
	itemsScroll.Size = UDim2.new(1, 0, 0.75, 0)
	itemsScroll.Position = UDim2.new(0, 0, 0.2, 0)
	itemsScroll.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
	itemsScroll.BorderSizePixel = 0
	itemsScroll.CanvasSize = UDim2.new(0, 0, #self.premiumShop * 0.15, 0)
	
	-- Populate items
	for index, item in ipairs(self.premiumShop) do
		local itemBtn = self:CreateItemButton(item)
		itemBtn.Parent = itemsScroll
		itemBtn.Position = UDim2.new(0.05, 0, (index - 1) * 0.15, 0)
		itemBtn.Size = UDim2.new(0.9, 0, 0.12, 0)
		
		itemBtn.MouseButton1Click:Connect(function()
			self:HandlePurchase(item)
		end)
	end
	
	-- Close button
	local closeBtn = Instance.new("TextButton")
	closeBtn.Parent = mainFrame
	closeBtn.Text = "X"
	closeBtn.Size = UDim2.new(0.05, 0, 0.08, 0)
	closeBtn.Position = UDim2.new(0.92, 0, 0.02, 0)
	closeBtn.BackgroundColor3 = Color3.fromRGB(255, 50, 50)
	closeBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
	closeBtn.Font = Enum.Font.GothamBold
	closeBtn.BorderSizePixel = 0
	closeBtn.MouseButton1Click:Connect(function()
		screenGui:Destroy()
	end)
	
	return screenGui
end

function PremiumShopUI:CreateItemButton(item)
	local button = Instance.new("TextButton")
	button.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
	button.BorderColor3 = Color3.fromRGB(255, 215, 0)
	button.BorderSizePixel = 2
	button.Text = ""
	
	-- Item icon/type indicator
	local typeLabel = Instance.new("TextLabel")
	typeLabel.Parent = button
	typeLabel.Text = "[" .. item.type:upper() .. "]"
	typeLabel.Size = UDim2.new(0.15, 0, 0.4, 0)
	typeLabel.Position = UDim2.new(0.02, 0, 0.3, 0)
	typeLabel.BackgroundTransparency = 1
	typeLabel.TextColor3 = Color3.fromRGB(255, 215, 0)
	typeLabel.Font = Enum.Font.GothamBold
	typeLabel.TextScaled = true
	
	-- Item name
	local nameLabel = Instance.new("TextLabel")
	nameLabel.Parent = button
	nameLabel.Text = item.name
	nameLabel.Size = UDim2.new(0.35, 0, 0.5, 0)
	nameLabel.Position = UDim2.new(0.18, 0, 0.25, 0)
	nameLabel.BackgroundTransparency = 1
	nameLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
	nameLabel.Font = Enum.Font.Gotham
	nameLabel.TextScaled = true
	
	-- Description
	local descLabel = Instance.new("TextLabel")
	descLabel.Parent = button
	descLabel.Text = item.description
	descLabel.Size = UDim2.new(0.35, 0, 0.4, 0)
	descLabel.Position = UDim2.new(0.18, 0, 0.55, 0)
	descLabel.BackgroundTransparency = 1
	descLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
	descLabel.Font = Enum.Font.Gotham
	descLabel.TextSize = 12
	
	-- Price tag
	local priceLabel = Instance.new("TextLabel")
	priceLabel.Parent = button
	priceLabel.Text = item.robuxtPrice .. " R$"
	priceLabel.Size = UDim2.new(0.2, 0, 0.7, 0)
	priceLabel.Position = UDim2.new(0.75, 0, 0.15, 0)
	priceLabel.BackgroundColor3 = Color3.fromRGB(100, 50, 200)
	priceLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
	priceLabel.Font = Enum.Font.GothamBold
	priceLabel.TextScaled = true
	
	return button
end

function PremiumShopUI:HandlePurchase(item)
	local Players = game:GetService("Players")
	local player = Players.LocalPlayer
	
	pcall(function()
		MarketplaceService:PromptBuyProductAsync(player, item.productId)
	end)
end

return PremiumShopUI
