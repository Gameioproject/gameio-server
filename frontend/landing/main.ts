import "./styles.css";
import { nameLatestBuild } from "./build";

nameLatestBuild(
  ["download", "download-top", "download2"].map(
    (id) => document.getElementById(id) as HTMLAnchorElement | null,
  ),
  document.getElementById("build-meta"),
);
