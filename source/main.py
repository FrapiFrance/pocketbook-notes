#!/bin/python
# -*- coding: utf-8 -*-

from optparse import OptionParser
from copy import deepcopy

from lib.db import *
from lib.json_utils import *


def _get_note_un_timestamped_json_copy(dict_ref):
    """Copy except timestamp and dates

    Args:
        dict_ref (json): a note json

    Returns:
        _type_: deepcopy of dict_ref note, without any time-related element (AFAIK)
    """
    note = deepcopy(dict_ref)
    note.pop('timestamp', None)
    if 'anchor' in note:
        note['anchor'].pop('created', None)
        note['anchor'].pop('updated', None)
    if 'quotation' in note:
        note['quotation'].pop('updated', None)
    return note

def export_as_json(ignore_types : List[str] = []):
    """Build a json with all relevant data from notes of the database

    Args:
        ignore_types (List[str], optional): list of ignored types (as stored in tag 102). Defaults to [].

    Returns:
        json: a json describing all notes
    """
    notes = {}
    for (title, author, item_id, item_uuid, item_timestamp, item_state) in select_notes(ignore_types, verbose=False):
        #print(note)
        if f"{title}_|_{author}" not in notes:
            # book not already listed
            notes[f"{title}_|_{author}"] = {}
        # get note detail
        notes[f"{title}_|_{author}"][item_uuid] = select_note_details(item_id=item_id, verbose=False)
        notes[f"{title}_|_{author}"][item_uuid]['timestamp'] = item_timestamp
        notes[f"{title}_|_{author}"][item_uuid]['state'] = item_state  # some are 0, some are 2... don't what it means. let us keep it unchanged
        
        my_current_note = _get_note_un_timestamped_json_copy(notes[f"{title}_|_{author}"][item_uuid])
        
        # now (could have been done before), let us check this content is not already in the list for this book
        duplicate = False
        for other_item_uuid in notes[f"{title}_|_{author}"]:
            if other_item_uuid == item_uuid:
                continue 
            other_note = _get_note_un_timestamped_json_copy(notes[f"{title}_|_{author}"][other_item_uuid])
                        
            if other_note == my_current_note:
                # duplicate
                duplicate = True
                break
        if duplicate:
            notes[f"{title}_|_{author}"].pop(item_uuid)
    return notes
        
def import_notes_into_database(json_data:json, ignore_types : List[str] = [], dry_run: bool=False, verbose: bool=False, skip_unknown_books: bool=False):
    """import notes into target database

    Args:
        json_data (json): a json describing all notes
        ignore_types (List[str], optional): list of ignored types (as stored in tag 102). Defaults to [].
        dry_run (bool, optional): do not alter database. Defaults to False.
        verbose (bool, optional): print warnings and data. Defaults to False.
        skip_unknown_books (bool, optional): skip books unknown in target database. Defaults to False.
    """
    target_database_existing_notes = export_as_json(ignore_types=ignore_types)
    
    unknown_books = list()
    for book in json_data:
        title, author = book.split('_|_')
        stop = 5 # FIXME
        if verbose:
            print(author, title)
        for note_uuid in json_data[book]:
            if json_data[book][note_uuid]['type'] in ignore_types:
                continue
            
            # search book into new DB. we do it here so that if all notes are of an ignored type, a missing book is not a warning 
            book_id = get_book(author, title, verbose=verbose)
            if book_id is None and book not in unknown_books:
                unknown_books.append(book)
                message = f"Book {author} - {title} not found in target database ! upload it to reader, open it, and get database again"
                if skip_unknown_books:
                    if verbose:
                        print("WARNING",message)
                    continue
                else:
                    raise(RuntimeWarning(message))

            if verbose:
                print(' '*4, json_data[book][note_uuid])
            # check if this note already exists on target DB : 
            # TODO here we check full identity, maybe we should only check book , type, highlighted text, text (for notes) 
            # and **page** (or at least only a part of je position ['quotation']['begin'] ?)
            my_current_note = _get_note_un_timestamped_json_copy(json_data[book][note_uuid])            
            duplicate = False
            if f"{title}_|_{author}" in target_database_existing_notes:
                for other_item_uuid in target_database_existing_notes[f"{title}_|_{author}"]:
                    other_note = _get_note_un_timestamped_json_copy(target_database_existing_notes[f"{title}_|_{author}"][other_item_uuid])                            
                    if other_note == my_current_note:
                        # duplicate
                        duplicate = True
                        break
            if duplicate:
                # if already there, continue
                if verbose:
                    print("WARNING",f"Note {note_uuid} already there as {other_item_uuid} in target database")                    
                continue
            # Let us add this note in target database            
            # add item linked to book, with given UUID and timestamp
            conn = create_connection()
            item_id = add_item(book_id, note_uuid, json_data[book][note_uuid]['timestamp'], json_data[book][note_uuid]['state'], dry_run=dry_run, commit=False)
            # add tags : 102 104 and 105 and others, same timestamp
            add_note_details(item_id= item_id, note= json_data[book][note_uuid], dry_run=dry_run, commit=False)
            if not(dry_run):
                conn.commit()
                stop -= 1
                5/stop  # FIXME let us stop at 5th element, just to check all is OK so far...

if __name__ == "__main__":
    parser = OptionParser("""Export/import pocketbook notes
        export: take books.db file (typically found on /mnt/ext1/system/config/), and extract all notes and highlights into a notes.json file (deduplicated as far as we can)
        import: given a books.db file and a notes.json file, add these into books.db. You will have to put back books.db file on reader's /mnt/ext1/system/config/
        """)
    parser.add_option(
        "-a",
        "--action",
        dest="ACTION",
        default='export',
        help="export from or import to a DB file (default export)",
    )
    parser.add_option(
        "-d",
        "--db-file",
        dest="DB_FILE",
        default=settings.DEFAULT_DB_FILE,
        help=f"DB file, default {settings.DEFAULT_DB_FILE}",
    )
    parser.add_option(
        "-j",
        "--json-file",
        dest="JSON_FILE",
        default=settings.DEFAULT_JSON_FILE,
        help=f"json file, default {settings.DEFAULT_JSON_FILE}",
    )
    parser.add_option(
        "-s",
        "--skip-unknown-books",
        action="store_true",
        dest="SKIP_UNKNOWN_BOOKS",
        default=False,
        help="skip unknown books, default False.",
    )
    parser.add_option(
        "-i",
        "--ignore-type",
        action="append",
        dest="IGNORE_TYPES",
        type="str",
        help="ignore some types (among bookmark highlight note)",
    )
    
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="VERBOSE",
        default=True,
        help="do not print data and warnings, default to print",
    )
    parser.add_option(
        "--dry-run",
        action="store_true",
        dest="DRY_RUN",
        default=False,
        help="do not alter target database (for import). default False",
    )
    (options, args) = parser.parse_args()
    conn = create_connection(db_file=options.DB_FILE)
    if options.ACTION == 'export':
        json_data = export_as_json(ignore_types=options.IGNORE_TYPES)
        if options.VERBOSE:
            print_json(json_data)
        if not options.DRY_RUN:
            with open(options.JSON_FILE, "w", encoding="utf8") as f:
                #  json.dump(json_data, f, ensure_ascii=False) :  not readable because not formatted, so we force a nice format
                f.write(print_json(json_data, quiet=True))
    else:
        with open(options.JSON_FILE, "r", encoding="utf8") as json_file:
            json_data = json.load(json_file)
        import_notes_into_database(json_data=json_data, ignore_types=options.IGNORE_TYPES, dry_run=options.DRY_RUN, verbose=options.VERBOSE, skip_unknown_books=options.SKIP_UNKNOWN_BOOKS)

    conn.close()
    print('done')