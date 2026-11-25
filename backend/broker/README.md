# Sparrow identity broker

Signs in with ORCID on behalf of Sparrow labs. Registering an ORCID API client
takes a public, stable, HTTPS address and some paperwork; with a broker, one
client serves every lab, and a lab sets only `SPARROW_ORCID_BROKER_URL`.

The broker answers who signed in and nothing else. Each lab still decides which
of its users an ORCID iD signs in as (see `sparrow link-orcid`), and issues its
own session.

## Running it

```sh
pip install ./backend/broker
sparrow-identity-broker      # or: python -m sparrow.broker
```

It serves plain HTTP on `SPARROW_BROKER_BIND` (default `0.0.0.0:8000`) and
should sit behind a proxy that terminates TLS.

| Variable | |
| --- | --- |
| `SPARROW_BROKER_URL` | The broker's public URL, e.g. `https://sparrow-data.org/broker`. It is the issuer (`iss`) of every assertion and must equal the `SPARROW_ORCID_BROKER_URL` that labs set. |
| `SPARROW_BROKER_ORCID_CLIENT_ID`, `SPARROW_BROKER_ORCID_CLIENT_SECRET` | The broker's ORCID API client. Register `{SPARROW_BROKER_URL}/callback` as its redirect URI. The secret is never logged or returned. |
| `SPARROW_BROKER_SIGNING_KEY` or `SPARROW_BROKER_SIGNING_KEY_FILE` | An unencrypted Ed25519 private key in PEM form, or the path to one. The broker refuses to start without it and never generates one. Make one with `openssl genpkey -algorithm ed25519 -out broker-key.pem`. |
| `SPARROW_BROKER_ALLOWED_ORIGINS` | Optional. Comma-separated lab origins (`https://lab.example.edu`) that may use the broker. Unset, any lab that passes the checks below may. |
| `SPARROW_BROKER_ORCID_BASE_URL` | Optional. `https://sandbox.orcid.org/oauth` to sign in against ORCID's sandbox. |
| `SPARROW_BROKER_BIND` | Optional. The address to listen on. |

The broker keeps no database. Its state between the redirects lives in a signed
token and a short-lived cookie, keyed by a secret derived from the signing key.

## Protocol

1. The lab sends the browser to

   ```
   GET {broker}/login?return_to={lab callback}&state={lab state}
   ```

   `return_to` is the lab's callback, `https://{lab}/api/v2/auth/orcid/callback`.
   The broker refuses one that is not `https` (except on `localhost`, `*.localhost`
   and `*.local`), has a query string, fragment or user info, does not end in
   `/api/v2/auth/orcid/callback`, or is outside `SPARROW_BROKER_ALLOWED_ORIGINS`.
   `state` is opaque to the broker.

2. The broker carries `return_to` and the lab's `state` through ORCID inside its
   own signed state, exchanges ORCID's code, and sends the browser to

   ```
   {return_to}?assertion={JWT}&state={lab state}
   ```

   If the person cancels at ORCID, it sends `{return_to}?error=access_denied&state=…`
   instead (`error=sign_in_failed` for any other failure ORCID reports).

3. The assertion is a JWT signed with EdDSA (Ed25519), its header naming the key
   by `kid`. Its claims:

   | Claim | |
   | --- | --- |
   | `iss` | The broker's URL, `SPARROW_BROKER_URL` |
   | `aud` | The origin of `return_to`, e.g. `https://lab.example.edu` |
   | `sub` | The ORCID iD, bare (`0000-0002-1825-0097`) |
   | `name` | The person's name as ORCID gives it; may be empty |
   | `iat`, `exp` | Issued now, valid for two minutes |
   | `jti` | A unique id, so a lab can refuse an assertion used twice |
   | `state` | The lab's `state`, echoed so the assertion is bound to one sign-in |

4. The broker publishes its public key at `{broker}/.well-known/jwks.json`. A lab
   verifies the signature against it, accepting only `alg: EdDSA`; it refetches
   the set when an assertion names a `kid` it has not seen, so the key can be
   rotated by publishing the new key and then signing with it. The lab also
   checks `iss`, that `aud` is its own origin, `exp`, that `state` matches both
   the query and the state cookie it set when the sign-in began, and that `jti`
   is new.

## Trust model

A lab in broker mode trusts the broker completely to say who signed in: anyone
holding the broker's signing key can sign in to every such lab as any user that
lab has linked to an ORCID iD. Guard the key as you would the labs' admin
passwords, and rotate it if it may have leaked.

What a lab does *not* have to trust:

- **Other labs.** Assertions are addressed to one origin (`aud`), so one lab
  cannot replay what it received at another.
- **The path the assertion travels.** It crosses the browser in a URL, so it can
  land in a proxy's access log or browser history. It expires within two
  minutes, is refused a second time, and is only accepted together with the
  state cookie set in the browser that began the sign-in.
- **Pages that start a sign-in.** Without the lab's state cookie, a sign-in
  started elsewhere (login CSRF) fails at the lab.

The broker does not decide who may use a lab. Without an allowlist it will sign
in for any HTTPS site that serves Sparrow's callback path; that site learns the
ORCID iD and name of whoever chooses to sign in to it, which is no more than
signing in to that site with ORCID directly would tell it.
