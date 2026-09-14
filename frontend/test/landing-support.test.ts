import { afterEach, describe, expect, it, vi } from "vitest";
import { loadSupportLink } from "../landing/support";

afterEach(() => vi.unstubAllGlobals());

describe("landing support", () => {
  it.each([
    null,
    "javascript:alert(1)",
    "http://example.org",
    "https://user:secret@example.org",
  ])("hides an unavailable or unsafe destination: %s", async (value) => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ FRONTEND: { SUPPORT_URL: value } }),
      }),
    );
    const link = document.createElement("a");
    link.hidden = true;
    await loadSupportLink(link);
    expect(link.hidden).toBe(true);
    expect(link.hasAttribute("href")).toBe(false);
  });

  it("opens only the configured hosted support destination", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          FRONTEND: { SUPPORT_URL: "https://checkout.example.org/gameio" },
        }),
      }),
    );
    const link = document.createElement("a");
    link.hidden = true;
    await loadSupportLink(link);
    expect(link.hidden).toBe(false);
    expect(link.href).toBe("https://checkout.example.org/gameio");
  });

  it("leaves the page usable when the server is offline", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    const link = document.createElement("a");
    link.hidden = true;
    await loadSupportLink(link);
    expect(link.hidden).toBe(true);
  });
});
