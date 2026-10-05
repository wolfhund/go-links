import { useState, type FormEvent } from 'react'
import { ApiError, createLink, type FieldErrors, type Link } from './api'

interface Props {
  initialSlug: string
  onCreated: (link: Link) => void
}

export function CreateLinkForm({ initialSlug, onCreated }: Props) {
  const [slug, setSlug] = useState(initialSlug)
  const [targetUrl, setTargetUrl] = useState('')
  const [errors, setErrors] = useState<FieldErrors>({})
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitting(true)
    setErrors({})
    try {
      const link = await createLink({ slug, target_url: targetUrl })
      onCreated(link)
      setSlug('')
      setTargetUrl('')
    } catch (error) {
      setErrors(
        error instanceof ApiError
          ? error.fields
          : { form: 'Could not reach the server. Is the API running?' },
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit} noValidate>
      <h2>Create a link</h2>

      <div className="field">
        <label htmlFor="slug">Short name</label>
        <div className="input-prefix">
          <span aria-hidden="true">go/</span>
          <input
            id="slug"
            name="slug"
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            placeholder="design-system"
            autoComplete="off"
            required
            aria-invalid={Boolean(errors.slug)}
            aria-describedby="slug-hint slug-error"
          />
        </div>
        <p id="slug-hint" className="hint">
          Lowercase letters, numbers and single dashes.
        </p>
        <p id="slug-error" className="error" role="alert">
          {errors.slug}
        </p>
      </div>

      <div className="field">
        <label htmlFor="target_url">Destination URL</label>
        <input
          id="target_url"
          name="target_url"
          type="url"
          value={targetUrl}
          onChange={(e) => setTargetUrl(e.target.value)}
          placeholder="https://example.com/docs"
          required
          aria-invalid={Boolean(errors.target_url)}
          aria-describedby="target_url-error"
        />
        <p id="target_url-error" className="error" role="alert">
          {errors.target_url}
        </p>
      </div>

      <p className="error" role="alert">
        {errors.form}
      </p>

      <button type="submit" disabled={submitting}>
        {submitting ? 'Creating…' : 'Create link'}
      </button>
    </form>
  )
}
