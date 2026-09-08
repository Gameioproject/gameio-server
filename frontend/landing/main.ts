import "./styles.css";
import { mountShelves } from "./browse";
import { nameLatestBuild } from "./build";
import { TOTAL_SYSTEMS, TOTAL_TITLES } from "./shelves";

const download = document.getElementById(
  "download",
) as HTMLAnchorElement | null;
const shelves = document.getElementById("shelves");
const status = document.getElementById("status");

if (shelves) {
  mountShelves(
    shelves,
    {
      backdrop: document.getElementById("backdrop") as HTMLImageElement | null,
      cover: document.getElementById("f-cover") as HTMLImageElement | null,
      platform: document.getElementById("f-platform"),
      year: document.getElementById("f-year"),
      rating: document.getElementById("f-rating"),
      shelf: document.getElementById("f-shelf"),
      name: document.getElementById("f-name"),
      summary: document.getElementById("f-summary"),
    },
    status,
    () => {
      if (!download) return;
      download.scrollIntoView({ block: "center", behavior: "smooth" });
      download.focus({ preventScroll: true });
    },
  );
}

if (status) {
  status.textContent = `${TOTAL_TITLES.toLocaleString("en")} titles · ${TOTAL_SYSTEMS} systems`;
}

nameLatestBuild(
  [
    download,
    document.getElementById("download-top") as HTMLAnchorElement | null,
    document.getElementById("download2") as HTMLAnchorElement | null,
  ],
  document.getElementById("build-meta"),
);
