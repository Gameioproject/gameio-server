import "./styles.css";
import { mountHandheld } from "./handheld";
import { nameLatestBuild } from "./build";

const device = document.getElementById("device");
const download = document.getElementById("download") as HTMLAnchorElement | null;

if (device) {
  mountHandheld(device, () => {
    if (!download) return;
    download.scrollIntoView({ block: "center", behavior: "smooth" });
    download.focus({ preventScroll: true });
  });
}

nameLatestBuild(
  [download, document.getElementById("download2") as HTMLAnchorElement | null],
  document.getElementById("build-meta"),
);

const clock = document.getElementById("clock");
function tick(): void {
  if (!clock) return;
  clock.textContent = new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}
tick();
window.setInterval(tick, 15000);
