import json
from pathlib import Path

from data_processers import ScrapedDataProcesser
from db_connect import DatabaseController


def process():
    path = Path(__file__).parent.parent / "outputs"
    processer = ScrapedDataProcesser(path)
    with open(path / "products_data.json", 'r', encoding='utf-8') as f:
        processer.load_data(f)

    with DatabaseController() as db:
        names_mapping = db.get_ingredients_mapping()
        processer.process_data(names_mapping)

        if db.try_prepare_for_loading(processer.new_mapping): #caching dim countries, producers and types, setting new mapping
            for t, data in processer.entries_to_add:
                db.load_ingredients_from_df(data, t)

        if db.try_prepare_for_update(processer.update_mapping): #pre-loading items to update
            for t, data in processer.entries_to_update:
                db.update_ingredients_from_df(data, t)
            log = db.question_log
            with open(path / "question_log.json", 'w', encoding='utf-8') as f:
                json.dump(log, f, ensure_ascii=False, indent=2)

        # pass the whole dataframe with prices to price manager for load
        print(f"To update prices redirected {len(processer.known_ingr)} entries")

def scrape():
    scraper = ScrapedDataProcesser()
    scraper.scrape_data()

if __name__ == "__main__":
    process()