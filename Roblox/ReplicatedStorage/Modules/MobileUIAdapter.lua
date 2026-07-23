-- MobileUIAdapter.lua
-- Adapts UI for mobile/touch devices with optimized layouts and controls

local MobileUIAdapter = {}
local MobileUIAdapter_mt = {__index = MobileUIAdapter}

local UserInputService = game:GetService("UserInputService")
local RunService = game:GetService("RunService")

local isMobileDevice = UserInputService.TouchEnabled and not UserInputService.KeyboardEnabled

function MobileUIAdapter:new()
	local self = setmetatable({}, MobileUIAdapter_mt)
	self.isMobile = isMobileDevice
	self.touchButtons = {}
	return self
end

function MobileUIAdapter:IsMobile()
	return self.isMobile
end

function MobileUIAdapter:CreateMobileButton(text, position, size, callback)
	local button = Instance.new("TextButton")
	button.Text = text
	button.Position = position
	button.Size = size
	button.BackgroundColor3 = Color3.fromRGB(80, 80, 120)
	button.TextColor3 = Color3.fromRGB(255, 255, 255)
	button.Font = Enum.Font.GothamBold
	button.BorderSizePixel = 0
	button.TextScaled = true
	
	-- Make button more touch-friendly
	if self.isMobile then
		button.Size = size + UDim2.new(0, 20, 0, 20) -- Larger touch area
	end
	
	button.MouseButton1Click:Connect(callback)
	
	-- Add touch-specific feedback
	button.TouchBegan:Connect(function()
		button.BackgroundColor3 = Color3.fromRGB(120, 120, 160)
	end)
	
	button.TouchEnded:Connect(function()
		button.BackgroundColor3 = Color3.fromRGB(80, 80, 120)
	end)
	
	return button
end

function MobileUIAdapter:CreateMobileHUD(playerGui, playerData)
	local hudGui = Instance.new("ScreenGui")
	hudGui.Name = "MobileHUD"
	hudGui.Parent = playerGui
	hudGui.ResetOnSpawn = false
	
	-- Top bar with level and gold
	local topBar = Instance.new("Frame")
	topBar.Parent = hudGui
	topBar.Size = UDim2.new(1, 0, 0.08, 0)
	topBar.Position = UDim2.new(0, 0, 0, 0)
	topBar.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
	topBar.BorderSizePixel = 0
	
	local levelLabel = Instance.new("TextLabel")
	levelLabel.Parent = topBar
	levelLabel.Text = "LVL " .. (playerData.level or 1)
	levelLabel.Size = UDim2.new(0.2, 0, 1, 0)
	levelLabel.Position = UDim2.new(0.02, 0, 0, 0)
	levelLabel.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
	levelLabel.TextColor3 = Color3.fromRGB(255, 215, 0)
	levelLabel.Font = Enum.Font.GothamBold
	levelLabel.TextScaled = true
	
	local goldLabel = Instance.new("TextLabel")
	goldLabel.Parent = topBar
	goldLabel.Text = "$ " .. (playerData.gold or 0)
	goldLabel.Size = UDim2.new(0.2, 0, 1, 0)
	goldLabel.Position = UDim2.new(0.23, 0, 0, 0)
	goldLabel.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
	goldLabel.TextColor3 = Color3.fromRGB(255, 215, 0)
	goldLabel.Font = Enum.Font.GothamBold
	goldLabel.TextScaled = true
	
	-- Mobile action buttons (bottom right)
	local buttonSize = UDim2.new(0.15, 0, 0.08, 0)
	local padding = 0.02
	
	local attackBtn = self:CreateMobileButton("⚡ Attack", UDim2.new(0.83, 0, 0.9, 0), buttonSize, function()
		print("Mobile: Attack pressed")
	end)
	attackBtn.Parent = hudGui
	
	local defendBtn = self:CreateMobileButton("🛡 Defend", UDim2.new(0.83, 0, 0.82, 0), buttonSize, function()
		print("Mobile: Defend pressed")
	end)
	defendBtn.Parent = hudGui
	
	local potionBtn = self:CreateMobileButton(😘 Potion", UDim2.new(0.83, 0, 0.74, 0), buttonSize, function()
		print("Mobile: Potion pressed")
	end)
	potionBtn.Parent = hudGui
	
	-- Menu button (top right)
	local menuBtn = self:CreateMobileButton("☰", UDim2.new(0.9, 0, 0.01, 0), UDim2.new(0.08, 0, 0.06, 0), function()
		print("Mobile: Menu pressed")
	end)
	menuBtn.Parent = hudGui
	
	return hudGui
end

function MobileUIAdapter:CreateMobileInventory(playerGui, inventory)
	local invGui = Instance.new("ScreenGui")
	invGui.Name = "MobileInventory"
	invGui.Parent = playerGui
	
	-- Header
	local header = Instance.new("Frame")
	header.Parent = invGui
	header.Size = UDim2.new(1, 0, 0.1, 0)
	header.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
	header.BorderSizePixel = 0
	
	local headerLabel = Instance.new("TextLabel")
	headerLabel.Parent = header
	headerLabel.Text = "📦 INVENTORY"
	headerLabel.Size = UDim2.new(0.8, 0, 1, 0)
	headerLabel.BackgroundTransparency = 1
	headerLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
	headerLabel.Font = Enum.Font.GothamBold
	headerLabel.TextScaled = true
	
	local closeBtn = Instance.new("TextButton")
	closeBtn.Parent = header
	closeBtn.Text = "X"
	closeBtn.Size = UDim2.new(0.15, 0, 1, 0)
	closeBtn.Position = UDim2.new(0.85, 0, 0, 0)
	closeBtn.BackgroundColor3 = Color3.fromRGB(255, 50, 50)
	closeBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
	closeBtn.Font = Enum.Font.GothamBold
	closeBtn.TextScaled = true
	closeBtn.BorderSizePixel = 0
	closeBtn.MouseButton1Click:Connect(function()
		invGui:Destroy()
	end)
	
	-- Scrollable inventory grid
	local scrollFrame = Instance.new("ScrollingFrame")
	scrollFrame.Parent = invGui
	scrollFrame.Size = UDim2.new(1, 0, 0.9, 0)
	scrollFrame.Position = UDim2.new(0, 0, 0.1, 0)
	scrollFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
	scrollFrame.BorderSizePixel = 0
	scrollFrame.CanvasSize = UDim2.new(0, 0, #inventory * 0.15, 0)
	
	-- Create grid layout (3 items per row for mobile)
	for i, item in ipairs(inventory) do
		local itemBtn = Instance.new("TextButton")
		itemBtn.Parent = scrollFrame
		itemBtn.Text = item.name
		itemBtn.Size = UDim2.new(0.3, -10, 0.12, 0)
		local row = math.floor((i - 1) / 3)
		local col = (i - 1) % 3
		itemBtn.Position = UDim2.new(col * 0.33 + 0.02, 0, row * 0.13, 0)
		itemBtn.BackgroundColor3 = Color3.fromRGB(50, 50, 60)
		itemBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
		itemBtn.Font = Enum.Font.Gotham
		itemBtn.TextScaled = true
		itemBtn.BorderColor3 = Color3.fromRGB(150, 150, 150)
		itemBtn.BorderSizePixel = 1
	end
	
	return invGui
end

function MobileUIAdapter:OptimizeUIForMobile(screenGui)
	if not self.isMobile then return end
	
	-- Increase text sizes
	for _, element in pairs(screenGui:GetDescendants()) do
		if element:IsA("TextLabel") or element:IsA("TextButton") then
			if element.TextScaled then
				element.TextSize = 24 -- Minimum for touch
			end
		end
	end
end

function MobileUIAdapter:GetOptimalButtonSize()
	return UDim2.new(0.2, 0, 0.08, 0)
end

function MobileUIAdapter:GetOptimalScrollSpeed()
	return 50
end

return MobileUIAdapter
