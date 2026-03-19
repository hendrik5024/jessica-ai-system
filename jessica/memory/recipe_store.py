"""
Recipe database: Store and retrieve cooking recipes.
Includes common starter recipes and allows custom additions.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

RECIPES_FILE = Path(__file__).resolve().parent.parent / "data" / "recipes.json"


STARTER_RECIPES = {
    "scrambled_eggs": {
        "name": "Scrambled Eggs",
        "category": "breakfast",
        "prep_time": "5 min",
        "cook_time": "5 min",
        "servings": 2,
        "difficulty": "easy",
        "ingredients": [
            "4 eggs",
            "2 tbsp milk",
            "1 tbsp butter",
            "Salt and pepper to taste"
        ],
        "instructions": [
            "Crack eggs into a bowl, add milk, salt, and pepper. Whisk together.",
            "Heat butter in a non-stick pan over medium heat.",
            "Pour egg mixture into pan.",
            "Gently stir with a spatula, folding eggs as they cook.",
            "Cook until just set but still creamy, about 3-4 minutes.",
            "Serve immediately."
        ],
        "tags": ["breakfast", "eggs", "quick", "vegetarian"]
    },
    "spaghetti_carbonara": {
        "name": "Spaghetti Carbonara",
        "category": "dinner",
        "prep_time": "10 min",
        "cook_time": "15 min",
        "servings": 4,
        "difficulty": "medium",
        "ingredients": [
            "400g spaghetti",
            "200g pancetta or bacon, diced",
            "4 egg yolks",
            "100g Parmesan cheese, grated",
            "Black pepper",
            "Salt for pasta water"
        ],
        "instructions": [
            "Cook spaghetti in salted boiling water until al dente.",
            "While pasta cooks, fry pancetta until crispy.",
            "In a bowl, whisk egg yolks with Parmesan and black pepper.",
            "Drain pasta, reserve 1 cup pasta water.",
            "Add hot pasta to pancetta pan, remove from heat.",
            "Quickly mix in egg mixture, adding pasta water to create creamy sauce.",
            "Serve immediately with extra Parmesan."
        ],
        "tags": ["italian", "pasta", "dinner", "comfort food"]
    },
    "chocolate_chip_cookies": {
        "name": "Chocolate Chip Cookies",
        "category": "dessert",
        "prep_time": "15 min",
        "cook_time": "12 min",
        "servings": 24,
        "difficulty": "easy",
        "ingredients": [
            "2¼ cups all-purpose flour",
            "1 tsp baking soda",
            "1 tsp salt",
            "1 cup butter, softened",
            "¾ cup granulated sugar",
            "¾ cup brown sugar",
            "2 eggs",
            "2 tsp vanilla extract",
            "2 cups chocolate chips"
        ],
        "instructions": [
            "Preheat oven to 375°F (190°C).",
            "Mix flour, baking soda, and salt in a bowl.",
            "Beat butter and sugars until creamy.",
            "Add eggs and vanilla, beat well.",
            "Gradually blend in flour mixture.",
            "Stir in chocolate chips.",
            "Drop rounded tablespoons onto baking sheet.",
            "Bake 9-11 minutes until golden brown.",
            "Cool on baking sheet for 2 minutes, then transfer to wire rack."
        ],
        "tags": ["dessert", "baking", "cookies", "sweet"]
    },
    "chicken_stir_fry": {
        "name": "Chicken Stir Fry",
        "category": "dinner",
        "prep_time": "15 min",
        "cook_time": "10 min",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": [
            "500g chicken breast, sliced",
            "2 bell peppers, sliced",
            "1 broccoli head, florets",
            "2 carrots, julienned",
            "3 tbsp soy sauce",
            "2 tbsp oyster sauce",
            "1 tbsp sesame oil",
            "2 cloves garlic, minced",
            "1 tbsp ginger, minced",
            "2 tbsp vegetable oil"
        ],
        "instructions": [
            "Heat oil in wok or large pan over high heat.",
            "Add chicken, stir-fry until cooked through, about 5 minutes.",
            "Remove chicken, set aside.",
            "Add more oil, stir-fry garlic and ginger for 30 seconds.",
            "Add vegetables, stir-fry for 3-4 minutes.",
            "Return chicken to pan.",
            "Add soy sauce, oyster sauce, and sesame oil.",
            "Toss everything together for 1 minute.",
            "Serve over rice."
        ],
        "tags": ["dinner", "asian", "chicken", "healthy", "quick"]
    },
    "pancakes": {
        "name": "Fluffy Pancakes",
        "category": "breakfast",
        "prep_time": "10 min",
        "cook_time": "15 min",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": [
            "1½ cups all-purpose flour",
            "3½ tsp baking powder",
            "1 tsp salt",
            "1 tbsp sugar",
            "1¼ cups milk",
            "1 egg",
            "3 tbsp melted butter"
        ],
        "instructions": [
            "Mix flour, baking powder, salt, and sugar in a bowl.",
            "Make a well in center, pour in milk, egg, and melted butter.",
            "Mix until smooth (some lumps are okay).",
            "Heat griddle or pan over medium heat, grease lightly.",
            "Pour ¼ cup batter for each pancake.",
            "Cook until bubbles form on surface, about 2-3 minutes.",
            "Flip and cook until golden brown, another 2 minutes.",
            "Serve with syrup, butter, or fresh fruit."
        ],
        "tags": ["breakfast", "pancakes", "sweet", "family"]
    }
}


class RecipeStore:
    def __init__(self):
        self.path = RECIPES_FILE
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.recipes = self._load()
        
        # Add starter recipes if database is empty
        if not self.recipes:
            self.recipes = STARTER_RECIPES.copy()
            self.save()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.load(open(self.path, "r", encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.recipes, f, indent=2, ensure_ascii=False)

    def add_recipe(self, recipe_id: str, recipe: dict):
        """Add or update a recipe."""
        self.recipes[recipe_id] = recipe
        self.save()

    def get_recipe(self, recipe_id: str) -> Optional[dict]:
        """Get a specific recipe by ID."""
        return self.recipes.get(recipe_id)

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search recipes by name, category, or tags."""
        query_lower = query.lower()
        results = []
        
        for recipe_id, recipe in self.recipes.items():
            name = recipe.get("name", "").lower()
            category = recipe.get("category", "").lower()
            tags = [t.lower() for t in recipe.get("tags", [])]
            
            if (query_lower in name or 
                query_lower in category or 
                any(query_lower in tag for tag in tags)):
                results.append({"id": recipe_id, **recipe})
        
        return results

    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all recipes in a category."""
        return [{"id": rid, **r} for rid, r in self.recipes.items() 
                if r.get("category", "").lower() == category.lower()]

    def list_all(self) -> List[str]:
        """List all recipe names."""
        return [r.get("name", rid) for rid, r in self.recipes.items()]

    def format_recipe(self, recipe: dict) -> str:
        """Format a recipe for display."""
        lines = [
            f"📖 {recipe.get('name', 'Recipe')}",
            f"⏱️  Prep: {recipe.get('prep_time', 'N/A')} | Cook: {recipe.get('cook_time', 'N/A')}",
            f"🍽️  Servings: {recipe.get('servings', 'N/A')} | Difficulty: {recipe.get('difficulty', 'N/A')}",
            "",
            "🛒 Ingredients:"
        ]
        
        for ing in recipe.get("ingredients", []):
            lines.append(f"  • {ing}")
        
        lines.append("\n👨‍🍳 Instructions:")
        for i, step in enumerate(recipe.get("instructions", []), 1):
            lines.append(f"  {i}. {step}")
        
        return "\n".join(lines)
