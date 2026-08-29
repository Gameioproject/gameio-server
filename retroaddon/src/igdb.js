"use strict";

// Minimal IGDB client: Twitch client-credentials auth, 4 req/s throttle,
// retry with backoff on 429 / 5xx / network errors, token refresh on 401.

const TOKEN_URL = "https://id.twitch.tv/oauth2/token";
const API_URL = "https://api.igdb.com/v4";
const MIN_INTERVAL_MS = 260; // IGDB allows 4 requests/second
const MAX_ATTEMPTS = 6;
const REQUEST_TIMEOUT_MS = 30_000;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

class IgdbClient {
  constructor({ clientId, clientSecret }) {
    if (!clientId || !clientSecret) {
      throw new Error("IGDB_CLIENT_ID and IGDB_CLIENT_SECRET must be set");
    }
    this.clientId = clientId;
    this.clientSecret = clientSecret;
    this.token = null;
    this.tokenExpiresAt = 0;
    this.lastRequestAt = 0;
  }

  async getToken() {
    if (this.token && Date.now() < this.tokenExpiresAt - 60_000)
      return this.token;
    const params = new URLSearchParams({
      client_id: this.clientId,
      client_secret: this.clientSecret,
      grant_type: "client_credentials",
    });
    const res = await fetch(`${TOKEN_URL}?${params}`, {
      method: "POST",
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });
    if (!res.ok)
      throw new Error(
        `Twitch token request failed: ${res.status} ${await res.text()}`,
      );
    const body = await res.json();
    this.token = body.access_token;
    this.tokenExpiresAt = Date.now() + body.expires_in * 1000;
    return this.token;
  }

  async throttle() {
    const wait = this.lastRequestAt + MIN_INTERVAL_MS - Date.now();
    if (wait > 0) await sleep(wait);
    this.lastRequestAt = Date.now();
  }

  // Run an Apicalypse query against an endpoint (e.g. 'games') and return parsed JSON.
  async query(endpoint, body) {
    let lastError;
    for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
      const token = await this.getToken(); // auth errors are fatal, not retried
      await this.throttle();
      let res;
      try {
        res = await fetch(`${API_URL}/${endpoint}`, {
          method: "POST",
          headers: {
            "Client-ID": this.clientId,
            Authorization: `Bearer ${token}`,
            Accept: "application/json",
          },
          body,
          signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
        });
      } catch (err) {
        lastError = err; // network error — retry
        await sleep(backoff(attempt));
        continue;
      }
      if (res.ok) return res.json();

      const text = await res.text();
      if (res.status === 401) {
        this.token = null; // expired/revoked token — refresh and retry
        lastError = new Error(`IGDB 401: ${text}`);
        continue;
      }
      if (res.status === 429 || res.status >= 500) {
        const retryAfter = Number(res.headers.get("retry-after"));
        const wait = retryAfter > 0 ? retryAfter * 1000 : backoff(attempt);
        console.warn(
          `IGDB ${res.status}, retrying in ${wait}ms (attempt ${attempt}/${MAX_ATTEMPTS})`,
        );
        lastError = new Error(`IGDB ${res.status}: ${text}`);
        await sleep(wait);
        continue;
      }
      throw new Error(`IGDB ${res.status}: ${text}\nQuery: ${body}`);
    }
    throw lastError;
  }
}

function backoff(attempt) {
  return Math.min(30_000, 1000 * 2 ** (attempt - 1)) + Math.random() * 500;
}

module.exports = { IgdbClient };
