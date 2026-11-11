from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

from flask import g, make_response, redirect, render_template, request, send_from_directory, url_for
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response

from app import app, critters, settings as island, timezones
from app.critters import KINDS, MONTH_ABBRS, MONTH_NAMES, format_hour
from app.types import CritterKind, CritterStatus, IslandSettings

CANONICAL_ORIGIN = "https://critter-catcher.vercel.app"

for _kind in CritterKind:
    critters.catalog(_kind)

_asset_versions: dict[str, str] = {}


def asset_url(filename: str) -> str:
    version = _asset_versions.get(filename)
    if version is None or app.debug:
        path = Path(app.static_folder or "static") / filename
        version = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        _asset_versions[filename] = version
    return url_for("static", filename=filename, v=version)


def nav_url(endpoint: str, **params: str) -> str:
    settings: IslandSettings | None = g.get("settings")
    values: dict[str, Any] = {**(island.query_params(settings) if settings else {}), **params}
    return url_for(endpoint, **values)


def sky_phase(hour: int) -> str:
    if 5 <= hour < 7:
        return "dawn"
    if 7 <= hour < 17:
        return "day"
    if 17 <= hour < 20:
        return "dusk"
    return "night"


app.jinja_env.globals.update(
    kinds=tuple(KINDS.values()),
    kind_lookup=KINDS,
    month_abbrs=MONTH_ABBRS,
    month_names=MONTH_NAMES,
    format_hour=format_hour,
    clock_time=timezones.clock_time,
    clock_date=timezones.clock_date,
    asset_url=asset_url,
    nav_url=nav_url,
)


@app.context_processor
def template_context() -> dict[str, object]:
    return {"canonical_url": CANONICAL_ORIGIN + request.path}


def _settings() -> IslandSettings:
    settings = island.resolve(request)
    g.settings = settings
    return settings


def _page(template: str, settings: IslandSettings, **context: object) -> Response:
    response = make_response(render_template(
        template,
        settings=settings,
        timezone_groups=timezones.options(settings.timezone),
        **context,
    ))
    island.persist(response, settings)
    return response


@app.route("/")
@app.route("/index")
def index() -> Response:
    settings = _settings()
    summaries = tuple(critters.summarize(kind, critters.statuses(kind, settings)) for kind in CritterKind)

    def by_price(items: list[CritterStatus]) -> list[CritterStatus]:
        return sorted(items, key=lambda item: -item.critter.price)

    return _page(
        "index.html",
        settings,
        summaries=summaries,
        leaving=by_price([item for summary in summaries for item in summary.leaving]),
        new=by_price([item for summary in summaries for item in summary.new]),
        phase=sky_phase(settings.hour),
    )


def _critter_page(kind: CritterKind) -> Response:
    info = KINDS[kind]
    if request.method == "POST":
        legacy: dict[str, Any] = {key: value for key in ("hemisphere", "timezone") if (value := request.form.get(key))}
        return redirect(url_for(info.endpoint, **legacy), code=303)
    settings = _settings()
    statuses = critters.statuses(kind, settings)
    return _page("critters.html", settings, info=info, statuses=statuses,
                 summary=critters.summarize(kind, statuses))


@app.route("/fish", methods=["GET", "POST"])
def fish() -> Response:
    return _critter_page(CritterKind.FISH)


@app.route("/bugs", methods=["GET", "POST"])
def bugs() -> Response:
    return _critter_page(CritterKind.BUGS)


@app.route("/sea_creatures", methods=["GET", "POST"])
def sea_creatures() -> Response:
    return _critter_page(CritterKind.SEA_CREATURES)


@app.route('/favicon.ico')
def favicon() -> Response:
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/apple-touch-icon.png')
def apple_touch_icon() -> Response:
    return send_from_directory(os.path.join(app.root_path, 'static'), 'apple-touch-icon.png')


@app.route('/android-icon-192x192.png')
def android_icon() -> Response:
    return send_from_directory(os.path.join(app.root_path, 'static'), 'android-icon-192x192.png')


@app.errorhandler(404)
def not_found(error: HTTPException) -> tuple[str, int]:
    settings = _settings()
    return render_template("error.html", settings=settings, timezone_groups=(), code=404), 404


@app.errorhandler(500)
def server_error(error: Exception) -> tuple[str, int]:
    return render_template("error.html", settings=None, timezone_groups=(), code=500), 500


@app.after_request
def add_headers(response: Response) -> Response:
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    if request.endpoint == "static" and request.args.get("v"):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return response
