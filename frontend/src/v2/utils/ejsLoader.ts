// Loads EmulatorJS's loader.js after the EJS_* globals are set, preferring
// the bundled copy and falling back to the CDN (or the reverse when netplay
// needs the nightly build).

const EMULATORJS_STABLE_VERSION = "4.2.3";
const LOCAL_PATH = "/assets/emulatorjs/data";

function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const s = document.createElement("script");
    s.src = src;
    s.async = true;
    s.onload = () => resolve();
    s.onerror = () => reject(new Error("Failed loading " + src));
    document.body.appendChild(s);
  });
}

// The Vite dev server (and many SPA hosts) returns 200 + index.html when a
// static asset is missing. A <script> tag happily "loads" that, so the URL
// is pre-flighted to make sure the body is actually JavaScript.
async function isJsResource(url: string): Promise<boolean> {
  try {
    const res = await fetch(url);
    if (!res.ok) return false;
    const ct = res.headers.get("content-type") ?? "";
    if (/javascript|ecmascript/i.test(ct)) return true;
    if (/text\/html/i.test(ct)) return false;
    const text = await res.clone().text();
    return !text.trimStart().startsWith("<");
  } catch {
    return false;
  }
}

async function attemptLoad(path: string) {
  const loaderUrl = `${path}/loader.js`;
  if (!(await isJsResource(loaderUrl))) {
    throw new Error(`Loader at ${loaderUrl} did not return JavaScript`);
  }
  window.EJS_pathtodata = path;
  await loadScript(loaderUrl);
}

/** Inject EmulatorJS; resolves once loader.js ran (the game boots on its own). */
export async function loadEmulatorJS(netplayEnabled: boolean): Promise<void> {
  const version = netplayEnabled ? "nightly" : EMULATORJS_STABLE_VERSION;
  const cdnPath = `https://cdn.emulatorjs.org/${version}/data`;
  const [first, second] = netplayEnabled
    ? [cdnPath, LOCAL_PATH]
    : [LOCAL_PATH, cdnPath];
  try {
    await attemptLoad(first);
  } catch (e) {
    console.warn("[Play] Primary EmulatorJS loader failed, trying fallback", e);
    await attemptLoad(second);
  }
}
