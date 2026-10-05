import { GO_BASE_URL, type Link } from './api'

interface Props {
  links: Link[]
}

export function LinkList({ links }: Props) {
  if (links.length === 0) {
    return <p className="empty">No links yet. Create the first one above.</p>
  }

  return (
    <table>
      <caption className="visually-hidden">Existing go links</caption>
      <thead>
        <tr>
          <th scope="col">Link</th>
          <th scope="col">Destination</th>
          <th scope="col">Created</th>
        </tr>
      </thead>
      <tbody>
        {links.map((link) => (
          <tr key={link.slug}>
            <td>
              <a href={`${GO_BASE_URL}/${link.slug}`}>go/{link.slug}</a>
            </td>
            <td className="target" title={link.target_url}>
              {link.target_url}
            </td>
            <td>
              <time dateTime={link.created_at}>
                {new Date(link.created_at).toLocaleDateString()}
              </time>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
