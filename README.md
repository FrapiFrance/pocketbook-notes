# pocketbook-notes
Tool to extract and insert notes &amp; highlights from a Pocketbook (also known as Vivlio in France) e-reader to another

# Extract
Take a `books.db` file (typically found on `/mnt/ext1/system/config/`), and extract all notes and highlights into a notes.json file (deduplicated as far as we can)

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
