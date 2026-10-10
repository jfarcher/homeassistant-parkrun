# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

When you cut a release, move items from **Unreleased** into a new section whose
heading version matches `custom_components/parkrun/manifest.json` exactly, then
bump that file. The release workflow publishes that section as the GitHub
release notes.

## [Unreleased]

## [0.2.0] - 2026-10-10

### Fixed

- Personal best is now the fastest 5k time. Junior 2k results no longer overwrite it when someone moves up to senior parkrun.

### Added

- Junior personal best sensor for 2k history.

## [0.1.0] - 2026-09-20

### Added

- Initial parkrun integration: public athlete results as Home Assistant sensors.
- Config flow using athlete ID and country website (no password).
- Brand images and HACS install link.
- GitHub release workflow driven by the manifest version.

### Changed

- Finish times display as minutes and seconds (for example `23:48`) instead of raw seconds.
