// Snapshot of the catalogue database, taken 2026-09-07. Cover and shot are IGDB image ids.
export interface Game {
  id: number;
  name: string;
  year: number;
  rating: number;
  cover: string;
  shot: string | null;
  platforms: string[];
  summary: string;
}
export interface Shelf {
  key: string;
  title: string;
  games: Game[];
}
export const TOTAL_TITLES = 29183;
export const TOTAL_SYSTEMS = 25;
export const SHELVES: Shelf[] = [
  {
    "key": "top",
    "title": "Top rated",
    "games": [
      {
        "id": 511,
        "name": "Super Metroid",
        "year": 1994,
        "rating": 96,
        "cover": "co5osy",
        "shot": "ajgpm9cnhjndlpkblwpw",
        "platforms": [
          "snes",
          "wii"
        ],
        "summary": "The Space Pirates, merciless agents of the evil Mother Brain, have stolen the last Metroid from a research station, and once again Mother Brain threatens the safety of the galaxy! Samus Aran must don her awesome…"
      },
      {
        "id": 455,
        "name": "The Legend of Zelda: A Link to the Past",
        "year": 1991,
        "rating": 96,
        "cover": "co3vzn",
        "shot": "mussjiqbllmh1lxkavc4",
        "platforms": [
          "snes",
          "wii"
        ],
        "summary": "Venture back to Hyrule and an age of magic and heroes. The predecessors of Link and Zelda face monsters on the march when a menacing magician takes over the kingdom. Only you can prevent his evil plot from shattering…"
      },
      {
        "id": 487,
        "name": "Super Mario World",
        "year": 1990,
        "rating": 96,
        "cover": "co8lo8",
        "shot": "sc8e1z",
        "platforms": [
          "snes",
          "wii"
        ],
        "summary": "A 2D platformer and first entry on the SNES in the Super Mario franchise, Super Mario World follows Mario as he attempts to defeat Bowser's underlings and rescue Princess Peach from his clutches. The game features a…"
      },
      {
        "id": 184,
        "name": "Final Fantasy III",
        "year": 1994,
        "rating": 95,
        "cover": "coaq5k",
        "shot": "sc9d75",
        "platforms": [
          "snes",
          "wii"
        ],
        "summary": "Final Fantasy VI is the sixth main installment in the Final Fantasy series, developed and published by Square. It was the final title in the series to feature two-dimensional graphics, and the first story that did…"
      },
      {
        "id": 904,
        "name": "Super Smash Bros. Melee",
        "year": 2001,
        "rating": 94,
        "cover": "co21yv",
        "shot": "sc88bq",
        "platforms": [
          "ngc"
        ],
        "summary": "A crossover platform fighting game featuring characters from Nintendo franchises including Mario, The Legend of Zelda, Star Fox, Pokémon, and Fire Emblem. Unlike traditional fighters, the goal is to knock opponents…"
      },
      {
        "id": 494,
        "name": "Super Mario Galaxy",
        "year": 2007,
        "rating": 94,
        "cover": "co21ro",
        "shot": "sc882z",
        "platforms": [
          "wii"
        ],
        "summary": "A 3D platformer and first Wii entry in the Super Mario franchise, Super Mario Galaxy sees Mario jump across planets and galaxies with varying items, enemies, geographies and gravity mechanics in order to reach his…"
      },
      {
        "id": 490,
        "name": "Super Mario World 2: Yoshi's Island",
        "year": 1995,
        "rating": 94,
        "cover": "co2kn9",
        "shot": "sc87fh",
        "platforms": [
          "snes"
        ],
        "summary": "Super Mario World 2: Yoshi's Island is a platform video game acting as a prequel to 1990's Super Mario World. The game casts players as Yoshi as he escorts Baby Mario through 48 levels in order to reunite him with…"
      },
      {
        "id": 31,
        "name": "Mass Effect 2",
        "year": 2010,
        "rating": 94,
        "cover": "co20ac",
        "shot": "k22nwxzx6eb4ek7xbjps",
        "platforms": [
          "ps3",
          "xbox360"
        ],
        "summary": "Are you prepared to lose everything to save the galaxy? You'll need to be, Commander Shephard. It's time to bring together your greatest allies and recruit the galaxy's fighting elite to continue the resistance…"
      },
      {
        "id": 513,
        "name": "Metroid Prime",
        "year": 2002,
        "rating": 93,
        "cover": "co3w4w",
        "shot": "koajaesby7cmhujlcwkl",
        "platforms": [
          "ngc"
        ],
        "summary": "A 3D exploration-focused metroidvania with first-person shooting mechanics and the first 3D entry in the Metroid series, Metroid Prime follows Samus Aran after the events of Metroid (1986) as she boards a Space…"
      },
      {
        "id": 5680,
        "name": "Persona 5",
        "year": 2016,
        "rating": 93,
        "cover": "co1r76",
        "shot": "sclnuh",
        "platforms": [
          "ps3"
        ],
        "summary": "Persona 5, a turn-based JRPG with visual novel elements, follows a high school student with a criminal record for a crime he didn't commit. Soon he meets several characters who share similar fates to him, and…"
      },
      {
        "id": 495,
        "name": "Super Mario Galaxy 2",
        "year": 2010,
        "rating": 93,
        "cover": "co21tl",
        "shot": "sc8836",
        "platforms": [
          "wii"
        ],
        "summary": "Super Mario Galaxy 2 is the sequel to Super Mario Galaxy and the fourth 3D platformer entry in the Mario franchise. The sequel retains many elements from its predecessor, such as the adventure being in outer space,…"
      },
      {
        "id": 1047,
        "name": "Chrono Trigger",
        "year": 1995,
        "rating": 92,
        "cover": "co3plw",
        "shot": "tve2cd2nclmri1x34wl7",
        "platforms": [
          "snes",
          "wii"
        ],
        "summary": "In this turn-based Japanese RPG, young Crono must travel through time through a misfunctioning teleporter to rescue his misfortunate companion and take part in an intricate web of past and present perils. The…"
      },
      {
        "id": 445,
        "name": "The Last of Us",
        "year": 2013,
        "rating": 92,
        "cover": "co1r7f",
        "shot": "scxnly",
        "platforms": [
          "ps3"
        ],
        "summary": "The Last of Us is a third-person action-adventure game featuring a mix of exploration, stealth and combat. Players face both infected creatures and hostile human enemies while progressing through varied environments.…"
      },
      {
        "id": 531,
        "name": "Castlevania: Symphony of the Night",
        "year": 1997,
        "rating": 92,
        "cover": "co53m8",
        "shot": "ioxxz5cyqrb56cginhj6",
        "platforms": [
          "ps3",
          "psp",
          "psx",
          "saturn",
          "xbox360"
        ],
        "summary": "Having been awoken from his eternal slumber by the reappearance of Castlevania, Alucard must once again face the evil minions of darkness. Use your vampiric powers, along with weapons, potions, and other magical…"
      }
    ]
  },
  {
    "key": "gems",
    "title": "Hidden gems",
    "games": [
      {
        "id": 3041,
        "name": "G-Force",
        "year": 2009,
        "rating": 90,
        "cover": "co1vxj",
        "shot": "emmla4dhbssf2xh87zcj",
        "platforms": [
          "ps3",
          "xbox360"
        ],
        "summary": "G-Force draws you into the adventures of an elite team of trained guinea pigs on a mission to thwart a sinister plot to destroy the world. Take control of both G-Force commander Darwin and his sidekick, Mooch, as…"
      },
      {
        "id": 2364,
        "name": "NBA Street Vol. 2",
        "year": 2003,
        "rating": 86,
        "cover": "co2etl",
        "shot": null,
        "platforms": [
          "ngc",
          "ps2",
          "xbox"
        ],
        "summary": "NBA Street Vol. 2 is a basketball video game, published by EA Sports BIG and developed by EA Canada. It is the sequel to NBA Street and the second game in the NBA Street series. It was released on April 28, 2003 for…"
      },
      {
        "id": 26803,
        "name": "Final Fantasy VI",
        "year": 1999,
        "rating": 88,
        "cover": "co8kxj",
        "shot": "scqr3p",
        "platforms": [
          "ps3",
          "psp",
          "psx"
        ],
        "summary": "A port of Final Fantasy VI for PlayStation that adds an opening and ending FMV cutscene and includes a number of bonuses, including a bestiary and artwork gallery that can be accessed from the main menu, and which…"
      },
      {
        "id": 2562,
        "name": "Panzer General",
        "year": 1994,
        "rating": 94,
        "cover": "co5pbv",
        "shot": "npx0mflgmsegzkrg2vuh",
        "platforms": [
          "psx"
        ],
        "summary": "You are the brightest and best of the new Axis generals in the Second World War. Your tactical skills will be tested in armored assaults, amphibious invasions, paradrops, naval engagements, and fierce aerial combat…"
      },
      {
        "id": 6970,
        "name": "Street Fighter II' Turbo",
        "year": 1993,
        "rating": 92,
        "cover": "co1w9x",
        "shot": "xn8fyfsniw0bqbvhslnf",
        "platforms": [
          "snes",
          "wii"
        ],
        "summary": "They're back, and they're badder than ever! Faster, stronger and with all new moves, twelve of the greatest fighters from across the globe are ready to battle. Choose your champion and get ready for the big brawl as…"
      },
      {
        "id": 1884,
        "name": "Bomberman '94",
        "year": 1993,
        "rating": 88,
        "cover": "co9sg7",
        "shot": "ackera2ww4qw0zta05ro",
        "platforms": [
          "ps3",
          "psp",
          "tg16",
          "wii"
        ],
        "summary": "BOMBERMAN has arrived to restore peace on the planet, which has been split into five parts by an evil hand! In addition to the nine members of the Bomber Family, the character ROOI shows up to lend a hand. Jump on…"
      },
      {
        "id": 8631,
        "name": "Utawarerumono",
        "year": 2002,
        "rating": 89,
        "cover": "co4hgg",
        "shot": "wvfzdjj8x2qbb3xolszc",
        "platforms": [
          "ps2",
          "psp"
        ],
        "summary": "Hakuoro, a man who wakes up in a tiny backwoods village near the mountains with heavy injuries, no memory, and a mask he cannot remove. After being nursed back to health by Eruruw, the girl who found him lying at the…"
      },
      {
        "id": 1011,
        "name": "Mega Man Battle Network 3 White",
        "year": 2002,
        "rating": 89,
        "cover": "co203l",
        "shot": "sc5xqo",
        "platforms": [
          "gba"
        ],
        "summary": "Using an RPG style, you must guide Mega Man through various levels defeating enemies along the way and collecting the various chips to upgrade Mega Man's weapons and other items.  Exclusive to this, the White…"
      },
      {
        "id": 1430,
        "name": "Rock Band 2",
        "year": 2008,
        "rating": 90,
        "cover": "co1wp9",
        "shot": "bixqom4buqliyr9dih1q",
        "platforms": [
          "ps2",
          "ps3",
          "wii",
          "xbox360"
        ],
        "summary": "Rock Band 2 is the sequel to the 2007 musical simulation game Rock Band and offers similar gameplay. Directly competing with Guitar Hero: World Tour, the game allows different people to play together as in a band,…"
      },
      {
        "id": 6550,
        "name": "Shin Megami Tensei: Strange Journey",
        "year": 2009,
        "rating": 88,
        "cover": "co26fw",
        "shot": "mq7moenvlgnqyclhdsw0",
        "platforms": [
          "nds"
        ],
        "summary": "In the near future, a mysterious, growing, black void appears at the Earth's southern pole. Unable to determine its cause and powerless to stop its deadly encroachment, humanity sends an elite team of explorers into…"
      },
      {
        "id": 8419,
        "name": "Last Window: The Secret of Cape West",
        "year": 2010,
        "rating": 91,
        "cover": "co1uvf",
        "shot": "jwbik2o0qs7ey2kwpbkd",
        "platforms": [
          "nds"
        ],
        "summary": "Last Window: The Secret of Cape West is an adventure video game developed by the now-defunct Cing and published by Nintendo for the Nintendo DS handheld game console. It is the sequel to Hotel Dusk: Room 215,…"
      },
      {
        "id": 5615,
        "name": "Terranigma",
        "year": 1995,
        "rating": 90,
        "cover": "co26g4",
        "shot": "y4d1s1ks6ixkuzvgqpea",
        "platforms": [
          "snes"
        ],
        "summary": "Terranigma is an action role-playing game for the SNES. It is one of the few games which has never been released in North America. The Game is about a boy named Ark whose fate is to resurrect the earth and to…"
      },
      {
        "id": 123,
        "name": "Operation Flashpoint: Cold War Crisis",
        "year": 2001,
        "rating": 89,
        "cover": "coca14",
        "shot": "up8t7ecilfhqsc8j4cn6",
        "platforms": [
          "xbox"
        ],
        "summary": "Bohemia Interactive's debut game published by Codemasters as Operation Flashpoint in 2001, became genre-defining combat military simulation and the No. 1 bestselling PC game around the world and has won many…"
      },
      {
        "id": 8831,
        "name": "Jurassic Park",
        "year": 1993,
        "rating": 97,
        "cover": "co2zpb",
        "shot": "sc9hn4",
        "platforms": [
          "nes"
        ],
        "summary": "Jurassic Park is a top-down action-adventure game based on the blockbuster film. Players take on the role of Dr. Alan Grant, exploring the island, rescuing stranded workers, and battling escaped dinosaurs. The game…"
      }
    ]
  },
  {
    "key": "rpg",
    "title": "Role-playing",
    "games": [
      {
        "id": 1810,
        "name": "Mario & Luigi: Bowser's Inside Story",
        "year": 2009,
        "rating": 93,
        "cover": "co21vr",
        "shot": "oiqinybnuh6wanbhpeqb",
        "platforms": [
          "nds"
        ],
        "summary": "Mario & Luigi: Bowser's Inside Story is the third game in the Mario & Luigi series of games. Players control Mario and Luigi simultaneously in the side-scrolling platform environment of Bowser's body, while also…"
      },
      {
        "id": 5596,
        "name": "Persona 3",
        "year": 2006,
        "rating": 91,
        "cover": "co5mo6",
        "shot": "sc9e1f",
        "platforms": [
          "ps2"
        ],
        "summary": "Shin Megami Tensei: Persona 3 is a role-playing video game developed by Atlus. In the game, the player takes the role of a male high-school student who joins the Specialized Extracurricular Execution Squad (SEES), a…"
      },
      {
        "id": 5604,
        "name": "Persona 4",
        "year": 2008,
        "rating": 91,
        "cover": "co1u07",
        "shot": "th1nw16odrnjuops4dix",
        "platforms": [
          "ps2",
          "ps3"
        ],
        "summary": "An entry in the JRPG/visual novel hybrid Persona series in which the player has to harness the power of Personas and fight entities called Shadows by forging bonds with the locals of Inaba, a rural Japanese town…"
      },
      {
        "id": 2083,
        "name": "Mother 3",
        "year": 2006,
        "rating": 90,
        "cover": "coa3qi",
        "shot": "tyhcoervcntjuy3bfucd",
        "platforms": [
          "gba"
        ],
        "summary": "A turn-based JRPG and sequel to EarthBound (1994) in which a tragedy surrounding a family in the primitive yet joyful village of Tazmily incites the coming-of-age story of Lucas, the family's younger son, who goes on…"
      },
      {
        "id": 7661,
        "name": "Ōkami HD",
        "year": 2012,
        "rating": 90,
        "cover": "co22s8",
        "shot": "w6mkenxprqizcghkca2v",
        "platforms": [
          "ps3"
        ],
        "summary": "Experience the critically acclaimed masterpiece with its renowned Sumi-e ink art style in breathtaking high resolution. Take on the role of Amaterasu, the Japanese sun goddess who inhabits the form of a legendary…"
      },
      {
        "id": 7,
        "name": "BioShock",
        "year": 2007,
        "rating": 90,
        "cover": "co2mli",
        "shot": "usn4aw2k54ym8jcjbkmg",
        "platforms": [
          "ps3",
          "xbox360"
        ],
        "summary": "BioShock is a horror-themed first-person shooter set in a steampunk underwater dystopia. The player is urged to turn everything into a weapon: biologically modifying their own body with Plasmids, hacking devices and…"
      },
      {
        "id": 608,
        "name": "Kingdom Hearts II",
        "year": 2005,
        "rating": 89,
        "cover": "co30t1",
        "shot": "buh7z8xjphqlnyizaods",
        "platforms": [
          "ps2"
        ],
        "summary": "Kingdom Hearts II is an action role-playing game, and the primary entry to the series since the 2002 Disney Interactive and Square collaboration. The game's setting is a collection of various levels (referred to…"
      },
      {
        "id": 592,
        "name": "Tales of Symphonia",
        "year": 2003,
        "rating": 89,
        "cover": "co1peo",
        "shot": "mnq1nim0acbjsvmqm06p",
        "platforms": [
          "ngc"
        ],
        "summary": "In a dying world, legend has it that a Chosen One will one day rise from amongst the people and the land will be reborn. The line between good and evil blurs in this epic adventure where the fate of two interlocked…"
      },
      {
        "id": 695,
        "name": "Xenogears",
        "year": 1998,
        "rating": 89,
        "cover": "cobxj4",
        "shot": "sc74tf",
        "platforms": [
          "ps3",
          "psp",
          "psx"
        ],
        "summary": "Xenogears Blends Authentic RPG Gameplay with Exquisite Hand-Drawn and Computer-Generated Animation in a Grand Science Fiction Tale. An intricate storyline involving many human and non-human characters will prove to…"
      },
      {
        "id": 641,
        "name": "Ōkami",
        "year": 2006,
        "rating": 89,
        "cover": "co3mpk",
        "shot": "ydnatplkfp9hhymhtuf9",
        "platforms": [
          "ps2",
          "ps3",
          "wii"
        ],
        "summary": "Set sometime in classical Japanese history, Ōkami combines several Japanese mythology and folklore to tell the story of how the land was saved from darkness by the Shinto sun goddess named Amaterasu, who took the…"
      },
      {
        "id": 1182,
        "name": "Dark Souls",
        "year": 2011,
        "rating": 89,
        "cover": "co1x78",
        "shot": "gdplcyvz8fvgxvgu2phn",
        "platforms": [
          "ps3",
          "xbox360"
        ],
        "summary": "Dark Souls is an action role-playing game developed by FromSoftware and published by Bandai Namco Entertainment. Released in September 2011 as a spiritual sequel to Demon's Souls, it is set in a dark, medieval…"
      },
      {
        "id": 1800,
        "name": "Paper Mario",
        "year": 2000,
        "rating": 89,
        "cover": "co1qda",
        "shot": "a5r3k2lf3lgvifrycqeg",
        "platforms": [
          "n64",
          "wii"
        ],
        "summary": "Paper Mario, a turn-based JRPG entry in the Mario franchise with a paper-based aesthetic and platforming elements, sees the titular character working his way through the Mushroom Kingdom's diverse locales and biomes,…"
      },
      {
        "id": 3519,
        "name": "Super Mario RPG: Legend of the Seven Stars",
        "year": 1996,
        "rating": 88,
        "cover": "co5r6p",
        "shot": "sc87qy",
        "platforms": [
          "snes",
          "wii"
        ],
        "summary": "A JRPG entry in the Super Mario franchise in which Mario meets many unlikely allies in order to jump and fight his way through the Mushroom Kingdom and collect stars to repair the Star Road, the pathway that grants…"
      },
      {
        "id": 764,
        "name": "Fire Emblem",
        "year": 2003,
        "rating": 88,
        "cover": "cobbmr",
        "shot": "sc7ncc",
        "platforms": [
          "gba"
        ],
        "summary": "It is the seventh game of the Fire Emblem series, the second game in the series to be released for the Game Boy Advance, and the first to be released in both North America and Europe. It features a prologue storyline…"
      }
    ]
  },
  {
    "key": "platform",
    "title": "Platformers",
    "games": [
      {
        "id": 1494,
        "name": "SpongeBob SquarePants: Battle for Bikini Bottom",
        "year": 2003,
        "rating": 92,
        "cover": "co3iyp",
        "shot": "npmdhpfxwlyawqg7male",
        "platforms": [
          "ngc",
          "ps2",
          "xbox"
        ],
        "summary": "The evil Plankton has set in motion his most diabolical plot ever! The fate of Bikini Bottom has been put into the unsuspecting hands of SpongeBob. Explore a huge world filled with unexpected surprises, challenges,…"
      },
      {
        "id": 438,
        "name": "Oddworld: Abe's Oddysee",
        "year": 1997,
        "rating": 91,
        "cover": "co89fk",
        "shot": "scbu17",
        "platforms": [
          "ps3",
          "psp",
          "psx"
        ],
        "summary": "Oddworld: Abe's Oddysee is the first game set in the fictional Oddworld universe. It is a platformer with puzzle-solving elements, focusing on the portrayal of a weak, underpowered character in a grim and hostile…"
      },
      {
        "id": 4677,
        "name": "Ico",
        "year": 2001,
        "rating": 91,
        "cover": "co3r78",
        "shot": "sc9502",
        "platforms": [
          "ps2"
        ],
        "summary": "An action-adventure game in which a boy is abandoned and taken to a massive castle by his people. After exploring it for a while, he meets a girl who speaks a different language than him, then decides to get both of…"
      },
      {
        "id": 514,
        "name": "Metroid: Zero Mission",
        "year": 2004,
        "rating": 90,
        "cover": "co1vci",
        "shot": "iz158hgxyswgxb7kq4ng",
        "platforms": [
          "gba"
        ],
        "summary": "The full story of Samus Aran's first mission finally unfolds...  The first Metroid game just scratched the surface of the cataclysmic events on planet Zebes, and at long last the rest of the tale has come to light.…"
      },
      {
        "id": 700,
        "name": "Journey",
        "year": 2012,
        "rating": 90,
        "cover": "cob9lk",
        "shot": "sc8nw6",
        "platforms": [
          "ps3"
        ],
        "summary": "A third-person adventure game in which the player, controlling a robed figure, makes a pilgrimage through a desert landscape to a rugged mountain with a beacon of light in the distance while uncovering the history of…"
      },
      {
        "id": 485,
        "name": "Super Mario Bros. 3",
        "year": 1988,
        "rating": 89,
        "cover": "co7ozx",
        "shot": "sc856r",
        "platforms": [
          "nes",
          "wii"
        ],
        "summary": "Super Mario Bros. 3, the third entry in the Super Mario Bros. series and Super Mario franchise, sees Mario or Luigi navigate a nonlinear world map containing platforming levels and optional minigames and challenges.…"
      },
      {
        "id": 23272,
        "name": "Super Mario Bros.",
        "year": 1993,
        "rating": 89,
        "cover": "co5k7b",
        "shot": "scknvq",
        "platforms": [
          "snes"
        ],
        "summary": "A remaster of the original Super Mario Bros., released exclusively as part of the Super Mario All-Stars bundle."
      },
      {
        "id": 267,
        "name": "God of War II",
        "year": 2007,
        "rating": 89,
        "cover": "co3dik",
        "shot": "ftficp3du1j15ytxkeo8",
        "platforms": [
          "ps2"
        ],
        "summary": "God of War II, an action-adventure hack-and-slash video game, was developed by Santa Monica Studio and published by Sony Computer Entertainment (SCE). Initially launched for the PlayStation 2, it serves as the second…"
      },
      {
        "id": 491,
        "name": "Super Mario 64",
        "year": 1996,
        "rating": 89,
        "cover": "co721v",
        "shot": "sc8e2l",
        "platforms": [
          "n64",
          "wii"
        ],
        "summary": "Mario is super in a whole new way! Combining the finest 3-D graphics ever developed for a video game and an explosive soundtrack, Super Mario 64 becomes a new standard for video games. It's packed with bruising…"
      },
      {
        "id": 234,
        "name": "Uncharted 3: Drake's Deception",
        "year": 2011,
        "rating": 89,
        "cover": "co1tp8",
        "shot": "htlgs12rau2b0ioyndhy",
        "platforms": [
          "ps3"
        ],
        "summary": "A search for the fabled \"Atlantis of the Sands\" propels fortune hunter Nathan Drake on a trek into the heart of the Arabian Desert. When the terrible secrets of this lost city are unearthed, Drake's quest descends…"
      },
      {
        "id": 1212,
        "name": "Shadow of the Colossus",
        "year": 2005,
        "rating": 89,
        "cover": "co1ozz",
        "shot": "sc8jij",
        "platforms": [
          "ps2"
        ],
        "summary": "An open-world action/adventure game in which a young wanderer, along with a stolen magical sword and his steed companion, trespasses a cursed land, makes a deal with an ancient being to bring a sacrificial victim…"
      },
      {
        "id": 528,
        "name": "Super Castlevania IV",
        "year": 1991,
        "rating": 89,
        "cover": "co20dc",
        "shot": "avqzngqz09r6trfirofz",
        "platforms": [
          "snes",
          "wii"
        ],
        "summary": "A century of Transylvanian tranquility is about to come to a shocking end. Once again the mortifying screams of helpless villagers shake the ground as they huddle against new nightmarish horrors unleashed by the Duke…"
      },
      {
        "id": 67,
        "name": "Assassin's Creed II",
        "year": 2009,
        "rating": 88,
        "cover": "co1rcf",
        "shot": "dxb4yiwyhvwehvsisy7a",
        "platforms": [
          "ps3",
          "xbox360"
        ],
        "summary": "Discover an intriguing and epic story of power, revenge and conspiracy set during a pivotal moment in history: the Italian Renaissance. Experience the freedom and immersion of an all new open world and mission…"
      },
      {
        "id": 1170,
        "name": "LittleBigPlanet 2",
        "year": 2011,
        "rating": 88,
        "cover": "co2ijw",
        "shot": "oact409tlmgncnz2yudc",
        "platforms": [
          "ps3"
        ],
        "summary": "LittleBigPlanet 2 is a puzzle platformer video game centered around user-generated content, first announced on May 8th, 2010 in the June 2010 issue of gaming magazine Game Informer. The game was developed by Media…"
      }
    ]
  },
  {
    "key": "fighting",
    "title": "Fighting",
    "games": [
      {
        "id": 5201,
        "name": "Marvel vs. Capcom: Clash of Super Heroes",
        "year": 1998,
        "rating": 86,
        "cover": "co8r3z",
        "shot": "px6uhczfepsivg1vcpwv",
        "platforms": [
          "dc",
          "ps3",
          "xbox360"
        ],
        "summary": "Marvel vs. Capcom: Clash of Super Heroes is the fifth Marvel Comics-licensed fighting game by Capcom and the third game in the Marvel vs. Capcom series. In contrast to X-Men vs. Street Fighter and Marvel Super Heroes…"
      },
      {
        "id": 376,
        "name": "Street Fighter IV",
        "year": 2008,
        "rating": 84,
        "cover": "co1w4t",
        "shot": "fxw59oaqikm3nruveare",
        "platforms": [
          "ps3",
          "xbox360"
        ],
        "summary": "Street Fighter IV brings the legendary fighting series back to its roots by taking the beloved fighting moves and techniques of the original Street Fighter II, and infusing them with Capcom’s latest advancements in…"
      },
      {
        "id": 1337,
        "name": "Dragon Ball Z: Budokai 3",
        "year": 2004,
        "rating": 84,
        "cover": "co6dfo",
        "shot": "sc7dv3",
        "platforms": [
          "ps2"
        ],
        "summary": "The third installment in the Dragon Ball Z: Budokai series begins another tournament of champions where only one fighter can prevail. As one of the characters from the Dragon Ball Z animated series, you can master an…"
      },
      {
        "id": 5500,
        "name": "Super Punch-Out!!",
        "year": 1994,
        "rating": 84,
        "cover": "co395t",
        "shot": "n3se2w5hmeic014glvvz",
        "platforms": [
          "snes",
          "wii"
        ],
        "summary": "Slug your way through the grueling and sweat-pounding matches of the Minor, Major and World Circuits. Dodge bone-bruising punches and dance to the top of the supreme Special Circuit. Face off against old favorites…"
      },
      {
        "id": 62,
        "name": "Mortal Kombat",
        "year": 2011,
        "rating": 84,
        "cover": "co20mc",
        "shot": "sc81mc",
        "platforms": [
          "ps3",
          "xbox360"
        ],
        "summary": "Mortal Kombat is a 2011 fighting game developed by NetherRealm Studios. It is the ninth main installment in the Mortal Kombat franchise and a soft reboot of the series. Although beginning during the events of Mortal…"
      },
      {
        "id": 903,
        "name": "Super Smash Bros.",
        "year": 1999,
        "rating": 83,
        "cover": "co2tso",
        "shot": "sc88bj",
        "platforms": [
          "n64",
          "wii"
        ],
        "summary": "Super Smash Bros. is a crossover fighting video game between several different Nintendo franchises, and the first installment in the Super Smash Bros. series. Players must defeat their opponents multiple times in a…"
      },
      {
        "id": 5202,
        "name": "Marvel vs. Capcom 2: New Age of Heroes",
        "year": 2000,
        "rating": 82,
        "cover": "co870e",
        "shot": "sc89wa",
        "platforms": [
          "dc",
          "ps2",
          "xbox"
        ],
        "summary": "Marvel vs. Capcom 2: New Age of Heroes is the fourth game in the Marvel vs. Capcom series of fighting games. The player's controls were simplified to make the gameplay more accessible to the wider audience of casual…"
      },
      {
        "id": 1610,
        "name": "Mortal Kombat: Komplete Edition",
        "year": 2012,
        "rating": 82,
        "cover": "co1xzx",
        "shot": "sc81md",
        "platforms": [
          "ps3",
          "xbox360"
        ],
        "summary": "This Komplete Edition is a re-release of the original game. It includes the full game, alongside all previously released downloadable content. It also includes the Mortal Kombat: Songs Inspired by the Warriors album…"
      },
      {
        "id": 3926,
        "name": "The Warriors",
        "year": 2005,
        "rating": 82,
        "cover": "co2yzp",
        "shot": "sc87an",
        "platforms": [
          "ps2",
          "psp",
          "xbox"
        ],
        "summary": "Based on the 1979 movie of the same name. A battle on the New York streets. The armies of the night number 60,000 strong, and tonight they're all after The Warriors - a street gang wrongly accused of killing a rival…"
      },
      {
        "id": 861,
        "name": "SoulCalibur III",
        "year": 2005,
        "rating": 82,
        "cover": "co4kmb",
        "shot": "scs2wc",
        "platforms": [
          "ps2"
        ],
        "summary": "Soulcalibur III is a fighting game produced by Namco as a sequel to Soulcalibur II and the fourth installment in the Soul series. The game includes three new modes and a larger character roster with 24 characters…"
      },
      {
        "id": 6225,
        "name": "Yakuza Kiwami",
        "year": 2016,
        "rating": 82,
        "cover": "cob1qh",
        "shot": "pw559s2tnxnhutpata8c",
        "platforms": [
          "ps3"
        ],
        "summary": "Yakuza: Kiwami is an enhanced remake of the original Yakuza game for PlayStation 2, not just an HD port. While the original PS2 release also had English voice-acting for western release, this PS4 remake only retains…"
      },
      {
        "id": 6531,
        "name": "The King of Fighters '97",
        "year": 1997,
        "rating": 81,
        "cover": "coc5fo",
        "shot": "ecxdyisquj8gde99z66u",
        "platforms": [
          "neogeoaes",
          "ps3",
          "psp",
          "psx",
          "saturn",
          "wii"
        ],
        "summary": "The King of Fighters '97 is a 1997 fighting game produced by SNK for the Neo Geo arcade and home console. It is the fourth game in The King of Fighters series. It was ported to the Neo-Geo CD, as well as the…"
      },
      {
        "id": 4950,
        "name": "Battletoads / Double Dragon",
        "year": 1993,
        "rating": 81,
        "cover": "co70dr",
        "shot": "sc9e5v",
        "platforms": [
          "nes"
        ],
        "summary": "Battletoads & Double Dragon - The Ultimate Team is the fourth game in the Battletoads series. It is a crossover with the Double Dragon series of beat 'em up games developed by Technos Japan. It was released for the…"
      },
      {
        "id": 5264,
        "name": "One Finger Death Punch",
        "year": 2013,
        "rating": 80,
        "cover": "co2h2c",
        "shot": "lghrtatlswpxnuos0u8z",
        "platforms": [
          "xbox360"
        ],
        "summary": "Experience cinematic kung-fu battles in the fastest, most intense brawler the indie world has ever seen! With the unique 1:1 response system of One Finger Death Punch, players will feel the immediate feedback of…"
      }
    ]
  },
  {
    "key": "racing",
    "title": "Racing",
    "games": [
      {
        "id": 889,
        "name": "Gran Turismo 3: A-Spec",
        "year": 2001,
        "rating": 92,
        "cover": "co5xru",
        "shot": "sc8joe",
        "platforms": [
          "ps2"
        ],
        "summary": "More than two years in the making, Gran Turismo 3 A-spec features over 150 detailed cars -- each composed of more than 4,000 polygons -- 60 beginner, amateur and professional championship races, as well as ten…"
      },
      {
        "id": 2493,
        "name": "SSX 3",
        "year": 2003,
        "rating": 90,
        "cover": "co1o4m",
        "shot": "yxzkoi3pnvxkg7b5xdh3",
        "platforms": [
          "ngc",
          "ps2",
          "xbox"
        ],
        "summary": "Players can discover the open mountain in the newest version of the smash-hit SSX snowboarding franchise.  SSX 3 allows gamers to go anywhere gravity will take them. Players will discover a colossal mountain where…"
      },
      {
        "id": 3697,
        "name": "Burnout 3: Takedown",
        "year": 2004,
        "rating": 88,
        "cover": "co1y53",
        "shot": "sc87am",
        "platforms": [
          "ps2",
          "xbox"
        ],
        "summary": "Take anarchic driving destruction on a world tour and experience the pure arcade adrenaline-rush of Burnout 3: Takedown. Combine aggressive high-speed racing with the ultimate in slamming crash action to boost your…"
      },
      {
        "id": 300,
        "name": "Burnout Paradise",
        "year": 2008,
        "rating": 87,
        "cover": "co28p7",
        "shot": "mlupgrrfxcnd0pmdx6p4",
        "platforms": [
          "ps3",
          "xbox360"
        ],
        "summary": "Burnout Paradise is an arcade racing game set in an open world called Paradise City, a departure from the fixed tracks of earlier Burnout games. Players roam the city freely and start events by pulling up to…"
      },
      {
        "id": 2495,
        "name": "SSX Tricky",
        "year": 2001,
        "rating": 87,
        "cover": "co2sup",
        "shot": "avudmk6a9te6egw6rvm4",
        "platforms": [
          "ngc",
          "ps2",
          "xbox"
        ],
        "summary": "SSX Tricky is a snowboarding video game, the second game in the SSX series published by EA Sports Big & developed by EA Canada. The game was developed under the working title SSX 2."
      },
      {
        "id": 1268,
        "name": "Super Mario Kart",
        "year": 1992,
        "rating": 86,
        "cover": "co21w8",
        "shot": "sc85li",
        "platforms": [
          "snes",
          "wii"
        ],
        "summary": "Super Mario Kart is a racing game for the Super Nintendo Entertainment System and the first game of the Mario Kart series, as well as the game that sets precedents to the fictional kart racing genre. Part of this…"
      },
      {
        "id": 1277,
        "name": "Mario Kart DS",
        "year": 2005,
        "rating": 86,
        "cover": "cob9rx",
        "shot": "tzzh27poxj7ncdmizqeq",
        "platforms": [
          "nds"
        ],
        "summary": "Mario Kart DS is the continuation of the long running racing game series that began on the Super Nintendo. It features 16 new tracks as well as 16 tracks from the previous 4 games, with each set split up into the…"
      },
      {
        "id": 311,
        "name": "Driver",
        "year": 1999,
        "rating": 86,
        "cover": "coc53l",
        "shot": "zmhwauey7nrqnxxy8gzj",
        "platforms": [
          "ps3",
          "psp",
          "psx"
        ],
        "summary": "The player is John Tanner, an undercover cop who try to take advantage of his own excellent driving skill in order to infiltrate a criminal organization. In the storyline, the player has the chance to drive several…"
      },
      {
        "id": 1920,
        "name": "F-Zero GX",
        "year": 2003,
        "rating": 85,
        "cover": "co525x",
        "shot": "jo6b8xkvh8jhapxny9wa",
        "platforms": [
          "ngc"
        ],
        "summary": "F-Zero GX is the fourth installment in the F-Zero series and the successor to F-Zero X. The game continues the series' difficult, high-speed racing style, retaining the basic gameplay and control system from the…"
      },
      {
        "id": 1660,
        "name": "Forza Motorsport 3",
        "year": 2009,
        "rating": 85,
        "cover": "co91qf",
        "shot": "j0vjkp50l9b47rd1u4pn",
        "platforms": [
          "xbox360"
        ],
        "summary": "Forza Motorsport 3 is a racing video game developed for Xbox 360 by Turn 10 Studios. It was released in October 2009. It is the sequel to Forza Motorsport 2 and the third installment in the Forza Motorsport series.…"
      },
      {
        "id": 1373,
        "name": "Burnout Revenge",
        "year": 2005,
        "rating": 85,
        "cover": "co2nhp",
        "shot": "fow9ntgqhhxjccdnbplo",
        "platforms": [
          "ps2",
          "xbox",
          "xbox360"
        ],
        "summary": "In Burnout Revenge, players compete in a range of racing game types with different aims. These take place within rush-hour traffic, and include circuit racing, Road Rage (where players cause as many rivals to crash…"
      },
      {
        "id": 50,
        "name": "Need for Speed: Most Wanted",
        "year": 2005,
        "rating": 85,
        "cover": "co209j",
        "shot": "y8ogspafaeoj3idr1m2m",
        "platforms": [
          "xbox360"
        ],
        "summary": "Need for Speed: Most Wanted is a single-player racing video game and the ninth installment in the Need for Speed series, following Underground 2. The game centers on street-racing gameplay, featuring a variety of…"
      },
      {
        "id": 4790,
        "name": "Forza Horizon 2",
        "year": 2014,
        "rating": 84,
        "cover": "co2f5s",
        "shot": "u7y5yt0hzhb0q8xnbec4",
        "platforms": [
          "xbox360"
        ],
        "summary": "Race through a massive wide-open world featuring dramatic weather and day-to-night cycle in Forza Horizon 2. Instantly connect with friends in the ultimate celebration of speed, style, and action-packed driving.…"
      },
      {
        "id": 1659,
        "name": "Forza Motorsport 4",
        "year": 2011,
        "rating": 84,
        "cover": "co2290",
        "shot": "pdfijxfgemphacg9rdbr",
        "platforms": [
          "xbox360"
        ],
        "summary": "Forza Motorsport 4 is a racing video game, and the fourth in the Forza Motorsport series. Like Sony's Gran Turismo franchise, Forza games are racing simulations; heavy emphasis is placed on making the cars drive and…"
      }
    ]
  },
  {
    "key": "early",
    "title": "Before 1990",
    "games": [
      {
        "id": 5183,
        "name": "Tetris",
        "year": 1989,
        "rating": 86,
        "cover": "co2ufk",
        "shot": "scs8lx",
        "platforms": [
          "nes"
        ],
        "summary": "Tetris is a puzzle video game created by Soviet software engineer Alexey Pajitnov in the mid-1980s. Players arrange falling pieces made of four connected blocks, called tetrominoes, into complete horizontal lines…"
      },
      {
        "id": 4214,
        "name": "Disney's DuckTales",
        "year": 1989,
        "rating": 84,
        "cover": "co3wks",
        "shot": "p34wb4n7dpex9m3ojmm3",
        "platforms": [
          "nes",
          "wii"
        ],
        "summary": "DuckTales is a platform game developed and published by Capcom and based on the Disney animated TV series of the same name. It was first released in North America for the Nintendo Entertainment System in 1989 and was…"
      },
      {
        "id": 4839,
        "name": "Ms. Pac-Man",
        "year": 1982,
        "rating": 82,
        "cover": "co53rj",
        "shot": "sc8d48",
        "platforms": [
          "gamegear",
          "sms",
          "xbox360"
        ],
        "summary": "In 1982, a sequel to the incredibly popular Pac-Man was introduced in the form of his girlfriend, Ms. Pac-Man. This sequel continued on the \"eat the dots/avoid the ghosts\" gameplay of the original game, but added new…"
      },
      {
        "id": 453,
        "name": "The Legend of Zelda",
        "year": 1986,
        "rating": 80,
        "cover": "co1uii",
        "shot": "sckdy6",
        "platforms": [
          "nes",
          "wii"
        ],
        "summary": "The Legend of Zelda is the first title in the Zelda series, it has marked the history of video games particularly for it's game mechanics and universe. The player controls Link and must make his way through the…"
      },
      {
        "id": 520,
        "name": "Castlevania",
        "year": 1986,
        "rating": 79,
        "cover": "coba2o",
        "shot": "scufs3",
        "platforms": [
          "nes",
          "wii"
        ],
        "summary": "Step into the shadows of the deadliest dwelling on earth. You've arrived at Castlevania, and you're here on business: To destroy forever the Curse of the Evil Count.  Unfortunately, everybody's home this evening.…"
      },
      {
        "id": 4878,
        "name": "Ninja Gaiden",
        "year": 1988,
        "rating": 79,
        "cover": "coc1yh",
        "shot": "nwnvofmobg9gjp0d2tnk",
        "platforms": [
          "wii"
        ],
        "summary": "Ninja Action! The stage is set for conspiracy, mystery and evil in America. Come with Ninja Ryu as he takes you on his fateful journey. Tecmo's unique cinema display system develops the story stage by stage. You…"
      },
      {
        "id": 21689,
        "name": "Contra",
        "year": 1988,
        "rating": 79,
        "cover": "co6ys0",
        "shot": "scf3wr",
        "platforms": [
          "nes"
        ],
        "summary": "Contra is the NES port of the homonymous 1987 arcade game. It is a run and gun action game developed and published by Konami. The NES port was originally released in North America, and it lacks the cutscenes and…"
      },
      {
        "id": 2812,
        "name": "Battle City",
        "year": 1985,
        "rating": 78,
        "cover": "co2f7d",
        "shot": "pd1gdodxo5gcmdxkvvh5",
        "platforms": [
          "nes",
          "wii"
        ],
        "summary": "Battle City, also known as Tank 1990 or Tank in some pirate multicart releases, is a multi-directional shooter video game for the Family Computer produced and published in 1985 by Namco. The game was later released…"
      }
    ]
  },
  {
    "key": "handheld",
    "title": "Pocket classics",
    "games": [
      {
        "id": 957,
        "name": "Advance Wars",
        "year": 2001,
        "rating": 92,
        "cover": "cob9nu",
        "shot": "xhhyrgwo9z1ebf0qy9gs",
        "platforms": [
          "gba"
        ],
        "summary": "Just because this battle fits in the palm of your hand doesn't mean the stakes are small. On the contrary, this all-or-nothing fight will have you accessing guns, grenades, launchers, and weaponry of all sorts.…"
      },
      {
        "id": 467,
        "name": "The Legend of Zelda: Oracle of Ages",
        "year": 2001,
        "rating": 90,
        "cover": "co2tw1",
        "shot": "lrj9bbm9a3i2ivp0vn6c",
        "platforms": [
          "gbc"
        ],
        "summary": "The Legend of Zelda: Oracle of Ages is one of two Zelda titles released for the Game Boy Color, the other being Oracle of Seasons. The game retain many gameplay elements from Link's Awakening such as the graphics,…"
      },
      {
        "id": 734,
        "name": "Professor Layton and the Unwound Future",
        "year": 2008,
        "rating": 88,
        "cover": "cobav0",
        "shot": "gbwqfjxvdzrvukaxx9pw",
        "platforms": [
          "nds"
        ],
        "summary": "As with previous Professor Layton games, Unwound Future is an adventure game where the player solves puzzles offered by local citizens to progress the story forward, through dialogue and around 32 minutes of full…"
      },
      {
        "id": 462,
        "name": "The Legend of Zelda: The Minish Cap",
        "year": 2004,
        "rating": 87,
        "cover": "co3nsk",
        "shot": "sckftc",
        "platforms": [
          "gba"
        ],
        "summary": "The Legend of Zelda: The Minish Cap is a top-down action adventure game that tells the origins of the evil Vaati from Four Swords. Like most other titles in the series, The Minish Cap features the fully explorable…"
      },
      {
        "id": 459,
        "name": "The Legend of Zelda: Oracle of Seasons",
        "year": 2001,
        "rating": 87,
        "cover": "co2tw0",
        "shot": "sckenj",
        "platforms": [
          "gbc"
        ],
        "summary": "The Legend of Zelda: Oracle of Seasons is one of two Zelda titles released for the Game Boy Color, the other being Oracle of Ages. The game retain many gameplay elements from Link's Awakening such as the graphics,…"
      },
      {
        "id": 153,
        "name": "Metal Gear Solid: Peace Walker",
        "year": 2010,
        "rating": 87,
        "cover": "coawb5",
        "shot": "scj1ny",
        "platforms": [
          "psp"
        ],
        "summary": "Metal Gear Solid: Peace Walker is an action-adventure stealth video game and is the third action-based Metal Gear title made specifically for the PSP. The gameplay consists of two primary modes: Mission and Mother…"
      },
      {
        "id": 968,
        "name": "WarioWare, Inc.: Mega Microgame$!",
        "year": 2003,
        "rating": 87,
        "cover": "co1wpz",
        "shot": "cmhs6pjfdhgr7dcjdwlf",
        "platforms": [
          "gba"
        ],
        "summary": "Frantic action! Prepare for lightning-quick game play as you blaze through over 200 bizarre microgames designed by a crazy crew of Wario's cronies! There are even two-player contests that can be played on a single…"
      },
      {
        "id": 5590,
        "name": "Nine Hours, Nine Persons, Nine Doors",
        "year": 2009,
        "rating": 86,
        "cover": "co4hsz",
        "shot": "v1zmbaj7nzmursjm9yzc",
        "platforms": [
          "nds"
        ],
        "summary": "The game is a murder mystery visual novel with a heavy story focus that requires multiple playthroughs to figure out and involves puzzle rooms used to progress through the story with dialogue choices to be made…"
      },
      {
        "id": 183,
        "name": "Final Fantasy VIII",
        "year": 1999,
        "rating": 86,
        "cover": "co2z7d",
        "shot": "sc9fd0",
        "platforms": [
          "ps3",
          "psp",
          "psx"
        ],
        "summary": "Final Fantasy VIII is the eighth main installment in the Final Fantasy series. The gameplay makes a departure from many series standards. While it still uses the Active Time Battle system, it deviates from the…"
      },
      {
        "id": 180,
        "name": "Final Fantasy IX",
        "year": 2000,
        "rating": 86,
        "cover": "co2unc",
        "shot": "sc9fxj",
        "platforms": [
          "ps3",
          "psp",
          "psx"
        ],
        "summary": "Final Fantasy IX is the ninth main installment in the FF series. The title is a return to the series's roots, with gameplay features and references to the past games featuring throughout, as well as a medieval…"
      },
      {
        "id": 266,
        "name": "God of War: Ghost of Sparta",
        "year": 2010,
        "rating": 86,
        "cover": "co3dio",
        "shot": "fotqy3bxetkbkhklizdt",
        "platforms": [
          "psp"
        ],
        "summary": "\"Marking Kratos' second foray into portable gaming, God of War: Ghost of Sparta stands as a spin-off nestled between the events of God of War and God of War II. Despite ascending to the title of the god of war,…"
      },
      {
        "id": 2455,
        "name": "Dino Crisis 2",
        "year": 2000,
        "rating": 86,
        "cover": "co8qbu",
        "shot": "sc88js",
        "platforms": [
          "ps3",
          "psp",
          "psx"
        ],
        "summary": "Dino Crisis 2 is a third-person action-adventure game and sequel to Dino Crisis. In a change from the survival horror theme of the first game, Dino Crisis 2 is more shoot 'em up oriented. The character always runs,…"
      },
      {
        "id": 816,
        "name": "Pokémon Blue Version",
        "year": 1996,
        "rating": 86,
        "cover": "co5pi7",
        "shot": "scapo8",
        "platforms": [
          "gb"
        ],
        "summary": "Pokémon Blue is the third core series Pokémon game released as a minor revision of Pokémon Red and Green, which were released earlier that year. It was thus the first solitary version in the core series of Pokémon…"
      },
      {
        "id": 176,
        "name": "Final Fantasy Tactics Advance",
        "year": 2003,
        "rating": 86,
        "cover": "cob8fn",
        "shot": "mk0vnpm419aaaxobmqsj",
        "platforms": [
          "gba"
        ],
        "summary": "Squaresoft brings its popular Final Fantasy franchise to the Game Boy Advance in the form of strategic warfare. Final Fantasy Tactics Advance trails the story of a young boy named Marche who is magically transported…"
      }
    ]
  }
];
