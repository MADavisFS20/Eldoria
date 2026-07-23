import os
from google import genai
from google.genai import types

class AIEngine:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.model_name = model_name
        self.client = None
        self.enabled = False
        
        if os.getenv("GEMINI_API_KEY"):
            try:
                self.client = genai.Client()
                self.enabled = True
            except Exception as e:
                print(f"[AI System]: SDK Initialization error: {e}")
                self.enabled = False

    def generate_npc_response(self, npc_name, npc_persona, player_name, prompt_text):
        if not self.enabled:
            return None

        sys_instruction = (
            f"You are {npc_name}, an NPC in the fantasy RPG realm of Eldoria.\n"
            f"Persona: {npc_persona}\n"
            f"Speaking to hero: {player_name}.\n"
            "Keep responses short (1-3 sentences), highly thematic, immersion-focused."
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"Player says: '{prompt_text}'",
                config=types.GenerateContentConfig(
                    system_instruction=sys_instruction,
                    temperature=0.7,
                    max_output_tokens=120,
                )
            )
            return response.text.strip()
        except Exception:
            return None

    def generate_combat_flavor(self, player_name, enemy_name, action_taken, damage):
        if not self.enabled:
            return None

        prompt = f"Vivid one-sentence description of fantasy combat: {player_name} uses {action_taken} against {enemy_name} dealing {damage} damage."
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=50,
                )
            )
            return response.text.strip()
        except Exception:
            return None
