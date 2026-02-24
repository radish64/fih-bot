#!/usr/bin/env python3
import psycopg2 as psycopg
import random
import sys
import io
from datetime import datetime
from fihfile import fihfile

psqlname = "YOUR POSTGRES DATABASE"
psqluser = "YOUR POSTGRES USERNAME"
psqlpass = "YOUR POSTGRES PASSWORD"

fishies = fihfile("fishies.fih")
trash = fishies.getCategory("Trash")
common = fishies.getCategory("Common")
uncommon = fishies.getCategory("Uncommon")
rare = fishies.getCategory("Rare")
epic = fishies.getCategory("Epic")
legendary = fishies.getCategory("Legendary")
ultra = fishies.getCategory("Ultra")
special = fishies.getCategory("Special")

with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
    with conn.cursor() as cur:
        cur.execute("""
               create table if not exists fishy(
                   id text,
                   name text,
                   fishies int,
                   time int)
                   
                    """)

def catch_fish(user, modifier):
    diceRoll = random.randint(0,1000)
    diceRoll = min(diceRoll+modifier, 1000)
    minFishies = 0
    maxFishies = 0
    if (diceRoll <= 50):
        caughtFishy = trash[random.randint(0,len(trash)-1)]
        minFishies = 0
        maxFishies = 0
    elif (diceRoll <= 480):
        caughtFishy = common[random.randint(0,len(common)-1)]
        minFishies = 1
        maxFishies = 10
    elif (diceRoll <= 680):
        caughtFishy = uncommon[random.randint(0,len(uncommon)-1)]
        minFishies = 11 
        maxFishies = 30 
    elif (diceRoll <= 830):
        caughtFishy = rare[random.randint(0,len(rare)-1)]
        minFishies = 31 
        maxFishies = 50
    elif (diceRoll <= 930):
        caughtFishy = epic[random.randint(0,len(epic)-1)]
        minFishies = 51 
        maxFishies = 100 
    elif (diceRoll < 980):
        caughtFishy = legendary[random.randint(0,len(legendary)-1)]
        minFishies = 101
        maxFishies = 300
    elif (diceRoll < 990):
        caughtFishy = special[random.randint(0,len(special)-1)]
        match caughtFishy:
            case " Weed Carp":
                minFishies = 420
                maxFishies = 420
            case " Satan Fih":
                minFishies = 666
                maxFishies = 666
            case " Pro Shop Bass":
                minFishies = 670
                maxFishies = 670
            case " Angel Fih":
                minFishies = 999
                maxFishies = 999
    elif (diceRoll <= 1000):
        caughtFishy = ultra[random.randint(0,len(ultra)-1)]
        minFishies = 1000 
        maxFishies = 1000
    caughtFishies = random.randint(minFishies,maxFishies)
    #print("Caught " + str(caughtFishies) + " fishies")
    with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DO
                $do$
                BEGIN
                        IF NOT EXISTS (SELECT * FROM fishy WHERE id = %s) THEN
                        INSERT INTO fishy (id, fishies, time) VALUES (%s, 0, 0);
                    END IF;
                END
                $do$
                """, (str(user.id),str(user.id)))
            cur.execute("SELECT fishies FROM fishy WHERE id = %s", [str(user.id)])
            currentFishies = cur.fetchone()[0]
            cur.execute("UPDATE fishy SET fishies = %s WHERE id = %s;", (currentFishies + caughtFishies, str(user.id)))
            cur.execute("UPDATE fishy SET name = %s WHERE id = %s;", (str(user.display_name), str(user.id)))
            cur.execute("UPDATE fishy SET time = %s WHERE id = %s;", (int(datetime.now().timestamp()), str(user.id)))
            conn.commit()
            return [caughtFishy, caughtFishies]

def check_timestamp(user):
    with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DO
                $do$
                BEGIN
                    IF NOT EXISTS (SELECT * FROM fishy WHERE id = %s) THEN
                        INSERT INTO fishy (id, fishies, time) VALUES (%s, 0, 0);
                    END IF;
                END
                $do$
                """, (str(user.id),str(user.id)))
            cur.execute("SELECT time FROM fishy WHERE id = %s", [str(user.id)])
            return int(cur.fetchone()[0])

def print_db():
    with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
        with conn.cursor() as cur:
            returnstring = ""
            cur.execute('select name, fishies from fishy order by fishies desc;')
            shopitems=cur.fetchall()
            count = 1
            for item in shopitems:
                #returnstring += f"\n{item[0]}) {item[1]}: {item[2]} ({item[3]} fih)"
                returnstring += f"\n{count}) {item[0]}:    {item[1]} fih"
                count += 1
            return returnstring

def destroy_fish(uid,amount):
    with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
        with conn.cursor() as cur:
            cur.execute('select fishies from fishy where id like %s',(str(uid),))
            currentFishies = cur.fetchone()[0]
            print(currentFishies)
            newFishies = currentFishies - amount
            cur.execute('update fishy set fishies = %s where id like %s',(newFishies,str(uid)))
            conn.commit()

def nuke():
    with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
        with conn.cursor() as cur:
            cur.execute('update fishy set fishies = 0;')
            conn.commit()


def getAllUsers():
    with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
        with conn.cursor() as cur:
            cur.execute('select id from fishy;')
            return cur.fetchall()[0]

