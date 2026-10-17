# this_file: Scripts/Font Info/Glyph Order Preview and Export.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Font Info · Glyph Order Preview & Export
"""Sort by Unicode, name or Unicode script; export one glyph name per line for the whole font.

Open this script with a font active. Choose Unicode, Name or Script, then select
Export order. The modeless chooser saves UTF-8 text for use in another workflow.
The font's glyph order and outlines stay unchanged. Reopen after switching fonts.
"""

from bisect import bisect_right
from pathlib import Path
from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    close_script_dialog,
    current_package,
    font_info_dialog_type,
    show_script_dialog,
)

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui

TITLE = "Glyph Order Preview & Export"
KEY = "fontinfo_glyph_order_tool"


def glyph_records(package: Any) -> Any:
    """Read all Unicode assignments, including secondary encodings, in font order."""
    FL = ap.FL

    active = current_package()
    if active is None or active.id != package.id:
        msg = "Activate the original font and reopen this tool."
        raise ValueError(msg)
    legacy = FL.fl.font
    return [
        (legacy[i].name, list(package.findName(legacy[i].name).fgGlyph.unicodes))
        for i in range(len(legacy))
    ]


# Unicode Script property boundaries (Unicode 18.0 data snapshot, 2026-06-29).
# Source: https://unicode.org/Public/UNIDATA/Scripts.txt via FontTools data.
# © 2026 Unicode, Inc. Terms: https://www.unicode.org/license.txt
# These are specification data; no FontTools runtime dependency.
SCRIPT_DATA = """
0:Zyyy 41:Latn 5B:Zyyy 61:Latn 7B:Zyyy AA:Latn AB:Zyyy BA:Latn BB:Zyyy C0:Latn D7:Zyyy D8:Latn F7:Zyyy F8:Latn
2B9:Zyyy 2E0:Latn 2E5:Zyyy 2EA:Bopo 2EC:Zyyy 300:Zinh 370:Grek 374:Zyyy 375:Grek 378:Zzzz 37A:Grek 37E:Zyyy
37F:Grek 380:Zzzz 384:Grek 385:Zyyy 386:Grek 387:Zyyy 388:Grek 38B:Zzzz 38C:Grek 38D:Zzzz 38E:Grek 3A2:Zzzz
3A3:Grek 3E2:Copt 3F0:Grek 400:Cyrl 485:Zinh 487:Cyrl 530:Zzzz 531:Armn 557:Zzzz 558:Armn 590:Zzzz 591:Hebr
5CA:Zzzz 5D0:Hebr 5EB:Zzzz 5EF:Hebr 5F5:Zzzz 600:Arab 605:Zyyy 606:Arab 60C:Zyyy 60D:Arab 61B:Zyyy 61C:Arab
61F:Zyyy 620:Arab 640:Zyyy 641:Arab 64B:Zinh 656:Arab 670:Zinh 671:Arab 6DD:Zyyy 6DE:Arab 700:Syrc 70E:Zzzz
70F:Syrc 74B:Zzzz 74D:Syrc 750:Arab 780:Thaa 7B2:Zzzz 7C0:Nkoo 7FB:Zzzz 7FD:Nkoo 800:Samr 82E:Zzzz 830:Samr
83F:Zzzz 840:Mand 85C:Zzzz 85E:Mand 85F:Zzzz 860:Syrc 86B:Zzzz 870:Arab 892:Zzzz 897:Arab 8E2:Zyyy 8E3:Arab
900:Deva 951:Zinh 955:Deva 964:Zyyy 966:Deva 980:Beng 984:Zzzz 985:Beng 98D:Zzzz 98F:Beng 991:Zzzz 993:Beng
9A9:Zzzz 9AA:Beng 9B1:Zzzz 9B2:Beng 9B3:Zzzz 9B6:Beng 9BA:Zzzz 9BC:Beng 9C5:Zzzz 9C7:Beng 9C9:Zzzz 9CB:Beng
9CF:Zzzz 9D7:Beng 9D8:Zzzz 9DC:Beng 9DE:Zzzz 9DF:Beng 9E4:Zzzz 9E6:Beng 9FF:Zzzz A01:Guru A04:Zzzz A05:Guru
A0B:Zzzz A0F:Guru A11:Zzzz A13:Guru A29:Zzzz A2A:Guru A31:Zzzz A32:Guru A34:Zzzz A35:Guru A37:Zzzz A38:Guru
A3A:Zzzz A3C:Guru A3D:Zzzz A3E:Guru A43:Zzzz A47:Guru A49:Zzzz A4B:Guru A4E:Zzzz A51:Guru A52:Zzzz A59:Guru
A5D:Zzzz A5E:Guru A5F:Zzzz A66:Guru A77:Zzzz A81:Gujr A84:Zzzz A85:Gujr A8E:Zzzz A8F:Gujr A92:Zzzz A93:Gujr
AA9:Zzzz AAA:Gujr AB1:Zzzz AB2:Gujr AB4:Zzzz AB5:Gujr ABA:Zzzz ABC:Gujr AC6:Zzzz AC7:Gujr ACA:Zzzz ACB:Gujr
ACE:Zzzz AD0:Gujr AD1:Zzzz AE0:Gujr AE4:Zzzz AE6:Gujr AF2:Zzzz AF9:Gujr B00:Zzzz B01:Orya B04:Zzzz B05:Orya
B0D:Zzzz B0F:Orya B11:Zzzz B13:Orya B29:Zzzz B2A:Orya B31:Zzzz B32:Orya B34:Zzzz B35:Orya B3A:Zzzz B3C:Orya
B45:Zzzz B47:Orya B49:Zzzz B4B:Orya B4E:Zzzz B53:Orya B58:Zzzz B5C:Orya B5E:Zzzz B5F:Orya B64:Zzzz B66:Orya
B78:Zzzz B82:Taml B84:Zzzz B85:Taml B8B:Zzzz B8E:Taml B91:Zzzz B92:Taml B96:Zzzz B99:Taml B9B:Zzzz B9C:Taml
B9D:Zzzz B9E:Taml BA0:Zzzz BA3:Taml BA5:Zzzz BA8:Taml BAB:Zzzz BAE:Taml BBA:Zzzz BBE:Taml BC3:Zzzz BC6:Taml
BC9:Zzzz BCA:Taml BCE:Zzzz BD0:Taml BD1:Zzzz BD7:Taml BD8:Zzzz BE6:Taml BFB:Zzzz C00:Telu C0D:Zzzz C0E:Telu
C11:Zzzz C12:Telu C29:Zzzz C2A:Telu C3A:Zzzz C3C:Telu C45:Zzzz C46:Telu C49:Zzzz C4A:Telu C4E:Zzzz C55:Telu
C57:Zzzz C58:Telu C5B:Zzzz C5C:Telu C5E:Zzzz C60:Telu C64:Zzzz C66:Telu C70:Zzzz C77:Telu C80:Knda C8D:Zzzz
C8E:Knda C91:Zzzz C92:Knda CA9:Zzzz CAA:Knda CB4:Zzzz CB5:Knda CBA:Zzzz CBC:Knda CC5:Zzzz CC6:Knda CC9:Zzzz
CCA:Knda CCE:Zzzz CD5:Knda CD7:Zzzz CDC:Knda CDF:Zzzz CE0:Knda CE4:Zzzz CE6:Knda CF0:Zzzz CF1:Knda CF4:Zzzz
D00:Mlym D0D:Zzzz D0E:Mlym D11:Zzzz D12:Mlym D45:Zzzz D46:Mlym D49:Zzzz D4A:Mlym D50:Zzzz D54:Mlym D64:Zzzz
D66:Mlym D80:Zzzz D81:Sinh D84:Zzzz D85:Sinh D97:Zzzz D9A:Sinh DB2:Zzzz DB3:Sinh DBC:Zzzz DBD:Sinh DBE:Zzzz
DC0:Sinh DC7:Zzzz DCA:Sinh DCB:Zzzz DCF:Sinh DD5:Zzzz DD6:Sinh DD7:Zzzz DD8:Sinh DE0:Zzzz DE6:Sinh DF0:Zzzz
DF2:Sinh DF5:Zzzz E01:Thai E3B:Zzzz E3F:Zyyy E40:Thai E5C:Zzzz E81:Laoo E83:Zzzz E84:Laoo E85:Zzzz E86:Laoo
E8B:Zzzz E8C:Laoo EA4:Zzzz EA5:Laoo EA6:Zzzz EA7:Laoo EBE:Zzzz EC0:Laoo EC5:Zzzz EC6:Laoo EC7:Zzzz EC8:Laoo
ECF:Zzzz ED0:Laoo EDA:Zzzz EDC:Laoo EE0:Zzzz F00:Tibt F48:Zzzz F49:Tibt F6D:Zzzz F71:Tibt F98:Zzzz F99:Tibt
FBD:Zzzz FBE:Tibt FCD:Zzzz FCE:Tibt FD5:Zyyy FD9:Tibt FDB:Zzzz 1000:Mymr 10A0:Geor 10C6:Zzzz 10C7:Geor
10C8:Zzzz 10CD:Geor 10CE:Zzzz 10D0:Geor 10FB:Zyyy 10FC:Geor 1100:Hang 1200:Ethi 1249:Zzzz 124A:Ethi 124E:Zzzz
1250:Ethi 1257:Zzzz 1258:Ethi 1259:Zzzz 125A:Ethi 125E:Zzzz 1260:Ethi 1289:Zzzz 128A:Ethi 128E:Zzzz 1290:Ethi
12B1:Zzzz 12B2:Ethi 12B6:Zzzz 12B8:Ethi 12BF:Zzzz 12C0:Ethi 12C1:Zzzz 12C2:Ethi 12C6:Zzzz 12C8:Ethi 12D7:Zzzz
12D8:Ethi 1311:Zzzz 1312:Ethi 1316:Zzzz 1318:Ethi 135B:Zzzz 135D:Ethi 137D:Zzzz 1380:Ethi 139A:Zzzz 13A0:Cher
13F6:Zzzz 13F8:Cher 13FE:Zzzz 1400:Cans 1680:Ogam 169D:Zzzz 16A0:Runr 16EB:Zyyy 16EE:Runr 16F9:Zzzz 1700:Tglg
1716:Zzzz 171F:Tglg 1720:Hano 1735:Zyyy 1737:Zzzz 1740:Buhd 1754:Zzzz 1760:Tagb 176D:Zzzz 176E:Tagb 1771:Zzzz
1772:Tagb 1774:Zzzz 1780:Khmr 17DE:Zzzz 17E0:Khmr 17EA:Zzzz 17F0:Khmr 17FA:Zzzz 1800:Mong 1802:Zyyy 1804:Mong
1805:Zyyy 1806:Mong 181A:Zzzz 1820:Mong 1879:Zzzz 1880:Mong 18AB:Zzzz 18B0:Cans 18F6:Zzzz 1900:Limb 191F:Zzzz
1920:Limb 192C:Zzzz 1930:Limb 193C:Zzzz 1940:Limb 1941:Zzzz 1944:Limb 1950:Tale 196E:Zzzz 1970:Tale 1975:Zzzz
1980:Talu 19AC:Zzzz 19B0:Talu 19CA:Zzzz 19D0:Talu 19DB:Zzzz 19DE:Talu 19E0:Khmr 1A00:Bugi 1A1C:Zzzz 1A1E:Bugi
1A20:Lana 1A5F:Zzzz 1A60:Lana 1A7D:Zzzz 1A7F:Lana 1A8A:Zzzz 1A90:Lana 1A9A:Zzzz 1AA0:Lana 1AAE:Zzzz 1AB0:Zinh
1AF1:Zzzz 1B00:Bali 1B4D:Zzzz 1B4E:Bali 1B80:Sund 1BC0:Batk 1BF4:Zzzz 1BFC:Batk 1C00:Lepc 1C38:Zzzz 1C3B:Lepc
1C4A:Zzzz 1C4D:Lepc 1C50:Olck 1C80:Cyrl 1C8B:Zzzz 1C90:Geor 1CBB:Zzzz 1CBD:Geor 1CC0:Sund 1CC8:Zzzz 1CD0:Zinh
1CD3:Zyyy 1CD4:Zinh 1CE1:Zyyy 1CE2:Zinh 1CE9:Zyyy 1CED:Zinh 1CEE:Zyyy 1CF4:Zinh 1CF5:Zyyy 1CF8:Zinh 1CFA:Zyyy
1CFB:Zzzz 1D00:Latn 1D26:Grek 1D2B:Cyrl 1D2C:Latn 1D5D:Grek 1D62:Latn 1D66:Grek 1D6B:Latn 1D78:Cyrl 1D79:Latn
1DBF:Grek 1DC0:Zinh 1E00:Latn 1F00:Grek 1F16:Zzzz 1F18:Grek 1F1E:Zzzz 1F20:Grek 1F46:Zzzz 1F48:Grek 1F4E:Zzzz
1F50:Grek 1F58:Zzzz 1F59:Grek 1F5A:Zzzz 1F5B:Grek 1F5C:Zzzz 1F5D:Grek 1F5E:Zzzz 1F5F:Grek 1F7E:Zzzz 1F80:Grek
1FB5:Zzzz 1FB6:Grek 1FC5:Zzzz 1FC6:Grek 1FD4:Zzzz 1FD6:Grek 1FDC:Zzzz 1FDD:Grek 1FF0:Zzzz 1FF2:Grek 1FF5:Zzzz
1FF6:Grek 1FFF:Zzzz 2000:Zyyy 200C:Zinh 200E:Zyyy 2065:Zzzz 2066:Zyyy 2071:Latn 2072:Zzzz 2074:Zyyy 207F:Latn
2080:Zyyy 2090:Latn 20A0:Zyyy 20C5:Zzzz 20D0:Zinh 20F1:Zzzz 2100:Zyyy 2126:Grek 2127:Zyyy 212A:Latn 212C:Zyyy
2132:Latn 2133:Zyyy 214E:Latn 214F:Zyyy 2160:Latn 2189:Zyyy 218C:Zzzz 2190:Zyyy 242A:Zzzz 2440:Zyyy 244B:Zzzz
2460:Zyyy 2800:Brai 2900:Zyyy 2B74:Zzzz 2B76:Zyyy 2C00:Glag 2C60:Latn 2C80:Copt 2CF4:Zzzz 2CF9:Copt 2D00:Geor
2D26:Zzzz 2D27:Geor 2D28:Zzzz 2D2D:Geor 2D2E:Zzzz 2D30:Tfng 2D68:Zzzz 2D6F:Tfng 2D71:Zzzz 2D7F:Tfng 2D80:Ethi
2D97:Zzzz 2DA0:Ethi 2DA7:Zzzz 2DA8:Ethi 2DAF:Zzzz 2DB0:Ethi 2DB7:Zzzz 2DB8:Ethi 2DBF:Zzzz 2DC0:Ethi 2DC7:Zzzz
2DC8:Ethi 2DCF:Zzzz 2DD0:Ethi 2DD7:Zzzz 2DD8:Ethi 2DDF:Zzzz 2DE0:Cyrl 2E00:Zyyy 2E5E:Zzzz 2E60:Zyyy 2E64:Zzzz
2E80:Hani 2E9A:Zzzz 2E9B:Hani 2EF4:Zzzz 2F00:Hani 2FD6:Zzzz 2FF0:Zyyy 3005:Hani 3006:Zyyy 3007:Hani 3008:Zyyy
3021:Hani 302A:Zinh 302E:Hang 3030:Zyyy 3038:Hani 303C:Zyyy 3040:Zzzz 3041:Hira 3097:Zzzz 3099:Zinh 309B:Zyyy
309D:Hira 30A0:Zyyy 30A1:Kana 30FB:Zyyy 30FD:Kana 3100:Zzzz 3105:Bopo 3130:Zzzz 3131:Hang 318F:Zzzz 3190:Zyyy
31A0:Bopo 31C0:Zyyy 31E6:Zzzz 31EF:Zyyy 31F0:Kana 3200:Hang 321F:Zzzz 3220:Zyyy 3260:Hang 327F:Zyyy 32D0:Kana
32FF:Zyyy 3300:Kana 3358:Zyyy 3400:Hani 4DC0:Zyyy 4E00:Hani A000:Yiii A48D:Zzzz A490:Yiii A4C7:Zzzz A4D0:Lisu
A500:Vaii A62C:Zzzz A640:Cyrl A6A0:Bamu A6F8:Zzzz A700:Zyyy A722:Latn A788:Zyyy A78B:Latn A7DE:Zzzz A7E2:Latn
A7E3:Zzzz A7F1:Latn A800:Sylo A82D:Zzzz A830:Zyyy A83A:Zzzz A840:Phag A878:Zzzz A880:Saur A8C6:Zzzz A8CE:Saur
A8DA:Zzzz A8E0:Deva A900:Kali A92E:Zyyy A92F:Kali A930:Rjng A954:Zzzz A95F:Rjng A960:Hang A97D:Zzzz A980:Java
A9CE:Zzzz A9CF:Zyyy A9D0:Java A9DA:Zzzz A9DE:Java A9E0:Mymr A9FF:Zzzz AA00:Cham AA37:Zzzz AA40:Cham AA4E:Zzzz
AA50:Cham AA5A:Zzzz AA5C:Cham AA60:Mymr AA80:Tavt AAC3:Zzzz AADB:Tavt AAE0:Mtei AAF7:Zzzz AB01:Ethi AB07:Zzzz
AB09:Ethi AB0F:Zzzz AB11:Ethi AB17:Zzzz AB20:Ethi AB27:Zzzz AB28:Ethi AB2F:Zzzz AB30:Latn AB5B:Zyyy AB5C:Latn
AB65:Grek AB66:Latn AB6A:Zyyy AB6C:Latn AB6E:Zzzz AB70:Cher ABC0:Mtei ABEE:Zzzz ABF0:Mtei ABFA:Zzzz AC00:Hang
D7A4:Zzzz D7B0:Hang D7C7:Zzzz D7CB:Hang D7FC:Zzzz F900:Hani FA6E:Zzzz FA70:Hani FADA:Zzzz FB00:Latn FB07:Zzzz
FB13:Armn FB18:Zzzz FB1D:Hebr FB37:Zzzz FB38:Hebr FB3D:Zzzz FB3E:Hebr FB3F:Zzzz FB40:Hebr FB42:Zzzz FB43:Hebr
FB45:Zzzz FB46:Hebr FB50:Arab FD3E:Zyyy FD40:Arab FDD0:Zzzz FDF0:Arab FE00:Zinh FE10:Zyyy FE1A:Zzzz FE20:Zinh
FE2E:Cyrl FE30:Zyyy FE53:Zzzz FE54:Zyyy FE67:Zzzz FE68:Zyyy FE6C:Zzzz FE70:Arab FE75:Zzzz FE76:Arab FEFD:Zzzz
FEFF:Zyyy FF00:Zzzz FF01:Zyyy FF21:Latn FF3B:Zyyy FF41:Latn FF5B:Zyyy FF66:Kana FF70:Zyyy FF71:Kana FF9E:Zyyy
FFA0:Hang FFBF:Zzzz FFC2:Hang FFC8:Zzzz FFCA:Hang FFD0:Zzzz FFD2:Hang FFD8:Zzzz FFDA:Hang FFDD:Zzzz FFE0:Zyyy
FFE7:Zzzz FFE8:Zyyy FFEF:Zzzz FFF9:Zyyy FFFE:Zzzz 10000:Linb 1000C:Zzzz 1000D:Linb 10027:Zzzz 10028:Linb
1003B:Zzzz 1003C:Linb 1003E:Zzzz 1003F:Linb 1004E:Zzzz 10050:Linb 1005E:Zzzz 10080:Linb 100FB:Zzzz 10100:Zyyy
10103:Zzzz 10107:Zyyy 10134:Zzzz 10137:Zyyy 10140:Grek 1018F:Zzzz 10190:Zyyy 1019D:Zzzz 101A0:Grek 101A1:Zzzz
101D0:Zyyy 101FD:Zinh 101FE:Zzzz 10280:Lyci 1029D:Zzzz 102A0:Cari 102D1:Zzzz 102E0:Zinh 102E1:Zyyy 102FC:Zzzz
10300:Ital 10324:Zzzz 1032D:Ital 10330:Goth 1034B:Zzzz 10350:Perm 1037B:Zzzz 10380:Ugar 1039E:Zzzz 1039F:Ugar
103A0:Xpeo 103C4:Zzzz 103C8:Xpeo 103D6:Zzzz 10400:Dsrt 10450:Shaw 10480:Osma 1049E:Zzzz 104A0:Osma 104AA:Zzzz
104B0:Osge 104D4:Zzzz 104D8:Osge 104FC:Zzzz 10500:Elba 10528:Zzzz 10530:Aghb 10564:Zzzz 1056F:Aghb 10570:Vith
1057B:Zzzz 1057C:Vith 1058B:Zzzz 1058C:Vith 10593:Zzzz 10594:Vith 10596:Zzzz 10597:Vith 105A2:Zzzz 105A3:Vith
105B2:Zzzz 105B3:Vith 105BA:Zzzz 105BB:Vith 105BD:Zzzz 105C0:Todr 105F4:Zzzz 10600:Lina 10737:Zzzz 10740:Lina
10756:Zzzz 10760:Lina 10768:Zzzz 10780:Latn 10786:Zzzz 10787:Latn 107B1:Zzzz 107B2:Latn 107C0:Zzzz 10800:Cprt
10806:Zzzz 10808:Cprt 10809:Zzzz 1080A:Cprt 10836:Zzzz 10837:Cprt 10839:Zzzz 1083C:Cprt 1083D:Zzzz 1083F:Cprt
10840:Armi 10856:Zzzz 10857:Armi 10860:Palm 10880:Nbat 1089F:Zzzz 108A7:Nbat 108B0:Zzzz 108E0:Hatr 108F3:Zzzz
108F4:Hatr 108F6:Zzzz 108FB:Hatr 10900:Phnx 1091C:Zzzz 1091F:Phnx 10920:Lydi 1093A:Zzzz 1093F:Lydi 10940:Sidt
1095A:Zzzz 10980:Mero 109A0:Merc 109B8:Zzzz 109BC:Merc 109D0:Zzzz 109D2:Merc 10A00:Khar 10A04:Zzzz 10A05:Khar
10A07:Zzzz 10A0C:Khar 10A14:Zzzz 10A15:Khar 10A18:Zzzz 10A19:Khar 10A36:Zzzz 10A38:Khar 10A3B:Zzzz 10A3F:Khar
10A49:Zzzz 10A50:Khar 10A59:Zzzz 10A60:Sarb 10A80:Narb 10AA0:Zzzz 10AC0:Mani 10AE7:Zzzz 10AEB:Mani 10AF7:Zzzz
10B00:Avst 10B36:Zzzz 10B39:Avst 10B40:Prti 10B56:Zzzz 10B58:Prti 10B60:Phli 10B73:Zzzz 10B78:Phli 10B80:Phlp
10B92:Zzzz 10B99:Phlp 10B9D:Zzzz 10BA9:Phlp 10BB0:Zzzz 10C00:Orkh 10C49:Zzzz 10C80:Hung 10CB3:Zzzz 10CC0:Hung
10CF3:Zzzz 10CFA:Hung 10D00:Rohg 10D28:Zzzz 10D30:Rohg 10D3A:Zzzz 10D40:Gara 10D66:Zzzz 10D69:Gara 10D86:Zzzz
10D8E:Gara 10D90:Zzzz 10E60:Arab 10E7F:Zzzz 10E80:Yezi 10EAA:Zzzz 10EAB:Yezi 10EAE:Zzzz 10EB0:Yezi 10EB2:Zzzz
10EC2:Arab 10EC8:Zzzz 10EC9:Arab 10EEF:Zzzz 10EF0:Arab 10F00:Sogo 10F28:Zzzz 10F30:Sogd 10F5A:Zzzz 10F70:Ougr
10F8A:Zzzz 10FB0:Chrs 10FCC:Zzzz 10FE0:Elym 10FF7:Zzzz 11000:Brah 1104E:Zzzz 11052:Brah 11076:Zzzz 1107F:Brah
11080:Kthi 110C3:Zzzz 110CD:Kthi 110CE:Zzzz 110D0:Sora 110E9:Zzzz 110F0:Sora 110FA:Zzzz 11100:Cakm 11135:Zzzz
11136:Cakm 11148:Zzzz 11150:Mahj 11177:Zzzz 11180:Shrd 111E0:Zzzz 111E1:Sinh 111F5:Zzzz 11200:Khoj 11212:Zzzz
11213:Khoj 11242:Zzzz 11280:Mult 11287:Zzzz 11288:Mult 11289:Zzzz 1128A:Mult 1128E:Zzzz 1128F:Mult 1129E:Zzzz
1129F:Mult 112AA:Zzzz 112B0:Sind 112EB:Zzzz 112F0:Sind 112FA:Zzzz 11300:Gran 11304:Zzzz 11305:Gran 1130D:Zzzz
1130F:Gran 11311:Zzzz 11313:Gran 11329:Zzzz 1132A:Gran 11331:Zzzz 11332:Gran 11334:Zzzz 11335:Gran 1133A:Zzzz
1133B:Zinh 1133C:Gran 11345:Zzzz 11347:Gran 11349:Zzzz 1134B:Gran 1134E:Zzzz 11350:Gran 11351:Zzzz 11357:Gran
11358:Zzzz 1135D:Gran 11364:Zzzz 11366:Gran 1136D:Zzzz 11370:Gran 11375:Zzzz 11380:Tutg 1138A:Zzzz 1138B:Tutg
1138C:Zzzz 1138E:Tutg 1138F:Zzzz 11390:Tutg 113B6:Zzzz 113B7:Tutg 113C1:Zzzz 113C2:Tutg 113C3:Zzzz 113C5:Tutg
113C6:Zzzz 113C7:Tutg 113CB:Zzzz 113CC:Tutg 113D6:Zzzz 113D7:Tutg 113D9:Zzzz 113E1:Tutg 113E3:Zzzz 11400:Newa
1145C:Zzzz 1145D:Newa 11462:Zzzz 11480:Tirh 114C8:Zzzz 114D0:Tirh 114DA:Zzzz 11580:Sidd 115B6:Zzzz 115B8:Sidd
115DE:Zzzz 11600:Modi 11645:Zzzz 11650:Modi 1165A:Zzzz 11660:Mong 1166D:Zzzz 11680:Takr 116BA:Zzzz 116C0:Takr
116CA:Zzzz 116D0:Mymr 116E4:Zzzz 11700:Ahom 1171B:Zzzz 1171D:Ahom 1172C:Zzzz 11730:Ahom 11747:Zzzz 11800:Dogr
1183C:Zzzz 118A0:Wara 118F3:Zzzz 118FF:Wara 11900:Diak 11907:Zzzz 11909:Diak 1190A:Zzzz 1190C:Diak 11914:Zzzz
11915:Diak 11917:Zzzz 11918:Diak 11936:Zzzz 11937:Diak 11939:Zzzz 1193B:Diak 11947:Zzzz 11950:Diak 1195A:Zzzz
119A0:Nand 119A8:Zzzz 119AA:Nand 119D8:Zzzz 119DA:Nand 119E5:Zzzz 11A00:Zanb 11A48:Zzzz 11A50:Soyo 11AA3:Zzzz
11AB0:Cans 11AC0:Pauc 11AF9:Zzzz 11B00:Deva 11B0B:Zzzz 11B60:Shrd 11B68:Zzzz 11BC0:Sunu 11BE2:Zzzz 11BF0:Sunu
11BFA:Zzzz 11C00:Bhks 11C09:Zzzz 11C0A:Bhks 11C37:Zzzz 11C38:Bhks 11C46:Zzzz 11C50:Bhks 11C6D:Zzzz 11C70:Marc
11C90:Zzzz 11C92:Marc 11CA8:Zzzz 11CA9:Marc 11CB7:Zzzz 11D00:Gonm 11D07:Zzzz 11D08:Gonm 11D0A:Zzzz 11D0B:Gonm
11D37:Zzzz 11D3A:Gonm 11D3B:Zzzz 11D3C:Gonm 11D3E:Zzzz 11D3F:Gonm 11D48:Zzzz 11D50:Gonm 11D5A:Zzzz 11D60:Gong
11D66:Zzzz 11D67:Gong 11D69:Zzzz 11D6A:Gong 11D8F:Zzzz 11D90:Gong 11D92:Zzzz 11D93:Gong 11D99:Zzzz 11DA0:Gong
11DAA:Zzzz 11DB0:Tols 11DDC:Zzzz 11DE0:Tols 11DEA:Zzzz 11DF0:Beng 11DF2:Zzzz 11EE0:Maka 11EF9:Zzzz 11F00:Kawi
11F11:Zzzz 11F12:Kawi 11F3B:Zzzz 11F3E:Kawi 11F5B:Zzzz 11FB0:Lisu 11FB1:Zzzz 11FC0:Taml 11FF2:Zzzz 11FFF:Taml
12000:Xsux 1239A:Zzzz 12400:Xsux 12544:Zzzz 12550:Xsux 125A8:Pcun 1264C:Xsux 12687:Zzzz 12F90:Cpmn 12FF3:Zzzz
13000:Egyp 13456:Zzzz 13460:Egyp 143FB:Zzzz 14400:Hluw 14647:Zzzz 16100:Gukh 1613A:Zzzz 16800:Bamu 16A39:Zzzz
16A40:Mroo 16A5F:Zzzz 16A60:Mroo 16A6A:Zzzz 16A6E:Mroo 16A70:Tnsa 16ABF:Zzzz 16AC0:Tnsa 16ACA:Zzzz 16AD0:Bass
16AEE:Zzzz 16AF0:Bass 16AF6:Zzzz 16B00:Hmng 16B46:Zzzz 16B50:Hmng 16B5A:Zzzz 16B5B:Hmng 16B62:Zzzz 16B63:Hmng
16B78:Zzzz 16B7D:Hmng 16B90:Zzzz 16D40:Krai 16D7A:Zzzz 16E40:Medf 16E9B:Zzzz 16EA0:Berf 16EB9:Zzzz 16EBB:Berf
16ED4:Zzzz 16F00:Plrd 16F4B:Zzzz 16F4F:Plrd 16F88:Zzzz 16F8F:Plrd 16FA0:Zzzz 16FE0:Tang 16FE1:Nshu 16FE2:Hani
16FE4:Kits 16FE5:Zzzz 16FF0:Hani 16FF7:Zzzz 17000:Tang 18B00:Kits 18CDB:Zzzz 18CFF:Kits 18D00:Tang 18D21:Zzzz
18D80:Tang 18DF3:Zzzz 18E00:Jurc 19192:Zzzz 191A0:Jurc 191D3:Zzzz 1AFF0:Kana 1AFF4:Zzzz 1AFF5:Kana 1AFFC:Zzzz
1AFFD:Kana 1AFFF:Zzzz 1B000:Kana 1B001:Hira 1B120:Kana 1B123:Hira 1B124:Kana 1B129:Zzzz 1B132:Hira 1B133:Zzzz
1B150:Hira 1B153:Zzzz 1B155:Kana 1B156:Zzzz 1B164:Kana 1B169:Zzzz 1B170:Nshu 1B2FC:Zzzz 1BC00:Dupl 1BC6B:Zzzz
1BC70:Dupl 1BC7D:Zzzz 1BC80:Dupl 1BC89:Zzzz 1BC90:Dupl 1BC9A:Zzzz 1BC9C:Dupl 1BCA0:Zyyy 1BCA4:Zzzz 1CC00:Zyyy
1CCFD:Zzzz 1CD00:Zyyy 1CEB4:Zzzz 1CEBA:Zyyy 1CED1:Zzzz 1CED2:Zyyy 1CED5:Zzzz 1CEDD:Zyyy 1CEFE:Zzzz 1CF00:Zinh
1CF2E:Zzzz 1CF30:Zinh 1CF47:Zzzz 1CF50:Zyyy 1CFC4:Zzzz 1D000:Zyyy 1D0F6:Zzzz 1D100:Zyyy 1D127:Zinh 1D129:Zyyy
1D167:Zinh 1D16A:Zyyy 1D17B:Zinh 1D183:Zyyy 1D185:Zinh 1D18C:Zyyy 1D1AA:Zinh 1D1AE:Zyyy 1D200:Grek 1D246:Zzzz
1D250:Zyyy 1D25B:Zinh 1D25D:Zyyy 1D282:Zzzz 1D2C0:Zyyy 1D2D4:Zzzz 1D2E0:Zyyy 1D2F4:Zzzz 1D300:Zyyy 1D357:Zzzz
1D360:Zyyy 1D379:Zzzz 1D400:Zyyy 1D455:Zzzz 1D456:Zyyy 1D49D:Zzzz 1D49E:Zyyy 1D4A0:Zzzz 1D4A2:Zyyy 1D4A3:Zzzz
1D4A5:Zyyy 1D4A7:Zzzz 1D4A9:Zyyy 1D4AD:Zzzz 1D4AE:Zyyy 1D4BA:Zzzz 1D4BB:Zyyy 1D4BC:Zzzz 1D4BD:Zyyy 1D4C4:Zzzz
1D4C5:Zyyy 1D506:Zzzz 1D507:Zyyy 1D50B:Zzzz 1D50D:Zyyy 1D515:Zzzz 1D516:Zyyy 1D51D:Zzzz 1D51E:Zyyy 1D53A:Zzzz
1D53B:Zyyy 1D53F:Zzzz 1D540:Zyyy 1D545:Zzzz 1D546:Zyyy 1D547:Zzzz 1D54A:Zyyy 1D551:Zzzz 1D552:Zyyy 1D6A7:Zzzz
1D6A8:Zyyy 1D7CC:Zzzz 1D7CE:Zyyy 1D800:Sgnw 1DA8C:Zzzz 1DA9B:Sgnw 1DAA0:Zzzz 1DAA1:Sgnw 1DAB0:Zzzz 1DB00:Zyyy
1DB1D:Zzzz 1DF00:Latn 1DF82:Zzzz 1DF90:Latn 1DF97:Zzzz 1DFCD:Latn 1DFF3:Grek 1DFF5:Latn 1E000:Glag 1E007:Zzzz
1E008:Glag 1E019:Zzzz 1E01B:Glag 1E022:Zzzz 1E023:Glag 1E025:Zzzz 1E026:Glag 1E02B:Zzzz 1E030:Cyrl 1E06E:Zzzz
1E08F:Cyrl 1E090:Zzzz 1E100:Hmnp 1E12D:Zzzz 1E130:Hmnp 1E13E:Zzzz 1E140:Hmnp 1E14A:Zzzz 1E14E:Hmnp 1E150:Zzzz
1E290:Toto 1E2AF:Zzzz 1E2C0:Wcho 1E2FA:Zzzz 1E2FF:Wcho 1E300:Zzzz 1E4D0:Nagm 1E4FA:Zzzz 1E5D0:Onao 1E5FB:Zzzz
1E5FF:Onao 1E600:Zzzz 1E6C0:Tayo 1E6DF:Zzzz 1E6E0:Tayo 1E6F6:Zzzz 1E6FE:Tayo 1E700:Zzzz 1E7E0:Ethi 1E7E7:Zzzz
1E7E8:Ethi 1E7EC:Zzzz 1E7ED:Ethi 1E7EF:Zzzz 1E7F0:Ethi 1E7FF:Zzzz 1E800:Mend 1E8C5:Zzzz 1E8C7:Mend 1E8D7:Zzzz
1E900:Adlm 1E94C:Zzzz 1E950:Adlm 1E95A:Zzzz 1E95E:Adlm 1E960:Zzzz 1EC71:Zyyy 1ECB5:Zzzz 1ED01:Zyyy 1ED3E:Zzzz
1EE00:Arab 1EE04:Zzzz 1EE05:Arab 1EE20:Zzzz 1EE21:Arab 1EE23:Zzzz 1EE24:Arab 1EE25:Zzzz 1EE27:Arab 1EE28:Zzzz
1EE29:Arab 1EE33:Zzzz 1EE34:Arab 1EE38:Zzzz 1EE39:Arab 1EE3A:Zzzz 1EE3B:Arab 1EE3C:Zzzz 1EE42:Arab 1EE43:Zzzz
1EE47:Arab 1EE48:Zzzz 1EE49:Arab 1EE4A:Zzzz 1EE4B:Arab 1EE4C:Zzzz 1EE4D:Arab 1EE50:Zzzz 1EE51:Arab 1EE53:Zzzz
1EE54:Arab 1EE55:Zzzz 1EE57:Arab 1EE58:Zzzz 1EE59:Arab 1EE5A:Zzzz 1EE5B:Arab 1EE5C:Zzzz 1EE5D:Arab 1EE5E:Zzzz
1EE5F:Arab 1EE60:Zzzz 1EE61:Arab 1EE63:Zzzz 1EE64:Arab 1EE65:Zzzz 1EE67:Arab 1EE6B:Zzzz 1EE6C:Arab 1EE73:Zzzz
1EE74:Arab 1EE78:Zzzz 1EE79:Arab 1EE7D:Zzzz 1EE7E:Arab 1EE7F:Zzzz 1EE80:Arab 1EE8A:Zzzz 1EE8B:Arab 1EE9C:Zzzz
1EEA1:Arab 1EEA4:Zzzz 1EEA5:Arab 1EEAA:Zzzz 1EEAB:Arab 1EEBC:Zzzz 1EEF0:Arab 1EEF2:Zzzz 1F000:Zyyy 1F02C:Zzzz
1F030:Zyyy 1F094:Zzzz 1F0A0:Zyyy 1F0AF:Zzzz 1F0B1:Zyyy 1F0C0:Zzzz 1F0C1:Zyyy 1F0D0:Zzzz 1F0D1:Zyyy 1F0F6:Zzzz
1F100:Zyyy 1F1AF:Zzzz 1F1E6:Zyyy 1F200:Hira 1F201:Zyyy 1F203:Zzzz 1F210:Zyyy 1F23C:Zzzz 1F240:Zyyy 1F249:Zzzz
1F250:Zyyy 1F252:Zzzz 1F260:Zyyy 1F266:Zzzz 1F300:Zyyy 1F6DA:Zzzz 1F6DC:Zyyy 1F6ED:Zzzz 1F6F0:Zyyy 1F6FD:Zzzz
1F700:Zyyy 1F7DC:Zzzz 1F7E0:Zyyy 1F7EC:Zzzz 1F7F0:Zyyy 1F80C:Zzzz 1F810:Zyyy 1F848:Zzzz 1F850:Zyyy 1F85A:Zzzz
1F860:Zyyy 1F888:Zzzz 1F890:Zyyy 1F8AE:Zzzz 1F8B0:Zyyy 1F8BC:Zzzz 1F8C0:Zyyy 1F8C2:Zzzz 1F8D0:Zyyy 1F8D9:Zzzz
1F900:Zyyy 1FA58:Zzzz 1FA60:Zyyy 1FA6E:Zzzz 1FA70:Zyyy 1FA7D:Zzzz 1FA80:Zyyy 1FAC7:Zzzz 1FAC8:Zyyy 1FAC9:Zzzz
1FACC:Zyyy 1FADE:Zzzz 1FADF:Zyyy 1FAEC:Zzzz 1FAEF:Zyyy 1FAFB:Zzzz 1FB00:Zyyy 1FB93:Zzzz 1FB94:Zyyy 1FBFB:Zzzz
20000:Hani 2A6E0:Zzzz 2A700:Hani 2B81F:Zzzz 2B820:Hani 2CEAE:Zzzz 2CEB0:Hani 2EBE1:Zzzz 2EBF0:Hani 2EE5E:Zzzz
2F800:Hani 2FA1E:Zzzz 30000:Hani 3134B:Zzzz 31350:Hani 3347A:Zzzz 3D000:Seal 3FC40:Zzzz E0001:Zyyy E0002:Zzzz
E0020:Zyyy E0080:Zzzz E0100:Zinh E01F0:Zzzz
"""
SCRIPT_BOUNDARIES = tuple(int(token.split(":")[0], 16) for token in SCRIPT_DATA.split())
SCRIPT_TAGS = tuple(token.split(":")[1] for token in SCRIPT_DATA.split())
SCRIPT_NAMES = {
    "Adlm": "Adlam",
    "Aghb": "Caucasian_Albanian",
    "Ahom": "Ahom",
    "Arab": "Arabic",
    "Armi": "Imperial_Aramaic",
    "Armn": "Armenian",
    "Avst": "Avestan",
    "Bali": "Balinese",
    "Bamu": "Bamum",
    "Bass": "Bassa_Vah",
    "Batk": "Batak",
    "Beng": "Bengali",
    "Berf": "Beria_Erfe",
    "Bhks": "Bhaiksuki",
    "Bopo": "Bopomofo",
    "Brah": "Brahmi",
    "Brai": "Braille",
    "Bugi": "Buginese",
    "Buhd": "Buhid",
    "Cakm": "Chakma",
    "Cans": "Canadian_Aboriginal",
    "Cari": "Carian",
    "Cham": "Cham",
    "Cher": "Cherokee",
    "Chrs": "Chorasmian",
    "Copt": "Coptic",
    "Cpmn": "Cypro_Minoan",
    "Cprt": "Cypriot",
    "Cyrl": "Cyrillic",
    "Deva": "Devanagari",
    "Diak": "Dives_Akuru",
    "Dogr": "Dogra",
    "Dsrt": "Deseret",
    "Dupl": "Duployan",
    "Egyp": "Egyptian_Hieroglyphs",
    "Elba": "Elbasan",
    "Elym": "Elymaic",
    "Ethi": "Ethiopic",
    "Gara": "Garay",
    "Geor": "Georgian",
    "Glag": "Glagolitic",
    "Gong": "Gunjala_Gondi",
    "Gonm": "Masaram_Gondi",
    "Goth": "Gothic",
    "Gran": "Grantha",
    "Grek": "Greek",
    "Gujr": "Gujarati",
    "Gukh": "Gurung_Khema",
    "Guru": "Gurmukhi",
    "Hang": "Hangul",
    "Hani": "Han",
    "Hano": "Hanunoo",
    "Hatr": "Hatran",
    "Hebr": "Hebrew",
    "Hira": "Hiragana",
    "Hluw": "Anatolian_Hieroglyphs",
    "Hmng": "Pahawh_Hmong",
    "Hmnp": "Nyiakeng_Puachue_Hmong",
    "Hrkt": "Katakana_Or_Hiragana",
    "Hung": "Old_Hungarian",
    "Ital": "Old_Italic",
    "Java": "Javanese",
    "Jurc": "Jurchen",
    "Kali": "Kayah_Li",
    "Kana": "Katakana",
    "Kawi": "Kawi",
    "Khar": "Kharoshthi",
    "Khmr": "Khmer",
    "Khoj": "Khojki",
    "Kits": "Khitan_Small_Script",
    "Knda": "Kannada",
    "Krai": "Kirat_Rai",
    "Kthi": "Kaithi",
    "Lana": "Tai_Tham",
    "Laoo": "Lao",
    "Latn": "Latin",
    "Lepc": "Lepcha",
    "Limb": "Limbu",
    "Lina": "Linear_A",
    "Linb": "Linear_B",
    "Lisu": "Lisu",
    "Lyci": "Lycian",
    "Lydi": "Lydian",
    "Mahj": "Mahajani",
    "Maka": "Makasar",
    "Mand": "Mandaic",
    "Mani": "Manichaean",
    "Marc": "Marchen",
    "Medf": "Medefaidrin",
    "Mend": "Mende_Kikakui",
    "Merc": "Meroitic_Cursive",
    "Mero": "Meroitic_Hieroglyphs",
    "Mlym": "Malayalam",
    "Modi": "Modi",
    "Mong": "Mongolian",
    "Mroo": "Mro",
    "Mtei": "Meetei_Mayek",
    "Mult": "Multani",
    "Mymr": "Myanmar",
    "Nagm": "Nag_Mundari",
    "Nand": "Nandinagari",
    "Narb": "Old_North_Arabian",
    "Nbat": "Nabataean",
    "Newa": "Newa",
    "Nkoo": "Nko",
    "Nshu": "Nushu",
    "Ogam": "Ogham",
    "Olck": "Ol_Chiki",
    "Onao": "Ol_Onal",
    "Orkh": "Old_Turkic",
    "Orya": "Oriya",
    "Osge": "Osage",
    "Osma": "Osmanya",
    "Ougr": "Old_Uyghur",
    "Palm": "Palmyrene",
    "Pauc": "Pau_Cin_Hau",
    "Pcun": "Proto_Cuneiform",
    "Perm": "Old_Permic",
    "Phag": "Phags_Pa",
    "Phli": "Inscriptional_Pahlavi",
    "Phlp": "Psalter_Pahlavi",
    "Phnx": "Phoenician",
    "Plrd": "Miao",
    "Prti": "Inscriptional_Parthian",
    "Rjng": "Rejang",
    "Rohg": "Hanifi_Rohingya",
    "Runr": "Runic",
    "Samr": "Samaritan",
    "Sarb": "Old_South_Arabian",
    "Saur": "Saurashtra",
    "Seal": "Seal",
    "Sgnw": "SignWriting",
    "Shaw": "Shavian",
    "Shrd": "Sharada",
    "Sidd": "Siddham",
    "Sidt": "Sidetic",
    "Sind": "Khudawadi",
    "Sinh": "Sinhala",
    "Sogd": "Sogdian",
    "Sogo": "Old_Sogdian",
    "Sora": "Sora_Sompeng",
    "Soyo": "Soyombo",
    "Sund": "Sundanese",
    "Sunu": "Sunuwar",
    "Sylo": "Syloti_Nagri",
    "Syrc": "Syriac",
    "Tagb": "Tagbanwa",
    "Takr": "Takri",
    "Tale": "Tai_Le",
    "Talu": "New_Tai_Lue",
    "Taml": "Tamil",
    "Tang": "Tangut",
    "Tavt": "Tai_Viet",
    "Tayo": "Tai_Yo",
    "Telu": "Telugu",
    "Tfng": "Tifinagh",
    "Tglg": "Tagalog",
    "Thaa": "Thaana",
    "Thai": "Thai",
    "Tibt": "Tibetan",
    "Tirh": "Tirhuta",
    "Tnsa": "Tangsa",
    "Todr": "Todhri",
    "Tols": "Tolong_Siki",
    "Toto": "Toto",
    "Tutg": "Tulu_Tigalari",
    "Ugar": "Ugaritic",
    "Vaii": "Vai",
    "Vith": "Vithkuqi",
    "Wara": "Warang_Citi",
    "Wcho": "Wancho",
    "Xpeo": "Old_Persian",
    "Xsux": "Cuneiform",
    "Yezi": "Yezidi",
    "Yiii": "Yi",
    "Zanb": "Zanabazar_Square",
    "Zinh": "Inherited",
    "Zyyy": "Common",
    "Zzzz": "Unknown",
}


def script_group(codes: list[int]) -> str:
    """Resolve the primary Unicode encoding using the retained data snapshot."""
    if not codes:
        return "Unencoded"
    code = min(codes)
    if not 0 <= code <= 0x10FFFF:
        return "Unknown"
    tag = SCRIPT_TAGS[bisect_right(SCRIPT_BOUNDARIES, code) - 1]
    return SCRIPT_NAMES[tag].replace("_", " ")


def sorted_order(
    records: list[tuple[str, list[int]]], mode: str
) -> list[tuple[str, list[int]]]:
    """Sort by the selected key while keeping .notdef first."""

    def key(record: Any) -> Any:
        """Return the selected glyph ordering key."""
        name, codes = record
        unicode_key = min(codes) if codes else 0x110000
        if mode == "Name":
            return name.casefold(), name
        if mode == "Script":
            return script_group(codes), unicode_key, name
        return unicode_key, name

    # Keep .notdef at GID 0 in every exported order.
    return sorted(records, key=lambda record: (record[0] != ".notdef", key(record)))


def run(records: list[tuple[str, list[int]]], mode: str) -> str:
    """Compute or apply the complete tool operation from validated inputs."""
    return "\n".join(name for name, _ in sorted_order(records, mode)) + (
        "\n" if records else ""
    )


FontInfoDialog = font_info_dialog_type()


class Dialog(FontInfoDialog):
    def __init__(self, parent: Any = None) -> None:
        """Open the shared Font Info panel with this tool's controls and preview."""
        FontInfoDialog.__init__(
            self,
            parent,
            title=TITLE,
            subtitle="Sort by Unicode, name or Unicode script; export one glyph name per line for the whole font.",
            key=KEY,
        )

    def closeEvent(self, event: Any) -> None:
        """Disconnect owned slots and destroy this modeless dialog on close."""
        self._preview_valid = False
        close_script_dialog(
            self,
            event,
            KEY,
            children=(self.chooser,) if self.chooser is not None else (),
        )
        self.chooser = None

    def setup(self) -> None:
        """Build all original controls and connect owned signals."""
        self.chooser = None
        self.records = glyph_records(self.package) if self.package else []
        self.mode = QtGui.QComboBox()
        self.mode.addItems(["Unicode", "Name", "Script"])
        self.form.addWidget(QtGui.QLabel("Sort by"), 0, 0)
        self.form.addWidget(self.mode, 0, 1)
        self.apply_button.setText("Export order…")
        self._connect(self.mode.currentIndexChanged, lambda *a: self.refresh())

    def refresh(self) -> None:
        """Validate and display a complete preview before enabling Apply."""
        self._preview_valid = False
        self.apply_button.setEnabled(False)
        if self.package is None:
            return
        self.ensure_font()
        self.records = glyph_records(self.package)
        ordered = sorted_order(self.records, self.mode.currentText)
        positions = {name: index for index, (name, _) in enumerate(self.records)}
        self.rows(
            ["Glyph", "Old index", "New index", "Script"],
            [
                (name, positions[name], index, script_group(codes))
                for index, (name, codes) in enumerate(ordered)
            ],
        )
        self.last_result = {
            "order": [name for name, _ in ordered],
            "text": run(self.records, self.mode.currentText),
        }
        self.apply_button.setEnabled(bool(ordered))
        self.status.setText(
            "Export only: no verified bound API safely reorders glyphs. Script uses the primary encoding and a Unicode 18.0 data snapshot. .notdef stays first.",
        )
        self._preview_valid = True

    def apply(self) -> None:
        """Show one owned modeless chooser for the refreshed glyph order."""
        self.ensure_preview()
        self.refresh()
        if self.chooser is None:
            self.chooser = QtGui.QFileDialog(
                self, "Export glyph order", "glyph-order.txt", "Text files (*.txt)"
            )
            self.chooser.setAcceptMode(QtGui.QFileDialog.AcceptSave)
            self.chooser.setDefaultSuffix("txt")
            self._connect(self.chooser.fileSelected, self.export_order)
        self.chooser.open()

    def export_order(self, path: str | Path) -> None:
        """Write the refreshed complete glyph order as UTF-8 text."""
        self.ensure_font()
        self.refresh()
        Path(path).write_text(self.last_result["text"], encoding="utf-8")
        self.status.setText(f"Exported {len(self.records)} names to {Path(path).name}")


def main() -> Any:
    """Replace this tool's owned dialog using the shared script registry."""
    return show_script_dialog(Dialog, KEY)


if __name__ == "__main__":
    main()
