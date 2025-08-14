# app/tools/diagnose.py
"""
Full scan:
- Modül import taraması (döngüsel import/ImportError)
- FastAPI route envanteri + duman testi (500 yakala)
- Pydantic response validation hataları yakalanır
- Jinja template parse: tanımsız variable'lar
- Güvenlik/lint özet komutları (ruff/mypy kancası)
"""
from __future__ import annotations
import os, sys, pkgutil, importlib, traceback, json, re
from typing import List, Tuple
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # repo root
APP_PKG = "app"
TEMPLATES_DIR = PROJECT_ROOT / "app" / "templates"

def header(t: str):
    print("\n" + "="*80)
    print(t)
    print("="*80)

def import_sweep(package: str) -> List[Tuple[str, str]]:
    """Import all modules under `package`. Return list of (module, error)."""
    errors = []
    pkg = importlib.import_module(package)
    for m in pkgutil.walk_packages(pkg.__path__, prefix=pkg.__name__ + "."):
        name = m.name
        try:
            importlib.import_module(name)
        except Exception as e:
            tb = traceback.format_exc(limit=4)
            errors.append((name, tb))
    return errors

def fastapi_smoke():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    bad = []
    # Sadece GET ve birkaç tipik POST uç noktası
    paths = []
    for r in app.routes:
        methods = getattr(r, "methods", set())
        if "GET" in methods:
            paths.append(("GET", r.path))
    # Duman testini çalıştır
    for method, path in paths:
        # UI sayfaları için query ekleyelim (feed boş argümanla da çalışmalı)
        url = path
        try:
            resp = client.request(method, url, timeout=10)
            if resp.status_code >= 500:
                bad.append((method, url, resp.status_code, resp.text[:300]))
        except Exception as e:
            bad.append((method, url, "EXC", str(e)))
    return bad

def jinja_parse_undeclared():
    from jinja2 import Environment, FileSystemLoader, meta
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    problems = []
    for p in TEMPLATES_DIR.rglob("*.html"):
        src = p.read_text(encoding="utf-8")
        ast = env.parse(src)
        vars_ = meta.find_undeclared_variables(ast)
        # Bazı global'leri whitelist edebiliriz
        whitelist = {"request", "url_for", "gettext", "_"}
        undeclared = sorted(v for v in vars_ if v not in whitelist)
        if undeclared:
            problems.append((str(p.relative_to(TEMPLATES_DIR)), undeclared))
    return problems

def main():
    os.chdir(PROJECT_ROOT)

    header("1) Ruff / Mypy (hızlı statik kontrol)")
    os.system("ruff check app || true")
    os.system("mypy app || true")

    header("2) Import taraması")
    errs = import_sweep(APP_PKG)
    if errs:
        for name, tb in errs:
            print(f"[IMPORT ERROR] {name}\n{tb}")
    else:
        print("✓ Tüm modüller import ediliyor (döngüsel import/ImportError yok).")

    header("3) FastAPI duman testi (500 arıyoruz)")
    bad = fastapi_smoke()
    if bad:
        for method, path, code, snippet in bad:
            print(f"[{code}] {method} {path}\n{snippet}\n")
    else:
        print("✓ Duman testinde 500 yok.")

    header("4) Jinja undeclared variable’lar")
    jissues = jinja_parse_undeclared()
    if jissues:
        for tpl, vars_ in jissues:
            print(f"[JINJA] {tpl}: {', '.join(vars_)}")
    else:
        print("✓ Template’lerde belirgin undeclared yok.")

    header("5) Güvenlik hızlı tarama")
    os.system("bandit -q -r app || true")

    header("6) Özet & Çıkış kodu")
    if errs or bad:
        print("✗ Problemler var (yukarıya bak).")
        sys.exit(1)
    print("✓ Büyük hata görünmedi.")
    sys.exit(0)

if __name__ == "__main__":
    main()
