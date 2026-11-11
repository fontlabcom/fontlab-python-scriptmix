---
this_file: src_docs/md/scripts/masters/italic-angle.md
tags: ["Masters"]
categories: ["Masters"]
---

# Italic Angle

Stage each master's italic angle, preview its slant and Apply in one Undo.

What it does:
    The font remains unchanged until Apply. Reopen after changing fonts, masters or
    their source angles. Close disconnects all owned signals and painter callbacks.

How it works:
    Use the App master-angle editor and its owned panel. Keep proposed angles
    separate from stored values until the explicit Apply action.

Why this design:
    Staging several angles together lets the user compare slant before
    changing master metadata.

How to use:
    Open the font and run Masters > Italic Angle. Edit the proposed angle
    values, inspect the slant preview and press Apply. Close to discard an
    unapplied proposal.

Benefit:
    Review a family's master angles in one place and record the Apply action
    as one Undo step.

Run **Masters > Italic Angle** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `c886ced09f78812bb00b330840870ed5f6285b6ad5ce403f7a789bec1d4ced30`

[Python source at `75235791e388`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/75235791e3880a7bc761f4bbc9c5dccc08813705/Scripts/Masters/Italic%20Angle.py)
