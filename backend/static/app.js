// Map keywords in category name → emoji icon (DoorDash-style colorful tiles)
const CATEGORY_EMOJI = [
  [/baby/i, "🍼"],
  [/yogurt/i, "🥛"],
  [/cheese/i, "🧀"],
  [/dairy|milk/i, "🥛"],
  [/bread|bagel|muffin|biscuit|pastry|doughnut|pancake|waffle/i, "🍞"],
  [/cake|pie|cookie|brownie|dessert|sweet|candy|chocolate/i, "🍰"],
  [/ice cream|sorbet|gelatin/i, "🍦"],
  [/pizza/i, "🍕"],
  [/burger|sandwich/i, "🍔"],
  [/fast food/i, "🍟"],
  [/mexican|tortilla|taco/i, "🌮"],
  [/asian|rice|noodle/i, "🍜"],
  [/soup|broth|gravy|sauce/i, "🍲"],
  [/salad|lettuce|coleslaw/i, "🥗"],
  [/fruit|juice|smoothie|berr/i, "🍎"],
  [/vegetable|veggie/i, "🥦"],
  [/nut|seed|peanut/i, "🥜"],
  [/cereal|oatmeal|grain/i, "🥣"],
  [/poultry|chicken|turkey/i, "🍗"],
  [/beef|pork|meat|sausage/i, "🥩"],
  [/fish|seafood|shrimp/i, "🐟"],
  [/egg/i, "🥚"],
  [/beverage|drink|water|tea|coffee/i, "🥤"],
  [/liquor|cocktail|wine|beer/i, "🍷"],
  [/snack|chip|popcorn|cracker|pretzel/i, "🍿"],
  [/jam|syrup|topping|sugar|spread/i, "🍯"],
  [/oil|dressing|fat/i, "🫒"],
  [/bar/i, "🍫"],
];

function prettifyName(raw, categoryName) {
  let s = String(raw || "").trim();

  // 1. Strip a leading "<Category>, " prefix (matches food's own category, or common ones)
  const prefixes = [categoryName, "Snacks", "Snack", "Beverages", "Soups",
                    "Cereals", "Cookies", "Candies", "Fast Foods"];
  for (const p of prefixes) {
    if (!p) continue;
    const re = new RegExp("^" + p.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\s*,\\s*", "i");
    if (re.test(s)) { s = s.replace(re, ""); break; }
  }

  // 2. Title-case ALL-CAPS words (FRITOLAY → Fritolay), preserve short ones (M&M, US, FDA)
  s = s.replace(/\b[A-Z][A-Z'&]{3,}\b/g, (w) =>
    w.charAt(0) + w.slice(1).toLowerCase()
  );

  // 3. Replace last ", " with " — " for a cleaner subtitle feel
  const lastComma = s.lastIndexOf(", ");
  if (lastComma > 0 && s.length - lastComma < 40) {
    s = s.slice(0, lastComma) + " — " + s.slice(lastComma + 2);
  }

  // 4. Capitalize first letter
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function emojiFor(name) {
  for (const [re, emoji] of CATEGORY_EMOJI) {
    if (re.test(name)) return emoji;
  }
  return "🍽️";
}

const $ = (sel) => document.querySelector(sel);

let activeCategoryId = null;

async function loadCategories() {
  const res = await fetch("/api/categories?limit=25");
  const cats = await res.json();
  const grid = $("#category-grid");
  grid.innerHTML = "";
  cats.forEach((c) => {
    const tile = document.createElement("div");
    tile.className = "category-tile";
    tile.dataset.id = c.category_id;
    tile.innerHTML = `
      <div class="icon">${emojiFor(c.name)}</div>
      <div class="label">${escapeHtml(c.name)}</div>
    `;
    tile.addEventListener("click", () => selectCategory(c));
    grid.appendChild(tile);
  });
  if (cats.length) selectCategory(cats[0]);
}

async function selectCategory(cat) {
  activeCategoryId = cat.category_id;
  document.querySelectorAll(".category-tile").forEach((t) =>
    t.classList.toggle("active", Number(t.dataset.id) === cat.category_id)
  );
  $("#explore-title").textContent = cat.name;
  $("#search-input").value = "";
  const res = await fetch(`/api/foods?category_id=${cat.category_id}`);
  const foods = await res.json();
  renderFoods(foods, cat.name);
}

function renderFoods(foods, fallbackCategory) {
  const grid = $("#food-grid");
  if (!foods.length) {
    grid.innerHTML = `<div class="empty">No foods found.</div>`;
    return;
  }
  grid.innerHTML = "";
  foods.forEach((f) => {
    const card = document.createElement("div");
    card.className = "food-card";
    const cat = f.category_name || fallbackCategory || "";
    card.innerHTML = `
      <div class="name">${escapeHtml(prettifyName(f.description, cat))}</div>
      <div class="meta">${escapeHtml(cat)}</div>
      <div class="emoji">${emojiFor(cat)}</div>
    `;
    card.addEventListener("click", () => openFoodDetail(f.fdc_id));
    grid.appendChild(card);
  });
}

async function openFoodDetail(fdc_id) {
  $("#modal-body").innerHTML = `<div class="loading">Loading...</div>`;
  $("#modal").classList.remove("hidden");
  const res = await fetch(`/api/food/${fdc_id}`);
  const data = await res.json();
  const rows = data.nutrients
    .filter((n) => n.amount && n.amount > 0)
    .map((n) => `<tr><td>${escapeHtml(n.nutrient)}</td><td>${formatAmount(n.amount)}</td></tr>`)
    .join("");
  $("#modal-body").innerHTML = `
    <h3>${escapeHtml(prettifyName(data.description, data.category_name))}</h3>
    <div class="modal-meta">${escapeHtml(data.category_name || "")} · ${escapeHtml(data.data_type)} · FDC ID ${data.fdc_id}</div>
    <h4>Nutrients</h4>
    <table class="nutrient-table"><tbody>${rows || '<tr><td colspan="2" class="empty">No nutrient data.</td></tr>'}</tbody></table>
  `;
}

function closeModal() { $("#modal").classList.add("hidden"); }

function formatAmount(n) {
  if (n >= 100) return n.toFixed(0);
  if (n >= 1) return n.toFixed(2);
  return n.toFixed(3);
}

function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

// Search (debounced)
let searchTimer = null;
$("#search-input").addEventListener("input", (e) => {
  clearTimeout(searchTimer);
  const q = e.target.value.trim();
  searchTimer = setTimeout(async () => {
    if (!q) {
      // clear search → reload current category
      if (activeCategoryId) {
        const res = await fetch(`/api/foods?category_id=${activeCategoryId}`);
        renderFoods(await res.json());
      }
      return;
    }
    $("#explore-title").textContent = `Search results for "${q}"`;
    document.querySelectorAll(".category-tile").forEach((t) => t.classList.remove("active"));
    const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
    renderFoods(await res.json());
  }, 200);
});

$("#modal-close").addEventListener("click", closeModal);
$(".modal-backdrop") && document.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal-backdrop")) closeModal();
});

loadCategories();
