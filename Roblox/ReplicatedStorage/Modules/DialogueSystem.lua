-- DialogueSystem.lua
-- Manages NPC dialogue with branching conversations and quest interactions

local DialogueSystem = {}
local DialogueSystem_mt = {__index = DialogueSystem}

local DIALOGUE_TREES = {
	GorwinBlacksmith = {
		npcName = "Gorwin the Blacksmith",
		greeting = "Hail, adventurer! Looking for the finest weapons in Eldoria?",
		nodes = {
			start = {
				id = "start",
				text = "I need a weapon for my journey.",
				options = {
					{text = "What do you have?", nextNode = "shop"},
					{text = "Tell me about yourself", nextNode = "backstory"},
					{text = "Farewell", nextNode = "end"}
				}
			},
			shop = {
				id = "shop",
				text = "I forge the strongest blades! Check my inventory for the best deals.",
				action = "open_shop",
				nextNode = "start"
			},
			backstory = {
				id = "backstory",
				text = "I've been smithing for 40 years. Dragons used to ravage these lands... *sighs* Those were dark times.",
				options = {
					{text = "Tell me more about the dragons", nextNode = "dragons"},
					{text = "Back to business", nextNode = "start"}
				}
			},
			dragons = {
				id = "dragons",
				text = "There's still one dragon left, atop the mountain. It's ancient and powerful. Many adventurers have tried...",
				options = {
					{text = "I'll defeat it", nextNode = "inspiration"},
					{text = "That sounds dangerous", nextNode = "start"}
				}
			},
			inspiration = {
				id = "inspiration",
				text = "Now THAT'S the spirit! Take this on your quest. [Received: Warrior's Blessing]",
				action = "give_reward",
				reward = {xp = 50, item = "WarriorBlessing"},
				nextNode = "end"
			},
			end = {
				id = "end",
				text = "Safe travels!",
				isEnd = true
			}
		}
	},
	
	AelithScout = {
		npcName = "Aelith the Scout",
		greeting = "*narrows eyes* More goblins have been spotted in the forest. Can you handle them?",
		nodes = {
			start = {
				id = "start",
				text = "I'll investigate.",
				options = {
					{text = "Tell me about the goblins", nextNode = "quest_info"},
					{text = "I need more information", nextNode = "details"},
					{text = "Not interested", nextNode = "end"}
				}
			},
			quest_info = {
				id = "quest_info",
				text = "The goblin infestation has grown out of control. We need them eliminated before they reach the village.",
				options = {
					{text = "I accept this quest", nextNode = "quest_accept"},
					{text = "Tell me more", nextNode = "details"}
				}
			},
			details = {
				id = "details",
				text = "They nest deep in the dark forest. Defeat 5 goblins and bring back proof. You'll be well rewarded.",
				options = {
					{text = "I accept", nextNode = "quest_accept"},
					{text = "Too dangerous", nextNode = "end"}
				}
			},
			quest_accept = {
				id = "quest_accept",
				text = "Excellent! Good luck, adventurer. The forest awaits.",
				action = "accept_quest",
				questId = "GoblinInfestation",
				reward = {xp = 25},
				nextNode = "end"
			},
			end = {
				id = "end",
				text = "Suit yourself.",
				isEnd = true
			}
		}
	},
	
	ThorneMountainClimber = {
		npcName = "Thorne the Climber",
		greeting = "The mountain calls to those with strength and courage. Are you ready to answer?",
		nodes = {
			start = {
				id = "start",
				text = "What lies at the peak?",
				options = {
					{text = "Tell me the full story", nextNode = "history"},
					{text = "I want to climb", nextNode = "quest_info"},
					{text = "Not now", nextNode = "end"}
				}
			},
			history = {
				id = "history",
				text = "At the summit dwells an ancient dragon. Thousands have tried to reach the peak. Few have returned.",
				options = {
					{text = "I will conquer the peak", nextNode = "quest_info"},
					{text = "That's madness", nextNode = "end"}
				}
			},
			quest_info = {
				id = "quest_info",
				text = "Defeat the dragon at the peak and prove your worth. Bring me proof of your victory.",
				options = {
					{text = "I accept this challenge", nextNode = "quest_accept"},
					{text = "I need to prepare", nextNode = "end"}
				}
			},
			quest_accept = {
				id = "quest_accept",
				text = "Go forth! Prove yourself a true hero!",
				action = "accept_quest",
				questId = "ConquerThePeak",
				reward = {xp = 100},
				nextNode = "end"
			},
			end = {
				id = "end",
				text = "When you're ready, return to me.",
				isEnd = true
			}
		}
	}
}

local DialogueClass = {}
DialogueClass.__index = DialogueClass

function DialogueClass:new(dialogueTreeId)
	local self = setmetatable({}, DialogueClass)
	self.treeId = dialogueTreeId
	self.tree = DIALOGUE_TREES[dialogueTreeId]
	self.currentNode = "start"
	self.nodeHistory = {}
	return self
end

function DialogueClass:Start()
	self.currentNode = "start"
	table.insert(self.nodeHistory, "start")
	return self.tree.greeting
end

function DialogueClass:GetCurrentNode()
	return self.tree.nodes[self.currentNode]
end

function DialogueClass:GetOptions()
	local node = self:GetCurrentNode()
	if not node then return {} end
	return node.options or {}
end

function DialogueClass:SelectOption(optionIndex)
	local node = self:GetCurrentNode()
	if not node or not node.options or optionIndex < 1 or optionIndex > #node.options then
		return false, "Invalid option"
	end
	
	local selectedOption = node.options[optionIndex]
	self.currentNode = selectedOption.nextNode
	table.insert(self.nodeHistory, self.currentNode)
	
	return true, self:GetCurrentNode()
end

function DialogueClass:GetNodeText()
	local node = self:GetCurrentNode()
	return node and node.text or ""
end

function DialogueClass:IsDialogueEnd()
	local node = self:GetCurrentNode()
	return node and node.isEnd or false
end

function DialogueClass:GetAction()
	local node = self:GetCurrentNode()
	return node and node.action or nil
end

function DialogueClass:GetQuestId()
	local node = self:GetCurrentNode()
	return node and node.questId or nil
end

function DialogueClass:GetReward()
	local node = self:GetCurrentNode()
	return node and node.reward or nil
end

function DialogueSystem:StartDialogue(npcId)
	return DialogueClass:new(npcId):Start()
end

function DialogueSystem:CreateDialogue(npcId)
	return DialogueClass:new(npcId)
end

function DialogueSystem:GetAllDialogueTrees()
	return DIALOGUE_TREES
end

function DialogueSystem:GetDialogueTree(treeId)
	return DIALOGUE_TREES[treeId]
end

return DialogueSystem
