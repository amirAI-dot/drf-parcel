# Security

Report a vulnerability privately, through GitHub's *Report a vulnerability*
on the repository's Security tab - not in a public issue.

## What the library does for you

* **A bug never tells its secrets.** An unexpected exception answers a
  generic sentence; its text - a query, a path, a person's details - stays in
  the log.
* **A 404 says nothing of what was looked for.** Django's text names the
  model; the answer does not.
* **The database's words stay in the database.** A constraint is answered by
  its kind, never its text, a column's or a constraint's name.
* **A client cannot read a whole table.** Every page size a client chooses
  has a ceiling, and none can be switched off.

## What it does not do

`data` leaves the server as it was raised: put in it only what the person
asking may read.
