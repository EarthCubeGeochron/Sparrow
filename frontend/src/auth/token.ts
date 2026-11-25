/** The JWT that PostgREST accepts, kept across page loads. */

const storageKey = "sparrow-api-token";

interface TokenPayload {
  exp?: number;
  role?: string;
}

function decodePayload(token: string): TokenPayload | null {
  try {
    const part = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(part));
  } catch {
    return null;
  }
}

export function isUsableToken(token: string | null): boolean {
  if (token == null) return false;
  const payload = decodePayload(token);
  // PostgREST switches to the claim's role; tokens without one act as anonymous
  if (payload?.role == null) return false;
  // Leave a minute of slack so a request doesn't race the expiry
  return payload.exp == null || payload.exp * 1000 > Date.now() + 60000;
}

export function readStoredToken(): string | null {
  try {
    const token = window.localStorage.getItem(storageKey);
    return isUsableToken(token) ? token : null;
  } catch {
    return null;
  }
}

export function storeToken(token: string | null) {
  try {
    if (token == null) {
      window.localStorage.removeItem(storageKey);
    } else {
      window.localStorage.setItem(storageKey, token);
    }
  } catch {
    // Storage can be unavailable (private windows); the session still works until reload
  }
}

export function tokenFromCookie(): string | null {
  const match = document.cookie.match(/(?:^|;\s*)access_token_cookie=([^;]+)/);
  if (match == null) return null;
  const token = decodeURIComponent(match[1]);
  return isUsableToken(token) ? token : null;
}
