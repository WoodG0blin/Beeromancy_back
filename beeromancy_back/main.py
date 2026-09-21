from parsers import crawler

from data_processers import ScrapedDataProcesser
from db_connect import DatabaseController
from data_processers import aggregator
from pathlib import Path


def process():
    pr = ScrapedDataProcesser()
    path = Path(__file__).parent.parent / "outputs"
    data = ""
    with open(path / "products_data.json", 'r', encoding='utf-8') as f:
        data = pr.get_cleared_data(f)

    with DatabaseController() as db:
        names_mapping = db.get_ingredients_mapping()
        merged_names = data.merge(names_mapping, how="left", on=["clean_name", "brand"])
        
        known_ingr = merged_names[merged_names["master_name"].notna()]
        if not known_ingr.empty:
            # pass dataframe with prices to price manager for load
            print(f"To update prices redirected {len(known_ingr)} entries")
            pass
        
        new_entries = merged_names[merged_names["master_name"].isna()].copy().reset_index(drop=True)
        if not new_entries.empty:
            new_entries = pr.clear_new_data(new_entries.copy())
            new_entries = pr.combine_master_names(new_entries, names_mapping) 

            # with open(path / "cleared_data.csv", 'w', encoding='utf-8') as f:
            #     new_entries.to_csv(f, sep='\t', encoding='utf-8', index=True, lineterminator='\n', header=True)

            malt_data = pr.get_malts_characteristics(new_entries[new_entries['item_type'] == 'malt'].copy(), str(path))
            malt_aggregated = aggregator.get_aggregated_ingredients(malt_data.copy())
            db.load_ingredients_from_df(malt_aggregated, malt_data[['brand', 'master_name', 'clean_name']].copy())

            hop_data = pr.get_hops_characteristics(new_entries[new_entries['item_type'] == 'hop'].copy(), str(path))
            hop_aggregated = aggregator.get_aggregated_ingredients(hop_data.copy())
            db.load_ingredients_from_df(hop_aggregated, hop_data[['brand', 'master_name', 'clean_name']].copy())

            yeast_data = pr.get_yeasts_characteristics(new_entries[new_entries['item_type'] == 'yeast'].copy(), str(path))
            yeast_aggregated = aggregator.get_aggregated_ingredients(yeast_data.copy())
            db.load_ingredients_from_df(yeast_aggregated, yeast_data[['brand', 'master_name', 'clean_name']].copy())




if __name__ == "__main__":
    crawler.run_parsers(Path(__file__).parent / "outputs" / "products_data.json")
    process()