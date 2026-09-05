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
