# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

When you cut a release, move items from **Unreleased** into a new section whose
heading version matches `custom_components/parkrun/manifest.json` exactly, then
bump that file. The release workflow publishes that section as the GitHub
release notes.

## [0.2.5] - 2026-11-23

### Fixed

- "Latest run was a PB" now means an overall PB. It was using parkrun's PB flag, which is per course, so a course PB slower than the athlete's best elsewhere showed as a PB.

## [0.2.4] - 2026-11-23

### Fixed

- Diagnostics downloads no longer include the athlete's name, athlete ID or profile URL, so they are safe to attach to public issues.

## [0.2.3] - 2026-11-22

### Added

- Junior parkrun milestone sensors: next junior milestone (with its wristband colour as an attribute) and how many junior parkruns or volunteer credits to go.

### Changed

- Integration manifest lists the `health_wellbeing` category.

### Fixed

- Run and volunteer milestones now match parkrun's milestone clubs (25, 50, 100, 200, 250, 300, 400, 500, then every 100 to 1000), plus 10 / v10 for under 18s.

## [0.2.1] - 2026-11-05

### Fixed

- Integration manifest now includes `issue_tracker`, `codeowners`, and a `documentation` link to this repository, so the release passes HACS validation.
- Added an MIT license.

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
