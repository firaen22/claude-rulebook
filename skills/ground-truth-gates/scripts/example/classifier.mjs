// Toy intent classifier — exists so the gate template can be self-tested.
// Replace with an import of YOUR real classifier; the gate runner is generic
// over any (text: string) => string | null function.
export function classify(text) {
  if (/^提醒\s+\d{6,10}\s+/.test(text)) return 'remind';
  if (/^睇下\s+\S+$/.test(text)) return 'view_client';
  return null; // defer to the fallback (safe miss)
}
export default classify;
