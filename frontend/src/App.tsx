import { useEffect, useState } from 'react'
import { listLinks, type Link } from './api'
import { CreateLinkForm } from './CreateLinkForm'
import { LinkList } from './LinkList'

type LoadState = 'loading' | 'ready' | 'error'

// Set when the redirect service sends us here for an unknown slug.
const initialMissingSlug =
  new URLSearchParams(window.location.search).get('slug') ?? ''

export default function App() {
  const [links, setLinks] = useState<Link[]>([])
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [status, setStatus] = useState('')
  const [missingSlug, setMissingSlug] = useState(initialMissingSlug)

  useEffect(() => {
    listLinks()
      .then((data) => {
        setLinks(data)
        setLoadState('ready')
      })
      .catch(() => setLoadState('error'))
  }, [])

  function handleCreated(link: Link) {
    setLinks((current) =>
      [...current, link].sort((a, b) => a.slug.localeCompare(b.slug)),
    )
    setStatus(`Created go/${link.slug}`)
    setMissingSlug('')
    window.history.replaceState(null, '', window.location.pathname)
  }

  return (
    <main>
      <header>
        <h1>Go Links</h1>
        <p>Short, memorable shortcuts to internal resources.</p>
      </header>

      {missingSlug && (
        <p className="notice" role="status">
          <strong>go/{missingSlug}</strong> doesn’t exist yet. Create it below.
        </p>
      )}

      <p className="success" role="status" aria-live="polite">
        {status}
      </p>

      <CreateLinkForm initialSlug={initialMissingSlug} onCreated={handleCreated} />

      <section className="card" aria-labelledby="links-heading">
        <h2 id="links-heading">Existing links</h2>
        {loadState === 'loading' && <p>Loading…</p>}
        {loadState === 'error' && (
          <p className="error" role="alert">
            Could not load links. Is the API running?
          </p>
        )}
        {loadState === 'ready' && <LinkList links={links} />}
      </section>
    </main>
  )
}
