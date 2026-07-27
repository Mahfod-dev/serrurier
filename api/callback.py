"""Réception des demandes de rappel du formulaire, envoi par e-mail.

Le formulaire n'avait aucun backend : il ouvrait WhatsApp, et la demande était
perdue dès que WhatsApp manquait. Cette fonction reçoit le POST et envoie la
demande à la boîte de contact de la marque, par le SMTP OVH du domaine.

Configuration attendue (variables d'environnement du projet Vercel) :

    SMTP_HOST       ssl0.ovh.net          (défaut)
    SMTP_PORT       465                   (défaut, SSL implicite)
    SMTP_USER       contact@serrio.fr     l'adresse complète sert d'identifiant
    SMTP_PASSWORD   le mot de passe de cette boîte
    SMTP_TO         destinataire ; à défaut, SMTP_USER

Tant que SMTP_USER ou SMTP_PASSWORD manquent, la fonction répond 503 sans rien
tenter : le formulaire retombe alors sur WhatsApp. Rien à désactiver pour
déployer avant d'avoir posé les secrets.
"""

from __future__ import annotations

import json
import os
import re
import smtplib
import unicodedata
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler

MAX_BODY = 8_000
FIELD_LIMITS = {"name": 80, "phone": 40, "need": 1500, "city": 80, "service": 80, "page": 300}
PHONE_RE = re.compile(r"^[+0-9 ().\-/]{6,40}$")


def _clean(value: object, limit: int) -> str:
    """Aplatit une valeur reçue : pas de retour chariot, longueur bornée.

    Les sauts de ligne sont retirés des champs courts pour qu'on ne puisse pas
    fabriquer d'en-têtes supplémentaires via le sujet.
    """
    text = value if isinstance(value, str) else ""
    text = unicodedata.normalize("NFC", text).strip()
    return text[:limit]


def _single_line(value: str) -> str:
    return re.sub(r"[\r\n\t]+", " ", value).strip()


class handler(BaseHTTPRequestHandler):
    def _reply(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802 - imposé par BaseHTTPRequestHandler
        user = os.environ.get("SMTP_USER", "").strip()
        password = os.environ.get("SMTP_PASSWORD", "")
        if not user or not password:
            # Pas encore configuré : le front basculera sur WhatsApp.
            self._reply(503, {"ok": False, "reason": "smtp_not_configured"})
            return

        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            self._reply(400, {"ok": False, "reason": "bad_length"})
            return

        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError
        except (ValueError, UnicodeDecodeError):
            self._reply(400, {"ok": False, "reason": "bad_json"})
            return

        fields = {key: _clean(data.get(key), limit) for key, limit in FIELD_LIMITS.items()}
        name = _single_line(fields["name"])
        phone = _single_line(fields["phone"])
        if not name or not PHONE_RE.match(phone):
            self._reply(422, {"ok": False, "reason": "invalid_fields"})
            return

        # Champ leurre : rempli uniquement par un robot qui remplit tout.
        if _clean(data.get("company"), 80):
            self._reply(200, {"ok": True})
            return

        city = _single_line(fields["city"])
        service = _single_line(fields["service"]) or "intervention"
        subject = f"Demande de rappel — {service}" + (f" à {city}" if city else "")

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = user
        message["To"] = os.environ.get("SMTP_TO", "").strip() or user
        message["Reply-To"] = user
        message.set_content(
            "Nouvelle demande de rappel depuis le site.\n\n"
            f"Prénom    : {name}\n"
            f"Téléphone : {phone}\n"
            f"Service   : {service}\n"
            f"Ville     : {city or '—'}\n"
            f"Page      : {_single_line(fields['page']) or '—'}\n\n"
            f"Besoin :\n{fields['need'] or '—'}\n"
        )

        host = os.environ.get("SMTP_HOST", "ssl0.ovh.net").strip()
        try:
            port = int(os.environ.get("SMTP_PORT", "465"))
        except ValueError:
            port = 465

        try:
            if port == 465:
                server = smtplib.SMTP_SSL(host, port, timeout=12)
            else:
                server = smtplib.SMTP(host, port, timeout=12)
                server.starttls()
            with server:
                server.login(user, password)
                server.send_message(message)
        except (smtplib.SMTPException, OSError):
            # Aucun détail renvoyé au client : le front repasse sur WhatsApp.
            self._reply(502, {"ok": False, "reason": "send_failed"})
            return

        self._reply(200, {"ok": True})

    def do_GET(self) -> None:  # noqa: N802
        configured = bool(os.environ.get("SMTP_USER") and os.environ.get("SMTP_PASSWORD"))
        self._reply(200, {"ok": True, "configured": configured})
