import sqlite3
from typing import *

import settings
import json

conn: sqlite3.Connection = None

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

def select_full_notes_desc(verbose=False):
    """
    gives list of notes with related books info
    :param verbose: shall we print the results
    :return: rows
    """
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""select OID, Title, Authors, item, json_extract(Highlight, '$.text') as Text, substr(json_extract(Highlight, '$.begin'),16,
			max(instr(json_extract(Highlight, '$.begin'),'&')-16 ,2)

			) as Page, json_extract(Highlight, '$.updated') as Date,  Highlight from 
Books inner join 
(select OID as BookID, item, Highlight from 
	Items inner join 
	(select ParentID, Items.OID as item, Highlight from 
		Items inner join 
			(select ItemID, Val as Highlight from 
				Tags 
				where TagID in (104, 105) and json_extract(Val,'$.text') <> "Bookmark"
			) as Highlights
		on Highlights.ItemID = OID
		) as Highlights
	on Highlights.ParentID = OID) as Highlights 
on BookID = OID order by title, oid, item;""")

    rows = cur.fetchall()

    if verbose:
        for row in rows:
            print(row)
    return rows

def select_notes(verbose=False):
    """
    gives list of notes with all details
    :param verbose: shall we print the results
    :return: rows
    """
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""select  Title, Authors, items.OID, hashUUID, TimeAlt from 
Books inner join items on Items.ParentID = Books.OID inner JOIN tags on tags.ItemID = Items.OID
where items.TypeID=4
and TagID=102 and Tags.Val in ('highlight','note')
order by items.OID, title;""")

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
                note['text'] = json_data['text']
        elif tag_id == 106:
            # 106	bm.color
            # colour; not very useful for b&w readers...
            note['color'] = val
        elif tag_id == 107:
            # 107	bm.icon
            # unused on my PB632
            note['icon'] = val
        elif tag_id == 108:
            # 108	bm.voice
            # 109	bm.image
            # unused on my PB632
            note['voice'] = val
        elif tag_id == 109:
            # 109	bm.image
            # unused on my PB632
            note['image'] = val
    return note  

def get_book(author : str, title : str, verbose : bool =False):
    """get book id on target database

    Args:
        author (str): author's name
        title (str): book's title
        verbose (bool, optional): shall we tell that we found it. Defaults to False.
    """    
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("select OID from Books where Title = ? and  Authors = ? ", (title,author))

    rows = cur.fetchall()
    
    if len(rows) == 1:
        if verbose:
            print(f"Book {author} - {title} found : {rows[0][0]}")
        return(rows[0][0])
    elif len(rows) > 1:
        raise(RuntimeError(f"Found two books {author} - {title} in target database ! - aborting"))
    return None
    
