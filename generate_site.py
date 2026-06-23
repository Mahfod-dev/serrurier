#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import html
import json
import os
import re
import shutil
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GENERATED_DATE = date.today().isoformat()

BUSINESS = {
    "name": os.environ.get("SOLYBAT_NAME", "Solybat"),
    "site_url": os.environ.get("SOLYBAT_SITE_URL", "https://www.solybat.fr"),
    "email": os.environ.get("SOLYBAT_EMAIL", "contact@solybat.fr"),
    "legal_name": os.environ.get("SOLYBAT_LEGAL_NAME", "Solybat"),
    "legal_form": os.environ.get("SOLYBAT_LEGAL_FORM", "Entreprise à compléter"),
    "siret": os.environ.get("SOLYBAT_SIRET", "SIRET à compléter"),
    "vat": os.environ.get("SOLYBAT_VAT", "TVA à compléter si applicable"),
    "director": os.environ.get("SOLYBAT_DIRECTOR", "Responsable de publication à compléter"),
    "address": os.environ.get("SOLYBAT_ADDRESS", "Adresse Solybat à compléter"),
    "fr_phone_display": os.environ.get("SOLYBAT_FR_PHONE_DISPLAY", "04 00 00 00 00"),
    "fr_phone_href": os.environ.get("SOLYBAT_FR_PHONE_HREF", "+33400000000"),
    "ch_phone_display": os.environ.get("SOLYBAT_CH_PHONE_DISPLAY", "+41 22 000 00 00"),
    "ch_phone_href": os.environ.get("SOLYBAT_CH_PHONE_HREF", "+41220000000"),
    "whatsapp": os.environ.get("SOLYBAT_WHATSAPP", "33600000000"),
    "host_name": os.environ.get("SOLYBAT_HOST_NAME", "Vercel Inc."),
    "host_address": os.environ.get("SOLYBAT_HOST_ADDRESS", "440 N Barranca Ave #4133, Covina, CA 91723, United States"),
}

CITY_GROUPS = """
Canton de Genève (Suisse)|Genève et Couronne|CH|Genève,Vernier,Lancy,Meyrin,Carouge,Thônex,Versoix,Le Grand-Saconnex,Chêne-Bougeries,Onex,Plan-les-Ouates,Collonge-Bellerive,Pregny-Chambésy,Veyrier,Châtelaine
Auvergne-Rhône-Alpes (France)|Rhône (69) & Métropole de Lyon|FR|Lyon,Villeurbanne,Vénissieux,Vaulx-en-Velin,Saint-Priest,Caluire-et-Cuire,Rillieux-la-Pape,Meyzieu,Décines-Charpieu,Oullins-Pierre-Bénite,Sainte-Foy-lès-Lyon,Saint-Fons,Givors,Villefranche-sur-Saône,Tassin-la-Demi-Lune,Écully,Genas,Brignais,Chassieu,Corbas,Craponne,Mions,Feyzin,Tarare
Auvergne-Rhône-Alpes (France)|Haute-Savoie (74) & Savoie (73)|FR|Annecy,Thonon-les-Bains,Annemasse,Cluses,Sallanches,Rumilly,Bonneville,Passy,Gaillard,Saint-Julien-en-Genevois,La Roche-sur-Foron,Publier,Évian-les-Bains,Cranves-Sales,Scionzier,Reignier-Ésery,Vétraz-Monthoux,Chambéry,Aix-les-Bains,Albertville,La Motte-Servolex,Bourg-Saint-Maurice,Ugine,Saint-Jean-de-Maurienne
Auvergne-Rhône-Alpes (France)|Isère (38) & Ain (01)|FR|Grenoble,Saint-Martin-d'Hères,Échirolles,Vienne,Bourgoin-Jallieu,Voiron,Villefontaine,Meylan,L'Isle-d'Abeau,Bourg-en-Bresse,Oyonnax,Valserhône (Bellegarde),Ambérieu-en-Bugey,Gex,Saint-Genis-Pouilly,Ferney-Voltaire,Divonne-les-Bains,Miribel
Auvergne-Rhône-Alpes (France)|Loire (42), Drôme (26) & Ardèche (07)|FR|Saint-Étienne,Saint-Chamond,Roanne,Valence,Montélimar,Romans-sur-Isère,Annonay,Guilherand-Granges,Tournon-sur-Rhône
Provence-Alpes-Côte d'Azur (France)|Bouches-du-Rhône (13) & Var (83)|FR|Marseille,Aix-en-Provence,Arles,Martigues,Aubagne,Salon-de-Provence,Vitrolles,Marignane,La Ciotat,Istres,Miramas,Les Pennes-Mirabeau,Toulon,La Seyne-sur-Mer,Hyères,Fréjus,Draguignan,Saint-Raphaël,Six-Fours-les-Plages,La Garde,La Valette-du-Var
Provence-Alpes-Côte d'Azur (France)|Alpes-Maritimes (06) & Vaucluse (84)|FR|Nice,Cannes,Antibes,Cagnes-sur-Mer,Grasse,Le Cannet,Menton,Saint-Laurent-du-Var,Vallauris,Mandelieu-la-Napoule,Mougins,Vence,Avignon,Orange,Carpentras,Cavaillon,L'Isle-sur-la-Sorgue,Pertuis
""".strip()

P1 = {
    "Genève",
    "Lyon",
    "Villeurbanne",
    "Grenoble",
    "Annecy",
    "Annemasse",
    "Marseille",
    "Aix-en-Provence",
    "Toulon",
    "Nice",
    "Cannes",
    "Antibes",
    "Avignon",
    "Valence",
    "Chambéry",
    "Saint-Étienne",
}

P2 = {
    "Vernier",
    "Lancy",
    "Meyrin",
    "Carouge",
    "Vénissieux",
    "Vaulx-en-Velin",
    "Saint-Priest",
    "Caluire-et-Cuire",
    "Meyzieu",
    "Thonon-les-Bains",
    "Saint-Julien-en-Genevois",
    "Ferney-Voltaire",
    "Gex",
    "Échirolles",
    "Bourgoin-Jallieu",
    "Voiron",
    "Bourg-en-Bresse",
    "Montélimar",
    "Aubagne",
    "Salon-de-Provence",
    "Vitrolles",
    "La Seyne-sur-Mer",
    "Hyères",
    "Fréjus",
    "Cagnes-sur-Mer",
    "Grasse",
    "Menton",
    "Orange",
    "Carpentras",
}

SERVICES = {
    "serrurier": {
        "label": "Serrurier",
        "plural": "serrurerie",
        "schema_type": "Locksmith",
        "headline": "Serrurier à {city} - urgence 24/7",
        "short": "Ouverture de porte, serrure bloquée, cylindre à remplacer et sécurisation après effraction.",
        "hero": "Porte claquée, clé perdue ou serrure forcée : Solybat intervient rapidement à {city}.",
        "image": "https://images.unsplash.com/photo-1558002038-1091a1661116?q=80&w=1800&auto=format&fit=crop",
        "accent": "#f97316",
        "secondary": "#2563eb",
        "audience": "particuliers, commerces, syndics et locaux professionnels",
        "promise": "Une intervention de serrurerie doit d'abord être expliquée : type de porte, niveau de sécurité, risque d'endommagement et prix avant ouverture.",
        "benefits": [
            "Ouverture fine quand la porte le permet",
            "Remplacement de cylindre et serrure multipoints",
            "Mise en sécurité après tentative d'effraction",
            "Devis annoncé avant intervention",
        ],
        "trust_points": [
            "Diagnostic téléphonique avant déplacement",
            "Justificatif d'occupation demandé si nécessaire",
            "Aucune ouverture destructrice sans accord préalable",
            "Conseil sur la sécurisation après effraction",
        ],
        "steps": [
            ("Qualification", "Vous décrivez la porte, la serrure, l'urgence et l'accès au logement ou au local."),
            ("Prix annoncé", "Un prix indicatif est donné avant déplacement selon l'horaire et la situation."),
            ("Intervention", "Le serrurier privilégie l'ouverture fine si la configuration le permet."),
            ("Sécurisation", "La fermeture est vérifiée, avec remplacement ou mise en sécurité si nécessaire."),
        ],
        "pricing": [
            ("Déplacement local", "Sur devis"),
            ("Ouverture de porte claquée", "à partir de 90 €"),
            ("Ouverture de porte verrouillée", "à partir de 130 €"),
            ("Remplacement cylindre", "à partir de 89 €"),
        ],
        "keywords": [
            "serrurier urgence {city}",
            "serrurier {city}",
            "ouverture porte {city}",
            "changement serrure {city}",
            "serrure bloquée {city}",
        ],
    },
    "plombier": {
        "label": "Plombier",
        "plural": "plomberie",
        "schema_type": "Plumber",
        "headline": "Plombier à {city} - dépannage rapide",
        "short": "Fuite d'eau, WC bouchés, robinetterie, chauffe-eau et dépannage sanitaire urgent.",
        "hero": "Fuite, dégât des eaux ou panne sanitaire : Solybat envoie un plombier à {city}.",
        "image": "https://images.unsplash.com/photo-1607472586893-edb57bdc0e39?q=80&w=1800&auto=format&fit=crop",
        "accent": "#0ea5e9",
        "secondary": "#f97316",
        "audience": "logements, copropriétés, commerces et locaux professionnels",
        "promise": "Une urgence plomberie doit limiter les dégâts rapidement : couper l'eau, identifier l'origine probable et confirmer le prix avant intervention.",
        "benefits": [
            "Recherche et arrêt de fuite",
            "Dépannage WC, évier, lavabo et douche",
            "Remplacement robinetterie et joints",
            "Intervention prioritaire en urgence",
        ],
        "trust_points": [
            "Priorité à la coupure et à la limitation du dégât des eaux",
            "Explication claire avant remplacement de pièce",
            "Intervention sur sanitaire, robinetterie et évacuation courante",
            "Compte rendu simple pour assurance ou propriétaire si besoin",
        ],
        "steps": [
            ("Sécuriser", "Vous indiquez si l'eau peut être coupée et si le dégât est encore actif."),
            ("Identifier", "La fuite, l'équipement ou l'évacuation concernée est qualifiée avant déplacement."),
            ("Réparer", "Le plombier intervient sur la cause accessible et explique les pièces nécessaires."),
            ("Contrôler", "L'étanchéité et l'écoulement sont vérifiés avant la fin de l'intervention."),
        ],
        "pricing": [
            ("Déplacement local", "Sur devis"),
            ("Recherche de fuite simple", "à partir de 90 €"),
            ("Dépannage sanitaire", "à partir de 110 €"),
            ("Main d'oeuvre horaire", "à partir de 70 €"),
        ],
        "keywords": [
            "plombier urgence {city}",
            "plombier {city}",
            "fuite eau {city}",
            "dépannage plomberie {city}",
            "wc bouché {city}",
        ],
    },
    "degorgement": {
        "label": "Dégorgement",
        "plural": "dégorgement",
        "schema_type": "Plumber",
        "headline": "Dégorgement canalisation à {city}",
        "short": "Débouchage, curage, hydrocurage, camion pompe et intervention sur canalisations obstruées.",
        "hero": "Canalisation bouchée, regard plein ou besoin de camion pompe : Solybat intervient à {city}.",
        "image": "https://images.unsplash.com/photo-1585704032915-c3400ca199e7?q=80&w=1800&auto=format&fit=crop",
        "accent": "#0891b2",
        "secondary": "#f97316",
        "audience": "maisons, immeubles, locaux commerciaux et réseaux extérieurs accessibles",
        "promise": "Un bouchon de canalisation demande une qualification précise : point de blocage, accès, remontées d'eau et besoin éventuel d'hydrocurage.",
        "benefits": [
            "Débouchage canalisation haute pression",
            "Curage préventif ou curatif",
            "Camion pompe selon accessibilité",
            "Diagnostic avant travaux lourds",
        ],
        "trust_points": [
            "Qualification du bouchon avant déplacement",
            "Vérification de l'accès au regard ou à l'évacuation",
            "Solution adaptée : débouchage simple, curage ou camion pompe",
            "Conseils pour éviter une récidive rapide",
        ],
        "steps": [
            ("Localiser", "Vous précisez l'équipement concerné, les remontées et l'accès aux regards."),
            ("Qualifier", "Le besoin est orienté entre débouchage, hydrocurage ou camion pompe."),
            ("Déboucher", "L'intervention est menée avec le matériel adapté au type de bouchon."),
            ("Prévenir", "Les causes possibles et les signes de récidive sont expliqués après intervention."),
        ],
        "pricing": [
            ("Diagnostic canalisation", "Sur devis"),
            ("Débouchage simple", "à partir de 120 €"),
            ("Hydrocurage", "Sur devis"),
            ("Camion pompe", "Sur devis"),
        ],
        "keywords": [
            "camion pompe {city}",
            "dégorgement {city}",
            "débouchage canalisation {city}",
            "canalisation bouchée {city}",
            "hydrocurage {city}",
        ],
    },
}

NEGATIVE_KEYWORDS = [
    "gratuit",
    "pas cher",
    "moins cher",
    "bricolage",
    "soi-même",
    "soi meme",
    "tutoriel",
    "tutorial",
    "video",
    "youtube",
    "formation",
    "emploi",
    "recrutement",
    "salaire",
    "stage",
    "leroy merlin",
    "castorama",
    "brico depot",
    "manomano",
    "amazon",
    "pdf",
    "schema",
    "définition",
    "definition",
]

LOCAL_SEO = {
    "geneve": {
        "micro_areas": ["Cornavin", "Plainpalais", "Eaux-Vives", "Pâquis", "Champel", "Nations"],
        "local_note": "À Genève, la cohérence du numéro suisse et la précision du secteur sont essentielles pour rassurer un client en urgence.",
    },
    "lyon": {
        "micro_areas": ["Part-Dieu", "Presqu'île", "Croix-Rousse", "Vieux Lyon", "Gerland", "Confluence"],
        "local_note": "À Lyon, les demandes se répartissent entre immeubles anciens, logements récents et locaux professionnels très denses.",
    },
    "villeurbanne": {
        "micro_areas": ["Gratte-Ciel", "Charpennes", "Tonkin", "Cusset", "Flachet", "République"],
        "local_note": "Villeurbanne demande un discours de proximité fort, car l'utilisateur compare souvent avec Lyon et les communes voisines.",
    },
    "grenoble": {
        "micro_areas": ["Hypercentre", "Europole", "Île Verte", "Championnet", "Eaux-Claires", "Presqu'île"],
        "local_note": "À Grenoble, la page doit rassurer sur la réactivité en centre dense comme sur les secteurs résidentiels autour des grands axes.",
    },
    "annecy": {
        "micro_areas": ["Vieille Ville", "Cran-Gevrier", "Seynod", "Novel", "Albigny", "Courier"],
        "local_note": "À Annecy, la saisonnalité et les logements de courte durée rendent les urgences serrure, fuite et canalisation très sensibles au délai.",
    },
    "annemasse": {
        "micro_areas": ["Centre-ville", "Romagny", "Perrier", "Brouaz", "Gare", "zone frontalière"],
        "local_note": "À Annemasse, le message doit clarifier la couverture frontalière et éviter toute confusion avec le numéro suisse.",
    },
    "marseille": {
        "micro_areas": ["Vieux-Port", "Castellane", "Prado", "La Joliette", "Saint-Charles", "La Valentine"],
        "local_note": "À Marseille, les pages doivent parler d'accès, d'urgence et de qualification du problème avant déplacement.",
    },
    "aix-en-provence": {
        "micro_areas": ["Centre historique", "Jas de Bouffan", "Encagnane", "La Duranne", "Puyricard", "Les Milles"],
        "local_note": "À Aix-en-Provence, la différence entre centre ancien, zones résidentielles et secteurs d'activité doit être visible.",
    },
    "toulon": {
        "micro_areas": ["Centre-ville", "Mourillon", "Pont du Las", "Saint-Jean-du-Var", "La Serinette", "Sainte-Musse"],
        "local_note": "À Toulon, la page doit rassurer sur les urgences en habitation, commerce et immeuble collectif.",
    },
    "nice": {
        "micro_areas": ["Jean-Médecin", "Libération", "Vieux-Nice", "Le Port", "Cimiez", "Californie"],
        "local_note": "À Nice, la page doit tenir compte des appartements, résidences secondaires et commerces avec forte exigence de délai.",
    },
    "cannes": {
        "micro_areas": ["Croisette", "Le Suquet", "Carnot", "La Bocca", "Palm Beach", "Prado-République"],
        "local_note": "À Cannes, les urgences concernent souvent logements, commerces et locations saisonnières ; la clarté du tarif est décisive.",
    },
    "antibes": {
        "micro_areas": ["Vieil Antibes", "Juan-les-Pins", "La Fontonne", "Les Bréguières", "Les Combes", "Cap d'Antibes"],
        "local_note": "À Antibes, le contenu doit distinguer centre ancien, littoral, copropriétés et zones résidentielles.",
    },
    "avignon": {
        "micro_areas": ["Intra-muros", "Saint-Ruf", "Montfavet", "Courtine", "Rocade", "Barthelasse"],
        "local_note": "À Avignon, la page doit couvrir l'intra-muros, les accès et les secteurs périphériques sans mélanger les intentions.",
    },
    "valence": {
        "micro_areas": ["Centre-ville", "Châteauvert", "Fontbarlettes", "Valensolles", "Briffaut", "Épervière"],
        "local_note": "À Valence, un contenu local efficace relie centre-ville, quartiers résidentiels et zones d'activité proches.",
    },
    "chambery": {
        "micro_areas": ["Centre-ville", "Bissy", "Biollay", "Bellevue", "Chambéry-le-Haut", "Laurier"],
        "local_note": "À Chambéry, la page doit rassurer sur la disponibilité en centre-ville comme sur les quartiers en hauteur.",
    },
    "saint-etienne": {
        "micro_areas": ["Centre-ville", "Châteaucreux", "Carnot", "Bellevue", "Montreynaud", "Terrenoire"],
        "local_note": "À Saint-Étienne, les demandes urgentes viennent autant de logements collectifs que de commerces et locaux professionnels.",
    },
}

SERVICE_LOCAL_CASES = {
    "serrurier": {
        "title": "Situations de serrurerie à traiter rapidement",
        "cases": [
            "porte claquée avec clés laissées à l'intérieur",
            "serrure forcée après tentative d'effraction",
            "cylindre bloqué ou clé cassée dans la serrure",
            "mise en sécurité d'une porte de commerce ou d'immeuble",
        ],
        "faq": (
            "Que préparer avant l'arrivée du serrurier ?",
            "Préparez une pièce d'identité, un justificatif d'occupation si disponible et une photo de la porte ou de la serrure. Cela aide à confirmer le bon matériel avant déplacement.",
        ),
    },
    "plombier": {
        "title": "Situations de plomberie fréquentes",
        "cases": [
            "fuite sous évier, lavabo ou robinetterie",
            "WC bouchés ou évacuation lente",
            "dégât des eaux nécessitant une coupure rapide",
            "remplacement de joints, siphon ou mécanisme sanitaire",
        ],
        "faq": (
            "Que faire avant l'arrivée du plombier ?",
            "Coupez l'arrivée d'eau si possible, protégez les sols, prenez une photo de la fuite et indiquez si l'accès se fait en appartement, maison ou local professionnel.",
        ),
    },
    "degorgement": {
        "title": "Situations de canalisation à qualifier",
        "cases": [
            "canalisation bouchée avec remontées d'eau",
            "regard ou évacuation extérieure saturée",
            "besoin possible d'hydrocurage ou camion pompe",
            "mauvaises odeurs persistantes après débouchage simple",
        ],
        "faq": (
            "Quand faut-il prévoir un camion pompe ?",
            "Un camion pompe peut être nécessaire si les eaux remontent, si un regard est plein ou si le bouchon semble profond. L'accès, le stationnement et la distance jusqu'au réseau doivent être précisés au téléphone.",
        ),
    },
}


@dataclass(frozen=True)
class City:
    name: str
    slug: str
    region: str
    zone: str
    country: str
    priority: int


@dataclass(frozen=True)
class BuildConfig:
    key: str
    label: str
    site_url: str
    output_root: Path
    service_keys: tuple[str, ...]
    primary_service_key: str | None
    include_city_hubs: bool
    preserve_existing_home: bool = False


SPLIT_DOMAIN_DEFAULTS = {
    "serrurier": "https://serrurier.solybat.fr",
    "plombier": "https://plombier.solybat.fr",
}


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def slugify(value: str) -> str:
    value = strip_accents(value)
    value = value.replace("'", " ")
    value = re.sub(r"\([^)]*\)", "", value)
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def city_priority(name: str) -> int:
    if name in P1:
        return 1
    if name in P2:
        return 2
    return 3


def load_cities() -> list[City]:
    cities: list[City] = []
    seen: set[str] = set()
    for line in CITY_GROUPS.splitlines():
        region, zone, country, raw_cities = line.split("|", 3)
        for name in [item.strip() for item in raw_cities.split(",")]:
            slug = slugify(name)
            if slug in seen:
                raise ValueError(f"Duplicate city slug: {slug}")
            seen.add(slug)
            cities.append(City(name, slug, region, zone, country, city_priority(name)))
    return cities


def phone_for(city: City) -> tuple[str, str]:
    if city.country == "CH":
        return BUSINESS["ch_phone_display"], BUSINESS["ch_phone_href"]
    return BUSINESS["fr_phone_display"], BUSINESS["fr_phone_href"]


def page_url(path: str, build: BuildConfig) -> str:
    return f"{build.site_url.rstrip('/')}{path}"


def service_path(city: City, service_key: str, build: BuildConfig) -> str:
    if build.primary_service_key == service_key:
        return f"/{city.slug}/"
    return f"/{service_key}/{city.slug}/"


def city_hub_path(city: City) -> str:
    return f"/{city.slug}/"


def service_names(build: BuildConfig) -> str:
    labels = [SERVICES[key]["plural"] for key in build.service_keys]
    if len(labels) == 1:
        return labels[0]
    return ", ".join(labels[:-1]) + " et " + labels[-1]


def example_service_path(service_key: str, build: BuildConfig) -> str:
    if build.primary_service_key == service_key:
        return "/lyon/"
    return f"/{service_key}/lyon/"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def output_path_for(url_path: str, build: BuildConfig) -> Path:
    clean_path = url_path.strip("/")
    if not clean_path:
        return build.output_root / "index.html"
    return build.output_root / clean_path / "index.html"


def display_path(path: Path) -> Path:
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def operations_root(build: BuildConfig) -> Path:
    if build.output_root == ROOT:
        return ROOT
    return ROOT / "ops" / build.key


def prepare_output(build: BuildConfig) -> None:
    if build.output_root == ROOT:
        return
    resolved_output = build.output_root.resolve()
    resolved_root = ROOT.resolve()
    if build.output_root.exists() and resolved_root in resolved_output.parents:
        shutil.rmtree(build.output_root)


def css(build: BuildConfig) -> str:
    theme_key = build.primary_service_key or build.service_keys[0]
    theme_service = SERVICES[theme_key]
    accent = str(theme_service.get("accent", "#f97316"))
    secondary = str(theme_service.get("secondary", "#2563eb"))
    css_text = """
:root {
  --ink: #111827;
  --muted: #526071;
  --line: #dde3ec;
  --soft: #f6f8fb;
  --brand: #101826;
  --brand-2: #1f2937;
  --accent: __ACCENT__;
  --secondary: __SECONDARY__;
  --green: #147a4f;
  --white: #ffffff;
  --warning-soft: #fff7ed;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--ink);
  background: var(--white);
  line-height: 1.58;
}
a { color: inherit; text-decoration: none; }
.skip-link { position: absolute; left: -999px; top: 10px; z-index: 100; background: var(--white); color: var(--ink); padding: 10px 12px; border-radius: 8px; }
.skip-link:focus { left: 10px; }
.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  background: var(--brand);
  color: var(--white);
  border-bottom: 1px solid rgba(255,255,255,.1);
}
.topbar-inner, .nav, .wrap { width: min(1160px, calc(100% - 32px)); margin: 0 auto; }
.topbar-inner { min-height: 52px; display: flex; gap: 14px; align-items: center; justify-content: space-between; }
.brand { font-weight: 900; font-size: 1.2rem; letter-spacing: 0; display: flex; gap: 10px; align-items: center; }
.brand-mark { display: inline-grid; place-items: center; width: 34px; height: 34px; border-radius: 8px; background: var(--accent); color: var(--white); font-weight: 900; }
.top-actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; justify-content: flex-end; }
.call-btn, .ghost-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 12px 16px;
  border-radius: 8px;
  font-weight: 800;
  white-space: nowrap;
}
.call-btn { background: var(--accent); color: var(--white); box-shadow: 0 10px 25px rgba(15, 23, 42, .18); }
.ghost-btn { border: 1px solid rgba(255,255,255,.28); color: var(--white); }
.nav-shell { background: rgba(255,255,255,.96); backdrop-filter: blur(8px); border-bottom: 1px solid var(--line); position: sticky; top: 52px; z-index: 19; }
.nav { min-height: 58px; display: flex; align-items: center; justify-content: space-between; gap: 20px; }
.nav-links { display: flex; gap: 18px; color: var(--muted); font-weight: 700; font-size: .95rem; flex-wrap: wrap; }
.nav-links a:hover { color: var(--accent); }
.hero {
  position: relative;
  color: var(--white);
  overflow: hidden;
  isolation: isolate;
  background: var(--brand);
}
.hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image: linear-gradient(90deg, rgba(16,24,38,.96), rgba(16,24,38,.76), rgba(16,24,38,.36)), var(--hero-image);
  background-size: cover;
  background-position: center;
  z-index: -1;
}
.hero-grid {
  width: min(1160px, calc(100% - 32px));
  margin: 0 auto;
  min-height: 620px;
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(300px, .85fr);
  align-items: center;
  gap: 40px;
  padding: 64px 0;
}
.eyebrow { display: inline-flex; gap: 8px; align-items: center; color: #fed7aa; font-weight: 900; text-transform: uppercase; font-size: .78rem; }
.section .eyebrow { color: var(--accent); }
h1 { font-size: 4.55rem; line-height: 1.02; margin: 14px 0 20px; letter-spacing: 0; max-width: 860px; }
.hero p { color: #e5e7eb; font-size: 1.15rem; max-width: 720px; }
.hero-badges { display: flex; gap: 10px; flex-wrap: wrap; margin: 22px 0 0; }
.hero-badge { display: inline-flex; align-items: center; min-height: 34px; padding: 7px 11px; border: 1px solid rgba(255,255,255,.24); border-radius: 999px; color: #f8fafc; background: rgba(255,255,255,.08); font-weight: 800; font-size: .85rem; }
.hero-card {
  background: rgba(255,255,255,.96);
  color: var(--ink);
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 24px 70px rgba(0,0,0,.25);
  border: 1px solid rgba(255,255,255,.36);
}
.hero-card h2 { margin: 0 0 14px; font-size: 1.25rem; }
.hero-card ul, .check-list { padding: 0; margin: 0; list-style: none; display: grid; gap: 10px; }
.hero-card li, .check-list li { display: flex; gap: 10px; align-items: flex-start; }
.hero-card li::before, .check-list li::before { content: "✓"; color: var(--green); font-weight: 900; }
.hero-meta { border-top: 1px solid var(--line); margin-top: 18px; padding-top: 18px; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.hero-meta strong { display: block; font-size: 1.4rem; color: var(--brand); }
.hero-meta span { color: var(--muted); font-weight: 700; font-size: .88rem; }
.cta-row { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 26px; }
.section { padding: 78px 0; }
.section.alt { background: var(--soft); }
.section-head { max-width: 760px; margin-bottom: 34px; }
.section-head.center { margin-left: auto; margin-right: auto; text-align: center; }
.section h2 { font-size: 2.55rem; line-height: 1.08; margin: 0 0 12px; letter-spacing: 0; }
.section p { color: var(--muted); }
.grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
.grid-2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 22px; }
.grid-4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.card {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--white);
  padding: 22px;
  box-shadow: 0 10px 30px rgba(15,23,42,.06);
}
.card h3 { margin: 0 0 8px; font-size: 1.25rem; }
.card-number { display: inline-grid; place-items: center; width: 36px; height: 36px; border-radius: 8px; background: color-mix(in srgb, var(--accent) 12%, white); color: var(--brand); font-weight: 900; margin-bottom: 14px; }
.trust-band { border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); background: #fff; }
.trust-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0; }
.trust-item { padding: 22px; border-right: 1px solid var(--line); }
.trust-item:last-child { border-right: 0; }
.trust-item strong { display: block; margin-bottom: 4px; color: var(--brand); }
.trust-item span { color: var(--muted); font-size: .93rem; }
.split-panel { background: linear-gradient(135deg, color-mix(in srgb, var(--secondary) 7%, white), var(--white)); border: 1px solid var(--line); border-radius: 8px; padding: 28px; }
.cta-panel { background: var(--brand); color: var(--white); border-radius: 8px; padding: 30px; display: flex; align-items: center; justify-content: space-between; gap: 22px; }
.cta-panel p { color: #cbd5e1; margin: 6px 0 0; }
.pill-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 16px; }
.pill { display: inline-flex; border: 1px solid var(--line); border-radius: 999px; padding: 8px 11px; color: var(--muted); background: var(--white); font-weight: 700; font-size: .88rem; }
.priority-1 { border-color: color-mix(in srgb, var(--accent) 45%, white); color: var(--brand); background: color-mix(in srgb, var(--accent) 8%, white); }
.priority-2 { border-color: color-mix(in srgb, var(--secondary) 35%, white); color: var(--brand); background: color-mix(in srgb, var(--secondary) 8%, white); }
.price-table { width: 100%; border-collapse: collapse; overflow: hidden; border-radius: 8px; border: 1px solid var(--line); background: var(--white); }
.price-table th, .price-table td { padding: 16px; border-bottom: 1px solid var(--line); text-align: left; }
.price-table th { background: var(--brand); color: var(--white); }
.price-table td:last-child, .price-table th:last-child { text-align: right; font-weight: 900; }
.notice { border-left: 4px solid var(--accent); padding: 16px 18px; background: var(--warning-soft); border-radius: 8px; color: #7c2d12; }
.faq details { border: 1px solid var(--line); border-radius: 8px; background: var(--white); padding: 18px 20px; }
.faq summary { cursor: pointer; font-weight: 900; list-style: none; }
.faq summary::-webkit-details-marker { display: none; }
.footer { background: var(--brand); color: #cbd5e1; padding: 42px 0; }
.footer .wrap { display: grid; grid-template-columns: 1.4fr 1fr 1fr; gap: 26px; }
.footer strong { color: var(--white); }
.footer a { color: inherit; }
.footer-links { display: grid; gap: 7px; }
.service-links { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 10px; }
.service-links a { border: 1px solid var(--line); border-radius: 8px; padding: 12px; background: var(--white); font-weight: 800; }
.service-links a:hover { border-color: var(--accent); color: var(--accent); }
.mobile-call { display: none; }
@media (max-width: 880px) {
  .topbar-inner, .nav { width: min(100% - 24px, 1160px); }
  .topbar-inner { align-items: flex-start; padding: 8px 0; }
  .brand { font-size: 1rem; }
  .top-actions { width: 100%; }
  .top-actions .call-btn { flex: 1; }
  .nav-shell { top: 60px; }
  .nav { align-items: flex-start; padding: 10px 0; }
  .nav-links { gap: 10px; font-size: .86rem; }
  h1 { font-size: 3rem; }
  .section h2 { font-size: 2rem; }
  .hero-grid { grid-template-columns: 1fr; min-height: auto; padding: 46px 0 38px; }
  .grid-4, .grid-3, .grid-2, .trust-grid { grid-template-columns: 1fr; }
  .trust-item { border-right: 0; border-bottom: 1px solid var(--line); }
  .trust-item:last-child { border-bottom: 0; }
  .cta-panel { align-items: flex-start; flex-direction: column; }
  .footer .wrap { grid-template-columns: 1fr; }
  .mobile-call {
    display: flex;
    position: fixed;
    left: 12px;
    right: 12px;
    bottom: 12px;
    z-index: 30;
    justify-content: center;
    box-shadow: 0 18px 40px rgba(0,0,0,.28);
  }
  .footer { padding-bottom: 86px; }
}
"""
    return css_text.replace("__ACCENT__", accent).replace("__SECONDARY__", secondary)


def layout(title: str, description: str, path: str, body: str, schema: dict, build: BuildConfig) -> str:
    canonical = page_url(path, build)
    schema_json = json.dumps(schema, ensure_ascii=False, indent=2)
    primary_key = build.primary_service_key or build.service_keys[0]
    image = str(SERVICES[primary_key]["image"])
    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{esc(canonical)}">
  <meta name="theme-color" content="#101826">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="fr_FR">
  <meta property="og:site_name" content="{esc(BUSINESS["name"])}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{esc(image)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <style>{css(build)}</style>
  <script type="application/ld+json">{schema_json}</script>
</head>
<body>
<a class="skip-link" href="#contenu">Aller au contenu</a>
{body}
</body>
</html>
"""


def header(current_phone_display: str, current_phone_href: str, build: BuildConfig) -> str:
    service_links = "\n      ".join(
        f'<a href="{example_service_path(key, build)}">{esc(SERVICES[key]["label"])}</a>' for key in build.service_keys
    )
    return f"""
<div class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="/"><span class="brand-mark">S</span><span>{esc(BUSINESS["name"])}</span></a>
    <div class="top-actions">
      <a class="ghost-btn" href="https://wa.me/{esc(BUSINESS["whatsapp"])}?text=Bonjour%20Solybat,%20j%27ai%20besoin%20d%27une%20intervention" target="_blank" rel="noopener">WhatsApp</a>
      <a class="call-btn js-call-track" href="tel:{esc(current_phone_href)}">Appeler {esc(current_phone_display)}</a>
    </div>
  </div>
</div>
<div class="nav-shell">
  <nav class="nav" aria-label="Navigation principale">
    <div class="nav-links">
      {service_links}
      <a href="/zones/">Villes</a>
    </div>
    <div class="nav-links">
      <a href="/mentions-legales/">Infos légales</a>
      <a href="#contact">Contact</a>
    </div>
  </nav>
</div>
"""


def footer(current_phone_display: str, current_phone_href: str, build: BuildConfig) -> str:
    scope = service_names(build)
    return f"""
<footer id="contact" class="footer">
  <div class="wrap">
    <div>
      <strong>{esc(BUSINESS["name"])}</strong><br>
      {esc(scope.capitalize())} en urgence, avec qualification de la demande et devis avant intervention.
      <div style="margin-top:12px">{esc(BUSINESS["address"])}</div>
    </div>
    <div>
      <strong>Contact direct</strong>
      <div class="footer-links" style="margin-top:10px">
        <a href="tel:{esc(current_phone_href)}">Téléphone : {esc(current_phone_display)}</a>
        <a href="mailto:{esc(BUSINESS["email"])}">Email : {esc(BUSINESS["email"])}</a>
        <a href="https://wa.me/{esc(BUSINESS["whatsapp"])}?text=Bonjour%20Solybat,%20j%27ai%20besoin%20d%27une%20intervention" target="_blank" rel="noopener">WhatsApp</a>
      </div>
    </div>
    <div>
      <strong>Informations</strong>
      <div class="footer-links" style="margin-top:10px">
        <a href="/zones/">Villes desservies</a>
        <a href="/mentions-legales/">Mentions légales</a>
        <a href="/confidentialite/">Confidentialité</a>
      </div>
      <div style="margin-top:14px">
      <a class="call-btn js-call-track" href="tel:{esc(current_phone_href)}">Appeler {esc(current_phone_display)}</a>
      </div>
    </div>
  </div>
</footer>
<a class="call-btn mobile-call js-call-track" href="tel:{esc(current_phone_href)}">Appeler maintenant</a>
<script>
document.querySelectorAll('.js-call-track').forEach(function(link) {{
  link.addEventListener('click', function() {{
    if (window.gtag) {{
      window.gtag('event', 'phone_call_click', {{
        event_category: 'lead',
        event_label: window.location.pathname
      }});
    }}
  }});
}});
</script>
"""


def local_business_schema(
    title: str,
    description: str,
    path: str,
    city: City | None,
    service_key: str | None,
    build: BuildConfig,
) -> dict:
    phone_display = BUSINESS["fr_phone_display"]
    phone_href = BUSINESS["fr_phone_href"]
    country = "FR"
    if city:
        phone_display, phone_href = phone_for(city)
        country = city.country
    service = SERVICES[service_key] if service_key else SERVICES["serrurier"]
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": service["schema_type"],
                "@id": f"{page_url(path, build)}#business",
                "name": BUSINESS["name"],
                "image": service.get("image"),
                "url": page_url(path, build),
                "telephone": phone_display,
                "email": BUSINESS["email"],
                "priceRange": "€€",
                "contactPoint": {
                    "@type": "ContactPoint",
                    "telephone": phone_href,
                    "contactType": "customer service",
                    "areaServed": "FR, CH",
                    "availableLanguage": ["fr"],
                },
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": BUSINESS["address"],
                    "addressCountry": country,
                },
                "openingHoursSpecification": {
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    "opens": "00:00",
                    "closes": "23:59",
                },
            },
            {
                "@type": "WebPage",
                "@id": f"{page_url(path, build)}#webpage",
                "url": page_url(path, build),
                "name": title,
                "description": description,
                "isPartOf": {"@type": "WebSite", "name": BUSINESS["name"], "url": build.site_url},
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{page_url(path, build)}#breadcrumb",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Accueil",
                        "item": build.site_url.rstrip("/") + "/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": title,
                        "item": page_url(path, build),
                    },
                ],
            },
        ],
    }
    if city:
        schema["@graph"][0]["areaServed"] = {"@type": "City", "name": city.name}
    if city and service_key:
        cases = SERVICE_LOCAL_CASES[service_key]
        faq_question, faq_answer = cases["faq"]
        schema["@graph"].append(
            {
                "@type": "FAQPage",
                "@id": f"{page_url(path, build)}#faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f"Intervenez-vous à {city.name} ?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f"Oui, les demandes sur {city.name} sont qualifiées par téléphone avant déplacement afin de confirmer le secteur, le délai possible et les conditions.",
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "Le devis est-il annoncé avant intervention ?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Oui. Le prix dépend de l'accès, de l'horaire, du matériel et de la complexité. Il doit être confirmé avant le début des travaux.",
                        },
                    },
                    {
                        "@type": "Question",
                        "name": faq_question,
                        "acceptedAnswer": {"@type": "Answer", "text": faq_answer},
                    },
                ],
            }
        )
    return schema


def service_links_for_city(city: City, build: BuildConfig, exclude_service_key: str | None = None) -> str:
    links = []
    for key in build.service_keys:
        if key == exclude_service_key:
            continue
        service = SERVICES[key]
        links.append(f'<a href="{service_path(city, key, build)}">{esc(service["label"])} à {esc(city.name)}</a>')
    if not links:
        return ""
    return '<div class="service-links">' + "\n".join(links) + "</div>"


def local_seo_for(city: City, nearby: list[City]) -> dict[str, object]:
    if city.slug in LOCAL_SEO:
        return LOCAL_SEO[city.slug]
    nearby_names = [item.name for item in nearby[:6]]
    if len(nearby_names) < 3:
        nearby_names = [city.zone, city.region, city.name]
    return {
        "micro_areas": nearby_names,
        "local_note": f"Cette page est rattachée au bassin {city.zone}. Les preuves locales doivent être ajoutées progressivement pour renforcer son indexation.",
    }


def local_enrichment_section(city: City, service_key: str, nearby: list[City]) -> str:
    local = local_seo_for(city, nearby)
    cases = SERVICE_LOCAL_CASES[service_key]
    micro_areas = [str(item) for item in local["micro_areas"]]
    sector_pills = " ".join(f'<span class="pill">{esc(area)}</span>' for area in micro_areas)
    case_items = "\n".join(f"<li>{esc(item)} à {esc(city.name)} ou dans un secteur proche</li>" for item in cases["cases"])
    nearby_sentence = ", ".join(item.name for item in nearby[:5])
    if nearby_sentence:
        nearby_text = f"Le maillage local relie aussi {esc(city.name)} aux communes proches comme {esc(nearby_sentence)}."
    else:
        nearby_text = f"Le maillage local relie cette page au bassin {esc(city.zone)}."
    return f"""
  <section class="section">
    <div class="wrap grid-2">
      <div class="card">
        <h2>Repères locaux à {esc(city.name)}</h2>
        <p>{esc(local["local_note"])}</p>
        <p>{nearby_text}</p>
        <div class="pill-row">{sector_pills}</div>
      </div>
      <div class="card">
        <h2>{esc(cases["title"])}</h2>
        <ul class="check-list">{case_items}</ul>
      </div>
    </div>
  </section>
"""


def trust_band(service: dict[str, object]) -> str:
    items = [str(item) for item in service["trust_points"]]
    cards = "\n".join(
        f"""
        <div class="trust-item">
          <strong>{esc(item)}</strong>
          <span>Point vérifié avant ou pendant l'intervention.</span>
        </div>
        """
        for item in items[:4]
    )
    return f"""
  <section class="trust-band" aria-label="Garanties d'intervention">
    <div class="wrap trust-grid">{cards}</div>
  </section>
"""


def process_section(service: dict[str, object], city: City) -> str:
    steps = [(str(title), str(text)) for title, text in service["steps"]]
    cards = "\n".join(
        f"""
        <article class="card">
          <span class="card-number">{index}</span>
          <h3>{esc(title)}</h3>
          <p>{esc(text)}</p>
        </article>
        """
        for index, (title, text) in enumerate(steps, start=1)
    )
    return f"""
  <section class="section alt">
    <div class="wrap">
      <div class="section-head">
        <h2>Déroulé d'intervention à {esc(city.name)}</h2>
        <p>Le but est de qualifier correctement l'urgence, d'éviter les mauvaises surprises et de garder une trace claire de ce qui est prévu.</p>
      </div>
      <div class="grid-4">{cards}</div>
    </div>
  </section>
"""


def expertise_section(city: City, service_key: str, service: dict[str, object], nearby: list[City]) -> str:
    audience = str(service["audience"])
    promise = str(service["promise"])
    local = local_seo_for(city, nearby)
    areas = ", ".join(str(item) for item in local["micro_areas"][:4])
    return f"""
  <section class="section">
    <div class="wrap grid-2">
      <div class="split-panel">
        <h2>Une page dédiée, pas un service mélangé</h2>
        <p>{esc(BUSINESS["name"])} présente ici uniquement le besoin {esc(SERVICES[service_key]["plural"])} pour {esc(audience)} à {esc(city.name)}. Cette séparation clarifie le message, les annonces Google Ads et le suivi des appels.</p>
      </div>
      <div>
        <h2>Ce qui est vérifié avant déplacement</h2>
        <p>{esc(promise)}</p>
        <p>Les secteurs comme {esc(areas)} sont traités avec la même logique : comprendre l'accès, l'urgence, le matériel possible et les conditions tarifaires avant validation.</p>
      </div>
    </div>
  </section>
"""


def final_cta_section(city: City, service: dict[str, object], phone_display: str, phone_href: str) -> str:
    return f"""
  <section class="section">
    <div class="wrap">
      <div class="cta-panel">
        <div>
          <h2>Besoin d'un avis rapide à {esc(city.name)} ?</h2>
          <p>Appelez avec l'adresse, une photo si possible et une description courte du problème. Le prix est confirmé avant intervention.</p>
        </div>
        <a class="call-btn js-call-track" href="tel:{esc(phone_href)}">Appeler {esc(phone_display)}</a>
      </div>
    </div>
  </section>
"""


def service_page(city: City, service_key: str, all_cities: list[City], build: BuildConfig) -> str:
    service = SERVICES[service_key]
    phone_display, phone_href = phone_for(city)
    path = service_path(city, service_key, build)
    title = f"{service['label']} à {city.name} | {BUSINESS['name']} urgence 24/7"
    description = f"{BUSINESS['name']} : {service['short']} Intervention à {city.name} et secteur proche. Appel direct, devis avant intervention."
    nearby = [c for c in all_cities if c.zone == city.zone and c.slug != city.slug][:8]
    nearby_links = " ".join(f'<a class="pill" href="{service_path(c, service_key, build)}">{esc(c.name)}</a>' for c in nearby)
    benefits = "\n".join(f"<li>{esc(item)}</li>" for item in service["benefits"])
    pricing_rows = "\n".join(
        f"<tr><td>{esc(label)}</td><td>{esc(price)}</td></tr>" for label, price in service["pricing"]
    )
    other_services = service_links_for_city(city, build, service_key)
    hero = service["hero"].format(city=city.name)
    headline = service["headline"].format(city=city.name)
    local_section = local_enrichment_section(city, service_key, nearby)
    trust_section = trust_band(service)
    expertise = expertise_section(city, service_key, service, nearby)
    process = process_section(service, city)
    final_cta = final_cta_section(city, service, phone_display, phone_href)
    service_faq_question, service_faq_answer = SERVICE_LOCAL_CASES[service_key]["faq"]
    if other_services:
        related_section = f"""
  <section class="section">
    <div class="wrap grid-2">
      <div class="card">
        <h2>Prestations complémentaires à {esc(city.name)}</h2>
        <p>Les prestations restent séparées pour garder un message clair et des URLs exploitables par métier.</p>
        {other_services}
      </div>
      <div class="card">
        <h2>Préparer votre appel</h2>
        <p>Indiquez la ville, l'accès au logement ou au local, l'urgence exacte, les photos disponibles et l'horaire souhaité. Ces éléments permettent d'éviter un déplacement mal qualifié.</p>
      </div>
    </div>
  </section>
"""
    else:
        related_section = f"""
  <section class="section">
    <div class="wrap">
      <div class="card">
        <h2>Préparer votre appel</h2>
        <p>Indiquez la ville, l'accès au logement ou au local, l'urgence exacte, les photos disponibles et l'horaire souhaité. Ces éléments permettent d'éviter un déplacement mal qualifié.</p>
      </div>
    </div>
  </section>
"""
    body = f"""
{header(phone_display, phone_href, build)}
<main id="contenu">
  <section class="hero" style="--hero-image: url('{esc(service["image"])}')">
    <div class="hero-grid">
      <div>
        <span class="eyebrow">Urgence locale 24/7 · {esc(city.zone)}</span>
        <h1>{esc(headline)}</h1>
        <p>{esc(hero)} Un interlocuteur récupère les informations essentielles et confirme les conditions avant déplacement.</p>
        <div class="hero-badges">
          <span class="hero-badge">Devis avant intervention</span>
          <span class="hero-badge">Appel direct</span>
          <span class="hero-badge">France et Genève</span>
        </div>
        <div class="cta-row">
          <a class="call-btn js-call-track" href="tel:{esc(phone_href)}">Appeler {esc(phone_display)}</a>
          <a class="ghost-btn" href="#tarifs">Voir les tarifs</a>
        </div>
      </div>
      <aside class="hero-card" aria-label="Points clés">
        <h2>Intervention à {esc(city.name)}</h2>
        <ul>{benefits}</ul>
        <div class="hero-meta">
          <div><strong>24/7</strong><span>urgence qualifiée</span></div>
          <div><strong>Devis</strong><span>avant travaux</span></div>
        </div>
      </aside>
    </div>
  </section>

{trust_section}

  <section class="section">
    <div class="wrap grid-2">
      <div>
        <div class="section-head">
          <h2>{esc(service["label"])} local à {esc(city.name)}</h2>
          <p>{esc(BUSINESS["name"])} traite les demandes urgentes et planifiées avec une information claire dès le premier appel : secteur, nature du problème, délai possible et devis avant intervention.</p>
        </div>
        <ul class="check-list">{benefits}</ul>
      </div>
      <div class="card">
        <h3>Zones proches couvertes</h3>
        <p>Selon la disponibilité des équipes, une intervention peut aussi être organisée dans les communes proches du même secteur.</p>
        <div class="pill-row">{nearby_links}</div>
      </div>
    </div>
  </section>

{expertise}

{local_section}

{process}

  <section id="tarifs" class="section alt">
    <div class="wrap">
      <div class="section-head">
        <h2>Tarifs et devis</h2>
        <p>Les prix dépendent de l'accès, de l'horaire, du matériel et de la complexité. Le devis est annoncé avant intervention.</p>
      </div>
      <table class="price-table">
        <thead><tr><th>Prestation</th><th>Prix indicatif</th></tr></thead>
        <tbody>{pricing_rows}</tbody>
      </table>
      <p class="notice">Les tarifs sont indicatifs. Le prix final est confirmé avant toute intervention, notamment en soirée, week-end, jour férié ou lorsqu'une pièce spécifique est nécessaire.</p>
    </div>
  </section>

{related_section}

{final_cta}

  <section id="faq" class="section alt faq">
    <div class="wrap">
      <div class="section-head">
        <h2>Questions fréquentes à {esc(city.name)}</h2>
      </div>
      <div class="grid-2">
        <details open><summary>Intervenez-vous vraiment à {esc(city.name)} ?</summary><p>Oui, les demandes sur {esc(city.name)} sont traitées avec une priorité locale et une vérification du secteur avant déplacement.</p></details>
        <details><summary>Le devis est-il obligatoire ?</summary><p>Oui. En urgence comme sur rendez-vous, le prix doit être annoncé avant l'intervention.</p></details>
        <details><summary>{esc(service_faq_question)}</summary><p>{esc(service_faq_answer)}</p></details>
        <details><summary>Quel numéro utiliser ?</summary><p>Utilisez un numéro local cohérent avec la zone : +41 pour Genève, 04 pour les zones France couvertes.</p></details>
      </div>
    </div>
  </section>
</main>
{footer(phone_display, phone_href, build)}
"""
    schema = local_business_schema(title, description, path, city, service_key, build)
    return layout(title, description, path, body, schema, build)


def city_page(city: City, all_cities: list[City], build: BuildConfig) -> str:
    phone_display, phone_href = phone_for(city)
    path = city_hub_path(city)
    title = f"Intervention à {city.name} | Serrurier, plombier, dégorgement Solybat"
    description = f"Solybat intervient à {city.name} en serrurerie, plomberie et dégorgement. Choisissez le service adapté : urgence serrure, fuite d'eau ou canalisation bouchée."
    nearby = [c for c in all_cities if c.zone == city.zone and c.slug != city.slug][:8]
    local = local_seo_for(city, nearby)
    sector_pills = " ".join(f'<span class="pill">{esc(area)}</span>' for area in local["micro_areas"])
    nearby_links = " ".join(f'<a class="pill" href="{city_hub_path(c)}">{esc(c.name)}</a>' for c in nearby)
    service_cards = "\n".join(
        f"""
        <article class="card">
          <h2>{esc(service["label"])} à {esc(city.name)}</h2>
          <p>{esc(service["short"])}</p>
          <a class="pill priority-2" href="{service_path(city, service_key, build)}">Voir la page {esc(service["label"].lower())}</a>
        </article>
        """
        for service_key in build.service_keys
        for service in [SERVICES[service_key]]
    )
    body = f"""
{header(phone_display, phone_href, build)}
<main id="contenu">
  <section class="hero" style="--hero-image: url('https://images.unsplash.com/photo-1558002038-1091a1661116?q=80&w=1800&auto=format&fit=crop')">
    <div class="hero-grid">
      <div>
        <span class="eyebrow">Solybat · {esc(city.zone)}</span>
        <h1>Intervention à {esc(city.name)}</h1>
        <p>Serrurerie, plomberie et dégorgement : choisissez le service correspondant à votre urgence pour accéder à la page locale la plus précise.</p>
        <div class="cta-row">
          <a class="call-btn js-call-track" href="tel:{esc(phone_href)}">Appeler {esc(phone_display)}</a>
          <a class="ghost-btn" href="#services-ville">Choisir un service</a>
        </div>
      </div>
      <aside class="hero-card">
        <h2>Services disponibles à {esc(city.name)}</h2>
        <ul>
          <li>Ouverture de porte et serrure bloquée</li>
          <li>Fuite d'eau et dépannage sanitaire</li>
          <li>Canalisation bouchée et camion pompe</li>
          <li>Devis confirmé avant intervention</li>
        </ul>
      </aside>
    </div>
  </section>

  <section id="services-ville" class="section">
    <div class="wrap">
      <div class="section-head">
        <h2>Quel service cherchez-vous à {esc(city.name)} ?</h2>
        <p>Chaque métier a sa propre page locale pour répondre plus vite à l'intention de recherche.</p>
      </div>
      <div class="grid-3">{service_cards}</div>
    </div>
  </section>

  <section class="section alt">
    <div class="wrap grid-2">
      <div class="card">
        <h2>Repères locaux</h2>
        <p>{esc(local["local_note"])}</p>
        <div class="pill-row">{sector_pills}</div>
      </div>
      <div class="card">
        <h2>Communes proches</h2>
        <p>Le maillage relie {esc(city.name)} aux villes du même bassin d'intervention.</p>
        <div class="pill-row">{nearby_links}</div>
      </div>
    </div>
  </section>
</main>
{footer(phone_display, phone_href, build)}
"""
    schema = local_business_schema(title, description, path, city, "serrurier", build)
    return layout(title, description, path, body, schema, build)


def home_page(cities: list[City], build: BuildConfig) -> str:
    phone_display = BUSINESS["fr_phone_display"]
    phone_href = BUSINESS["fr_phone_href"]
    homepage_path = "/campagnes-locales/" if build.preserve_existing_home else "/"
    p1 = [c for c in cities if c.priority == 1]

    if build.primary_service_key:
        primary = SERVICES[build.primary_service_key]
        primary_label = str(primary["label"])
        service_scope = service_names(build)
        title = f"{BUSINESS['name']} | {primary_label} urgence 24/7"
        description = f"{BUSINESS['name']} intervient en {service_scope} avec des pages locales par ville, appel direct et devis avant intervention."
        domain_scope = "la serrurerie" if build.primary_service_key == "serrurier" else "la plomberie"
        priority_links = "\n".join(
            f'<a class="pill priority-1" href="{service_path(c, build.primary_service_key, build)}">{esc(c.name)}</a>' for c in p1
        )
        cards = "\n".join(
            f"""
        <article class="card">
          <h3>{esc(SERVICES[key]["label"])}</h3>
          <p>{esc(SERVICES[key]["short"])}</p>
          <a class="pill priority-2" href="{example_service_path(key, build)}">Exemple : {esc(SERVICES[key]["label"])} à Lyon</a>
        </article>
        """
            for key in build.service_keys
        )
        primary_benefits = "\n".join(f"<li>{esc(item)}</li>" for item in primary["benefits"])
        home_trust = trust_band(primary)
        body = f"""
{header(phone_display, phone_href, build)}
<main id="contenu">
  <section class="hero" style="--hero-image: url('{esc(primary["image"])}')">
    <div class="hero-grid">
      <div>
        <span class="eyebrow">{esc(BUSINESS["name"])} · urgence locale</span>
        <h1>{esc(primary_label)} par ville</h1>
        <p>Un service dédié à {esc(domain_scope)} pour répondre vite aux demandes urgentes, ville par ville, avec une qualification claire avant déplacement.</p>
        <div class="hero-badges">
          <span class="hero-badge">Intervention locale</span>
          <span class="hero-badge">Devis avant travaux</span>
          <span class="hero-badge">Appel direct</span>
        </div>
        <div class="cta-row">
          <a class="call-btn js-call-track" href="tel:{esc(phone_href)}">Appeler {esc(phone_display)}</a>
          <a class="ghost-btn" href="/zones/">Voir les villes</a>
        </div>
      </div>
      <aside class="hero-card">
        <h2>Intervention locale</h2>
        <ul>
          {primary_benefits}
          <li>Devis annoncé avant intervention</li>
        </ul>
        <div class="hero-meta">
          <div><strong>{len(cities)}</strong><span>villes ciblées</span></div>
          <div><strong>1</strong><span>domaine métier</span></div>
        </div>
      </aside>
    </div>
  </section>

{home_trust}

  <section class="section">
    <div class="wrap">
      <div class="section-head center">
        <h2>Prestations couvertes</h2>
        <p>Les prestations sont présentées séparément pour aider l'appelant à expliquer rapidement son besoin.</p>
      </div>
      <div class="grid-3">{cards}</div>
    </div>
  </section>

  <section class="section alt">
    <div class="wrap">
      <div class="section-head">
        <h2>Un parcours clair pour votre urgence</h2>
        <p>L'objectif est simple : comprendre vite le problème, confirmer la zone et annoncer les conditions avant intervention.</p>
      </div>
      <div class="grid-3">
        <article class="card">
          <h3>Votre ville</h3>
          <p>Les pages locales permettent de vérifier rapidement la zone concernée et le bon numéro à utiliser.</p>
        </article>
        <article class="card">
          <h3>Votre problème</h3>
          <p>La demande est qualifiée avant déplacement pour éviter une intervention mal préparée.</p>
        </article>
        <article class="card">
          <h3>Votre accord</h3>
          <p>Le prix et les conditions doivent être confirmés avant le début de l'intervention.</p>
        </article>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="section-head">
        <h2>Villes couvertes en priorité</h2>
        <p>Les liens ci-dessous pointent directement vers les pages locales du site {esc(primary_label.lower())}.</p>
      </div>
      <div class="pill-row">{priority_links}</div>
    </div>
  </section>
</main>
{footer(phone_display, phone_href, build)}
"""
        schema = local_business_schema(title, description, homepage_path, None, build.primary_service_key, build)
        return layout(title, description, homepage_path, body, schema, build)

    title = f"{BUSINESS['name']} | Serrurerie, plomberie et dégorgement"
    description = "Solybat intervient en serrurerie, plomberie et dégorgement camion pompe avec des pages locales par ville et par métier."
    priority_links = "\n".join(
        f'<a class="pill priority-1" href="{service_path(c, "serrurier", build)}">{esc(c.name)}</a>' for c in p1
    )
    cards = "\n".join(
        f"""
        <article class="card">
          <h3>{esc(service["label"])}</h3>
          <p>{esc(service["short"])}</p>
          <a class="pill priority-2" href="{example_service_path(key, build)}">Exemple : {esc(service["label"])} à Lyon</a>
        </article>
        """
        for key in build.service_keys
        for service in [SERVICES[key]]
    )
    body = f"""
{header(phone_display, phone_href, build)}
<main id="contenu">
  <section class="hero" style="--hero-image: url('https://images.unsplash.com/photo-1558002038-1091a1661116?q=80&w=1800&auto=format&fit=crop')">
    <div class="hero-grid">
      <div>
        <span class="eyebrow">Solybat · urgence locale</span>
        <h1>Serrurerie, plomberie et dégorgement par ville</h1>
        <p>Un seul point d'entrée pour les urgences locales : ouverture de porte, fuite d'eau, canalisation bouchée et intervention camion pompe selon le besoin.</p>
        <div class="cta-row">
          <a class="call-btn js-call-track" href="tel:{esc(phone_href)}">Appeler {esc(phone_display)}</a>
      <a class="ghost-btn" href="/campagnes-locales/">Voir les services</a>
        </div>
      </div>
      <aside class="hero-card">
        <h2>Intervention locale</h2>
        <ul>
          <li>Serrurerie, plomberie et dégorgement</li>
          <li>France et canton de Genève</li>
          <li>Appel direct sur mobile</li>
          <li>Devis annoncé avant intervention</li>
        </ul>
      </aside>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="section-head center">
        <h2>Services Solybat</h2>
        <p>Les services sont présentés séparément pour que chaque demande trouve rapidement la bonne réponse.</p>
      </div>
      <div class="grid-3">{cards}</div>
    </div>
  </section>

  <section class="section alt">
    <div class="wrap">
      <div class="section-head">
        <h2>Villes couvertes en priorité</h2>
        <p>Les grandes zones ci-dessous concentrent les demandes les plus urgentes et les volumes d'intervention les plus importants.</p>
      </div>
      <div class="pill-row">{priority_links}</div>
    </div>
  </section>
</main>
{footer(phone_display, phone_href, build)}
"""
    schema = local_business_schema(title, description, homepage_path, None, "serrurier", build)
    return layout(title, description, homepage_path, body, schema, build)


def zones_page(cities: list[City], build: BuildConfig) -> str:
    phone_display = BUSINESS["fr_phone_display"]
    phone_href = BUSINESS["fr_phone_href"]
    scope = service_names(build)
    title = f"Zones d'intervention {build.label} | {BUSINESS['name']}"
    description = f"Toutes les villes ciblées par Solybat pour les pages {scope}."
    sections: list[str] = []
    zones = sorted({(c.region, c.zone) for c in cities})
    for region, zone in zones:
        zone_cities = [c for c in cities if c.region == region and c.zone == zone]
        links = "\n".join(
            f"""
            <div class="card">
              <h3><a href="{city_hub_path(c) if build.include_city_hubs else service_path(c, build.primary_service_key or build.service_keys[0], build)}">{esc(c.name)}</a></h3>
              <p>Priorité {c.priority} · {esc(c.country)}</p>
              {service_links_for_city(c, build, build.primary_service_key if not build.include_city_hubs else None)}
            </div>
            """
            for c in zone_cities
        )
        sections.append(
            f"""
            <section class="section">
              <div class="wrap">
                <div class="section-head">
                  <h2>{esc(zone)}</h2>
                  <p>{esc(region)} · {len(zone_cities)} villes ciblées</p>
                </div>
                <div class="grid-3">{links}</div>
              </div>
            </section>
            """
        )
    body = f"""
{header(phone_display, phone_href, build)}
<main id="contenu">
  <section class="hero" style="--hero-image: url('https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1800&auto=format&fit=crop')">
    <div class="hero-grid">
      <div>
        <span class="eyebrow">Ciblage géographique</span>
        <h1>Zones d'intervention {esc(build.label)}</h1>
        <p>Liste complète des villes couvertes, avec accès direct aux pages {esc(scope)}.</p>
      </div>
      <aside class="hero-card">
        <h2>Règle d'exploitation</h2>
        <ul>
          <li>Accès rapide par ville</li>
          <li>Services séparés par domaine</li>
          <li>France et canton de Genève</li>
        </ul>
      </aside>
    </div>
  </section>
  {''.join(sections)}
</main>
{footer(phone_display, phone_href, build)}
"""
    schema_key = build.primary_service_key or build.service_keys[0]
    schema = local_business_schema(title, description, "/zones/", None, schema_key, build)
    return layout(title, description, "/zones/", body, schema, build)


def legal_page(kind: str, build: BuildConfig) -> str:
    phone_display = BUSINESS["fr_phone_display"]
    phone_href = BUSINESS["fr_phone_href"]
    schema_key = build.primary_service_key or build.service_keys[0]
    scope = service_names(build)
    if kind == "mentions":
        path = "/mentions-legales/"
        title = f"Mentions légales | {BUSINESS['name']}"
        description = f"Mentions légales du site {BUSINESS['name']} dédié aux interventions {scope}."
        content = f"""
  <section class="section">
    <div class="wrap grid-2">
      <div>
        <div class="section-head">
          <span class="eyebrow">Informations légales</span>
          <h1>Mentions légales</h1>
          <p>Cette page regroupe les informations d'édition, de contact et d'hébergement du site.</p>
        </div>
      </div>
      <div class="card">
        <h2>Éditeur du site</h2>
        <p><strong>{esc(BUSINESS["legal_name"])}</strong><br>{esc(BUSINESS["legal_form"])}<br>{esc(BUSINESS["address"])}</p>
        <p>SIRET : {esc(BUSINESS["siret"])}<br>TVA : {esc(BUSINESS["vat"])}</p>
        <p>Responsable de publication : {esc(BUSINESS["director"])}</p>
      </div>
    </div>
  </section>

  <section class="section alt">
    <div class="wrap grid-2">
      <div class="card">
        <h2>Contact</h2>
        <p>Téléphone : <a href="tel:{esc(phone_href)}">{esc(phone_display)}</a><br>Email : <a href="mailto:{esc(BUSINESS["email"])}">{esc(BUSINESS["email"])}</a></p>
      </div>
      <div class="card">
        <h2>Hébergement</h2>
        <p>{esc(BUSINESS["host_name"])}<br>{esc(BUSINESS["host_address"])}</p>
      </div>
      <div class="card">
        <h2>Activité</h2>
        <p>Le site présente des services d'intervention {esc(scope)}. Les tarifs affichés sont indicatifs et peuvent varier selon la zone, l'horaire, l'accès, le matériel et la complexité de l'intervention.</p>
      </div>
      <div class="card">
        <h2>Responsabilité</h2>
        <p>Les informations publiées sont fournies à titre informatif. Un devis ou prix confirmé doit être communiqué avant toute intervention payante.</p>
      </div>
    </div>
  </section>
"""
    elif kind == "privacy":
        path = "/confidentialite/"
        title = f"Politique de confidentialité | {BUSINESS['name']}"
        description = f"Politique de confidentialité du site {BUSINESS['name']} dédié aux interventions {scope}."
        content = f"""
  <section class="section">
    <div class="wrap grid-2">
      <div>
        <div class="section-head">
          <span class="eyebrow">Données personnelles</span>
          <h1>Politique de confidentialité</h1>
          <p>Cette page explique quelles données peuvent être transmises lors d'une demande d'intervention et comment exercer vos droits.</p>
        </div>
      </div>
      <div class="card">
        <h2>Responsable du traitement</h2>
        <p>{esc(BUSINESS["legal_name"])}<br>{esc(BUSINESS["address"])}<br><a href="mailto:{esc(BUSINESS["email"])}">{esc(BUSINESS["email"])}</a></p>
      </div>
    </div>
  </section>

  <section class="section alt">
    <div class="wrap grid-2">
      <div class="card">
        <h2>Données concernées</h2>
        <p>Lors d'un appel, d'un email ou d'un message WhatsApp, vous pouvez transmettre votre nom, téléphone, adresse d'intervention, photos du problème et informations nécessaires à la qualification de l'urgence.</p>
      </div>
      <div class="card">
        <h2>Finalités</h2>
        <p>Les données servent à répondre à la demande, qualifier l'intervention, établir un devis, organiser le déplacement et assurer le suivi administratif ou commercial lié à l'intervention.</p>
      </div>
      <div class="card">
        <h2>Durée de conservation</h2>
        <p>Les données sont conservées pendant la durée nécessaire au traitement de la demande, puis selon les obligations comptables, contractuelles ou légales applicables.</p>
      </div>
      <div class="card">
        <h2>Vos droits</h2>
        <p>Vous pouvez demander l'accès, la rectification ou la suppression de vos données en écrivant à <a href="mailto:{esc(BUSINESS["email"])}">{esc(BUSINESS["email"])}</a>.</p>
      </div>
      <div class="card">
        <h2>Mesure d'audience et appels</h2>
        <p>Le site peut utiliser des outils de mesure d'audience ou de suivi de clics téléphone pour comprendre l'origine des demandes. Les paramètres exacts doivent être vérifiés lors de l'installation des tags publicitaires.</p>
      </div>
      <div class="card">
        <h2>Services tiers</h2>
        <p>Un clic WhatsApp ouvre le service WhatsApp. Les appels, emails et outils publicitaires peuvent impliquer leurs propres traitements de données.</p>
      </div>
    </div>
  </section>
"""
    else:
        raise ValueError(f"Unknown legal page: {kind}")

    body = f"""
{header(phone_display, phone_href, build)}
<main id="contenu">
{content}
</main>
{footer(phone_display, phone_href, build)}
"""
    schema = local_business_schema(title, description, path, None, schema_key, build)
    return layout(title, description, path, body, schema, build)


def sitemap(cities: list[City], build: BuildConfig) -> str:
    paths = ["/zones/", "/mentions-legales/", "/confidentialite/"]
    if build.preserve_existing_home:
        paths = ["/", "/campagnes-locales/", "/zones/", "/mentions-legales/", "/confidentialite/"]
    else:
        paths.insert(0, "/")
    for city in cities:
        if build.include_city_hubs:
            paths.append(city_hub_path(city))
        for service_key in build.service_keys:
            paths.append(service_path(city, service_key, build))

    city_paths = {city_hub_path(city) for city in cities} if build.include_city_hubs else set()
    service_paths = {service_path(city, service_key, build) for city in cities for service_key in build.service_keys}

    def sitemap_priority(path: str) -> str:
        if path == "/":
            return "1.0"
        if path in service_paths:
            return "0.8"
        if path in city_paths:
            return "0.6"
        return "0.5"

    urls = "\n".join(
        f"  <url><loc>{esc(page_url(path, build))}</loc><lastmod>{GENERATED_DATE}</lastmod><changefreq>weekly</changefreq><priority>{sitemap_priority(path)}</priority></url>"
        for path in paths
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'


def write_ads_files(cities: list[City], build: BuildConfig) -> None:
    ads_dir = operations_root(build) / "google-ads"
    ads_dir.mkdir(parents=True, exist_ok=True)

    with (ads_dir / "negative-keywords.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["level", "match_type", "negative_keyword"])
        for keyword in NEGATIVE_KEYWORDS:
            writer.writerow(["campaign", "Phrase", keyword])

    with (ads_dir / "landing-pages.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["priority", "country", "region", "zone", "city", "service", "final_url", "recommended_phone"])
        for city in cities:
            phone_display, _ = phone_for(city)
            for service_key in build.service_keys:
                service = SERVICES[service_key]
                writer.writerow([
                    city.priority,
                    city.country,
                    city.region,
                    city.zone,
                    city.name,
                    service["label"],
                    page_url(service_path(city, service_key, build), build),
                    phone_display,
                ])

    with (ads_dir / "keyword-plan.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["campaign", "ad_group", "match_type", "keyword", "google_ads_syntax", "final_url"])
        for city in cities:
            for service_key in build.service_keys:
                service = SERVICES[service_key]
                campaign = f"{service['label']} - {'Genève' if city.country == 'CH' else city.region}"
                ad_group = f"{service['label']} - {city.name}"
                final_url = page_url(service_path(city, service_key, build), build)
                for template in service["keywords"]:
                    keyword = template.format(city=city.name)
                    writer.writerow([campaign, ad_group, "Phrase", keyword, f'"{keyword}"', final_url])

    with (ads_dir / "campaign-settings.md").open("w", encoding="utf-8") as f:
        f.write(f"""# Configuration Google Ads Solybat

## Structure

- 1 campagne par métier et grande zone.
- 1 groupe d'annonces par ville.
- 1 page finale par ville et métier.
- Type de correspondance : expression exacte uniquement, avec guillemets.
- Requête large interdite au lancement.

## Ciblage

- Option de lieu : Présence, personnes situées dans vos zones ciblées.
- Ne pas utiliser l'option par défaut Présence ou intérêt.
- Genève : numéro suisse +41.
- France : numéro local/régional en 04.

## Enchères

- Phase 1, 14 jours : CPC maximal ou Maximiser les clics avec plafonds.
- Phase 2 : basculer sur Maximiser les conversions puis CPA cible après 15 à 30 appels suivis.

## Tracking

- Installer le tag Google Ads / gtag.
- Déclarer les clics sur `.js-call-track` comme conversions d'appel.
- Ajouter le call tracking dynamique avant d'activer le CPA cible.
- Installer ClickCease ou équivalent avant ouverture du budget.

## A remplacer avant production

- Domaine actuel dans ce build : `{build.site_url}`
- Numéro France actuel : `{BUSINESS["fr_phone_display"]}`
- Numéro Genève actuel : `{BUSINESS["ch_phone_display"]}`
""")


def write_seo_files(cities: list[City], build: BuildConfig) -> None:
    seo_dir = operations_root(build) / "seo"
    seo_dir.mkdir(parents=True, exist_ok=True)
    priority_cities = [city for city in cities if city.priority == 1]

    with (seo_dir / "local-enrichment-priority.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "priority",
            "city",
            "service",
            "url",
            "micro_areas_to_cover",
            "proofs_to_collect",
            "photos_to_collect",
            "reviews_to_request",
            "content_status",
        ])
        for city in priority_cities:
            local = local_seo_for(city, [])
            areas = ", ".join(str(item) for item in local["micro_areas"])
            for service_key in build.service_keys:
                service = SERVICES[service_key]
                writer.writerow([
                    city.priority,
                    city.name,
                    service["label"],
                    page_url(service_path(city, service_key, build), build),
                    areas,
                    "adresse/secteur réel d'intervention, problème traité, délai annoncé, solution appliquée",
                    "photo véhicule/outillage, photo avant-après si autorisée, photo non identifiable du chantier",
                    "demander un avis client après intervention réussie",
                    "base enrichie générée, preuves réelles à ajouter",
                ])

    with (seo_dir / "content-collection-checklist.md").open("w", encoding="utf-8") as f:
        f.write("""# Checklist SEO local Solybat

Objectif : renforcer progressivement les pages villes sans publier de fausses preuves.

## Pour chaque ville prioritaire

- Ajouter 3 à 6 secteurs réels couverts.
- Ajouter au moins 1 exemple d'intervention réel par métier.
- Ajouter une photo non sensible : véhicule, matériel, chantier sans visage ni adresse visible.
- Ajouter 1 avis client réel si le client l'a publié ou autorisé.
- Ajouter un délai moyen réaliste par zone si la donnée est suivie.
- Vérifier que le numéro affiché correspond bien au pays et à la zone.

## Ne pas publier

- Faux avis.
- Faux chantiers.
- Photos prises ailleurs sans rapport avec Solybat.
- Délais garantis impossibles à tenir.
- Coordonnées client, plaques, digicodes ou adresses privées.
""")


def production_warnings() -> list[str]:
    checks = {
        "SOLYBAT_ADDRESS": BUSINESS["address"],
        "SOLYBAT_FR_PHONE_DISPLAY": BUSINESS["fr_phone_display"],
        "SOLYBAT_FR_PHONE_HREF": BUSINESS["fr_phone_href"],
        "SOLYBAT_CH_PHONE_DISPLAY": BUSINESS["ch_phone_display"],
        "SOLYBAT_CH_PHONE_HREF": BUSINESS["ch_phone_href"],
        "SOLYBAT_WHATSAPP": BUSINESS["whatsapp"],
        "SOLYBAT_LEGAL_FORM": BUSINESS["legal_form"],
        "SOLYBAT_SIRET": BUSINESS["siret"],
        "SOLYBAT_DIRECTOR": BUSINESS["director"],
    }
    warning_markers = ("à compléter", "00 00", "+33400000000", "+41220000000", "33600000000", "SIRET")
    warnings: list[str] = []
    for env_name, value in checks.items():
        if any(marker in str(value) for marker in warning_markers):
            warnings.append(env_name)
    return warnings


def write_production_checklist(build: BuildConfig) -> None:
    warnings = production_warnings()
    warning_lines = "\n".join(f"- {item}" for item in warnings) if warnings else "- Aucun placeholder détecté dans les champs critiques."
    write(
        operations_root(build) / "preproduction-checklist.md",
        f"""# Checklist préproduction - {build.label}

## Données à confirmer

{warning_lines}

## Vérifications avant mise en ligne

- Domaine final renseigné dans `SERRURIER_SITE_URL` ou `PLOMBIER_SITE_URL`.
- Numéros d'appel testés depuis mobile.
- WhatsApp testé avec le numéro final.
- Mentions légales complétées : forme juridique, SIRET, responsable de publication, adresse.
- Balises Google Ads / Analytics installées si nécessaires.
- Conversion de clic téléphone testée avec `.js-call-track`.
- Pages `/mentions-legales/`, `/confidentialite/`, `/robots.txt` et `/sitemap.xml` accessibles.
- Aucun fichier `google-ads/`, `seo/`, `ops/` ou `README.md` dans le dossier public `dist`.
""",
    )


def write_readme(cities: list[City], build: BuildConfig) -> None:
    if build.preserve_existing_home:
        pages_summary = f"""- L'accueil `index.html` existant est conservé.
- {len(cities)} villes issues du document Word.
- {len(build.service_keys)} métiers : {service_names(build)}.
- {len(cities)} pages hubs villes (`/lyon/`, `/geneve/`, etc.).
- {len(cities) * len(build.service_keys)} pages locales.
- Une page d'entrée technique : `campagnes-locales/index.html`."""
        generate_command = "python3 generate_site.py"
    else:
        pages_summary = f"""- `index.html` est l'accueil du site {build.label}.
- {len(cities)} villes issues du document Word.
- Services inclus : {service_names(build)}.
- Les pages du service principal sont à la racine (`/lyon/`, `/geneve/`, etc.).
- {len(cities) * len(build.service_keys)} pages locales."""
        generate_command = f"python3 generate_site.py --target {build.key}"
    ops_path = display_path(operations_root(build))

    readme_path = build.output_root / "README.md" if build.output_root == ROOT else operations_root(build) / "README.md"
    write(
        readme_path,
        f"""# Site local Solybat - {build.label}

Ce dossier contient un site statique généré pour la stratégie Google Ads et SEO local.

{pages_summary}
- `sitemap.xml` et `robots.txt`.
- Pages légales : `/mentions-legales/` et `/confidentialite/`.
- Fichiers d'exploitation Google Ads et SEO local générés dans `{ops_path}`.

## Générer le site

```bash
{generate_command}
```

## Générer les deux domaines séparés

```bash
python3 generate_site.py --target split
```

## Avant mise en ligne

Remplacer dans `generate_site.py` :

- `site_url` ou passer `--site-url` pour un build unique
- `SERRURIER_SITE_URL` et `PLOMBIER_SITE_URL` pour `--target split`
- `fr_phone_display` et `fr_phone_href`
- `ch_phone_display` et `ch_phone_href`
- `whatsapp`
- `email`
- `address`

Les numéros actuels sont des valeurs temporaires. Ne lancez pas Google Ads avant remplacement et test du suivi d'appel.
""",
    )


def build_config(target: str, output_root: Path | None = None, site_url: str | None = None) -> BuildConfig:
    if target == "full":
        resolved_output = output_root or ROOT
        preserve_existing_home = resolved_output == ROOT
        return BuildConfig(
            key="full",
            label="multi-services",
            site_url=site_url or os.environ.get("SOLYBAT_SITE_URL", BUSINESS["site_url"]),
            output_root=resolved_output,
            service_keys=tuple(SERVICES.keys()),
            primary_service_key=None,
            include_city_hubs=True,
            preserve_existing_home=preserve_existing_home,
        )
    if target == "serrurier":
        return BuildConfig(
            key="serrurier",
            label="serrurier",
            site_url=site_url or os.environ.get("SERRURIER_SITE_URL", SPLIT_DOMAIN_DEFAULTS["serrurier"]),
            output_root=output_root or ROOT / "dist" / "serrurier",
            service_keys=("serrurier",),
            primary_service_key="serrurier",
            include_city_hubs=False,
        )
    if target == "plombier":
        return BuildConfig(
            key="plombier",
            label="plombier",
            site_url=site_url or os.environ.get("PLOMBIER_SITE_URL", SPLIT_DOMAIN_DEFAULTS["plombier"]),
            output_root=output_root or ROOT / "dist" / "plombier",
            service_keys=("plombier", "degorgement"),
            primary_service_key="plombier",
            include_city_hubs=False,
        )
    raise ValueError(f"Unknown target: {target}")


def render_build(cities: list[City], build: BuildConfig) -> int:
    prepare_output(build)
    if build.preserve_existing_home:
        write(output_path_for("/campagnes-locales/", build), home_page(cities, build))
    else:
        write(output_path_for("/", build), home_page(cities, build))

    write(output_path_for("/zones/", build), zones_page(cities, build))
    write(output_path_for("/mentions-legales/", build), legal_page("mentions", build))
    write(output_path_for("/confidentialite/", build), legal_page("privacy", build))
    for city in cities:
        if build.include_city_hubs:
            write(output_path_for(city_hub_path(city), build), city_page(city, cities, build))
        for service_key in build.service_keys:
            write(output_path_for(service_path(city, service_key, build), build), service_page(city, service_key, cities, build))

    write(build.output_root / "sitemap.xml", sitemap(cities, build))
    write(
        build.output_root / "robots.txt",
        f"User-agent: *\nDisallow: /google-ads/\nSitemap: {build.site_url.rstrip('/')}/sitemap.xml\n",
    )
    write_ads_files(cities, build)
    write_seo_files(cities, build)
    write_readme(cities, build)
    write_production_checklist(build)
    return 4 + (len(cities) if build.include_city_hubs else 0) + len(cities) * len(build.service_keys)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Solybat static pages.")
    parser.add_argument(
        "--target",
        choices=("full", "serrurier", "plombier", "split"),
        default="full",
        help="full keeps the historical mixed site; split writes dist/serrurier and dist/plombier.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory for full/serrurier/plombier. With --target split, this is the parent output directory.",
    )
    parser.add_argument(
        "--site-url",
        help="Canonical domain for a single target build. For split, use SERRURIER_SITE_URL and PLOMBIER_SITE_URL.",
    )
    args = parser.parse_args()
    if args.target == "split" and args.site_url:
        parser.error("--site-url cannot be used with --target split; use SERRURIER_SITE_URL and PLOMBIER_SITE_URL.")
    return args


def main() -> None:
    args = parse_args()
    cities = load_cities()
    if args.target == "split":
        output_parent = args.output or ROOT / "dist"
        builds = [
            build_config("serrurier", output_parent / "serrurier"),
            build_config("plombier", output_parent / "plombier"),
        ]
    else:
        builds = [build_config(args.target, args.output, args.site_url)]

    for build in builds:
        page_count = render_build(cities, build)
        print(f"Generated {page_count} HTML pages for {build.label} in {display_path(build.output_root)}.")


if __name__ == "__main__":
    main()
