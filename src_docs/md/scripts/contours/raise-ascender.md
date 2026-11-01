---
this_file: src_docs/md/scripts/contours/raise-ascender.md
tags: ["Contours"]
categories: ["Contours"]
---

# Raise Ascender

Raise own nodes strictly above associated-master x-height + 10 by Amount.

What it does:
    Raise this master processes every selected layer occurrence. Raise all masters
    processes ALL foreground layers of the first selected glyph, including auxiliaries.
    Controls move too; components stay unchanged. Default Amount is 10. See the guide
    for complete original scope, supported native associations and history limits.
    Behavior adapted from Simon Cozens' MIT Raise Ascender; full attribution in NOTICE.

How it works:
    Delegate the original two-action workflow to App. Test own nodes against
    the associated master's x-height plus ten, then move qualifying nodes by
    the requested amount.

Why this design:
    Using the associated master keeps the threshold meaningful for auxiliary
    layers; components remain outside the node movement.

How to use:
    Select the required glyph/layer and run Contours > Raise Ascender. Set
    Amount, choose Raise this master or Raise all masters and review the
    guide's exact scope and refusals.

Benefit:
    Adjust the defined ascender-node range without changing component
    placement or adding a separate transformation tool.

Run **Contours > Raise Ascender** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/e296cc6ea40bc077e7c2ce667407b62cd04c0cd38b817d2f5f56c152bd139ab7.py)
<!--/codeinclude-->
