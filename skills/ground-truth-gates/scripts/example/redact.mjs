// Toy structure-preserving redactor — exists so the replay gate can be
// self-tested. Replace with an import of YOUR real transform. Order matters:
// emails before digit runs before handles (so placeholders don't re-match).
export function redact(text) {
  return text
    .replace(/[\w.+-]+@[\w-]+\.[\w.]+/g, 'client@example.com')
    .replace(/\b[A-Z][0-9]{6}\(?[0-9A]\)?/g, 'X123456(7)')   // HKID-shaped
    .replace(/\d{8,}/g, '12345678')                          // digit runs keep their shape
    .replace(/(?<![\w.@-])@[A-Za-z0-9_]+/g, '@user');        // handles, not email tails
}
export default redact;
