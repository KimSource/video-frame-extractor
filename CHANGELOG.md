## [0.1.0]

### Added

- Add input validation before extraction.
- Add local or system PATH FFmpeg selection.
- Add asynchronous extraction status and cancellation.
- Add automated tests for frame selection, validation, and FFmpeg command generation.

### Changed

- Use `subprocess` arguments instead of shell command strings to run FFmpeg.
- Use `-fps_mode passthrough` instead of deprecated numeric `-vsync`.
- Explicitly use the `libwebp` encoder so selected WebP frames are written as separate files.
- Update Tk variable tracing for Tk 9 compatibility.
- Add Python 3.14 and PyInstaller build setup.

### Fixed

- Fix extraction failures for paths containing spaces.
- Fix bundled resource and adjacent FFmpeg lookup when the working directory differs.
- Fix multiple WebP frame extraction producing a single animated WebP file.

## [0.0.4]

### Added

- Add WebP option to output file type

## [0.0.3]

### Added

- Add option to use old frame extraction method
- Add links to release tags in changelog

## [0.0.2]

### Added

- Add changelog

### Fixed

- Fix malfunction of specific frames method

## [0.0.1]

### Added

- Initial Release
- Add readme

[0.0.4]: https://github.com/KimSource/video-frame-extractor/releases/tag/v0.0.4
[0.1.0]: https://github.com/KimSource/video-frame-extractor/releases/tag/v0.1.0
[0.0.3]: https://github.com/KimSource/video-frame-extractor/releases/tag/v0.0.3
[0.0.2]: https://github.com/KimSource/video-frame-extractor/releases/tag/v0.0.2
[0.0.1]: https://github.com/KimSource/video-frame-extractor/releases/tag/v0.0.1
