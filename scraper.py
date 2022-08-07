from google_play_scraper.scraper import PlayStoreScraper
from google_play_scraper.util import PlayStoreCategories
from google_play_scraper.util import PlayStoreCollections
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client['coral']
db_collection = db['packages']


def get_all_class_members(obj):
    return [attr for attr in dir(obj) if
            not callable(getattr(obj, attr)) and not attr.startswith("__")]


def fetch_packages_by_country(country='gb', lang='en'):
    categories = get_all_class_members(PlayStoreCategories())
    categories = [category for category in categories
                  if not (category.startswith("GAME_") or category.startswith("FAMILY_"))]
    collections = [PlayStoreCollections.NEW_FREE, PlayStoreCollections.TOP_FREE,
                   PlayStoreCollections.NEW_PAID, PlayStoreCollections.TOP_PAID]

    packages = list()
    scraper = PlayStoreScraper()
    for category in categories:
        for collection in collections:
            try:
                package_names = scraper.get_app_ids_for_collection(collection=collection,
                                                                   category=category,
                                                                   country=country,
                                                                   lang=lang)
            except IndexError:
                package_names = []

            for package_name in package_names:
                packages.append({"package": package_name, "category": category,
                                 "collection": collection, "country": country})

    return packages


def fetch_packages():
    countries = ["AL", "DZ", "AO", "AG", "AR", "AM", "AW", "AU", "AT", "AZ", "BS", "BH", "BD", "BY",
                 "BE", "BZ", "BJ", "BO", "BA", "BW", "BR", "BG", "BF", "KH", "CM", "CA", "CV", "CL",
                 "CO", "CR", "CY", "CZ", "DK", "DO", "EC", "EG", "SV", "EE", "FJ", "FI", "FR", "GA",
                 "GE", "DE", "GH", "GR", "GT", "GW", "HT", "HN", "IS", "IN", "ID", "IQ", "IE", "IL",
                 "IT", "JM", "JP", "JO", "KZ", "KE", "KW", "KG", "LA", "LV", "LB", "LI", "LT", "LU",
                 "MO", "MK", "MY", "ML", "MT", "MU", "MX", "MD", "MA", "MZ", "MM", "NA", "NP", "NL",
                 "AN", "NZ", "NI", "NE", "NO", "OM", "PK", "PA", "PG", "PE", "PH", "PL", "PT", "QA",
                 "RO", "RU", "RW", "SA", "SN", "RS", "SG", "SK", "SI", "ZA", "ES", "LK", "SE", "CH",
                 "TW", "TJ", "TZ", "TH", "TG", "TT", "TN", "TR", "TM", "UG", "UA", "AE", "GB", "US",
                 "UY", "UZ", "VE", "VN", "YE", "ZM", "ZW"]

    for country in countries:
        packages = fetch_packages_by_country(country=country)
        db_collection.insert_many(packages)


def main():
    fetch_packages()


if __name__ == "__main__":
    main()
