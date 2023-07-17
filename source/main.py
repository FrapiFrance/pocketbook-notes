#!/bin/python
# -*- coding: utf-8 -*-

from lib.db import *
from optparse import OptionParser
import json



def export_as_json():
    notes = {}
    for (title, author, item_id, item_uuid, item_timestamp) in select_notes(verbose=False):
        #print(note)
        if f"{title}_|_{author}" not in notes:
            # book not already listed
            notes[f"{title}_|_{author}"] = {}
        # get note detail
        notes[f"{title}_|_{author}"][item_uuid] = select_note_details(item_id=item_id, verbose=False)
        notes[f"{title}_|_{author}"][item_uuid]['timestamp'] = item_timestamp
        
    return notes
        
def import_notes_into_database(json_data:json, dry_run: bool=False, verbose: bool=False, skip: bool=False):
    for book in json_data:
        title, author = book.split('_|_')
        book_id = get_book(author, title, verbose=verbose)
        if book_id is None:
            message = f"Book {author} - {title} not found in target database ! upload it to reader, open it, and get database again"
            if skip:
                if verbose:
                    print("WARNING",message)
                continue
            else:
                raise(RuntimeWarning(message))
        # should we create it ?

        if verbose:
            print(book, author, title, book_id)
        for note in json_data[book]:
            if verbose:
                print(' '*4, note)
            # TODO check if this note already exists on target DB : book (thru l'item), type, highlighted text, text (for notes) 
            # ; maybe check also page and/or portion of quotation ?
            # if already there, continue
            # add item linked to book, with given UUID and timestamp
            # add tags : 102 104 and 105, same timestamp


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
        "--skip-unknown",
        action="store_true",
        dest="SKIP",
        default=False,
        help="skip unknown books",
    )
    parser.add_option(
        "-v",
        "--verbose",
        action="store_true",
        dest="VERBOSE",
        default=False,
        help="print data",
    )
    parser.add_option(
        "--dry-run",
        action="store_true",
        dest="DRY_RUN",
        default=False,
        help="do not alter target database (for import). default False",
    )
    (options, args) = parser.parse_args()
    create_connection(db_file=options.DB_FILE)
    if options.ACTION == 'export':
        json_data = export_as_json()
        if options.VERBOSE:
            print(json.dumps(json_data, sort_keys=False, indent=4, ensure_ascii=False ))
        if not options.DRY_RUN:
            with open(options.JSON_FILE, "w", encoding="utf8") as f:
                # not readable json.dump(json_data, f, ensure_ascii=False)
                f.write(json.dumps(json_data, sort_keys=False, indent=4, ensure_ascii=False ))
    else:
        with open(options.JSON_FILE, "r", encoding="utf8") as json_file:
            json_data = json.load(json_file)
        import_notes_into_database(json_data=json_data, dry_run=options.DRY_RUN, verbose=options.VERBOSE, skip=options.SKIP)

 
    



print('done')