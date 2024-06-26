const url_path = window.location.pathname;
const allowed =
  url_path === "/lists/create" || url_path.startsWith("/lists/modify");
const form_item_init = allowed
  ? document.querySelector(".item-root[data-bgit='item-form-0']")
  : undefined;
const form_item_bp = allowed ? form_item_init.cloneNode(true) : undefined;
if (allowed && form_item_bp.classList.contains("d-none"))
  form_item_bp.classList.remove("d-none");

function lists() {
  if (allowed) {
    const add_item_btn = document.querySelector(".add-item");
    add_item_btn.addEventListener("click", handleAddItem);

    handleItem(form_item_init);

    const form = document.querySelector("#listform");
    form.addEventListener("submit", handleSubmit);

    if (url_path.startsWith("/lists/modify/")) {
      const form_items = document.querySelectorAll(".item-root");
      form_items.forEach((form_item, index) => {
        // form_item.querySelectorAll("[id^='item']").forEach((input) => {
        //   input.id = `${input.id}-${index}`;
        //   input.name = `${input.id}`;
        // });
        handleItem(form_item);
      });
    }

    return;
  }
  function handleAddItem(event) {
    event.preventDefault();

    const form_item_new = form_item_bp.cloneNode(true);
    const form_item_list = document.querySelector("#item-list");
    const form_item_number = document.querySelectorAll(".item-form").length;

    form_item_new.dataset["bgit"] = `item-form-${form_item_number}`;
    form_item_new
      .querySelectorAll("[data-bgit='item-form-0']")
      .forEach((element) =>
        element.setAttribute("data-bgit", `item-form-${form_item_number}`)
      );

    handleItem(form_item_list.appendChild(form_item_new));
  }
}

function handleItem(form_item) {
  const form_item_id = form_item.dataset["bgit"].split("-")[2];

  const remove_btns = form_item.querySelectorAll(".remove-item");
  remove_btns.forEach((btn) => btn.addEventListener("click", handleRemoveItem));

  const validate_btn = form_item.querySelector(".validate-item");
  validate_btn.addEventListener("click", handleValidateItem);

  const modify_btn = form_item.querySelector(".modify-item");
  modify_btn.addEventListener("click", handleModifyItem);

  return form_item;
}

function handleRemoveItem(event) {
  event.preventDefault();

  const item_id = event.target.dataset["bgit"].trim();

  document.querySelector(`.item-root[data-bgit='${item_id}']`).remove();
  return;
}

function handleValidateItem(event) {
  event.preventDefault();

  handleItemPreview(event.target);

  const item_id = event.target.dataset["bgit"];
  const item_form = document.querySelector(
    `.item-form[data-bgit='${item_id}']`
  );
  const item_card = document.querySelector(`.card[data-bgit='${item_id}']`);
  item_form.hidden = true;
  item_card.hidden = false;

  return;
}

function handleItemPreview(item) {
  const item_id = item.dataset["bgit"];
  // Handles image preview
  const image_input = document.querySelector(
    `#item_image[data-bgit='${item_id}']`
  );
  const image_preview = document.querySelector(
    `.item-image[data-bgit='${item_id}']`
  );

  const handleImage = () => {
    const image = image_input.files[0];
    if (!image) return;
    if (!image.type.startsWith("image/")) return;

    image_preview.file = image;

    const reader = new FileReader();
    reader.onload = (e) => {
      image_preview.src = e.target.result;
    };
    reader.readAsDataURL(image);
  };

  handleImage();

  // Handles title preview
  const title_input = document.querySelector(
    `#item_title[data-bgit='${item_id}']`
  );
  const title_preview = document.querySelector(
    `.card-title[data-bgit='${item_id}']`
  );

  title_preview.innerHTML = `${title_input.value}`;

  return;
}

function handleModifyItem(event) {
  event.preventDefault();

  const item_id = event.target.dataset["bgit"];
  const item_form = document.querySelector(
    `.item-form[data-bgit='${item_id}']`
  );
  const item_card = document.querySelector(`.card[data-bgit='${item_id}']`);
  item_form.hidden = false;
  item_card.hidden = true;

  return;
}

function handleSubmit(event) {
  // Remove utility item form
  if (url_path.startsWith("/lists/modify/")) {
    const utility_item_form = document.querySelector(".item-root.d-none");
    utility_item_form.remove();
  }
  // Rename fields name and id for each items
  const item_roots = event.target.querySelectorAll(".item-root");
  item_roots.forEach((root, index) => {
    const root_number = url_path.startsWith("/lists/modify/")
      ? index
      : parseInt(root.dataset["bgit"].split("-")[2]);
    root.querySelectorAll("[id^='item']").forEach((input) => {
      input.id = `${input.id}-${root_number}`;
      input.name = `${input.id}`;
    });
  });
}

export { lists };
