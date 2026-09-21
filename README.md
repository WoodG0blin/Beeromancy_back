# **Beeromancy**  
**An inventory-driven brewing assistant for homebrewers.**  
Beeromancy is a personal project that helps homebrewers design recipes, track brewing process, and — most importantly — **brew with what you already have**. Unlike existing tools that start from a recipe and ask you to buy ingredients, Beeromancy starts from your inventory and tells you what you can brew, what can be substituted, and how much it will cost.  
**Status:** early development. The data pipeline (parsing → cleaning → aggregation → database) is functional. API, client, and inventory features are in progress.  
## **Why this project exists**  
I brew beer at home. Like many homebrewers, I kept recipes on paper, juggled external timers during brew day, and constantly checked what ingredients I actually had in stock. Existing apps (BeerSmith, Brewfather, Brew Pilot) are powerful, but they are **recipe-first**, not  **inventory-first**:  
- You design a recipe, then discover you're missing half the ingredients.  
- Substitutions are based on style categories, not on what you have.  
- Local pricing and local shops (especially in Russia) are not integrated.  
- The loop "what's in stock → what can I brew → what do I need to buy → how much does it cost" is fragmented.  
Beeromancy is an attempt to close that loop. It is **not a commercial product** — it's a learning project and a tool for personal use, but built with production-grade engineering practices.  
## **Core concept: inventory-driven brewing**  
The central idea is simple: **your inventory is the starting point, not an afterthought.**  
- **Recipe design** — from scratch, from a published recipe, or from a previous batch.  
- **Batch scaling** — recalculate ingredient amounts for your target volume or kettle size.  
- **Brew day guidance** — phase sequence, temperature hints, duration limits, built-in timers.  
- **Inventory tracking** — know what you have, get reminders when you're running low.  
- **Substitutions** — find ingredient alternatives based on actual characteristics, not just style labels.  
- **Cost estimation** — ingredient prices from major online shops, batch cost breakdown.  
- **Batch evaluation** — rate the result, leave notes for the next iteration.  
## **Architecture**  
**Client:** Unity (mobile) — planned.  
 **Backend:** Python (FastAPI) — in progress.  
 **Database:** SQLite for development, DIM/FACT schema.  
### **Key technical decisions**  
- **DIM/FACT modeling** — separate reference tables (dim_ingredients, dim_producers, dim_countries) from fact tables (fact_recipes, fact_prices).  
- **Source prioritization** — when two shops provide conflicting data, priority is resolved via np.select with a fallback chain (structured characteristics → full description → short description → additional info).  
- **Master name matching** — the same product has different names in different shops; matching is done via a dim_ingredient_mapping table and a "most common variant" heuristic.  
- **Cyrillic URL handling** — a custom Scrapy middleware decodes IDNA-encoded domains back to Cyrillic via process_response.  
## **Tech stack**  
- **Python 3.x**  
- **Scrapy** — parsing  
- **pandas** — data transformation  
- **SQLAlchemy** — ORM  
- **SQLite** — storage  
- **pytest** — testing  
- **FastAPI** — API (in progress)  
## **Current status**  
**Done:**  
- Scrapy parsers for two Russian shops (beer.rf, grainrus) with pagination and per-package price handling.  
- Data cleaning and normalization pipeline.  
- Characteristic extraction (malt: color, extract, protein, share, kolbach, diastatic; hop: alpha, beta, cohumulon, oils; yeast: attenuation, flocculation, fermentation temp, alcohol tolerance, diastatic, phenolic).  
- Aggregation with source prioritization.  
- DIM/FACT database schema (SQLAlchemy ORM).  
- Parametrized tests for cleaning and characteristic extraction, including edge cases (non-breaking space, zero-width space, BOM, control characters).  
**In ** **progress** **:**  
- Fixing critical bugs in the database loading step.  
- API on FastAPI (ingredients → recipes → inventory).  
- README and project packaging.  
**Planned** **:**  
- Docker deployment.  
- Unity client.  
- Inventory tracking and substitution engine.  
- Price integration with local shops.  
## **Tests covering**  
- String cleaning edge cases (\xa0, \u200b, \ufeff, control characters).  
- Name parsing and metadata extraction.  
- Characteristic extraction for malts, hops, yeasts.  
- Data cleaning pipeline on a real data slice.  
## **Roadmap**  
1. **Minimal API** — CRUD for ingredients, recipes, inventory.  
2. **Docker + deployment** — containerize and run on a VPS.  
3. **Basic client** — Unity or minimal web frontend.  
4. **Inventory + substitutions** — the core differentiator.  
5. **Refactoring** — section by section, with accumulated context.  
## **About**  
Personal learning project by a career-switcher moving from economics/strategy into Python backend development. Built with an emphasis on real-world data complexity, clean architecture, and iterative improvement.  
**Not intended for commercial use.** Feedback and code review are welcome.  
   
