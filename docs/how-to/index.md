# How-to guides

One question a project meets, answered in a few steps. Each assumes the
library is [installed](../getting-started/installation.md).

| | |
|---|---|
| [Adopt it in an existing project](adopt.md) | a project with an envelope of its own - what changes for its clients, and in what order |
| [Read the envelope from a frontend](frontend.md) | types, one fetch function, a pager for both kinds, a form's errors |
| [Choose how a list is paged](choose-a-page.md) | by number or by cursor, its size, the client's say, and no pages at all |
| [Write your own errors](own-errors.md) | a `DomainError` with `data`, raised from a service, a task or a command |
| [Rename the error codes](rename-error-codes.md) | for a client that already branches on other words |
| [Leave a view out of the envelope](leave-a-view-out.md) | a webhook, a health check, a file |
| [Report bugs to Sentry](report-bugs.md) | the `REPORTER`, the log, and `DEBUG` |
| [Answer a database constraint](database-constraints.md) | two requests taking the same name at once |
| [Use your own schema class or handler](own-schema-or-handler.md) | with an `AutoSchema` or an exception handler of the project's |
| [Test an API in the envelope](testing.md) | reading answers as a client does |
