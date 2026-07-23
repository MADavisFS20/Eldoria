-- CombatEffectsSystem.lua
-- Handles combat animations, visual effects, and feedback

local CombatEffectsSystem = {}

local COMBAT_EFFECTS = {
	MeleeAttack = {
		duration = 0.5,
		effect = "slash",
		color = Color3.fromRGB(255, 100, 0),
		damagePopupColor = Color3.fromRGB(255, 50, 50)
	},
	SpellAttack = {
		duration = 1.0,
		effect = "magical_burst",
		color = Color3.fromRGB(100, 150, 255),
		damagePopupColor = Color3.fromRGB(100, 150, 255)
	},
	Healing = {
		duration = 0.75,
		effect = "heal_pulse",
		color = Color3.fromRGB(100, 255, 100),
		damagePopupColor = Color3.fromRGB(100, 255, 100)
	},
	CriticalHit = {
		duration = 0.75,
		effect = "critical_burst",
		color = Color3.fromRGB(255, 215, 0),
		damagePopupColor = Color3.fromRGB(255, 215, 0)
	},
	Defense = {
		duration = 0.5,
		effect = "shield",
		color = Color3.fromRGB(150, 150, 255),
		damagePopupColor = Color3.fromRGB(150, 150, 255)
	}
}

function CombatEffectsSystem:CreateDamagePopup(parent, damage, effectType, position)
	local effect = COMBAT_EFFECTS[effectType] or COMBAT_EFFECTS.MeleeAttack
	
	local popup = Instance.new("TextLabel")
	popup.Name = "DamagePopup"
	popup.Parent = parent
	popup.Text = tostring(damage)
	popup.Size = UDim2.new(0.1, 0, 0.08, 0)
	popup.Position = position or UDim2.new(0.5, 0, 0.5, 0)
	popup.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
	popup.TextColor3 = effect.damagePopupColor
	popup.Font = Enum.Font.GothamBold
	popup.TextScaled = true
	popup.BorderSizePixel = 2
	popup.BorderColor3 = effect.damagePopupColor
	
	-- Animate popup floating upward
	local startPos = popup.Position
	local startTime = tick()
	
	while popup.Parent and (tick() - startTime) < effect.duration do
		local elapsed = tick() - startTime
		local progress = elapsed / effect.duration
		
		popup.Position = startPos + UDim2.new(0, 0, -progress * 0.15, 0)
		popup.TextTransparency = progress
		
		wait(0.016) -- 60 FPS
	end
	
	if popup.Parent then
		popup:Destroy()
	end
end

function CombatEffectsSystem:PlayAttackAnimation(targetFrame, effectType)
	local effect = COMBAT_EFFECTS[effectType] or COMBAT_EFFECTS.MeleeAttack
	
	local originalColor = targetFrame.BackgroundColor3
	local flashCount = 0
	local maxFlashes = 3
	
	while flashCount < maxFlashes do
		targetFrame.BackgroundColor3 = effect.color
		wait(0.1)
		targetFrame.BackgroundColor3 = originalColor
		wait(0.1)
		flashCount = flashCount + 1
	end
end

function CombatEffectsSystem:PlayHealthBarUpdate(healthBar, newPercentage)
	local targetSize = UDim2.new(newPercentage / 100, 0, 1, 0)
	local startSize = healthBar.Size
	local startTime = tick()
	local duration = 0.3
	
	while (tick() - startTime) < duration do
		local elapsed = tick() - startTime
		local progress = elapsed / duration
		
		healthBar.Size = startSize:Lerp(targetSize, progress)
		wait(0.016)
	end
	
	healthBar.Size = targetSize
end

function CombatEffectsSystem:CreateCombatLog(parent, actionText)
	local logLabel = Instance.new("TextLabel")
	logLabel.Parent = parent
	logLabel.Text = actionText
	logLabel.Size = UDim2.new(0.8, 0, 0.08, 0)
	logLabel.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
	logLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
	logLabel.Font = Enum.Font.GothamMonospace
	logLabel.TextScaled = true
	logLabel.TextXAlignment = Enum.TextXAlignment.Left
	
	-- Auto-remove after 3 seconds
	game:GetService("Debris"):AddItem(logLabel, 3)
end

function CombatEffectsSystem:ShowBuffIcon(parent, buffName, duration)
	local buffFrame = Instance.new("Frame")
	buffFrame.Parent = parent
	buffFrame.Size = UDim2.new(0.05, 0, 0.05, 0)
	buffFrame.BackgroundColor3 = Color3.fromRGB(100, 255, 100)
	buffFrame.BorderSizePixel = 1
	buffFrame.BorderColor3 = Color3.fromRGB(50, 150, 50)
	
	local label = Instance.new("TextLabel")
	label.Parent = buffFrame
	label.Text = buffName:sub(1, 1):upper()
	label.Size = UDim2.new(1, 0, 1, 0)
	label.BackgroundTransparency = 1
	label.TextColor3 = Color3.fromRGB(0, 0, 0)
	label.Font = Enum.Font.GothamBold
	
	if duration then
		game:GetService("Debris"):AddItem(buffFrame, duration)
	end
	
	return buffFrame
end

function CombatEffectsSystem:PlayVictoryAnimation(victoryFrame)
	local originalSize = victoryFrame.Size
	local bounceCount = 0
	
	while bounceCount < 3 do
		victoryFrame.Size = originalSize * 1.2
		wait(0.1)
		victoryFrame.Size = originalSize
		wait(0.1)
		bounceCount = bounceCount + 1
	end
end

function CombatEffectsSystem:PlayDefeatAnimation(defeatFrame)
	local startTime = tick()
	local duration = 1.0
	
	while (tick() - startTime) < duration do
		local elapsed = tick() - startTime
		local progress = elapsed / duration
		
		defeatFrame.Rotation = progress * 5
		defeatFrame.TextTransparency = progress
		
		wait(0.016)
	end
end

return CombatEffectsSystem
