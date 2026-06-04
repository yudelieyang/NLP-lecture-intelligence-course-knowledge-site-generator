const sidebar = document.getElementById("sidebar");
const menu = document.getElementById("menu-toggle");
const theme = document.getElementById("theme-toggle");
const topButton = document.getElementById("back-to-top");
const main = document.querySelector("main");
const pageSections = [...main.querySelectorAll(":scope > .lecture-section")];
const pages = pageSections.filter((page) => page.id !== "unprocessed");
const pageIds = pages.map((page) => page.id);
const lecturePages = pages.filter((page) => page.id.startsWith("lecture-"));
const navLinks = [...document.querySelectorAll(".sidebar a[href^='#']")];
const lectureLinks = [...document.querySelectorAll(".nav-lecture")];

pageSections.forEach((page) => page.classList.add("lecture-page"));

function pageIdFromHash(hash = location.hash) {
  const targetId = hash.replace(/^#/, "");
  if (!targetId) return "overview";
  if (pageIds.includes(targetId)) return targetId;
  const lectureMatch = targetId.match(/^(lecture-\d+)(?:-|$)/);
  return lectureMatch && pageIds.includes(lectureMatch[1]) ? lectureMatch[1] : "overview";
}

function currentPage() {
  return pages.find((page) => page.classList.contains("active-page"));
}

function updateActiveLink(targetId) {
  navLinks.forEach((link) => link.classList.remove("active"));
  const exact = document.querySelector(`.sidebar a[href="#${CSS.escape(targetId)}"]`);
  const pageLink = document.querySelector(`.sidebar a[href="#${CSS.escape(pageIdFromHash(`#${targetId}`))}"]`);
  (exact || pageLink)?.classList.add("active");
}

function addPageNavigation() {
  pages.forEach((page, index) => {
    if (page.querySelector(":scope > .page-navigation")) return;
    const navigation = document.createElement("nav");
    navigation.className = "page-navigation";
    navigation.setAttribute("aria-label", "章节切换");
    const previous = pages[index - 1];
    const next = pages[index + 1];
    if (previous) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.target = previous.id;
      button.textContent = `← 上一页：${previous.id === "overview" ? "课程总览" : previous.querySelector(".eyebrow")?.textContent || previous.id}`;
      navigation.appendChild(button);
    }
    if (next) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.target = next.id;
      button.textContent = `下一页：${next.querySelector(".eyebrow")?.textContent || next.id} →`;
      navigation.appendChild(button);
    }
    page.appendChild(navigation);
  });
}

function scrollWithinPage(targetId) {
  const target = document.getElementById(targetId);
  if (target && target !== currentPage()) target.scrollIntoView({ behavior: "smooth", block: "start" });
  else main.scrollTo({ top: 0, behavior: "smooth" });
}

function showPage(targetId, options = {}) {
  const pageId = pageIdFromHash(`#${targetId}`);
  pages.forEach((page) => page.classList.toggle("active-page", page.id === pageId));
  updateActiveLink(targetId);
  if (options.updateHash !== false && location.hash !== `#${targetId}`) {
    history.pushState(null, "", `#${targetId}`);
  }
  requestAnimationFrame(() => scrollWithinPage(targetId));
}

menu?.addEventListener("click", () => {
  const open = sidebar.classList.toggle("open");
  menu.setAttribute("aria-expanded", String(open));
});

theme?.addEventListener("click", () => {
  document.body.classList.toggle("dark");
  localStorage.setItem("nlp-theme", document.body.classList.contains("dark") ? "dark" : "light");
});

if (localStorage.getItem("nlp-theme") === "dark") document.body.classList.add("dark");

lectureLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    const group = link.closest(".nav-group");
    const wasOpen = group.classList.contains("open");
    document.querySelectorAll(".nav-group.open").forEach((item) => item.classList.remove("open"));
    if (!wasOpen) group.classList.add("open");
    showPage(link.hash.slice(1));
  });
});

document.querySelector(".nav-overview")?.addEventListener("click", (event) => {
  event.preventDefault();
  showPage("overview");
});

document.querySelectorAll(".nav-children a").forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    showPage(link.hash.slice(1));
  });
});

document.addEventListener("click", (event) => {
  const button = event.target.closest(".page-navigation button");
  if (button) showPage(button.dataset.target);
});

document.querySelectorAll(".sidebar a").forEach((link) => {
  link.addEventListener("click", () => {
    if (window.innerWidth <= 900) {
      sidebar.classList.remove("open");
      menu?.setAttribute("aria-expanded", "false");
    }
  });
});

main.addEventListener("scroll", () => topButton.classList.toggle("visible", main.scrollTop > 500));
topButton.addEventListener("click", () => main.scrollTo({ top: 0, behavior: "smooth" }));
window.addEventListener("hashchange", () => showPage(location.hash.slice(1), { updateHash: false }));

addPageNavigation();
showPage(location.hash.slice(1) || "overview", { updateHash: false });

const lightbox = document.getElementById("slide-lightbox");
const lightboxImage = lightbox?.querySelector("img");
const lightboxCaption = lightbox?.querySelector("p");

function closeLightbox() {
  lightbox?.classList.remove("open");
  lightbox?.setAttribute("aria-hidden", "true");
}

document.addEventListener("click", (event) => {
  const image = event.target.closest(".slide-figure img");
  if (image && lightbox) {
    lightboxImage.src = image.src;
    lightboxImage.alt = image.alt;
    lightboxCaption.textContent = image.closest("figure")?.querySelector("figcaption")?.textContent || image.alt;
    lightbox.classList.add("open");
    lightbox.setAttribute("aria-hidden", "false");
    return;
  }
  if (event.target === lightbox || event.target.closest("#slide-lightbox button")) closeLightbox();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeLightbox();
});
