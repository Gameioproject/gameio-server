/** Shows voluntary support only when the server provides a hosted checkout. */
export async function loadSupportLink(
  link: HTMLAnchorElement | null,
): Promise<void> {
  if (!link) return;
  try {
    const response = await fetch("/api/heartbeat");
    if (!response.ok) return;
    const data = (await response.json()) as {
      FRONTEND?: { SUPPORT_URL?: unknown };
    };
    const value = data.FRONTEND?.SUPPORT_URL;
    if (typeof value !== "string") return;
    const url = new URL(value);
    if (
      url.protocol !== "https:" ||
      !url.hostname ||
      url.username ||
      url.password
    )
      return;
    link.href = url.href;
    link.hidden = false;
  } catch {
    // The optional link must not interrupt the landing page or APK download.
  }
}
