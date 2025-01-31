import xml.etree.ElementTree as ET
import json

xmlfile = "quest/keklidercquest.xml"
outpath = "game/quest/part1/"

tree = ET.parse(xmlfile)
root = tree.getroot()

roomid = 1
verbid = 0x20
rooms = {}
objects = {}
builinverbs = [ (0x01,["é    ", "észak"])
, (0x02,["ék   "])
, (0x03,["k    ", "kelet"])
, (0x04,["dk   "])
, (0x05,["d    ", "dél  "])
, (0x06,["dny  "])
, (0x07,["ny   ", "nyuga"])
, (0x08,["ény  "])
, (0x09,["fel  ", "föl  "])
, (0x0a,["le   "])
, (0x0b,["be   ", "bemeg", "belép"])
, (0x0c,["ki   ", "kimeg", "kilép"])
, (0x0d,["n    ", "néz  ", "körül", "nézek"])
, (0x0e,["f    ", "fog  ", "visz "])
, (0x0f,["rak  ", "r    ", "letes", "tesz ", "lerak"])
, (0x10,["l    ", "lista", "leltá"])
, (0x12,["load ", "betöl"])
, (0x13,["save ", "felve", "elmen"])
, (0x14,["erő  ", "e    ", "eredm", "pont ", "energ"])
, (0x15,["v    ", "vizsg", "megvi", "kutat", "kikut"])
, (0x16,["s    ", "segít"])
, (0x17,["játék", "állás", "helyz"])
, (0x18,["magnó", "kazet"])
, (0x19,["disk ", "diskr", "lemez", "flopp"])
, (0x1a,["undo ", "bom  ", "vel  "])
, (0x1b,["save ", "qsave", "ment ", "menté", "elmen"]) # same as 0x12?
, (0x1c,["load ", "qload", "tölté", "betöl"])
]
verbs = {}
for verb in builinverbs:
    #verb = builinverbs[verbi]
    verbs[verb[1][0].strip()] = {
        'id': verb[0],
        'aliases': verb[1]
    }
verbs["felad; befej"] = {
        'id': 0x1d,
        'aliases': ["felad", "befej"],
        'script': "SetPlayerStatus 255"
    }
verbs["haszn"] = {
        'id': 0x1e,
        'aliases': ['haszn']
    }

startroom = ""

exitConv = {
    "up": "fel",
    "down": "le",
    "out": "ki",
    "in": "be",
    "north": "é",
    "south": "d",
    "west": "ny",
    "east": "k",
    "northeast": "ék",
    "northwest": "ény",
    "southeast": "dk",
    "southwest": "dny"
}

def readVerbs(doc, room):
    global verbid
    for item in doc.findall('./verb'):
        pattern = item.findtext('pattern')
        script = item.findtext('script')
        defaultExpr = item.findtext('defaultexpression')
        verb = verbs.get(pattern)
        if verb:
            if not room:
                print(f" duplicated Verb: '{pattern}'")
                continue
        else:
            aliases = pattern.split("; ")
            aliases = list(map(lambda s : s.ljust(5)[:5], aliases))

            print("verb: " + pattern)
            verbs[pattern]={
                'id': verbid,
                'aliases': aliases,
                'default': defaultExpr,
                'script': script
            }
            verbid+=1
            verb = verbs[pattern]
        if room:
            roomverbs = room.get('verbs')
            if not roomverbs:
                roomverbs = {}
            roomverbs[pattern] = {
                'id' : verb['id'],
                'default': defaultExpr,
                'script': script
            }
            room['verbs']=roomverbs

def exitConvert(exitstring):
    global exitConv
    res = exitConv.get(exitstring)
    if res:
        return res
    print(f" exit string not found '{exitstring}'")
    return exitstring

for item in root.findall('./object'):
    roomName = item.attrib['name']
    print("room: " + item.attrib['name'])
    exits = {}
    for exit in item.findall('exit') :
        e = exitConvert(exit.attrib['alias'])
        to = exit.attrib['to']
        print(f"  exit: {e} - {to}")
        exits[e]={'toRoom': to}
    for object in item.findall('object'):
        objName = object.attrib['name']
        objAlias = object.findtext('alias')
        print("  object: " + objName)
        if (objName == "player"):
            startroom = roomName
        else :
            objects[objName] = {
                'inRoom' : roomName,
                'alias' : objAlias,
                'look' : object.findtext('look')
            }
    room={
        'id' : roomid,
        'description': item.findtext('description'),
        'exits': exits,
    }
    readVerbs(item, room)
    rooms[roomName]=room
    roomid += 1




readVerbs(root, False)

print(f"\n objects: {len(objects)}")
print(f"\n rooms: {len(rooms)}")
print(f"\n rooms: {json.dumps(rooms, ensure_ascii=False, indent=2)}")
print(f"\n verbs: {len(verbs)}")
#print(f"\n verbs: {json.dumps(verbs, ensure_ascii=False, indent=2)}")


texts1 = {
  "Nem értem. Próbálkozz mással! ": {'id': 1},
  "Nem teheted meg. ": {'id': 2},
  "Nem mehetsz abba az irányba. ": {'id': 3},
  "OK. ": {'id': 4},
  "Nem látom itt azt a tárgyat. ": {'id': 5},
  "Nincs nálad az a tárgy. ": {'id': 6},
  "Egy gyors leltár: ": {'id': 7},
  "Nincs nálad semmi. ": {'id': 8},
  "Nem látsz semmi érdekeset. ": {'id': 9},
  "Minden rendben. ": {'id': 10},
  "Ezt látod: ": {'id': 11},
  "Meghaltál. ": {'id': 12},
  "Így használd: FELVESZEM A JÁTÉKOT xxx-RE ": {'id': 13},
  "Így használd: BETÖLTÖM A JÁTÉKOT xxx-RŐL ": {'id':14},
  "xxx: KAZETTA vagy LEMEZ ": {'id':15},
  "Nincs itt semmi. ": {'id': 16},
  "Nincs nálad semmisem. ": {'id': 17},
  """\r\tA Bosszú 1.\n\nKitalálta, kidolgozta, megtervezte, szkriptelte: Rátkai István\n\nHomeLab-2-re programozta: Érdi Gergő""": {'id': 18}

}
textid1=18


def Text1(text):
    global textid1
    global texts1
    t = texts1.get(text)
    if t:
        return t['id']
    textid1 += 1
    texts1[text] = {
        'id': textid1
    }
    return textid1
texts = {}
textid = 0
def Text(text):
    global textid
    global texts
    t = texts.get(text)
    if t:
        return t['id']
    textid += 1
    texts[text] = {
        'id': textid
    }
    return textid

def Exits(room):
    retstr = "Kijáratok:"
    for exitDir in room['exits']:
        retstr += f" {exitDir}"
    return retstr

# WRITE OUT
with open(outpath+"enter.txt", "w", encoding="utf-8") as f:
    f.write("-- -*- haskell -*-\n")
    f.write("[\n")
    comma = ""
    for roomName in rooms:
       room = rooms[roomName]
       f.write(f"{comma} -- ROOM {room['id']} {roomName}\n")
       f.write("  [\n")
       f.write(f"     CompactMessage {Text(room['description']+' ')}  -- {room['description']}\n")
       f.write(f"  ,  CompactMessage {Text(Exits(room))}  -- {Exits(room)}\n")
       f.write("  ]\n")
       if comma == "" :
           comma = ","
    f.write("]\n")







with open(outpath+"dict.txt", "w", encoding="utf-8") as f:
    f.write("-- -*- haskell -*-\n")
    f.write("[")
    comma = ""
    # for tuple in builinverbs:
    #     f.write(f"{comma} (0x{tuple[0]:02x} , {json.dumps(tuple[1], ensure_ascii=False)})\n")
    #     if comma == "" :
    #        comma = ","
    for verbString in verbs:
        verb = verbs[verbString]
        f.write(f"{comma} (0x{verb['id']:02x} , {json.dumps(verb['aliases'], ensure_ascii=False)})\n")
        if comma == "" :
           comma = ","
    f.write("]\n")

with open(outpath+"interactive-global.txt", "w", encoding="utf-8") as f:
    f.write("-- -*- haskell -*-\n")
    f.write("[")
    comma = ""
    for verbString in verbs:
        verb = verbs[verbString]
        if verb.get('default') or verb.get('script'):
            f.write(f"{comma} InputDispatch [0x{verb['id']:02x}]  -- {verb['aliases'][0]}\n")
            f.write("    [")
            defaultText = verb.get('default')
            if defaultText:
                f.write(f"      Message {Text1(defaultText)}  -- {defaultText}\n")
            scriptText = verb.get('script')
            if scriptText:
                f.write(f"      Sleep 5  -- {scriptText}\n") #proper script parser here
            f.write("    ]\n")
            if comma == "" :
                comma = ","
    f.write("]\n")

with open(outpath+"interactive-local.txt", "w", encoding="utf-8") as f:
    f.write("-- -*- haskell -*-\n")
    f.write("[")
    comma = ""
    for roomName in rooms:
        room = rooms[roomName]
        comma2 = ""
        f.write(f"{comma} -- ROOM {room['id']} {roomName}\n")
        f.write(f"  [")
        for exitDir in room['exits']:
            exit = room['exits'][exitDir]
            verb = verbs[exitDir]
            f.write(f"  {comma2} InputDispatch [0x{verb['id']:02x}]  -- {verb['aliases'][0]}\n")
            f.write("    [")
            f.write(f" MoveTo {rooms[exit['toRoom']]['id']}   -- {exit['toRoom']}\n")
            if comma2 == "" :
                comma2 = ","
            f.write("    ]\n")
        for verbString in room.get('verbs', []):
            #verb = verbs[verbString]
            verb = room['verbs'][verbString]
            if verb.get('default') or verb.get('script'):
                f.write(f"  {comma2} InputDispatch [0x{verb['id']:02x}]  -- {verb['aliases'][0]}\n")
                f.write("    [")
                defaultText = verb.get('default')
                if defaultText:
                    f.write(f" Message {Text1(defaultText)}  -- {defaultText}\n")
                scriptText = verb.get('script')
                if scriptText:
                    f.write(f"      Sleep 5  -- {scriptText}\n") #proper script parser here
                f.write("    ]\n")
                if comma2 == "" :
                    comma2 = ","
        f.write(f"  ]\n")
        if comma == "" :
            comma = ","
    f.write("]\n")


with open(outpath+"text2.txt", "w", encoding="utf-8") as f:
    f.write("-- -*- haskell -*-\n")
    f.write("[")
    comma = ""
    for textString in texts:
       text = texts[textString]
       f.write(f"{comma} ({text['id']} , \"{textString}\")\n")
       if (len(textString)> 250):
           print(f"Too long text2 {len(textString)} chars: ' {textString}'")
       if comma == "" :
           comma = ","
    f.write("]\n")

with open(outpath+"text1.txt", "w", encoding="utf-8") as f:
    f.write("-- -*- haskell -*-\n")
    f.write("[")
    comma = ""
    for textString in texts1:
       text = texts1[textString]
       f.write(f"{comma} ({text['id']} , {json.dumps(textString, ensure_ascii=False)})\n")
       if (len(textString)> 250):
           print(f"Too long text1 {len(textString)} chars: '{textString}'")
       if comma == "" :
           comma = ","
    f.write("]\n")

with open(outpath+"help.txt", "w", encoding="utf-8") as f:
    f.write("-- -*- haskell -*-\n")
    f.write("[")
    comma = ""
    for roomName in rooms:
        room = rooms[roomName]
        f.write(f"{comma}")
        f.write(f"  0  -- ROOM {room['id']} {roomName}\n")
        if comma == "" :
            comma = ","
    f.write("]\n")