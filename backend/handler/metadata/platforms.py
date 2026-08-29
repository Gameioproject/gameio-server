"""Universal platform slugs and their IGDB platform records. Pure data: no clients, no models."""

import enum
from typing import TypedDict


class UniversalPlatformSlug(enum.StrEnum):
    _3DO = "3do"
    ABC_80 = "abc-80"
    ACORN_ARCHIMEDES = "acorn-archimedes"
    ACORN_ELECTRON = "acorn-electron"
    ACPC = "acpc"
    ACTION_MAX = "action-max"
    ADVANCED_PICO_BEENA = "advanced-pico-beena"
    ADVENTURE_VISION = "adventure-vision"
    AIRCONSOLE = "airconsole"
    ALICE_3290 = "alice-3290"
    ALTAIR_680 = "altair-680"
    ALTAIR_8800 = "altair-8800"
    AMAZON_ALEXA = "amazon-alexa"
    AMAZON_FIRE_TV = "amazon-fire-tv"
    AMIGA = "amiga"
    AMIGA_CD = "amiga-cd"
    AMIGA_CD32 = "amiga-cd32"
    AMSTRAD_GX4000 = "amstrad-gx4000"
    AMSTRAD_PCW = "amstrad-pcw"
    ANALOGUEELECTRONICS = "analogueelectronics"
    ANDROID = "android"
    ANTSTREAM = "antstream"
    APF = "apf"
    APPLE = "apple"
    APPLE_IIGS = "apple-iigs"
    APPLE_LISA = "apple-lisa"
    APPLE_PIPPIN = "apple-pippin"
    APPLEII = "appleii"
    APPLEIII = "appleiii"
    APVS = "1292-advanced-programmable-video-system"
    AQUARIUS = "aquarius"
    ARCADE = "arcade"
    ARCADIA_2001 = "arcadia-2001"
    ARDUBOY = "arduboy"
    ASTRAL_2000 = "astral-2000"
    ASTROCADE = "astrocade"
    ATARI_JAGUAR_CD = "atari-jaguar-cd"
    ATARI_ST = "atari-st"
    ATARI_VCS = "atari-vcs"
    ATARI_XEGS = "atari-xegs"
    ATARI2600 = "atari2600"
    ATARI5200 = "atari5200"
    ATARI7800 = "atari7800"
    ATARI800 = "atari800"
    ATARI8BIT = "atari8bit"
    ATMOS = "atmos"
    ATOM = "atom"
    AY_3_8500 = "ay-3-8500"
    AY_3_8603 = "ay-3-8603"
    AY_3_8605 = "ay-3-8605"
    AY_3_8606 = "ay-3-8606"
    AY_3_8607 = "ay-3-8607"
    AY_3_8610 = "ay-3-8610"
    AY_3_8710 = "ay-3-8710"
    AY_3_8760 = "ay-3-8760"
    BADA = "bada"
    BBCMICRO = "bbcmicro"
    BEENA = "beena"
    BEOS = "beos"
    BIT_90 = "bit-90"
    BK = "bk"
    BK_01 = "bk-01"
    BLACK_POINT = "black-point"
    BLACKBERRY = "blackberry"
    BLACKNUT = "blacknut"
    BLU_RAY_PLAYER = "blu-ray-player"
    BREW = "brew"
    BROWSER = "browser"
    BUBBLE = "bubble"
    C_PLUS_4 = "c-plus-4"
    C128 = "c128"
    C16 = "c16"
    C64 = "c64"
    CALL_A_COMPUTER = "call-a-computer"
    CAMPUTERS_LYNX = "camputers-lynx"
    CASIO_CFX_9850 = "casio-cfx-9850"
    CASIO_FP_1000 = "casio-fp-1000"
    CASIO_LOOPY = "casio-loopy"
    CASIO_PB_1000 = "casio-pb-1000"
    CASIO_PROGRAMMABLE_CALCULATOR = "casio-programmable-calculator"
    CASIO_PV_1000 = "casio-pv-1000"
    CASIO_PV_2000 = "casio-pv-2000"
    CDCCYBER70 = "cdccyber70"
    CHAMPION_2711 = "champion-2711"
    CLICKSTART = "clickstart"
    COLECOADAM = "colecoadam"
    COLECOVISION = "colecovision"
    COLOUR_GENIE = "colour-genie"
    COMMANDER_X16 = "commander-x16"
    COMMODORE_CDTV = "commodore-cdtv"
    COMPAL_80 = "compal-80"
    COMPUCOLOR_I = "compucolor-i"
    COMPUCOLOR_II = "compucolor-ii"
    COMPUCORP_PROGRAMMABLE_CALCULATOR = "compucorp-programmable-calculator"
    CPET = "cpet"
    CPS1 = "cps1"
    CPS2 = "cps2"
    CPS3 = "cps3"
    CPM = "cpm"
    CREATIVISION = "creativision"
    CYBERVISION = "cybervision"
    DANGER_OS = "danger-os"
    DAYDREAM = "daydream"
    DC = "dc"
    DEDICATED_CONSOLE = "dedicated-console"
    DEDICATED_HANDHELD = "dedicated-handheld"
    DIDJ = "didj"
    DIGIBLAST = "digiblast"
    DOJA = "doja"
    DONNER30 = "donner30"
    DOS = "dos"
    DRAGON_32_SLASH_64 = "dragon-32-slash-64"
    DVD_PLAYER = "dvd-player"
    E_READER_SLASH_CARD_E_READER = "e-reader-slash-card-e-reader"
    ECD_MICROMIND = "ecd-micromind"
    EDSAC = "edsac"
    ELEKTOR = "elektor"
    ENTERPRISE = "enterprise"
    EPOCH_CASSETTE_VISION = "epoch-cassette-vision"
    EPOCH_GAME_POCKET_COMPUTER = "epoch-game-pocket-computer"
    EPOCH_SUPER_CASSETTE_VISION = "epoch-super-cassette-vision"
    EVERCADE = "evercade"
    EXCALIBUR_64 = "excalibur-64"
    EXELVISION = "exelvision"
    EXEN = "exen"
    EXIDY_SORCERER = "exidy-sorcerer"
    FAIRCHILD_CHANNEL_F = "fairchild-channel-f"
    FAMICOM = "famicom"
    FDS = "fds"
    FM_7 = "fm-7"
    FM_TOWNS = "fm-towns"
    FRED_COSMAC = "fred-cosmac"
    FREEBOX = "freebox"
    G_AND_W = "g-and-w"
    G_CLUSTER = "g-cluster"
    GALAKSIJA = "galaksija"
    GAMATE = "gamate"
    GAME_DOT_COM = "game-dot-com"
    GAME_WAVE = "game-wave"
    GAMEGEAR = "gamegear"
    GAMESTICK = "gamestick"
    GB = "gb"
    GBA = "gba"
    GBC = "gbc"
    GEAR_VR = "gear-vr"
    GENESIS = "genesis"
    GIMINI = "gimini"
    GIZMONDO = "gizmondo"
    GLOUD = "gloud"
    GLULX = "glulx"
    GNEX = "gnex"
    GP2X = "gp2x"
    GP2X_WIZ = "gp2x-wiz"
    GP32 = "gp32"
    GT40 = "gt40"
    GVM = "gvm"
    HANDHELD_ELECTRONIC_LCD = "handheld-electronic-lcd"
    HARTUNG = "hartung"
    HD_DVD_PLAYER = "hd-dvd-player"
    HEATHKIT_H11 = "heathkit-h11"
    HEATHZENITH = "heathzenith"
    HIKARU = "hikaru"
    HITACHI_S1 = "hitachi-s1"
    HP_9800 = "hp-9800"
    HP_PROGRAMMABLE_CALCULATOR = "hp-programmable-calculator"
    HP2100 = "hp2100"
    HP3000 = "hp3000"
    HRX = "hrx"
    HUGO = "hugo"
    HYPER_NEO_GEO_64 = "hyper-neo-geo-64"
    HYPERSCAN = "hyperscan"
    IBM_5100 = "ibm-5100"
    IDEAL_COMPUTER = "ideal-computer"
    IIRCADE = "iircade"
    IMLAC_PDS1 = "imlac-pds1"
    INTEL_8008 = "intel-8008"
    INTEL_8080 = "intel-8080"
    INTEL_8086 = "intel-8086"
    INTELLIVISION = "intellivision"
    INTELLIVISION_AMICO = "intellivision-amico"
    INTERACT_MODEL_ONE = "interact-model-one"
    INTERTON_VC_4000 = "interton-vc-4000"
    INTERTON_VIDEO_2000 = "interton-video-2000"
    IOS = "ios"
    IPAD = "ipad"
    IPOD_CLASSIC = "ipod-classic"
    J2ME = "j2me"
    JAGUAR = "jaguar"
    JOLT = "jolt"
    JUPITER_ACE = "jupiter-ace"
    KAIOS = "kaios"
    KIM_1 = "kim-1"
    KINDLE = "kindle"
    LASER200 = "laser200"
    LASERACTIVE = "laseractive"
    LEAPFROG_EXPLORER = "leapfrog-explorer"
    LEAPSTER = "leapster"
    LEAPSTER_EXPLORER_SLASH_LEADPAD_EXPLORER = (
        "leapster-explorer-slash-leadpad-explorer"
    )
    LEAPTV = "leaptv"
    LEGACY_COMPUTER = "legacy-computer"
    LINUX = "linux"
    LUNA = "luna"
    LYNX = "lynx"
    MAC = "mac"
    MAEMO = "maemo"
    MAINFRAME = "mainframe"
    MATSUSHITAPANASONIC_JR = "matsushitapanasonic-jr"
    MEEGO = "meego"
    MEGA_DUCK_SLASH_COUGAR_BOY = "mega-duck-slash-cougar-boy"
    MEMOTECH_MTX = "memotech-mtx"
    MERITUM = "meritum"
    META_QUEST_2 = "meta-quest-2"
    META_QUEST_3 = "meta-quest-3"
    MICROBEE = "microbee"
    MICROCOMPUTER = "microcomputer"
    MICROTAN_65 = "microtan-65"
    MICROVISION = "microvision"
    MOBILE = "mobile"
    MOBILE_CUSTOM = "mobile-custom"
    MODEL1 = "model1"
    MODEL2 = "model2"
    MODEL3 = "model3"
    MOPHUN = "mophun"
    MOS_TECHNOLOGY_6502 = "mos-technology-6502"
    MOTOROLA_6800 = "motorola-6800"
    MOTOROLA_68K = "motorola-68k"
    MRE = "mre"
    MSX = "msx"
    MSX_TURBO = "msx-turbo"
    MSX2 = "msx2"
    MSX2PLUS = "msx2plus"
    MTX512 = "mtx512"
    MUGEN = "mugen"
    MULTIVISION = "multivision"
    N3DS = "3ds"
    N64 = "n64"
    N64DD = "64dd"
    NASCOM = "nascom"
    NDS = "nds"
    NEC_PC_6000_SERIES = "nec-pc-6000-series"
    NEO_GEO_CD = "neo-geo-cd"
    NEO_GEO_POCKET = "neo-geo-pocket"
    NEO_GEO_POCKET_COLOR = "neo-geo-pocket-color"
    NEO_GEO_X = "neo-geo-x"
    NEOGEOAES = "neogeoaes"
    NEOGEOMVS = "neogeomvs"
    NES = "nes"
    NEW_NINTENDON3DS = "new-nintendo-3ds"
    NEWBRAIN = "newbrain"
    NEWTON = "newton"
    NGAGE = "ngage"
    NGAGE2 = "ngage2"
    NGC = "ngc"
    NIMROD = "nimrod"
    NINTENDO_DSI = "nintendo-dsi"
    NORTHSTAR = "northstar"
    NOVAL_760 = "noval-760"
    NUON = "nuon"
    OCULUS_GO = "oculus-go"
    OCULUS_QUEST = "oculus-quest"
    OCULUS_RIFT = "oculus-rift"
    OCULUS_VR = "oculus-vr"
    ODYSSEY = "odyssey"
    ODYSSEY_2 = "odyssey-2"
    OHIO_SCIENTIFIC = "ohio-scientific"
    ONLIVE_GAME_SYSTEM = "onlive-game-system"
    OOPARTS = "ooparts"
    OPENBOR = "openbor"
    ORAO = "orao"
    ORIC = "oric"
    OS2 = "os2"
    OUYA = "ouya"
    PALM_OS = "palm-os"
    PALMTEX = "palmtex"
    PANASONIC_JUNGLE = "panasonic-jungle"
    PANASONIC_M2 = "panasonic-m2"
    PANDORA = "pandora"
    PC_50X_FAMILY = "pc-50x-family"
    PC_6001 = "pc-6001"
    PC_8000 = "pc-8000"
    PC_8800_SERIES = "pc-8800-series"
    PC_9800_SERIES = "pc-9800-series"
    PC_BOOTER = "pc-booter"
    PC_FX = "pc-fx"
    PC_JR = "pc-jr"
    PDP_7 = "pdp-7"
    PDP_8 = "pdp-8"
    PDP1 = "pdp1"
    PDP10 = "pdp10"
    PDP11 = "pdp11"
    PEBBLE = "pebble"
    PEGASUS = "pegasus"
    PHILIPS_CD_I = "philips-cd-i"
    PHILIPS_VG_5000 = "philips-vg-5000"
    PHOTOCD = "photocd"
    PICO = "pico"
    PINBALL = "pinball"
    PIPPIN = "pippin"
    PLATO = "plato"
    PLAYDATE = "playdate"
    PLAYDIA = "playdia"
    PLAYSTATION_NOW = "playstation-now"
    PLEX_ARCADE = "plex-arcade"
    PLUG_AND_PLAY = "plug-and-play"
    POCKET_CHALLENGE_V2 = "pocket-challenge-v2"
    POCKET_CHALLENGE_W = "pocket-challenge-w"
    POCKETSTATION = "pocketstation"
    POKEMON_MINI = "pokemon-mini"
    POKITTO = "pokitto"
    POLY_88 = "poly-88"
    POLYMEGA = "polymega"
    PS2 = "ps2"
    PS3 = "ps3"
    PS4 = "ps4"
    PS5 = "ps5"
    PSP = "psp"
    PSP_MINIS = "psp-minis"
    PSVITA = "psvita"
    PSVR = "psvr"
    PSVR2 = "psvr2"
    PSX = "psx"
    R_ZONE = "r-zone"
    RCA_STUDIO_II = "rca-studio-ii"
    RESEARCH_MACHINES_380Z = "research-machines-380z"
    ROKU = "roku"
    SAM_COUPE = "sam-coupe"
    SATELLAVIEW = "satellaview"
    SATURN = "saturn"
    SC3000 = "sc3000"
    SCMP = "scmp"
    SCUMMVM = "scummvm"
    SD_200270290 = "sd-200270290"
    SDSSIGMA7 = "sdssigma7"
    SEGA_PICO = "sega-pico"
    SEGA32 = "sega32"
    SEGACD = "segacd"
    SEGACD32 = "segacd32"
    SERIES_X_S = "series-x-s"
    SFAM = "sfam"
    SG1000 = "sg1000"
    SHARP_MZ_2200 = "sharp-mz-2200"
    SHARP_MZ_80B20002500 = "sharp-mz-80b20002500"
    SHARP_MZ_80K7008001500 = "sharp-mz-80k7008001500"
    SHARP_X68000 = "sharp-x68000"
    SHARP_ZAURUS = "sharp-zaurus"
    SIGNETICS_2650 = "signetics-2650"
    SINCLAIR_QL = "sinclair-ql"
    SK_VM = "sk-vm"
    SMC_777 = "smc-777"
    SMS = "sms"
    SNES = "snes"
    SOCRATES = "socrates"
    SOL_20 = "sol-20"
    SORD_M5 = "sord-m5"
    SPECTRAVIDEO = "spectravideo"
    SRI_5001000 = "sri-5001000"
    STADIA = "stadia"
    STEAM = "steam"
    STEAM_VR = "steam-vr"
    STV = "stv"
    SUFAMI_TURBO = "sufami-turbo"
    SUPER_ACAN = "super-acan"
    SUPER_NES_CD_ROM_SYSTEM = "super-nes-cd-rom-system"
    SUPER_VISION_8000 = "super-vision-8000"
    SUPERGRAFX = "supergrafx"
    SUPERVISION = "supervision"
    SURE_SHOT_HD = "sure-shot-hd"
    SWANCRYSTAL = "swancrystal"
    SWITCH = "switch"
    SWITCH_2 = "switch-2"
    SWTPC_6800 = "swtpc-6800"
    SYMBIAN = "symbian"
    SYSTEM_32 = "system-32"
    SYSTEM16 = "system16"
    SYSTEM32 = "system32"
    TADS = "tads"
    TAITO_X_55 = "taito-x-55"
    TANDY_VIS = "tandy-vis"
    TATUNG_EINSTEIN = "tatung-einstein"
    TEKTRONIX_4050 = "tektronix-4050"
    TELE_SPIEL = "tele-spiel"
    TELSTAR_ARCADE = "telstar-arcade"
    TEREBIKKO_SLASH_SEE_N_SAY_VIDEO_PHONE = "terebikko-slash-see-n-say-video-phone"
    TERMINAL = "terminal"
    TG16 = "tg16"
    THOMSON_MO5 = "thomson-mo5"
    THOMSON_TO = "thomson-to"
    TI_82 = "ti-82"
    TI_83 = "ti-83"
    TI_99 = "ti-99"
    TI_994A = "ti-994a"
    TI_PROGRAMMABLE_CALCULATOR = "ti-programmable-calculator"
    TIC_80 = "tic-80"
    TIKI_100 = "tiki-100"
    TIM = "tim"
    TIMEX_SINCLAIR_2068 = "timex-sinclair-2068"
    TIZEN = "tizen"
    TOMAHAWK_F1 = "tomahawk-f1"
    TOMY_TUTOR = "tomy-tutor"
    TOMY_TUTOR_SLASH_PYUTA_SLASH_GRANDSTAND_TUTOR = (
        "tomy-tutor-slash-pyuta-slash-grandstand-tutor"
    )
    TRITON = "triton"
    TRS_80 = "trs-80"
    TRS_80_COLOR_COMPUTER = "trs-80-color-computer"
    TRS_80_MC_10 = "trs-80-mc-10"
    TRS_80_MODEL_100 = "trs-80-model-100"
    TURBOGRAFX_CD = "turbografx-cd"
    TVOS = "tvos"
    TYPE_X = "type-x"
    UZEBOX = "uzebox"
    VC = "vc"
    VC_4000 = "vc-4000"
    VECTOR_06C = "06c"
    VECTREX = "vectrex"
    VERSATILE = "versatile"
    VFLASH = "vflash"
    VIC_20 = "vic-20"
    VIDEOBRAIN = "videobrain"
    VIDEOPAC_G7400 = "videopac-g7400"
    VIRTUALBOY = "virtualboy"
    VIS = "vis"
    VISIONOS = "visionos"
    VISUAL_MEMORY_UNIT_SLASH_VISUAL_MEMORY_SYSTEM = (
        "visual-memory-unit-slash-visual-memory-system"
    )
    VMU = "vmu"
    VSMILE = "vsmile"
    WANG2200 = "wang2200"
    WASM_4 = "wasm-4"
    WATCHOS = "watchos"
    WEBOS = "webos"
    WII = "wii"
    WIIU = "wiiu"
    WIN = "win"
    WIN3X = "win3x"
    WIN9X = "win9x"
    WINDOWS_APPS = "windows-apps"
    WINDOWS_MIXED_REALITY = "windows-mixed-reality"
    WINDOWS_MOBILE = "windows-mobile"
    WINPHONE = "winphone"
    WIPI = "wipi"
    WONDERSWAN = "wonderswan"
    WONDERSWAN_COLOR = "wonderswan-color"
    X1 = "x1"
    XAVIXPORT = "xavixport"
    XBOX = "xbox"
    XBOX360 = "xbox360"
    XBOXCLOUDGAMING = "xboxcloudgaming"
    XBOXONE = "xboxone"
    XEROX_ALTO = "xerox-alto"
    Z_MACHINE = "z-machine"
    Z80 = "z80"
    Z88 = "z88"
    ZEEBO = "zeebo"
    ZILOG_Z8000 = "zilog-z8000"
    ZINC = "zinc"
    ZOD = "zod"
    ZODIAC = "zodiac"
    ZUNE = "zune"
    ZX_SPECTRUM_NEXT = "zx-spectrum-next"
    ZX80 = "zx80"
    ZX81 = "zx81"
    ZXS = "zxs"


UPS = UniversalPlatformSlug


class SlugToIGDB(TypedDict):
    id: int
    slug: str
    name: str
    category: str
    generation: int
    family_name: str
    family_slug: str
    url: str
    url_logo: str


IGDB_PLATFORM_CATEGORIES: dict[int, str] = {
    0: "Unknown",
    1: "Console",
    2: "Arcade",
    3: "Platform",
    4: "Operating System",
    5: "Portable Console",
    6: "Computer",
}


IGDB_PLATFORM_LIST: dict[UPS, SlugToIGDB] = {
    UPS.APVS: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 2,
        "id": 139,
        "name": "1292 Advanced Programmable Video System",
        "slug": "1292-advanced-programmable-video-system",
        "url": "https://www.igdb.com/platforms/1292-advanced-programmable-video-system",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/yfdqsudagw0av25dawjr.jpg",
    },
    UPS._3DO: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 5,
        "id": 50,
        "name": "3DO Interactive Multiplayer",
        "slug": "3do",
        "url": "https://www.igdb.com/platforms/3do",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7u.jpg",
    },
    UPS.N3DS: {
        "category": "Portable Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 8,
        "id": 37,
        "name": "Nintendo 3DS",
        "slug": "3ds",
        "url": "https://www.igdb.com/platforms/3ds",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pln6.jpg",
    },
    UPS.N64DD: {
        "category": "Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 5,
        "id": 416,
        "name": "Nintendo 64DD",
        "slug": "64dd",
        "url": "https://www.igdb.com/platforms/64dd",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plj8.jpg",
    },
    UPS.ACORN_ARCHIMEDES: {
        "category": "Computer",
        "family_name": "Acorn",
        "family_slug": "acorn",
        "generation": -1,
        "id": 116,
        "name": "Acorn Archimedes",
        "slug": "acorn-archimedes",
        "url": "https://www.igdb.com/platforms/acorn-archimedes",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plas.jpg",
    },
    UPS.ACORN_ELECTRON: {
        "category": "Computer",
        "family_name": "Acorn",
        "family_slug": "acorn",
        "generation": -1,
        "id": 134,
        "name": "Acorn Electron",
        "slug": "acorn-electron",
        "url": "https://www.igdb.com/platforms/acorn-electron",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8d.jpg",
    },
    UPS.ACPC: {
        "category": "Computer",
        "family_name": "Amstrad",
        "family_slug": "amstrad",
        "generation": -1,
        "id": 25,
        "name": "Amstrad CPC",
        "slug": "acpc",
        "url": "https://www.igdb.com/platforms/acpc",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plnh.jpg",
    },
    UPS.ADVANCED_PICO_BEENA: {
        "category": "Console",
        "family_name": "Sega",
        "family_slug": "sega",
        "generation": 6,
        "id": 507,
        "name": "Advanced Pico Beena",
        "slug": "advanced-pico-beena",
        "url": "https://www.igdb.com/platforms/advanced-pico-beena",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plou.jpg",
    },
    UPS.AIRCONSOLE: {
        "category": "Platform",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 389,
        "name": "AirConsole",
        "slug": "airconsole",
        "url": "https://www.igdb.com/platforms/airconsole",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plkq.jpg",
    },
    UPS.AMAZON_FIRE_TV: {
        "category": "Platform",
        "family_name": "Amazon",
        "family_slug": "amazon",
        "generation": -1,
        "id": 132,
        "name": "Amazon Fire TV",
        "slug": "amazon-fire-tv",
        "url": "https://www.igdb.com/platforms/amazon-fire-tv",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl91.jpg",
    },
    UPS.AMIGA: {
        "category": "Computer",
        "family_name": "Amiga",
        "family_slug": "amiga",
        "generation": -1,
        "id": 16,
        "name": "Amiga",
        "slug": "amiga",
        "url": "https://www.igdb.com/platforms/amiga",
        "url_logo": "",
    },
    UPS.AMIGA_CD32: {
        "category": "Console",
        "family_name": "Amiga",
        "family_slug": "amiga",
        "generation": 5,
        "id": 114,
        "name": "Amiga CD32",
        "slug": "amiga-cd32",
        "url": "https://www.igdb.com/platforms/amiga-cd32",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7v.jpg",
    },
    UPS.AMSTRAD_GX4000: {
        "category": "Console",
        "family_name": "Amstrad",
        "family_slug": "amstrad",
        "generation": 3,
        "id": 506,
        "name": "Amstrad GX4000",
        "slug": "amstrad-gx4000",
        "url": "https://www.igdb.com/platforms/amstrad-gx4000",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plot.jpg",
    },
    UPS.AMSTRAD_PCW: {
        "category": "Computer",
        "family_name": "Amstrad",
        "family_slug": "amstrad",
        "generation": -1,
        "id": 154,
        "name": "Amstrad PCW",
        "slug": "amstrad-pcw",
        "url": "https://www.igdb.com/platforms/amstrad-pcw",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plf7.jpg",
    },
    UPS.ANALOGUEELECTRONICS: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 1,
        "id": 100,
        "name": "Analogue electronics",
        "slug": "analogueelectronics",
        "url": "https://www.igdb.com/platforms/analogueelectronics",
        "url_logo": "",
    },
    UPS.ANDROID: {
        "category": "Operating System",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 34,
        "name": "Android",
        "slug": "android",
        "url": "https://www.igdb.com/platforms/android",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pln3.jpg",
    },
    UPS.APPLE_IIGS: {
        "category": "Computer",
        "family_name": "Apple",
        "family_slug": "apple",
        "generation": -1,
        "id": 115,
        "name": "Apple IIGS",
        "slug": "apple-iigs",
        "url": "https://www.igdb.com/platforms/apple-iigs",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl87.jpg",
    },
    UPS.APPLE_PIPPIN: {
        "category": "Console",
        "family_name": "Apple",
        "family_slug": "apple",
        "generation": 5,
        "id": 476,
        "name": "Apple Pippin",
        "slug": "apple-pippin",
        "url": "https://www.igdb.com/platforms/apple-pippin",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plnn.jpg",
    },
    UPS.APPLEII: {
        "category": "Computer",
        "family_name": "Apple",
        "family_slug": "apple",
        "generation": -1,
        "id": 75,
        "name": "Apple II",
        "slug": "appleii",
        "url": "https://www.igdb.com/platforms/appleii",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8r.jpg",
    },
    UPS.ARCADE: {
        "category": "Arcade",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 52,
        "name": "Arcade",
        "slug": "arcade",
        "url": "https://www.igdb.com/platforms/arcade",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plmz.jpg",
    },
    UPS.ARCADIA_2001: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 2,
        "id": 473,
        "name": "Arcadia 2001",
        "slug": "arcadia-2001",
        "url": "https://www.igdb.com/platforms/arcadia-2001",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plnk.jpg",
    },
    UPS.ARDUBOY: {
        "category": "Portable Console",
        "family_name": "",
        "family_slug": "",
        "generation": 8,
        "id": 438,
        "name": "Arduboy",
        "slug": "arduboy",
        "url": "https://www.igdb.com/platforms/arduboy",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plk6.jpg",
    },
    UPS.ASTROCADE: {
        "category": "Console",
        "family_name": "Bally",
        "family_slug": "bally",
        "generation": 2,
        "id": 91,
        "name": "Bally Astrocade",
        "slug": "astrocade",
        "url": "https://www.igdb.com/platforms/astrocade",
        "url_logo": "",
    },
    UPS.ATARI_JAGUAR_CD: {
        "category": "Console",
        "family_name": "Atari",
        "family_slug": "atari",
        "generation": 5,
        "id": 410,
        "name": "Atari Jaguar CD",
        "slug": "atari-jaguar-cd",
        "url": "https://www.igdb.com/platforms/atari-jaguar-cd",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plj4.jpg",
    },
    UPS.ATARI_ST: {
        "category": "Computer",
        "family_name": "Atari",
        "family_slug": "atari",
        "generation": 4,
        "id": 63,
        "name": "Atari ST/STE",
        "slug": "atari-st",
        "url": "https://www.igdb.com/platforms/atari-st",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pla7.jpg",
    },
    UPS.ATARI2600: {
        "category": "Console",
        "family_name": "Atari",
        "family_slug": "atari",
        "generation": 2,
        "id": 59,
        "name": "Atari 2600",
        "slug": "atari2600",
        "url": "https://www.igdb.com/platforms/atari2600",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pln4.jpg",
    },
    UPS.ATARI5200: {
        "category": "Console",
        "family_name": "Atari",
        "family_slug": "atari",
        "generation": 2,
        "id": 66,
        "name": "Atari 5200",
        "slug": "atari5200",
        "url": "https://www.igdb.com/platforms/atari5200",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8g.jpg",
    },
    UPS.ATARI7800: {
        "category": "Console",
        "family_name": "Atari",
        "family_slug": "atari",
        "generation": 3,
        "id": 60,
        "name": "Atari 7800",
        "slug": "atari7800",
        "url": "https://www.igdb.com/platforms/atari7800",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8f.jpg",
    },
    UPS.ATARI8BIT: {
        "category": "Computer",
        "family_name": "Atari",
        "family_slug": "atari",
        "generation": -1,
        "id": 65,
        "name": "Atari 8-bit",
        "slug": "atari8bit",
        "url": "https://www.igdb.com/platforms/atari8bit",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plad.jpg",
    },
    UPS.AY_3_8500: {
        "category": "Computer",
        "family_name": "General Instruments",
        "family_slug": "general-instruments",
        "generation": -1,
        "id": 140,
        "name": "AY-3-8500",
        "slug": "ay-3-8500",
        "url": "https://www.igdb.com/platforms/ay-3-8500",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/x42zeitpbuo2ltn7ybb2.jpg",
    },
    UPS.AY_3_8603: {
        "category": "Console",
        "family_name": "General Instruments",
        "family_slug": "general-instruments",
        "generation": 1,
        "id": 145,
        "name": "AY-3-8603",
        "slug": "ay-3-8603",
        "url": "https://www.igdb.com/platforms/ay-3-8603",
        "url_logo": "",
    },
    UPS.AY_3_8605: {
        "category": "Console",
        "family_name": "General Instruments",
        "family_slug": "general-instruments",
        "generation": 1,
        "id": 146,
        "name": "AY-3-8605",
        "slug": "ay-3-8605",
        "url": "https://www.igdb.com/platforms/ay-3-8605",
        "url_logo": "",
    },
    UPS.AY_3_8606: {
        "category": "Console",
        "family_name": "General Instruments",
        "family_slug": "general-instruments",
        "generation": 1,
        "id": 147,
        "name": "AY-3-8606",
        "slug": "ay-3-8606",
        "url": "https://www.igdb.com/platforms/ay-3-8606",
        "url_logo": "",
    },
    UPS.AY_3_8607: {
        "category": "Console",
        "family_name": "General Instruments",
        "family_slug": "general-instruments",
        "generation": 1,
        "id": 148,
        "name": "AY-3-8607",
        "slug": "ay-3-8607",
        "url": "https://www.igdb.com/platforms/ay-3-8607",
        "url_logo": "",
    },
    UPS.AY_3_8610: {
        "category": "Computer",
        "family_name": "General Instruments",
        "family_slug": "general-instruments",
        "generation": 1,
        "id": 141,
        "name": "AY-3-8610",
        "slug": "ay-3-8610",
        "url": "https://www.igdb.com/platforms/ay-3-8610",
        "url_logo": "",
    },
    UPS.AY_3_8710: {
        "category": "Console",
        "family_name": "General Instruments",
        "family_slug": "general-instruments",
        "generation": 1,
        "id": 144,
        "name": "AY-3-8710",
        "slug": "ay-3-8710",
        "url": "https://www.igdb.com/platforms/ay-3-8710",
        "url_logo": "",
    },
    UPS.AY_3_8760: {
        "category": "Console",
        "family_name": "General Instruments",
        "family_slug": "general-instruments",
        "generation": 1,
        "id": 143,
        "name": "AY-3-8760",
        "slug": "ay-3-8760",
        "url": "https://www.igdb.com/platforms/ay-3-8760",
        "url_logo": "",
    },
    UPS.BBCMICRO: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 69,
        "name": "BBC Microcomputer System",
        "slug": "bbcmicro",
        "url": "https://www.igdb.com/platforms/bbcmicro",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl86.jpg",
    },
    UPS.BLACKBERRY: {
        "category": "Operating System",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 73,
        "name": "BlackBerry OS",
        "slug": "blackberry",
        "url": "https://www.igdb.com/platforms/blackberry",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/bezbkk17hk0uobdkhjcv.jpg",
    },
    UPS.BLU_RAY_PLAYER: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 7,
        "id": 239,
        "name": "Blu-ray Player",
        "slug": "blu-ray-player",
        "url": "https://www.igdb.com/platforms/blu-ray-player",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plbv.jpg",
    },
    UPS.BROWSER: {
        "category": "Platform",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 82,
        "name": "Browser (Flash/HTML5)",
        "slug": "browser",
        "url": "https://www.igdb.com/platforms/browser",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plmx.jpg",
    },
    UPS.C_PLUS_4: {
        "category": "Computer",
        "family_name": "Commodore",
        "family_slug": "commodore",
        "generation": -1,
        "id": 94,
        "name": "Commodore Plus/4",
        "slug": "c-plus-4",
        "url": "https://www.igdb.com/platforms/c-plus-4",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8m.jpg",
    },
    UPS.C16: {
        "category": "Computer",
        "family_name": "Commodore",
        "family_slug": "commodore",
        "generation": -1,
        "id": 93,
        "name": "Commodore 16",
        "slug": "c16",
        "url": "https://www.igdb.com/platforms/c16",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plf4.jpg",
    },
    UPS.C64: {
        "category": "Computer",
        "family_name": "Commodore",
        "family_slug": "commodore",
        "generation": -1,
        "id": 15,
        "name": "Commodore C64/128/MAX",
        "slug": "c64",
        "url": "https://www.igdb.com/platforms/c64",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pll3.jpg",
    },
    UPS.CALL_A_COMPUTER: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 107,
        "name": "Call-A-Computer time-shared mainframe computer system",
        "slug": "call-a-computer",
        "url": "https://www.igdb.com/platforms/call-a-computer",
        "url_logo": "",
    },
    UPS.CASIO_LOOPY: {
        "category": "Console",
        "family_name": "Casio",
        "family_slug": "casio",
        "generation": 5,
        "id": 380,
        "name": "Casio Loopy",
        "slug": "casio-loopy",
        "url": "https://www.igdb.com/platforms/casio-loopy",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plkm.jpg",
    },
    UPS.CDCCYBER70: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 109,
        "name": "CDC Cyber 70",
        "slug": "cdccyber70",
        "url": "https://www.igdb.com/platforms/cdccyber70",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plae.jpg",
    },
    UPS.COLECOVISION: {
        "category": "Console",
        "family_name": "Coleco",
        "family_slug": "coleco",
        "generation": 2,
        "id": 68,
        "name": "ColecoVision",
        "slug": "colecovision",
        "url": "https://www.igdb.com/platforms/colecovision",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8n.jpg",
    },
    UPS.COMMODORE_CDTV: {
        "category": "Computer",
        "family_name": "Commodore",
        "family_slug": "commodore",
        "generation": -1,
        "id": 158,
        "name": "Commodore CDTV",
        "slug": "commodore-cdtv",
        "url": "https://www.igdb.com/platforms/commodore-cdtv",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl84.jpg",
    },
    UPS.CPET: {
        "category": "Computer",
        "family_name": "Commodore",
        "family_slug": "commodore",
        "generation": -1,
        "id": 90,
        "name": "Commodore PET",
        "slug": "cpet",
        "url": "https://www.igdb.com/platforms/cpet",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plf3.jpg",
    },
    UPS.DAYDREAM: {
        "category": "Console",
        "family_name": "Google",
        "family_slug": "google",
        "generation": 8,
        "id": 164,
        "name": "Daydream",
        "slug": "daydream",
        "url": "https://www.igdb.com/platforms/daydream",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/lwbdsvaveyxmuwnsga7g.jpg",
    },
    UPS.DC: {
        "category": "Console",
        "family_name": "Sega",
        "family_slug": "sega",
        "generation": 6,
        "id": 23,
        "name": "Dreamcast",
        "slug": "dc",
        "url": "https://www.igdb.com/platforms/dc",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7i.jpg",
    },
    UPS.DIGIBLAST: {
        "category": "Portable Console",
        "family_name": "",
        "family_slug": "",
        "generation": 7,
        "id": 486,
        "name": "Digiblast",
        "slug": "digiblast",
        "url": "https://www.igdb.com/platforms/digiblast",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plo2.jpg",
    },
    UPS.DONNER30: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 85,
        "name": "Donner Model 30",
        "slug": "donner30",
        "url": "https://www.igdb.com/platforms/donner30",
        "url_logo": "",
    },
    UPS.DOS: {
        "category": "Operating System",
        "family_name": "Microsoft",
        "family_slug": "microsoft",
        "generation": -1,
        "id": 13,
        "name": "DOS",
        "slug": "dos",
        "url": "https://www.igdb.com/platforms/dos",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/sqgw6vespav1buezgjjn.jpg",
    },
    UPS.DRAGON_32_SLASH_64: {
        "category": "Computer",
        "family_name": "Dragon Data",
        "family_slug": "dragon-data",
        "generation": -1,
        "id": 153,
        "name": "Dragon 32/64",
        "slug": "dragon-32-slash-64",
        "url": "https://www.igdb.com/platforms/dragon-32-slash-64",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8e.jpg",
    },
    UPS.DVD_PLAYER: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 6,
        "id": 238,
        "name": "DVD Player",
        "slug": "dvd-player",
        "url": "https://www.igdb.com/platforms/dvd-player",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plbu.jpg",
    },
    UPS.E_READER_SLASH_CARD_E_READER: {
        "category": "Portable Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 6,
        "id": 510,
        "name": "e-Reader / Card-e Reader",
        "slug": "e-reader-slash-card-e-reader",
        "url": "https://www.igdb.com/platforms/e-reader-slash-card-e-reader",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/ploy.jpg",
    },
    UPS.EDSAC: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 102,
        "name": "EDSAC",
        "slug": "edsac--1",
        "url": "https://www.igdb.com/platforms/edsac--1",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plat.jpg",
    },
    UPS.ELEKTOR: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 505,
        "name": "Elektor TV Games Computer",
        "slug": "elektor-tv-games-computer",
        "url": "https://www.igdb.com/platforms/elektor-tv-games-computer",
        "url_logo": "",
    },
    UPS.EPOCH_CASSETTE_VISION: {
        "category": "Console",
        "family_name": "Epoch",
        "family_slug": "epoch",
        "generation": 2,
        "id": 375,
        "name": "Epoch Cassette Vision",
        "slug": "epoch-cassette-vision",
        "url": "https://www.igdb.com/platforms/epoch-cassette-vision",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plko.jpg",
    },
    UPS.EPOCH_SUPER_CASSETTE_VISION: {
        "category": "Console",
        "family_name": "Epoch",
        "family_slug": "epoch",
        "generation": 3,
        "id": 376,
        "name": "Epoch Super Cassette Vision",
        "slug": "epoch-super-cassette-vision",
        "url": "https://www.igdb.com/platforms/epoch-super-cassette-vision",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plkn.jpg",
    },
    UPS.EVERCADE: {
        "category": "Portable Console",
        "family_name": "",
        "family_slug": "",
        "generation": 8,
        "id": 309,
        "name": "Evercade",
        "slug": "evercade",
        "url": "https://www.igdb.com/platforms/evercade",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plky.jpg",
    },
    UPS.EXIDY_SORCERER: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 236,
        "name": "Exidy Sorcerer",
        "slug": "exidy-sorcerer",
        "url": "https://www.igdb.com/platforms/exidy-sorcerer",
        "url_logo": "",
    },
    UPS.FAIRCHILD_CHANNEL_F: {
        "category": "Console",
        "family_name": "Fairchild",
        "family_slug": "fairchild",
        "generation": 2,
        "id": 127,
        "name": "Fairchild Channel F",
        "slug": "fairchild-channel-f",
        "url": "https://www.igdb.com/platforms/fairchild-channel-f",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8s.jpg",
    },
    UPS.FAMICOM: {
        "category": "Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 3,
        "id": 99,
        "name": "Family Computer",
        "slug": "famicom",
        "url": "https://www.igdb.com/platforms/famicom",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plnf.jpg",
    },
    UPS.FDS: {
        "category": "Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 3,
        "id": 51,
        "name": "Family Computer Disk System",
        "slug": "fds",
        "url": "https://www.igdb.com/platforms/fds",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8b.jpg",
    },
    UPS.FM_7: {
        "category": "Computer",
        "family_name": "Fujitsu",
        "family_slug": "fujitsu",
        "generation": -1,
        "id": 152,
        "name": "FM-7",
        "slug": "fm-7",
        "url": "https://www.igdb.com/platforms/fm-7",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pley.jpg",
    },
    UPS.FM_TOWNS: {
        "category": "Computer",
        "family_name": "Fujitsu",
        "family_slug": "fujitsu",
        "generation": -1,
        "id": 118,
        "name": "FM Towns",
        "slug": "fm-towns",
        "url": "https://www.igdb.com/platforms/fm-towns",
        "url_logo": "",
    },
    UPS.G_AND_W: {
        "category": "Portable Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 2,
        "id": 307,
        "name": "Game & Watch",
        "slug": "g-and-w",
        "url": "https://www.igdb.com/platforms/g-and-w",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pler.jpg",
    },
    UPS.GAMATE: {
        "category": "Portable Console",
        "family_name": "",
        "family_slug": "",
        "generation": 4,
        "id": 378,
        "name": "Gamate",
        "slug": "gamate",
        "url": "https://www.igdb.com/platforms/gamate",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plhf.jpg",
    },
    UPS.GAME_DOT_COM: {
        "category": "Portable Console",
        "family_name": "",
        "family_slug": "",
        "generation": 5,
        "id": 379,
        "name": "Game.com",
        "slug": "game-dot-com",
        "url": "https://www.igdb.com/platforms/game-dot-com",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plgk.jpg",
    },
    UPS.GAMEGEAR: {
        "category": "Portable Console",
        "family_name": "Sega",
        "family_slug": "sega",
        "generation": 4,
        "id": 35,
        "name": "Sega Game Gear",
        "slug": "gamegear",
        "url": "https://www.igdb.com/platforms/gamegear",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7z.jpg",
    },
    UPS.GB: {
        "category": "Portable Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 4,
        "id": 33,
        "name": "Game Boy",
        "slug": "gb",
        "url": "https://www.igdb.com/platforms/gb",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7m.jpg",
    },
    UPS.GBA: {
        "category": "Portable Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 6,
        "id": 24,
        "name": "Game Boy Advance",
        "slug": "gba",
        "url": "https://www.igdb.com/platforms/gba",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl74.jpg",
    },
    UPS.GBC: {
        "category": "Portable Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 5,
        "id": 22,
        "name": "Game Boy Color",
        "slug": "gbc",
        "url": "https://www.igdb.com/platforms/gbc",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7l.jpg",
    },
    UPS.GEAR_VR: {
        "category": "Console",
        "family_name": "Samsung",
        "family_slug": "samsung",
        "generation": 8,
        "id": 388,
        "name": "Gear VR",
        "slug": "gear-vr",
        "url": "https://www.igdb.com/platforms/gear-vr",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plkj.jpg",
    },
    UPS.GENESIS: {
        "category": "Console",
        "family_name": "Sega",
        "family_slug": "sega",
        "generation": 4,
        "id": 29,
        "name": "Sega Mega Drive/Genesis",
        "slug": "genesis-slash-megadrive",
        "url": "https://www.igdb.com/platforms/genesis-slash-megadrive",
        "url_logo": "",
    },
    UPS.GIZMONDO: {
        "category": "Portable Console",
        "family_name": "",
        "family_slug": "",
        "generation": 7,
        "id": 474,
        "name": "Gizmondo",
        "slug": "gizmondo",
        "url": "https://www.igdb.com/platforms/gizmondo",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plnl.jpg",
    },
    UPS.GT40: {
        "category": "Computer",
        "family_name": "DEC",
        "family_slug": "dec",
        "generation": -1,
        "id": 98,
        "name": "DEC GT40",
        "slug": "gt40",
        "url": "https://www.igdb.com/platforms/gt40",
        "url_logo": "",
    },
    UPS.HANDHELD_ELECTRONIC_LCD: {
        "category": "Portable Console",
        "family_name": "",
        "family_slug": "",
        "generation": 1,
        "id": 411,
        "name": "Handheld Electronic LCD",
        "slug": "handheld-electronic-lcd",
        "url": "https://www.igdb.com/platforms/handheld-electronic-lcd",
        "url_logo": "",
    },
    UPS.HP2100: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 104,
        "name": "HP 2100",
        "slug": "hp2100",
        "url": "https://www.igdb.com/platforms/hp2100",
        "url_logo": "",
    },
    UPS.HP3000: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 105,
        "name": "HP 3000",
        "slug": "hp3000",
        "url": "https://www.igdb.com/platforms/hp3000",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pla9.jpg",
    },
    UPS.HYPER_NEO_GEO_64: {
        "category": "Arcade",
        "family_name": "SNK",
        "family_slug": "snk",
        "generation": 5,
        "id": 135,
        "name": "Hyper Neo Geo 64",
        "slug": "hyper-neo-geo-64",
        "url": "https://www.igdb.com/platforms/hyper-neo-geo-64",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/ubf1qgytr069wm0ikh0z.jpg",
    },
    UPS.HYPERSCAN: {
        "category": "Console",
        "family_name": "Mattel",
        "family_slug": "mattel",
        "generation": 7,
        "id": 407,
        "name": "HyperScan",
        "slug": "hyperscan",
        "url": "https://www.igdb.com/platforms/hyperscan",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plj2.jpg",
    },
    UPS.IMLAC_PDS1: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 111,
        "name": "Imlac PDS-1",
        "slug": "imlac-pds1",
        "url": "https://www.igdb.com/platforms/imlac-pds1",
        "url_logo": "",
    },
    UPS.INTELLIVISION: {
        "category": "Console",
        "family_name": "Mattel",
        "family_slug": "mattel",
        "generation": 2,
        "id": 67,
        "name": "Intellivision",
        "slug": "intellivision",
        "url": "https://www.igdb.com/platforms/intellivision",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8o.jpg",
    },
    UPS.INTELLIVISION_AMICO: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 9,
        "id": 382,
        "name": "Intellivision Amico",
        "slug": "intellivision-amico",
        "url": "https://www.igdb.com/platforms/intellivision-amico",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plkp.jpg",
    },
    UPS.IOS: {
        "category": "Operating System",
        "family_name": "Apple",
        "family_slug": "apple",
        "generation": -1,
        "id": 39,
        "name": "iOS",
        "slug": "ios",
        "url": "https://www.igdb.com/platforms/ios",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl6w.jpg",
    },
    UPS.JAGUAR: {
        "category": "Console",
        "family_name": "Atari",
        "family_slug": "atari",
        "generation": 5,
        "id": 62,
        "name": "Atari Jaguar",
        "slug": "jaguar",
        "url": "https://www.igdb.com/platforms/jaguar",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7y.jpg",
    },
    UPS.LASERACTIVE: {
        "category": "Console",
        "family_name": "NEC",
        "family_slug": "nec",
        "generation": 4,
        "id": 487,
        "name": "LaserActive",
        "slug": "laseractive",
        "url": "https://www.igdb.com/platforms/laseractive",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plo4.jpg",
    },
    UPS.LEAPSTER: {
        "category": "Portable Console",
        "family_name": "Leapster",
        "family_slug": "leapster",
        "generation": 6,
        "id": 412,
        "name": "Leapster",
        "slug": "leapster",
        "url": "https://www.igdb.com/platforms/leapster",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plj5.jpg",
    },
    UPS.LEAPSTER_EXPLORER_SLASH_LEADPAD_EXPLORER: {
        "category": "Portable Console",
        "family_name": "Leapster",
        "family_slug": "leapster",
        "generation": 7,
        "id": 413,
        "name": "Leapster Explorer/LeadPad Explorer",
        "slug": "leapster-explorer-slash-leadpad-explorer",
        "url": "https://www.igdb.com/platforms/leapster-explorer-slash-leadpad-explorer",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plna.jpg",
    },
    UPS.LEAPTV: {
        "category": "Console",
        "family_name": "Leapster",
        "family_slug": "leapster",
        "generation": 8,
        "id": 414,
        "name": "LeapTV",
        "slug": "leaptv",
        "url": "https://www.igdb.com/platforms/leaptv",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plj6.jpg",
    },
    UPS.LEGACY_COMPUTER: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 409,
        "name": "Legacy Computer",
        "slug": "legacy-computer",
        "url": "https://www.igdb.com/platforms/legacy-computer",
        "url_logo": "",
    },
    UPS.LINUX: {
        "category": "Operating System",
        "family_name": "Linux",
        "family_slug": "linux",
        "generation": -1,
        "id": 3,
        "name": "Linux",
        "slug": "linux",
        "url": "https://www.igdb.com/platforms/linux",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plak.jpg",
    },
    UPS.LYNX: {
        "category": "Portable Console",
        "family_name": "Atari",
        "family_slug": "atari",
        "generation": 4,
        "id": 61,
        "name": "Atari Lynx",
        "slug": "lynx",
        "url": "https://www.igdb.com/platforms/lynx",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl82.jpg",
    },
    UPS.MAC: {
        "category": "Operating System",
        "family_name": "Apple",
        "family_slug": "apple",
        "generation": -1,
        "id": 14,
        "name": "Mac",
        "slug": "mac",
        "url": "https://www.igdb.com/platforms/mac",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plo3.jpg",
    },
    UPS.MEGA_DUCK_SLASH_COUGAR_BOY: {
        "category": "Portable Console",
        "family_name": "",
        "family_slug": "",
        "generation": 4,
        "id": 408,
        "name": "Mega Duck/Cougar Boy",
        "slug": "mega-duck-slash-cougar-boy",
        "url": "https://www.igdb.com/platforms/mega-duck-slash-cougar-boy",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plj3.jpg",
    },
    UPS.META_QUEST_2: {
        "category": "Console",
        "family_name": "Meta",
        "family_slug": "meta",
        "generation": 9,
        "id": 386,
        "name": "Meta Quest 2",
        "slug": "meta-quest-2",
        "url": "https://www.igdb.com/platforms/meta-quest-2",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pll0.jpg",
    },
    UPS.META_QUEST_3: {
        "category": "Console",
        "family_name": "Meta",
        "family_slug": "meta",
        "generation": 9,
        "id": 471,
        "name": "Meta Quest 3",
        "slug": "meta-quest-3",
        "url": "https://www.igdb.com/platforms/meta-quest-3",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plnb.jpg",
    },
    UPS.MICROCOMPUTER: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 112,
        "name": "Microcomputer",
        "slug": "microcomputer--1",
        "url": "https://www.igdb.com/platforms/microcomputer--1",
        "url_logo": "",
    },
    UPS.MICROVISION: {
        "category": "Portable Console",
        "family_name": "Milton Bradley",
        "family_slug": "milton-bradley",
        "generation": 2,
        "id": 89,
        "name": "Microvision",
        "slug": "microvision--1",
        "url": "https://www.igdb.com/platforms/microvision--1",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8q.jpg",
    },
    UPS.MOBILE: {
        "category": "Portable Console",
        "family_name": "",
        "family_slug": "",
        "generation": 7,
        "id": 55,
        "name": "Legacy Mobile Device",
        "slug": "mobile",
        "url": "https://www.igdb.com/platforms/mobile",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plnd.jpg",
    },
    UPS.MSX: {
        "category": "Computer",
        "family_name": "ASCII",
        "family_slug": "ascii",
        "generation": -1,
        "id": 27,
        "name": "MSX",
        "slug": "msx",
        "url": "https://www.igdb.com/platforms/msx",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8j.jpg",
    },
    UPS.MSX2: {
        "category": "Computer",
        "family_name": "ASCII",
        "family_slug": "ascii",
        "generation": -1,
        "id": 53,
        "name": "MSX2",
        "slug": "msx2",
        "url": "https://www.igdb.com/platforms/msx2",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8k.jpg",
    },
    UPS.N64: {
        "category": "Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 5,
        "id": 4,
        "name": "Nintendo 64",
        "slug": "n64",
        "url": "https://www.igdb.com/platforms/n64",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl78.jpg",
    },
    UPS.NDS: {
        "category": "Portable Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 7,
        "id": 20,
        "name": "Nintendo DS",
        "slug": "nds",
        "url": "https://www.igdb.com/platforms/nds",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl6t.jpg",
    },
    UPS.NEC_PC_6000_SERIES: {
        "category": "Computer",
        "family_name": "NEC",
        "family_slug": "nec",
        "generation": -1,
        "id": 157,
        "name": "NEC PC-6000 Series",
        "slug": "nec-pc-6000-series",
        "url": "https://www.igdb.com/platforms/nec-pc-6000-series",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plaa.jpg",
    },
    UPS.NEO_GEO_CD: {
        "category": "Console",
        "family_name": "SNK",
        "family_slug": "snk",
        "generation": 4,
        "id": 136,
        "name": "Neo Geo CD",
        "slug": "neo-geo-cd",
        "url": "https://www.igdb.com/platforms/neo-geo-cd",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7t.jpg",
    },
    UPS.NEO_GEO_POCKET: {
        "category": "Portable Console",
        "family_name": "SNK",
        "family_slug": "snk",
        "generation": 5,
        "id": 119,
        "name": "Neo Geo Pocket",
        "slug": "neo-geo-pocket",
        "url": "https://www.igdb.com/platforms/neo-geo-pocket",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plau.jpg",
    },
    UPS.NEO_GEO_POCKET_COLOR: {
        "category": "Portable Console",
        "family_name": "SNK",
        "family_slug": "snk",
        "generation": 5,
        "id": 120,
        "name": "Neo Geo Pocket Color",
        "slug": "neo-geo-pocket-color",
        "url": "https://www.igdb.com/platforms/neo-geo-pocket-color",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7h.jpg",
    },
    UPS.NEOGEOAES: {
        "category": "Console",
        "family_name": "SNK",
        "family_slug": "snk",
        "generation": 4,
        "id": 80,
        "name": "Neo Geo AES",
        "slug": "neogeoaes",
        "url": "https://www.igdb.com/platforms/neogeoaes",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/hamfdrgnhenxb2d9g8mh.jpg",
    },
    UPS.NEOGEOMVS: {
        "category": "Arcade",
        "family_name": "SNK",
        "family_slug": "snk",
        "generation": 4,
        "id": 79,
        "name": "Neo Geo MVS",
        "slug": "neogeomvs",
        "url": "https://www.igdb.com/platforms/neogeomvs",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/cbhfilmhdgwdql8nzsy0.jpg",
    },
    UPS.NES: {
        "category": "Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 3,
        "id": 18,
        "name": "Nintendo Entertainment System",
        "slug": "nes",
        "url": "https://www.igdb.com/platforms/nes",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plmo.jpg",
    },
    UPS.NEW_NINTENDON3DS: {
        "category": "Portable Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 8,
        "id": 137,
        "name": "New Nintendo 3DS",
        "slug": "new-nintendo-3ds",
        "url": "https://www.igdb.com/platforms/new-nintendo-3ds",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl6j.jpg",
    },
    UPS.NGAGE: {
        "category": "Portable Console",
        "family_name": "",
        "family_slug": "",
        "generation": 6,
        "id": 42,
        "name": "N-Gage",
        "slug": "ngage",
        "url": "https://www.igdb.com/platforms/ngage",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl76.jpg",
    },
    UPS.NGC: {
        "category": "Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 6,
        "id": 21,
        "name": "Nintendo GameCube",
        "slug": "ngc",
        "url": "https://www.igdb.com/platforms/ngc",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7a.jpg",
    },
    UPS.NIMROD: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 101,
        "name": "Ferranti Nimrod Computer",
        "slug": "nimrod",
        "url": "https://www.igdb.com/platforms/nimrod",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plaq.jpg",
    },
    UPS.NINTENDO_DSI: {
        "category": "Portable Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 7,
        "id": 159,
        "name": "Nintendo DSi",
        "slug": "nintendo-dsi",
        "url": "https://www.igdb.com/platforms/nintendo-dsi",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl6u.jpg",
    },
    UPS.NUON: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 6,
        "id": 122,
        "name": "Nuon",
        "slug": "nuon",
        "url": "https://www.igdb.com/platforms/nuon",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7g.jpg",
    },
    UPS.OCULUS_GO: {
        "category": "Console",
        "family_name": "Meta",
        "family_slug": "meta",
        "generation": 8,
        "id": 387,
        "name": "Oculus Go",
        "slug": "oculus-go",
        "url": "https://www.igdb.com/platforms/oculus-go",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plkk.jpg",
    },
    UPS.OCULUS_QUEST: {
        "category": "Console",
        "family_name": "Meta",
        "family_slug": "meta",
        "generation": 8,
        "id": 384,
        "name": "Oculus Quest",
        "slug": "oculus-quest",
        "url": "https://www.igdb.com/platforms/oculus-quest",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plh7.jpg",
    },
    UPS.OCULUS_RIFT: {
        "category": "Console",
        "family_name": "Meta",
        "family_slug": "meta",
        "generation": 7,
        "id": 385,
        "name": "Oculus Rift",
        "slug": "oculus-rift",
        "url": "https://www.igdb.com/platforms/oculus-rift",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pln8.jpg",
    },
    UPS.OCULUS_VR: {
        "category": "Console",
        "family_name": "Meta",
        "family_slug": "meta",
        "generation": 7,
        "id": 162,
        "name": "Oculus VR",
        "slug": "oculus-vr",
        "url": "https://www.igdb.com/platforms/oculus-vr",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pivaofe9ll2b8cqfvvbu.jpg",
    },
    UPS.ODYSSEY: {
        "category": "Console",
        "family_name": "Magnavox",
        "family_slug": "magnavox",
        "generation": 1,
        "id": 88,
        "name": "Magnavox Odyssey",
        "slug": "odyssey--1",
        "url": "https://www.igdb.com/platforms/odyssey--1",
        "url_logo": "",
    },
    UPS.ODYSSEY_2: {
        "category": "Computer",
        "family_name": "Magnavox",
        "family_slug": "magnavox",
        "generation": 2,
        "id": 133,
        "name": "Odyssey 2 / Videopac G7000",
        "slug": "odyssey-2-slash-videopac-g7000",
        "url": "https://www.igdb.com/platforms/odyssey-2-slash-videopac-g7000",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/fqwnmmpanb5se6ebccm3.jpg",
    },
    UPS.ONLIVE_GAME_SYSTEM: {
        "category": "Platform",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 113,
        "name": "OnLive Game System",
        "slug": "onlive-game-system",
        "url": "https://www.igdb.com/platforms/onlive-game-system",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plan.jpg",
    },
    UPS.OOPARTS: {
        "category": "Platform",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 372,
        "name": "OOParts",
        "slug": "ooparts",
        "url": "https://www.igdb.com/platforms/ooparts",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plgi.jpg",
    },
    UPS.OUYA: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 8,
        "id": 72,
        "name": "Ouya",
        "slug": "ouya",
        "url": "https://www.igdb.com/platforms/ouya",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl6k.jpg",
    },
    UPS.PALM_OS: {
        "category": "Operating System",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 417,
        "name": "Palm OS",
        "slug": "palm-os",
        "url": "https://www.igdb.com/platforms/palm-os",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plj9.jpg",
    },
    UPS.PANASONIC_JUNGLE: {
        "category": "Portable Console",
        "family_name": "Panasonic",
        "family_slug": "panasonic",
        "generation": 8,
        "id": 477,
        "name": "Panasonic Jungle",
        "slug": "panasonic-jungle",
        "url": "https://www.igdb.com/platforms/panasonic-jungle",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plnp.jpg",
    },
    UPS.PANASONIC_M2: {
        "category": "Console",
        "family_name": "Panasonic",
        "family_slug": "panasonic",
        "generation": 6,
        "id": 478,
        "name": "Panasonic M2",
        "slug": "panasonic-m2",
        "url": "https://www.igdb.com/platforms/panasonic-m2",
        "url_logo": "",
    },
    UPS.PC_50X_FAMILY: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 1,
        "id": 142,
        "name": "PC-50X Family",
        "slug": "pc-50x-family",
        "url": "https://www.igdb.com/platforms/pc-50x-family",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/dpwrkxrjkuxwqroqwjsw.jpg",
    },
    UPS.PC_8800_SERIES: {
        "category": "Computer",
        "family_name": "NEC",
        "family_slug": "nec",
        "generation": -1,
        "id": 125,
        "name": "PC-8800 Series",
        "slug": "pc-8800-series",
        "url": "https://www.igdb.com/platforms/pc-8800-series",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plf2.jpg",
    },
    UPS.PC_9800_SERIES: {
        "category": "Computer",
        "family_name": "NEC",
        "family_slug": "nec",
        "generation": -1,
        "id": 149,
        "name": "PC-9800 Series",
        "slug": "pc-9800-series",
        "url": "https://www.igdb.com/platforms/pc-9800-series",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pla6.jpg",
    },
    UPS.PC_FX: {
        "category": "Console",
        "family_name": "NEC",
        "family_slug": "nec",
        "generation": 5,
        "id": 274,
        "name": "PC-FX",
        "slug": "pc-fx",
        "url": "https://www.igdb.com/platforms/pc-fx",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plf8.jpg",
    },
    UPS.PDP_7: {
        "category": "Computer",
        "family_name": "DEC",
        "family_slug": "dec",
        "generation": -1,
        "id": 103,
        "name": "PDP-7",
        "slug": "pdp-7--1",
        "url": "https://www.igdb.com/platforms/pdp-7--1",
        "url_logo": "",
    },
    UPS.PDP_8: {
        "category": "Computer",
        "family_name": "DEC",
        "family_slug": "dec",
        "generation": -1,
        "id": 97,
        "name": "PDP-8",
        "slug": "pdp-8--1",
        "url": "https://www.igdb.com/platforms/pdp-8--1",
        "url_logo": "",
    },
    UPS.PDP1: {
        "category": "Computer",
        "family_name": "DEC",
        "family_slug": "dec",
        "generation": -1,
        "id": 95,
        "name": "PDP-1",
        "slug": "pdp1",
        "url": "https://www.igdb.com/platforms/pdp1",
        "url_logo": "",
    },
    UPS.PDP10: {
        "category": "Computer",
        "family_name": "DEC",
        "family_slug": "dec",
        "generation": -1,
        "id": 96,
        "name": "PDP-10",
        "slug": "pdp10",
        "url": "https://www.igdb.com/platforms/pdp10",
        "url_logo": "",
    },
    UPS.PDP11: {
        "category": "Computer",
        "family_name": "DEC",
        "family_slug": "dec",
        "generation": -1,
        "id": 108,
        "name": "PDP-11",
        "slug": "pdp11",
        "url": "https://www.igdb.com/platforms/pdp11",
        "url_logo": "",
    },
    UPS.PHILIPS_CD_I: {
        "category": "Console",
        "family_name": "Philips",
        "family_slug": "philips",
        "generation": 4,
        "id": 117,
        "name": "Philips CD-i",
        "slug": "philips-cd-i",
        "url": "https://www.igdb.com/platforms/philips-cd-i",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl80.jpg",
    },
    UPS.PLATO: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 110,
        "name": "PLATO",
        "slug": "plato--1",
        "url": "https://www.igdb.com/platforms/plato--1",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plaf.jpg",
    },
    UPS.PLAYDATE: {
        "category": "Portable Console",
        "family_name": "",
        "family_slug": "",
        "generation": 9,
        "id": 381,
        "name": "Playdate",
        "slug": "playdate",
        "url": "https://www.igdb.com/platforms/playdate",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plgx.jpg",
    },
    UPS.PLAYDIA: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 5,
        "id": 308,
        "name": "Playdia",
        "slug": "playdia",
        "url": "https://www.igdb.com/platforms/playdia",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/ples.jpg",
    },
    UPS.PLUG_AND_PLAY: {
        "category": "Platform",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 377,
        "name": "Plug & Play",
        "slug": "plug-and-play",
        "url": "https://www.igdb.com/platforms/plug-and-play",
        "url_logo": "",
    },
    UPS.POCKETSTATION: {
        "category": "Portable Console",
        "family_name": "Sony",
        "family_slug": "sony",
        "generation": 5,
        "id": 441,
        "name": "PocketStation",
        "slug": "pocketstation",
        "url": "https://www.igdb.com/platforms/pocketstation",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plkc.jpg",
    },
    UPS.POKEMON_MINI: {
        "category": "Portable Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 6,
        "id": 166,
        "name": "Pokémon mini",
        "slug": "pokemon-mini",
        "url": "https://www.igdb.com/platforms/pokemon-mini",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7f.jpg",
    },
    UPS.POLYMEGA: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 9,
        "id": 509,
        "name": "Polymega",
        "slug": "polymega",
        "url": "https://www.igdb.com/platforms/polymega",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plox.jpg",
    },
    UPS.PSX: {
        "category": "Console",
        "family_name": "Sony",
        "family_slug": "sony",
        "generation": 5,
        "id": 7,
        "name": "PlayStation",
        "slug": "ps",
        "url": "https://www.igdb.com/platforms/ps",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plmb.jpg",
    },
    UPS.PS2: {
        "category": "Console",
        "family_name": "Sony",
        "family_slug": "sony",
        "generation": 6,
        "id": 8,
        "name": "PlayStation 2",
        "slug": "ps2",
        "url": "https://www.igdb.com/platforms/ps2",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl72.jpg",
    },
    UPS.PS3: {
        "category": "Console",
        "family_name": "Sony",
        "family_slug": "sony",
        "generation": 7,
        "id": 9,
        "name": "PlayStation 3",
        "slug": "ps3",
        "url": "https://www.igdb.com/platforms/ps3",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/tuyy1nrqodtmbqajp4jg.jpg",
    },
    UPS.PS4: {
        "category": "Console",
        "family_name": "Sony",
        "family_slug": "sony",
        "generation": 8,
        "id": 48,
        "name": "PlayStation 4",
        "slug": "ps4--1",
        "url": "https://www.igdb.com/platforms/ps4--1",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl6f.jpg",
    },
    UPS.PS5: {
        "category": "Console",
        "family_name": "Sony",
        "family_slug": "sony",
        "generation": 9,
        "id": 167,
        "name": "PlayStation 5",
        "slug": "ps5",
        "url": "https://www.igdb.com/platforms/ps5",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plos.jpg",
    },
    UPS.PSP: {
        "category": "Portable Console",
        "family_name": "Sony",
        "family_slug": "sony",
        "generation": 7,
        "id": 38,
        "name": "PlayStation Portable",
        "slug": "psp",
        "url": "https://www.igdb.com/platforms/psp",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl5y.jpg",
    },
    UPS.PSVITA: {
        "category": "Portable Console",
        "family_name": "Sony",
        "family_slug": "sony",
        "generation": 8,
        "id": 46,
        "name": "PlayStation Vita",
        "slug": "psvita",
        "url": "https://www.igdb.com/platforms/psvita",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl6g.jpg",
    },
    UPS.PSVR: {
        "category": "Console",
        "family_name": "Sony",
        "family_slug": "sony",
        "generation": 8,
        "id": 165,
        "name": "PlayStation VR",
        "slug": "psvr",
        "url": "https://www.igdb.com/platforms/psvr",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plnc.jpg",
    },
    UPS.PSVR2: {
        "category": "Console",
        "family_name": "Sony",
        "family_slug": "sony",
        "generation": 9,
        "id": 390,
        "name": "PlayStation VR2",
        "slug": "psvr2",
        "url": "https://www.igdb.com/platforms/psvr2",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plo5.jpg",
    },
    UPS.R_ZONE: {
        "category": "Portable Console",
        "family_name": "",
        "family_slug": "",
        "generation": 5,
        "id": 475,
        "name": "R-Zone",
        "slug": "r-zone",
        "url": "https://www.igdb.com/platforms/r-zone",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plnm.jpg",
    },
    UPS.SATELLAVIEW: {
        "category": "Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 4,
        "id": 306,
        "name": "Satellaview",
        "slug": "satellaview",
        "url": "https://www.igdb.com/platforms/satellaview",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plgj.jpg",
    },
    UPS.SATURN: {
        "category": "Console",
        "family_name": "Sega",
        "family_slug": "sega",
        "generation": 5,
        "id": 32,
        "name": "Sega Saturn",
        "slug": "saturn",
        "url": "https://www.igdb.com/platforms/saturn",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/hrmqljpwunky1all3v78.jpg",
    },
    UPS.SCUMMVM: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        # Note: The ID 50501 is a keyword ID (not a platform ID) in IGDB's system
        "id": 50501,
        "name": "ScummVM",
        "slug": "scummvm",
        "url": "https://www.igdb.com/categories/scummvm-compatible",
        "url_logo": "",
    },
    UPS.SDSSIGMA7: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 106,
        "name": "SDS Sigma 7",
        "slug": "sdssigma7",
        "url": "https://www.igdb.com/platforms/sdssigma7",
        "url_logo": "",
    },
    UPS.SEGACD: {
        "category": "Console",
        "family_name": "Sega",
        "family_slug": "sega",
        "generation": 4,
        "id": 78,
        "name": "Sega CD",
        "slug": "sega-cd",
        "url": "https://www.igdb.com/platforms/sega-cd",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7w.jpg",
    },
    UPS.SEGACD32: {
        "category": "Console",
        "family_name": "Sega",
        "family_slug": "sega",
        "generation": 4,
        "id": 482,
        "name": "Sega CD 32X",
        "slug": "sega-cd-32x",
        "url": "https://www.igdb.com/platforms/sega-cd-32x",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plnu.jpg",
    },
    UPS.SEGA_PICO: {
        "category": "Console",
        "family_name": "Sega",
        "family_slug": "sega",
        "generation": 4,
        "id": 339,
        "name": "Sega Pico",
        "slug": "sega-pico",
        "url": "https://www.igdb.com/platforms/sega-pico",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plgo.jpg",
    },
    UPS.SEGA32: {
        "category": "Console",
        "family_name": "Sega",
        "family_slug": "sega",
        "generation": 4,
        "id": 30,
        "name": "Sega 32X",
        "slug": "sega32",
        "url": "https://www.igdb.com/platforms/sega32",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7r.jpg",
    },
    UPS.SERIES_X_S: {
        "category": "Console",
        "family_name": "Microsoft",
        "family_slug": "microsoft",
        "generation": 9,
        "id": 169,
        "name": "Xbox Series X/S",
        "slug": "series-x-s",
        "url": "https://www.igdb.com/platforms/series-x-s",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plfl.jpg",
    },
    UPS.SFAM: {
        "category": "Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 4,
        "id": 58,
        "name": "Super Famicom",
        "slug": "sfam",
        "url": "https://www.igdb.com/platforms/sfam",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/a9x7xjy4p9sqynrvomcf.jpg",
    },
    UPS.SG1000: {
        "category": "Console",
        "family_name": "Sega",
        "family_slug": "sega",
        "generation": 3,
        "id": 84,
        "name": "SG-1000",
        "slug": "sg1000",
        "url": "https://www.igdb.com/platforms/sg1000",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plmn.jpg",
    },
    UPS.SHARP_MZ_2200: {
        "category": "Computer",
        "family_name": "Sharp",
        "family_slug": "sharp",
        "generation": -1,
        "id": 374,
        "name": "Sharp MZ-2200",
        "slug": "sharp-mz-2200",
        "url": "https://www.igdb.com/platforms/sharp-mz-2200",
        "url_logo": "",
    },
    UPS.SHARP_X68000: {
        "category": "Computer",
        "family_name": "Sharp",
        "family_slug": "sharp",
        "generation": -1,
        "id": 121,
        "name": "Sharp X68000",
        "slug": "sharp-x68000",
        "url": "https://www.igdb.com/platforms/sharp-x68000",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8i.jpg",
    },
    UPS.SINCLAIR_QL: {
        "category": "Computer",
        "family_name": "Sinclair",
        "family_slug": "sinclair",
        "generation": -1,
        "id": 406,
        "name": "Sinclair QL",
        "slug": "sinclair-ql",
        "url": "https://www.igdb.com/platforms/sinclair-ql",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plih.jpg",
    },
    UPS.ZX81: {
        "category": "Computer",
        "family_name": "Sinclair",
        "family_slug": "sinclair",
        "generation": -1,
        "id": 373,
        "name": "Sinclair ZX81",
        "slug": "sinclair-zx81",
        "url": "https://www.igdb.com/platforms/sinclair-zx81",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plgr.jpg",
    },
    UPS.SMS: {
        "category": "Console",
        "family_name": "Sega",
        "family_slug": "sega",
        "generation": 3,
        "id": 64,
        "name": "Sega Master System/Mark III",
        "slug": "sms",
        "url": "https://www.igdb.com/platforms/sms",
        "url_logo": "",
    },
    UPS.SNES: {
        "category": "Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 4,
        "id": 19,
        "name": "Super Nintendo Entertainment System",
        "slug": "snes",
        "url": "https://www.igdb.com/platforms/snes",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/ifw2tvdkynyxayquiyk4.jpg",
    },
    UPS.SOL_20: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 237,
        "name": "Sol-20",
        "slug": "sol-20",
        "url": "https://www.igdb.com/platforms/sol-20",
        "url_logo": "",
    },
    UPS.STADIA: {
        "category": "Platform",
        "family_name": "Linux",
        "family_slug": "linux",
        "generation": -1,
        "id": 170,
        "name": "Google Stadia",
        "slug": "stadia",
        "url": "https://www.igdb.com/platforms/stadia",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl94.jpg",
    },
    UPS.STEAM_VR: {
        "category": "Platform",
        "family_name": "Valve",
        "family_slug": "valve",
        "generation": 8,
        "id": 163,
        "name": "SteamVR",
        "slug": "steam-vr",
        "url": "https://www.igdb.com/platforms/steam-vr",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/ipbdzzx7z3rwuzm9big4.jpg",
    },
    UPS.SUPER_ACAN: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 4,
        "id": 480,
        "name": "Super A'Can",
        "slug": "super-acan",
        "url": "https://www.igdb.com/platforms/super-acan",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plns.jpg",
    },
    UPS.SUPER_NES_CD_ROM_SYSTEM: {
        "category": "Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 4,
        "id": 131,
        "name": "Super NES CD-ROM System",
        "slug": "super-nes-cd-rom-system",
        "url": "https://www.igdb.com/platforms/super-nes-cd-rom-system",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plep.jpg",
    },
    UPS.SUPERGRAFX: {
        "category": "Console",
        "family_name": "NEC",
        "family_slug": "nec",
        "generation": 4,
        "id": 128,
        "name": "PC Engine SuperGrafx",
        "slug": "supergrafx",
        "url": "https://www.igdb.com/platforms/supergrafx",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pla4.jpg",
    },
    UPS.SWANCRYSTAL: {
        "category": "Portable Console",
        "family_name": "Bandai",
        "family_slug": "bandai",
        "generation": 5,
        "id": 124,
        "name": "SwanCrystal",
        "slug": "swancrystal",
        "url": "https://www.igdb.com/platforms/swancrystal",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8v.jpg",
    },
    UPS.SWITCH: {
        "category": "Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 8,
        "id": 130,
        "name": "Nintendo Switch",
        "slug": "switch",
        "url": "https://www.igdb.com/platforms/switch",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plgu.jpg",
    },
    UPS.SWITCH_2: {
        "category": "Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 9,
        "id": 508,
        "name": "Nintendo Switch 2",
        "slug": "switch-2",
        "url": "https://www.igdb.com/platforms/switch-2",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plow.jpg",
    },
    UPS.TATUNG_EINSTEIN: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 155,
        "name": "Tatung Einstein",
        "slug": "tatung-einstein",
        "url": "https://www.igdb.com/platforms/tatung-einstein",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pla8.jpg",
    },
    UPS.TEREBIKKO_SLASH_SEE_N_SAY_VIDEO_PHONE: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 479,
        "name": "Terebikko / See 'n Say Video Phone",
        "slug": "terebikko-slash-see-n-say-video-phone",
        "url": "https://www.igdb.com/platforms/terebikko-slash-see-n-say-video-phone",
        "url_logo": "",
    },
    UPS.THOMSON_MO5: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 156,
        "name": "Thomson MO5",
        "slug": "thomson-mo5",
        "url": "https://www.igdb.com/platforms/thomson-mo5",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plex.jpg",
    },
    UPS.TI_99: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 129,
        "name": "Texas Instruments TI-99",
        "slug": "ti-99",
        "url": "https://www.igdb.com/platforms/ti-99",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plf0.jpg",
    },
    UPS.TOMY_TUTOR_SLASH_PYUTA_SLASH_GRANDSTAND_TUTOR: {
        "category": "Computer",
        "family_name": "",
        "family_slug": "",
        "generation": -1,
        "id": 481,
        "name": "Tomy Tutor / Pyuta / Grandstand Tutor",
        "slug": "tomy-tutor-slash-pyuta-slash-grandstand-tutor",
        "url": "https://www.igdb.com/platforms/tomy-tutor-slash-pyuta-slash-grandstand-tutor",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plnt.jpg",
    },
    UPS.TRS_80: {
        "category": "Computer",
        "family_name": "Tandy",
        "family_slug": "tandy",
        "generation": -1,
        "id": 126,
        "name": "TRS-80",
        "slug": "trs-80",
        "url": "https://www.igdb.com/platforms/trs-80",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plac.jpg",
    },
    UPS.TRS_80_COLOR_COMPUTER: {
        "category": "Computer",
        "family_name": "Tandy",
        "family_slug": "tandy",
        "generation": -1,
        "id": 151,
        "name": "TRS-80 Color Computer",
        "slug": "trs-80-color-computer",
        "url": "https://www.igdb.com/platforms/trs-80-color-computer",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plf1.jpg",
    },
    UPS.TURBOGRAFX_CD: {
        "category": "Console",
        "family_name": "NEC",
        "family_slug": "nec",
        "generation": 4,
        "id": 150,
        "name": "Turbografx-16/PC Engine CD",
        "slug": "turbografx-16-slash-pc-engine-cd",
        "url": "https://www.igdb.com/platforms/turbografx-16-slash-pc-engine-cd",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl83.jpg",
    },
    UPS.TG16: {
        "category": "Console",
        "family_name": "NEC",
        "family_slug": "nec",
        "generation": 4,
        "id": 86,
        "name": "TurboGrafx-16/PC Engine",
        "slug": "turbografx16--1",
        "url": "https://www.igdb.com/platforms/turbografx16--1",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl88.jpg",
    },
    UPS.UZEBOX: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 9,
        "id": 504,
        "name": "Uzebox",
        "slug": "uzebox",
        "url": "https://www.igdb.com/platforms/uzebox",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plor.jpg",
    },
    UPS.VC: {
        "category": "Platform",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": -1,
        "id": 47,
        "name": "Virtual Console",
        "slug": "vc",
        "url": "https://www.igdb.com/platforms/vc",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plao.jpg",
    },
    UPS.VC_4000: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 2,
        "id": 138,
        "name": "VC 4000",
        "slug": "vc-4000",
        "url": "https://www.igdb.com/platforms/vc-4000",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/phikgyfmv1fevj2jhzr5.jpg",
    },
    UPS.VECTREX: {
        "category": "Console",
        "family_name": "Milton Bradley",
        "family_slug": "milton-bradley",
        "generation": 2,
        "id": 70,
        "name": "Vectrex",
        "slug": "vectrex",
        "url": "https://www.igdb.com/platforms/vectrex",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8h.jpg",
    },
    UPS.VIC_20: {
        "category": "Computer",
        "family_name": "Commodore",
        "family_slug": "commodore",
        "generation": -1,
        "id": 71,
        "name": "Commodore VIC-20",
        "slug": "vic-20",
        "url": "https://www.igdb.com/platforms/vic-20",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl8p.jpg",
    },
    UPS.VIRTUALBOY: {
        "category": "Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 5,
        "id": 87,
        "name": "Virtual Boy",
        "slug": "virtualboy",
        "url": "https://www.igdb.com/platforms/virtualboy",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7s.jpg",
    },
    UPS.VISIONOS: {
        "category": "Operating System",
        "family_name": "Apple",
        "family_slug": "apple",
        "generation": -1,
        "id": 472,
        "name": "visionOS",
        "slug": "visionos",
        "url": "https://www.igdb.com/platforms/visionos",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plnj.jpg",
    },
    UPS.VISUAL_MEMORY_UNIT_SLASH_VISUAL_MEMORY_SYSTEM: {
        "category": "Portable Console",
        "family_name": "Sega",
        "family_slug": "sega",
        "generation": 6,
        "id": 440,
        "name": "Visual Memory Unit / Visual Memory System",
        "slug": "visual-memory-unit-slash-visual-memory-system",
        "url": "https://www.igdb.com/platforms/visual-memory-unit-slash-visual-memory-system",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plk8.jpg",
    },
    UPS.VSMILE: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 6,
        "id": 439,
        "name": "V.Smile",
        "slug": "vsmile",
        "url": "https://www.igdb.com/platforms/vsmile",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plk7.jpg",
    },
    UPS.SUPERVISION: {
        "category": "Portable Console",
        "family_name": "",
        "family_slug": "",
        "generation": 4,
        "id": 415,
        "name": "Watara/QuickShot Supervision",
        "slug": "watara-slash-quickshot-supervision",
        "url": "https://www.igdb.com/platforms/watara-slash-quickshot-supervision",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plj7.jpg",
    },
    UPS.WII: {
        "category": "Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 7,
        "id": 5,
        "name": "Wii",
        "slug": "wii",
        "url": "https://www.igdb.com/platforms/wii",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl92.jpg",
    },
    UPS.WIIU: {
        "category": "Console",
        "family_name": "Nintendo",
        "family_slug": "nintendo",
        "generation": 8,
        "id": 41,
        "name": "Wii U",
        "slug": "wiiu",
        "url": "https://www.igdb.com/platforms/wiiu",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl6n.jpg",
    },
    UPS.WIN: {
        "category": "Operating System",
        "family_name": "Microsoft",
        "family_slug": "microsoft",
        "generation": -1,
        "id": 6,
        "name": "Windows",
        "slug": "win",
        "url": "https://www.igdb.com/platforms/win",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plim.jpg",
    },
    UPS.WINDOWS_MIXED_REALITY: {
        "category": "Platform",
        "family_name": "Microsoft",
        "family_slug": "microsoft",
        "generation": 8,
        "id": 161,
        "name": "Windows Mixed Reality",
        "slug": "windows-mixed-reality",
        "url": "https://www.igdb.com/platforms/windows-mixed-reality",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plm4.jpg",
    },
    UPS.WINDOWS_MOBILE: {
        "category": "Operating System",
        "family_name": "Microsoft",
        "family_slug": "microsoft",
        "generation": -1,
        "id": 405,
        "name": "Windows Mobile",
        "slug": "windows-mobile",
        "url": "https://www.igdb.com/platforms/windows-mobile",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plkl.jpg",
    },
    UPS.WINPHONE: {
        "category": "Operating System",
        "family_name": "Microsoft",
        "family_slug": "microsoft",
        "generation": -1,
        "id": 74,
        "name": "Windows Phone",
        "slug": "winphone",
        "url": "https://www.igdb.com/platforms/winphone",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pla3.jpg",
    },
    UPS.WONDERSWAN: {
        "category": "Portable Console",
        "family_name": "Bandai",
        "family_slug": "bandai",
        "generation": 5,
        "id": 57,
        "name": "WonderSwan",
        "slug": "wonderswan",
        "url": "https://www.igdb.com/platforms/wonderswan",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7b.jpg",
    },
    UPS.WONDERSWAN_COLOR: {
        "category": "Portable Console",
        "family_name": "Bandai",
        "family_slug": "bandai",
        "generation": 5,
        "id": 123,
        "name": "WonderSwan Color",
        "slug": "wonderswan-color",
        "url": "https://www.igdb.com/platforms/wonderswan-color",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl79.jpg",
    },
    UPS.X1: {
        "category": "Computer",
        "family_name": "Sharp",
        "family_slug": "sharp",
        "generation": -1,
        "id": 77,
        "name": "Sharp X1",
        "slug": "x1",
        "url": "https://www.igdb.com/platforms/x1",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl89.jpg",
    },
    UPS.XBOX: {
        "category": "Console",
        "family_name": "Microsoft",
        "family_slug": "microsoft",
        "generation": 6,
        "id": 11,
        "name": "Xbox",
        "slug": "xbox",
        "url": "https://www.igdb.com/platforms/xbox",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl7e.jpg",
    },
    UPS.XBOX360: {
        "category": "Console",
        "family_name": "Microsoft",
        "family_slug": "microsoft",
        "generation": 7,
        "id": 12,
        "name": "Xbox 360",
        "slug": "xbox360",
        "url": "https://www.igdb.com/platforms/xbox360",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plha.jpg",
    },
    UPS.XBOXONE: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 8,
        "id": 49,
        "name": "Xbox One",
        "slug": "xboxone",
        "url": "https://www.igdb.com/platforms/xboxone",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/pl95.jpg",
    },
    UPS.ZEEBO: {
        "category": "Console",
        "family_name": "",
        "family_slug": "",
        "generation": 7,
        "id": 240,
        "name": "Zeebo",
        "slug": "zeebo",
        "url": "https://www.igdb.com/platforms/zeebo",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plbx.jpg",
    },
    UPS.ZOD: {
        "category": "Portable Console",
        "family_name": "",
        "family_slug": "",
        "generation": 5,
        "id": 44,
        "name": "Tapwave Zodiac",
        "slug": "zod",
        "url": "https://www.igdb.com/platforms/zod",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/lfsdnlko80ftakbugceu.jpg",
    },
    UPS.ZXS: {
        "category": "Computer",
        "family_name": "Sinclair",
        "family_slug": "sinclair",
        "generation": -1,
        "id": 26,
        "name": "ZX Spectrum",
        "slug": "zxs",
        "url": "https://www.igdb.com/platforms/zxs",
        "url_logo": "https://images.igdb.com/igdb/image/upload/t_1080p/plab.jpg",
    },
}
