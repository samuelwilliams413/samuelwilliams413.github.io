#!/usr/bin/env python3

from pathlib import Path

def strip_all(string):
    return ''.join(e for e in string if e.isalnum())


file_cont = Path("prip.log").open().read().split("(Click to view large version)")
add = False
weapons = []
for line in file_cont:
    if add:
        weapons.append(line.strip())
    add = not add

def grab_value(line, delim):
    return line.split("%",1)[0].split(delim,1)[1].strip()

guns = {}
for arm in weapons:
    details = arm.splitlines()
    name = details[0]
    weapon = {'name': name}
    if name == "Bulldog-6":
        continue
    weapon['lore'] = details[1]

    for index,line in enumerate(details):
        if "inaccurateAccuracy" in line:
            weapon['accuracy'] = grab_value(line, "inaccurateAccuracy")
        if "operateHandling" in line:
            weapon['handling'] = grab_value(line, "operateHandling")
        if "fireDamage" in line:
            weapon['damage'] = grab_value(line, "fireDamage")
        if "Fire Rate" in line:
            weapon['rof'] = grab_value(line, "Fire Rate")
        if "DurabilityDurability" in line:
            weapon['durability'] = details[index + 2].strip()[:-1]
        if "conditionRepair" in line:
            weapon['repair'] = line.split("RU",1)[0].split("conditionRepair",1)[1].strip()
        if "(when empty)Weight" in line:
            weapon['weight'] = line.split("kg",1)[0].split("(when empty)Weight",1)[1].strip()
        if "Ammunition" in line:
            weapon['capacity'] = str([s for s in details[index + 1].split() if s.isdigit()][0])
            weapon['ammunition'] = details[index + 2].strip()
    guns[strip_all(name)] = weapon


    #print(weapon)

from bs4 import BeautifulSoup
merchant_cont = Path("Prices.html").open().read()
soup = BeautifulSoup(merchant_cont, 'html.parser')
for s in soup.find_all('tr'):
    for t in s.find_all('td'):
        ass = s.find_all('a')
        if ass:
            name = strip_all(ass[0].get('name', ""))
            href = ass[1].get('href')
        prices = t.find_all('td')
        
        if len(prices) > 1:
            buying = prices[1]
            if "Buying price (Non-trader)" in buying.get("title"):
                price = buying.text
                try:
                    if price != "-":
                        guns[name]['price'] = round(2.5 * int(price.strip().replace(",","")), -1)
                        guns[name]['href'] = href.strip()
                except KeyError:
                    pass


r1 = "Short (25m)"
r2 = "Medium (100m)"
r3 = "Long (500m)"
r4 = "Ultralong: 0/0/0"
r5 = "Short (25m), 1/2 on miss when in melee"
ammo = {
    strip_all(".45 ACP rounds"): r2,
    strip_all("9x18 mm rounds"): r1,
    strip_all("9x19mm FMJ"): r1,
    strip_all("12x70 shot rounds"): r5,
    strip_all("5.45x39 mm rounds"): r2,
    strip_all("5.56x45 mm rounds"): r2,
    strip_all("9x39 mm SP-5 rounds"): r3,
    strip_all("7.62x54 PP rounds"): r2,
    strip_all("7.62x54 mm 7H1 rounds"): r3,
    strip_all("Batteries"): r4,
}
with open('somefile.md', 'w') as the_file:
    for gun, stuff in guns.items():
        try:
            if gun not in ["Bulldog6", "StrelokSGI5k", "ZulusRP74", "HonoraryPMm", "SVU2A", "Lynx", "Alpine", "Storm", "Frasier", "March"] and stuff.get('price'):
                def tfwri(string):
                    the_file.write(f"{string}\n")
                href = stuff.get('href', f'http://cop.zsg.dk/Items_Weapons.php#{gun}')
                name = stuff.get('name')
                url_name = name.replace(" ", "_").replace("/", "")
                hit = int((float(stuff['accuracy'])) / 20)
                pen = int((100 - float(stuff['handling'])) / 20)
                effective = ammo[strip_all(stuff['ammunition'])]
                rof = int((float(stuff['rof'])) / 20) + 1
                dam = int((float(stuff['damage'])) / 5)
                jam = int(float((stuff.get('durability', 0))))


                standing = hit
                prone = standing * 2
                walking = -pen
                running = min(2 * walking, -1)
                def hit_crit(tohit):
                    jam = 0 + tohit
                    std = 10 - tohit
                    crit = 20 - tohit
                    return f"{std} / {crit}"


                tfwri(f"## [{name}]({href})")
                tfwri(f"> {stuff['lore']}")
                tfwri(f"")
                tfwri(f'![image](http://cop.zsg.dk/Resources/Items/Weapons/{url_name}_Large.jpg "{name}")\n')
                tfwri(f"")
                tfwri(f"- **To Hit**: Bonus (to hit / to crit)")
                tfwri(f"    - **Prone**:    \t{prone}\t({hit_crit(prone)})")
                tfwri(f"    - **Standing**: \t{standing}\t({hit_crit(standing)})")
                tfwri(f"    - **Walking**:  \t{walking}\t({hit_crit(walking)})")
                tfwri(f"    - **Running**:  \t{running}\t({hit_crit(running)})")
                tfwri(f"- **Range**: {effective}")
                tfwri(f"- **Damage**: {rof}d6 + {dam}")                
                tfwri(f"- **Jam Chance**: {jam}% on a 1 or less")
                tfwri(f"- **Weight**: {stuff['weight']} kgs")
                tfwri(f"- **Price**: {stuff.get('price')} RU")
                tfwri(f"- **Ammo**: {stuff['capacity']} ({stuff['ammunition']})")
                tfwri(f"")
        except Exception as e:
            print(stuff)
            raise e
