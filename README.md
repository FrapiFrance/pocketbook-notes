# pocketbook-notes
Tool to extract and insert notes &amp; highlights from a Pocketbook e-reader to another

# Extract
Take a `books.db` file (typically found on `/mnt/ext1/system/config/`), and extract all notes and highlights into a notes.json file (deduplicated as far as we can)

caveats : 
When getting `books.db`, just make sure (for instance by rebooting the reader before) that all the [wal](https://www.sqlite.org/wal.html) are actually synced into `books.db`, so no more `books.db-wal` or `books.db-shm` in `/mnt/ext1/system/config/`

# Import
Given a `books.db` file and a notes.json file, add these into `books.db`.
You will have to put back `books.db` file on reader's `/mnt/ext1/system/config/`

Caveats : notes from notes.json from a book never opened on `books.db`'s reader (same Title/Author) won't be inserted


# technical notes
The books.db can actually be read & write 

copy books.db on a computer
any sqlite editor allows you to add notes or highlights.

1) create a new item, 
ParentID : book's OID
TypeID : 4 (book_mark)
State : 0 (?)
TimeAlt : a timestamp
HashUUID : an UUID

2) Then create parts in Tags
For note : 
ItemId : item's OID you just created
TagID : 101 (for book_mark)
Val : json, eg {"anchor":"pbr:/word?page=1&offs=398","created":1687936650}, with pos on the book (page/offset) and same timestamp
TimeEdt : same timestamp

then
TagId : 102 (for type)
Val : note

TagId : 104 (for quotation)
Val : json, eg {"begin":"pbr:/word?page=1&offs=398","end":"pbr:/word?page=1&over=484","text":"Nous avons toujours cru que les vies de nos enfants seraient meilleures que les nôtres."} ( ! no timestamp there)

TagID : 105 (for text)
Val : json eg  {"text":"Et maintenant en 2023 on en est encore plus sûrs !"}

_(optional I think)
TagID : 106 (for color)
val: cian_

For highlight : same, but no 105, and 102 is "highlight"

Then copy back books.db on reader's  /mnt/ext1/system/config/

Definitely, it's not easy from a printed book to identify page & offset, but in my case I wanted to re-insert notes from a previous reader's books.db database, so it's OK.

Caveats : 
- Not quite sure how we should build UUID, when from scratch... might be dependent from other fields ?
- I had it work on my PB632 (french vivlio version, with poscketbook ROM ROM 6.7.1706 and [rooted](https://github.com/ezdiy/pbjb) YMMV, SGDG, toussa
