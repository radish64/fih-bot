#!/usr/bin/env python3
import psycopg2 as psycopg
import csv
from datetime import datetime

psqlname = "YOUR POSTGRES DATABASE"
psqluser = "YOUR POSTGRES USERNAME"
psqlpass = "YOUR POSTGRES PASSWORD"

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
            cur.execute('select * from shop;')
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
                            join fishy on inventory.user_id = fishy.id;
                        ''')
            shopitems=cur.fetchall()
            if (not shopitems):
                return "You have no items!"
            for item in shopitems:
                #returnstring += f"\n{item[0]}) {item[1]}: {item[2]} ({item[3]} fih)"
                returnstring += f"\n- {item[0]}"
            return returnstring

def buy_item(user,itemname):
    with psycopg.connect(dbname=psqlname, user=psqluser, host='localhost', password=psqlpass) as conn:
        with conn.cursor() as cur:
            cur.execute('select * from shop where lower(name) like lower(%s)',(itemname,))
            item = cur.fetchone()
            if (not item):
                return 1
            cur.execute('select fishies from fishy where id like %s', (str(user.id),))
            wallet = cur.fetchone()
            if (not user):
                return 2
            if (wallet[0] < item[3]):
                return 3
            cur.execute('insert into inventory (user_id, item_id) values (%s, %s);',(str(user.id),item[0]))
            cur.execute('update fishy set fishies = %s where id like %s',(wallet[0]-item[3],str(user.id)))
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

