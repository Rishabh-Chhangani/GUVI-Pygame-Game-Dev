# CI/CD Pipeline Recovery Guide

This document outlines common failures that can occur in the Ninja Collector automated pipeline and how to resolve them.

## 1. Pytest Failure (build-and-test job)
**Symptom:** The pipeline fails on the "Run Tests and Generate Coverage" step.
**Cause:** A code change broke existing game logic.
**Recovery:**
1. Click into the failed GitHub Action run and download the `coverage-reports` artifact (or read the terminal output).
2. Open `junit.xml` or look at the pytest terminal output to identify the exact failing test.
3. Fix the logic locally, run `.\run_coverage.bat` to verify it passes, and commit the fix.

## 2. Ruff Linting Failure
**Symptom:** The pipeline fails on the "Lint with Ruff" step.
**Cause:** Code style violation or syntax error.
**Recovery:**
1. Run `ruff check .` locally to see the errors.
2. Run `ruff check --fix .` to automatically fix most formatting issues.
3. Commit and push the fixed code.

## 3. Pip-Audit Security Failure
**Symptom:** The pipeline fails on the "Run pip-audit" step.
**Cause:** A known vulnerability was found in one of the dependencies in `requirements.txt`.
**Recovery:**
1. Check the action logs to identify the vulnerable package.
2. Update the version number of that package in `requirements.txt` to a patched version.
3. Commit and push the updated `requirements.txt`.

## 4. PyInstaller Build Failure
**Symptom:** The `build-windows` or `build-and-release` job fails on the PyInstaller step.
**Cause:** Usually a missing asset file, a syntax error that wasn't caught by tests, or a bad path reference.
**Recovery:**
1. Verify that all assets are correctly referenced and exist in the `assets/` folder.
2. Ensure you haven't introduced any complex Python modules that PyInstaller cannot trace.
3. Run `pyinstaller --noconfirm --onedir --windowed --add-data "assets;assets" --name "NinjaCollector" main.py` locally on your Windows machine to debug the build process.

## 5. Release Checksum Generation Failure
**Symptom:** The release workflow fails on the "Generate Checksum" step.
**Cause:** PowerShell couldn't find the `.zip` file, likely because the archiving step failed silently.
**Recovery:**
1. Check the logs for the previous "Zip the Build" step.
2. Ensure that `dist/NinjaCollector/` was actually created by PyInstaller.
