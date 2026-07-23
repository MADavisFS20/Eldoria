-- CombatSystem.lua
-- Handles turn-based combat between players and enemies

local CombatSystem = {}

local ENEMIES = {
	Goblin = {
		name = "Goblin",
		healthMax = 25,
		health = 25,
		attack = 8,
		defense = 2,
		experienceReward = 25,
		goldReward = 10
	},
	Orc = {
		name = "Orc",
		healthMax = 50,
		health = 50,
		attack = 15,
		defense = 5,
		experienceReward = 50,
		goldReward = 30
	},
	Dragon = {
		name = "Dragon",
		healthMax = 200,
		health = 200,
		attack = 40,
		defense = 20,
		experienceReward = 500,
		goldReward = 250
	}
}

local EncounterClass = {}
EncounterClass.__index = EncounterClass

function EncounterClass:new(player, enemyType)
	local self = setmetatable({}, EncounterClass)
	
	self.player = player
	self.enemyTemplate = ENEMIES[enemyType]
	self.enemy = {
		name = self.enemyTemplate.name,
		healthMax = self.enemyTemplate.healthMax,
		health = self.enemyTemplate.health,
		attack = self.enemyTemplate.attack,
		defense = self.enemyTemplate.defense
	}
	
	self.combatLog = {}
	self.turn = 0
	self.playerTurn = true
	
	return self
end

function EncounterClass:PlayerAttack()
	self.turn = self.turn + 1
	local playerDamage = self.player:GetTotalAttack()
	local actualDamage = math.max(1, playerDamage - self.enemy.defense)
	
	self.enemy.health = math.max(0, self.enemy.health - actualDamage)
	
	table.insert(self.combatLog, {
		actor = "Player",
		action = "attack",
		damage = actualDamage,
		targetHealth = self.enemy.health
	})
	
	return actualDamage, self.enemy.health <= 0
end

function EncounterClass:EnemyAttack()
	self.turn = self.turn + 1
	local enemyDamage = math.random(self.enemy.attack - 3, self.enemy.attack + 3)
	local actualDamage = self.player:TakeDamage(enemyDamage)
	
	table.insert(self.combatLog, {
		actor = "Enemy",
		action = "attack",
		damage = actualDamage,
		targetHealth = self.player.character.currentHealth
	})
	
	return actualDamage, not self.player:IsAlive()
end

function EncounterClass:PlayerUsePotion()
	self.turn = self.turn + 1
	local healAmount = 50
	self.player.character.currentHealth = math.min(self.player.character.maxHealth, self.player.character.currentHealth + healAmount)
	
	table.insert(self.combatLog, {
		actor = "Player",
		action = "potion",
		healing = healAmount,
		targetHealth = self.player.character.currentHealth
	})
end

function EncounterClass:IsPlayerTurn()
	return self.playerTurn
end

function EncounterClass:SwitchTurn()
	self.playerTurn = not self.playerTurn
end

function EncounterClass:IsEncounterOver()
	return self.enemy.health <= 0 or not self.player:IsAlive()
end

function EncounterClass:GetRewards()
	if self.enemy.health <= 0 then
		return {
			experience = self.enemyTemplate.experienceReward,
			gold = self.enemyTemplate.goldReward,
			victory = true
		}
	else
		return {
			experience = 0,
			gold = 0,
			victory = false
		}
	end
end

function CombatSystem:StartEncounter(player, enemyType)
	return EncounterClass:new(player, enemyType)
end

function CombatSystem:GetEnemies()
	return ENEMIES
end

return CombatSystem
