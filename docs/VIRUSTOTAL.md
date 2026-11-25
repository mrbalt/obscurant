# Setting up VirusTotal download checks

Obscurant can check every file you download against VirusTotal. It sends only the file's fingerprint (a SHA-256 hash), never the file, unless you press **Scan with VirusTotal** yourself on a file VirusTotal has never seen. Without a key, downloads are not checked.

## Get a free key

1. Go to https://www.virustotal.com/gui/join-us and sign up with an email address and a password.
2. Open the confirmation email and click the link.
3. Sign in, click your profile picture (top right), then **API key**.
4. Click the copy button next to the key. It is 64 letters and numbers.

The free key allows about 4 lookups a minute, which is plenty for downloads.

## Give it to Obscurant (Linux, Windows and Android)

1. In Obscurant open **Settings > Downloads**, find **VirusTotal key**.
2. Paste the key and press **Save and test**. Obscurant checks the key with VirusTotal before saving it.
3. The pill next to the row says **Key saved** when it worked.

**Android:** open *Settings*, scroll to the bottom, tap *VirusTotal key*, paste the key and tap OK. Finished downloads then show a notice with the result. The key stays inside the app's private storage.

Where the key is stored on desktop (only your user can read it):

- Linux: `~/.config/browser/vt-api-key`
- Windows: `%APPDATA%\Obscurant\vt-api-key`

Press **Remove** in the same row to delete it.

## If something is off

- "No VirusTotal key yet" in the Downloads panel: add the key as above.
- "VirusTotal rejected this key": copy the whole key again, with no spaces.
- "Out of lookups": the free key is rate-limited; wait a few minutes.
- A school or work network may block virustotal.com. Then checks cannot run.
