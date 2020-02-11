# Developed for module tiericide, this script will quickly print out a market
# conversion map based on patch notes, as well as database conversion mapping.

import argparse
import os.path
import sqlite3
import sys

# Add eos root path to sys.path so we can import ourselves
path = os.path.dirname(__file__)
sys.path.append(os.path.realpath(os.path.join(path, "..")))

# change to correct conversion

rename_phrase = " renamed to "
conversion_phrase = " converted to "

text = """
    Small Asymmetric Remote Capacitor Transmitter renamed to Small Radiative Scoped Remote Capacitor Transmitter
    Small 'Regard' Remote Capacitor Transmitter renamed to Small Inductive Compact Remote Capacitor Transmitter
    Medium Asymmetric Remote Capacitor Transmitter renamed to Medium Radiative Scoped Remote Capacitor Transmitter
    Medium 'Regard' Remote Capacitor Transmitter renamed to Medium Inductive Compact Remote Capacitor Transmitter
    Large Asymmetric Remote Capacitor Transmitter renamed to Large Radiative Scoped Remote Capacitor Transmitter
    Large 'Regard' Remote Capacitor Transmitter renamed to Large Inductive Compact Remote Capacitor Transmitter
    Small Partial E95a Remote Capacitor Transmitter converted to Small Radiative Scoped Remote Capacitor Transmitter
    Small Murky Remote Capacitor Transmitter converted to Small Inductive Compact Remote Capacitor Transmitter
    Medium Partial E95b Remote Capacitor Transmitter converted to Medium Radiative Scoped Remote Capacitor Transmitter
    Medium Murky Remote Capacitor Transmitter converted to Medium Inductive Compact Remote Capacitor Transmitter
    Large Partial E95c Remote Capacitor Transmitter converted to Large Radiative Scoped Remote Capacitor Transmitter
    Large Murky Remote Capacitor Transmitter converted to Large Inductive Compact Remote Capacitor Transmitter
    """

def main(old, new):
    # Open both databases and get their cursors
    old_db = sqlite3.connect(os.path.expanduser(old))
    old_cursor = old_db.cursor()
    new_db = sqlite3.connect(os.path.expanduser(new))
    new_cursor = new_db.cursor()

    renames = {}
    conversions = {}

    for x in text.splitlines():
        x = x.strip()
        if not x:
            continue
        if conversion_phrase in x:
            c = x.split(conversion_phrase)
            container = conversions
        elif rename_phrase in x:
            c = x.split(rename_phrase)
            container = renames
        else:
            print("Unknown format: {}".format(x))
            sys.exit()

        old_name, new_name = c[0], c[1]
        old_item, new_item = None, None

        if "Blueprint" in old_name or "Blueprint" in new_name:
            print("Blueprint: Skipping this line: %s"%x)
            continue

        # gather item info
        new_cursor.execute('SELECT "typeID" FROM "invtypes" WHERE "typeName" = ?', (new_name,))
        for row in new_cursor:
            new_item = row[0]
            break

        old_cursor.execute('SELECT "typeID" FROM "invtypes" WHERE "typeName" = ?', (old_name,))
        for row in old_cursor:
            old_item = row[0]
            break

        if not old_item:
            print("Error finding old item in {} -> {}".format(old_name, new_name))
        if not new_item:
            print("Error finding new item in {} -> {}".format(old_name, new_name))

        if not container.get((new_item,new_name), None):
            container[(new_item,new_name)] = []


        container[(new_item,new_name)].append((old_item, old_name))

    print("    # Renamed items")

    for new, old in renames.items():
        if len(old) != 1:
            print("Incorrect length, key: {}, value: {}".format(new, old))
            sys.exit()
        old = old[0]

        print("    \"{}\": \"{}\",".format(old[1], new[1]))

    # Convert modules
    print("\n    # Converted items")

    for new, olds in conversions.items():
        for old in olds:
            print("    \"{}\": \"{}\",".format(old[1], new[1]))

    print()
    print()

    for new, old in conversions.items():
        print("    {}: (  # {}".format(new[0], new[1]))
        for item in old:
            print("        {},  # {}".format(item[0], item[1]))
        print("    ),")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--old", type=str)
    parser.add_argument("-n", "--new", type=str)
    args = parser.parse_args()

    main(args.old, args.new)
