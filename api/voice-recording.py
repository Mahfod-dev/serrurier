"""Réception des enregistrements d'appel : trace, et rien de plus.

Twilio appelle cette fonction quand un enregistrement est prêt. Elle ne
télécharge rien et ne stocke rien : l'audio reste chez Twilio, où il s'écoute
depuis la console (Monitor → Logs → Calls). Ce point d'entrée existe pour que
l'URL déclarée dans le TwiML réponde 200 — sans quoi Twilio la réessaie en
boucle — et pour laisser une trace lisible dans les journaux Vercel.

Le jour où ces appels devront remonter dans Flowcontent, c'est ici qu'on
posera l'appel à l'API, pas dans le TwiML.

⚠️ Ne jamais écrire l'URL de l'enregistrement en clair ailleurs que dans les
journaux : elle donne accès à l'audio d'une conversation privée.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

MAX_BODY = 16_000


class handler(BaseHTTPRequestHandler):
    def _ok(self) -> None:
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802 - imposé par BaseHTTPRequestHandler
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        raw = self.rfile.read(length).decode("utf-8", "replace") if 0 < length <= MAX_BODY else ""
        fields = parse_qs(raw, keep_blank_values=True)

        def first(key: str) -> str:
            return (fields.get(key) or [""])[0]

        # Durée et identifiant suffisent à retrouver l'appel dans la console.
        print(
            "[voice] enregistrement prêt "
            f"call={first('CallSid')} recording={first('RecordingSid')} "
            f"duree={first('RecordingDuration')}s statut={first('RecordingStatus')}"
        )
        self._ok()

    def do_GET(self) -> None:  # noqa: N802
        self._ok()
