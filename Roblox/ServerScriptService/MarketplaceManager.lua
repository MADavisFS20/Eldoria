-- MarketplaceManager.lua
-- Handles Robux purchases and premium item distribution

local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local DataStoreService = game:GetService("DataStoreService")

-- IMPORTANT: Replace these with your actual product IDs from Roblox Creator Hub
local PRODUCT_IDS = {
	-- Premium Cosmetics
	DRACON_KNIGHT_SKIN = 0, -- Replace with actual ID
	FIREMAGE_SKIN = 0,
	ICEWIZARD_SKIN = 0,
	
	-- Weapons
	DRAGON_FANG_BLADE = 0,
	RUNIC_WARHAMMER = 0,
	MYSTIC_STAFF = 0,
	
	-- Boosts
	xp_BOOSTER_1H = 0,
	xp_BOOSTER_24H = 0,
	
	-- Battle Pass
	BATTLE_PASS_SEASON_1 = 0,
	
	-- Other
	INVENTORY_EXPANSION = 0,
	CHARACTER_SLOT = 0
}

local function processPurchase(player, productId, price)
	local playerData = ReplicatedStorage:WaitForChild("PlayerData")
	
	-- Find which premium item was purchased
	local itemGranted = false
	
	if productId == PRODUCT_IDS.DRACON_KNIGHT_SKIN then
		local cosmetics = playerData:FindFirstChild("Cosmetics") or Instance.new("Folder")
		cosmetics.Parent = playerData
		local skin = Instance.new("StringValue")
		skin.Name = "DraconKnightSkin"
		skin.Value = "owned"
		skin.Parent = cosmetics
		itemGranted = true
		
	elseif productId == PRODUCT_IDS.xp_BOOSTER_1H then
		local buffs = playerData:FindFirstChild("Buffs") or Instance.new("Folder")
		buffs.Parent = playerData
		local booster = Instance.new("IntValue")
		booster.Name = "XPBooster1H"
		booster.Value = os.time() + 3600 -- 1 hour from now
		booster.Parent = buffs
		itemGranted = true
		
	elseif productId == PRODUCT_IDS.BATTLE_PASS_SEASON_1 then
		local battlePass = playerData:FindFirstChild("BattlePass") or Instance.new("Folder")
		battlePass.Parent = playerData
		local season1 = Instance.new("BoolValue")
		season1.Name = "Season1Purchased"
		season1.Value = true
		season1.Parent = battlePass
		itemGranted = true
	end
	
	if itemGranted then
		local events = ReplicatedStorage:WaitForChild("Events")
		events:WaitForChild("PurchaseComplete"):FireClient(player, productId)
		print("Premium item granted to " .. player.Name .. " (Product ID: " .. productId .. ")")
	else
		print("Unknown product ID: " .. productId)
	end
end

local function onProcessReceipt(receiptInfo)
	local player = Players:GetPlayerByUserId(receiptInfo.PlayerId)
	
	if not player then
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
	
	-- Process the purchase
	local success, err = pcall(function()
		processPurchase(player, receiptInfo.ProductId, receiptInfo.Price)
	end)
	
	if success then
		return Enum.ProductPurchaseDecision.PurchaseGranted
	else
		print("Error processing purchase: " .. err)
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
end

MarketplaceService.ProcessReceipt = onProcessReceipt

print("MarketplaceManager initialized")
