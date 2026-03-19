"""
Recipe skill: Search and retrieve cooking recipes.
"""

def can_handle(intent):
    i = intent.get("intent", "")
    text = (intent.get("text", "") or "").lower()
    
    return (i == "recipe" or 
            "recipe for" in text or
            "how to make" in text or
            "how do i cook" in text or
            "how to cook" in text or
            any(word in text for word in ["breakfast recipe", "dinner recipe", "dessert recipe"]))


def run(intent, context, relevant, manager):
    from jessica.memory.recipe_store import RecipeStore
    
    text = intent.get("text", "").lower()
    rs = RecipeStore()
    
    # List all recipes
    if "list recipes" in text or "what recipes" in text or "all recipes" in text:
        recipes = rs.list_all()
        if not recipes:
            return {"reply": "I don't have any recipes yet. You can teach me recipes!"}
        return {
            "reply": f"I know {len(recipes)} recipes:\n• " + "\n• ".join(recipes),
            "recipes": recipes
        }
    
    # Category search
    for category in ["breakfast", "lunch", "dinner", "dessert", "snack"]:
        if category in text:
            results = rs.get_by_category(category)
            if results:
                names = [r["name"] for r in results]
                return {
                    "reply": f"{category.title()} recipes I know:\n• " + "\n• ".join(names),
                    "recipes": names
                }
    
    # Extract search query
    query = text.replace("recipe for", "").replace("how to make", "").replace("how to cook", "").strip()
    
    # Search for recipe
    results = rs.search(query)
    
    if not results:
        return {
            "reply": f"I don't have a recipe for '{query}'. Try asking for pancakes, cookies, pasta, stir fry, or eggs. Or teach me a new recipe!"
        }
    
    if len(results) == 1:
        recipe = results[0]
        return {
            "reply": rs.format_recipe(recipe),
            "recipe": recipe
        }
    
    # Multiple matches
    names = [r["name"] for r in results]
    return {
        "reply": f"I found {len(results)} recipes matching '{query}':\n• " + "\n• ".join(names) + "\n\nAsk for a specific one!",
        "recipes": names
    }
