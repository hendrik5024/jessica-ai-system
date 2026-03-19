<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# JESSICA AI — Offline Personal AI Assistant

## Project Overview
Jessica is a fully offline AI system with adaptive learning, semantic memory, dual-model LLM routing (chat + coding), and 17 specialized knowledge stores covering emotional intelligence, specialized knowledge, creative thinking, practical life skills, and four major life domains (critical thinking, professional diplomacy, systems thinking, digital wellness).

## Current Status
- ✅ Self-learning pipeline with LoRA adapters (export, train, convert, promote)
- ✅ Multi-model support with automated scheduling (6-hour intervals)
- ✅ Context memory (chat history, entity tracking, knowledge import)
- ✅ Chess and recipe skills
- ✅ 17 knowledge stores across 6 categories
- ✅ **7-Layer Meta-Cognition Stack** (MetaObserver, SelfModel, LongTermGoals, Counterfactual, Response States, ReflectionWindow, AlignmentTracker)
- ✅ **Identity Anchors** (9 persistent principles across PURPOSE, BOUNDARY, BECOMING)
- ✅ **Causal World Models** (5 domains with cause→effect understanding, outcome prediction, intervention planning)
- ✅ **Autodidactic Loop** (weekly learning cycles, failure tracking, synthetic data generation, self-improvement)
- ✅ **Phase 87-92 Cognitive Architecture** (cognitive kernel, beliefs, permissions, autonomy proposals)

## Knowledge Domains
### Emotional Intelligence (3 stores)
- emotional_intelligence_store.py: Active listening, empathy responses, emotional vocabulary
- conflict_resolution_store.py: Nonviolent Communication, FBI negotiation, DESC Script, Aikido
- decision_making_store.py: Eisenhower Matrix, Pros/Cons, 10-10-10, Regret Minimization

### Specialized Knowledge (3 stores)
- financial_literacy_store.py: 50/30/20 budgeting, 401(k) vs IRA, compound interest, debt strategies
- travel_planning_store.py: Vibe-based planning, Tokyo/Lisbon/Reykjavik itineraries
- tech_support_store.py: Keyboard shortcuts, coding principles, troubleshooting

### Creative Thinking (2 stores)
- thinking_frameworks_store.py: Six Thinking Hats, First Principles, Inversion, SCAMPER
- storytelling_store.py: Hero's Journey (12 stages), Three-Act Structure, Save the Cat

### Practical Life (4 stores)
- etiquette_store.py: Formal introductions, thank-you notes, RSVP, tipping
- first_aid_store.py: CPR, choking, burns, cuts, sprains
- home_maintenance_store.py: Faucets, drains, breakers, water heaters
- recipe_store.py: Breakfast, dinner, dessert recipes

### Four Major Domains (4 stores - NEW)
1. logical_fallacies_store.py: 11 fallacies (Ad Hominem, Straw Man, Sunk Cost, etc.), Socratic questioning with 6 question types, critical thinking checklist, cognitive biases
2. professional_communication_store.py: Feedback frameworks (Sandwich, SBI), "I" statements, 5 email templates, 3 difficult conversation scripts, professional phrase upgrades
3. systems_thinking_store.py: 5 Whys root cause analysis, cooking substitution chemistry for 5 ingredients, DMAIC framework
4. digital_wellness_store.py: 7-question source verification, misinformation recognition, digital security (2FA, passwords, phishing), digital ethics, healthy habits

## Integration Status
- ✅ All 17 stores created and functional
- ✅ Integrated into advice_skill.py with category routing
- ✅ Intent parser updated with keywords for all domains
- ✅ End-to-end testing passed (6/6 test queries)
- ✅ Meta-cognition stack integrated into agent_loop.py
- ✅ Identity anchors integrated with persistence layer
- ✅ Causal world models implemented with 5 domain models (23/23 tests passing)
- ✅ Autodidactic loop system implemented with failure tracking, data generation, and weekly cycles (16/16 tests passing)
- ✅ **Phase 87-92 Complete** (223/223 tests passing across all cognitive phases)
- ✅ **Phase 720-780 Intelligence & Planning** (architecture mapping, dependency graphs, autonomous debugging, multi-agent orchestration, task planning)
- ✅ **Phase 800 Autonomous Agent Creation** (self-evolving intelligence, pattern detection, automatic agent generation and registration)

## Example Queries
- "What is ad hominem fallacy?"
- "Help me write an email to a coworker missing deadlines"
- "What's a substitute for eggs in baking?"
- "How do I spot phishing emails?"
- "Why is my car not starting? Use 5 whys"
- "Give me a Tokyo itinerary"
- "How do I use Six Thinking Hats?"
- "What would happen if I get 8 hours of sleep?" (causal prediction)
- "How can I improve my focus?" (intervention planning)
- "search internet for weather" (generates high-risk proposal requiring approval)
- "open file config.yaml" (generates medium-risk proposal)
- "calculate 2 + 2" (generates low-risk proposal)
- Jessica automatically identifies and improves her weakest skills weekly (autodidactic learning)
- Repeat "analyze project" 3 times → Jessica auto-creates AnalyzeProjectAgent (Phase 800 autonomous agent creation)
- "agent AnalyzeProjectAgent" (execute generated agent)
- "multi-agent analyze codebase" (parallel orchestration with auto-generated agents)

## Development Guidelines
- [ ] Verify that the copilot-instructions.md file in the .github directory is created.

- [ ] Clarify Project Requirements
	<!-- Ask for project type, language, and frameworks if not specified. Skip if already provided. -->

- [ ] Scaffold the Project
	<!--
	Ensure that the previous step has been marked as completed.
	Call project setup tool with projectType parameter.
	Run scaffolding command to create project files and folders.
	Use '.' as the working directory.
	If no appropriate projectType is available, search documentation using available tools.
	Otherwise, create the project structure manually using available file creation tools.
	-->

- [ ] Customize the Project
	<!--
	Verify that all previous steps have been completed successfully and you have marked the step as completed.
	Develop a plan to modify codebase according to user requirements.
	Apply modifications using appropriate tools and user-provided references.
	Skip this step for "Hello World" projects.
	-->

- [ ] Install Required Extensions
	<!-- ONLY install extensions provided mentioned in the get_project_setup_info. Skip this step otherwise and mark as completed. -->

- [ ] Compile the Project
	<!--
	Verify that all previous steps have been completed.
	Install any missing dependencies.
	Run diagnostics and resolve any issues.
	Check for markdown files in project folder for relevant instructions on how to do this.
	-->

- [ ] Create and Run Task
	<!--
	Verify that all previous steps have been completed.
	Check https://code.visualstudio.com/docs/debugtest/tasks to determine if the project needs a task. If so, use the create_and_run_task to create and launch a task based on package.json, README.md, and project structure.
	Skip this step otherwise.
	 -->

- [ ] Launch the Project
	<!--
	Verify that all previous steps have been completed.
	Prompt user for debug mode, launch only if confirmed.
	 -->

- [ ] Ensure Documentation is Complete
	<!--
	Verify that all previous steps have been completed.
	Verify that README.md and the copilot-instructions.md file in the .github directory exists and contains current project information.
	Clean up the copilot-instructions.md file in the .github directory by removing all HTML comments.
	 -->

<!--
## Execution Guidelines
PROGRESS TRACKING:
- If any tools are available to manage the above todo list, use it to track progress through this checklist.
- After completing each step, mark it complete and add a summary.
- Read current todo list status before starting each new step.

COMMUNICATION RULES:
- Avoid verbose explanations or printing full command outputs.
- If a step is skipped, state that briefly (e.g. "No extensions needed").
- Do not explain project structure unless asked.
- Keep explanations concise and focused.

DEVELOPMENT RULES:
- Use '.' as the working directory unless user specifies otherwise.
- Avoid adding media or external links unless explicitly requested.
- Use placeholders only with a note that they should be replaced.
- Use VS Code API tool only for VS Code extension projects.
- Once the project is created, it is already opened in Visual Studio Code—do not suggest commands to open this project in Visual Studio again.
- If the project setup information has additional rules, follow them strictly.

FOLDER CREATION RULES:
- Always use the current directory as the project root.
- If you are running any terminal commands, use the '.' argument to ensure that the current working directory is used ALWAYS.
- Do not create a new folder unless the user explicitly requests it besides a .vscode folder for a tasks.json file.
- If any of the scaffolding commands mention that the folder name is not correct, let the user know to create a new folder with the correct name and then reopen it again in vscode.

EXTENSION INSTALLATION RULES:
- Only install extension specified by the get_project_setup_info tool. DO NOT INSTALL any other extensions.

PROJECT CONTENT RULES:
- If the user has not specified project details, assume they want a "Hello World" project as a starting point.
- Avoid adding links of any type (URLs, files, folders, etc.) or integrations that are not explicitly required.
- Avoid generating images, videos, or any other media files unless explicitly requested.
- If you need to use any media assets as placeholders, let the user know that these are placeholders and should be replaced with the actual assets later.
- Ensure all generated components serve a clear purpose within the user's requested workflow.
- If a feature is assumed but not confirmed, prompt the user for clarification before including it.
- If you are working on a VS Code extension, use the VS Code API tool with a query to find relevant VS Code API references and samples related to that query.

TASK COMPLETION RULES:
- Your task is complete when:
  - Project is successfully scaffolded and compiled without errors
  - copilot-instructions.md file in the .github directory exists in the project
  - README.md file exists and is up to date
  - User is provided with clear instructions to debug/launch the project

Before starting a new task in the above plan, update progress in the plan.
-->
- Work through each checklist item systematically.
- Keep communication concise and focused.
- Follow development best practices.
