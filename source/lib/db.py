#!/bin/python
# -*- coding: utf-8 -*-

import sqlite3
from typing import *

import settings
import json

conn: sqlite3.Connection = None

OBJ_BOOK_MARK_TYPE_ID = 4

def create_connection(db_file = settings.DEFAULT_DB_FILE):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    global conn
    if conn is not None:
        return conn
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.DatabaseError as e:
        print(e)
    return conn

def select_notes(ignore_types : List[str] = [], verbose=False):
    """gives list of notes with all details

    Args:
        ignore_types (List[str], optional): list of ignored types (as stored in tag 102). Defaults to [].
        verbose (bool, optional): shall we print the results. Defaults to False.
    """    
    ignore_str = "('" + "', '".join(ignore_types) + "')"
    
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(f"""select  Title, Authors, Items.OID, Items.hashUUID, Items.TimeAlt, Items.State from 
Books inner join items on Items.ParentID = Books.OID inner JOIN tags on tags.ItemID = Items.OID
where items.TypeID=4
and TagID=102 and Tags.Val in ('highlight','note','bookmark') -- I've found 2 'draws' on my PB632, also; discarded
and Tags.Val not in {ignore_str}
order by title, items.OID, title;""")

    rows = cur.fetchall()

    if verbose:
        for row in rows:
            print(row)
    return rows

def select_note_details(item_id=None, verbose=False):
    """
    gives list of notes with all details
    
    :param item_id: str/int with the OID of the item
    :param verbose: shall we print the results
    :return: json dict with type, postion, and for notes (not highlights) text
    """
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("select TagID, Val from Tags where TagID and ItemID =? order by TagID""", (item_id,))

    rows = cur.fetchall()
    
    note={}
    is_highlight = False
    if verbose:
        print()
    for tag_id, val in rows:
        if verbose:
            print((tag_id,val))
        if tag_id == 101:
            # 101	bm.book_mark
            # anchor; seems duplicate with quotation's "begin" (for highlights and notes ; may be useful for bookmarks)
            note['anchor'] = json.loads(val)
        elif tag_id == 102:
            # 102	bm.type
            note['type'] = val
        elif tag_id == 103:
            # 103	bm.subtype
            # unused on my PB632
            note['subtype'] = val
        elif tag_id == 104:
            # 104	bm.quotation
            note['quotation'] = json.loads(val)
        elif tag_id == 105:
            # 105	bm.note
            # for notes, 104 with quotation, 105 with note's text
            # I have at least 1 bm with type 'highlight' AND a 105 with empty json, no 'text' element
            json_data = json.loads(val)
            if 'text' in json_data:
                note['text'] = json_data
        elif tag_id == 106:
            # 106	bm.color
            # colour; not very useful for b&w readers... frequently there for highlight, not for note. values : cian, yellow
            note['color'] = val
        elif tag_id == 107:
            # 107	bm.icon
            # unused on my PB632
            note['icon'] = val
        elif tag_id == 108:
            # 108	bm.voice
            # unused on my PB632
            note['voice'] = val
        elif tag_id == 109:
            # 109	bm.image
            # unused on my PB632
            note['image'] = val
    return note  


book_id_cache = {}
def get_book(author : str, title : str, verbose : bool =False):
    """get book id on target database

    Args:
        author (str): author's name
        title (str): book's title
        verbose (bool, optional): shall we tell that we found it. Defaults to False.
    """    
    global book_id_cache
    if f"{title}_|_{author}" in book_id_cache:
        return book_id_cache[f"{title}_|_{author}"]
    
    conn = create_connection()
    cur = conn.cursor()
    if author != "None":
        cur.execute("select OID from Books where Title = ? and  Authors = ? ", (title,author))
    else:
        cur.execute("select OID from Books where Title = ? ", (title,))

    rows = cur.fetchall()
    
    if len(rows) == 1:
        if verbose:
            print(f"Book {author} - {title} found : {rows[0][0]}")
        book_id_cache[f"{title}_|_{author}"] = rows[0][0]
        return(rows[0][0])
    elif len(rows) > 1:
        raise(RuntimeError(f"Found two books {author} - {title} in target database ! - aborting"))
    return None
    
def add_item(book_id, note_uuid, timestamp, state, dry_run: bool=False, commit: bool=True):
    conn = create_connection()
    cur = conn.cursor()
    if not(dry_run):
        # some state are 0, some are 2... don't what it means. shall we keep it unchanged ?
        # actuallyn state 2 seems hidden. Will force state to 0 for all according to FORCE_0_STATE
        if settings.FORCE_0_STATE:
            state=0

        cur.execute("""insert into Items(ParentID, TypeID, State, TimeAlt, HashUUID)  values(?,?,?,?,?)""",
                    (book_id, OBJ_BOOK_MARK_TYPE_ID, state, timestamp, note_uuid))
        if commit:
            conn.commit()
    return cur.lastrowid
    
def add_note_details(item_id, note, dry_run: bool=False, commit: bool=True):
    conn = create_connection()
    cur = conn.cursor()
    if not(dry_run):
        if 'anchor' in note:
            cur.execute("""insert into Tags(ItemID, TagID, Val, TimeEdt)  values(?,?,?,?)""", 
                        (item_id, 101, json.dumps(note['anchor'], ensure_ascii=False), note['timestamp']))
        if 'type' in note:
            cur.execute("""insert into Tags(ItemID, TagID, Val, TimeEdt)  values(?,?,?,?)""", 
                        (item_id, 102, note['type'], note['timestamp']))
        if 'subtype' in note:
            cur.execute("""insert into Tags(ItemID, TagID, Val, TimeEdt)  values(?,?,?,?)""", 
                        (item_id, 103, note['tsubype'], note['timestamp']))
        if 'quotation' in note:
            cur.execute("""insert into Tags(ItemID, TagID, Val, TimeEdt)  values(?,?,?,?)""", 
                        (item_id, 104, json.dumps(note['quotation'], ensure_ascii=False), note['timestamp']))
        if 'text' in note:
            cur.execute("""insert into Tags(ItemID, TagID, Val, TimeEdt)  values(?,?,?,?)""", 
                        (item_id, 105, json.dumps({ 'text': note['text']}, ensure_ascii=False), note['timestamp']))
        if 'color' in note:
            cur.execute("""insert into Tags(ItemID, TagID, Val, TimeEdt)  values(?,?,?,?)""", 
                        (item_id, 106, note['color'], note['timestamp']))
        if 'icon' in note:
            cur.execute("""insert into Tags(ItemID, TagID, Val, TimeEdt)  values(?,?,?,?)""", 
                        (item_id, 107, note['icon'], note['timestamp']))
        if 'voice' in note:
            cur.execute("""insert into Tags(ItemID, TagID, Val, TimeEdt)  values(?,?,?,?)""", 
                        (item_id, 108, note['voice'], note['timestamp']))
        if 'image' in note:
            cur.execute("""insert into Tags(ItemID, TagID, Val, TimeEdt)  values(?,?,?,?)""", 
                        (item_id, 109, note['image'], note['timestamp']))
        
        if commit:
            conn.commit()
    return cur.lastrowid