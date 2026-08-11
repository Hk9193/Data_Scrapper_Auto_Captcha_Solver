"""
cleanup.py — Remove / auto-clear unwanted cache and unused files.

WHAT IT DELETES (all regenerate automatically and are NOT needed for scraping):
  * Browser-profile caches, e.g. browser_profile/<Default|top>/:
      Cache, Code Cache, GPUCache, DawnWebGPUCache, DawnGraphiteCache,
      GrShaderCache, ShaderCache, Shared Dictionary, Sessions,
      JumpListIconsRecentClosed, Crashpad, component_crx_cache,
      extensions_crx_cache, segmentation_platform, Safe Browsing.
  * Stray fallback profiles (browser_profile_<timestamp>/) left behind by
    scraper._launch_context() when the main profile was temporarily locked.
  * Python bytecode caches (__pycache__ dirs and *.pyc files).
  * Leftover temporary audio-CAPTCHA files (audio_tmp/).

WHAT IS PRESERVED (essential persistent session state):
  Cookies, Local Storage, Session Storage, WebStorage, Preferences,
  Login Data (stored accounts), History, and other non-cache profile files —
  deleting these would log you out / break the persistent session.
"""

from __future__ import annotations

import logging
import os
import shutil

logger = logging.getLogger("scraper.cleanup")

# Directories that are pure caches, safe + regenerable to delete.
# Each name is looked up under the profile root AND under Default/.
CACHE_DIR_NAMES = {
    "Cache",
    "Code Cache",
    "GPUCache",
    "DawnWebGPUCache",
    "DawnGraphiteCache",
    "GrShaderCache",
    "ShaderCache",
    "Shared Dictionary",
    "Sessions",
    "JumpListIconsRecentClosed",
    "Crashpad",
    "component_crx_cache",
    "extensions_crx_cache",
    "segmentation_platform",
    "Safe Browsing",
}
# Only auto-clean browser caches once they exceed this size (MB).
CACHE_CLEAN_THRESHOLD_MB = 50.0

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def _dir_size_mb(path: str) -> float:
    total = 0
    for dirpath, _dirnames, filenames in os.walk(path):
        for fn in filenames:
            try:
                total += os.path.getsize(os.path.join(dirpath, fn))
            except OSError:
                pass
    return total / (1024 * 1024)


def _rmtree(path: str, label: str) -> float:
    """Best-effort delete of *path*. Returns freed MB (approx)."""
    if not os.path.isdir(path):
        return 0.0
    freed = _dir_size_mb(path)
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Could not fully remove %s: %s", label, exc)
    if not os.path.isdir(path):
        logger.debug("Removed %s (%.1f MB)", label, freed)
        return freed
    logger.warning("Partial removal of %s (%.1f MB)", label, freed)
    return freed


def _remove_files_with_ext(root: str, exts: tuple) -> float:
    freed = 0.0
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(exts):
                fp = os.path.join(dirpath, fn)
                try:
                    sz = os.path.getsize(fp)
                    os.remove(fp)
                    freed += sz / (1024 * 1024)
                except OSError:
                    pass
    return freed


def cleanup_browser_cache(profile_dir: str | None = None,
                          threshold_mb: float = CACHE_CLEAN_THRESHOLD_MB) -> float:
    """Delete regenerable cache dirs inside a browser profile.

    Session/login state (cookies, Local Storage, Preferences, Login Data) is
    left untouched. Returns MB freed.
    """
    profile_dir = profile_dir or os.path.join(PROJECT_ROOT, "browser_profile")
    if not os.path.isdir(profile_dir):
        return 0.0

    default_dir = os.path.join(profile_dir, "Default")
    root_total_mb = 0.0
    for root in (profile_dir, default_dir):
        if not os.path.isdir(root):
            continue
        for entry in os.listdir(root):
            candidate = os.path.join(root, entry)
            if os.path.isdir(candidate) and entry in CACHE_DIR_NAMES:
                root_total_mb += _dir_size_mb(candidate)

    if root_total_mb < threshold_mb:
        logger.info("Browser cache below %.0f MB (%.1f MB) — skipping cleanup.",
                    threshold_mb, root_total_mb)
        return 0.0

    freed = 0.0
    for root in (profile_dir, default_dir):
        if not os.path.isdir(root):
            continue
        for entry in os.listdir(root):
            candidate = os.path.join(root, entry)
            if not os.path.isdir(candidate):
                continue
            if entry in CACHE_DIR_NAMES:
                freed += _rmtree(candidate, f"cache '{candidate}'")

    freed += _remove_files_with_ext(profile_dir, (".tmp",))

    logger.info("Browser cache cleaned (%.1f MB freed).", freed)
    return freed


def cleanup_stray_profiles(project_root: str | None = None) -> float:
    """Remove leftover browser_profile_<timestamp>/ fallback directories."""
    project_root = project_root or PROJECT_ROOT
    freed = 0.0
    for entry in os.listdir(project_root):
        if not entry.startswith("browser_profile_"):
            continue
        path = os.path.join(project_root, entry)
        if os.path.isdir(path):
            freed += _rmtree(path, f"stray profile '{entry}'")
    if freed:
        logger.info("Removed stray fallback profiles (%.1f MB).", freed)
    return freed


    return freed
def cleanup_pycache(project_root: str | None = None) -> float:
    """Remove __pycache__ dirs and *.pyc under the project (excluding venv)."""
    project_root = project_root or PROJECT_ROOT
    skips = {"venv", ".git", "node_modules", "browser_profile"}
    removed_dirs = 0
    for dirpath, dirnames, _filenames in os.walk(project_root):
        dirnames[:] = [d for d in dirnames if d not in skips]
        if "__pycache__" in dirnames:
            target = os.path.join(dirpath, "__pycache__")
            _rmtree(target, f"pycache '{target}'")
            removed_dirs += 1

    # Also remove stray .pyc files directly in source dirs.
    freed = 0.0
    for dirpath, dirnames, filenames in os.walk(project_root):
        dirnames[:] = [d for d in dirnames if d not in skips]
        for fn in filenames:
            if fn.endswith(".pyc"):
                fp = os.path.join(dirpath, fn)
                try:
                    freed += os.path.getsize(fp) / (1024 * 1024)
                    os.remove(fp)
                except OSError:
                    pass
    if removed_dirs:
        logger.info("Removed %d __pycache__ dir(s) (%.2f MB pyc files).",
                    removed_dirs, freed)
    return freed


def cleanup_audio_tmp(project_root: str | None = None) -> float:
    """Clear the scoped temporary dir used by the audio CAPTCHA solver."""
    tmp_dir = os.path.join(project_root or PROJECT_ROOT, "audio_tmp")
    if os.path.isdir(tmp_dir):
        freed = 0.0
        for fn in os.listdir(tmp_dir):
            fp = os.path.join(tmp_dir, fn)
            try:
                if os.path.isfile(fp):
                    freed += os.path.getsize(fp) / (1024 * 1024)
                    os.remove(fp)
            except OSError:
                pass
        logger.info("Cleaned audio temp dir (%.2f MB).", freed)
        return freed
    return 0.0


def cleanup_all(profile_dir: str | None = None) -> float:
    """Run every cleanup pass. Returns total MB freed."""
    total = 0.0
    try:
        total += cleanup_browser_cache(profile_dir)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Browser-cache cleanup failed: %s", exc)
    try:
        total += cleanup_stray_profiles()
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Stray-profile cleanup failed: %s", exc)
    try:
        total += cleanup_pycache()
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Pycache cleanup failed: %s", exc)
    logger.info("Cleanup complete (%.1f MB freed total).", total)
    return total


if __name__ == "__main__":
    import sys

    from logger_setup import setup_logger

    setup_logger("scraper")
    freed = cleanup_all()
    print(f"\nTotal freed: {freed:.1f} MB")
    sys.exit(0)