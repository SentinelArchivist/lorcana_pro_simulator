# Lorcana Pro Simulator Data Contracts

This document defines the core data structures used throughout the application. These contracts serve as the "shared language" that enables modules to interact reliably.

## Card Object JSON Schema

This schema represents a single, static Lorcana card's properties. This data is loaded once from the card database.

```json
{
  "name": "string",            // Full card name (e.g., "Mickey Mouse - Brave Little Tailor")
  "cost": "integer",           // Ink cost to play the card
  "inkable": "boolean",        // True if the card can be put into the inkwell
  "color": "string",           // E.g., "Amber", "Amethyst", "Emerald", "Ruby", "Sapphire", "Steel"
  "type": "string",            // "Character", "Action", "Item"
  "subtypes": ["string"],      // E.g., ["Hero", "King", "Sorcerer"]
  "attack": "integer | null",  // Strength value; null for non-Character cards
  "defense": "integer | null", // Willpower value; null for non-Character cards
  "lore": "integer | null",    // Lore value when questing; null for non-Character cards
  "abilities": ["string"]      // Text description of abilities
}
```

## Game State JSON Schema

This schema represents the entire state of a single game at a specific moment. It is a mutable object passed between the game simulator and the AI players.

```json
{
  "turn_number": "integer",
  "active_player_index": "integer", // 0 or 1
  "players": [
    {
      "name": "string",             // Player's deck name
      "lore": "integer",
      "deck_size": "integer",
      "hand": ["Card Object JSON"], // Array of card objects in hand
      "discard_pile": ["Card Object JSON"],
      "inkwell_size": "integer",    // Total number of cards in inkwell
      "inkwell_exerted": "integer", // Number of exerted ink cards
      "board": [                  // Characters and Items in play
        {
          "card": "Card Object JSON",
          "exerted": "boolean",
          "damage": "integer",
          "can_act_this_turn": "boolean" // For characters, tracks 'summoning sickness'
        }
      ]
    },
    {
      "name": "string",
      "lore": "integer",
      // ... same structure as player 1
    }
  ],
  "game_log": ["Player Action JSON"] // A history of all actions taken
}
```

## Player Action JSON Schema

This schema represents a single, discrete action a player can take during their turn.

```json
{
  "action_type": "string", // "PLAY_CARD", "INK_CARD", "QUEST", "CHALLENGE", "PASS_TURN"
  "source_card": "string | null", // Name of the card performing the action (e.g., card being played or challenging)
  "target_card": "string | null", // Name of the card being targeted (e.g., in a challenge)
  "player_index": "integer"
}
```
