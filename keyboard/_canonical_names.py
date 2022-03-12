# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
    basestring
except NameError:
    basestring = str

import platform

# Defaults to Windows canonical names (platform-specific overrides below)
canonical_names = {
    "escape": "esc",
    "return": "enter",
    "del": "delete",
    "control": "ctrl",
    "left arrow": "left",
    "up arrow": "up",
    "down arrow": "down",
    "right arrow": "right",
    " ": "space",  # Prefer to spell out keys that would be hard to read.
    "\x1b": "esc",
    "\x08": "backspace",
    "\n": "enter",
    "\t": "tab",
    "\r": "enter",
    "scrlk": "scroll lock",
    "prtscn": "print screen",
    "prnt scrn": "print screen",
    "snapshot": "print screen",
    "ins": "insert",
    "pause break": "pause",
    "ctrll lock": "caps lock",
    "capslock": "caps lock",
    "number lock": "num lock",
    "numlock": "num lock",
    "space bar": "space",
    "spacebar": "space",
    "linefeed": "enter",
    "win": "windows",
    # Mac keys
    "command": "windows",
    "cmd": "windows",
    "control": "ctrl",
    "option": "alt",
    "app": "menu",
    "apps": "menu",
    "application": "menu",
    "applications": "menu",
    "pagedown": "page down",
    "pageup": "page up",
    "pgdown": "page down",
    "pgup": "page up",
    "play/pause": "play/pause media",
    "num multiply": "*",
    "num divide": "/",
    "num add": "+",
    "num plus": "+",
    "num minus": "-",
    "num sub": "-",
    "num enter": "enter",
    "num 0": "0",
    "num 1": "1",
    "num 2": "2",
    "num 3": "3",
    "num 4": "4",
    "num 5": "5",
    "num 6": "6",
    "num 7": "7",
    "num 8": "8",
    "num 9": "9",
    "left win": "left windows",
    "right win": "right windows",
    "left control": "left ctrl",
    "right control": "right ctrl",
    "left menu": "left alt",  # Windows...
    "altgr": "alt gr",
    # https://www.x.org/releases/X11R7.6/doc/libX11/Compose/en_US.UTF-8.html
    # https://svn.apache.org/repos/asf/xmlgraphics/commons/tags/commons-1_0/src/java/org/apache/xmlgraphics/fonts/Glyphs.java
    # Note this list has plenty of uppercase letters that are not being used
    # at the moment, as normalization forces names to be lowercase.
    "Aacute": "Á",
    "aacute": "á",
    "Aacutesmall": "",
    "abovedot": "˙",
    "Abreve": "Ă",
    "abreve": "ă",
    "Abreveacute": "Ắ",
    "abreveacute": "ắ",
    "Abrevebelowdot": "Ặ",
    "abrevebelowdot": "ặ",
    "Abrevegrave": "Ằ",
    "abrevegrave": "ằ",
    "Abrevehook": "Ẳ",
    "abrevehook": "ẳ",
    "Abrevetilde": "Ẵ",
    "abrevetilde": "ẵ",
    "Acircumflex": "Â",
    "acircumflex": "â",
    "Acircumflexacute": "Ấ",
    "acircumflexacute": "ấ",
    "Acircumflexbelowdot": "Ậ",
    "acircumflexbelowdot": "ậ",
    "Acircumflexgrave": "Ầ",
    "acircumflexgrave": "ầ",
    "Acircumflexhook": "Ẩ",
    "acircumflexhook": "ẩ",
    "Acircumflexsmall": "",
    "Acircumflextilde": "Ẫ",
    "acircumflextilde": "ẫ",
    "acute": "´",
    "Acute": "",
    "acutecomb": "́",
    "Acutesmall": "",
    "add": "+",
    "Adiaeresis": "Ä",
    "adiaeresis": "ä",
    "Adieresis": "Ä",
    "adieresis": "ä",
    "Adieresissmall": "",
    "ae": "æ",
    "AE": "Æ",
    "AEacute": "Ǽ",
    "aeacute": "ǽ",
    "AEsmall": "",
    "afii00208": "―",
    "afii10017": "А",
    "afii10018": "Б",
    "afii10019": "В",
    "afii10020": "Г",
    "afii10021": "Д",
    "afii10022": "Е",
    "afii10023": "Ё",
    "afii10024": "Ж",
    "afii10025": "З",
    "afii10026": "И",
    "afii10027": "Й",
    "afii10028": "К",
    "afii10029": "Л",
    "afii10030": "М",
    "afii10031": "Н",
    "afii10032": "О",
    "afii10033": "П",
    "afii10034": "Р",
    "afii10035": "С",
    "afii10036": "Т",
    "afii10037": "У",
    "afii10038": "Ф",
    "afii10039": "Х",
    "afii10040": "Ц",
    "afii10041": "Ч",
    "afii10042": "Ш",
    "afii10043": "Щ",
    "afii10044": "Ъ",
    "afii10045": "Ы",
    "afii10046": "Ь",
    "afii10047": "Э",
    "afii10048": "Ю",
    "afii10049": "Я",
    "afii10050": "Ґ",
    "afii10051": "Ђ",
    "afii10052": "Ѓ",
    "afii10053": "Є",
    "afii10054": "Ѕ",
    "afii10055": "І",
    "afii10056": "Ї",
    "afii10057": "Ј",
    "afii10058": "Љ",
    "afii10059": "Њ",
    "afii10060": "Ћ",
    "afii10061": "Ќ",
    "afii10062": "Ў",
    "afii10063": "",
    "afii10064": "",
    "afii10065": "а",
    "afii10066": "б",
    "afii10067": "в",
    "afii10068": "г",
    "afii10069": "д",
    "afii10070": "е",
    "afii10071": "ё",
    "afii10072": "ж",
    "afii10073": "з",
    "afii10074": "и",
    "afii10075": "й",
    "afii10076": "к",
    "afii10077": "л",
    "afii10078": "м",
    "afii10079": "н",
    "afii10080": "о",
    "afii10081": "п",
    "afii10082": "р",
    "afii10083": "с",
    "afii10084": "т",
    "afii10085": "у",
    "afii10086": "ф",
    "afii10087": "х",
    "afii10088": "ц",
    "afii10089": "ч",
    "afii10090": "ш",
    "afii10091": "щ",
    "afii10092": "ъ",
    "afii10093": "ы",
    "afii10094": "ь",
    "afii10095": "э",
    "afii10096": "ю",
    "afii10097": "я",
    "afii10098": "ґ",
    "afii10099": "ђ",
    "afii10100": "ѓ",
    "afii10101": "є",
    "afii10102": "ѕ",
    "afii10103": "і",
    "afii10104": "ї",
    "afii10105": "ј",
    "afii10106": "љ",
    "afii10107": "њ",
    "afii10108": "ћ",
    "afii10109": "ќ",
    "afii10110": "ў",
    "afii10145": "Џ",
    "afii10146": "Ѣ",
    "afii10147": "Ѳ",
    "afii10148": "Ѵ",
    "afii10192": "",
    "afii10193": "џ",
    "afii10194": "ѣ",
    "afii10195": "ѳ",
    "afii10196": "ѵ",
    "afii10831": "",
    "afii10832": "",
    "afii10846": "ә",
    "afii299": "‎",
    "afii300": "‏",
    "afii301": "‍",
    "afii57381": "٪",
    "afii57388": "،",
    "afii57392": "٠",
    "afii57393": "١",
    "afii57394": "٢",
    "afii57395": "٣",
    "afii57396": "٤",
    "afii57397": "٥",
    "afii57398": "٦",
    "afii57399": "٧",
    "afii57400": "٨",
    "afii57401": "٩",
    "afii57403": "؛",
    "afii57407": "؟",
    "afii57409": "ء",
    "afii57410": "آ",
    "afii57411": "أ",
    "afii57412": "ؤ",
    "afii57413": "إ",
    "afii57414": "ئ",
    "afii57415": "ا",
    "afii57416": "ب",
    "afii57417": "ة",
    "afii57418": "ت",
    "afii57419": "ث",
    "afii57420": "ج",
    "afii57421": "ح",
    "afii57422": "خ",
    "afii57423": "د",
    "afii57424": "ذ",
    "afii57425": "ر",
    "afii57426": "ز",
    "afii57427": "س",
    "afii57428": "ش",
    "afii57429": "ص",
    "afii57430": "ض",
    "afii57431": "ط",
    "afii57432": "ظ",
    "afii57433": "ع",
    "afii57434": "غ",
    "afii57440": "ـ",
    "afii57441": "ف",
    "afii57442": "ق",
    "afii57443": "ك",
    "afii57444": "ل",
    "afii57445": "م",
    "afii57446": "ن",
    "afii57448": "و",
    "afii57449": "ى",
    "afii57450": "ي",
    "afii57451": "ً",
    "afii57452": "ٌ",
    "afii57453": "ٍ",
    "afii57454": "َ",
    "afii57455": "ُ",
    "afii57456": "ِ",
    "afii57457": "ّ",
    "afii57458": "ْ",
    "afii57470": "ه",
    "afii57505": "ڤ",
    "afii57506": "پ",
    "afii57507": "چ",
    "afii57508": "ژ",
    "afii57509": "گ",
    "afii57511": "ٹ",
    "afii57512": "ڈ",
    "afii57513": "ڑ",
    "afii57514": "ں",
    "afii57519": "ے",
    "afii57534": "ە",
    "afii57636": "₪",
    "afii57645": "־",
    "afii57658": "׃",
    "afii57664": "א",
    "afii57665": "ב",
    "afii57666": "ג",
    "afii57667": "ד",
    "afii57668": "ה",
    "afii57669": "ו",
    "afii57670": "ז",
    "afii57671": "ח",
    "afii57672": "ט",
    "afii57673": "י",
    "afii57674": "ך",
    "afii57675": "כ",
    "afii57676": "ל",
    "afii57677": "ם",
    "afii57678": "מ",
    "afii57679": "ן",
    "afii57680": "נ",
    "afii57681": "ס",
    "afii57682": "ע",
    "afii57683": "ף",
    "afii57684": "פ",
    "afii57685": "ץ",
    "afii57686": "צ",
    "afii57687": "ק",
    "afii57688": "ר",
    "afii57689": "ש",
    "afii57690": "ת",
    "afii57694": "שׁ",
    "afii57695": "שׂ",
    "afii57700": "וֹ",
    "afii57705": "ײַ",
    "afii57716": "װ",
    "afii57717": "ױ",
    "afii57718": "ײ",
    "afii57723": "וּ",
    "afii57793": "ִ",
    "afii57794": "ֵ",
    "afii57795": "ֶ",
    "afii57796": "ֻ",
    "afii57797": "ָ",
    "afii57798": "ַ",
    "afii57799": "ְ",
    "afii57800": "ֲ",
    "afii57801": "ֱ",
    "afii57802": "ֳ",
    "afii57803": "ׂ",
    "afii57804": "ׁ",
    "afii57806": "ֹ",
    "afii57807": "ּ",
    "afii57839": "ֽ",
    "afii57841": "ֿ",
    "afii57842": "׀",
    "afii57929": "ʼ",
    "afii61248": "℅",
    "afii61289": "ℓ",
    "afii61352": "№",
    "afii61573": "‬",
    "afii61574": "‭",
    "afii61575": "‮",
    "afii61664": "‌",
    "afii63167": "٭",
    "afii64937": "ʽ",
    "Agrave": "À",
    "agrave": "à",
    "Agravesmall": "",
    "agudo": "´",
    "aleph": "ℵ",
    "Alpha": "Α",
    "alpha": "α",
    "Alphatonos": "Ά",
    "alphatonos": "ά",
    "Amacron": "Ā",
    "amacron": "ā",
    "ampersand": "&",
    "ampersandsmall": "",
    "angle": "∠",
    "angleleft": "〈",
    "angleright": "〉",
    "anoteleia": "·",
    "Aogonek": "Ą",
    "aogonek": "ą",
    "apostrophe": "'",
    "approxequal": "≈",
    "Aring": "Å",
    "aring": "å",
    "Aringacute": "Ǻ",
    "aringacute": "ǻ",
    "Aringsmall": "",
    "arrowboth": "↔",
    "arrowdblboth": "⇔",
    "arrowdbldown": "⇓",
    "arrowdblleft": "⇐",
    "arrowdblright": "⇒",
    "arrowdblup": "⇑",
    "arrowdown": "↓",
    "arrowhorizex": "",
    "arrowleft": "←",
    "arrowright": "→",
    "arrowup": "↑",
    "arrowupdn": "↕",
    "arrowupdnbse": "↨",
    "arrowvertex": "",
    "asciicircum": "^",
    "asciitilde": "~",
    "Asmall": "",
    "asterisk": "*",
    "asteriskmath": "∗",
    "asuperior": "",
    "at": "@",
    "Atilde": "Ã",
    "atilde": "ã",
    "Atildesmall": "",
    "backslash": "\\",
    "bar": "|",
    "Beta": "Β",
    "beta": "β",
    "block": "█",
    "braceex": "",
    "braceleft": "{",
    "braceleftbt": "",
    "braceleftmid": "",
    "bracelefttp": "",
    "braceright": "}",
    "bracerightbt": "",
    "bracerightmid": "",
    "bracerighttp": "",
    "bracketleft": "[",
    "bracketleftbt": "",
    "bracketleftex": "",
    "bracketlefttp": "",
    "bracketright": "]",
    "bracketrightbt": "",
    "bracketrightex": "",
    "bracketrighttp": "",
    "breve": "˘",
    "Brevesmall": "",
    "brokenbar": "¦",
    "Bsmall": "",
    "bsuperior": "",
    "bullet": "•",
    "Cacute": "Ć",
    "cacute": "ć",
    "caron": "ˇ",
    "Caron": "",
    "Caronsmall": "",
    "carriagereturn": "↵",
    "Ccaron": "Č",
    "ccaron": "č",
    "Ccedilla": "Ç",
    "ccedilla": "ç",
    "Ccedillasmall": "",
    "Ccircumflex": "Ĉ",
    "ccircumflex": "ĉ",
    "Cdotaccent": "Ċ",
    "cdotaccent": "ċ",
    "cedilla": "¸",
    "Cedillasmall": "",
    "cent": "¢",
    "centinferior": "",
    "centoldstyle": "",
    "centsuperior": "",
    "Chi": "Χ",
    "chi": "χ",
    "circle": "○",
    "circlemultiply": "⊗",
    "circleplus": "⊕",
    "circumflex": "^",
    "circumflex": "ˆ",
    "Circumflexsmall": "",
    "club": "♣",
    "colon": ":",
    "colonmonetary": "₡",
    "ColonSign": "₡",
    "comma": ",",
    "commaaccent": "",
    "commainferior": "",
    "commasuperior": "",
    "congruent": "≅",
    "copyright": "©",
    "copyrightsans": "",
    "copyrightserif": "",
    "CruzeiroSign": "₢",
    "Csmall": "",
    "currency": "¤",
    "cyrBreve": "",
    "cyrbreve": "",
    "cyrFlex": "",
    "cyrflex": "",
    "dagger": "†",
    "daggerdbl": "‡",
    "dblGrave": "",
    "dblgrave": "",
    "Dcaron": "Ď",
    "dcaron": "ď",
    "Dcroat": "Đ",
    "dcroat": "đ",
    "degree": "°",
    "Delta": "Δ",
    "delta": "δ",
    "diaeresis": "¨",
    "diamond": "♦",
    "dieresis": "¨",
    "Dieresis": "",
    "DieresisAcute": "",
    "dieresisacute": "",
    "DieresisGrave": "",
    "dieresisgrave": "",
    "Dieresissmall": "",
    "dieresistonos": "΅",
    "divide": "/",
    "divide": "÷",
    "division": "÷",
    "dkshade": "▓",
    "dnblock": "▄",
    "dollar": "$",
    "dollarinferior": "",
    "dollaroldstyle": "",
    "dollarsuperior": "",
    "dong": "₫",
    "DongSign": "₫",
    "dot": ".",
    "dotaccent": "˙",
    "Dotaccentsmall": "",
    "dotbelowcomb": "̣",
    "dotlessi": "ı",
    "dotlessj": "",
    "dotmath": "⋅",
    "Dsmall": "",
    "dstroke": "đ",
    "Dstroke": "Đ",
    "dsuperior": "",
    "Eacute": "É",
    "eacute": "é",
    "Eacutesmall": "",
    "Ebreve": "Ĕ",
    "ebreve": "ĕ",
    "Ecaron": "Ě",
    "ecaron": "ě",
    "Ecircumflex": "Ê",
    "ecircumflex": "ê",
    "Ecircumflexacute": "Ế",
    "ecircumflexacute": "ế",
    "Ecircumflexbelowdot": "Ệ",
    "ecircumflexbelowdot": "ệ",
    "Ecircumflexgrave": "Ề",
    "ecircumflexgrave": "ề",
    "Ecircumflexhook": "Ể",
    "ecircumflexhook": "ể",
    "Ecircumflexsmall": "",
    "Ecircumflextilde": "Ễ",
    "ecircumflextilde": "ễ",
    "EcuSign": "₠",
    "Ediaeresis": "Ë",
    "ediaeresis": "ë",
    "Edieresis": "Ë",
    "edieresis": "ë",
    "Edieresissmall": "",
    "Edotaccent": "Ė",
    "edotaccent": "ė",
    "Egrave": "È",
    "egrave": "è",
    "Egravesmall": "",
    "eight": "8",
    "eightinferior": "₈",
    "eightoldstyle": "",
    "eightsubscript": "₈",
    "eightsuperior": "⁸",
    "element": "∈",
    "ellipsis": "…",
    "Emacron": "Ē",
    "emacron": "ē",
    "emdash": "—",
    "emptyset": "∅",
    "endash": "–",
    "enfilledcircbullet": "•",
    "Eng": "Ŋ",
    "eng": "ŋ",
    "Eogonek": "Ę",
    "eogonek": "ę",
    "Epsilon": "Ε",
    "epsilon": "ε",
    "Epsilontonos": "Έ",
    "epsilontonos": "έ",
    "equal": "=",
    "equivalence": "≡",
    "Esmall": "",
    "estimated": "℮",
    "esuperior": "",
    "Eta": "Η",
    "eta": "η",
    "Etatonos": "Ή",
    "etatonos": "ή",
    "ETH": "Ð",
    "eth": "ð",
    "Eth": "Ð",
    "Ethsmall": "",
    "euro": "€",
    "Euro": "€",
    "EuroSign": "€",
    "exclam": "!",
    "exclamdbl": "‼",
    "exclamdown": "¡",
    "exclamdownsmall": "",
    "exclamsmall": "",
    "existential": "∃",
    "female": "♀",
    "ff": "ﬀ",
    "ffi": "ﬃ",
    "ffl": "ﬄ",
    "FFrancSign": "₣",
    "fi": "ﬁ",
    "figuredash": "‒",
    "filledbox": "■",
    "filledrect": "▬",
    "five": "5",
    "fiveeighths": "⅝",
    "fiveinferior": "₅",
    "fiveoldstyle": "",
    "fivesubscript": "₅",
    "fivesuperior": "⁵",
    "fl": "ﬂ",
    "florin": "ƒ",
    "four": "4",
    "fourinferior": "₄",
    "fouroldstyle": "",
    "foursubscript": "₄",
    "foursuperior": "⁴",
    "fraction": "∕",
    "franc": "₣",
    "Fsmall": "",
    "function": "ƒ",
    "Gamma": "Γ",
    "gamma": "γ",
    "Gbreve": "Ğ",
    "gbreve": "ğ",
    "Gcaron": "Ǧ",
    "gcaron": "ǧ",
    "Gcircumflex": "Ĝ",
    "gcircumflex": "ĝ",
    "Gcommaaccent": "Ģ",
    "gcommaaccent": "ģ",
    "Gdotaccent": "Ġ",
    "gdotaccent": "ġ",
    "germandbls": "ß",
    "gradient": "∇",
    "grave": "`",
    "Grave": "",
    "gravecomb": "̀",
    "Gravesmall": "",
    "greater": ">",
    "greaterequal": "≥",
    "Gsmall": "",
    "guillemotleft": "«",
    "guillemotright": "»",
    "guilsinglleft": "‹",
    "guilsinglright": "›",
    "H18533": "●",
    "H18543": "▪",
    "H18551": "▫",
    "H22073": "□",
    "hash": "#",
    "hashtag": "#",
    "Hbar": "Ħ",
    "hbar": "ħ",
    "Hcircumflex": "Ĥ",
    "hcircumflex": "ĥ",
    "heart": "♥",
    "hookabovecomb": "̉",
    "house": "⌂",
    "Hsmall": "",
    "hungarumlaut": "˝",
    "Hungarumlaut": "",
    "Hungarumlautsmall": "",
    "hyphen": "­",
    "hypheninferior": "",
    "hyphensuperior": "",
    "Iacute": "Í",
    "iacute": "í",
    "Iacutesmall": "",
    "Ibreve": "Ĭ",
    "ibreve": "ĭ",
    "Icircumflex": "Î",
    "icircumflex": "î",
    "Icircumflexsmall": "",
    "Idiaeresis": "Ï",
    "idiaeresis": "ï",
    "Idieresis": "Ï",
    "idieresis": "ï",
    "Idieresissmall": "",
    "Idotaccent": "İ",
    "Ifraktur": "ℑ",
    "Igrave": "Ì",
    "igrave": "ì",
    "Igravesmall": "",
    "IJ": "Ĳ",
    "ij": "ĳ",
    "Imacron": "Ī",
    "imacron": "ī",
    "infinity": "∞",
    "integral": "∫",
    "integralbt": "⌡",
    "integralex": "",
    "integraltp": "⌠",
    "intersection": "∩",
    "invbullet": "◘",
    "invcircle": "◙",
    "invsmileface": "☻",
    "Iogonek": "Į",
    "iogonek": "į",
    "Iota": "Ι",
    "iota": "ι",
    "Iotadieresis": "Ϊ",
    "iotadieresis": "ϊ",
    "iotadieresistonos": "ΐ",
    "Iotatonos": "Ί",
    "iotatonos": "ί",
    "Ismall": "",
    "isuperior": "",
    "Itilde": "Ĩ",
    "itilde": "ĩ",
    "Jcircumflex": "Ĵ",
    "jcircumflex": "ĵ",
    "Jsmall": "",
    "Kappa": "Κ",
    "kappa": "κ",
    "Kcommaaccent": "Ķ",
    "kcommaaccent": "ķ",
    "kgreenlandic": "ĸ",
    "Ksmall": "",
    "Lacute": "Ĺ",
    "lacute": "ĺ",
    "Lambda": "Λ",
    "lambda": "λ",
    "Lcaron": "Ľ",
    "lcaron": "ľ",
    "Lcommaaccent": "Ļ",
    "lcommaaccent": "ļ",
    "Ldot": "Ŀ",
    "ldot": "ŀ",
    "less": "<",
    "lessequal": "≤",
    "lfblock": "▌",
    "lira": "₤",
    "LiraSign": "₤",
    "LL": "",
    "ll": "",
    "logicaland": "∧",
    "logicalnot": "¬",
    "logicalor": "∨",
    "longs": "ſ",
    "lozenge": "◊",
    "Lslash": "Ł",
    "lslash": "ł",
    "Lslashsmall": "",
    "Lsmall": "",
    "lsuperior": "",
    "ltshade": "░",
    "macron": "¯",
    "macron": "ˉ",
    "Macron": "",
    "Macronsmall": "",
    "male": "♂",
    "masculine": "º",
    "MillSign": "₥",
    "minplus": "+",
    "minus": "-",
    "minus": "−",
    "minute": "′",
    "Msmall": "",
    "msuperior": "",
    "mu": "µ",
    "Mu": "Μ",
    "mu": "μ",
    "multiply": "*",
    "multiply": "×",
    "musicalnote": "♪",
    "musicalnotedbl": "♫",
    "Nacute": "Ń",
    "nacute": "ń",
    "NairaSign": "₦",
    "napostrophe": "ŉ",
    "Ncaron": "Ň",
    "ncaron": "ň",
    "Ncommaaccent": "Ņ",
    "ncommaaccent": "ņ",
    "NewSheqelSign": "₪",
    "nine": "9",
    "nineinferior": "₉",
    "nineoldstyle": "",
    "ninesubscript": "₉",
    "ninesuperior": "⁹",
    "nobreakspace": " ",
    "notelement": "∉",
    "notequal": "≠",
    "notsign": "¬",
    "notsubset": "⊄",
    "Nsmall": "",
    "nsuperior": "ⁿ",
    "Ntilde": "Ñ",
    "ntilde": "ñ",
    "Ntildesmall": "",
    "Nu": "Ν",
    "nu": "ν",
    "numbersign": "#",
    "numerosign": "№",
    "Oacute": "Ó",
    "oacute": "ó",
    "Oacutesmall": "",
    "Obreve": "Ŏ",
    "obreve": "ŏ",
    "Ocircumflex": "Ô",
    "ocircumflex": "ô",
    "Ocircumflexacute": "Ố",
    "ocircumflexacute": "ố",
    "Ocircumflexbelowdot": "Ộ",
    "ocircumflexbelowdot": "ộ",
    "Ocircumflexgrave": "Ồ",
    "ocircumflexgrave": "ồ",
    "Ocircumflexhook": "Ổ",
    "ocircumflexhook": "ổ",
    "Ocircumflexsmall": "",
    "Ocircumflextilde": "Ỗ",
    "ocircumflextilde": "ỗ",
    "Odiaeresis": "Ö",
    "odiaeresis": "ö",
    "Odieresis": "Ö",
    "odieresis": "ö",
    "Odieresissmall": "",
    "oe": "œ",
    "OE": "Œ",
    "OEsmall": "",
    "ogonek": "˛",
    "Ogoneksmall": "",
    "Ograve": "Ò",
    "ograve": "ò",
    "Ogravesmall": "",
    "Ohorn": "Ơ",
    "ohorn": "ơ",
    "Ohornacute": "Ớ",
    "ohornacute": "ớ",
    "Ohornbelowdot": "Ợ",
    "ohornbelowdot": "ợ",
    "Ohorngrave": "Ờ",
    "ohorngrave": "ờ",
    "Ohornhook": "Ở",
    "ohornhook": "ở",
    "Ohorntilde": "Ỡ",
    "ohorntilde": "ỡ",
    "Ohungarumlaut": "Ő",
    "ohungarumlaut": "ő",
    "Omacron": "Ō",
    "omacron": "ō",
    "Omega": "Ω",
    "omega": "ω",
    "omega1": "ϖ",
    "Omegatonos": "Ώ",
    "omegatonos": "ώ",
    "Omicron": "Ο",
    "omicron": "ο",
    "Omicrontonos": "Ό",
    "omicrontonos": "ό",
    "one": "1",
    "onedotenleader": "․",
    "oneeighth": "⅛",
    "onefitted": "",
    "onehalf": "½",
    "oneinferior": "₁",
    "oneoldstyle": "",
    "onequarter": "¼",
    "onesubscript": "₁",
    "onesuperior": "¹",
    "onethird": "⅓",
    "openbullet": "◦",
    "ordfeminine": "ª",
    "ordmasculine": "º",
    "orthogonal": "∟",
    "Oslash": "Ø",
    "oslash": "ø",
    "Oslashacute": "Ǿ",
    "oslashacute": "ǿ",
    "Oslashsmall": "",
    "Osmall": "",
    "osuperior": "",
    "Otilde": "Õ",
    "otilde": "õ",
    "Otildesmall": "",
    "paragraph": "¶",
    "parenleft": "(",
    "parenleftbt": "",
    "parenleftex": "",
    "parenleftinferior": "₍",
    "parenleftsuperior": "⁽",
    "parenlefttp": "",
    "parenright": ")",
    "parenrightbt": "",
    "parenrightex": "",
    "parenrightinferior": "₎",
    "parenrightsuperior": "⁾",
    "parenrighttp": "",
    "partialdiff": "∂",
    "percent": "%",
    "period": ".",
    "periodcentered": "·",
    "periodcentered": "∙",
    "periodinferior": "",
    "periodsuperior": "",
    "perpendicular": "⊥",
    "perthousand": "‰",
    "peseta": "₧",
    "PesetaSign": "₧",
    "Phi": "Φ",
    "phi": "φ",
    "phi1": "ϕ",
    "Pi": "Π",
    "pi": "π",
    "plus": "+",
    "plusminus": "±",
    "pound": "£",
    "prescription": "℞",
    "product": "∏",
    "propersubset": "⊂",
    "propersuperset": "⊃",
    "proportional": "∝",
    "Psi": "Ψ",
    "psi": "ψ",
    "Psmall": "",
    "Qsmall": "",
    "question": "?",
    "questiondown": "¿",
    "questiondownsmall": "",
    "questionsmall": "",
    "quotedbl": '"',
    "quotedblbase": "„",
    "quotedblleft": "“",
    "quotedblright": "”",
    "quoteleft": "‘",
    "quotereversed": "‛",
    "quoteright": "’",
    "quotesinglbase": "‚",
    "quotesingle": "'",
    "Racute": "Ŕ",
    "racute": "ŕ",
    "radical": "√",
    "radicalex": "",
    "Rcaron": "Ř",
    "rcaron": "ř",
    "Rcommaaccent": "Ŗ",
    "rcommaaccent": "ŗ",
    "reflexsubset": "⊆",
    "reflexsuperset": "⊇",
    "registered": "®",
    "registersans": "",
    "registerserif": "",
    "revlogicalnot": "⌐",
    "Rfraktur": "ℜ",
    "Rho": "Ρ",
    "rho": "ρ",
    "ring": "˚",
    "Ringsmall": "",
    "Rsmall": "",
    "rsuperior": "",
    "rtblock": "▐",
    "RupeeSign": "₨",
    "rupiah": "",
    "Sacute": "Ś",
    "sacute": "ś",
    "Scaron": "Š",
    "scaron": "š",
    "Scaronsmall": "",
    "Scedilla": "",
    "scedilla": "",
    "Scircumflex": "Ŝ",
    "scircumflex": "ŝ",
    "Scommaaccent": "Ș",
    "scommaaccent": "ș",
    "second": "″",
    "section": "§",
    "semicolon": ";",
    "seven": "7",
    "seveneighths": "⅞",
    "seveninferior": "₇",
    "sevenoldstyle": "",
    "sevensubscript": "₇",
    "sevensuperior": "⁷",
    "SF010000": "┌",
    "SF020000": "└",
    "SF030000": "┐",
    "SF040000": "┘",
    "SF050000": "┼",
    "SF060000": "┬",
    "SF070000": "┴",
    "SF080000": "├",
    "SF090000": "┤",
    "SF100000": "─",
    "SF110000": "│",
    "SF190000": "╡",
    "SF200000": "╢",
    "SF210000": "╖",
    "SF220000": "╕",
    "SF230000": "╣",
    "SF240000": "║",
    "SF250000": "╗",
    "SF260000": "╝",
    "SF270000": "╜",
    "SF280000": "╛",
    "SF360000": "╞",
    "SF370000": "╟",
    "SF380000": "╚",
    "SF390000": "╔",
    "SF400000": "╩",
    "SF410000": "╦",
    "SF420000": "╠",
    "SF430000": "═",
    "SF440000": "╬",
    "SF450000": "╧",
    "SF460000": "╨",
    "SF470000": "╤",
    "SF480000": "╥",
    "SF490000": "╙",
    "SF500000": "╘",
    "SF510000": "╒",
    "SF520000": "╓",
    "SF530000": "╫",
    "SF540000": "╪",
    "shade": "▒",
    "Sigma": "Σ",
    "sigma": "σ",
    "sigma1": "ς",
    "similar": "∼",
    "similarequal": "≃",
    "six": "6",
    "sixinferior": "₆",
    "sixoldstyle": "",
    "sixsubscript": "₆",
    "sixsuperior": "⁶",
    "slash": "/",
    "smileface": "☺",
    "spade": "♠",
    "ssharp": "§",
    "ssharp": "ß",
    "Ssharp": "ẞ",
    "Ssmall": "",
    "ssuperior": "",
    "sterling": "£",
    "subtract": "-",
    "suchthat": "∋",
    "summation": "∑",
    "sun": "☼",
    "Tau": "Τ",
    "tau": "τ",
    "Tbar": "Ŧ",
    "tbar": "ŧ",
    "Tcaron": "Ť",
    "tcaron": "ť",
    "Tcommaaccent": "Ț",
    "tcommaaccent": "ț",
    "Thai_baht": "฿",
    "therefore": "∴",
    "Theta": "Θ",
    "theta": "θ",
    "theta1": "ϑ",
    "THORN": "Þ",
    "thorn": "þ",
    "Thorn": "Þ",
    "Thornsmall": "",
    "three": "3",
    "threeeighths": "⅜",
    "threeinferior": "₃",
    "threeoldstyle": "",
    "threequarters": "¾",
    "threequartersemdash": "",
    "threesubscript": "₃",
    "threesuperior": "³",
    "til": "~",
    "tilde": "~",
    "tilde": "˜",
    "tildecomb": "̃",
    "Tildesmall": "",
    "tonos": "΄",
    "trademark": "™",
    "trademarksans": "",
    "trademarkserif": "",
    "triagdn": "▼",
    "triaglf": "◄",
    "triagrt": "►",
    "triagup": "▲",
    "Tsmall": "",
    "tsuperior": "",
    "two": "2",
    "twodotenleader": "‥",
    "twoinferior": "₂",
    "twooldstyle": "",
    "twosubscript": "₂",
    "twosuperior": "²",
    "twothirds": "⅔",
    "Uacute": "Ú",
    "uacute": "ú",
    "Uacutesmall": "",
    "Ubreve": "Ŭ",
    "ubreve": "ŭ",
    "Ucircumflex": "Û",
    "ucircumflex": "û",
    "Ucircumflexsmall": "",
    "Udiaeresis": "Ü",
    "udiaeresis": "ü",
    "Udieresis": "Ü",
    "udieresis": "ü",
    "Udieresissmall": "",
    "Ugrave": "Ù",
    "ugrave": "ù",
    "Ugravesmall": "",
    "Uhorn": "Ư",
    "uhorn": "ư",
    "Uhornacute": "Ứ",
    "uhornacute": "ứ",
    "Uhornbelowdot": "Ự",
    "uhornbelowdot": "ự",
    "Uhorngrave": "Ừ",
    "uhorngrave": "ừ",
    "Uhornhook": "Ử",
    "uhornhook": "ử",
    "Uhorntilde": "Ữ",
    "uhorntilde": "ữ",
    "Uhungarumlaut": "Ű",
    "uhungarumlaut": "ű",
    "Umacron": "Ū",
    "umacron": "ū",
    "underscore": "_",
    "underscoredbl": "‗",
    "union": "∪",
    "universal": "∀",
    "Uogonek": "Ų",
    "uogonek": "ų",
    "upblock": "▀",
    "Upsilon": "Υ",
    "upsilon": "υ",
    "Upsilon1": "ϒ",
    "Upsilondieresis": "Ϋ",
    "upsilondieresis": "ϋ",
    "upsilondieresistonos": "ΰ",
    "Upsilontonos": "Ύ",
    "upsilontonos": "ύ",
    "Uring": "Ů",
    "uring": "ů",
    "Usmall": "",
    "Utilde": "Ũ",
    "utilde": "ũ",
    "Vsmall": "",
    "Wacute": "Ẃ",
    "wacute": "ẃ",
    "Wcircumflex": "Ŵ",
    "wcircumflex": "ŵ",
    "Wdieresis": "Ẅ",
    "wdieresis": "ẅ",
    "weierstrass": "℘",
    "Wgrave": "Ẁ",
    "wgrave": "ẁ",
    "WonSign": "₩",
    "Wsmall": "",
    "Xi": "Ξ",
    "xi": "ξ",
    "Xsmall": "",
    "Yacute": "Ý",
    "yacute": "ý",
    "Yacutesmall": "",
    "Ycircumflex": "Ŷ",
    "ycircumflex": "ŷ",
    "ydiaeresis": "ÿ",
    "Ydieresis": "Ÿ",
    "ydieresis": "ÿ",
    "Ydieresissmall": "",
    "yen": "¥",
    "Ygrave": "Ỳ",
    "ygrave": "ỳ",
    "Ysmall": "",
    "Zacute": "Ź",
    "zacute": "ź",
    "Zcaron": "Ž",
    "zcaron": "ž",
    "Zcaronsmall": "",
    "Zdotaccent": "Ż",
    "zdotaccent": "ż",
    "zero": "0",
    "zeroinferior": "₀",
    "zerooldstyle": "",
    "zerosubscript": "₀",
    "zerosuperior": "⁰",
    "zeta": "ζ",
    "Zeta": "Ζ",
    "Zsmall": "",
}
sided_modifiers = {"ctrl", "alt", "shift", "windows"}
all_modifiers = (
    {"alt", "alt gr", "ctrl", "shift", "windows"}
    | set("left " + n for n in sided_modifiers)
    | set("right " + n for n in sided_modifiers)
)

# Platform-specific canonical overrides

if platform.system() == "Darwin":
    canonical_names.update(
        {
            "command": "command",
            "windows": "command",
            "cmd": "command",
            "win": "command",
            "backspace": "delete",
            "alt gr": "alt",  # Issue #117
        }
    )
    all_modifiers = {"alt", "ctrl", "shift", "windows"}
if platform.system() == "Linux":
    canonical_names.update(
        {
            "select": "end",
            "find": "home",
            "next": "page down",
            "prior": "page up",
        }
    )


def normalize_name(name):
    """
    Given a key name (e.g. "LEFT CONTROL"), clean up the string and convert to
    the canonical representation (e.g. "left ctrl") if one is known.
    """
    if not name or not isinstance(name, basestring):
        raise ValueError("Can only normalize non-empty string names. Unexpected " + repr(name))

    if len(name) > 1:
        name = name.lower()
    if name != "_" and "_" in name:
        name = name.replace("_", " ")

    return canonical_names.get(name, name)
