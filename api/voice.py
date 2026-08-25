"""Ligne téléphonique suivie : annonce légale, transfert, enregistrement.

Le numéro affiché sur le site n'est plus celui de l'artisan mais un numéro
Twilio. Twilio appelle cette fonction à chaque appel entrant ; elle répond en
TwiML : une phrase d'information, puis le transfert vers le mobile réel, avec
enregistrement des deux voix.

Pourquoi ici plutôt que dans le back-office Flowcontent : les 24 numéros
français de ce compte pointent tous vers le même webhook, celui qui sert
l'agent vocal des clients. Y ajouter un mode « transfert simple » ferait porter
à ces lignes le risque d'une régression qui ne les concerne pas. Cette
fonction vit à côté du site qu'elle dessert, se déploie avec lui, et n'est
appelée que par le seul numéro qu'on lui affecte.

Configuration (variables d'environnement du projet Vercel) :

    VOICE_FORWARD_TO      +33785040248   le mobile qui doit sonner
    VOICE_NOTICE          phrase d'annonce ; un défaut est prévu
    VOICE_TIMEOUT         25             sonneries avant abandon, en secondes
    TWILIO_AUTH_TOKEN     vérifie la signature des requêtes (optionnel)

⚠️ L'annonce n'est pas décorative. Enregistrer un appel sans en informer
l'appelant est illicite en France ; la phrase doit rester en tête du flux,
avant le décroché du destinataire.

Sans VOICE_FORWARD_TO, la fonction répond une excuse parlée plutôt qu'un
silence : un appelant en urgence doit comprendre qu'il doit rappeler, pas
tomber sur une ligne muette.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

DEFAULT_NOTICE = (
    "Bonjour, votre appel peut être enregistré à des fins de suivi "
    "et d'amélioration du service. Nous vous mettons en relation."
)
MAX_BODY = 16_000


def _escape(text: str) -> str:
    """Échappe le XML. Le nom de l'appelant peut arriver dans l'annonce."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _signature_ok(url: str, params: dict[str, list[str]], received: str) -> bool:
    """Signature Twilio : HMAC-SHA1 de l'URL suivie des champs POST triés.

    Absente de la configuration, la vérification est ignorée : mieux vaut une
    ligne qui sonne sans contrôle qu'une ligne d'urgence muette parce qu'un
    secret manque. Le pire cas d'un appel forgé est un transfert facturé.
    """
    token = os.environ.get("TWILIO_AUTH_TOKEN", "").strip()
    if not token:
        return True
    if not received:
        return False
    payload = url + "".join(
        f"{key}{values[0]}" for key, values in sorted(params.items()) if values
    )
    expected = base64.b64encode(
        hmac.new(token.encode(), payload.encode("utf-8"), hashlib.sha1).digest()
    ).decode()
    return hmac.compare_digest(expected, received)


class handler(BaseHTTPRequestHandler):
    def _twiml(self, body: str, status: int = 200) -> None:
        payload = f'<?xml version="1.0" encoding="UTF-8"?>\n<Response>{body}</Response>'.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/xml; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _say(self, text: str) -> str:
        return f'<Say language="fr-FR" voice="Polly.Lea">{_escape(text)}</Say>'

    def do_POST(self) -> None:  # noqa: N802 - imposé par BaseHTTPRequestHandler
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        raw = self.rfile.read(length).decode("utf-8", "replace") if 0 < length <= MAX_BODY else ""
        params = parse_qs(raw, keep_blank_values=True)

        # Twilio signe l'URL exacte qu'il a appelée, protocole compris.
        host = self.headers.get("X-Forwarded-Host") or self.headers.get("Host", "")
        proto = self.headers.get("X-Forwarded-Proto", "https")
        url = f"{proto}://{host}{self.path}"
        if not _signature_ok(url, params, self.headers.get("X-Twilio-Signature", "")):
            self._twiml(self._say("Appel non autorisé."), status=403)
            return

        forward_to = os.environ.get("VOICE_FORWARD_TO", "").strip()
        if not forward_to:
            self._twiml(
                self._say(
                    "Notre ligne est momentanément indisponible. "
                    "Merci de rappeler dans quelques instants."
                )
            )
            return

        notice = os.environ.get("VOICE_NOTICE", "").strip() or DEFAULT_NOTICE
        try:
            timeout = max(10, min(60, int(os.environ.get("VOICE_TIMEOUT", "25"))))
        except ValueError:
            timeout = 25

        # `record-from-answer-dual` : deux pistes séparées, appelant et artisan.
        # L'enregistrement ne démarre qu'au décroché — les sonneries dans le
        # vide ne sont ni enregistrées ni facturées au stockage.
        callback = f"{proto}://{host}/api/voice-recording"
        # L'artisan voit sonner le numéro du site, pas celui de l'appelant :
        # il sait ainsi d'où vient l'appel avant de décrocher. Twilio n'accepte
        # en `callerId` qu'un numéro du compte, d'où le `To` de la requête ;
        # absent, on omet l'attribut plutôt que d'en envoyer un vide.
        appele = (params.get("To") or [""])[0].strip()
        caller_id = f' callerId="{_escape(appele)}"' if appele else ""
        dial = (
            f'<Dial timeout="{timeout}"{caller_id}'
            f' record="record-from-answer-dual"'
            f' recordingStatusCallback="{_escape(callback)}"'
            f' recordingStatusCallbackEvent="completed">'
            f"{_escape(forward_to)}</Dial>"
        )
        # Si le transfert échoue ou n'est pas décroché, le flux continue ici :
        # sans ce message, l'appelant entend un silence puis un raccrochage sec.
        fallback = self._say(
            "Nous n'avons pas pu vous mettre en relation. "
            "Merci de renouveler votre appel."
        )
        self._twiml(self._say(notice) + dial + fallback)

    def do_GET(self) -> None:  # noqa: N802
        """Sonde de configuration — ne révèle jamais le numéro de destination."""
        configured = bool(os.environ.get("VOICE_FORWARD_TO", "").strip())
        signed = bool(os.environ.get("TWILIO_AUTH_TOKEN", "").strip())
        body = f'{{"ok": true, "configured": {str(configured).lower()}, "signature_checked": {str(signed).lower()}}}'.encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
