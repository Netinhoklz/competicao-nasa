// Abre a página no Edge headless (CDP), roda uma expressão e imprime o resultado. Uso: node cdp.mjs <url> <largura> <arquivo-js>
import { spawn } from "node:child_process";
import { readFileSync } from "node:fs";
const [url, largura = "390", arq] = process.argv.slice(2);
const expr = readFileSync(arq, "utf8");
const D = (await import("node:os")).tmpdir() + "/quadra-perfil-cdp";  // perfil temporário do Edge
const porta = 9337;
const edge = spawn("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  ["--headless=new", "--disable-gpu", "--hide-scrollbars", `--remote-debugging-port=${porta}`, `--user-data-dir=${D}`, `--window-size=${largura},900`, "about:blank"],
  { stdio: "ignore" });
const espera = (ms) => new Promise((r) => setTimeout(r, ms));
let alvo;
for (let i = 0; i < 40 && !alvo; i++) {
  await espera(250);
  try { alvo = (await (await fetch(`http://127.0.0.1:${porta}/json`)).json()).find((t) => t.type === "page"); } catch (_) { /* ainda subindo */ }
}
const ws = new WebSocket(alvo.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0;
const pend = new Map();
ws.addEventListener("message", (ev) => { const m = JSON.parse(ev.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } });
const cmd = (method, params = {}) => new Promise((r) => { const k = ++id; pend.set(k, r); ws.send(JSON.stringify({ id: k, method, params })); });
await cmd("Emulation.setDeviceMetricsOverride", { width: +largura, height: 900, deviceScaleFactor: 1, mobile: false });
if (process.env.ESCURO) await cmd("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "dark" }] });
// o site abre em inglês por padrão (js/i18n.js): o print sai em português; ?lang=en na URL sai em inglês
await cmd("Page.addScriptToEvaluateOnNewDocument", { source: "try { if (!/[?&]lang=/.test(location.search + location.hash)) localStorage.setItem('quadra-lingua', 'pt'); } catch (_) {}" });
await cmd("Page.navigate", { url });
await espera(6000);
const r = await cmd("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
console.log(JSON.stringify(r.result?.result?.value ?? r.result, null, 1));
if (process.argv[5]) {
  const { writeFileSync } = await import("node:fs");
  const alt = (await cmd("Runtime.evaluate", { expression: "document.documentElement.scrollHeight", returnByValue: true })).result.result.value;
  await cmd("Emulation.setDeviceMetricsOverride", { width: +largura, height: alt, deviceScaleFactor: 1, mobile: false });
  await espera(800);
  const shot = await cmd("Page.captureScreenshot", { format: "png" });
  writeFileSync(process.argv[5], Buffer.from(shot.result.data, "base64"));
  console.log("print", process.argv[5], alt);
}
await cmd("Browser.close");
ws.close();
setTimeout(() => process.exit(0), 500);
