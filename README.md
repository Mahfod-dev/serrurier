# Site local Solybat

Ce dépôt contient un site statique généré pour la stratégie Google Ads et SEO local :

- L'accueil `index.html` existant est conservé.
- 129 villes issues du document Word.
- 3 métiers : serrurier, plombier, dégorgement.
- 129 pages hubs villes (`/lyon/`, `/geneve/`, etc.).
- 387 pages locales.
- Une page d'entrée technique : `campagnes-locales/index.html`.
- `sitemap.xml` et `robots.txt`.
- Fichiers d'exploitation Google Ads dans `google-ads/`.
- Fichiers de suivi SEO local dans `seo/`.

## Générer le site

```bash
python3 generate_site.py
```

## Générer deux sites séparés

```bash
python3 generate_site.py --target split
```

Cette commande crée :

- `dist/serrurier/` : site serrurier seul, avec les pages ville à la racine (`/lyon/`, `/geneve/`, etc.).
- `dist/plombier/` : site plombier, avec les pages plomberie à la racine et le dégorgement sous `/degorgement/`.

Chaque dossier contient son propre `index.html`, `sitemap.xml`, `robots.txt`, `google-ads/` et `seo/`. Pour renseigner les futurs domaines avant génération :

```bash
SERRURIER_SITE_URL="https://www.domaine-serrurier.fr" \
PLOMBIER_SITE_URL="https://www.domaine-plombier.fr" \
python3 generate_site.py --target split
```

## Avant mise en ligne

Remplacer dans `generate_site.py` :

- `site_url`
- `SERRURIER_SITE_URL` et `PLOMBIER_SITE_URL` si les deux domaines sont générés ensemble
- `fr_phone_display` et `fr_phone_href`
- `ch_phone_display` et `ch_phone_href`
- `whatsapp`
- `email`
- `address`

Les numéros actuels sont des valeurs temporaires. Ne lancez pas Google Ads avant remplacement et test du suivi d'appel.
