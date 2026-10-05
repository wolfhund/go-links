export interface Link {
  slug: string
  target_url: string
  created_at: string
}

export interface NewLink {
  slug: string
  target_url: string
}

/** Field-level messages keyed by input name, plus a general fallback. */
export type FieldErrors = Partial<Record<keyof NewLink | 'form', string>>

/** Base URL where go links resolve (the API server's root). */
export const GO_BASE_URL: string =
  import.meta.env.VITE_GO_BASE_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  readonly fields: FieldErrors

  constructor(fields: FieldErrors) {
    super(Object.values(fields).join(' '))
    this.fields = fields
  }
}

interface ValidationIssue {
  loc: (string | number)[]
  msg: string
  type: string
}

// Friendlier copy for validation errors whose default message is technical.
const FRIENDLY_MESSAGES: Record<string, string> = {
  string_pattern_mismatch: 'Use lowercase letters, numbers and single dashes.',
  string_too_short: 'This field is required.',
}

const issueMessage = (issue: ValidationIssue): string =>
  FRIENDLY_MESSAGES[issue.type] ?? issue.msg.replace(/^Value error, /, '')

function toFieldErrors(status: number, detail: unknown): FieldErrors {
  if (status === 409 && typeof detail === 'string') {
    return { slug: detail }
  }
  if (status === 422 && Array.isArray(detail)) {
    return Object.fromEntries(
      (detail as ValidationIssue[]).map((issue) => [issue.loc.at(-1), issueMessage(issue)]),
    )
  }
  return { form: `Unexpected error (HTTP ${status}). Please try again.` }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  const body = await response.json().catch(() => null)
  if (!response.ok) {
    throw new ApiError(toFieldErrors(response.status, body?.detail))
  }
  return body as T
}

export const listLinks = (): Promise<Link[]> => request<Link[]>('/api/links')

export const createLink = (link: NewLink): Promise<Link> =>
  request<Link>('/api/links', { method: 'POST', body: JSON.stringify(link) })
