"""
Generation de donnees synthetiques pour le schema en etoile retail.

Produit 4 dimensions (dim_date, dim_product, dim_store, dim_customer) et une
table de faits (fact_sales) avec tendance, saisonnalite et quelques anomalies
volontaires (doublons, valeurs aberrantes, cles orphelines, nulls) qui servent
de terrain de jeu au fichier sql/05_qualite_donnees.sql.

Reproductible : une seule seed (RANDOM_SEED) pilote tous les tirages aleatoires.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RANDOM_SEED = 42
N_TARGET_ROWS = 100_000
START_DATE = pd.Timestamp("2024-01-01")
END_DATE = pd.Timestamp("2025-12-31")

MONTH_NAMES_FR = [
    "Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Decembre",
]
DAY_NAMES_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


# ---------------------------------------------------------------------------
# dim_date
# ---------------------------------------------------------------------------
def generate_dim_date() -> pd.DataFrame:
    dates = pd.date_range(START_DATE, END_DATE, freq="D")
    df = pd.DataFrame({"full_date": dates})
    df["date_key"] = df["full_date"].dt.strftime("%Y%m%d").astype(int)
    df["year"] = df["full_date"].dt.year
    df["quarter"] = df["full_date"].dt.quarter
    df["month"] = df["full_date"].dt.month
    df["month_name"] = df["month"].map(lambda m: MONTH_NAMES_FR[m - 1])
    df["day"] = df["full_date"].dt.day
    df["day_of_week"] = df["full_date"].dt.dayofweek + 1  # 1 = Lundi ... 7 = Dimanche
    df["day_name"] = df["full_date"].dt.dayofweek.map(lambda d: DAY_NAMES_FR[d])
    df["week_of_year"] = df["full_date"].dt.isocalendar().week.astype(int)
    df["is_weekend"] = df["day_of_week"].isin([6, 7])
    return df[[
        "date_key", "full_date", "year", "quarter", "month", "month_name",
        "day", "day_of_week", "day_name", "week_of_year", "is_weekend",
    ]]


# ---------------------------------------------------------------------------
# dim_product
# ---------------------------------------------------------------------------
CATEGORIES = {
    "Epicerie": {
        "subcategories": ["Pates & Riz", "Conserves", "Petit-dejeuner", "Snacking"],
        "brands": ["Panzani", "Barilla", "Bonduelle", "Kellogg's", "Lu", "St Michel"],
        "cost_range": (0.5, 4.0),
        "popularity": 1.0,
    },
    "Boissons": {
        "subcategories": ["Eaux", "Sodas", "Jus de fruits", "Cafe & The"],
        "brands": ["Evian", "Coca-Cola", "Oasis", "Lavazza", "Lipton"],
        "cost_range": (0.4, 3.0),
        "popularity": 0.9,
    },
    "Hygiene & Beaute": {
        "subcategories": ["Soin visage", "Hygiene corporelle", "Parfumerie"],
        "brands": ["Nivea", "Dove", "L'Oreal", "Garnier"],
        "cost_range": (1.0, 8.0),
        "popularity": 0.7,
    },
    "Entretien Maison": {
        "subcategories": ["Lessive", "Nettoyants", "Papier essuie-tout"],
        "brands": ["Ariel", "Mr Propre", "Sopalin", "Cif"],
        "cost_range": (1.5, 9.0),
        "popularity": 0.6,
    },
    "Bebe": {
        "subcategories": ["Couches", "Lait infantile", "Petits pots"],
        "brands": ["Pampers", "Nestle", "Bledina"],
        "cost_range": (2.0, 15.0),
        "popularity": 0.3,
    },
    "Animalerie": {
        "subcategories": ["Alimentation chien", "Alimentation chat", "Accessoires"],
        "brands": ["Purina", "Whiskas", "Royal Canin"],
        "cost_range": (1.5, 12.0),
        "popularity": 0.35,
    },
    "High-tech": {
        "subcategories": ["Accessoires telephone", "Informatique", "Son"],
        "brands": ["Samsung", "Logitech", "JBL", "Sony"],
        "cost_range": (8.0, 120.0),
        "popularity": 0.25,
    },
    "Textile & Mode": {
        "subcategories": ["Vetements homme", "Vetements femme", "Chaussures"],
        "brands": ["Petit Bateau", "Levi's", "Eram"],
        "cost_range": (5.0, 40.0),
        "popularity": 0.3,
    },
}
PRODUCTS_PER_CATEGORY = 22


def generate_dim_product(rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    product_key = 1
    for category, cfg in CATEGORIES.items():
        cost_lo, cost_hi = cfg["cost_range"]
        for i in range(PRODUCTS_PER_CATEGORY):
            subcategory = rng.choice(cfg["subcategories"])
            brand = rng.choice(cfg["brands"])
            unit_cost = round(float(rng.uniform(cost_lo, cost_hi)), 2)
            margin_factor = float(rng.uniform(1.25, 1.9))
            unit_price = round(unit_cost * margin_factor, 2)
            # Poids Pareto : quelques references locomotives, beaucoup de references de fond de rayon.
            popularity_weight = cfg["popularity"] * float(rng.lognormal(mean=0.0, sigma=0.9))
            rows.append({
                "product_key": product_key,
                "product_name": f"{brand} {subcategory} n{i + 1}",
                "category": category,
                "subcategory": subcategory,
                "brand": brand,
                "unit_cost": unit_cost,
                "unit_price": unit_price,
                "popularity_weight": popularity_weight,
            })
            product_key += 1
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# dim_store
# ---------------------------------------------------------------------------
STORES = [
    ("Paris Centre", "Paris", "Ile-de-France", "Centre-ville", 2.2),
    ("Paris Nord", "Paris", "Ile-de-France", "Peripherie", 1.8),
    ("Lyon Part-Dieu", "Lyon", "Auvergne-Rhone-Alpes", "Centre-ville", 1.6),
    ("Lyon Confluence", "Lyon", "Auvergne-Rhone-Alpes", "Peripherie", 1.3),
    ("Marseille", "Marseille", "Provence-Alpes-Cote d'Azur", "Centre-ville", 1.4),
    ("Toulouse", "Toulouse", "Occitanie", "Peripherie", 1.1),
    ("Nice", "Nice", "Provence-Alpes-Cote d'Azur", "Centre-ville", 1.0),
    ("Nantes", "Nantes", "Pays de la Loire", "Peripherie", 1.0),
    ("Strasbourg", "Strasbourg", "Grand Est", "Centre-ville", 0.9),
    ("Lille", "Lille", "Hauts-de-France", "Peripherie", 1.0),
    ("Bordeaux", "Bordeaux", "Nouvelle-Aquitaine", "Centre-ville", 1.0),
    ("Rennes", "Rennes", "Bretagne", "Peripherie", 0.8),
    ("Montpellier", "Montpellier", "Occitanie", "Centre-ville", 0.8),
    ("Reims", "Reims", "Grand Est", "Peripherie", 0.6),
    ("Dijon", "Dijon", "Bourgogne-Franche-Comte", "Centre-ville", 0.6),
    ("Angers", "Angers", "Pays de la Loire", "Peripherie", 0.6),
    ("Grenoble", "Grenoble", "Auvergne-Rhone-Alpes", "Centre-ville", 0.7),
    ("Le Havre", "Le Havre", "Normandie", "Peripherie", 0.5),
]


def generate_dim_store(rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    store_key = 1
    for name, city, region, store_type, weight in STORES:
        opening_date = pd.Timestamp("2015-01-01") + pd.Timedelta(
            days=int(rng.integers(0, (START_DATE - pd.Timestamp("2015-01-01")).days))
        )
        rows.append({
            "store_key": store_key,
            "store_name": name,
            "store_type": store_type,
            "city": city,
            "region": region,
            "opening_date": opening_date,
            "traffic_weight": weight,
        })
        store_key += 1
    # Magasin en ligne : sa part de trafic augmente avec le temps (cf. generate_fact_sales).
    rows.append({
        "store_key": store_key,
        "store_name": "Boutique en ligne",
        "store_type": "En ligne",
        "city": "National",
        "region": "National",
        "opening_date": pd.Timestamp("2015-01-01"),
        "traffic_weight": 0.0,  # non utilise : le canal en ligne est tire a part
    })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# dim_customer
# ---------------------------------------------------------------------------
FIRST_NAMES = [
    "Lea", "Hugo", "Chloe", "Louis", "Manon", "Jules", "Camille", "Arthur",
    "Ines", "Gabriel", "Sarah", "Adam", "Emma", "Nathan", "Julie", "Lucas",
    "Alice", "Mohamed", "Sofia", "Thomas", "Zoe", "Antoine", "Clara", "Maxime",
]
LAST_NAMES = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit",
    "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel",
    "Garcia", "David", "Bertrand", "Roux", "Vincent", "Fontaine",
]
N_CUSTOMERS = 6_000


def generate_dim_customer(rng: np.random.Generator, dim_store: pd.DataFrame) -> pd.DataFrame:
    cities = dim_store.loc[dim_store["store_type"] != "En ligne", ["city", "region"]].drop_duplicates()
    cities = cities.reset_index(drop=True)
    city_idx = rng.integers(0, len(cities), size=N_CUSTOMERS)

    signup_start = pd.Timestamp("2020-01-01")
    signup_span_days = (END_DATE - signup_start).days
    # Plus de clients inscrits recemment (croissance de la base) : tirage triangulaire.
    signup_offsets = rng.triangular(0, signup_span_days, signup_span_days, size=N_CUSTOMERS).astype(int)

    segments = rng.choice(["Particulier", "Professionnel"], size=N_CUSTOMERS, p=[0.75, 0.25])
    # Propension d'achat (loi log-normale) : quelques clients tres fideles, beaucoup de clients occasionnels.
    purchase_propensity = rng.lognormal(mean=0.0, sigma=1.1, size=N_CUSTOMERS)

    first_names = rng.choice(FIRST_NAMES, size=N_CUSTOMERS)
    last_names = rng.choice(LAST_NAMES, size=N_CUSTOMERS)

    df = pd.DataFrame({
        "customer_key": np.arange(1, N_CUSTOMERS + 1),
        "customer_name": [f"{f} {l}" for f, l in zip(first_names, last_names)],
        "segment": segments,
        "city": cities.loc[city_idx, "city"].to_numpy(),
        "region": cities.loc[city_idx, "region"].to_numpy(),
        "signup_date": [signup_start + pd.Timedelta(days=int(o)) for o in signup_offsets],
        "purchase_propensity": purchase_propensity,
    })
    return df


# ---------------------------------------------------------------------------
# fact_sales
# ---------------------------------------------------------------------------
def _daily_transaction_counts(rng: np.random.Generator, dim_date: pd.DataFrame) -> np.ndarray:
    n_days = len(dim_date)
    t = np.linspace(0.0, 1.0, n_days)  # position dans l'historique, 0 = debut, 1 = fin

    trend = 0.8 + 0.45 * t  # croissance du business sur 2 ans

    weekday_mult = {1: 0.85, 2: 0.85, 3: 0.9, 4: 0.95, 5: 1.15, 6: 1.35, 7: 0.7}
    weekday = dim_date["day_of_week"].map(weekday_mult).to_numpy()

    month_mult = {
        1: 1.0, 2: 0.85, 3: 0.95, 4: 1.0, 5: 1.0, 6: 1.05,
        7: 0.9, 8: 0.7, 9: 1.0, 10: 1.05, 11: 1.2, 12: 1.35,
    }
    month = dim_date["month"].map(month_mult).to_numpy()

    base_lambda = 141.0
    lam = base_lambda * trend * weekday * month
    return rng.poisson(lam)


def generate_fact_sales(
    rng: np.random.Generator,
    dim_date: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_store: pd.DataFrame,
    dim_customer: pd.DataFrame,
) -> pd.DataFrame:
    daily_counts = _daily_transaction_counts(rng, dim_date)
    transaction_dates = np.repeat(dim_date["date_key"].to_numpy(), daily_counts)
    transaction_day_frac = np.repeat(np.linspace(0.0, 1.0, len(dim_date)), daily_counts)
    n = len(transaction_dates)

    # Ramene le volume a exactement N_TARGET_ROWS pour un chiffre rond et reproductible.
    if n > N_TARGET_ROWS:
        keep = np.sort(rng.choice(n, size=N_TARGET_ROWS, replace=False))
        transaction_dates = transaction_dates[keep]
        transaction_day_frac = transaction_day_frac[keep]
        n = N_TARGET_ROWS

    # --- Canal de vente : la part du "en ligne" progresse de 5% a 15% sur la periode. ---
    p_online = 0.05 + 0.10 * transaction_day_frac
    is_online = rng.random(n) < p_online

    store_ids = dim_store.loc[dim_store["store_type"] != "En ligne", "store_key"].to_numpy()
    store_weights = dim_store.loc[dim_store["store_type"] != "En ligne", "traffic_weight"].to_numpy()
    store_weights = store_weights / store_weights.sum()
    online_store_key = int(dim_store.loc[dim_store["store_type"] == "En ligne", "store_key"].iloc[0])

    store_key = np.empty(n, dtype=int)
    store_key[is_online] = online_store_key
    n_physical = int((~is_online).sum())
    store_key[~is_online] = rng.choice(store_ids, size=n_physical, p=store_weights)

    # --- Produit : tirage pondere par popularite (effet Pareto). ---
    product_weights = dim_product["popularity_weight"].to_numpy()
    product_weights = product_weights / product_weights.sum()
    product_idx = rng.choice(len(dim_product), size=n, p=product_weights)
    product_key = dim_product["product_key"].to_numpy()[product_idx]
    unit_cost = dim_product["unit_cost"].to_numpy()[product_idx]
    base_price = dim_product["unit_price"].to_numpy()[product_idx]

    # --- Client : 85% des ventes sont rattachees a un client (carte de fidelite), le reste anonyme. ---
    has_customer = rng.random(n) >= 0.15
    cust_weights = dim_customer["purchase_propensity"].to_numpy()
    cust_weights = cust_weights / cust_weights.sum()
    customer_key = np.full(n, np.nan)
    n_with_cust = int(has_customer.sum())
    customer_key[has_customer] = rng.choice(
        dim_customer["customer_key"].to_numpy(), size=n_with_cust, p=cust_weights
    )

    # --- Quantite : les professionnels achetent en plus grande quantite. ---
    customer_segment = pd.Series(customer_key).map(
        dict(zip(dim_customer["customer_key"], dim_customer["segment"]))
    )
    is_pro = (customer_segment == "Professionnel").to_numpy()
    quantity = rng.poisson(1.2, size=n) + 1
    quantity[is_pro] += rng.poisson(2.5, size=is_pro.sum())
    quantity = np.clip(quantity, 1, 12)

    # --- Remise : plus frequente et plus forte en periode de soldes / Black Friday. ---
    month = (transaction_dates // 100) % 100
    promo_month = np.isin(month, [1, 6, 11, 12])
    discount_prob = np.where(promo_month, 0.45, 0.15)
    has_discount = rng.random(n) < discount_prob
    discount_rate = np.where(has_discount, rng.uniform(0.05, 0.30, size=n), 0.0)

    price_noise = np.clip(rng.normal(0.0, 0.01, size=n), -0.05, 0.05)
    unit_price_final = np.round(base_price * (1 - discount_rate) * (1 + price_noise), 2)

    revenue = np.round(quantity * unit_price_final, 2)
    cost = np.round(quantity * unit_cost, 2)
    margin = np.round(revenue - cost, 2)

    df = pd.DataFrame({
        "sale_id": np.arange(1, n + 1),
        "date_key": transaction_dates,
        "product_key": product_key,
        "store_key": store_key,
        "customer_key": customer_key,
        "quantity": quantity.astype(float),
        "unit_price": unit_price_final,
        "discount_rate": np.round(discount_rate, 2),
        "revenue": revenue,
        "cost": cost,
        "margin": margin,
    })

    df = _inject_data_quality_issues(rng, df, dim_product, dim_store)
    return df


def _inject_data_quality_issues(
    rng: np.random.Generator,
    df: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_store: pd.DataFrame,
) -> pd.DataFrame:
    """
    Injecte volontairement des anomalies realistes pour donner du contenu au
    fichier sql/05_qualite_donnees.sql : sans anomalies, les controles qualite
    n'auraient rien a detecter.
    """
    n = len(df)

    # 1) Valeurs aberrantes : quantite ou prix anormalement eleves (erreur de
    # saisie). Les deux anomalies sont decouplees (une seule des deux colonnes
    # est modifiee a la fois, et la quantite est neutralisee sur les lignes de
    # prix aberrant) afin qu'elles restent detectables individuellement sans
    # produire des montants extremes qui fausseraient les analyses metier des
    # autres fichiers (une anomalie doit rester une anomalie plausible).
    cheap_pool = df.index[df["unit_price"] < 20]
    qty_outlier_idx = rng.choice(cheap_pool, size=12, replace=False)
    df.loc[qty_outlier_idx, "quantity"] = rng.integers(30, 80, size=12)

    remaining_pool = np.setdiff1d(df.index, qty_outlier_idx)
    price_outlier_idx = rng.choice(remaining_pool, size=13, replace=False)
    df.loc[price_outlier_idx, "unit_price"] = df.loc[price_outlier_idx, "unit_price"] * rng.uniform(6, 10, size=13)
    df.loc[price_outlier_idx, "quantity"] = 1

    outlier_idx = np.concatenate([qty_outlier_idx, price_outlier_idx])
    df.loc[outlier_idx, "revenue"] = np.round(df.loc[outlier_idx, "quantity"] * df.loc[outlier_idx, "unit_price"], 2)
    df.loc[outlier_idx, "margin"] = np.round(df.loc[outlier_idx, "revenue"] - df.loc[outlier_idx, "cost"], 2)

    # 2) Nulls inattendus : quantite non capturee alors que la vente existe bien.
    null_idx = rng.choice(np.setdiff1d(np.arange(n), outlier_idx), size=10, replace=False)
    df.loc[df.index[null_idx], "quantity"] = np.nan

    # 3) Doublons : meme ligne de vente enregistree deux fois (double scan caisse).
    dup_idx = rng.choice(n, size=60, replace=False)
    duplicates = df.iloc[dup_idx].copy()

    # 4) Cles orphelines : reference produit/magasin inexistante dans la dimension.
    n_orphans = 15
    orphan_base = df.iloc[rng.choice(n, size=n_orphans, replace=False)].copy()
    invalid_product_key = int(dim_product["product_key"].max()) + 9999
    invalid_store_key = int(dim_store["store_key"].max()) + 9999
    orphan_base.iloc[: n_orphans // 2, orphan_base.columns.get_loc("product_key")] = invalid_product_key
    orphan_base.iloc[n_orphans // 2:, orphan_base.columns.get_loc("store_key")] = invalid_store_key

    extra = pd.concat([duplicates, orphan_base], ignore_index=True)
    extra["sale_id"] = np.arange(n + 1, n + 1 + len(extra))

    return pd.concat([df, extra], ignore_index=True)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def generate(output_dir: Path) -> dict[str, int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(RANDOM_SEED)

    dim_date = generate_dim_date()
    dim_product = generate_dim_product(rng)
    dim_store = generate_dim_store(rng)
    dim_customer = generate_dim_customer(rng, dim_store)
    fact_sales = generate_fact_sales(rng, dim_date, dim_product, dim_store, dim_customer)

    dim_date.to_csv(output_dir / "dim_date.csv", index=False)
    dim_product.drop(columns=["popularity_weight"]).to_csv(output_dir / "dim_product.csv", index=False)
    dim_store.drop(columns=["traffic_weight"]).to_csv(output_dir / "dim_store.csv", index=False)
    dim_customer.drop(columns=["purchase_propensity"]).to_csv(output_dir / "dim_customer.csv", index=False)
    fact_sales.to_csv(output_dir / "fact_sales.csv", index=False)

    return {
        "dim_date": len(dim_date),
        "dim_product": len(dim_product),
        "dim_store": len(dim_store),
        "dim_customer": len(dim_customer),
        "fact_sales": len(fact_sales),
    }


if __name__ == "__main__":
    counts = generate(Path(__file__).parent)
    for table, count in counts.items():
        print(f"{table:15s} {count:>8,d} lignes".replace(",", " "))
