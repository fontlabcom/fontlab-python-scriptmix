# Release 1.0.0 — 31 October 2026

## Distribution

`python3 tools/build_release.py` produces:

- `HT-Letterspacer-FontLab-1.0.0.zip`: customer download. Unzip and double-click the installer.
- `Install-HT-Letterspacer-1.0.0.vfpy`: standalone native FontLab installer, suitable for a direct download.
- `HT-Letterspacer-FontLab-1.0.0-source.zip`: complete gateway source, tests, documentation, installer and build scripts.
- `SHA256SUMS.txt`: artifact checksums.

Both installer forms are independent of the checkout and download location. The standalone installer contains the runtime plus a full corresponding-source ZIP. Original upstream source is downloaded at installation, kept unchanged in a private vendor folder, and retained as the complete GitHub archive with its licenses. No compiled or unsigned executable launcher is required; `.vfpy` is FontLab's own script file type.

The installer performs the requested install immediately after the file is opened in FontLab. Platform file associations may require Open With → FontLab 9. No URL-scheme security preference is enabled or changed. Internet access to GitHub is needed at installation, not during spacing.

## Validation completed

- 33 unit tests, including fresh installation, relocation to a different Unicode/space-containing user path, repair, development-launcher migration, failed-write rollback, network/checksum failure, unrelated-script preservation, uninstall backup, archive traversal rejection, concurrent installer exclusion and native data-path discovery.
- A real online clean installation downloaded the pinned GitHub archive, verified it and loaded the original engine. The old development path was deliberately invalid.
- The actual `.vfpy` was opened through FontLab 9 on macOS. Native Qt networking completed the download without blocking the scripting runtime. The installer installed/updated the release and refreshed the Scripts menu automatically.
- The installed runtime passed the disposable FontLab smoke suite: spacing, scaled/sheared component preservation, side toggles, fixed and explicit widths, ordinary pen strokes, italic metrics, embedded settings, and native VFJ/VFC save/reopen.
- The installed Scripts-menu launcher opened the compact palette with development import paths removed. The engine path resolved inside Extensions, not the Developer checkout.
- The source checkout and upstream clone are not runtime dependencies. The original Git repository remains unchanged.

Windows uses the same PythonQt installer and FontLab's `dataPathDefault`. The Windows Documents path, including redirection, is handled by FontLab rather than inferred from AppData. Windows path selection is covered by tests. **A real Windows install/run has not been performed on this macOS host; treat Windows as pending native release verification.**

The earlier cross-host spacing validation remains documented in PARITY.md. This installer release changes deployment, not the spacing algorithm.

## Updating the upstream pin

Review the upstream changes first. Run `tools/pin_upstream.py` against the reviewed clone; it verifies the downloaded archive's engine files against that clone and records both the commit and archive checksum. It does not edit the original repository. Run unit tests, the installed-runtime smoke suite and relevant parity tests before rebuilding a release. Do not substitute a floating `master` download in the installer.

## Publication

The artifacts are ready to host on the product download page or attach to a release. No public upload, repository publication or website deployment is performed by the build. Publish the matching source ZIP and SHA256SUMS alongside the customer ZIP. Keep the user-facing Windows validation status accurate until tested there.
