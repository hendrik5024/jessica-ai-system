"""
Financial Literacy Store: Budgeting, investing, retirement, and money management.
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FINANCIAL_LITERACY_FILE = os.path.join(DATA_DIR, "financial_literacy.json")


class FinancialLiteracyStore:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(FINANCIAL_LITERACY_FILE):
            with open(FINANCIAL_LITERACY_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = self._get_starter_knowledge()
            self.save()

    def _get_starter_knowledge(self):
        return {
            "budgeting": [
                {
                    "method": "50/30/20 Rule",
                    "description": "Simple budgeting framework for allocating after-tax income",
                    "breakdown": {
                        "50% Needs": "Essentials you can't avoid: rent, utilities, groceries, insurance, minimum debt payments",
                        "30% Wants": "Non-essentials: dining out, entertainment, hobbies, subscriptions, travel",
                        "20% Savings & Debt": "Emergency fund, retirement, investments, extra debt payments"
                    },
                    "example": "Monthly income $4,000 after tax → $2,000 needs, $1,200 wants, $800 savings/debt",
                    "tips": [
                        "Start tracking expenses for 1 month to see where money actually goes",
                        "If 50% doesn't cover needs, cut wants first before touching savings",
                        "Automate the 20% savings—pay yourself first"
                    ]
                },
                {
                    "method": "Zero-Based Budget",
                    "description": "Every dollar has a job—assign all income to categories until balance is zero",
                    "how_it_works": "Income - expenses - savings = $0. You're not leaving money unassigned.",
                    "example": "$4,000 income → $1,400 rent, $600 groceries, $200 utilities, $300 transport, $400 fun, $800 savings, $300 debt = $4,000 assigned",
                    "when_to_use": "When you need tight control or have irregular income (freelancers, commission-based)"
                },
                {
                    "concept": "Emergency Fund",
                    "description": "Savings buffer for unexpected expenses (job loss, medical, car repair)",
                    "target": "3-6 months of essential expenses (rent, food, utilities, insurance)",
                    "where_to_keep": "High-yield savings account (accessible but not too easy to touch)",
                    "priority": "Build this BEFORE investing—it prevents debt when emergencies happen"
                }
            ],
            "retirement_accounts": [
                {
                    "account": "401(k)",
                    "type": "Employer-sponsored retirement plan",
                    "how_it_works": "Pre-tax contributions from paycheck → grows tax-deferred → taxed when you withdraw in retirement",
                    "contribution_limit": "$23,000/year (2024), $30,500 if 50+",
                    "pros": [
                        "Employer match (free money! Always contribute enough to get full match)",
                        "Lowers taxable income now",
                        "High contribution limits"
                    ],
                    "cons": [
                        "Penalties if you withdraw before 59½",
                        "Limited investment options (only what employer offers)",
                        "Taxed in retirement"
                    ],
                    "key_tip": "ALWAYS contribute enough to get employer match—it's an instant 50-100% return"
                },
                {
                    "account": "Traditional IRA",
                    "type": "Individual retirement account (you open it yourself)",
                    "how_it_works": "Pre-tax contributions → grows tax-deferred → taxed when you withdraw",
                    "contribution_limit": "$7,000/year (2024), $8,000 if 50+",
                    "pros": [
                        "Tax deduction now (lowers current taxable income)",
                        "More investment choices than 401(k)"
                    ],
                    "cons": [
                        "Lower contribution limit than 401(k)",
                        "Income limits for tax deduction if you also have a 401(k)"
                    ],
                    "when_to_use": "After maxing 401(k) match, or if no employer plan"
                },
                {
                    "account": "Roth IRA",
                    "type": "Individual retirement account with after-tax contributions",
                    "how_it_works": "After-tax contributions → grows tax-free → withdrawals in retirement are TAX-FREE",
                    "contribution_limit": "$7,000/year (2024), $8,000 if 50+",
                    "pros": [
                        "No taxes in retirement (huge if you expect higher tax bracket later)",
                        "Can withdraw contributions anytime penalty-free (not earnings)",
                        "No required minimum distributions (RMDs)"
                    ],
                    "cons": [
                        "No tax deduction now",
                        "Income limits: Can't contribute if you earn too much (>$161k single, >$240k married in 2024)"
                    ],
                    "when_to_use": "If you're young/early career (lower tax bracket now, higher later)"
                },
                {
                    "comparison": "Traditional vs. Roth",
                    "key_question": "Will your tax rate be higher now or in retirement?",
                    "choose_traditional": "If high earner now, expect lower income in retirement → save on taxes today",
                    "choose_roth": "If early career or expect higher income later → pay taxes now at lower rate",
                    "pro_tip": "Many people do BOTH (401(k) for match + employer tax break, Roth IRA for tax-free growth)"
                }
            ],
            "investing_basics": [
                {
                    "concept": "Compound Interest",
                    "description": "Earning interest on your interest—exponential growth over time",
                    "formula": "A = P(1 + r)^t (Amount = Principal × (1 + rate)^years)",
                    "example": "$10,000 at 8% annual return:\n  • After 10 years: $21,589\n  • After 20 years: $46,610\n  • After 30 years: $100,627\n  Same $10k becomes $100k just by waiting!",
                    "key_insight": "Time is more powerful than amount—start investing EARLY, even if small",
                    "einstein_quote": "Compound interest is the eighth wonder of the world. He who understands it, earns it; he who doesn't, pays it."
                },
                {
                    "concept": "Index Funds vs. Individual Stocks",
                    "index_funds": {
                        "description": "Buy a basket of hundreds of stocks (e.g., S&P 500 = top 500 US companies)",
                        "pros": ["Instant diversification", "Low fees (0.03-0.20%)", "Matches market returns (~10% historically)"],
                        "cons": ["Won't outperform market", "No excitement of picking winners"],
                        "best_for": "Most people, especially beginners"
                    },
                    "individual_stocks": {
                        "description": "Buy shares of specific companies (Apple, Tesla, etc.)",
                        "pros": ["Potential to beat market", "Fun/engaging"],
                        "cons": ["Risky (company can fail)", "Requires research", "Time-consuming", "Most people underperform index funds"],
                        "best_for": "Experienced investors with time and risk tolerance"
                    },
                    "expert_consensus": "Even professional fund managers rarely beat index funds long-term. For 90%+ of people, index funds are the answer."
                },
                {
                    "concept": "Asset Allocation (Stocks vs. Bonds)",
                    "stocks": "Higher risk, higher reward. Volatile short-term, strong returns long-term (~10%/year avg)",
                    "bonds": "Lower risk, lower reward. Stable, protects against stock crashes (~3-5%/year)",
                    "rule_of_thumb": "Age in bonds (e.g., 30 years old → 30% bonds, 70% stocks). Adjust based on risk tolerance.",
                    "aggressive": "90% stocks, 10% bonds (young investors)",
                    "moderate": "60% stocks, 40% bonds (mid-career)",
                    "conservative": "40% stocks, 60% bonds (near retirement)"
                }
            ],
            "debt_management": [
                {
                    "strategy": "Debt Avalanche",
                    "description": "Pay off highest interest rate debt first",
                    "how_to": "Make minimum payments on all debts, put extra money toward highest interest rate",
                    "pros": "Saves most money on interest (mathematically optimal)",
                    "example": "Credit card (18% APR) before student loan (4% APR)"
                },
                {
                    "strategy": "Debt Snowball",
                    "description": "Pay off smallest balance first",
                    "how_to": "Make minimum payments on all debts, put extra money toward smallest balance",
                    "pros": "Quick wins boost motivation, psychological boost",
                    "example": "$500 medical bill before $20k student loan"
                },
                {
                    "concept": "Good Debt vs. Bad Debt",
                    "good_debt": "Appreciating assets or income-generating: Mortgage (home value), student loans (career earnings), business loans",
                    "bad_debt": "Depreciating or consumption: Credit cards (high interest), car loans (car loses value), payday loans (predatory)",
                    "rule": "Avoid bad debt. Use good debt strategically (low rates, builds wealth)."
                }
            ],
            "money_tips": [
                "Pay yourself first: Automate savings before you see the money",
                "Match gets you rich: Always get full employer 401(k) match",
                "High-interest debt is an emergency: Pay off credit cards ASAP (18%+ is bleeding money)",
                "Lifestyle inflation is the enemy: Don't increase spending just because income rises",
                "Time beats timing: Start investing now, don't wait for 'the right moment'",
                "Don't buy what you can't afford twice: If you can't buy it twice, you can't afford it once"
            ]
        }

    def save(self):
        with open(FINANCIAL_LITERACY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def search(self, query):
        """Search for relevant financial knowledge."""
        query_lower = query.lower()
        results = []

        # Budgeting
        if any(term in query_lower for term in ["budget", "spending", "allocate", "50/30/20", "emergency fund"]):
            results.extend([{"type": "budgeting", "data": item} for item in self.data.get("budgeting", [])])

        # Retirement accounts
        if any(term in query_lower for term in ["401k", "401(k)", "ira", "roth", "traditional", "retirement", "difference between"]):
            results.extend([{"type": "retirement", "data": item} for item in self.data.get("retirement_accounts", [])])

        # Investing
        if any(term in query_lower for term in ["invest", "compound", "interest", "index fund", "stock", "bond", "asset allocation"]):
            results.extend([{"type": "investing", "data": item} for item in self.data.get("investing_basics", [])])

        # Debt
        if any(term in query_lower for term in ["debt", "loan", "pay off", "credit card", "avalanche", "snowball"]):
            results.extend([{"type": "debt", "data": item} for item in self.data.get("debt_management", [])])

        # General tips
        if "tip" in query_lower or not results:
            results.append({"type": "tips", "data": self.data.get("money_tips", [])})

        return results[:5]  # Limit results

    def format_response(self, results):
        """Format financial knowledge for display."""
        if not results:
            return "I don't have specific financial information on that topic yet."

        output = []

        for result in results:
            if result["type"] == "budgeting":
                item = result["data"]
                if "method" in item:
                    output.append(f"💰 **{item['method']}**")
                    output.append(f"{item['description']}\n")
                    if "breakdown" in item:
                        for category, desc in item["breakdown"].items():
                            output.append(f"  **{category}:** {desc}")
                        output.append("")
                    if "example" in item:
                        output.append(f"**Example:** {item['example']}")
                    if "tips" in item:
                        output.append("**Tips:**")
                        for tip in item["tips"]:
                            output.append(f"  • {tip}")
                    output.append("")
                elif "concept" in item:
                    output.append(f"🛡️ **{item['concept']}**")
                    output.append(f"{item['description']}")
                    for key, val in item.items():
                        if key not in ["concept", "description"]:
                            output.append(f"  **{key.replace('_', ' ').title()}:** {val}")
                    output.append("")

            elif result["type"] == "retirement":
                item = result["data"]
                if "account" in item:
                    output.append(f"🏦 **{item['account']}**")
                    output.append(f"*{item['type']}*\n")
                    output.append(f"**How it works:** {item['how_it_works']}")
                    output.append(f"**Contribution limit:** {item['contribution_limit']}\n")
                    if "pros" in item:
                        output.append("**Pros:**")
                        for pro in item["pros"]:
                            output.append(f"  ✅ {pro}")
                    if "cons" in item:
                        output.append("**Cons:**")
                        for con in item["cons"]:
                            output.append(f"  ⚠️ {con}")
                    if "key_tip" in item:
                        output.append(f"\n💡 **Key tip:** {item['key_tip']}")
                    output.append("")
                elif "comparison" in item:
                    output.append(f"⚖️ **{item['comparison']}**")
                    output.append(f"**{item['key_question']}**")
                    output.append(f"  • Traditional: {item['choose_traditional']}")
                    output.append(f"  • Roth: {item['choose_roth']}")
                    output.append(f"\n💡 {item['pro_tip']}\n")

            elif result["type"] == "investing":
                item = result["data"]
                output.append(f"📈 **{item['concept']}**")
                output.append(f"{item['description']}\n")
                for key, val in item.items():
                    if key not in ["concept", "description"]:
                        if isinstance(val, dict):
                            output.append(f"**{key.replace('_', ' ').title()}:**")
                            for subkey, subval in val.items():
                                if isinstance(subval, list):
                                    output.append(f"  {subkey.replace('_', ' ').title()}:")
                                    for point in subval:
                                        output.append(f"    • {point}")
                                else:
                                    output.append(f"  {subkey.replace('_', ' ').title()}: {subval}")
                        else:
                            output.append(f"**{key.replace('_', ' ').title()}:** {val}")
                output.append("")

            elif result["type"] == "debt":
                item = result["data"]
                if "strategy" in item:
                    output.append(f"💳 **{item['strategy']}**")
                    output.append(f"{item['description']}\n")
                    output.append(f"**How to:** {item['how_to']}")
                    output.append(f"**Pros:** {item['pros']}")
                    if "example" in item:
                        output.append(f"**Example:** {item['example']}")
                    output.append("")
                elif "concept" in item:
                    output.append(f"💡 **{item['concept']}**")
                    for key, val in item.items():
                        if key != "concept":
                            output.append(f"  **{key.replace('_', ' ').title()}:** {val}")
                    output.append("")

            elif result["type"] == "tips":
                tips = result["data"]
                output.append("💡 **Money Tips:**")
                for tip in tips:
                    output.append(f"  • {tip}")
                output.append("")

        return "\n".join(output)


if __name__ == "__main__":
    store = FinancialLiteracyStore()
    results = store.search("what is the difference between 401k and IRA")
    print(store.format_response(results))
