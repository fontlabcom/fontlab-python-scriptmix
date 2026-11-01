---
this_file: src_docs/md/scripts/features/build-suffix-substitution.md
tags: ["Features"]
categories: ["Features"]
---

# Build Suffix Substitution

Preview a font-wide suffix substitution. Append to source only; compile and test in the Features panel.

What it does:
    Run with a font active. All original controls use the shared fly panel lifecycle.
    Feature data is font-wide; reopen after switching fonts or changing source.

How it works:
    Build safe base/alternate pairs from a suffix and append statements
    through Fontport's exact-source writer. Refuse stale references or
    ambiguous existing code.

Why this design:
    Keeping the original prefix and unrelated feature blocks prevents a small
    substitution edit from replacing other stored source.

How to use:
    Run Features > Build Suffix Substitution. Set suffix and tag, inspect the
    full proposed source, then Apply or Copy preview. Compile and test
    manually in FontLab's Features panel.

Benefit:
    Prepare a consistent substitution block while retaining source outside the
    requested feature edit.

Run **Features > Build Suffix Substitution** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/def83c621849aa1bd9c0c416e011596b47e76b509693bb78a1e441c06091c18c.py)
<!--/codeinclude-->
