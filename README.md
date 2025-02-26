# pocketbook-notes
Tool to extract and insert notes &amp; highlights from a Pocketbook (also known as Vivlio in France) e-reader to another

TL;DR Usage:
1. reboot your legacy e-reader
2. copy legacy reader's `/mnt/ext1/system/config/books.db` into a `run` directory to be created next to `source`
3. run `python source/main.py` (some other options can be interesting, see `python source/main.py -h`)
4. reboot your target e-reader
5. copy target reader's `/mnt/ext1/system/config/books.db` into `run` directory
6. run `python source/main.py -a import -s -- dry-run|grep WARNING` (some other options can be interesting, see `python source/main.py -h`)
7. on target e-reader, **open** all missing books if you want its notes to be imported
8. run again 4. to 7. until you are OK. *You may also alter `run/notes.json` file if author and/or titles are different for same book between legacy and target e-reader, or to delete some useless notes...*
9. run a definitive `python source/main.py -a import`
10. copy `run/books.db` into target reader's `/mnt/ext1/system/config/books.db`
11. reboot your target e-reader
12. pray and/or enjoy



# Extract
Take a `books.db` file (typically found on `/mnt/ext1/system/config/`; this can also be `/system/profiles/default/`, especially for recent devices, I was said), and extract all notes and highlights into a notes.json file (deduplicated as far as we can)

caveats : 
When getting `books.db`, just make sure (for instance by rebooting the reader before) that all the [wal](https://www.sqlite.org/wal.html) are actually synced into `books.db`, so no more `books.db-wal` or `books.db-shm` in `/mnt/ext1/system/config/`
# Import
Given a `books.db` file and a notes.json file, add these into `books.db`.
You will have to put back `books.db` file on reader's `/mnt/ext1/system/config/`

Caveats : notes from notes.json from a book never opened on `books.db`'s reader (same Title/Author) won't be inserted

Definitely, it's not easy from a printed book to identify page & offset in order to uild a notes.json file, but in my case I wanted to re-insert notes from a previous reader's books.db database, so it's OK.

# technical notes
Caveats : 
- Not quite sure how we should build UUID, when from scratch... might be dependent from other fields ? => by default, let us keep the same as in the original db
- I had it work on my PB632 (french vivlio version, with pocketbook ROM 6.7.1706 and [rooted](https://github.com/ezdiy/pbjb)) YMMV, SGDG, toussa



devcontainer : 
- https://code.visualstudio.com/learn/develop-cloud/containers
- https://code.visualstudio.com/docs/python/python-tutorial
- https://code.visualstudio.com/docs/containers/quickstart-python
- https://github.com/microsoft/vscode-remote-try-python ?
