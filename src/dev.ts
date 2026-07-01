import { spawn } from "node:child_process";

const isWindows = process.platform === "win32";

const python = spawn("python", ["../servidor_simulacao.py"], {
  cwd: process.cwd(),
  shell: isWindows,
  stdio: "inherit",
});

const vite = spawn("npx", ["vite", "--host", "127.0.0.1"], {
  cwd: process.cwd(),
  shell: isWindows,
  stdio: "inherit",
});

function shutdown() {
  python.kill();
  vite.kill();
}

process.on("SIGINT", () => {
  shutdown();
  process.exit(0);
});

process.on("SIGTERM", () => {
  shutdown();
  process.exit(0);
});

python.on("exit", (code) => {
  if (code !== 0 && code !== null) {
    vite.kill();
    process.exit(code);
  }
});

vite.on("exit", (code) => {
  python.kill();
  process.exit(code ?? 0);
});
