# Site local Solybat

Ce dépôt contient un site statique généré pour la stratégie Google Ads et SEO local :

- L'accueil `index.html` existant est conservé.
- 129 villes issues du document Word.
- 3 métiers : serrurier, plombier, dégorgement.
- 387 pages locales.
- Une page d'entrée technique : `campagnes-locales/index.html`.
- `sitemap.xml` et `robots.txt`.
- Fichiers d'exploitation Google Ads dans `google-ads/`.
- Fichiers de suivi SEO local dans `seo/`.

## Générer le site

```bash
python3 generate_site.py
```

## Avant mise en ligne

Remplacer dans `generate_site.py` :

- `site_url`
- `fr_phone_display` et `fr_phone_href`
- `ch_phone_display` et `ch_phone_href`
- `whatsapp`
- `email`
- `address`

Les numéros actuels sont des valeurs temporaires. Ne lancez pas Google Ads avant remplacement et test du suivi d'appel.
