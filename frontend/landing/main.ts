import { nameLatestBuild } from "./build";
import "./styles.css";
import { loadSupportLink } from "./support";

void loadSupportLink(
  document.getElementById("support-gameio") as HTMLAnchorElement | null,
);

nameLatestBuild(
  ["download", "download-top", "download2"].map(
    (id) => document.getElementById(id) as HTMLAnchorElement | null,
  ),
  document.getElementById("build-meta"),
);
