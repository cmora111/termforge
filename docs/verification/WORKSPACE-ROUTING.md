# Workspace Routing Verification

## Record

- **Project:** TermForge
- **Date:** September 21, 2026
- **Implementation checkpoint:** `be50630` — `Add GNOME window discovery and
  Tilix workspace integration`
- **Branch at checkpoint:**
  `TermForge-Project/Engineering_library_foundation`
- **Result:** PASS for all ten planned workspace destinations.
- **Evidence type:** User-reported interactive observations in Tilix and
  TermForge. This document is a test record, not an automated test log.

## Objective

Verify that selecting a workspace in TermForge and sending an echo command
through the test popout causes Tilix to activate the corresponding tab and
the command to execute in the intended tmux pane.

## Environment and assumptions

The tested configuration used the tmux backend, the tmux server addressed by
`tmux -S ''`, and one Tilix window with ten tabs in a fixed order. The launch
configuration included `TERMFORGE_TMUX_SOCKET=empty` and a verified
`TERMFORGE_TILIX_WINDOW_ID` (then `8`). The Tilix window ID is transient.

The tmux pane listing established `forge-main:0.0` as `%20` and
`stage-main:0.0` as `%4` during diagnosis. These pane IDs are observations,
not stable configuration values.

## Procedure

1. Select the intended workspace using the TermForge menu.
2. Begin from a different Tilix workspace tab.
3. Open the TermForge test popout and issue its echo command.
4. Observe the visible Tilix tab and the destination of the echo output.
5. Record PASS only when the selected workspace activates and the command
   executes there.

## Results


| Destination | Starting workspace / direction | Result |
| --- | --- | --- |
| `forge-main:0.0` | Stage Main → Forge Main | PASS |
| `forge-secondary:0.0` | Stage Secondary → Forge Secondary | PASS |
| `stage-main:0.0` | Forge Main → Stage Main | PASS |
| `stage-secondary:0.0` | Forge Secondary → Stage Secondary | PASS |
| `marlin-main:0.0` | Forge Main → Marlin 1 | PASS |
| `marlin-secondary:0.0` | Forge Secondary → Marlin 2 | PASS |
| `bible-main:0.0` | Forge Main → Bible 1 | PASS |
| `bible-secondary:0.0` | Forge Secondary → Bible 2 | PASS |
| `termforge-main:0.0` | Forge Main → TermForge 1 | PASS |
| `termforge-secondary:0.0` | Forge Secondary → TermForge 2 | PASS |


The user explicitly reported the main and secondary Forge/Stage routing
working in both directions. The Marlin, Bible, and TermForge destinations
were subsequently reported as passing from the Forge tabs indicated above.
Reverse-direction tests for every Marlin, Bible, and TermForge destination
were not separately reported.

## Earlier focused checks

Four focused tests passed before the ten-destination sweep:

1. Startup and configuration: tmux backend and Forge target displayed.
2. Direct backend test: switched to Forge and executed the test echo.
3. Normal command button: switched to Forge and executed its echo.
4. Target persistence: target remained usable after restarting TermForge.

When Stage was selected later, an initial command was observed in Forge.
Subsequent inspection found the saved configuration and application display
both showed `stage-main:0.0`; the direct backend test then switched to Stage
and executed there. A repeated regular-button test also switched to Stage
and executed there. No code change was established as necessary for that
particular observation.

## Interpretation

All ten planned destinations passed the reported menu/test-popout routing
procedure. This supports the workspace-routing milestone for the tested
configuration. It does **not** establish universal reliability, independent
verification of D-Bus activation, or correctness after changing tab order,
Tilix window ID, tmux server, or workspace layout.

Other command types (including Spawn and Detached), GNOME window-picker
behavior, and the rest of TermForge's features require separate verification.

## Follow-up

- Preserve this record in `docs/verification/WORKSPACE-ROUTING.md`.
- Keep backup files such as `tmux_backend.py.bak` out of Git.
- Review the documentation diff and commit this record separately from the
  already-pushed implementation checkpoint.
- Repeat the routing procedure if the tab layout or activation mechanism
  changes.
