# Read the envelope from a frontend

Every answer has the same top level, so a client needs one type, one fetch
function and one pager. TypeScript, though the shape is the same from any
language.

## The types

```typescript
type Page =
  | { type: 'page'; count: number; page: number; pages: number; page_size: number;
      has_next: boolean; has_previous: boolean }
  | { type: 'cursor'; next_cursor: string | null; previous_cursor: string | null;
      page_size: number; has_next: boolean; has_previous: boolean };

type Success<T> = { success: true; status_code: number; message: string; data: T;
                    pagination?: Page };

type Failure = { success: false; status_code: number; message: string; error_code: string;
                 data: { fields?: Record<string, { code: string; message: string }[]> }
                       & Record<string, unknown> };

type Envelope<T> = Success<T> | Failure;
```

If the project uses the [schema](../reference/api/schema.md), generate these
from it instead: the schema describes the envelope, so the generated types
are the same.

## One fetch function

```typescript
async function ask<T>(path: string, init: RequestInit = {}): Promise<Envelope<T>> {
  const response = await fetch(`${API}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json',
               'Accept-Language': currentLanguage(),     // the messages in the reader's language
               ...init.headers },
  });
  return response.json();                                // always the envelope
}

const answer = await ask<Product>('/products/1/');

if (answer.success) {
  show(answer.data);
} else if (answer.error_code === 'out_of_stock') {   // branch on the code, never the message
  offer(answer.data.available as number);
} else {
  toast(answer.message);                              // a person reads the message
}
```

## One pager for both kinds

```typescript
function nextQuery(page: Page): Record<string, string> | null {
  if (!page.has_next) return null;
  return page.type === 'page'
    ? { page: String(page.page + 1) }
    : { cursor: page.next_cursor! };
}
```

`has_next` is in both kinds, so "load more" works on a numbered list and a
feed alike.

## A form's errors

```typescript
if (!answer.success && answer.error_code === 'validation_error') {
  for (const [field, problems] of Object.entries(answer.data.fields ?? {})) {
    markField(field, problems[0].message);           // "items.0.quantity" for a nested one
  }
}
```

`problems[0].code` - `required`, `max_length`, `unique` - tells a client what
went wrong without reading translated text.
