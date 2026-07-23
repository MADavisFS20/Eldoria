-- SoundManager.lua
-- Manages game audio, music, and sound effects

local SoundManager = {}
local SoundManager_mt = {__index = SoundManager}

local SOUND_IDS = {
	Music = {
		MainMenu = "rbxassetid://1839930556", -- Epic orchestral (sample)
		Village = "rbxassetid://1839930556",
		Forest = "rbxassetid://1839930556",
		Mountain = "rbxassetid://1839930556",
		Boss = "rbxassetid://1839930556"
	},
	SFX = {
		ButtonClick = "rbxassetid://12221976",
		LevelUp = "rbxassetid://12221967",
		CombatStart = "rbxassetid://12221967",
		MeleeAttack = "rbxassetid://1298941278",
		MeleeHit = "rbxassetid://16373237",
		MagicAttack = "rbxassetid://1088390500",
		MagicHit = "rbxassetid://138084314",
		Healing = "rbxassetid://1298941278",
		CriticalHit = "rbxassetid://20067415",
		Victory = "rbxassetid://1435841026",
		Defeat = "rbxassetid://4397518710",
		Error = "rbxassetid://12221976"
	}
}

function SoundManager:new()
	local self = setmetatable({}, SoundManager_mt)
	self.soundInstances = {}
	self.currentMusic = nil
	self.musicVolume = 0.5
	self.sfxVolume = 0.7
	return self
end

function SoundManager:PlayMusic(musicKey, parent, looped)
	looped = looped ~= false
	
	-- Stop previous music
	if self.currentMusic then
		self.currentMusic:Stop()
		self.currentMusic:Destroy()
	end
	
	local soundId = SOUND_IDS.Music[musicKey]
	if not soundId then return false, "Music not found" end
	
	local sound = Instance.new("Sound")
	sound.SoundId = soundId
	sound.Volume = self.musicVolume
	sound.Looped = looped
	sound.Parent = parent
	sound:Play()
	
	self.currentMusic = sound
	return true
end

function SoundManager:PlaySFX(sfxKey, parent)
	local soundId = SOUND_IDS.SFX[sfxKey]
	if not soundId then return false, "SFX not found" end
	
	local sound = Instance.new("Sound")
	sound.SoundId = soundId
	sound.Volume = self.sfxVolume
	sound.Parent = parent or workspace
	sound:Play()
	
	game:GetService("Debris"):AddItem(sound, 2) -- Remove after 2 seconds
	return true
end

function SoundManager:StopMusic()
	if self.currentMusic then
		self.currentMusic:Stop()
	end
end

function SoundManager:SetMusicVolume(volume)
	self.musicVolume = math.clamp(volume, 0, 1)
	if self.currentMusic then
		self.currentMusic.Volume = self.musicVolume
	end
end

function SoundManager:SetSFXVolume(volume)
	self.sfxVolume = math.clamp(volume, 0, 1)
end

function SoundManager:GetMusicVolume()
	return self.musicVolume
end

function SoundManager:GetSFXVolume()
	return self.sfxVolume
end

return SoundManager
