function getSeason(date = new Date()) {
  const month = date.getMonth() + 1;
  if (month === 12 || month === 1 || month === 2) return "winter";
  if (month >= 3 && month <= 5) return "spring";
  if (month >= 6 && month <= 8) return "summer";
  return "fall";
}

function prefersReducedMotion() {
  return (
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
}

function setCssHeroImage(path) {
  document.documentElement.style.setProperty("--hero-image", `url("${path}")`);
}

function setLayerImage(layer, path) {
  if (!layer) return;
  layer.style.backgroundImage = `url("${path}")`;
}

function copyToClipboard(text) {
  if (navigator.clipboard?.writeText) return navigator.clipboard.writeText(text);

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
  return Promise.resolve();
}

const yearEl = document.querySelector("[data-year]");
if (yearEl) yearEl.textContent = String(new Date().getFullYear());

document.documentElement.dataset.season = getSeason();

// Header / hero slideshow
const heroEl = document.querySelector("[data-hero]");
const heroToggle = document.querySelector("[data-hero-toggle]");
const heroLayerA = document.querySelector('[data-hero-layer="a"]');
const heroLayerB = document.querySelector('[data-hero-layer="b"]');
const heroImages = [
  "Assets/Images/hus_solnedgang.jpg",
  "Assets/Images/entre.jpg",
  "Assets/Images/frukost2.jpg",
  "Assets/Images/Home/IMG_20170617_135615278.jpg",
];

let heroIndex = 0;
let heroInterval = null;
let heroPaused = false;
let heroActiveLayer = "a";

function swapHeroImage(path) {
  if (!heroLayerA || !heroLayerB) {
    setCssHeroImage(path);
    return;
  }

  const nextLayer = heroActiveLayer === "a" ? heroLayerB : heroLayerA;
  const prevLayer = heroActiveLayer === "a" ? heroLayerA : heroLayerB;

  setLayerImage(nextLayer, path);
  nextLayer.classList.add("is-active");
  prevLayer.classList.remove("is-active");
  heroActiveLayer = heroActiveLayer === "a" ? "b" : "a";
}

function startHero() {
  if (!heroEl || prefersReducedMotion()) return;
  if (heroInterval) return;

  heroInterval = window.setInterval(() => {
    heroIndex = (heroIndex + 1) % heroImages.length;
    swapHeroImage(heroImages[heroIndex]);
  }, 6500);
}

function stopHero() {
  if (!heroInterval) return;
  window.clearInterval(heroInterval);
  heroInterval = null;
}

setCssHeroImage(heroImages[heroIndex]);
setLayerImage(heroLayerA, heroImages[heroIndex]);
setLayerImage(heroLayerB, heroImages[(heroIndex + 1) % heroImages.length]);
startHero();

if (heroToggle) {
  heroToggle.addEventListener("click", () => {
    heroPaused = !heroPaused;
    if (heroPaused) {
      stopHero();
      heroToggle.textContent = "Starta bildspel";
      heroToggle.setAttribute("aria-pressed", "true");
    } else {
      startHero();
      heroToggle.textContent = "Pausa bildspel";
      heroToggle.setAttribute("aria-pressed", "false");
    }
  });
}

// Mobile menu
const menuButton = document.querySelector("[data-menu-button]");
const siteNav = document.querySelector("[data-site-nav]");

function setNavOpen(open) {
  document.body.classList.toggle("nav-open", open);
  menuButton?.setAttribute("aria-expanded", open ? "true" : "false");
}

menuButton?.addEventListener("click", () => {
  const open = !document.body.classList.contains("nav-open");
  setNavOpen(open);
});

siteNav?.addEventListener("click", (e) => {
  const target = e.target;
  if (target instanceof HTMLAnchorElement) setNavOpen(false);
});

window.addEventListener("keydown", (e) => {
  if (e.key === "Escape") setNavOpen(false);
});

// Active section highlight
const navLinks = [...document.querySelectorAll("[data-nav-link]")];
const sections = navLinks
  .map((a) => {
    const href = a.getAttribute("href");
    return href ? document.querySelector(href) : null;
  })
  .filter(Boolean);

if ("IntersectionObserver" in window && sections.length) {
  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((x) => x.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;

      const id = `#${visible.target.id}`;
      navLinks.forEach((a) => {
        a.setAttribute("aria-current", a.getAttribute("href") === id ? "true" : "false");
      });
    },
    { rootMargin: "-30% 0px -60% 0px", threshold: [0.1, 0.2, 0.35] }
  );

  sections.forEach((section) => observer.observe(section));
}

// Gallery + modal
const galleryItems = [
  { src: "Assets/Images/entre.jpg", title: "Entré" },
  { src: "Assets/Images/frukost2.jpg", title: "Frukost" },
  { src: "Assets/Images/services/frukost.jpg", title: "Frukost (servering)" },
  { src: "Assets/Images/ros.jpg", title: "Rosor" },
  { src: "Assets/Images/flower.jpg", title: "Blommor" },
  { src: "Assets/Images/spring_flowers.jpg", title: "Vårblommor" },
  { src: "Assets/Images/white_spring_flowers.jpg", title: "Vårblommor" },
  { src: "Assets/Images/hus_solnedgang.jpg", title: "Kvällsljus" },
  { src: "Assets/Images/I_skuggan_under_bladverket.JPG", title: "I skuggan" },
  { src: "Assets/Images/Home/IMG_20170617_135615278.jpg", title: "Hemmiljö" },
  { src: "Assets/Images/Home/IMG_20170617_135705673.jpg", title: "Hemmiljö" },
  { src: "Assets/Images/Home/IMG_20170617_135924267.jpg", title: "Hemmiljö" },
  { src: "Assets/Images/IMG_20170617_135520339.jpg", title: "Sommar" },
  { src: "Assets/Images/IMG_20170617_135542725.jpg", title: "Sommar" },
  { src: "Assets/Images/IMG_20170617_135749950.jpg", title: "Sommar" },
  { src: "Assets/Images/rosegarden_wrong_format.jpg", title: "Rosenträdgård" },
  { src: "Assets/Images/easter.jpg", title: "Påsk" },
  { src: "Assets/Images/entre_konsthall_tjornedala.jpg", title: "Utflykt" },
];

const galleryEl = document.querySelector("[data-gallery]");
const modalEl = document.querySelector("[data-modal]");
const modalImage = document.querySelector("[data-modal-image]");
const modalCaption = document.querySelector("[data-modal-caption]");
const modalTitle = document.querySelector("[data-modal-title]");
const modalPrev = document.querySelector("[data-modal-prev]");
const modalNext = document.querySelector("[data-modal-next]");
const modalCloses = [...document.querySelectorAll("[data-modal-close]")];

let modalIndex = 0;
let lastFocusedEl = null;

function renderGallery() {
  if (!galleryEl) return;
  const fragment = document.createDocumentFragment();

  galleryItems.forEach((item, i) => {
    const button = document.createElement("button");
    button.type = "button";
    button.setAttribute("aria-label", `${item.title} (öppna)`);
    button.dataset.index = String(i);

    const img = document.createElement("img");
    img.src = item.src;
    img.alt = item.title;
    img.loading = "lazy";

    button.appendChild(img);
    fragment.appendChild(button);
  });

  galleryEl.appendChild(fragment);
}

function setModalImage(i) {
  modalIndex = (i + galleryItems.length) % galleryItems.length;
  const item = galleryItems[modalIndex];
  if (!item || !modalImage) return;

  modalImage.src = item.src;
  modalImage.alt = item.title;
  if (modalTitle) modalTitle.textContent = item.title;
  if (modalCaption) modalCaption.textContent = item.title;
}

function openModal(i) {
  if (!modalEl) return;
  lastFocusedEl = document.activeElement instanceof HTMLElement ? document.activeElement : null;
  setModalImage(i);
  modalEl.hidden = false;
  document.body.style.overflow = "hidden";
  modalEl.querySelector("button")?.focus();
}

function closeModal() {
  if (!modalEl) return;
  modalEl.hidden = true;
  document.body.style.overflow = "";
  if (lastFocusedEl) lastFocusedEl.focus();
}

renderGallery();

galleryEl?.addEventListener("click", (e) => {
  const target = e.target;
  const button = target instanceof HTMLElement ? target.closest("button") : null;
  if (!button) return;
  const i = Number(button.dataset.index);
  if (Number.isFinite(i)) openModal(i);
});

modalCloses.forEach((el) => el.addEventListener("click", closeModal));

modalPrev?.addEventListener("click", () => setModalImage(modalIndex - 1));
modalNext?.addEventListener("click", () => setModalImage(modalIndex + 1));

window.addEventListener("keydown", (e) => {
  if (!modalEl || modalEl.hidden) return;
  if (e.key === "Escape") closeModal();
  if (e.key === "ArrowLeft") setModalImage(modalIndex - 1);
  if (e.key === "ArrowRight") setModalImage(modalIndex + 1);
});

// Copy buttons
document.addEventListener("click", async (e) => {
  const target = e.target;
  if (!(target instanceof HTMLElement)) return;
  const btn = target.closest("[data-copy]");
  if (!(btn instanceof HTMLElement)) return;

  const value = btn.getAttribute("data-copy");
  if (!value) return;

  const original = btn.textContent;
  try {
    await copyToClipboard(value);
    btn.textContent = "Kopierat!";
  } catch {
    btn.textContent = "Kunde inte kopiera";
  } finally {
    window.setTimeout(() => {
      if (original) btn.textContent = original;
    }, 1100);
  }
});
