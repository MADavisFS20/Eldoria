import os

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

class AIEngine:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.model_name = model_name
        self.client = None
        self.enabled = False

        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and genai is None:
            print("[AI Engine]: GEMINI_API_KEY is set but the 'google-genai' package is not installed. Run: pip install google-genai")
        elif api_key:
            try:
                self.client = genai.Client(api_key=api_key)
                self.enabled = True
            except Exception as e:
                print(f"[AI Engine]: Initialization failed: {e}")
                self.enabled = False

    def _generate_content(self, system_instruction: str, contents: str, temperature: float, max_output_tokens: int) -> str | None:
        if not self.enabled:
            return None
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                )
            )
            return response.text.strip()
        except Exception:
            return None

    def generate_npc_response(self, npc_name: str, npc_persona: str, player, prompt_text: str, location_name: str) -> str:
        sys_instruction = (
            f"You are {npc_name}, located at {location_name} in Eldoria.\n"
            f"Persona: {npc_persona}\n"
            f"Speaking to: {player.name} (Class: {player.player_class.name}, Lvl: {player.level}).\n"
            "Keep responses strictly within 1-3 sentences. Focus on high fantasy lore and world depth."
        )
        return self._generate_content(sys_instruction, f"Player says: '{prompt_text}'", 0.7, 120)

    def generate_location_flavor(self, location_name: str, description: str, player_level: int) -> str:
        prompt = f"Location: {location_name}. Base Info: {description}. Hero Level: {player_level}."
        sys_instruction = "Act as an immersive Dungeon Master. Provide a 2-sentence ambient sensory description."
        return self._generate_content(sys_instruction, prompt, 0.8, 80)

    def generate_combat_flavor(self, player_name: str, enemy_name: str, action: str, damage: int) -> str:
        prompt = f"Action: {player_name} performs {action} on {enemy_name} causing {damage} damage."
        sys_instruction = "Viscerally describe this fantasy attack in 1 dynamic sentence."
        return self._generate_content(sys_instruction, prompt, 0.85, 50)

    def generate_backstory(self, player_name: str, player_class_name: str, player_class_description: str) -> str:
        sys_instruction = "You are a mystical storyteller. Generate a 3-sentence origin story for a new RPG character, focusing on their class and potential destiny."
        contents = f"Character Name: {player_name}. Class: {player_class_name}. Class Description: {player_class_description}."
        return self._generate_content(sys_instruction, contents, 0.75, 150)

    def generate_item_flavor(self, item_name: str, base_description: str, item_type: str) -> str:
        sys_instruction = "You are a seasoned merchant describing an item. Provide a 1-2 sentence evocative description, expanding on its basic info and hinting at its utility or lore."
        contents = f"Item Name: {item_name}. Type: {item_type}. Basic Description: {base_description}."
        return self._generate_content(sys_instruction, contents, 0.7, 100)

    def generate_enemy_flavor(self, enemy_name: str, player_level: int) -> str:
        sys_instruction = "You are a Dungeon Master. Describe the appearance and immediate threat of an enemy in 1-2 vivid sentences, suitable for a fantasy RPG encounter."
        contents = f"Enemy: {enemy_name}. Player Level: {player_level}."
        return self._generate_content(sys_instruction, contents, 0.8, 100)

    def generate_quest_flavor(self, quest_name: str, base_description: str, player_level: int, is_completion: bool = False) -> str:
        if is_completion:
            sys_instruction = "You are a wise chronicler. Write a 2-sentence celebratory message for completing a quest, highlighting the hero's achievement."
            contents = f"Quest Completed: {quest_name}. Original Goal: {base_description}. Hero Level: {player_level}."
        else:
            sys_instruction = "You are a quest giver. Elaborate on a quest's purpose and initial challenge in 2-3 sentences, making it sound intriguing."
            contents = f"Quest Name: {quest_name}. Basic Description: {base_description}. Player Level: {player_level}."
        return self._generate_content(sys_instruction, contents, 0.75, 150)

    def generate_perk_flavor(self, perk_name: str, base_description: str, perk_level: int) -> str:
        sys_instruction = "You are a mystical mentor. Describe the essence and benefit of a character perk in 1-2 sentences, inspiring the player."
        contents = f"Perk Name: {perk_name}. Basic Description: {base_description}. Current Level: {perk_level}."
        return self._generate_content(sys_instruction, contents, 0.7, 100)

    def generate_game_over_flavor(self, player_name: str, enemy_name: str, location_name: str) -> str:
        sys_instruction = "You are a somber chronicler. Write a 2-sentence dramatic game over message, detailing the hero's final moments and the impact of their defeat in the fantasy world."
        contents = f"Hero: {player_name}. Defeated by: {enemy_name}. Location: {location_name}."
        return self._generate_content(sys_instruction, contents, 0.9, 120)
