#!/usr/bin/env python3
import psycopg2 as psycopg
import csv
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
psqlname = os.getenv("POSTGRES_DB")
psqluser = os.getenv("POSTGRES_USER")
psqlpass = os.getenv("POSTGRES_PASSWORD")

with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
    with conn.cursor() as cur:
        cur.execute("""
               create table if not exists shop(
                   id int,
                   name text,
                   description text,
                   price int);
               create table if not exists inventory(
                   unique_id serial primary key,
                   user_id text,
                   item_id int);
               create table if not exists queue(
                   unique_id serial primary key,
                   user_id text,
                   item_id int);
               create table if not exists timer(
                   unique_id serial primary key,
                   user_id text,
                   item_id int,
                   time int);

                    """)
        conn.commit()
        with open("shop.csv","r") as shopfile:
            shopreader = csv.DictReader(shopfile)
            for row in shopreader:
                cur.execute("""
                    DO
                    $do$
                    BEGIN
                            IF NOT EXISTS (SELECT * FROM shop WHERE id = %s) THEN
                            INSERT INTO shop (id, name, description, price) VALUES (%s, %s, %s, %s);
                        END IF;
                    END
                    $do$
                    """, (row['id'],row['id'],row['name'],row['description'],row['price']))
        conn.commit()

def print_shop():
    with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
        with conn.cursor() as cur:
            returnstring = ""
            cur.execute('select * from shop order by price;')
            shopitems=cur.fetchall()
            for item in shopitems:
                #returnstring += f"\n{item[0]}) {item[1]}: {item[2]} ({item[3]} fih)"
                returnstring += f"\n- {item[1]}: {item[2]} ({item[3]} fih)"
            return returnstring

def print_inventory(user):
    with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
        with conn.cursor() as cur:
            returnstring = ""
            cur.execute('''select shop.name from inventory
                            join shop on inventory.item_id = shop.id
                            join fishy on inventory.user_id = fishy.id
                            where inventory.user_id = %s
                        ''', (str(user.id),))
            shopitems=cur.fetchall()
            if (not shopitems):
                return "You have no items!"
            for item in shopitems:
                #returnstring += f"\n{item[0]}) {item[1]}: {item[2]} ({item[3]} fih)"
                returnstring += f"\n- {item[0]}"
            return returnstring

def buy_item(userid,itemname):
    with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
        with conn.cursor() as cur:
            cur.execute('select * from shop where lower(name) like lower(%s)',(itemname,))
            item = cur.fetchone()
            if (not item):
                return 1
            cur.execute('select fishies from fishy where id like %s', (userid,))
            wallet = cur.fetchone()
            if (not wallet):
                return 2
            if (wallet[0] < item[3]):
                return 3
            cur.execute('insert into inventory (user_id, item_id) values (%s, %s);',(userid,item[0]))
            cur.execute('update fishy set fishies = %s where id like %s',(wallet[0]-item[3],userid))
            conn.commit()
            return item[1]
            
def use_item(user,itemname):
    with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
        with conn.cursor() as cur:
            cur.execute('select * from shop where lower(name) like lower(%s)',(itemname,))
            item = cur.fetchone()
            if (not item):
                return -1
            cur.execute('select unique_id, item_id from inventory where item_id = %s and user_id like %s;',(item[0], str(user.id)))
            useditem=cur.fetchone()
            if (not useditem):
                return -2
            conn.commit()
            return useditem

def delete_item(itemid):
    with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
        with conn.cursor() as cur:
            cur.execute('delete from inventory where unique_id = %s',(itemid,))
            conn.commit()

def cast_item(userid,itemid):
    with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
        with conn.cursor() as cur:
            cur.execute('insert into queue (user_id, item_id) values (%s, %s);',(userid,itemid))
            print(f"added {itemid} to queue for {userid}")
            conn.commit()
            return True

def start_timer(userid,itemid):
    with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
        with conn.cursor() as cur:
            cur.execute('insert into timer (user_id, item_id, time) values (%s, %s, %s);',(userid,itemid,int(datetime.now().timestamp())))
            conn.commit()

def check_timer(userid,itemid):
    with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
        with conn.cursor() as cur:
            cur.execute('select item_id, time from timer where user_id like %s and item_id = %s',(userid,itemid,))
            timer = cur.fetchone()
            if not(timer):
                return False
            elif(timer[0] == 5):
                if(int(datetime.now().timestamp() - timer[1] > 86400)):
                    cur.execute('delete from timer where user_id = %s and item_id = %s',(userid,itemid,))
                    return False
                else:
                    return True
            conn.commit()

def popQueue(user):
    with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
        with conn.cursor() as cur:
            cur.execute('select * from queue where user_id like %s',(str(user.id),))
            item = cur.fetchone()
            if (not item):
                return False
            else:
                cur.execute('delete from queue where unique_id = %s',(item[0],))
                conn.commit()
                return item
