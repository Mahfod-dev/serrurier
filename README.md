# Site local Solybat - multi-services

Ce dossier contient un site statique généré pour la stratégie Google Ads et SEO local.

- L'accueil `index.html` existant est conservé.
- 129 villes issues du document Word.
- 3 métiers : serrurerie, plomberie et dégorgement.
- 129 pages hubs villes (`/lyon/`, `/geneve/`, etc.).
- 387 pages locales.
- Une page d'entrée technique : `campagnes-locales/index.html`.
- `sitemap.xml` et `robots.txt`.
- Pages légales : `/mentions-legales/` et `/confidentialite/`.
- Fichiers d'exploitation Google Ads et SEO local générés dans `.`.

## Générer le site

```bash
python3 generate_site.py
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
