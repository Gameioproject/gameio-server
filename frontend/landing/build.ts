interface LatestBuild {
  file: string;
  size?: number;
  published?: string;
}

const MIB = 1048576;

/** Points every download link at the current build and names it, so two downloads are tellable apart. */
export async function nameLatestBuild(
  links: Array<HTMLAnchorElement | null>,
  meta: HTMLElement | null,
): Promise<void> {
  let latest: LatestBuild | null = null;
  try {
    const response = await fetch("/apk/latest.json", { cache: "no-store" });
    latest = response.ok ? ((await response.json()) as LatestBuild) : null;
  } catch {
    latest = null;
  }
  if (!latest?.file) return;
  for (const link of links) link?.setAttribute("href", `/apk/${latest.file}`);
  if (meta) {
    const size = latest.size ? ` · ${(latest.size / MIB).toFixed(0)} MB` : "";
    meta.textContent = `${latest.file}${size} · Android 8.0 and up`;
  }
}
