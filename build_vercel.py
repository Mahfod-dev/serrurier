#!/usr/bin/env python3
"""Point d'entrée du build Vercel.

Les deux sites (Serrio, Plombio) vivent dans le même dépôt et partagent la même
commande de build. Seule la variable d'environnement SITE_TARGET change d'un
projet Vercel à l'autre :

    SITE_TARGET=serrurier  -> Serrio   (serrurerie)
    SITE_TARGET=plombier   -> Plombio  (plomberie + dégorgement)

Le résultat est toujours écrit dans `public/`, qui est le répertoire de sortie
configuré côté Vercel. Les fichiers internes (ops/, seo/, google-ads/) sont
générés hors de `public/` et ne sont donc jamais publiés.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "public"
TARGETS = ("serrurier", "plombier")


def main() -> int:
    target = os.environ.get("SITE_TARGET", "").strip()
    if target not in TARGETS:
        print(
            f"SITE_TARGET doit valoir {' ou '.join(TARGETS)} (reçu : {target!r}).\n"
            "Définissez-la dans les variables d'environnement du projet Vercel.",
            file=sys.stderr,
        )
        return 1

    result = subprocess.run(
        [sys.executable, "generate_site.py", "--target", target, "--output", str(OUTPUT)],
        cwd=ROOT,
    )
    if result.returncode != 0:
        return result.returncode

    pages = len(list(OUTPUT.rglob("index.html")))
    print(f"Build {target} terminé : {pages} pages dans public/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
